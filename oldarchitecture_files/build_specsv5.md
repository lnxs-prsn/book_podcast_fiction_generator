# Build Specs v5 — CLI / Endpoints / Engines Refactor

> Derived from `build_specsv4.md`.
> v5 fixes structural and design issues found in a post-v4 review.
>
> Changes from v4 are marked with **[v5]** in the relevant section.
> All prior **[v4]** and **[v3]** markers are retained where they were already correct.
>
> Each pass names every file touched, the change type (add / modify / delete), and a
> done condition. Passes within a phase are ordered; complete each pass before the next.

---

## Gap Index (v4 → v5)

| Gap | Severity | Fixed In |
|-----|----------|----------|
| All new endpoint and CLI files use module-level `sys.path.insert` — institutionalizing a path hack rather than establishing a consistent invocation model | High | Pass 0.0 |
| Pass 1.1 adds `sys.path.insert` at module level to `tts/cli.py` and `call_api.py` — unnecessary once PYTHONPATH is set | Medium | Pass 0.0 / Pass 1.1 |
| `PodcastResult.audio_path` typed `str` while `script_path` is `Path` — inconsistent; `ok: bool` field permits invalid state `PodcastResult(ok=True, error=ValueError(...))` | Medium | Pass 2.2 |
| `_prompt_user()` is explicitly duplicated across `cli/fiction.py` and `novel_pipeline/cli.py` with no extraction plan | Medium | Pass 4.3 |
| `endpoints/podcast.py`, `endpoints/slicer.py`, `endpoints/fiction.py` each contain module-level `sys.path.insert` — removed by invocation model | Medium | Pass 0.0 / Passes 2.3, 3.2, 4.4 |
| Approximate line-number references (`~157`, `lines 55–117`, `~574`) drift as prior passes shift file content | Low | Throughout |
| No cross-phase behavioral smoke test verifying that the full endpoint stack executes end-to-end | Low | Phase 6 |
| Pass 4.4 retains a fallback `sys.path.insert` for `novel_pipeline` — contradicts Pass 0.0's convention | Low | Pass 4.4 |
| CLI entry points give silent `ModuleNotFoundError` if invoked without `PYTHONPATH=src` — no actionable message | Low | Pass 2.5 / Pass 4.5 |

---

## Phase 0 — Invocation Model

**Goal**: Establish a single, consistent import model for all scripts before any code is
written. All subsequent passes assume this model is in place.

---

### Pass 0.0 — PYTHONPATH Convention

**[v5] Root cause of the sys.path.insert proliferation**: When a script is invoked as
`python src/cli/podcast.py`, Python adds `src/cli/` to `sys.path[0]` — not `src/`. Any
import of a sibling package (`from config import load_config`, `from endpoints.podcast import
...`) fails unless `src/` is added to the path. v4 patches this per-file with
`sys.path.insert`. v5 fixes it once at the invocation level.

**The invocation model**: all scripts are run from `harnessv3/` with `src/` on PYTHONPATH:

```bash
# Canonical form — prefix every invocation:
PYTHONPATH=src python src/cli/podcast.py <args>
PYTHONPATH=src python src/cli/fiction.py <args>

# Or set once in the shell for a session:
export PYTHONPATH=src
```

**Persistent option** — add a `.env` at `harnessv3/` (uv reads this automatically):

```
# harnessv3/.env
PYTHONPATH=src
```

With the `.env` in place, `uv run python src/cli/podcast.py` picks up `PYTHONPATH=src`
without any prefix. Plain `python src/cli/podcast.py` still requires the explicit prefix
or shell export.

**What this eliminates in subsequent passes**:
- The module-level `sys.path.insert(0, str(_SRC))` block that v4 adds to
  `endpoints/podcast.py`, `endpoints/slicer.py`, `endpoints/fiction.py`,
  `cli/podcast.py`, and `cli/fiction.py` — all removed.
- The module-level `sys.path.insert(0, str(Path(__file__).parent.parent))` blocks that
  v4 adds to `tts/cli.py` and `call_api.py` in Pass 1.1 — also removed.

**What this does NOT change**:
- The `sys.path.insert` calls inside function bodies of `run_local()`, `run_llm()`, and
  `run_tts()` in `run_chapter.py` — those insert subdirectory paths for modules that
  have no `__init__.py` (`src/podcast_script_generator/llm/`, `src/tts/`). They are
  pre-existing, function-scoped, and are migrated as-is in Pass 2.3.

**`_SRC` / `_ROOT` constants**: `endpoints/podcast.py` still needs `_SRC` and `_ROOT`
for computing output paths (`data/output/scripts/`, `data/output/audio/`). These constants
remain but are no longer needed for `sys.path` manipulation:

```python
from pathlib import Path

_SRC  = Path(__file__).parent.parent        # src/
_ROOT = Path(__file__).parent.parent.parent  # harnessv3/
_SCRIPTS_OUT = _ROOT / "data" / "output" / "scripts"
_AUDIO_OUT   = _ROOT / "data" / "output" / "audio"
```

No `import sys` and no `sys.path.insert` at module level in this file.

**Done**:
```
PYTHONPATH=src python -c "from config import load_config; print(load_config())"
# exits 0

PYTHONPATH=src python -c "from endpoints.podcast import generate_chapter_podcast; print('ok')"
# exits 0 after Pass 2.3 is complete; checking import path works before that point
```

---

## Phase 1 — Foundation

**Goal**: Config loading and exception hierarchy in place before any endpoints are written.
No behavior change to existing entry points.

---

### Pass 1.1 — Shared Config Loader

| File | Change |
|------|--------|
| `src/config.py` | add |
| `src/run_chapter.py` | modify — remove `_load_config()` definition; add `from config import load_config`; **[v4] rename 1 call site** |
| `src/run_book.py` | modify — same; **[v4] rename 1 call site** |
| `src/tts/cli.py` | modify — remove `_load_config()` definition; add `from config import load_config`; **[v3] rename 3 call sites** |
| `src/podcast_script_generator/llm/call_api.py` | modify — remove `_load_config()` definition; add `from config import load_config`; **[v3] rename 4 call sites** |

**`src/config.py` full implementation:**

```python
import json
from pathlib import Path

_DEFAULT_PATH = Path(__file__).parent / "config.json"

def load_config(path=None) -> dict:
    p = Path(path) if path else _DEFAULT_PATH
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
```

**[v5] Import pattern for `tts/cli.py` and `call_api.py`** — Pass 0.0 establishes
`PYTHONPATH=src`, so `src/` is already on the path at import time. No `sys.path.insert`
is needed:

```python
from config import load_config
```

Do NOT add `sys.path.insert` to these files. The v4 spec's `sys.path.insert` blocks
for these files are superseded by the invocation model in Pass 0.0.

`src/run_chapter.py` and `src/run_book.py` compute `SRC = Path(__file__).parent` (IS
`src/`). They need no path-insert — `from config import load_config` works as-is.

**[v3] Call-site renames for `tts/cli.py` and `call_api.py`**:

- `src/tts/cli.py`: rename `_load_config()` → `load_config()` at 3 call sites inside
  `build_api_payload()`, `send_to_api()`, and `cli_entrypoint()`.
- `src/podcast_script_generator/llm/call_api.py`: rename `_load_config()` → `load_config()`
  at all call sites inside the resolver functions. Locate them with:
  `grep -n "_load_config" src/podcast_script_generator/llm/call_api.py`

**[v4] Call-site renames for `run_chapter.py` and `run_book.py`**:

- `src/run_chapter.py`: rename `_load_config()` → `load_config()` at the call site inside
  `run_tts()` — `cfg_speakers = _load_config().get("speakers", {})`.
  Locate it with: `grep -n "_load_config" src/run_chapter.py`
- `src/run_book.py`: rename `_load_config()` → `load_config()` at the call site inside
  `main()` — `toc_page = args.toc_page or _load_config().get("toc_page")`.
  Locate it with: `grep -n "_load_config" src/run_book.py`

> Note: the novel_pipeline has a completely separate TOML-based `load_config()` in
> `src/fiction/pipeline/novel_pipeline/config.py`. That loader is NOT related to
> `src/config.py` and must not be modified.

**Done**:
```
PYTHONPATH=src python -c "from config import load_config; print(load_config())"
# exits 0

PYTHONPATH=src python src/run_chapter.py --help
# still works

grep -rn "_load_config" src/run_chapter.py src/run_book.py src/tts/cli.py \
  src/podcast_script_generator/llm/call_api.py
# returns empty
```

---

### Pass 1.2 — Podcast Exception Hierarchy

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/exceptions.py` | add |
| `src/podcast_script_generator/llm/main.py` | modify — `sys.exit()` calls → typed raises; add `__main__` guard |
| `src/tts/cli.py` | modify — remap `AuthError` → `TTSSubmissionError`; remap `RuntimeError` (WaveSpeed) → `TTSSubmissionError`; remap timeout/network errors → `TTSTimeoutError`; broaden `cli_entrypoint()` catch |
| `src/run_chapter.py` | modify — catch `PodcastError` at CLI boundary; print to stderr; `sys.exit(1)` |

**`src/podcast_script_generator/llm/exceptions.py` full content:**

```python
class PodcastError(Exception):
    pass

class PDFExtractionError(PodcastError):
    pass

class ScriptGenerationError(PodcastError):
    pass

class TTSSubmissionError(PodcastError):
    pass

class TTSTimeoutError(PodcastError):
    pass
```

**`tts/cli.py` remapping** — type-remap only (no new raises, just replace types):
- Delete local `AuthError` class definition.
- `raise AuthError(...)` → `raise TTSSubmissionError(...)`
- `raise RuntimeError(f"WaveSpeed job failed...")` → `raise TTSSubmissionError(...)`
- `raise ConnectionError(...)` → `raise TTSTimeoutError(...)`
- `cli_entrypoint()` catch: `(ValueError, AuthError, ConnectionError, RuntimeError, OSError)`
  → `(PodcastError, ValueError, OSError)`

**[v4] Exception import path for `tts/cli.py`** — `PYTHONPATH=src` is set (Pass 0.0),
so the full dotted import path works as-is:

```python
from podcast_script_generator.llm.exceptions import (
    PodcastError, TTSSubmissionError, TTSTimeoutError
)
```

**`main.py` update** — replace `sys.exit()` inside `main()` and update `__main__` guard:

```python
# Inside main():
#   FileNotFoundError path → raise PDFExtractionError(...)
#   ValueError / KeyError path → raise ScriptGenerationError(...)
#   catch-all → raise PodcastError(...)

if __name__ == "__main__":
    try:
        main()
    except PodcastError as e:
        import sys
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

**[v3] Done condition — corrected grep for `main.py`**:

```
grep -rn "sys.exit" src/podcast_script_generator/ | grep -v "__main__"
# returns empty (the sys.exit(1) in the __main__ guard is the allowed exception)

grep "sys.exit" src/tts/cli.py
# returns hits only inside cli_entrypoint()

grep "sys.exit" src/run_chapter.py
# returns exactly one hit (the CLI boundary catch)
```

---

### Pass 1.3 — Structured Logging Migration

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/call_api.py` | modify — add `import logging` + `logger`; `print(f"OpenRouter 429...")` → `logger.debug(...)` |
| `src/podcast_script_generator/llm/save_output.py` | modify — add `import logging` + `logger`; `print(f"Wrote N files...")` → `logger.debug(...)` |
| `src/tts/cli.py` | modify — add `import logging` + `logger`; convert **[v4] 5 prints** in `send_to_api()` to logger calls |
| `src/run_chapter.py` | modify — add `logging.basicConfig(level=logging.INFO, format="%(message)s")` at entry |
| `src/run_book.py` | modify — same |

**Logger setup pattern** (add to each of the three library files):

```python
import logging
logger = logging.getLogger(__name__)
```

**[v4] `tts/cli.py` print mapping** — all 5 prints inside `send_to_api()`:
- Submission confirmation (`TTS submitted  request_id=...`) → `logger.info(...)`
- Recovery-file notice (`Recovery file  {job_file}`) → `logger.info(...)` (conditional on `job_file`)
- Polling start (`Polling for completion...`) → `logger.info(...)`
- Per-poll status (`[{elapsed}s] status=...`) → `logger.debug(...)`
- Completion confirmation (`[done] {elapsed}s`) → `logger.info(...)`

> The prints in `run_chapter.py`'s `main()` are intentionally left as-is here — they are
> CLI output that will be stripped entirely in Pass 2.3 when the body migrates to
> `generate_chapter_podcast()`. Premature conversion would complicate that pass.

**Done**:

```
grep -rn "^\s*print(" src/podcast_script_generator/ src/tts/cli.py
# returns empty

PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# produces INFO-level output without crashing
```

---

## Phase 2 — Podcast Pipeline Endpoint

**Goal**: `generate_chapter_podcast()` and `generate_book_podcast()` are directly callable
with no argparse, no print, no sys.exit. CLI wrappers are thin.

---

### Pass 2.1 — Speaker Normalization Extract

| File | Change |
|------|--------|
| `src/util/__init__.py` | add — empty |
| `src/util/normalize.py` | add — `normalize_speakers(text: str) -> str` |
| `src/run_chapter.py` | modify — delete `_to_speaker_format()` definition; update 3 call sites; add import |

**What to extract**: the function is currently named `_to_speaker_format` in `run_chapter.py`.
Locate it with: `grep -n "def _to_speaker_format" src/run_chapter.py`.
This pass is an extraction AND a rename to `normalize_speakers`.

**Three call sites to update in `run_chapter.py`**:
- Inside `run_local()` — `grep -n "_to_speaker_format" src/run_chapter.py` will show all three
- Inside `run_llm()` — two calls (one for `fiction_meta` branch, one for all other modes)

**Import to add**:
```python
from util.normalize import normalize_speakers
```

(`PYTHONPATH=src` is set, so this resolves correctly from any invocation.)

**Done**:

```
PYTHONPATH=src python -c \
  "from util.normalize import normalize_speakers; print(normalize_speakers('ALEX: hi'))"
# exits 0; returns a Speaker 0:-prefixed line

PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# behavior unchanged
```

---

### Pass 2.2 — Canonical Types

| File | Change |
|------|--------|
| `src/endpoints/__init__.py` | add — empty |
| `src/endpoints/podcast.py` | add — `ScriptMode` enum and `PodcastResult` dataclass |

**`ScriptMode` values** (mirror `run_chapter.py`'s `--mode` choices exactly):
```python
from enum import Enum

class ScriptMode(str, Enum):
    TWO_PERSON    = "2person"
    FOUR_PERSON   = "4person"
    CODE          = "code"
    REALWORLD     = "realworld"
    FICTION_META  = "fiction_meta"
```

**[v5] `PodcastResult` — consistent types, `ok` as computed property**:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PodcastResult:
    script_path: Path | None = None
    audio_path: Path | None = None   # [v5] Path, not str — consistent with script_path
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
```

`ok` is a read-only property computed from `error`. This eliminates the impossible
`PodcastResult(ok=True, error=ValueError(...))` state that the v4 definition permits.

**Constructor usage throughout the spec changes accordingly**:
- Success with audio: `PodcastResult(script_path=script_out, audio_path=Path(saved))`
- Success without audio: `PodcastResult(script_path=script_out)`
- Failure: `PodcastResult(error=some_exception)`
- `slice_only` success: `PodcastResult()`

**Done**:

```
PYTHONPATH=src python -c \
  "from endpoints.podcast import ScriptMode, PodcastResult
r = PodcastResult(error=ValueError('x'))
assert r.ok == False
r2 = PodcastResult(script_path=__import__('pathlib').Path('/tmp/x'))
assert r2.ok == True
print('ok')"
# exits 0
```

---

### Pass 2.3 — generate_chapter_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_chapter_podcast()`; **[v3]** move `run_local`, `run_llm`, `run_tts` helper functions; **[v4]** add `_SRC`/`_ROOT` constants |

**[v5] Path constants — no sys.path.insert at module level**. `PYTHONPATH=src` (Pass 0.0)
makes `from config import load_config` work without path surgery. Add near the top of the
file, before local imports:

```python
from pathlib import Path

_SRC  = Path(__file__).parent.parent        # src/
_ROOT = Path(__file__).parent.parent.parent  # harnessv3/
_SCRIPTS_OUT = _ROOT / "data" / "output" / "scripts"
_AUDIO_OUT   = _ROOT / "data" / "output" / "audio"

from config import load_config  # noqa: E402
```

No `import sys` and no `sys.path.insert` at module level in `endpoints/podcast.py`.

**[v4] Updated function signature** — `fiction_dir: Path | None` replaces
`fiction_content: str | None`:

```python
def generate_chapter_podcast(
    pdf_path: Path,
    llm: bool = False,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    fiction_dir: Path | None = None,
) -> PodcastResult:
```

**[v4] Fiction-dir discovery inside the endpoint**:

```python
fiction_content: str | None = None
if mode == "fiction_meta":
    if fiction_dir is None:
        return PodcastResult(error=ValueError(
            "mode 'fiction_meta' requires fiction_dir"))
    if not fiction_dir.is_dir():
        return PodcastResult(error=ValueError(
            f"fiction directory not found: {fiction_dir}"))
    chapter_num_match = re.match(r"^(\d+)", pdf_path.stem)
    if not chapter_num_match:
        return PodcastResult(error=ValueError(
            f"cannot extract chapter number from PDF stem: {pdf_path.stem}"))
    chapter_num = int(chapter_num_match.group(1))
    fiction_file = fiction_dir / f"chapter_{chapter_num:02d}.md"
    if not fiction_file.exists():
        candidates = sorted(fiction_dir.glob(f"*{chapter_num_match.group(1)}*.md"))
        if not candidates:
            return PodcastResult(error=ValueError(
                f"no fiction chapter found for chapter {chapter_num:02d} in {fiction_dir}"))
        fiction_file = candidates[0]
    fiction_content = fiction_file.read_text(encoding="utf-8").strip()
```

`re` must be imported at module level in `endpoints/podcast.py`.

**[v3] Helper function migration** — `run_chapter.py` currently defines three helper functions
(`run_local`, `run_llm`, `run_tts`) that the `main()` body calls. Pass 5.3 will shim
`run_chapter.py` to a single forwarding line, destroying its module namespace. If these
helpers are not moved now, the endpoint breaks at Pass 5.3.

Move `run_local()`, `run_llm()`, and `run_tts()` from `run_chapter.py` into
`src/endpoints/podcast.py` alongside `generate_chapter_podcast()`. They become private
helpers of the endpoint module. Update all internal path references from bare `ROOT`/`SRC`
to `_ROOT`/`_SRC`.

The existing `sys.path.insert` calls inside `run_local`, `run_llm`, and `run_tts` bodies
(inserting `src/decide_later/local/`, `src/podcast_script_generator/llm/`, `src/tts/`)
are function-scoped subdirectory inserts — they move as-is into `endpoints/podcast.py`.
These are distinct from the module-level inserts eliminated in Pass 0.0.

`run_book.py` currently calls them as `rc.run_llm()` etc. After this pass, `run_book.py`
needs a temporary re-import until it is shimmed in Pass 5.3:
```python
from endpoints.podcast import run_llm, run_local, run_tts
```

(This temporary import is removed when Pass 5.3 shims `run_book.py`.)

**Endpoint body construction**:
- Copy `run_chapter.py`'s `main()` body verbatim into `generate_chapter_podcast()`.
- Strip: all `argparse` setup, all `print()` calls, all `sys.exit()` calls.
  Locate `main()` with: `grep -n "^def main" src/run_chapter.py`
- The fiction-dir block is replaced entirely by the **[v4] discovery block** above.
- The realworld context block stays; remap `args.context` → `context` parameter and
  `sys.exit()` paths → `return PodcastResult(error=...)`.
- Wrap entire body in:
  ```python
  try:
      ...
  except Exception as e:
      return PodcastResult(error=e)
  ```
- Return `PodcastResult(script_path=script_out, audio_path=Path(saved))` on success.
- Return `PodcastResult(script_path=script_out)` when `skip_audio=True`.

**Done**:

```
PYTHONPATH=src python -c \
  "from endpoints.podcast import generate_chapter_podcast
r = generate_chapter_podcast(__import__('pathlib').Path('/nonexistent.pdf'))
assert not r.ok
assert r.error is not None
print('ok')"
# exits 0; missing PDF returns PodcastResult with ok=False — no raise, no print, no sys.exit

grep "def run_local\|def run_llm\|def run_tts" src/run_chapter.py
# returns empty (definitions removed)

grep "_SRC\|_ROOT" src/endpoints/podcast.py
# returns hits confirming path constants are defined and used
```

---

### Pass 2.4 — generate_book_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_book_podcast()` |

**Function signature** **[v3] includes `slice_only` parameter**:
```python
def generate_book_podcast(
    book_pdf: Path | None = None,
    chapters_dir: Path | None = None,
    toc_page: int | None = None,
    no_ocr: bool = False,
    force: bool = False,
    llm: bool = False,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    slice_only: bool = False,
) -> list[PodcastResult]:
```

**[v5] Temporary `run_splitter` import** — no `sys.path.insert` (PYTHONPATH covers it):
```python
from slicer.pdf_splitter import run_splitter  # TODO: replace after Pass 3.2
```

After Pass 3.2, replace with `from endpoints.slicer import run_splitter`.

**[v3] `toc_page` handling** — the endpoint must never call `input()`:

```python
if toc_page is None:
    toc_page = load_config().get("toc_page")
if toc_page is None:
    raise ValueError("toc_page is required: pass it as a parameter or set it in config.json")
```

The interactive `toc_page` prompt belongs only in the CLI wrapper (Pass 2.5).

**[v3] `slice_only` behavior** — if `slice_only=True`, call `run_splitter`, then return
`[PodcastResult()]` without processing chapters:
```python
if slice_only:
    run_splitter(...)
    return [PodcastResult()]
```

**Chapter loop behavior**: Call `generate_chapter_podcast()` per chapter. A failed chapter
produces `PodcastResult(error=...)` — remaining chapters continue.

**Done**:

```
# Calling with a fixture book PDF returns list[PodcastResult]
# A chapter that fails produces PodcastResult with .ok == False; remaining chapters still run
# After Pass 3.2, update the slicer import and re-verify
```

---

### Pass 2.5 — Podcast CLI Wrapper

| File | Change |
|------|--------|
| `src/cli/__init__.py` | add — empty |
| `src/cli/podcast.py` | add — argparse wrapper |

**[v5] No `sys.path.insert` in this file** — `PYTHONPATH=src` (Pass 0.0) makes all
imports resolve correctly without path surgery.

**[v5] PYTHONPATH guard** — add at the top of `src/cli/podcast.py`, before any local
imports. Turns a silent `ModuleNotFoundError` into an actionable message:

```python
import sys
from pathlib import Path
if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/podcast.py ..."
    )
```

This is detection, not a patch — it does not add anything to `sys.path`.

**Routing logic**: `--book PDF` is the router flag. Absent → routes to
`generate_chapter_podcast()` using positional `pdf`. Present → routes to
`generate_book_podcast()`.

**Full argument surface**:

Chapter flags:
- `pdf` (positional)
- `--llm`
- `--skip-audio`
- `--mode`
- `--context`
- `--context-file`
- `--fiction-dir`

Book flags:
- `--book`
- `--toc-page`
- `--no-ocr`
- `--force`
- `--slice-only`

**[v4] `--mode` choices** — use the full set for chapter routing, the restricted set for
book routing:

```python
CHAPTER_MODES = ["2person", "4person", "code", "realworld", "fiction_meta"]
BOOK_MODES    = ["2person", "4person", "code", "realworld"]
# fiction_meta requires per-chapter fiction files; not supported in batch
```

After parsing, if `args.book` is set and `args.mode == "fiction_meta"`, print an error and
`sys.exit(1)` — `fiction_meta` is not supported in book mode.

**[v4] `--fiction-dir` handling** — the endpoint owns discovery; the CLI just passes the path:

```python
fiction_dir = Path(args.fiction_dir) if args.fiction_dir else None
# Pass to generate_chapter_podcast(fiction_dir=fiction_dir)
```

**`--context-file` handling** — read the file content and pass as `context`:
```python
if args.context_file:
    context = Path(args.context_file).read_text(encoding="utf-8").strip()
```

**[v3] `--slice-only` routing**: pass `slice_only=True` to `generate_book_podcast()`.

**[v3] Interactive `toc_page` prompt** (the only place it may appear):
```python
if args.book and args.toc_page is None:
    try:
        toc_page = int(input("TOC page number: "))
    except (ValueError, EOFError):
        toc_page = None
else:
    toc_page = args.toc_page
```

Print result paths to stdout. Print errors to stderr. `sys.exit(1)` on any failure.

**Done**:

```
PYTHONPATH=src python src/cli/podcast.py --help
# exits 0; shows both `pdf` positional and `--book` flag

PYTHONPATH=src python src/cli/podcast.py <fixture_pdf>
# produces identical output to PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
```

---

## Phase 3 — TTS Engine Cleanup + Slicer Endpoint

**Goal**: `tts/cli.py` `main()` is a clean engine function with no argparse. Slicer has a
stable import path. Pass 2.4's temporary import is upgraded.

---

### Pass 3.1 — TTS Engine Boundary

| File | Change |
|------|--------|
| `src/tts/cli.py` | modify — move `import argparse` from module level into `cli_entrypoint()` body |

The only change required is moving that one import line. `main()` already has the correct
signature. `cli_entrypoint()` already exists. Locate the module-level argparse import with:
`grep -n "^import argparse" src/tts/cli.py`

**Done**:

```
grep "argparse" src/tts/cli.py
# returns hits only inside cli_entrypoint()

grep "sys.exit" src/tts/cli.py
# returns hits only inside cli_entrypoint()
```

---

### Pass 3.2 — Slicer Import Anchor

| File | Change |
|------|--------|
| `src/endpoints/slicer.py` | add |

**[v5] Full content of `src/endpoints/slicer.py`** — no `sys.path.insert` (PYTHONPATH
from Pass 0.0 makes `slicer.pdf_splitter` resolvable):

```python
from slicer.pdf_splitter import run_splitter  # noqa: E402

__all__ = ["run_splitter"]
```

After this pass, update `src/endpoints/podcast.py`: replace the temporary direct import
from Pass 2.4 with `from endpoints.slicer import run_splitter`.

**Done**:

```
PYTHONPATH=src python -c "from endpoints.slicer import run_splitter; print('ok')"
# exits 0

grep "TODO.*Pass 3.2" src/endpoints/podcast.py
# returns empty (temporary import replaced)
```

---

## Phase 4 — Novel Pipeline Callback Refactor

**Goal**: `session.py` has no `input()` in the chapter-approval path, no `sys.exit()`.
Approval injected via callable. Tests drive the session without touching stdin.

---

### Pass 4.1 — SessionResult Dataclass + Callback Type

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — add `ApproveChapterFn` type alias; add `SessionResult` dataclass |

**Definitions to add** (no behavior change in this pass):
```python
from typing import Callable
from dataclasses import dataclass

ApproveChapterFn = Callable[[int, str], bool]
# args: (chapter_number, full_chapter_text) → True = approve, False = reject

@dataclass
class SessionResult:
    chapters_written: int
    final_chapter_number: int
    cost_usd: float
    completed: bool
    state_path: Path
```

`cost_usd` is populated from `current_totals(config)["session_total"]` (already imported).
`state_path` is populated from `Path(config["state_file_path"])`.

`Callable` and `dataclass` imports need to be added; `Path` is already imported.

**Done**:

```
PYTHONPATH=src python -c \
  "from fiction.pipeline.novel_pipeline.session import SessionResult, ApproveChapterFn; print('ok')"
# exits 0
```

---

### Pass 4.2 — session.py Callback Injection

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — inject callback; replace `sys.exit(1)` with `raise`; convert draft-preview prints to logger; return `SessionResult`; thread callback to `_run_one_chapter()` |

**Changes in detail:**

1. Add `approve_chapter: ApproveChapterFn = lambda n, text: True` parameter to
   `run_session()`.

2. Add `approve_chapter: ApproveChapterFn` parameter to `_run_one_chapter()`. Pass it
   through from `run_session()` at the `_run_one_chapter(...)` call site.

3. Inside `_run_one_chapter()`: replace the entire approval block — both the
   `auto_approve` fast-path and the `input("Approve and update living doc? [y/n/q]: ")`
   branch — with:
   ```python
   approved = approve_chapter(chapter_num, chapter_text)
   if not approved:
       # rejected: log and continue for regeneration
       log_event("chapter_rejected", {"chapter": chapter_num, "attempt": attempt})
       print(f"Rejected. Draft remains at {draft_path}. Attempt {attempt}/{max_rejections}.")
       chapter_text = None
       continue
   break  # approved
   ```
   `True` → proceeds to promotion; `False` → rejected (loops for regeneration);
   `KeyboardInterrupt` (raised by the callback on `q`) → propagates to caller.

   **[v4] The `[auto-approve] approving draft` print** that was in the old `auto_approve`
   fast-path is removed with the block. It is not converted to a logger call — it simply
   does not appear under callback-based approval.

4. Convert the draft-preview print block to `logger.info(...)`. Locate it with:
   `grep -n "Draft saved\|draft_path" src/fiction/pipeline/novel_pipeline/session.py`

5. Replace `sys.exit(1)` in `except KeyboardInterrupt:` with `raise KeyboardInterrupt`
   so it propagates to the caller. Locate it with:
   `grep -n "KeyboardInterrupt" src/fiction/pipeline/novel_pipeline/session.py`

6. **[v4] Return `SessionResult` at the 2 early-exit points and the normal completion
   fall-through** — the current code has exactly 2 early `return` statements plus the
   post-loop fall-through. Locate the early exits with:
   `grep -n "should_continue\|Proceed" src/fiction/pipeline/novel_pipeline/session.py`

   - Early exit when `should_continue` is False →
     `return SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False, state_path=Path(config["state_file_path"]))`
   - Early exit when "Proceed?" is declined → same pattern
   - Normal completion (post-loop fall-through) →
     `return SessionResult(chapters_written=completed, final_chapter_number=current_chapter, cost_usd=current_totals(config)["session_total"], completed=True, state_path=Path(config["state_file_path"]))`

**[v3] `input()` Done condition — scope clarification**:

`session.py` also contains `_prompt_yes_no()` and `_prompt_choice()`, both of which call
`input()`. These helpers are gated by `auto=True` paths and are intentionally preserved
for interactive use.

```
grep "input()" src/fiction/pipeline/novel_pipeline/session.py | \
  grep -v "_prompt_yes_no\|_prompt_choice"
# returns empty

grep "sys.exit" src/fiction/pipeline/novel_pipeline/session.py
# returns empty

# Behavioral test:
# run_session(config, auto_approve=True, approve_chapter=lambda n, t: True)
# completes without touching stdin
```

---

### Pass 4.3 — Shared Prompt Helper + novel_pipeline cli.py Update

| File | Change |
|------|--------|
| `src/util/prompt.py` | add — `prompt_user()` function |
| `src/fiction/pipeline/novel_pipeline/cli.py` | modify — add `approve_fn`; pass `approve_chapter=approve_fn` to `run_session()`; import `prompt_user` |

**[v5] Extract to `src/util/prompt.py`** — both `cli/fiction.py` (Pass 4.5) and
`novel_pipeline/cli.py` need this function. Extract it once here rather than duplicating:

```python
# src/util/prompt.py

def prompt_user(chapter_num: int, draft_text: str) -> bool:
    print(f"Chapter {chapter_num} draft (first 500 chars):\n{draft_text[:500]}\n")
    choice = input("[y/n/q]: ").strip().lower()
    if choice == "q":
        raise KeyboardInterrupt
    return choice == "y"
```

**[v3] `q` quit semantics**: `q` raises `KeyboardInterrupt`, which propagates to
`run_session()`'s existing `except KeyboardInterrupt` handler — the correct quit path.
Do not return `False` for `q` — that would loop for regeneration.

**`novel_pipeline/cli.py` update**:

> The `--auto-approve` flag already exists and is already wired. Do NOT add it again.

1. Import `prompt_user`:
   ```python
   from util.prompt import prompt_user
   ```

2. After parsing args, construct:
   ```python
   if args.auto_approve:
       approve_fn = lambda n, t: True
   else:
       approve_fn = prompt_user
   ```

3. Pass `approve_chapter=approve_fn` to `run_session()`.

**Done**:

```
PYTHONPATH=src python -c "from util.prompt import prompt_user; print('ok')"
# exits 0

PYTHONPATH=src python src/fiction/pipeline/novel_pipeline/cli.py \
  --auto-approve <config>
# runs without any stdin prompts
```

---

### Pass 4.4 — Fiction Endpoint Wrapper

| File | Change |
|------|--------|
| `src/endpoints/fiction.py` | add |

**[v5] No `sys.path.insert`** — `PYTHONPATH=src` covers all imports.

**Import resolution** — `novel_pipeline.egg-info` is present at
`src/fiction/pipeline/novel_pipeline.egg-info/`, which means the package was installed in
editable mode into the venv. With the venv active, the egg-link makes `novel_pipeline`
importable regardless of PYTHONPATH:

```python
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult
```

**[v5] No fallback `sys.path.insert`** — if the import fails, the fix is to reinstall the
package (`pip install -e .` from `src/fiction/pipeline/`), not to add a runtime path hack.
A fallback sys.path.insert here would contradict Pass 0.0's convention. Delete it.

> The TOML loader is `load_config(path)` in `novel_pipeline/config.py`. There is no
> `load_config_toml()` alias — do not create one.

**Function signature**:
```python
def run_novel_session(
    config_path: str | Path,
    resume: bool = False,
    auto_approve: bool = False,
    dry_run: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: ApproveChapterFn | None = None,
) -> SessionResult:
```

**Implementation**:
```python
def run_novel_session(config_path, resume=False, auto_approve=False,
                      dry_run=False, chapter_start=None,
                      ignore_cost_limit=False, approve_chapter=None) -> SessionResult:
    config = load_config(str(config_path))
    if approve_chapter is None:
        approve_chapter = lambda n, t: True
    return run_session(
        config,
        resume=resume,
        auto_approve=auto_approve,
        dry_run=dry_run,
        chapter_start=chapter_start,
        ignore_cost_limit=ignore_cost_limit,
        approve_chapter=approve_chapter,
    )
```

**Done**:

```
PYTHONPATH=src python -c \
  "from endpoints.fiction import run_novel_session; print('ok')"
# exits 0

# Calling run_novel_session(..., approve_chapter=lambda n, t: n != 2)
# rejects chapter 2 without touching stdin
```

---

### Pass 4.5 — Fiction CLI Shim

| File | Change |
|------|--------|
| `src/cli/fiction.py` | add — thin argparse wrapper |

**[v5] No `sys.path.insert`** — `PYTHONPATH=src` covers all imports.

**[v5] PYTHONPATH guard** — same guard as Pass 2.5, add at the top of `src/cli/fiction.py`:

```python
import sys
from pathlib import Path
if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/fiction.py ..."
    )
```

Mirror the exact flag set from `src/fiction/pipeline/novel_pipeline/cli.py`:
`--config` (required), `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start`,
`--ignore-cost-limit`.

**[v5] Import `prompt_user` from `src/util/prompt.py`** — do NOT redefine it here:
```python
from util.prompt import prompt_user
```

Construct `approve_fn` the same way as Pass 4.3. Call `run_novel_session()` from
`src/endpoints/fiction.py`.

**Done**:

```
PYTHONPATH=src python src/cli/fiction.py --help
# exposes the same flags as src/fiction/pipeline/novel_pipeline/cli.py

PYTHONPATH=src python src/cli/fiction.py --auto-approve <config>
# produces no stdin prompts
```

---

## Phase 5 — Cleanup

**Goal**: Dead code removed. Root-level entry points shimmed. README reflects new CLI paths.

---

### Pass 5.1 — Remove Private Config Loaders

**Pre-condition**: Pass 1.1 is complete and all four files use `load_config` from
`src/config.py`. Verify with:
```
grep -rn "from config import load_config" src/run_chapter.py src/run_book.py \
  src/tts/cli.py src/podcast_script_generator/llm/call_api.py
```
Must return 4 hits before proceeding.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — delete `_load_config()` definition |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — same |
| `src/podcast_script_generator/llm/call_api.py` | modify — same |

Locate each definition with:
`grep -n "def _load_config" src/run_chapter.py src/run_book.py src/tts/cli.py src/podcast_script_generator/llm/call_api.py`

**Done**:

```
grep -rn "_load_config" src/
# returns empty
```

---

### Pass 5.2 — Delete run_simple.py

| File | Change |
|------|--------|
| `src/fiction/run_simple.py` | delete |

Verify no remaining imports first:
```
grep -rn "run_simple" src/
# must return empty before deletion
```

The file uses `sys.exit()`, `input()`, and hardcoded global config — none of these need
cleanup before deletion. It is an orphaned prototype superseded by the novel_pipeline.

**Done**:

```
ls src/fiction/run_simple.py
# returns "No such file"

grep -rn "run_simple" src/
# returns empty
```

---

### Pass 5.3 — Shim run_chapter.py and run_book.py

**Pre-conditions** — verify ALL of these before proceeding:

1. Passes 2.3, 2.4, and 2.5 are complete.
2. `src/cli/podcast.py` has all book-level flags:
   ```
   PYTHONPATH=src python src/cli/podcast.py --help | grep -- "--book"
   # returns a hit
   ```
3. **[v3] Helper functions have been moved**: `run_local`, `run_llm`, `run_tts` are in
   `endpoints/podcast.py`, NOT in `run_chapter.py`. Verify:
   ```
   grep "def run_local\|def run_llm\|def run_tts" src/endpoints/podcast.py
   # returns 3 hits

   grep "def run_local\|def run_llm\|def run_tts" src/run_chapter.py
   # returns empty
   ```

> **Critical**: Apply BOTH shims in the same commit. `run_book.py` depends on
> `run_chapter.py`'s helpers which no longer exist after shimming. If `run_chapter.py`
> is shimmed first alone, `run_book.py` breaks at its `import run_chapter as rc` line.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — replace entire body with `from cli.podcast import main; main()` |
| `src/run_book.py` | modify — replace entire body with `from cli.podcast import main; main()` |

**Done**:

```
PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# produces output identical to:
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf>

PYTHONPATH=src python src/run_book.py --help
# exits 0 and exposes the --book flag
```

---

### Pass 5.4 — Update initial_readme.md

| File | Change |
|------|--------|
| `src/initial_readme.md` | modify — update Entry Points section |

List `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs. Document
`run_chapter.py` and `run_book.py` as shims forwarding to `src/cli/podcast.py`. Document
the `PYTHONPATH=src` invocation convention.

**Done**:

```
grep "src/cli/podcast.py" src/initial_readme.md
# returns a hit

grep "PYTHONPATH" src/initial_readme.md
# returns a hit
```

---

## Phase 6 — Behavioral Verification

**Goal**: Confirm end-to-end behavior of each new endpoint with lightweight behavioral
checks that go beyond grep-based Done conditions. No test framework required.

---

### Pass 6.1 — Podcast Endpoint Smoke Tests

Run each check in order. All should exit 0.

```bash
# Import surface
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast, generate_book_podcast, \
  ScriptMode, PodcastResult
from endpoints.slicer import run_splitter
print('import ok')
"

# PodcastResult invariant — ok computed from error
PYTHONPATH=src python -c "
from endpoints.podcast import PodcastResult
from pathlib import Path
r1 = PodcastResult(error=ValueError('x'))
r2 = PodcastResult(script_path=Path('/tmp/x'))
r3 = PodcastResult()
assert not r1.ok, 'ok should be False when error is set'
assert r2.ok,     'ok should be True when error is None'
assert r3.ok,     'empty PodcastResult should be ok'
print('PodcastResult invariants ok')
"

# Missing PDF returns failure, not exception
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
r = generate_chapter_podcast(Path('/nonexistent/file.pdf'))
assert not r.ok
assert r.error is not None
print('missing PDF handled gracefully ok')
"

# fiction_meta without fiction_dir returns failure
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
r = generate_chapter_podcast(Path('/nonexistent/file.pdf'), mode='fiction_meta')
assert not r.ok
assert 'fiction_dir' in str(r.error)
print('fiction_meta validation ok')
"
```

---

### Pass 6.2 — Fiction Endpoint Smoke Tests

```bash
# Import surface
PYTHONPATH=src python -c "
from endpoints.fiction import run_novel_session
from util.prompt import prompt_user
print('import ok')
"

# prompt_user module is importable by both cli.fiction and novel_pipeline.cli
PYTHONPATH=src python -c "
from util.prompt import prompt_user
import inspect
sig = inspect.signature(prompt_user)
params = list(sig.parameters)
assert params == ['chapter_num', 'draft_text'], f'unexpected signature: {params}'
print('prompt_user signature ok')
"
```

---

### Pass 6.3 — Shim Equivalence Check

Run after Pass 5.3.

```bash
# Both shims expose --book flag
PYTHONPATH=src python src/run_chapter.py --help | grep -q "\-\-help" && echo "run_chapter shim ok"
PYTHONPATH=src python src/run_book.py --help | grep -q "\-\-book" && echo "run_book shim ok"

# No private symbols escape into shim namespace
python -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('rc', 'src/run_chapter.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
leaked = [x for x in dir(mod) if not x.startswith('_') and x not in ('main',)]
assert leaked == [], f'unexpected symbols in shim: {leaked}'
print('no symbol leakage ok')
"
```

---

## Appendix — Cross-Phase Dependencies

| Dependency | Consumer | Provider |
|------------|----------|----------|
| `PYTHONPATH=src` invocation model in place | All passes | Pass 0.0 |
| `src/config.py` exists | Passes 1.2–5.1 | Pass 1.1 |
| `_load_config()` call sites renamed (all 9 across 4 files) | Pass 5.1 Done condition | Pass 1.1 |
| `PodcastError` hierarchy exists | Passes 2.3, 2.5 | Pass 1.2 |
| `src/util/normalize.py` exists | Pass 2.3 | Pass 2.1 |
| `PodcastResult`, `ScriptMode` defined with correct types (`ok` as property) | Pass 2.3 | Pass 2.2 |
| `run_local/run_llm/run_tts` moved into `endpoints/podcast.py` | Pass 5.3 pre-condition | Pass 2.3 |
| `generate_chapter_podcast()` has `fiction_dir` param and owns discovery | Pass 2.4, 2.5 | Pass 2.3 |
| `generate_chapter_podcast()` exists | Passes 2.4, 2.5 | Pass 2.3 |
| `generate_book_podcast()` has `slice_only` param | Pass 2.5 | Pass 2.4 |
| `src/endpoints/slicer.py` exists | Pass 2.4 import upgrade | Pass 3.2 |
| `src/cli/podcast.py` has full book flags incl. `--slice-only` | Pass 5.3 pre-condition | Pass 2.5 |
| `SessionResult` + `ApproveChapterFn` defined | Pass 4.2 | Pass 4.1 |
| `approve_chapter` wired in `run_session()` + `_run_one_chapter()` | Passes 4.3, 4.4 | Pass 4.2 |
| `src/util/prompt.py` exists | Passes 4.3, 4.5 | Pass 4.3 |
| `run_novel_session()` exists | Pass 4.5 | Pass 4.4 |
| All four files use shared `load_config` | Pass 5.1 | Pass 1.1 |
| `src/endpoints/podcast.py` has full book logic | Pass 5.3 | Pass 2.4 |
