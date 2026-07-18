"""Pytest conversion of test_all.py — 37 test functions, one per original check() call.

Do NOT modify test_all.py (the original is kept as-is for PYTHONPATH=src python test_all.py).

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
import textwrap
from unittest.mock import patch

import fitz
import pytest

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


# ---------- parse_args ----------

def test_parse_args_happy_path_returns_four_values(tmp_path):
    pdf = str(tmp_path / "x.pdf")
    out = str(tmp_path / "out")
    make_pdf(pdf)
    with patch.object(sys, "argv", ["script.py", pdf, out]):
        a, b, c, d = parse_args()
    assert a == pdf and isinstance(b, str) and c == out and d is None


def test_parse_args_output_dir_created(tmp_path):
    pdf = str(tmp_path / "x.pdf")
    out = str(tmp_path / "out")
    make_pdf(pdf)
    with patch.object(sys, "argv", ["script.py", pdf, out]):
        parse_args()
    assert os.path.isdir(out)


def test_parse_args_nested_output_dir_created(tmp_path):
    pdf = str(tmp_path / "x.pdf")
    make_pdf(pdf)
    nested = str(tmp_path / "deep" / "nested" / "out")
    with patch.object(sys, "argv", ["script.py", pdf, nested]):
        parse_args()
    assert os.path.isdir(nested)


def test_parse_args_missing_pdf_raises_file_not_found_with_path(tmp_path):
    out = str(tmp_path / "out")
    missing_pdf = str(tmp_path / "nope.pdf")
    with patch.object(sys, "argv", ["script.py", missing_pdf, out]):
        with pytest.raises(FileNotFoundError) as exc_info:
            parse_args()
    assert missing_pdf in str(exc_info.value)


def test_parse_args_wrong_arg_count_exits_nonzero():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.argv = ['script.py']; "
         "from podcast_script_generator.llm.parse_args import parse_args; parse_args()"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode != 0


def test_parse_args_wrong_arg_count_prints_usage():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.argv = ['script.py']; "
         "from podcast_script_generator.llm.parse_args import parse_args; parse_args()"],
        capture_output=True, text=True, env=env,
    )
    assert "usage:" in r.stderr


# ---------- extract_pdf ----------

def test_extract_pdf_extracts_text(tmp_path):
    pdf = str(tmp_path / "doc.pdf")
    make_pdf(pdf, "The quick brown fox jumps over the lazy dog.")
    text = extract_pdf(pdf)
    assert "quick brown fox" in text


def test_extract_pdf_broken_file_raises_value_error_with_path(tmp_path):
    bogus = str(tmp_path / "bogus.pdf")
    with open(bogus, "wb") as f:
        f.write(b"not a real pdf")
    with pytest.raises(ValueError) as exc_info:
        extract_pdf(bogus)
    assert bogus in str(exc_info.value)


def test_extract_pdf_empty_pdf_raises_value_error_with_path(tmp_path):
    empty = str(tmp_path / "empty.pdf")
    make_empty_pdf(empty)
    with pytest.raises(ValueError) as exc_info:
        extract_pdf(empty)
    assert empty in str(exc_info.value)


# ---------- read_prompt ----------

def test_read_prompt_strips_trailing_whitespace(tmp_path):
    p = str(tmp_path / "p.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write("Summarize this.\n  \n")  # trailing whitespace
    assert read_prompt(p) == "Summarize this."


def test_read_prompt_preserves_internal_newlines(tmp_path):
    p2 = str(tmp_path / "p2.txt")
    with open(p2, "w", encoding="utf-8") as f:
        f.write("line one\n\nline two\n")
    assert read_prompt(p2) == "line one\n\nline two"


def test_read_prompt_empty_file_raises_value_error_with_path(tmp_path):
    empty = str(tmp_path / "empty.txt")
    open(empty, "w").close()
    with pytest.raises(ValueError) as exc_info:
        read_prompt(empty)
    assert empty in str(exc_info.value)


def test_read_prompt_missing_file_raises_value_error_with_path(tmp_path):
    missing = str(tmp_path / "nope.txt")
    with pytest.raises(ValueError) as exc_info:
        read_prompt(missing)
    assert missing in str(exc_info.value)


# ---------- parse_output ----------

_MULTI = textwrap.dedent("""\
    ### FILE: summary.txt
    This is the summary.

    ### FILE: keywords.txt
    keyword1
    keyword2
""")

_PLAIN = "Just a single response with no header.\n\nMore text."

_WITH_CODE = textwrap.dedent("""\
    ### FILE: script.py
    ```python
    x = "hi"
    ```
""")

_WITH_PREAMBLE = "Here are your files:\n\n### FILE: a.txt\nA\n### FILE: b.txt\nB\n"


def test_parse_output_multi_two_files_parsed():
    files = parse_output(_MULTI)
    assert len(files) == 2


def test_parse_output_multi_first_filename():
    files = parse_output(_MULTI)
    assert files[0][0] == "summary.txt"


def test_parse_output_multi_first_content():
    files = parse_output(_MULTI)
    assert files[0][1] == "This is the summary."


def test_parse_output_multi_second_filename():
    files = parse_output(_MULTI)
    assert files[1][0] == "keywords.txt"


def test_parse_output_multi_second_content():
    files = parse_output(_MULTI)
    assert files[1][1] == "keyword1\nkeyword2"


def test_parse_output_fallback_one_file():
    files = parse_output(_PLAIN)
    assert len(files) == 1


def test_parse_output_fallback_name_is_output_txt():
    files = parse_output(_PLAIN)
    assert files[0][0] == "output.txt"


def test_parse_output_fallback_content_stripped():
    files = parse_output(_PLAIN)
    assert files[0][1] == _PLAIN.strip()


def test_parse_output_code_filename():
    files = parse_output(_WITH_CODE)
    assert files[0][0] == "script.py"


def test_parse_output_code_content_preserved():
    files = parse_output(_WITH_CODE)
    assert '```python' in files[0][1] and 'x = "hi"' in files[0][1]


def test_parse_output_preamble_only_headerd_files_returned():
    files = parse_output(_WITH_PREAMBLE)
    assert len(files) == 2


def test_parse_output_preamble_first_content():
    files = parse_output(_WITH_PREAMBLE)
    assert files[0][1] == "A"


def test_parse_output_empty_response_raises_value_error():
    with pytest.raises(ValueError):
        parse_output("")


# ---------- save_output ----------

def test_save_output_a_txt_written(tmp_path):
    out = str(tmp_path / "out")
    save_output([("a.txt", "alpha"), ("b.txt", "beta")], out)
    assert open(os.path.join(out, "a.txt"), encoding="utf-8").read() == "alpha"


def test_save_output_b_txt_written(tmp_path):
    out = str(tmp_path / "out")
    save_output([("a.txt", "alpha"), ("b.txt", "beta")], out)
    assert open(os.path.join(out, "b.txt"), encoding="utf-8").read() == "beta"


def test_save_output_overwrite_works(tmp_path):
    out = str(tmp_path / "out")
    save_output([("a.txt", "alpha")], out)
    save_output([("a.txt", "gamma")], out)
    assert open(os.path.join(out, "a.txt"), encoding="utf-8").read() == "gamma"


def test_save_output_creates_missing_dir(tmp_path):
    fresh = str(tmp_path / "new" / "deeper")
    save_output([("x.txt", "x")], fresh)
    assert os.path.isfile(os.path.join(fresh, "x.txt"))


def test_save_output_dotdot_filename_rejected(tmp_path):
    out = str(tmp_path / "out")
    os.makedirs(out, exist_ok=True)
    with pytest.raises(ValueError):
        save_output([("../escape.txt", "bad")], out)


def test_save_output_absolute_filename_rejected(tmp_path):
    out = str(tmp_path / "out")
    os.makedirs(out, exist_ok=True)
    with pytest.raises(ValueError):
        save_output([("/tmp/abs.txt", "bad")], out)


# ---------- end-to-end with mocked API ----------

_FAKE_RESPONSE = textwrap.dedent("""\
    ### FILE: fact.txt
    Paris is the capital of France.

    ### FILE: keyword.txt
    Paris
""")


def _run_e2e(tmp_path):
    """Run the e2e pipeline subprocess once and return (returncode, stdout, out_dir)."""
    pdf = str(tmp_path / "in.pdf")
    prompt = str(tmp_path / "in.txt")
    out = str(tmp_path / "out")
    make_pdf(pdf, "The capital of France is Paris.")
    with open(prompt, "w") as f:
        f.write("Extract one fact and one keyword.")

    wrapper = textwrap.dedent(f"""
        import sys
        import podcast_script_generator.llm.call_api as call_api
        call_api.call_api = lambda pdf_text, prompt_text, llm: {_FAKE_RESPONSE!r}
        sys.argv = ['main.py', {pdf!r}, {out!r}]
        import podcast_script_generator.llm.main as main
        main.main()
    """)
    env = os.environ.copy()
    env["BOOKGEN_LLM_API_KEY"] = "fake-key-for-test"
    env["PYTHONPATH"] = "src"
    r = subprocess.run(
        [sys.executable, "-c", wrapper],
        capture_output=True, text=True, env=env,
    )
    return r, out


def test_e2e_pipeline_exits_0(tmp_path):
    r, out = _run_e2e(tmp_path)
    assert r.returncode == 0, f"stderr={r.stderr!r}"


def test_e2e_pipeline_announces_wrote(tmp_path):
    r, out = _run_e2e(tmp_path)
    assert "Wrote 2 files" in r.stdout


def test_e2e_fact_txt_produced(tmp_path):
    r, out = _run_e2e(tmp_path)
    assert os.path.isfile(os.path.join(out, "fact.txt"))


def test_e2e_keyword_txt_produced(tmp_path):
    r, out = _run_e2e(tmp_path)
    assert os.path.isfile(os.path.join(out, "keyword.txt"))


def test_e2e_fact_txt_content(tmp_path):
    r, out = _run_e2e(tmp_path)
    assert os.path.isfile(os.path.join(out, "fact.txt"))
    assert open(os.path.join(out, "fact.txt")).read() == "Paris is the capital of France."
