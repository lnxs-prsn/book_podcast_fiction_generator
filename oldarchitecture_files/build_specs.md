# Build Specs — CLI / Endpoints / Engines Refactor

> Derived from `initial_specs_v2.md` (2026-06-06).
> Each pass names every file touched, the change type (add / modify / delete), and a done condition.
> Passes within a phase are ordered; complete each pass before starting the next.

---

## Phase 1 — Foundation

**Goal**: Config loading and exception hierarchy in place before any endpoints are written. No behavior change to existing entry points.

---

### Pass 1.1 — Shared Config Loader

| File | Change |
|------|--------|
| `src/config.py` | add |
| `src/run_chapter.py` | modify — remove `_load_config()`, add `from config import load_config` |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — same |
| `src/podcast_script_generator/llm/call_api.py` | modify — same |

**Done**: `python -c "from src.config import load_config; print(load_config())"` exits 0. `python src/run_chapter.py --help` still works.

---

### Pass 1.2 — Podcast Exception Hierarchy

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/exceptions.py` | add — `PodcastError`, `PDFExtractionError`, `ScriptGenerationError`, `TTSSubmissionError`, `TTSTimeoutError` |
| `src/podcast_script_generator/llm/main.py` | modify — `sys.exit()` → `raise PDFExtractionError` / `raise ScriptGenerationError` |
| `src/tts/cli.py` | modify — `sys.exit()` inside `main()` → `raise TTSSubmissionError` / `raise TTSTimeoutError`; add `cli_entrypoint()` that catches `PodcastError` and exits |
| `src/run_chapter.py` | modify — catch `PodcastError` at CLI boundary; print error to stderr; `sys.exit(1)` |

**Done**: `grep -rn "sys.exit" src/podcast_script_generator/ src/tts/cli.py` returns empty. `grep "sys.exit" src/run_chapter.py` returns exactly one hit (the CLI boundary catch).

---

### Pass 1.3 — Structured Logging Migration

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/call_api.py` | modify — `print(f"Rate limited...")` → `logger.debug(...)` |
| `src/podcast_script_generator/llm/save_output.py` | modify — `print("Saved...")` → `logger.debug(...)` |
| `src/tts/cli.py` | modify — polling prints → `logger.info(...)`; retry wait prints → `logger.debug(...)` |
| `src/run_chapter.py` | modify — add `logging.basicConfig(level=logging.INFO, format="%(message)s")` at entry |
| `src/run_book.py` | modify — same `logging.basicConfig` at entry |

**Done**: `grep -rn "^    print\|^print" src/podcast_script_generator/ src/tts/cli.py` returns empty. Running `python src/run_chapter.py <fixture_pdf>` produces INFO-level output without crashing.

---

## Phase 2 — Podcast Pipeline Endpoint

**Goal**: `generate_chapter_podcast()` and `generate_book_podcast()` are directly callable with no argparse, no print, no sys.exit. CLI wrappers are thin.

---

### Pass 2.1 — Speaker Normalization Extract

| File | Change |
|------|--------|
| `src/util/__init__.py` | add — empty |
| `src/util/normalize.py` | add — `normalize_speakers(text: str) -> str` extracted from `run_chapter.py` |
| `src/run_chapter.py` | modify — remove inline normalizer body; add `from util.normalize import normalize_speakers` |

**Done**: `python -c "from src.util.normalize import normalize_speakers; print(normalize_speakers('ALEX: hi'))"` exits 0 and returns normalized text. `python src/run_chapter.py <fixture_pdf>` behavior unchanged.

---

### Pass 2.2 — Canonical Types

| File | Change |
|------|--------|
| `src/endpoints/__init__.py` | add — empty |
| `src/endpoints/podcast.py` | add — `ScriptMode` enum, `PodcastResult` dataclass; no functions yet |

**Done**: `python -c "from src.endpoints.podcast import ScriptMode, PodcastResult; print('ok')"` exits 0.

---

### Pass 2.3 — generate_chapter_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_chapter_podcast()` with logic moved verbatim from `run_chapter.py` `main()` body |

**Done**: Calling with a missing PDF returns `PodcastResult(error=PDFExtractionError(...))` — does not raise, does not print, does not call `sys.exit`. `python -c "from src.endpoints.podcast import generate_chapter_podcast; print('ok')"` exits 0.

---

### Pass 2.4 — generate_book_podcast()

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_book_podcast()` that calls `run_splitter` then `generate_chapter_podcast()` per chapter |

**Done**: Calling with a fixture book PDF returns `list[PodcastResult]`. A chapter that fails produces a `PodcastResult` with `.ok == False`; remaining chapters still run.

---

### Pass 2.5 — Podcast CLI Wrapper

| File | Change |
|------|--------|
| `src/cli/__init__.py` | add — empty |
| `src/cli/podcast.py` | add — thin `argparse` wrapper; `main()` calls `generate_chapter_podcast()` / `generate_book_podcast()`; prints result paths to stdout; prints errors to stderr; `sys.exit(1)` on failure |

**Done**: `python src/cli/podcast.py --help` matches the argument surface of `run_chapter.py`. `python src/cli/podcast.py <fixture_pdf>` produces identical output to `python src/run_chapter.py <fixture_pdf>`.

---

## Phase 3 — TTS Engine Cleanup + Slicer Endpoint

**Goal**: `tts/cli.py` `main()` is a clean engine function with no argparse. Slicer has a stable import path.

---

### Pass 3.1 — TTS Engine Boundary

| File | Change |
|------|--------|
| `src/tts/cli.py` | modify — confirm `main(script_path, output_folder, api_key, speakers) -> str` signature; move any remaining argparse into `cli_entrypoint()` if not already done in Pass 1.2; `cli_entrypoint()` is the only function allowed to call `sys.exit` |

**Done**: `grep "argparse" src/tts/cli.py` returns hits only inside `cli_entrypoint()`. `grep "sys.exit" src/tts/cli.py` returns hits only inside `cli_entrypoint()`.

---

### Pass 3.2 — Slicer Import Anchor

| File | Change |
|------|--------|
| `src/endpoints/slicer.py` | add — `from slicer.pdf_splitter import run_splitter; __all__ = ["run_splitter"]` |

**Done**: `python -c "from src.endpoints.slicer import run_splitter; print('ok')"` exits 0.

---

## Phase 4 — Novel Pipeline Callback Refactor

**Goal**: `session.py` has no `input()`, no `sys.exit()`. Approval injected via callable. Tests drive the session without touching stdin.

---

### Pass 4.1 — SessionResult Dataclass + Callback Type

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — add `ApproveChapterFn = Callable[[int, str], bool]` type alias; add `SessionResult` dataclass with fields: `chapters_written: int`, `final_chapter_number: int`, `cost_usd: float`, `completed: bool`, `state_path: Path` |

**Done**: `python -c "from src.fiction.pipeline.novel_pipeline.session import SessionResult, ApproveChapterFn; print('ok')"` exits 0.

---

### Pass 4.2 — session.py Callback Injection

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — add `approve_chapter: ApproveChapterFn = lambda n, text: True` param to `run_session()`; replace `_prompt_yes_no("Approve?")` with `approve_chapter(chapter_num, draft_text)`; replace `sys.exit(1)` on `KeyboardInterrupt` with `raise KeyboardInterrupt`; replace `print(draft_text)` with `logger.info(draft_text)`; return `SessionResult` |

**Done**: `grep "input()" src/fiction/pipeline/novel_pipeline/session.py` returns empty. `grep "sys.exit" src/fiction/pipeline/novel_pipeline/session.py` returns empty. `run_session(..., approve_chapter=lambda n, t: True)` completes without touching stdin.

---

### Pass 4.3 — novel_pipeline cli.py Update

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/cli.py` | modify — add `_prompt_user(chapter_num: int, draft_text: str) -> bool`; set `approve_fn = (lambda n, t: True) if args.auto_approve else _prompt_user`; pass `approve_chapter=approve_fn` to `run_session()` |

**Done**: `python src/fiction/pipeline/novel_pipeline/cli.py --auto-approve <config>` runs to completion without any stdin prompts. Interactive path (no `--auto-approve`) still calls `_prompt_user` for each chapter.

---

### Pass 4.4 — Fiction Endpoint Wrapper

| File | Change |
|------|--------|
| `src/endpoints/fiction.py` | add — `run_novel_session(config_path, resume, auto_approve, dry_run, chapter_start, ignore_cost_limit, approve_chapter) -> SessionResult`; loads config via `load_config_toml(config_path)`; delegates to `run_session()` |

**Done**: `python -c "from src.endpoints.fiction import run_novel_session; print('ok')"` exits 0. Calling `run_novel_session(..., approve_chapter=lambda n, t: n != 2)` rejects chapter 2 without touching stdin.

---

### Pass 4.5 — Fiction CLI Shim

| File | Change |
|------|--------|
| `src/cli/fiction.py` | add — thin `argparse` wrapper; `main()` calls `run_novel_session()`; interactive mode passes `_prompt_user` equivalent; `--auto-approve` passes `lambda n, t: True` |

**Done**: `python src/cli/fiction.py --help` exposes the same flags as `src/fiction/pipeline/novel_pipeline/cli.py`. Running with `--auto-approve` produces no stdin prompts.

---

## Phase 5 — Cleanup

**Goal**: Dead code removed. Root-level entry points shimmed. README reflects new CLI paths.

---

### Pass 5.1 — Remove Private Config Loaders

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — delete `_load_config()` definition (already using `load_config` from Pass 1.1) |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — same |
| `src/podcast_script_generator/llm/call_api.py` | modify — same |

**Done**: `grep -rn "_load_config" src/` returns empty.

---

### Pass 5.2 — Delete run_simple.py

| File | Change |
|------|--------|
| `src/fiction/run_simple.py` | delete |

**Done**: `ls src/fiction/run_simple.py` returns "No such file". `grep -rn "run_simple" src/` returns empty (no remaining imports).

---

### Pass 5.3 — Shim run_chapter.py and run_book.py

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — replace body with `from cli.podcast import main; main()` |
| `src/run_book.py` | modify — same |

**Done**: `python src/run_chapter.py <fixture_pdf>` produces output identical to `python src/cli/podcast.py <fixture_pdf>`. `python src/run_book.py --help` works.

---

### Pass 5.4 — Update initial_readme.md

| File | Change |
|------|--------|
| `src/initial_readme.md` | modify — update Entry Points section: list `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs; document `run_chapter.py` and `run_book.py` as shims forwarding to `src/cli/podcast.py` |

**Done**: `grep "src/cli/podcast.py" src/initial_readme.md` returns a hit. `grep "shim" src/initial_readme.md` returns a hit.
