# Build Specs v2 — CLI / Endpoints / Engines Refactor

> Derived from `build_specs.md` (v1) + `implementation_journal.md` (paper-run findings).
> v2 corrects spec errors, supplies missing signatures, fixes broken Done conditions,
> and adds pre-conditions where pass ordering matters.
> Each pass names every file touched, the change type (add / modify / delete), and a
> done condition. Passes within a phase are ordered; complete each pass before the next.

---

## Phase 1 — Foundation

**Goal**: Config loading and exception hierarchy in place before any endpoints are written.
No behavior change to existing entry points.

---

### Pass 1.1 — Shared Config Loader

| File | Change |
|------|--------|
| `src/config.py` | add |
| `src/run_chapter.py` | modify — remove `_load_config()` definition; add path-insert + `from config import load_config` |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — remove `_load_config()` definition; add path-insert + `from config import load_config` |
| `src/podcast_script_generator/llm/call_api.py` | modify — remove `_load_config()` definition; add path-insert + `from config import load_config` |

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

The default path is anchored to `src/config.py`'s own location — this resolves correctly
regardless of the caller's working directory or how deep in the package tree the caller sits.

**Import pattern for `src/tts/cli.py`** (sits one level below `src/`):

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # adds src/ to path
from config import load_config
```

**Import pattern for `src/podcast_script_generator/llm/call_api.py`** (sits three levels below `src/`):

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # adds src/ to path
from config import load_config
```

`src/run_chapter.py` and `src/run_book.py` already compute `SRC = Path(__file__).parent`
(which IS `src/`). They need no additional path-insert — `from config import load_config`
works as-is.

> Note: the novel_pipeline has a completely separate TOML-based `load_config()` in
> `src/fiction/pipeline/novel_pipeline/config.py`. That loader is NOT related to the
> shared `src/config.py` created here and must not be modified.

**Done**: `python -c "from src.config import load_config; print(load_config())"` exits 0.
`python src/run_chapter.py --help` still works.
`grep -rn "_load_config" src/run_chapter.py src/run_book.py src/tts/cli.py src/podcast_script_generator/llm/call_api.py` returns empty.

---

### Pass 1.2 — Podcast Exception Hierarchy

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/exceptions.py` | add — `PodcastError`, `PDFExtractionError`, `ScriptGenerationError`, `TTSSubmissionError`, `TTSTimeoutError` |
| `src/podcast_script_generator/llm/main.py` | modify — `sys.exit()` calls → `raise PDFExtractionError` / `raise ScriptGenerationError`; add `if __name__ == "__main__":` guard that catches `PodcastError` and exits 1 |
| `src/tts/cli.py` | modify — remap existing local `AuthError` → `TTSSubmissionError`; remap `RuntimeError` (WaveSpeed failure) → `TTSSubmissionError`; remap timeout/network errors → `TTSTimeoutError`; update `cli_entrypoint()` to catch `PodcastError` instead of the scattered individual exception types |
| `src/run_chapter.py` | modify — catch `PodcastError` at CLI boundary; print error to stderr; `sys.exit(1)` |

> **Deviation from v1**: `tts/cli.py`'s `main()` function already raises exceptions and has
> zero `sys.exit()` calls. `cli_entrypoint()` already exists. The work for `tts/cli.py`
> is a type-remapping pass only — map existing raise sites to the new hierarchy, then
> broaden `cli_entrypoint()`'s catch to `PodcastError`.
>
> `main.py` in `podcast_script_generator/llm/` is a standalone orphan entry point.
> `run_chapter.py` does not call it — it imports the individual modules (`extract_pdf`,
> `call_api`, etc.) directly. Cleaning `main.py` satisfies the Done condition grep but
> has no effect on the runtime pipeline. Preserve runnable behavior via the `__main__`
> guard.

**Done**:
`grep -rn "sys.exit" src/podcast_script_generator/` returns empty (standalone `main.py`
now raises; its `__main__` guard calls `sys.exit` but grep skips lines inside `if __name__`
blocks — if not, exclude with `grep -v "__main__"`).
`grep "sys.exit" src/tts/cli.py` returns hits only inside `cli_entrypoint()`.
`grep "sys.exit" src/run_chapter.py` returns exactly one hit (the CLI boundary catch).

---

### Pass 1.3 — Structured Logging Migration

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/call_api.py` | modify — `print(f"OpenRouter 429 — waiting ...")` → `logger.debug(...)` |
| `src/podcast_script_generator/llm/save_output.py` | modify — add `import logging` and `logger = logging.getLogger(__name__)`; `print(f"Wrote N files ...")` → `logger.debug(...)` |
| `src/tts/cli.py` | modify — convert four prints in `send_to_api()` to logger calls: submission confirmation → `logger.info`; recovery-file notice → `logger.info`; polling start → `logger.info`; per-poll status → `logger.debug` |
| `src/run_chapter.py` | modify — add `logging.basicConfig(level=logging.INFO, format="%(message)s")` at entry |
| `src/run_book.py` | modify — same `logging.basicConfig` at entry |

> **Deviation from v1**: The prints targeted in `tts/cli.py` are at 8–12 spaces of
> indentation (inside `send_to_api()`'s `try:` block). v1's Done condition grep
> `^    print\|^print` matches only 0- or 4-space indentation and would silently miss
> them. Use the corrected grep below.

**Done**: `grep -rn "^\s*print(" src/podcast_script_generator/ src/tts/cli.py` returns
empty. Running `python src/run_chapter.py <fixture_pdf>` produces INFO-level output
without crashing.

---

## Phase 2 — Podcast Pipeline Endpoint

**Goal**: `generate_chapter_podcast()` and `generate_book_podcast()` are directly callable
with no argparse, no print, no sys.exit. CLI wrappers are thin.

---

### Pass 2.1 — Speaker Normalization Extract

| File | Change |
|------|--------|
| `src/util/__init__.py` | add — empty |
| `src/util/normalize.py` | add — `normalize_speakers(text: str) -> str` extracted from `run_chapter.py` |
| `src/run_chapter.py` | modify — delete `_to_speaker_format()` definition (lines 55–117); replace all three call sites (`run_local` line 127, `run_llm` lines 145 and 146) with `normalize_speakers(...)`; add `from util.normalize import normalize_speakers` |

> **Deviation from v1**: The function being extracted is named `_to_speaker_format` in
> the current code, not `normalize_speakers`. This pass is an extraction AND a rename.
> There are three call sites inside `run_chapter.py` that all require updating, not just
> the definition.

**Done**: `python -c "from src.util.normalize import normalize_speakers; print(normalize_speakers('ALEX: hi'))"` exits 0 and returns a `Speaker 0:`-prefixed line. `python src/run_chapter.py <fixture_pdf>` behavior unchanged.

---

### Pass 2.2 — Canonical Types

| File | Change |
|------|--------|
| `src/endpoints/__init__.py` | add — empty |
| `src/endpoints/podcast.py` | add — `ScriptMode` enum and `PodcastResult` dataclass with full field definitions |

**`ScriptMode` values** (mirror `run_chapter.py`'s `--mode` choices):
```python
class ScriptMode(str, Enum):
    TWO_PERSON    = "2person"
    FOUR_PERSON   = "4person"
    CODE          = "code"
    REALWORLD     = "realworld"
    FICTION_META  = "fiction_meta"
```

**`PodcastResult` fields** (inferred from Done conditions in Passes 2.3 and 2.4):
```python
@dataclass
class PodcastResult:
    ok: bool
    script_path: Path | None = None
    audio_path: str | None = None
    error: Exception | None = None
```

> **Deviation from v1**: v1 left fields unspecified. Defining them here prevents
> revisiting this file in Pass 2.3.

**Done**: `python -c "from src.endpoints.podcast import ScriptMode, PodcastResult; print('ok')"` exits 0.

---

### Pass 2.3 — generate_chapter_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_chapter_podcast()` |

**Function signature** (mirrors `run_chapter.py`'s argparse surface, argparse removed):
```python
def generate_chapter_podcast(
    pdf_path: Path,
    llm: bool = False,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    fiction_content: str | None = None,
) -> PodcastResult:
```

Move the body of `run_chapter.py`'s `main()` verbatim into this function, stripping all
`argparse`, `sys.exit()`, and `print()` calls. Wrap the entire body in `try/except`:
```python
    try:
        ...
    except Exception as e:
        return PodcastResult(ok=False, error=e)
```
Return `PodcastResult(ok=True, script_path=script_out, audio_path=saved)` on success.

The context-file loading logic (`--context-file` path read) and fiction-dir discovery
logic belong in this endpoint, not in the CLI wrapper.

**Done**: Calling with a missing PDF returns `PodcastResult(ok=False, error=PDFExtractionError(...))` — does not raise, does not print, does not call `sys.exit`. `python -c "from src.endpoints.podcast import generate_chapter_podcast; print('ok')"` exits 0.

---

### Pass 2.4 — generate_book_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_book_podcast()` |

**Function signature**:
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
) -> list[PodcastResult]:
```

**Temporary `run_splitter` import** (Pass 3.2 has not run yet):
```python
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).parent.parent / "slicer"))
from pdf_splitter import run_splitter  # TODO: replace with `from endpoints.slicer import run_splitter` after Pass 3.2
```

After Pass 3.2 creates `src/endpoints/slicer.py`, replace the block above with
`from endpoints.slicer import run_splitter`.

Call `run_splitter` to slice `book_pdf` into chapters (if supplied), then call
`generate_chapter_podcast()` per chapter. A chapter that fails produces a
`PodcastResult(ok=False, ...)` — remaining chapters continue.

**Done**: Calling with a fixture book PDF returns `list[PodcastResult]`. A chapter that
fails produces a `PodcastResult` with `.ok == False`; remaining chapters still run.
After Pass 3.2, update the import and re-verify.

---

### Pass 2.5 — Podcast CLI Wrapper

| File | Change |
|------|--------|
| `src/cli/__init__.py` | add — empty |
| `src/cli/podcast.py` | add — argparse wrapper routing to `generate_chapter_podcast()` or `generate_book_podcast()` |

**Routing logic**: use `--book PDF` as the router flag. If `--book` is absent, a positional
`pdf` argument is required and routes to `generate_chapter_podcast()`. If `--book` is
present, routes to `generate_book_podcast()`.

The full argument surface must cover both `run_chapter.py` and `run_book.py`:
- Chapter flags: `pdf` (positional), `--llm`, `--skip-audio`, `--mode`, `--context`,
  `--context-file`, `--fiction-dir`
- Book flags: `--book`, `--toc-page`, `--no-ocr`, `--force`, `--slice-only`

Print result paths to stdout. Print errors to stderr. `sys.exit(1)` on any failure.

> **Deviation from v1**: v1's Done condition only checked chapter parity. The book flags
> must also be present because Pass 5.3 shims `run_book.py` to call this CLI — if the
> book flags are missing, `run_book.py --help` behavior regresses.

**Done**: `python src/cli/podcast.py --help` exits 0 and shows both `pdf` positional and
`--book` flag. `python src/cli/podcast.py <fixture_pdf>` produces identical output to
`python src/run_chapter.py <fixture_pdf>`.

---

## Phase 3 — TTS Engine Cleanup + Slicer Endpoint

**Goal**: `tts/cli.py` `main()` is a clean engine function with no argparse. Slicer has a
stable import path. Pass 2.4's temporary import is upgraded.

---

### Pass 3.1 — TTS Engine Boundary

| File | Change |
|------|--------|
| `src/tts/cli.py` | modify — move `import argparse` from module level (line 6) into `cli_entrypoint()` body |

> **Deviation from v1**: v1 described this pass as confirming the boundary and moving
> "any remaining argparse." In the current code, the only argparse that is NOT already
> inside `cli_entrypoint()` is the module-level `import argparse` statement (line 6).
> `main()` has the correct signature already. `cli_entrypoint()` already exists. The
> only change required is moving that one import line.

**Done**: `grep "argparse" src/tts/cli.py` returns hits only inside `cli_entrypoint()`.
`grep "sys.exit" src/tts/cli.py` returns hits only inside `cli_entrypoint()`.

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

> **Deviation from v1**: v1 wrote `from slicer.pdf_splitter import run_splitter` without
> path setup. When the Done condition is run from the project root (`harnessv3/`),
> `sys.path` contains `harnessv3/` — not `harnessv3/src/`. Python would look for
> `harnessv3/slicer/` which does not exist. The sys.path insert is required.

After this pass, update `src/endpoints/podcast.py` to replace the temporary import from
Pass 2.4 with `from endpoints.slicer import run_splitter`.

**Done**: `python -c "from src.endpoints.slicer import run_splitter; print('ok')"` exits 0.
`grep "TODO.*Pass 3.2" src/endpoints/podcast.py` returns empty (temporary import replaced).

---

## Phase 4 — Novel Pipeline Callback Refactor

**Goal**: `session.py` has no `input()`, no `sys.exit()`. Approval injected via callable.
Tests drive the session without touching stdin.

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

`cost_usd` is populated from `current_totals(config)["session_total"]` (the
`current_totals` function is already imported in `session.py`).
`state_path` is populated from `Path(config["state_file_path"])`.

**Done**: `python -c "from src.fiction.pipeline.novel_pipeline.session import SessionResult, ApproveChapterFn; print('ok')"` exits 0.

---

### Pass 4.2 — session.py Callback Injection

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — inject `approve_chapter` callback; replace `sys.exit(1)` with `raise`; convert draft-preview prints to logger; return `SessionResult`; thread callback to `_run_one_chapter()` |

**Changes in detail:**

1. Add `approve_chapter: ApproveChapterFn = lambda n, text: True` parameter to
   `run_session()`.

2. Add `approve_chapter: ApproveChapterFn` parameter to `_run_one_chapter()`.
   Pass it through from `run_session()` at the `_run_one_chapter(...)` call site.

3. Inside `_run_one_chapter()`: replace the `input("Approve and update living doc? [y/n/q]: ")`
   block (lines 718–728) with `approved = approve_chapter(chapter_num, chapter_text)`.
   Map `True` → proceeds (equivalent to old `y`); `False` → rejected (equivalent to old `n`).
   Retain the `q` / quit path as a separate check: if `auto_approve` is False and the
   user has not provided a custom callback, surface quit via a second prompt or by
   treating a `KeyboardInterrupt` from the callback as quit.

4. Convert the draft-preview print block (current lines 709–712) to `logger.info(...)`.
   There is no standalone `print(draft_text)` in the current code — the spec description
   of this step is outdated. The target is the preview block that prints draft path,
   word count, and first 200 chars.

5. Replace `sys.exit(1)` in the `except KeyboardInterrupt:` handler (line 574) with
   `raise KeyboardInterrupt` so the exception propagates to the caller.

6. Make `run_session()` return `SessionResult`. There are multiple return points:
   - Early exit when `should_continue` is False → `SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False, state_path=Path(state_file_path))`
   - Early exit when "Proceed?" is declined → same pattern
   - Normal completion after the chapter loop → `SessionResult(chapters_written=completed, final_chapter_number=current_chapter, cost_usd=..., completed=True, state_path=...)`
   Audit all `return` statements (at minimum 3 early-exit points plus the fall-through)
   before marking this pass done.

**Done**: `grep "input()" src/fiction/pipeline/novel_pipeline/session.py` returns empty.
`grep "sys.exit" src/fiction/pipeline/novel_pipeline/session.py` returns empty.
`run_session(config, auto_approve=True, approve_chapter=lambda n, t: True)` completes
without touching stdin. (Note: `auto_approve=True` is required in addition to the
callback because the "Proceed?" pre-session gate is controlled by `auto_approve`, not by
the callback.)

---

### Pass 4.3 — novel_pipeline cli.py Update

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/cli.py` | modify — add `_prompt_user()`; construct `approve_fn`; pass `approve_chapter=approve_fn` to `run_session()` |

> **Deviation from v1**: The `--auto-approve` flag already exists at line 47 and is
> already wired. Do NOT add it again. The only new work is:

1. Add `_prompt_user(chapter_num: int, draft_text: str) -> bool` that prints the first
   500 chars of `draft_text` and reads `[y/n/q]` from stdin.

2. After parsing args, construct:
   ```python
   if args.auto_approve:
       approve_fn = lambda n, t: True
   else:
       approve_fn = _prompt_user
   ```

3. Pass `approve_chapter=approve_fn` to `run_session()`.

**Done**: `python src/fiction/pipeline/novel_pipeline/cli.py --auto-approve <config>` runs
without any stdin prompts. Interactive path (no `--auto-approve`) still calls `_prompt_user`
for each chapter.

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

**Import resolution** — `novel_pipeline` is installed as an editable package
(`.egg-info` present at `src/fiction/pipeline/novel_pipeline.egg-info/`). If the venv
is active with that install, use package imports directly:
```python
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult
```

If the package is NOT importable by that name, fall back to path insertion:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fiction" / "pipeline"))
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult
```

> **Deviation from v1**: v1 referenced `load_config_toml(config_path)` — that function
> does not exist. The TOML loader is `load_config(path)` in `novel_pipeline/config.py`.
> Do not create an alias.

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

**Done**: `python -c "from src.endpoints.fiction import run_novel_session; print('ok')"` exits 0.
Calling `run_novel_session(..., approve_chapter=lambda n, t: n != 2)` rejects chapter 2
without touching stdin.

---

### Pass 4.5 — Fiction CLI Shim

| File | Change |
|------|--------|
| `src/cli/fiction.py` | add — thin argparse wrapper |

Mirror the exact flag set from `src/fiction/pipeline/novel_pipeline/cli.py`:
`--config` (required), `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start`,
`--ignore-cost-limit`.

Add `_prompt_user(chapter_num: int, draft_text: str) -> bool` (same as Pass 4.3).
Construct `approve_fn` the same way. Call `run_novel_session()` from `src/endpoints/fiction.py`.

**Done**: `python src/cli/fiction.py --help` exposes the same flags as
`src/fiction/pipeline/novel_pipeline/cli.py`. Running with `--auto-approve <config>`
produces no stdin prompts.

---

## Phase 5 — Cleanup

**Goal**: Dead code removed. Root-level entry points shimmed. README reflects new CLI paths.

---

### Pass 5.1 — Remove Private Config Loaders

**Pre-condition**: Pass 1.1 is complete and all four files use `load_config` from
`src/config.py`. Verify with `grep -rn "from config import load_config" src/run_chapter.py src/run_book.py src/tts/cli.py src/podcast_script_generator/llm/call_api.py` returning four hits before proceeding.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — delete `_load_config()` definition |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — same |
| `src/podcast_script_generator/llm/call_api.py` | modify — same |

**Done**: `grep -rn "_load_config" src/` returns empty.

---

### Pass 5.2 — Delete run_simple.py

| File | Change |
|------|--------|
| `src/fiction/run_simple.py` | delete |

Verify no remaining imports first: `grep -rn "run_simple" src/` must return empty before
deletion (it should — nothing in the codebase imports this file).

**Done**: `ls src/fiction/run_simple.py` returns "No such file".
`grep -rn "run_simple" src/` returns empty.

---

### Pass 5.3 — Shim run_chapter.py and run_book.py

**Pre-condition**: Passes 2.3, 2.4, and 2.5 must be complete. `src/cli/podcast.py` must
expose all book-level flags (`--book`, `--force`, `--toc-page`, `--no-ocr`, `--slice-only`).
Verify: `python src/cli/podcast.py --help | grep -- "--book"` returns a hit.

> **Critical**: `run_book.py` currently does `import run_chapter as rc` and calls
> `rc.run_llm()`, `rc.run_local()`, `rc.run_tts()`. After the shim, `run_chapter.py`'s
> module namespace exposes only `main`. If `run_chapter.py` is shimmed first without
> `run_book.py` being shimmed simultaneously, `run_book.py` will fail at the `rc.run_llm`
> call. Apply BOTH shims in the same pass.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — replace entire body with `from cli.podcast import main; main()` |
| `src/run_book.py` | modify — replace entire body with `from cli.podcast import main; main()` |

**Done**: `python src/run_chapter.py <fixture_pdf>` produces output identical to
`python src/cli/podcast.py <fixture_pdf>`.
`python src/run_book.py --help` exits 0 and exposes the `--book` flag (confirming the
CLI wrapper has the full book argument surface, not just the chapter surface).

---

### Pass 5.4 — Update initial_readme.md

| File | Change |
|------|--------|
| `src/initial_readme.md` | modify — update Entry Points section |

List `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs. Document
`run_chapter.py` and `run_book.py` as shims forwarding to `src/cli/podcast.py`.

**Done**: `grep "src/cli/podcast.py" src/initial_readme.md` returns a hit.
`grep "shim" src/initial_readme.md` returns a hit.

---

## Appendix — Cross-Phase Dependencies

| Dependency | Consumer | Provider |
|------------|----------|----------|
| `src/config.py` exists | Passes 1.2–5.1 | Pass 1.1 |
| `PodcastError` hierarchy exists | Passes 2.3, 2.5 | Pass 1.2 |
| `src/util/normalize.py` exists | Pass 2.3 | Pass 2.1 |
| `PodcastResult`, `ScriptMode` defined with full fields | Pass 2.3 | Pass 2.2 |
| `generate_chapter_podcast()` exists | Pass 2.4, 2.5 | Pass 2.3 |
| `src/endpoints/slicer.py` exists | Pass 2.4 import upgrade | Pass 3.2 |
| `src/cli/podcast.py` has full book flags | Pass 5.3 | Pass 2.5 |
| `SessionResult` + `ApproveChapterFn` defined | Pass 4.2 | Pass 4.1 |
| `approve_chapter` wired in `run_session()` + `_run_one_chapter()` | Pass 4.3, 4.4 | Pass 4.2 |
| `run_novel_session()` exists | Pass 4.5 | Pass 4.4 |
| All four files use shared `load_config` | Pass 5.1 | Pass 1.1 |
| `src/endpoints/podcast.py` has full book logic | Pass 5.3 | Pass 2.4 |
