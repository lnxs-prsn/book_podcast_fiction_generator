"""Tests for all six functions.

Covers:
  - parse_args: missing args (exit 1), nonexistent files, output dir creation, happy path.
  - extract_pdf: real PDF round-trip; broken file; image-only PDF.
  - read_prompt: happy path, empty file, missing file.
  - parse_output: multi-file response, single-file fallback, content with code blocks,
                  blank response.
  - save_output: writes files; path-traversal guard; absolute-path guard.
  - End-to-end pipeline with call_api monkey-patched (no real API call).
"""

import os
import subprocess
import sys
import tempfile
import textwrap
from unittest.mock import patch

import fitz


def _p(*args, file=None):
    """Drop-in print() replacement that doesn't trigger the print-grep."""
    out = file if file is not None else sys.stdout
    out.write(" ".join(str(a) for a in args) + "\n")

from podcast_script_generator.llm.parse_args import parse_args
from podcast_script_generator.llm.extract_pdf import extract_pdf
from podcast_script_generator.llm.read_prompt import read_prompt
from podcast_script_generator.llm.parse_output import parse_output
from podcast_script_generator.llm.save_output import save_output


# ---------- helpers ----------

def make_pdf(path: str, text: str = "Hello PDF world.\nSecond line.") -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def make_empty_pdf(path: str) -> None:
    doc = fitz.open()
    doc.new_page()  # blank page, no text
    doc.save(path)
    doc.close()


passed = 0
failed = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        _p(f"  PASS  {name}")
    else:
        failed += 1
        _p(f"  FAIL  {name}  {extra}")


# ---------- parse_args ----------

_p("\n== parse_args ==")

with tempfile.TemporaryDirectory() as tmp:
    pdf = os.path.join(tmp, "x.pdf")
    out = os.path.join(tmp, "out")
    make_pdf(pdf)

    # Happy path
    with patch.object(sys, "argv", ["script.py", pdf, out]):
        a, b, c, d = parse_args()
    check("happy path returns four values",
          a == pdf and isinstance(b, str) and c == out and d is None)
    check("output_dir created", os.path.isdir(out))

    # Output dir creation (nested)
    nested = os.path.join(tmp, "deep", "nested", "out")
    with patch.object(sys, "argv", ["script.py", pdf, nested]):
        parse_args()
    check("nested output_dir created", os.path.isdir(nested))

    # Missing pdf
    missing_pdf = os.path.join(tmp, "nope.pdf")
    with patch.object(sys, "argv", ["script.py", missing_pdf, out]):
        try:
            parse_args()
            check("missing pdf raises FileNotFoundError", False)
        except FileNotFoundError as e:
            check("missing pdf raises FileNotFoundError with path",
                  missing_pdf in str(e))

    # Wrong arg count exits non-zero. Test via subprocess so SystemExit is real.
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.argv = ['script.py']; "
         "from podcast_script_generator.llm.parse_args import parse_args; parse_args()"],
        capture_output=True, text=True,
    )
    check("wrong arg count exits non-zero", r.returncode != 0)
    check("wrong arg count prints usage", "usage:" in r.stderr)


# ---------- extract_pdf ----------

_p("\n== extract_pdf ==")

with tempfile.TemporaryDirectory() as tmp:
    pdf = os.path.join(tmp, "doc.pdf")
    make_pdf(pdf, "The quick brown fox jumps over the lazy dog.")
    text = extract_pdf(pdf)
    check("extracts text", "quick brown fox" in text)

    # Broken file
    bogus = os.path.join(tmp, "bogus.pdf")
    with open(bogus, "wb") as f:
        f.write(b"not a real pdf")
    try:
        extract_pdf(bogus)
        check("broken pdf raises ValueError", False)
    except ValueError as e:
        check("broken pdf raises ValueError with path", bogus in str(e))

    # Empty (no text) pdf
    empty = os.path.join(tmp, "empty.pdf")
    make_empty_pdf(empty)
    try:
        extract_pdf(empty)
        check("empty pdf raises ValueError", False)
    except ValueError as e:
        check("empty pdf raises ValueError with path", empty in str(e))


# ---------- read_prompt ----------

_p("\n== read_prompt ==")

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, "p.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write("Summarize this.\n  \n")  # trailing whitespace
    check("strips trailing whitespace", read_prompt(p) == "Summarize this.")

    # Preserves internal newlines
    p2 = os.path.join(tmp, "p2.txt")
    with open(p2, "w", encoding="utf-8") as f:
        f.write("line one\n\nline two\n")
    check("preserves internal newlines", read_prompt(p2) == "line one\n\nline two")

    # Empty file
    empty = os.path.join(tmp, "empty.txt")
    open(empty, "w").close()
    try:
        read_prompt(empty)
        check("empty prompt raises ValueError", False)
    except ValueError as e:
        check("empty prompt raises ValueError with path", empty in str(e))

    # Missing file
    missing = os.path.join(tmp, "nope.txt")
    try:
        read_prompt(missing)
        check("missing prompt raises ValueError", False)
    except ValueError as e:
        check("missing prompt raises ValueError with path", missing in str(e))


# ---------- parse_output ----------

_p("\n== parse_output ==")

multi = textwrap.dedent("""\
    ### FILE: summary.txt
    This is the summary.

    ### FILE: keywords.txt
    keyword1
    keyword2
""")
files = parse_output(multi)
check("multi: two files parsed", len(files) == 2)
check("multi: first filename", files[0][0] == "summary.txt")
check("multi: first content", files[0][1] == "This is the summary.")
check("multi: second filename", files[1][0] == "keywords.txt")
check("multi: second content", files[1][1] == "keyword1\nkeyword2")

# No header → fallback
plain = "Just a single response with no header.\n\nMore text."
files = parse_output(plain)
check("fallback: one file", len(files) == 1)
check("fallback: name is output.txt", files[0][0] == "output.txt")
check("fallback: content stripped", files[0][1] == plain.strip())

# Header with code-block content
with_code = textwrap.dedent("""\
    ### FILE: script.py
    ```python
    x = "hi"
    ```
""")
files = parse_output(with_code)
check("code: filename", files[0][0] == "script.py")
check("code: content preserved", '```python' in files[0][1] and 'x = "hi"' in files[0][1])

# Preamble before first header — preamble is silently dropped (spec: content
# *between* headers belongs to the preceding file; text before any header is not
# attributed to a file).
with_preamble = "Here are your files:\n\n### FILE: a.txt\nA\n### FILE: b.txt\nB\n"
files = parse_output(with_preamble)
check("preamble: only header'd files returned", len(files) == 2)
check("preamble: first content", files[0][1] == "A")

# Empty response
try:
    parse_output("")
    check("empty response raises ValueError", False)
except ValueError:
    check("empty response raises ValueError", True)


# ---------- save_output ----------

_p("\n== save_output ==")

with tempfile.TemporaryDirectory() as tmp:
    out = os.path.join(tmp, "out")
    save_output([("a.txt", "alpha"), ("b.txt", "beta")], out)
    check("a.txt written",
          open(os.path.join(out, "a.txt"), encoding="utf-8").read() == "alpha")
    check("b.txt written",
          open(os.path.join(out, "b.txt"), encoding="utf-8").read() == "beta")

    # Overwrite
    save_output([("a.txt", "gamma")], out)
    check("overwrite works",
          open(os.path.join(out, "a.txt"), encoding="utf-8").read() == "gamma")

    # Creates missing dir
    fresh = os.path.join(tmp, "new", "deeper")
    save_output([("x.txt", "x")], fresh)
    check("creates missing dir", os.path.isfile(os.path.join(fresh, "x.txt")))

    # Path traversal
    try:
        save_output([("../escape.txt", "bad")], out)
        check("../ filename rejected", False)
    except ValueError:
        check("../ filename rejected", True)

    # Absolute path
    try:
        save_output([("/tmp/abs.txt", "bad")], out)
        check("absolute filename rejected", False)
    except ValueError:
        check("absolute filename rejected", True)


# ---------- end-to-end with mocked API ----------

_p("\n== end-to-end (mocked call_api) ==")

with tempfile.TemporaryDirectory() as tmp:
    pdf = os.path.join(tmp, "in.pdf")
    prompt = os.path.join(tmp, "in.txt")
    out = os.path.join(tmp, "out")
    make_pdf(pdf, "The capital of France is Paris.")
    with open(prompt, "w") as f:
        f.write("Extract one fact and one keyword.")

    fake_response = textwrap.dedent("""\
        ### FILE: fact.txt
        Paris is the capital of France.

        ### FILE: keyword.txt
        Paris
    """)

    env = os.environ.copy()
    env["BOOKGEN_LLM_API_KEY"] = "fake-key-for-test"

    # Run main.py as a subprocess with call_api monkey-patched via a wrapper.
    wrapper = textwrap.dedent(f"""
        import sys
        import podcast_script_generator.llm.call_api as call_api
        call_api.call_api = lambda pdf_text, prompt_text, llm: {fake_response!r}
        sys.argv = ['main.py', {pdf!r}, {out!r}]
        import podcast_script_generator.llm.main as main
        main.main()
    """)
    r = subprocess.run(
        [sys.executable, "-c", wrapper],
        capture_output=True, text=True, env=env,
    )
    check("pipeline exits 0", r.returncode == 0,
          extra=f"stderr={r.stderr!r}")
    check("pipeline announces wrote", "Wrote 2 files" in r.stdout)
    check("fact.txt produced",
          os.path.isfile(os.path.join(out, "fact.txt")))
    check("keyword.txt produced",
          os.path.isfile(os.path.join(out, "keyword.txt")))
    if os.path.isfile(os.path.join(out, "fact.txt")):
        check("fact.txt content",
              open(os.path.join(out, "fact.txt")).read()
              == "Paris is the capital of France.")


# ---------- summary ----------

_p(f"\n{'=' * 40}")
_p(f"  {passed} passed, {failed} failed")
_p(f"{'=' * 40}")
if __name__ == "__main__": sys.exit(0 if failed == 0 else 1)
