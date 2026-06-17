# Build Specs v4 — CLI / Endpoints / Engines Refactor

> Derived from `build_specsv3.md` + `implementation_journalv3.md` (paper-run decisions).
> v4 closes spec gaps found during the v3 paper run: names every implicit call site, provides
> every import path, resolves one signature contradiction, and corrects one return-count error.
>
> Changes from v3 are marked with **[v4]** in the relevant section.
> All prior **[v3]** markers are retained where they were already correct.
>
> Each pass names every file touched, the change type (add / modify / delete), and a
> done condition. Passes within a phase are ordered; complete each pass before the next.

---

## Gap Index (v3 → v4)

| Gap | Severity | Fixed In |
|-----|----------|----------|
| `run_chapter.py` line 157 and `run_book.py` line 97 each have an unnamed `_load_config()` call site — caught by Done condition grep but not mentioned in spec prose | Low | Pass 1.1 |
| `tts/cli.py` exception import path not given (`podcast_script_generator.llm.exceptions`) | Low | Pass 1.2 |
| 5th print in `send_to_api()` — `[done]` confirmation on completion — missing from spec prose list but caught by Done condition grep | Low | Pass 1.3 |
| `endpoints/podcast.py` needs its own `sys.path.insert` + `from config import load_config` after helper move — spec omits this | Medium | Pass 2.3 |
| `ROOT`/`SRC` path constants resolve incorrectly after helper move to `endpoints/podcast.py` — spec says "move helpers" but omits constant recomputation | Medium | Pass 2.3 |
| Contradiction: spec says "keep fiction-dir discovery in endpoint" but endpoint signature took `fiction_content: str` (pre-loaded) — incompatible | High | Pass 2.3 / 2.5 |
| `fiction_meta` mode not excluded from book-mode `--mode` choices | Low | Pass 2.5 |
| `[auto-approve] approving draft` print inside `_run_one_chapter()` silently disappears when approval block is replaced by callback — fate unspecified | Low | Pass 4.2 |
| Spec states "minimum 3 early-exit return points" in `run_session()` — actual code has 2 early-exit returns; spec overcounts | Low | Pass 4.2 |

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
| `src/tts/cli.py` | modify — remove `_load_config()` definition; add path-insert + `from config import load_config`; **[v3] rename 3 call sites** |
| `src/podcast_script_generator/llm/call_api.py` | modify — remove `_load_config()` definition; add path-insert + `from config import load_config`; **[v3] rename 4 call sites** |

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

The default path is anchored to `src/config.py`'s own location — resolves correctly
regardless of the caller's working directory.

**Import pattern for `src/tts/cli.py`** (one level below `src/`):

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # adds src/ to path
from config import load_config
```

**Import pattern for `src/podcast_script_generator/llm/call_api.py`** (three levels below `src/`):

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # adds src/ to path
from config import load_config
```

`src/run_chapter.py` and `src/run_book.py` compute `SRC = Path(__file__).parent` (IS `src/`).
They need no path-insert — `from config import load_config` works as-is.

**[v3] Call-site renames for `tts/cli.py` and `call_api.py`** — removing the definition alone leaves broken calls:

- `src/tts/cli.py`: rename `_load_config()` → `load_config()` at 3 call sites inside
  `build_api_payload()`, `send_to_api()`, and `cli_entrypoint()`.
- `src/podcast_script_generator/llm/call_api.py`: rename at 4 call sites inside the
  resolver functions (lines ~33, 40, 47, 62 in the current source).

**[v4] Call-site renames for `run_chapter.py` and `run_book.py`** — these files also have call sites beyond their definitions:

- `src/run_chapter.py`: rename `_load_config()` → `load_config()` at 1 call site inside
  `run_tts()` (line ~157: `cfg_speakers = _load_config().get("speakers", {})`).
- `src/run_book.py`: rename `_load_config()` → `load_config()` at 1 call site inside
  `main()` (line ~97: `toc_page = args.toc_page or _load_config().get("toc_page")`).

> Note: the novel_pipeline has a completely separate TOML-based `load_config()` in
> `src/fiction/pipeline/novel_pipeline/config.py`. That loader is NOT related to
> `src/config.py` and must not be modified.

**Done**:
```
python -c "from src.config import load_config; print(load_config())"
# exits 0

python src/run_chapter.py --help
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

**[v4] Exception import path for `tts/cli.py`** — Pass 1.1 added
`sys.path.insert(0, str(Path(__file__).parent.parent))` which puts `src/` on the path.
From `src/`, the full dotted import path is:

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

python src/run_chapter.py <fixture_pdf>
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
| `src/run_chapter.py` | modify — delete `_to_speaker_format()` definition (lines 55–117); update 3 call sites; add import |

**What to extract**: the function is named `_to_speaker_format` in the current code —
this pass is an extraction AND a rename to `normalize_speakers`.

**Three call sites to update in `run_chapter.py`**:
- `run_local()` — line ~127
- `run_llm()` — lines ~145 and ~146 (one for `fiction_meta` branch, one for all other modes)

**Import to add**:
```python
from util.normalize import normalize_speakers
```

(`run_chapter.py` is in `src/` — no path-insert needed.)

**Done**:

```
python -c "from src.util.normalize import normalize_speakers; print(normalize_speakers('ALEX: hi'))"
# exits 0; returns a Speaker 0:-prefixed line

python src/run_chapter.py <fixture_pdf>
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

**`PodcastResult` fields**:
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PodcastResult:
    ok: bool
    script_path: Path | None = None
    audio_path: str | None = None
    error: Exception | None = None
```

**Done**:

```
python -c "from src.endpoints.podcast import ScriptMode, PodcastResult; print('ok')"
# exits 0
```

---

### Pass 2.3 — generate_chapter_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_chapter_podcast()`; **[v3]** move `run_local`, `run_llm`, `run_tts` helper functions; **[v4]** add `_SRC`/`_ROOT` constants and `load_config` import |

**[v4] Path constants and `load_config` import** — `endpoints/podcast.py` is one level below
`src/`, so the same `sys.path.insert` pattern from Pass 1.1 applies. Add near the top of the
file, before any local imports:

```python
import sys
from pathlib import Path

_SRC  = Path(__file__).parent.parent        # src/
_ROOT = Path(__file__).parent.parent.parent  # harnessv3/

sys.path.insert(0, str(_SRC))  # makes src/ importable as a package root
from config import load_config  # noqa: E402
```

Use `_SRC` and `_ROOT` throughout this file instead of bare `SRC`/`ROOT` names to avoid
collision with caller namespaces. Also update the output path constants that move here with
the helpers:

```python
_SCRIPTS_OUT = _ROOT / "data" / "output" / "scripts"
_AUDIO_OUT   = _ROOT / "data" / "output" / "audio"
```

**[v4] Updated function signature** — `fiction_content: str | None` is replaced by
`fiction_dir: Path | None`. The endpoint performs the chapter-file discovery internally so
that a programmatic caller does not need to implement it:

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

**[v4] Fiction-dir discovery inside the endpoint** — this block runs before the script
generation call when `mode == "fiction_meta"`:

```python
fiction_content: str | None = None
if mode == "fiction_meta":
    if fiction_dir is None:
        return PodcastResult(ok=False, error=ValueError(
            "mode 'fiction_meta' requires fiction_dir"))
    if not fiction_dir.is_dir():
        return PodcastResult(ok=False, error=ValueError(
            f"fiction directory not found: {fiction_dir}"))
    chapter_num_match = re.match(r"^(\d+)", pdf_path.stem)
    if not chapter_num_match:
        return PodcastResult(ok=False, error=ValueError(
            f"cannot extract chapter number from PDF stem: {pdf_path.stem}"))
    chapter_num = int(chapter_num_match.group(1))
    fiction_file = fiction_dir / f"chapter_{chapter_num:02d}.md"
    if not fiction_file.exists():
        candidates = sorted(fiction_dir.glob(f"*{chapter_num_match.group(1)}*.md"))
        if not candidates:
            return PodcastResult(ok=False, error=ValueError(
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

`run_book.py` currently calls them as `rc.run_llm()` etc. After this pass, `run_book.py`
needs a temporary re-import until it is shimmed in Pass 5.3:
```python
from endpoints.podcast import run_llm, run_local, run_tts
```

(This temporary import is removed when Pass 5.3 shims `run_book.py`.)

**Endpoint body construction**:
- Copy `run_chapter.py`'s `main()` body verbatim into `generate_chapter_podcast()`.
- Strip: all `argparse` setup (lines 168–186), all `print()` calls, all `sys.exit()` calls.
- The fiction-dir block (lines 207–231) is replaced entirely by the **[v4] discovery block**
  above — do not port the `sys.exit()` version.
- The realworld context block (lines 194–205) stays; remap `args.context` → `context`
  parameter and `sys.exit()` paths → `return PodcastResult(ok=False, error=...)`.
- Wrap entire body in:
  ```python
  try:
      ...
  except Exception as e:
      return PodcastResult(ok=False, error=e)
  ```
- Return `PodcastResult(ok=True, script_path=script_out, audio_path=saved)` on success.
- Return `PodcastResult(ok=True, script_path=script_out)` when `skip_audio=True`.

**Done**:

```
python -c "from src.endpoints.podcast import generate_chapter_podcast; print('ok')"
# exits 0; calling with missing PDF returns PodcastResult(ok=False, ...) — no raise, no print, no sys.exit

grep "run_local\|run_llm\|run_tts" src/run_chapter.py
# returns empty (definitions removed)

grep "def _SRC\|def _ROOT\|def _SCRIPTS_OUT\|def _AUDIO_OUT" src/endpoints/podcast.py
# returns empty (these are constants, not functions — grep confirms they exist as assignments)

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

**Temporary `run_splitter` import** (Pass 3.2 has not run yet):
```python
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).parent.parent))
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
`[PodcastResult(ok=True)]` without processing chapters:
```python
if slice_only:
    run_splitter(...)
    return [PodcastResult(ok=True)]
```

**Chapter loop behavior**: Call `generate_chapter_podcast()` per chapter. A failed chapter
produces `PodcastResult(ok=False, ...)` — remaining chapters continue.

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

**[v4] `--mode` choices** — use the full set for chapter routing, the restricted set for book
routing:

```python
CHAPTER_MODES = ["2person", "4person", "code", "realworld", "fiction_meta"]
BOOK_MODES    = ["2person", "4person", "code", "realworld"]
# fiction_meta requires per-chapter fiction files; not supported in batch
```

After parsing, if `args.book` is set and `args.mode == "fiction_meta"`, print an error and
`sys.exit(1)` — `fiction_meta` is not supported in book mode.

**[v4] `--fiction-dir` handling** — the endpoint now takes `fiction_dir: Path | None` and
performs the file discovery internally. The CLI wrapper simply passes the path:

```python
fiction_dir = Path(args.fiction_dir) if args.fiction_dir else None
# Pass to generate_chapter_podcast(fiction_dir=fiction_dir)
```

Do NOT read or resolve the fiction file in the CLI wrapper. The endpoint owns discovery.

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
python src/cli/podcast.py --help
# exits 0; shows both `pdf` positional and `--book` flag

python src/cli/podcast.py <fixture_pdf>
# produces identical output to python src/run_chapter.py <fixture_pdf>
```

---

## Phase 3 — TTS Engine Cleanup + Slicer Endpoint

**Goal**: `tts/cli.py` `main()` is a clean engine function with no argparse. Slicer has a
stable import path. Pass 2.4's temporary import is upgraded.

---

### Pass 3.1 — TTS Engine Boundary

| File | Change |
|------|--------|
| `src/tts/cli.py` | modify — move `import argparse` from module level (line 6/7) into `cli_entrypoint()` body |

The only change required is moving that one import line. `main()` already has the correct
signature. `cli_entrypoint()` already exists.

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

**Full content of `src/endpoints/slicer.py`**:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # adds src/ to path
from slicer.pdf_splitter import run_splitter            # noqa: E402

__all__ = ["run_splitter"]
```

The `sys.path.insert` is required: running from `harnessv3/` means `sys.path` contains
`harnessv3/`, not `harnessv3/src/`. Without the insert, Python looks for
`harnessv3/slicer/` which does not exist.

After this pass, update `src/endpoints/podcast.py`: replace the temporary direct import
from Pass 2.4 with `from endpoints.slicer import run_splitter`.

**Done**:

```
python -c "from src.endpoints.slicer import run_splitter; print('ok')"
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
python -c "from src.fiction.pipeline.novel_pipeline.session import SessionResult, ApproveChapterFn; print('ok')"
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
   does not appear under callback-based approval. The caller's `approve_fn` is a `lambda`
   that returns `True` silently when `auto_approve=True`.

4. Convert the draft-preview print block (lines ~709–712) to `logger.info(...)`.

5. Replace `sys.exit(1)` in `except KeyboardInterrupt:` (line ~574) with
   `raise KeyboardInterrupt` so it propagates to the caller.

6. **[v4] Return `SessionResult` at the 2 early-exit points and the normal completion
   fall-through** — the current code has exactly 2 early `return` statements plus the
   post-loop fall-through:

   - Early exit when `should_continue` is False →
     `return SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False, state_path=Path(config["state_file_path"]))`
   - Early exit when "Proceed?" is declined → same pattern
   - Normal completion (post-loop fall-through) →
     `return SessionResult(chapters_written=completed, final_chapter_number=current_chapter, cost_usd=current_totals(config)["session_total"], completed=True, state_path=Path(config["state_file_path"]))`

   Do not add additional return points; the `break` paths inside the loop fall through to
   the post-loop code and are covered by the single fall-through return.

**[v3] `input()` Done condition — scope clarification**:

`session.py` also contains `_prompt_yes_no()` (line ~68) and `_prompt_choice()` (lines
~105–106), both of which call `input()`. These helpers are gated by `auto=True` paths that
never reach `input()` under `auto_approve=True`, and are intentionally preserved for
interactive use.

Use the scoped grep as the practical Done condition:

```
grep "input()" src/fiction/pipeline/novel_pipeline/session.py | grep -v "_prompt_yes_no\|_prompt_choice"
# returns empty

grep "sys.exit" src/fiction/pipeline/novel_pipeline/session.py
# returns empty

# Behavioral test:
run_session(config, auto_approve=True, approve_chapter=lambda n, t: True)
# completes without touching stdin
```

---

### Pass 4.3 — novel_pipeline cli.py Update

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/cli.py` | modify — add `_prompt_user()`; construct `approve_fn`; pass `approve_chapter=approve_fn` to `run_session()` |

> The `--auto-approve` flag already exists at line 47 and is already wired. Do NOT add it again.

1. Add `_prompt_user(chapter_num: int, draft_text: str) -> bool` that prints the first
   500 chars of `draft_text` and reads `[y/n/q]` from stdin.

2. **[v3] `q` quit semantics**: when the user enters `q`, `_prompt_user` raises
   `KeyboardInterrupt`. This propagates to `run_session()`'s existing `except KeyboardInterrupt`
   handler, which is the correct quit path. Do not return `False` for `q` — that would loop
   for regeneration instead of quitting.

   ```python
   def _prompt_user(chapter_num: int, draft_text: str) -> bool:
       print(f"Chapter {chapter_num} draft (first 500 chars):\n{draft_text[:500]}\n")
       choice = input("[y/n/q]: ").strip().lower()
       if choice == "q":
           raise KeyboardInterrupt
       return choice == "y"
   ```

3. After parsing args, construct:
   ```python
   if args.auto_approve:
       approve_fn = lambda n, t: True
   else:
       approve_fn = _prompt_user
   ```

4. Pass `approve_chapter=approve_fn` to `run_session()`.

**Done**:

```
python src/fiction/pipeline/novel_pipeline/cli.py --auto-approve <config>
# runs without any stdin prompts

# Interactive path (no --auto-approve) calls _prompt_user for each chapter
```

---

### Pass 4.4 — Fiction Endpoint Wrapper

| File | Change |
|------|--------|
| `src/endpoints/fiction.py` | add |

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

**Import resolution** — `novel_pipeline.egg-info` is present at
`src/fiction/pipeline/novel_pipeline.egg-info/`, so package imports should work with the
venv active:

```python
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult
```

If the package is not importable by that name, fall back to:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fiction" / "pipeline"))
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult
```

> The TOML loader is `load_config(path)` in `novel_pipeline/config.py`. There is no
> `load_config_toml()` alias — do not create one.

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
python -c "from src.endpoints.fiction import run_novel_session; print('ok')"
# exits 0

# Calling run_novel_session(..., approve_chapter=lambda n, t: n != 2)
# rejects chapter 2 without touching stdin
```

---

### Pass 4.5 — Fiction CLI Shim

| File | Change |
|------|--------|
| `src/cli/fiction.py` | add — thin argparse wrapper |

Mirror the exact flag set from `src/fiction/pipeline/novel_pipeline/cli.py`:
`--config` (required), `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start`,
`--ignore-cost-limit`.

Add the same `_prompt_user()` function as Pass 4.3 (same implementation — intentional
duplication; extraction to `src/util/` is out of scope). Construct `approve_fn` the same
way. Call `run_novel_session()` from `src/endpoints/fiction.py`.

**Done**:

```
python src/cli/fiction.py --help
# exposes the same flags as src/fiction/pipeline/novel_pipeline/cli.py

python src/cli/fiction.py --auto-approve <config>
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
   python src/cli/podcast.py --help | grep -- "--book"
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

> **Critical**: Apply BOTH shims in the same pass. `run_book.py` depends on
> `run_chapter.py`'s helpers which no longer exist after shimming. If `run_chapter.py` is
> shimmed first alone, `run_book.py` breaks at its `import run_chapter as rc` line.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — replace entire body with `from cli.podcast import main; main()` |
| `src/run_book.py` | modify — replace entire body with `from cli.podcast import main; main()` |

**Done**:

```
python src/run_chapter.py <fixture_pdf>
# produces output identical to python src/cli/podcast.py <fixture_pdf>

python src/run_book.py --help
# exits 0 and exposes the --book flag
```

---

### Pass 5.4 — Update initial_readme.md

| File | Change |
|------|--------|
| `src/initial_readme.md` | modify — update Entry Points section |

List `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs. Document
`run_chapter.py` and `run_book.py` as shims forwarding to `src/cli/podcast.py`.

**Done**:

```
grep "src/cli/podcast.py" src/initial_readme.md
# returns a hit

grep "shim" src/initial_readme.md
# returns a hit
```

---

## Appendix — Cross-Phase Dependencies

| Dependency | Consumer | Provider |
|------------|----------|----------|
| `src/config.py` exists | Passes 1.2–5.1 | Pass 1.1 |
| `_load_config()` call sites renamed (all 9 across 4 files) | Pass 5.1 Done condition | Pass 1.1 |
| `PodcastError` hierarchy exists | Passes 2.3, 2.5 | Pass 1.2 |
| `src/util/normalize.py` exists | Pass 2.3 | Pass 2.1 |
| `PodcastResult`, `ScriptMode` defined with full fields | Pass 2.3 | Pass 2.2 |
| `endpoints/podcast.py` has `_SRC`/`_ROOT` constants and `load_config` import | Pass 2.3 runtime | Pass 2.3 self |
| `run_local/run_llm/run_tts` moved into `endpoints/podcast.py` | Pass 5.3 pre-condition | Pass 2.3 |
| `generate_chapter_podcast()` has `fiction_dir` param and owns discovery | Pass 2.4, 2.5 | Pass 2.3 |
| `generate_chapter_podcast()` exists | Passes 2.4, 2.5 | Pass 2.3 |
| `generate_book_podcast()` has `slice_only` param | Pass 2.5 | Pass 2.4 |
| `src/endpoints/slicer.py` exists | Pass 2.4 import upgrade | Pass 3.2 |
| `src/cli/podcast.py` has full book flags incl. `--slice-only` | Pass 5.3 pre-condition | Pass 2.5 |
| `SessionResult` + `ApproveChapterFn` defined | Pass 4.2 | Pass 4.1 |
| `approve_chapter` wired in `run_session()` + `_run_one_chapter()` | Passes 4.3, 4.4 | Pass 4.2 |
| `run_novel_session()` exists | Pass 4.5 | Pass 4.4 |
| All four files use shared `load_config` | Pass 5.1 | Pass 1.1 |
| `src/endpoints/podcast.py` has full book logic | Pass 5.3 | Pass 2.4 |
