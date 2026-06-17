# Implementation Journal

This document tracks decisions, deviations, and clarifications encountered during the static (paper) build run against `build_specs.md`. Every finding is based on reading the actual source files. No code was changed.

---

## Pass 1.1 — Shared Config Loader

### Decision 1
**Situation**: The spec creates `src/config.py` with a shared `load_config()` but does not specify whether it reads JSON or TOML. All four files targeted (`run_chapter.py`, `run_book.py`, `tts/cli.py`, `call_api.py`) have their own `_load_config()` that reads `src/config.json` (JSON format). The novel_pipeline has a completely separate TOML-based `load_config()` in `src/fiction/pipeline/novel_pipeline/config.py`.

**Action**: The new `src/config.py` shared loader must read JSON, not TOML. The existing `config.json` is the config file in use across all four podcast/TTS files. The novel_pipeline's TOML loader is unrelated and must not be confused with or replaced by the new shared loader.

**Why**: All four target files hardcode paths that resolve to `src/config.json`. Changing the format would break all existing deployments that have that file.

**Resolution**: Implement `load_config(path: str | Path | None = None) -> dict` in `src/config.py`. Default path is `Path(__file__).parent / "config.json"` so it resolves correctly when called with no arguments. The Done condition `python -c "from src.config import load_config; print(load_config())"` requires zero-arg invocation to work.

---

### Decision 2
**Situation**: After Pass 1.1, all four files should do `from config import load_config`. However, `call_api.py` sits at `src/podcast_script_generator/llm/call_api.py` — three directory levels below `src/`. A bare `from config import load_config` will fail at runtime unless `src/` is on `sys.path`.

**Action**: Each file using the shared import needs `src/` on `sys.path` at the time of import. `run_chapter.py` and `run_book.py` already compute `SRC = Path(__file__).parent` (which IS `src/`). `tts/cli.py` and `call_api.py` do not pre-add `src/` to the path.

**Why**: Python resolves bare module names against `sys.path`. Without `src/` on the path, `from config import load_config` raises `ModuleNotFoundError` in the deeper files.

**Resolution**: Before the `from config import load_config` line in `tts/cli.py` and `call_api.py`, add a path-insert guard:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # tts/cli.py → src/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # call_api.py → src/
```
Alternatively, `src/config.py` can expose a `load_config_at(path)` convenience that accepts an explicit path, allowing callers to keep their existing path resolution logic.

---

### Decision 3
**Situation**: `tts/cli.py` calls `_load_config()` in three places: inside `build_api_payload()` (line 68), `send_to_api()` (line 99), and `cli_entrypoint()` (line 233). These are engine functions, not just the CLI entry point. After migration, the shared `load_config()` must resolve `src/config.json` correctly regardless of the call stack — including when `tts/cli.py` is imported by `run_chapter.py` via `sys.path.insert(0, str(SRC / "tts"))`.

**Action**: The shared `load_config()` must locate `config.json` relative to its own file (`src/config.py`), not relative to the caller. Using `Path(__file__).parent / "config.json"` inside `src/config.py` satisfies this.

**Why**: When `run_chapter.py` does `sys.path.insert(0, str(SRC / "tts"))` and then `from cli import main as tts_main`, the working directory and `__file__` of `tts/cli.py` are unchanged — but the caller's context is `run_chapter.py`. An anchor in `src/config.py` is stable regardless.

**Resolution**: Confirm the shared loader uses `Path(__file__).parent / "config.json"` as the default path anchor.

---

## Pass 1.2 — Podcast Exception Hierarchy

### Decision 4
**Situation**: The spec says to modify `tts/cli.py` — "`sys.exit()` inside `main()` → raise `TTSSubmissionError` / raise `TTSTimeoutError`". However, reading `tts/cli.py` reveals that `main()` already raises exceptions — it has zero `sys.exit()` calls. The function at line 202 raises `RuntimeError`, `AuthError`, `ConnectionError`, `ValueError`, `FileNotFoundError`, and `OSError`. `sys.exit()` is confined entirely to `cli_entrypoint()` (lines 264–268), and `cli_entrypoint()` itself already exists.

**Action**: Pass 1.2's description of `tts/cli.py` is already partially complete. The actual work remaining is: (1) create the `PodcastError` hierarchy in `exceptions.py`, (2) remap `tts/cli.py`'s existing exception types (`AuthError`, `RuntimeError`, etc.) to the new hierarchy types (`TTSSubmissionError`, `TTSTimeoutError`), (3) update `cli_entrypoint()` to catch `PodcastError` instead of the scattered individual exception types.

**Why**: The spec was written against a version of `tts/cli.py` that may have had `sys.exit()` in `main()`. The current implementation is ahead of the spec in this regard.

**Resolution**: Treat Pass 1.2's `tts/cli.py` work as a type-remapping pass: replace `AuthError` (custom local class) with `TTSSubmissionError`, `RuntimeError` with `TTSSubmissionError` for WaveSpeed failures, and map timeout/network errors to `TTSTimeoutError`.

---

### Decision 5
**Situation**: Pass 1.2's Done condition states: `grep -rn "sys.exit" src/podcast_script_generator/ src/tts/cli.py` returns empty. But the spec also says to add `cli_entrypoint()` that "catches `PodcastError` and exits." Exiting means calling `sys.exit()`. This creates a contradiction: `cli_entrypoint()` must call `sys.exit()`, yet the grep must return empty.

**Action**: The Done condition as written is inconsistent with the stated behavior. Pass 3.1's Done condition resolves this correctly: "`grep "sys.exit" src/tts/cli.py` returns hits only inside `cli_entrypoint()`." Pass 1.2's Done condition should be read as applying only to `src/podcast_script_generator/` (excluding `src/tts/cli.py` from the empty-return requirement).

**Why**: Pass 3.1 explicitly allows `sys.exit()` in `cli_entrypoint()`. Pass 1.2 cannot have a stricter requirement for the same file than the dedicated cleanup pass.

**Resolution**: For Pass 1.2, verify `sys.exit()` is absent from `src/podcast_script_generator/` and from `main()` in `tts/cli.py`. Allow it to remain in `cli_entrypoint()`.

---

### Decision 6
**Situation**: `src/podcast_script_generator/llm/main.py` currently catches `FileNotFoundError`, `ValueError`, `KeyError`, and a catch-all `Exception`, all calling `sys.exit(1)`. The spec says to raise `PDFExtractionError` or `ScriptGenerationError` instead. However, `main.py` is a standalone script (run with `python main.py <args>`) not called by `run_chapter.py`'s pipeline — `run_chapter.py` imports `extract_pdf`, `call_api`, etc. directly, bypassing `main.py` entirely.

**Action**: `main.py` in `podcast_script_generator/llm/` is an orphan entry point for the standalone LLM pipeline, not part of the chapter-podcast flow. The spec's Done condition (`grep -rn "sys.exit" src/podcast_script_generator/` returns empty) still requires its cleanup, but callers are unaffected.

**Why**: `run_chapter.py` uses `sys.path.insert` + direct imports of individual modules (`extract_pdf`, `call_api`, etc.) rather than importing `main.py`. The exception hierarchy from `main.py` never propagates to `run_chapter.py`.

**Resolution**: Proceed with the sys.exit→raise substitution in `main.py` as a standalone cleanup. Add a bare `if __name__ == "__main__":` block that catches `PodcastError` and exits with code 1 to preserve runnable behavior.

---

## Pass 1.3 — Structured Logging Migration

### Decision 7
**Situation**: The Done condition `grep -rn "^    print\|^print" src/podcast_script_generator/ src/tts/cli.py` returns empty is intended to verify print removal. However, the target prints in `tts/cli.py`'s `send_to_api()` function are at 8-space indentation (inside a `try:` block inside the function body). The grep pattern `^    print` matches only exactly 4 leading spaces. The 8-space prints will silently pass the grep.

**Action**: The Done condition will give a false-positive pass even if the prints in `send_to_api()` are not converted. The actual prints to convert in `tts/cli.py` are:
- Line 119: `print(f"TTS submitted  request_id={request_id}")` (8 spaces)
- Lines 120–122: `print(f"Recovery file ...")`, `print("Polling for completion ...")` (8 spaces)
- Line 144: `print(f"  [{elapsed:.0f}s] status=...")` (12 spaces)

**Why**: The grep Done condition is too narrow in indentation depth to serve as a reliable gate.

**Resolution**: Convert all target prints to logger calls as described, regardless of grep coverage. The Done condition passes but the real correctness check is manually verifying the target lines.

---

### Decision 8
**Situation**: `save_output.py` has exactly one print: `print(f"Wrote {len(files)} files to {output_dir}")` at line 26. The spec says convert to `logger.debug(...)`. However, this function has no logger configured — it imports only `os`. Adding a logger requires adding `import logging` and `logger = logging.getLogger(__name__)`.

**Action**: Add `import logging` and a module-level `logger = logging.getLogger(__name__)` to `save_output.py`, then convert the print.

**Why**: Consistent with structured logging migration. `save_output.py` is a leaf module — having a logger here is minimal overhead and correct.

**Resolution**: Standard migration. No complication.

---

## Pass 2.1 — Speaker Normalization Extract

### Decision 9
**Situation**: The spec says extract `normalize_speakers(text: str) -> str` from `run_chapter.py`. The actual function in `run_chapter.py` is named `_to_speaker_format(text: str) -> str` (lines 55–117). The spec introduces a new public name `normalize_speakers`. This is an extraction AND a rename.

**Action**: Create `src/util/normalize.py` with the function body from `_to_speaker_format`, named `normalize_speakers`. Update all three call sites in `run_chapter.py` (lines 127, 145, 146) from `_to_speaker_format(...)` to `normalize_speakers(...)`.

**Why**: The Done condition tests `normalize_speakers('ALEX: hi')` — the new name is confirmed by spec.

**Resolution**: Three call-site updates in `run_chapter.py` are required, not just the definition removal.

---

### Decision 10
**Situation**: After extraction, `run_chapter.py` does `from util.normalize import normalize_speakers`. `run_chapter.py` is at `src/run_chapter.py`. `util/` is at `src/util/`. This import works when `src/` is the working directory or on `sys.path` — which it is when invoked as `python src/run_chapter.py`. However, when `run_book.py` imports `run_chapter` via `sys.path.insert(0, str(SRC))` then `import run_chapter as rc`, `run_chapter`'s top-level `from util.normalize import normalize_speakers` will execute with `src/` already on the path (set by `run_book.py`'s line 142). This should resolve correctly.

**Action**: No path change needed. The existing `sys.path` management in `run_book.py` covers this.

**Why**: `run_book.py` line 142 does `sys.path.insert(0, str(SRC))` before importing `run_chapter`, so `util` is findable.

**Resolution**: No additional path manipulation required for this pass.

---

## Pass 2.2 — Canonical Types

### Decision 11
**Situation**: The spec creates `ScriptMode` enum and `PodcastResult` dataclass in `src/endpoints/podcast.py` but does not specify the fields of `PodcastResult` in this pass. Pass 2.3's Done condition reveals `PodcastResult(error=PDFExtractionError(...))` and Pass 2.4's Done condition reveals `.ok == False`. The fields must be inferred across passes.

**Action**: Define `PodcastResult` with at minimum: `ok: bool`, `script_path: Path | None = None`, `audio_path: str | None = None`, `error: Exception | None = None`. `ScriptMode` should map to the `--mode` values from `run_chapter.py`: `TWO_PERSON`, `FOUR_PERSON`, `CODE`, `REALWORLD`, `FICTION_META`.

**Why**: The Done conditions for Passes 2.3 and 2.4 together pin the minimum required fields. Defining them in Pass 2.2 ensures Pass 2.3 can use them without revisiting this file.

**Resolution**: Define both types in full during Pass 2.2 using inferred fields rather than waiting for Pass 2.3 to reveal them.

---

## Pass 2.3 — generate_chapter_podcast()

### Decision 12
**Situation**: The spec says "add `generate_chapter_podcast()` with logic moved verbatim from `run_chapter.py` `main()` body." The `main()` body handles argparse, path resolution, context loading, fiction_content loading, then calls `run_llm()` or `run_local()`, writes the script file, and calls `run_tts()`. Moving this "verbatim" requires defining a function signature. The spec does not specify the signature.

**Action**: Define the signature as:
```python
def generate_chapter_podcast(
    pdf_path: Path,
    llm: bool = False,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    fiction_content: str | None = None,
) -> PodcastResult
```
This mirrors the argparse surface of `run_chapter.py` without the argparse layer.

**Why**: The Done condition requires returning `PodcastResult(error=...)` for a missing PDF, not raising. The function must wrap all error paths in try/except and return a result object instead of calling sys.exit.

**Resolution**: Strip argparse from the moved logic. Wrap the body in a try/except that catches all exceptions and returns `PodcastResult(ok=False, error=e)`. The context-file loading (`--context-file`) and fiction-dir discovery logic also belong in the endpoint, not the CLI.

---

## Pass 2.4 — generate_book_podcast()

### Decision 13
**Situation**: `generate_book_podcast()` must call `run_splitter` then `generate_chapter_podcast()` per chapter. But `src/endpoints/slicer.py` (the clean import anchor for `run_splitter`) is not created until Pass 3.2, which is in Phase 3 — after Phase 2. Pass 2.4 has a forward dependency on Pass 3.2.

**Action**: In Pass 2.4, import `run_splitter` using the legacy `sys.path.insert` pattern from `run_book.py` (line 93–94):
```python
sys.path.insert(0, str(Path(__file__).parent.parent / "slicer"))
from pdf_splitter import run_splitter
```
After Pass 3.2 creates `src/endpoints/slicer.py`, replace this with `from endpoints.slicer import run_splitter`.

**Why**: Forcing a dependency on a later pass would break the ordered execution model. Temporary legacy import is acceptable.

**Resolution**: Flag this as a two-step migration. Add a comment in `src/endpoints/podcast.py` during Pass 2.4 noting the import should be updated in Pass 3.2.

---

## Pass 2.5 — Podcast CLI Wrapper

### Decision 14
**Situation**: The Done condition says `python src/cli/podcast.py --help` matches the argument surface of `run_chapter.py`. But `src/cli/podcast.py` wraps both `generate_chapter_podcast()` and `generate_book_podcast()`. `run_chapter.py` handles a single chapter (has `pdf` positional arg). `run_book.py` handles batch (has `--book`, `--force`, `--toc-page`, `--no-ocr`, `--slice-only`). A single flat CLI cannot serve both surfaces simultaneously.

**Action**: Use mutually exclusive routing: if a positional `pdf` argument is provided, route to `generate_chapter_podcast()`; if `--book` is provided, route to `generate_book_podcast()`. This preserves both argument surfaces under one CLI.

**Why**: The spec says "main() calls `generate_chapter_podcast()` / `generate_book_podcast()`" using a slash — implying both are reachable from the same entry point. A routing flag or subcommand is the only way to resolve this.

**Resolution**: Implement with subcommands (`chapter` and `book`) or with the `--book` flag as the router. The Done condition only tests `--help` and chapter output parity, so either approach satisfies it.

---

## Pass 3.1 — TTS Engine Boundary

### Decision 15
**Situation**: The Done condition says `grep "argparse" src/tts/cli.py` returns hits only inside `cli_entrypoint()`. However, `tts/cli.py` currently has `import argparse` at line 6 — module level, not inside `cli_entrypoint()`. The grep would find this module-level import and fail the condition.

**Action**: Move `import argparse` from module level into `cli_entrypoint()`. This is the primary code change required for Pass 3.1.

**Why**: The `argparse` module is only used inside `cli_entrypoint()`. Moving the import inward is the minimal change to satisfy the Done condition.

**Resolution**: One-line change: move `import argparse` to the first line of `cli_entrypoint()`. The `sys.exit()` Done condition is already satisfied — `sys.exit()` is only in `cli_entrypoint()` today.

---

## Pass 3.2 — Slicer Import Anchor

### Decision 16
**Situation**: The Done condition runs `python -c "from src.endpoints.slicer import run_splitter; print('ok')"` from the project root (`harnessv3/`). The proposed `src/endpoints/slicer.py` would contain `from slicer.pdf_splitter import run_splitter`. When Python executes `src/endpoints/slicer.py`, `sys.path` contains `harnessv3/`. Python looks for `slicer` as `harnessv3/slicer/` — which does not exist. The slicer is at `harnessv3/src/slicer/pdf_splitter.py`.

**Action**: `src/endpoints/slicer.py` must add `src/` to `sys.path` before the slicer import, or use an absolute path resolution:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # → src/
from slicer.pdf_splitter import run_splitter
__all__ = ["run_splitter"]
```

**Why**: The file is run from the project root, not from `src/`, so module resolution anchors at `harnessv3/`, not `src/`.

**Resolution**: The sys.path insert is the correct fix. It mirrors the pattern already used in `run_book.py` (line 93).

---

## Pass 4.1 — SessionResult Dataclass + Callback Type

### Decision 17
**Situation**: `run_session()` currently returns `None` (implicit return). The spec adds `SessionResult` with fields: `chapters_written: int`, `final_chapter_number: int`, `cost_usd: float`, `completed: bool`, `state_path: Path`. The `state_path` field must be populated from `config["state_file_path"]`, which is accessible inside `run_session()`.

**Action**: Define the dataclass and type alias in Pass 4.1 only (no behavior change). Actual return-value wiring happens in Pass 4.2.

**Why**: Separation of concerns — Pass 4.1 is type definitions only, Pass 4.2 is behavior change. This order is correct as written.

**Resolution**: `cost_usd` will need to read from the session's spend tracking (`cost.current_totals()`). This dependency is available in `session.py` since it already imports `from .cost import current_totals`.

---

## Pass 4.2 — session.py Callback Injection

### Decision 18
**Situation**: The spec says "replace `print(draft_text)` with `logger.info(draft_text)`". There is no standalone `print(draft_text)` in `session.py`. The draft text is never printed in full — only the first 200 chars are shown (line 712: `f"First 200 chars: {chapter_text[:200]!r}"`). There is no `print(draft_text)` to replace.

**Action**: The spec description is inaccurate for the current code. The closest intent is to convert the draft preview prints (lines 709–712) to logger calls. The approve_chapter callback receives the full `chapter_text` regardless of what is printed.

**Why**: The callback signature `ApproveChapterFn = Callable[[int, str], bool]` passes the full chapter text to the approver even though it isn't printed. The spec likely wrote this based on an earlier version of `session.py` that printed the full draft.

**Resolution**: Convert lines 709–712 to `logger.info(...)` calls. Pass the full `chapter_text` to `approve_chapter()` as specified.

---

### Decision 19
**Situation**: The `approve_chapter` callback is added to `run_session()` signature, but the actual approval input prompt is inside `_run_one_chapter()` at lines 718–728. `run_session()` must thread the callback down into `_run_one_chapter()`. Currently `_run_one_chapter()` takes no approval-related parameter.

**Action**: Add `approve_chapter: ApproveChapterFn` as a parameter to `_run_one_chapter()` and pass it through from `run_session()` at line 517.

**Why**: The callback must reach the approval logic, which is in a private helper function. Passing it through the call chain is the correct approach.

**Resolution**: Two-function signature update: `run_session()` and `_run_one_chapter()` both get the parameter.

---

### Decision 20
**Situation**: The Done condition says `run_session(..., approve_chapter=lambda n, t: True)` completes without touching stdin. But `run_session()` contains a pre-session gate at line 497: `_prompt_yes_no("Proceed?", auto=auto_approve, ...)`. Without also passing `auto_approve=True`, the "Proceed?" prompt still blocks on stdin. The `approve_chapter` callback only replaces the per-chapter approval prompt.

**Action**: The Done condition implicitly requires `auto_approve=True` in addition to the approve_chapter callback. The test invocation should be `run_session(config, auto_approve=True, approve_chapter=lambda n, t: True)`.

**Why**: Two distinct stdin points exist: the session-level "Proceed?" gate and the per-chapter approval. The callback controls only the latter. The gate is controlled by `auto_approve`.

**Resolution**: The Done condition wording is underspecified. The implementation is correct as designed — callers must supply `auto_approve=True` to go fully non-interactive.

---

### Decision 21
**Situation**: `run_session()` has multiple early-return paths (return at line 491 `if not should_continue`, implicit return after `_prompt_yes_no("Proceed?")` fails, etc.). After Pass 4.2 requires returning `SessionResult`, all these early exits must return a valid `SessionResult` with `completed=False`.

**Action**: Replace all bare `return` statements in `run_session()` with `return SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False, state_path=Path(state_file_path))`.

**Why**: A function declared to return `SessionResult` cannot return `None`. There are at minimum 3 early-return points to update.

**Resolution**: Audit all `return` statements in `run_session()` during Pass 4.2. Count: line 491 (should_continue=False), line 499 (declined at summary), implicit fall-through after the chapter loop. All need `SessionResult` wrapping.

---

## Pass 4.3 — novel_pipeline cli.py Update

### Decision 22
**Situation**: The spec says "add `--auto-approve` flag." `src/fiction/pipeline/novel_pipeline/cli.py` already has `--auto-approve` at line 47. The argument exists and is wired to `args.auto_approve` which is passed to `run_session()`. No `--auto-approve` flag work is needed.

**Action**: Skip the flag addition. The Pass 4.3 work is limited to: (1) adding the `_prompt_user(chapter_num: int, draft_text: str) -> bool` function, (2) constructing `approve_fn` based on `args.auto_approve`, (3) passing `approve_chapter=approve_fn` to `run_session()`.

**Why**: The existing `cli.py` is ahead of the spec on the `--auto-approve` flag. The callback wiring is new work.

**Resolution**: Pass 4.3 is smaller than described. The flag already works; the callback threading is the only real change.

---

## Pass 4.4 — Fiction Endpoint Wrapper

### Decision 23
**Situation**: The spec says `run_novel_session()` "loads config via `load_config_toml(config_path)`." No function named `load_config_toml` exists anywhere in the codebase. The TOML loader in `src/fiction/pipeline/novel_pipeline/config.py` is simply `load_config(path: str) -> dict`. The name in the spec does not match the actual function name.

**Action**: Import the existing `load_config` from `novel_pipeline.config` and use it directly. Do not create an alias named `load_config_toml` — that would add a dead name with no benefit.

**Why**: The spec name is a documentation artifact, not a real function. Creating an alias would introduce naming confusion.

**Resolution**: In `src/endpoints/fiction.py`, use `from fiction.pipeline.novel_pipeline.config import load_config` (subject to path resolution below).

---

### Decision 24
**Situation**: `src/endpoints/fiction.py` is outside the `novel_pipeline` package. The novel_pipeline uses relative imports (`from .config import load_config`, `from .session import run_session`). From `src/endpoints/fiction.py`, these modules must be reached via absolute imports. The novel_pipeline has a `.egg-info` directory, suggesting it may be installed as a package named `novel_pipeline`.

**Action**: Verify import path at implementation time. If `novel_pipeline` is installed, use `from novel_pipeline.config import load_config` and `from novel_pipeline.session import run_session`. If not installed (editable or path-only), add `sys.path.insert(0, str(Path(__file__).parent.parent / "fiction" / "pipeline"))` to `src/endpoints/fiction.py`.

**Why**: The presence of `novel_pipeline.egg-info` in `src/fiction/pipeline/novel_pipeline.egg-info/` suggests an installed editable package (`pip install -e .`). If that install is active in the current venv, package imports work without path manipulation.

**Resolution**: Check for `novel_pipeline` in the venv before committing to one import strategy.

---

## Pass 4.5 — Fiction CLI Shim

### Decision 25
**Situation**: The Done condition says `python src/cli/fiction.py --help` exposes the same flags as `src/fiction/pipeline/novel_pipeline/cli.py`. The `novel_pipeline/cli.py` flags are: `--config` (required), `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start`, `--ignore-cost-limit`. `src/cli/fiction.py` wraps `run_novel_session()` which takes these same inputs as function parameters. Direct translation to argparse flags gives an identical surface.

**Action**: Mirror the existing `novel_pipeline/cli.py` flag set exactly. No new flags should be added to `src/cli/fiction.py`.

**Why**: The Done condition requires flag surface parity. Adding flags would fail it; removing any would also fail.

**Resolution**: Copy the `_build_parser()` logic from `novel_pipeline/cli.py` into `src/cli/fiction.py`'s parser definition. Add the `_prompt_user` function that mirrors the one from Pass 4.3.

---

## Pass 5.1 — Remove Private Config Loaders

### Decision 26
**Situation**: `tts/cli.py`'s `_load_config()` is called from `build_api_payload()` (line 68) to read `tts_scale`, and from `send_to_api()` (line 99) to read `wavespeed_model`. These are pure engine functions, not CLI-specific. After migrating to the shared `load_config()`, these functions call into `src/config.py`. The import path issue from Decision 2 applies here as well.

**Action**: After Pass 1.1 establishes the path-insert pattern in `tts/cli.py`, Pass 5.1 simply removes the now-redundant `_load_config()` function definition at lines 22–28.

**Why**: If Pass 1.1 correctly establishes `from config import load_config` with the required path manipulation, Pass 5.1 is a deletion-only operation.

**Resolution**: No new decisions. Verify the `_load_config` grep returns empty only after confirming all call sites have been updated to `load_config` in Pass 1.1.

---

## Pass 5.2 — Delete run_simple.py

### Decision 27
**Situation**: `src/fiction/run_simple.py` is a 387-line standalone script with its own `run_session()` function (line 283). The novel_pipeline `session.py` also has a `run_session()`. No file in the codebase imports `run_simple`. The deletion is safe.

**Action**: Delete `src/fiction/run_simple.py`. Verify with `grep -rn "run_simple" src/` before deletion.

**Why**: No import graph edges point to this file. It is dead code from before the novel_pipeline was built.

**Resolution**: Straightforward. The name collision of `run_session()` in both files is irrelevant since they are not in the same import scope.

---

## Pass 5.3 — Shim run_chapter.py and run_book.py

### Decision 28
**Situation**: `run_book.py` at line 143 does `import run_chapter as rc` and calls `rc.run_llm()`, `rc.run_local()`, `rc.run_tts()` (lines 166–172). After Pass 5.3 shims `run_chapter.py` to `from cli.podcast import main; main()`, all three of those functions will be gone from `run_chapter`'s module namespace. `run_book.py` will fail at the `rc.run_llm(...)` call.

**Action**: Both shims must be applied simultaneously — shimming `run_chapter.py` alone breaks `run_book.py`. The batch logic in `run_book.py` (the `for pdf_path in pdfs:` loop) must already be fully migrated to `src/endpoints/podcast.py` via `generate_book_podcast()` (Pass 2.4) before either shim is applied.

**Why**: `run_book.py` is not a thin wrapper — it imports and calls functions from `run_chapter.py` at the module level. After the shim, `run_chapter` only exposes `main`, nothing else.

**Resolution**: Confirm Passes 2.3/2.4/2.5 are complete before executing Pass 5.3. Apply both shims in the same pass, not one at a time.

---

### Decision 29
**Situation**: The Done condition for Pass 5.3 says `python src/run_book.py --help` works. After shimming `run_book.py` to `from cli.podcast import main; main()`, `--help` would display the chapter-level CLI help, not the batch/book help. The `--book`, `--force`, `--toc-page`, `--no-ocr`, `--slice-only` flags from the original `run_book.py` would be lost.

**Action**: For the Done condition to be meaningfully satisfied, `src/cli/podcast.py` must expose the book-level flags as well (either via subcommands or a `--book` routing flag as decided in Decision 14). Otherwise `run_book.py --help` changes output, which constitutes behavior regression.

**Why**: The Done condition says "`python src/run_book.py --help` works" — but "works" is ambiguous. If it merely exits 0 and prints something, the shim satisfies it trivially. If it means full flag-surface parity, the CLI wrapper must include book flags.

**Resolution**: Clarify "works" as: exits 0 and exposes at minimum `--book` flag. Design `src/cli/podcast.py` in Pass 2.5 to include the full book argument surface to avoid revisiting in Pass 5.3.

---

## Pass 5.4 — Update initial_readme.md

### Decision 30
**Situation**: This is a documentation-only pass. `src/initial_readme.md` needs to list `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs, and document `run_chapter.py` and `run_book.py` as shims.

**Action**: Standard documentation update. No code decisions required.

**Why**: The Done condition greps for specific strings — straightforward to satisfy.

**Resolution**: No complications.

---

## Cross-Phase Summary of Blockers

| Finding | Passes Affected | Risk |
|---------|----------------|------|
| `import argparse` at module level in `tts/cli.py` fails Pass 3.1 Done condition | 3.1 | Medium — easy one-line fix but easy to overlook |
| `load_config_toml` name in spec does not exist in code | 4.4 | Medium — spec naming error |
| Forward dependency: `endpoints/slicer.py` not available during Pass 2.4 | 2.4, 3.2 | Low — documented bridge import |
| Pass 1.2 Done condition contradicts Pass 3.1 Done condition for `tts/cli.py` | 1.2, 3.1 | Low — resolve in favor of Pass 3.1 |
| `run_book.py` imports `rc.run_llm` etc. — must not shim until all book logic migrated | 5.3 | High — breaks `run_book.py` if done out of order |
| Print grep pattern misses 8-space indentation in `tts/cli.py` | 1.3 | Low — false-pass on Done condition |
| `--auto-approve` in Pass 4.3 already exists | 4.3 | Low — less work than described |
| `approve_chapter` callback must thread through to `_run_one_chapter()` | 4.2 | Medium — requires two function signatures, not one |
