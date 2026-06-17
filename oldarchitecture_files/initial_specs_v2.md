# CLI / Endpoints / Engines — Decision-Locked Build Spec

> Version 2. Written: 2026-06-06.
> v1 (`initial_specs.md`) identified blockers. This document locks decisions and defines phases.
> Open questions are collected at the bottom — these require your input before implementation of the affected phase.

---

## Locked Decisions

| # | Decision | Rejected Alternatives |
|---|----------|-----------------------|
| D1 | Approval gate: **callback injection** (Option A) | Option B (generator/yield) — uncommon pattern, harder to onboard; Option C (split endpoint) — forces caller to manage state across calls |
| D2 | Progress reporting: **Python `logging` module**, `__name__` loggers everywhere | print() — not suppressible; callback — heavier API surface without benefit |
| D3 | Batch failure: **FailableResult** — continue on failure, return full list | Raise immediately — loses partial work; on_error callback — unnecessary complexity |
| D4 | `seed_gen`: **CLI-only, no endpoint** — excluded from refactor | Parameterized endpoint — over-engineering for a one-shot bootstrap tool |
| D5 | `harness.py` unified entry point: **explicitly deferred**, out of scope | — |
| D6 | Directory restructure: **additive only** — add `src/endpoints/`, `src/cli/`, `src/config.py`; engines stay in place | Full rename to `src/engines/` — breaks all existing import paths in the submodule |
| D7 | Exception hierarchy: **separate `PodcastError` root** for podcast pipeline; novel_pipeline keeps its existing `PipelineError` root | Single shared base — coupling unrelated pipelines |
| D8 | `run_simple.py`: **delete** — superseded by `run_novel_session()`; duplicates novel_pipeline without importing it | Convert to thin wrapper — unnecessary indirection for a dead-end script |
| D9 | `run_chapter.py` / `run_book.py`: **keep as shims** forwarding to `src/cli/podcast.py` | Delete — breaks any existing shell usage with no benefit |
| D10 | Engine directories (`podcast_script_generator/`, `tts/`, `slicer/`): **stay in place** (D6 additive-only applies here too) | Rename to `src/engines/` — breaks submodule import paths; endpoint layer hides internals anyway |
| D11 | CLI logging level: **INFO by default** — matches current print() chattiness | WARNING + `--verbose` flag — unnecessarily quieter than current behavior |

---

## Architecture After Refactor

```
src/
├── config.py               ← NEW: single load_config() for all engines
│
├── endpoints/              ← NEW: callable business logic, no CLI
│   ├── podcast.py          ← generate_chapter_podcast(), generate_book_podcast()
│   └── fiction.py          ← run_novel_session()
│
├── cli/                    ← NEW: thin argparse wrappers
│   ├── podcast.py          ← replaces run_chapter.py + run_book.py
│   └── fiction.py          ← replaces novel_pipeline CLI
│
├── util/                   ← NEW: shared transforms
│   └── normalize.py        ← speaker normalization (moved from run_chapter.py)
│
├── podcast_script_generator/   ← UNCHANGED (already engine-shaped)
│   └── llm/
│       ├── exceptions.py   ← NEW: PodcastError hierarchy added here
│       └── ...             ← existing files: print() → logger.*
│
├── tts/                    ← UNCHANGED structure
│   └── cli.py              ← print() → logger.*; main() stays as engine interface
│
├── slicer/                 ← UNCHANGED (run_splitter already endpoint-shaped)
│   └── pdf_splitter.py
│
├── fiction/
│   ├── run_simple.py       ← OPEN QUESTION (see below)
│   ├── seed_gen/           ← UNCHANGED (CLI-only, excluded)
│   └── pipeline/
│       └── novel_pipeline/
│           ├── session.py  ← REFACTORED: remove input(), sys.exit(); add callback
│           ├── cli.py      ← REFACTORED: add _prompt_user(); pass lambda to session
│           └── ...         ← other modules unchanged
│
├── run_chapter.py          ← OPEN QUESTION: delete or keep as shim (see below)
└── run_book.py             ← OPEN QUESTION: delete or keep as shim (see below)
```

---

## Phase 1 — Foundation (unblocks all other phases)

**Goal**: Config loading and exception hierarchy in place before any endpoints are written.

### 1a. Shared Config Loader

Create `src/config.py`:

```python
import json
from pathlib import Path

_DEFAULT_PATH = Path(__file__).parent / "config.json"

def load_config(path: Path | None = None) -> dict:
    """Load JSON config. Returns {} on missing file. Raises ValueError on malformed JSON."""
    p = path or _DEFAULT_PATH
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
```

**Files to update** (remove their private `_load_config()`):
- `src/run_chapter.py` — imports `from config import load_config`
- `src/run_book.py` — same
- `src/tts/cli.py` — same
- `src/podcast_script_generator/llm/call_api.py` — same

### 1b. Podcast Exception Hierarchy

Add `src/podcast_script_generator/llm/exceptions.py`:

```python
class PodcastError(Exception):
    """Base for all podcast pipeline errors."""

class PDFExtractionError(PodcastError):
    """PDF could not be read or yielded no text."""

class ScriptGenerationError(PodcastError):
    """LLM call failed or returned unusable output."""

class TTSSubmissionError(PodcastError):
    """WaveSpeed job could not be submitted."""

class TTSTimeoutError(PodcastError):
    """WaveSpeed job did not complete within the expected window."""
```

Replace `sys.exit()` calls in `podcast_script_generator/llm/main.py` and `tts/cli.py` with raises from this hierarchy. `run_chapter.py` catches `PodcastError` at the CLI boundary and exits.

### 1c. Structured Logging Migration

All engines switch from `print()` to `logger = logging.getLogger(__name__)`.

| File | Change |
|------|--------|
| `podcast_script_generator/llm/call_api.py` | `print(f"Rate limited...")` → `logger.debug(...)` |
| `podcast_script_generator/llm/save_output.py` | `print("Saved...")` → `logger.debug(...)` |
| `tts/cli.py` | polling prints → `logger.info(...)`; retry waits → `logger.debug(...)` |

CLI entry points configure the handler:
```python
logging.basicConfig(level=logging.INFO, format="%(message)s")
```

**Verification**: after Phase 1, `from src.config import load_config` works. Running `run_chapter.py` still works end-to-end (no behavior change, just internals).

---

## Phase 2 — Podcast Pipeline Endpoint

**Goal**: `generate_chapter_podcast()` and `generate_book_podcast()` exist and are directly callable. CLI wrappers are thin.

### Canonical Types

```python
# src/endpoints/podcast.py

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class ScriptMode(Enum):
    TWOPERSON    = "2person"
    FOURPERSON   = "4person"
    CODE         = "code"
    REALWORLD    = "realworld"
    FICTION_META = "fiction_meta"

@dataclass
class PodcastResult:
    chapter_pdf:  Path
    script_path:  Path | None
    audio_path:   Path | None
    tts_job_id:   str | None
    error:        Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
```

### `generate_chapter_podcast`

```python
def generate_chapter_podcast(
    chapter_pdf:      Path,
    mode:             ScriptMode = ScriptMode.TWOPERSON,
    generate_script:  bool = True,       # was --llm
    generate_audio:   bool = True,       # was not --skip-audio
    context:          str | None = None,
    fiction_dir:      Path | None = None,
    output_dir:       Path = Path("data/output"),
    config_path:      Path | None = None,
) -> PodcastResult:
    """No argparse. No print(). No sys.exit(). Raises PodcastError subclasses on failure."""
```

Internal steps (moved verbatim from `run_chapter.py`):
1. Load config via `load_config(config_path)`
2. Extract PDF text via `extract_pdf.extract_pdf()`
3. Normalize speaker labels via `util.normalize.normalize_speakers()`
4. If `generate_script`: call `call_api.call_api()`, then `save_output.save_output()`
5. If `generate_audio`: call `tts.cli.main()`
6. Return `PodcastResult`; on `PodcastError`, return `PodcastResult(..., error=e)`

### `generate_book_podcast`

```python
def generate_book_podcast(
    book_pdf:         Path,
    toc_page:         int,
    mode:             ScriptMode = ScriptMode.TWOPERSON,
    slice_only:       bool = False,
    force_reprocess:  bool = False,
    output_dir:       Path = Path("data/output"),
    config_path:      Path | None = None,
) -> list[PodcastResult]:
    """Runs slicer then calls generate_chapter_podcast() per chapter.
    Continues on per-chapter failure. Returns full list including failed chapters."""
```

### Speaker Normalization — New Home

Extract the 73-line normalizer from `run_chapter.py` into:

```python
# src/util/normalize.py

def normalize_speakers(text: str) -> str:
    """Maps ALEX/JORDAN/HOST/EXPERT labels to Speaker 0 / Speaker 1."""
    ...
```

### CLI Wrapper

```python
# src/cli/podcast.py  (or keep as run_chapter.py — see Open Questions)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter_pdf", type=Path)
    parser.add_argument("--llm", action="store_true", dest="generate_script")
    parser.add_argument("--skip-audio", action="store_false", dest="generate_audio")
    parser.add_argument("--mode", default="2person")
    # ... etc
    args = parser.parse_args()

    result = generate_chapter_podcast(
        chapter_pdf=args.chapter_pdf,
        generate_script=args.generate_script,
        generate_audio=args.generate_audio,
        mode=ScriptMode(args.mode),
    )

    if not result.ok:
        print(f"Error: {result.error}", file=sys.stderr)
        sys.exit(1)

    if result.script_path:
        print(f"Script: {result.script_path}")
    if result.audio_path:
        print(f"Audio:  {result.audio_path}")
```

**Verification**: `pytest tests/test_podcast_endpoints.py` — tests call `generate_chapter_podcast()` directly with a fixture PDF. No subprocess. Tests cover: script-only mode, audio mode, bad PDF raises `PDFExtractionError`.

---

## Phase 3 — TTS Engine Cleanup + Slicer Endpoint

**Goal**: `tts/cli.py` is a clean engine (no argparse in `main()`). Slicer has a documented stable signature.

### TTS: No Changes to Structure

`main(script_path, output_folder, api_key, speakers) → str` is already the right shape.
Only changes:
- `print()` → `logger.info()` / `logger.debug()` (done in Phase 1)
- Ensure `TTSSubmissionError` / `TTSTimeoutError` are raised (not `sys.exit()`)
- `cli_entrypoint()` catches those and exits — stays as the CLI boundary

### Slicer: Document and Stabilize

`run_splitter(pdf_path, output_dir, toc_page, no_ocr, verbose)` already exists. Add a thin `src/endpoints/slicer.py`:

```python
# src/endpoints/slicer.py
from slicer.pdf_splitter import run_splitter  # re-export with stable import path

__all__ = ["run_splitter"]
```

No functional changes. The endpoint file is purely an import-path anchor.

**Verification**: `python -c "from src.endpoints.slicer import run_splitter; print('ok')"`.

---

## Phase 4 — Novel Pipeline: Callback Refactor

**Goal**: `session.py` has no `input()`, no `sys.exit()`. Approval is injected. Tests can simulate rejection.

### Callback Signature

```python
ApproveChapterFn = Callable[[int, str], bool]
# args: (chapter_number, draft_text) → True = approve, False = reject
```

### `run_session` Signature (updated)

```python
# novel_pipeline/session.py

def run_session(
    config: Config,
    resume: bool = False,
    auto_approve: bool = False,
    dry_run: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: ApproveChapterFn = lambda n, text: True,
) -> SessionResult:
    ...
```

Add `SessionResult`:

```python
@dataclass
class SessionResult:
    chapters_written:     int
    final_chapter_number: int
    cost_usd:             float
    completed:            bool   # False if interrupted or rejection limit reached
    state_path:           Path
```

### What Changes in `session.py`

| Before | After |
|--------|-------|
| `approved = _prompt_yes_no("Approve?")` | `approved = approve_chapter(chapter_num, draft_text)` |
| `sys.exit(1)` on KeyboardInterrupt | `raise KeyboardInterrupt` (let it propagate) |
| `print(draft_text)` before approval | `logger.info(draft_text)` |

### What Changes in `cli.py`

```python
def _prompt_user(chapter_num: int, draft_text: str) -> bool:
    print(f"\n--- Chapter {chapter_num} Draft ---\n")
    print(draft_text)
    return _prompt_yes_no("Approve this chapter? [y/n]: ")

# Pass to run_session:
approve_fn = (lambda n, t: True) if args.auto_approve else _prompt_user
run_session(..., approve_chapter=approve_fn)
```

### `NovelSessionResult` → `SessionResult`

The existing endpoint wrapper in `src/endpoints/fiction.py`:

```python
def run_novel_session(
    config_path:       Path,
    resume:            bool = False,
    auto_approve:      bool = False,
    dry_run:           bool = False,
    chapter_start:     int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter:   ApproveChapterFn = lambda n, text: True,
) -> SessionResult:
    config = load_config_toml(config_path)
    return run_session(config, ..., approve_chapter=approve_chapter)
```

**Verification**: `pytest tests/test_novel_session.py` with injected `lambda n, text: n != 2` (reject chapter 2) runs without touching stdin. Confirm rejection triggers retry logic. Confirm `completed=False` in result on rejection limit.

---

## Phase 5 — Cleanup (after all phases pass)

- Remove private `_load_config()` from `run_chapter.py`, `run_book.py`, `tts/cli.py`, `call_api.py`
- **Delete `src/fiction/run_simple.py`** — superseded by Phase 4's `run_novel_session()`; duplicates novel_pipeline without importing it; not referenced anywhere in the codebase
- **Keep `run_chapter.py` and `run_book.py` as shims** — each forwards to `src/cli/podcast.py:main()`; safe default that preserves any existing shell usage
- **Logging defaults to INFO** — matches current print() chattiness; no `--verbose` flag
- Update `initial_readme.md` entry points section to reflect new CLI paths

---

## Deferred (Explicitly Out of Scope)

- `src/harness.py` unified entry point — defer until all phase endpoints exist and the natural unification shape is obvious
- `seed_gen` interactivity refactor — stays CLI-only; no programmatic endpoint needed
- `src/fiction/pipeline/pyproject.toml` restructure — keep novel_pipeline as its own package; do not absorb into flat src layout
- Engine directory rename to `src/engines/` — D6 already decided against this; endpoint layer hides internal paths from callers
