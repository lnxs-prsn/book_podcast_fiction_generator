# Implementation Journal v2 — Paper Run



## Pass 1.1 — Shared Config Loader

### Decision 1
**Situation**: `src/config.py` does not exist. `src/config.json` exists at the same location
the spec targets as the default path. All four files (`run_chapter.py`, `run_book.py`,
`tts/cli.py`, `call_api.py`) carry their own private `_load_config()` definition that each
manually constructs a path to `config.json`.

**Action**: Create `src/config.py` with the exact body given in the spec. The default path
`Path(__file__).parent / "config.json"` resolves to `src/config.json` — correct.

**Why**: Single source of truth for config loading; removes the duplicated path computation
across four files.

**Resolution**: Straightforward create. No conflict with the TOML-based
`src/fiction/pipeline/novel_pipeline/config.py` — they are independent modules.

---

### Decision 2
**Situation**: The spec gives import patterns per file depth, but `tts/cli.py` calls
`_load_config()` in three places beyond its definition: inside `build_api_payload()` (line 68),
`send_to_api()` (line 98), and `cli_entrypoint()` (line 233). Similarly, `call_api.py` calls
`_load_config()` in four resolver functions (lines 33, 40, 47, 62).

**Action**: After replacing the definition with `from config import load_config`, rename every
call site from `_load_config()` to `load_config()` in both files.

**Why**: The Done condition is `grep -rn "_load_config" ...` returning empty. Removing only
the definition while leaving the call sites would break the files entirely.

**Resolution**: The spec implies this but does not list call sites explicitly. Treat it as
implicit in the "remove definition" instruction. Three renames in `tts/cli.py`, four in
`call_api.py`.

---

### Decision 3
**Situation**: `run_chapter.py` computes `SRC = Path(__file__).parent` (IS `src/`). Same for
`run_book.py`. Both can resolve `from config import load_config` without a path-insert since
their directory is already `src/`.

**Action**: Add no `sys.path.insert` to `run_chapter.py` or `run_book.py`. Only `tts/cli.py`
(`parent.parent`) and `call_api.py` (`parent.parent.parent`) need the insert.

**Why**: The spec confirms this: "They need no additional path-insert." Adding one would be
redundant but harmless; omitting it is cleaner.

**Resolution**: Confirmed by the spec's own note. No action needed for the two top-level runners.

---

## Pass 1.2 — Podcast Exception Hierarchy

### Decision 4
**Situation**: `src/podcast_script_generator/llm/exceptions.py` does not exist. The new
exception classes (`PodcastError`, `PDFExtractionError`, `ScriptGenerationError`,
`TTSSubmissionError`, `TTSTimeoutError`) need to be created from scratch.

**Action**: Create the file with the five-class hierarchy. `PodcastError` is the base class;
the others inherit from it.

**Why**: The hierarchy provides typed catch targets at the CLI boundary and in `cli_entrypoint()`.

**Resolution**: New file, clean slate. Import path for consumers:
`from src.podcast_script_generator.llm.exceptions import PodcastError` (or relative if inside
the `llm/` package).

---

### Decision 5
**Situation**: `tts/cli.py`'s `main()` already raises exceptions (no `sys.exit()` in it).
`cli_entrypoint()` already exists. There is a local `AuthError` class defined at lines 33–35.
The spec deviation note correctly identifies this: the work for `tts/cli.py` is a type-remap,
not an exception-introduction pass.

**Action**: Replace the local `AuthError` with `TTSSubmissionError` from the new hierarchy.
Map the existing `raise RuntimeError(f"WaveSpeed job failed...")` (line 141) and the
`AuthError` raise site (line 154) to `TTSSubmissionError`. Map `raise ConnectionError(...)`
(line 156) to `TTSTimeoutError`. Broaden `cli_entrypoint()`'s catch clause from
`(ValueError, AuthError, ConnectionError, RuntimeError, OSError)` to `(PodcastError,
ValueError, OSError)`.

**Why**: After type-remapping, the hierarchy propagates consistently to the boundary.

**Resolution**: `AuthError` class definition is deleted in this pass (the only `sys.exit()` that
remains in `tts/cli.py` after this is the one inside `cli_entrypoint()` — that is the CLI
boundary and is intentional per the Done condition).

---

### Decision 6
**Situation**: `main.py` in `podcast_script_generator/llm/` currently has multiple `sys.exit()`
calls inside its `main()` function (lines 31, 33, 37, 41). It already has a `__main__` guard
at lines 44–45 that just calls `main()` directly.

**Action**: Replace `sys.exit()` calls inside `main()` with `raise PDFExtractionError` (for
`FileNotFoundError`), `raise ScriptGenerationError` (for `ValueError` and `KeyError`), and
`raise PodcastError` (for the catch-all). Update the `__main__` guard to wrap the `main()`
call in a `try/except PodcastError` that prints to stderr and calls `sys.exit(1)`.

**Why**: `sys.exit()` inside library-style functions prevents programmatic reuse. Moving it to
the `__main__` guard keeps the file runnable while making the pipeline functions clean.

**Resolution**: Done condition uses `grep -rn "sys.exit" src/podcast_script_generator/`
expecting empty. But `sys.exit(1)` in the updated `__main__` guard would be caught by grep.
The spec acknowledges this: "exclude with `grep -v '__main__'"`. Use the qualified form
`grep -rn "sys.exit" src/podcast_script_generator/ | grep -v "__main__"` for verification.

---

## Pass 1.3 — Structured Logging Migration

### Decision 7
**Situation**: `tts/cli.py` has no `import logging` and no `logger` object. The four target
print calls are inside `send_to_api()` at 8–12 spaces of indentation (inside `try:`). Neither
`call_api.py` nor `save_output.py` have a logger defined.

**Action**: Add `import logging` and `logger = logging.getLogger(__name__)` to all three files
before converting print calls. In `tts/cli.py`: convert lines 119, 121, 122 to `logger.info`,
line 144 to `logger.debug`. In `call_api.py`: convert line 126 to `logger.debug`. In
`save_output.py`: convert line 26 to `logger.debug`.

**Why**: `logging.getLogger(__name__)` uses the module name as the logger identifier, which is
the standard Python pattern for library code.

**Resolution**: Three files need both the import and the logger assignment added, not just the
print-to-log conversion. The spec does not call out the missing logger setup explicitly for
`call_api.py` — it is implied by the migration.

---

### Decision 8
**Situation**: `run_chapter.py`'s `main()` has seven `print()` calls (lines 232, 237–240, 244,
249). The spec only adds `logging.basicConfig` to `run_chapter.py` and `run_book.py` in this
pass. None of those `main()` prints are targeted here.

**Action**: Add `logging.basicConfig(level=logging.INFO, format="%(message)s")` near the top
of the `main()` function (or at module level) in both files. Do not touch the existing print
calls in those functions.

**Why**: The print calls in `run_chapter.py`'s `main()` are the CLI output — they are stripped
entirely in Pass 2.3 when the body migrates to `generate_chapter_podcast()`. Premature
conversion would complicate that pass.

**Resolution**: The Done condition grep only targets `src/podcast_script_generator/` and
`src/tts/cli.py`. The prints surviving in `run_chapter.py`/`run_book.py` are expected at this
stage.

---

## Pass 2.1 — Speaker Normalization Extract

### Decision 9
**Situation**: The function to extract is named `_to_speaker_format` in the current code
(lines 55–117 of `run_chapter.py`), not `normalize_speakers`. It has three call sites:
line 127 (`run_local`), and lines 145 and 146 (`run_llm` — one for `fiction_meta` branch,
one for all other modes). `src/util/` does not exist.

**Action**: Create `src/util/__init__.py` (empty) and `src/util/normalize.py` containing the
extracted function renamed to `normalize_speakers`. Update all three call sites in
`run_chapter.py`. Delete the original `_to_speaker_format` definition.

**Why**: Extract-and-rename is the spec's intent. The Done condition verifies function
name: `from src.util.normalize import normalize_speakers`.

**Resolution**: `run_chapter.py` sits in `src/` and can import `from util.normalize import
normalize_speakers` directly, no path insert needed. The function body is a pure text
transform (no side effects, no imports) — safe to lift verbatim.

---

## Pass 2.2 — Canonical Types

### Decision 10
**Situation**: `src/endpoints/` does not exist. `PodcastResult` and `ScriptMode` need to be
created as a foundation before any endpoint functions are written. The codebase uses `str | None`
union syntax without `from __future__ import annotations` (confirmed in `run_chapter.py` line 135),
confirming Python 3.10+ — the `Path | None` union in `PodcastResult` is valid.

**Action**: Create `src/endpoints/__init__.py` (empty) and `src/endpoints/podcast.py` with the
`ScriptMode` enum and `PodcastResult` dataclass exactly as specified.

**Why**: Defining full fields here avoids revisiting the file in Pass 2.3 (spec's own note).

**Resolution**: Clean new file. The `ScriptMode` values mirror `run_chapter.py`'s argparse
`choices` exactly; no inference needed.

---

## Pass 2.3 — generate_chapter_podcast()

### Decision 11
**Situation**: The spec says "move the body of `run_chapter.py`'s `main()` verbatim into this
function." The body (lines 167–253) calls three helper functions: `run_local()`, `run_llm()`,
and `run_tts()` — all defined in `run_chapter.py`. After Pass 5.3 shims `run_chapter.py` to a
single forwarding line, those helpers are destroyed. If `generate_chapter_podcast()` in
`endpoints/podcast.py` still calls them via `import run_chapter`, it breaks at Pass 5.3.

**Action**: When building `generate_chapter_podcast()`, move (not just call) `run_local()`,
`run_llm()`, and `run_tts()` into `endpoints/podcast.py` as well. `run_chapter.py` can then
re-export them for `run_book.py`'s current usage until that is shimmed in Pass 5.3.

**Why**: The spec does not state this explicitly but the dependency is unavoidable — Pass 5.3
destroys `run_chapter.py`'s module namespace, which is the only current home for those
helpers.

**Resolution**: This is a spec gap. Calling out now so Pass 5.3 does not hit a broken import.
The safest resolution: move all three helpers into `endpoints/podcast.py` during this pass.
`run_book.py` temporarily imports them from there (`from endpoints.podcast import run_llm ...`)
until it is also shimmed in Pass 5.3.

---

### Decision 12
**Situation**: `run_chapter.py`'s `main()` contains seven `print()` calls (lines 232, 237–240,
244, 249) and seven `sys.exit()` calls (lines 191, 201, 205, 213, 219, 225, 229). The context-
file and fiction-dir loading blocks span lines 193–231. The endpoint wraps the entire body in
`try/except Exception`.

**Action**: Strip argparse (lines 168–186), all `print()` calls, and all `sys.exit()` calls
when copying the body. Context-file and fiction-dir loading logic stays in the endpoint
(the function accepts `context: str | None` and `fiction_content: str | None` directly,
but the file-resolution logic for `--context-file` and `--fiction-dir` belongs here, not in
the CLI wrapper). Return `PodcastResult(ok=True, script_path=script_out, audio_path=saved)` on
success; `PodcastResult(ok=True, script_path=script_out)` when `skip_audio=True`.

**Why**: The endpoint must have zero argparse, zero print, zero sys.exit per the phase goal.

**Resolution**: The fiction-dir discovery (lines 207–231) requires the source PDF's stem to
extract the chapter number — that logic is parameterized by `pdf_path`, so it ports cleanly.

---

## Pass 2.4 — generate_book_podcast()

### Decision 13
**Situation**: `run_book.py`'s `main()` includes an `input()` call at lines 100–103 to prompt
for `toc_page` when it is not provided by CLI or config. The `generate_book_podcast()` signature
accepts `toc_page: int | None = None`. The endpoint must not prompt stdin.

**Action**: If `toc_page` is `None` when the endpoint runs, fall back to
`_load_config().get("toc_page")` then raise an error if still missing — do not call `input()`.
The `input()` prompt belongs only in the CLI wrapper (Pass 2.5).

**Why**: `generate_book_podcast()` is a programmatic endpoint; callers cannot provide stdin.

**Resolution**: The spec does not call this out explicitly. Flag it: the CLI wrapper (`cli/podcast.py`,
Pass 2.5) is where the interactive `toc_page` prompt lives, if at all.

---

### Decision 14
**Situation**: `run_book.py` currently imports `run_chapter as rc` and calls `rc.run_llm()`,
`rc.run_local()`, `rc.run_tts()`. After Pass 5.3 shims both files, those calls would be broken.
`generate_book_podcast()` calls `generate_chapter_podcast()` per chapter instead — so the
dependency on `run_chapter`'s helpers is severed at this pass.

**Action**: `generate_book_podcast()` calls `generate_chapter_podcast()` per chapter. No direct
use of `run_llm/run_local/run_tts`. This is the clean break.

**Why**: `generate_chapter_podcast()` already encapsulates all chapter-level logic including
helper calls.

**Resolution**: The temporary slicer import from Pass 2.4 (`sys.path.insert ... from pdf_splitter import run_splitter`) is replaced by `from endpoints.slicer import run_splitter` after Pass 3.2.

---

## Pass 2.5 — Podcast CLI Wrapper

### Decision 15
**Situation**: `src/cli/` does not exist. The wrapper must cover the full flag surface of both
`run_chapter.py` and `run_book.py`. `run_book.py` has `--slice-only` (line 75) which is not
listed in `run_chapter.py`'s argparse at all.

**Action**: Create `src/cli/__init__.py` (empty) and `src/cli/podcast.py` with the routing
logic. Include ALL flags: chapter flags (`pdf` positional, `--llm`, `--skip-audio`, `--mode`,
`--context`, `--context-file`, `--fiction-dir`) and book flags (`--book`, `--toc-page`,
`--no-ocr`, `--force`, `--slice-only`).

**Why**: Pass 5.3 pre-condition explicitly checks: `python src/cli/podcast.py --help | grep -- "--book"`. If book flags are missing, `run_book.py --help` behavior regresses after shimming.

**Resolution**: The `--slice-only` flag routes to a `generate_book_podcast()`-level concept
that stops after slicing. The endpoint's `generate_book_podcast()` would need to support a
`slice_only: bool = False` parameter, or the CLI handles it by calling the slicer directly
and returning early. Prefer the former to keep the endpoint self-contained.

---

## Pass 3.1 — TTS Engine Boundary

### Decision 16
**Situation**: `import argparse` sits at line 7 of `tts/cli.py` (module level). Every import
of `tts.cli` currently triggers argparse loading. Moving it inside `cli_entrypoint()` means the
module is importable for its `main()` function without the argparse side-load.

**Action**: Cut line 7 (`import argparse`) and paste it as the first line inside
`cli_entrypoint()`.

**Why**: `run_chapter.py`'s `run_tts()` already does `from cli import main as tts_main` — it
never needs argparse. After Phase 2, `generate_chapter_podcast()` in `endpoints/podcast.py`
imports `main` from `tts/cli.py` similarly. Lazy-loading argparse keeps the import side-effect-
free.

**Resolution**: One-line change. Done condition: `grep "argparse" src/tts/cli.py` returns hits
only inside `cli_entrypoint()`.

---

## Pass 3.2 — Slicer Import Anchor

### Decision 17
**Situation**: `src/slicer/pdf_splitter.py` exists (confirmed). `src/endpoints/slicer.py` does
not. The spec's full content adds `sys.path.insert(0, str(Path(__file__).parent.parent))` —
this resolves to `src/`, making `from slicer.pdf_splitter import run_splitter` valid.

**Action**: Create `src/endpoints/slicer.py` with the exact content given. Then update
`endpoints/podcast.py` to replace the temporary direct import with
`from endpoints.slicer import run_splitter`.

**Why**: Without the path-insert, running from `harnessv3/` would look for `harnessv3/slicer/`,
which does not exist (the correct path is `harnessv3/src/slicer/`).

**Resolution**: After this pass, the TODO comment planted in Pass 2.4 is removed. Done condition
grep confirms it.

---

## Pass 4.1 — SessionResult Dataclass + Callback Type

### Decision 18
**Situation**: `session.py`'s `run_session()` currently returns `None` (line 456 signature:
`-> None`). `current_totals` is already imported from `.cost` (used elsewhere in the file).
`ApproveChapterFn` and `SessionResult` do not exist anywhere in the module.

**Action**: Add the two definitions to `session.py`. No behavior change. `cost_usd` field
reads from `current_totals(config)["session_total"]`; `state_path` from
`Path(config["state_file_path"])`.

**Why**: Defining them in this pass isolates the type work from the behavior change in Pass 4.2.
Pass 4.1 being a no-op behaviorally means it can be verified by import alone.

**Resolution**: `dataclass` and `Callable` imports need to be added. `Path` is already imported.
Clean add.

---

## Pass 4.2 — session.py Callback Injection

### Decision 19
**Situation**: `run_session()` has multiple return points. Full audit:
- Line 492: `return` (should_continue is False — early exit from `_resolve_starting_chapter`)
- Line 499: `return` (session declined at "Proceed?" gate)
- Implicit fall-through at end of function after the try/except/for block (normal completion
  or loop-break paths)

The `break` cases inside the loop (user quit at line 532, stale living doc at line 554) both
fall through to `log_event("session_complete", ...)` at line 562 and then the implicit
fall-through return.

**Action**: Return a `SessionResult` at all three exit points. The two early exits return
`SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False,
state_path=Path(config["state_file_path"]))`. The fall-through returns
`SessionResult(chapters_written=completed, final_chapter_number=current_chapter,
cost_usd=current_totals(config)["session_total"], completed=True, state_path=...)`.

**Why**: Callers (Pass 4.4's `run_novel_session()`) inspect the result to report session
outcomes without parsing stdout.

**Resolution**: `sys.exit(1)` on line 574 (inside `except KeyboardInterrupt`) becomes
`raise KeyboardInterrupt` so it propagates cleanly to the CLI boundary. This replaces a hard
process exit with exception propagation — the caller in `novel_pipeline/cli.py` already
handles `KeyboardInterrupt` (line 111).

---

### Decision 20
**Situation**: The Done condition says `grep "input()" src/fiction/pipeline/novel_pipeline/session.py`
returns empty. But two helper functions in `session.py` — `_prompt_yes_no()` (line 68) and
`_prompt_choice()` (lines 105–106) — both call `input()` directly. The spec's Pass 4.2 only
targets the approval prompt in `_run_one_chapter()` (lines 718–728).

**Action**: If the Done condition must be satisfied strictly, `_prompt_yes_no` and `_prompt_choice`
also need `input()` removed from their bodies. However those helpers are gated by `auto=True`
paths that never reach `input()`. With `auto_approve=True` the grep-found `input()` calls
are unreachable at runtime.

**Why**: The Done condition is stricter than the described changes. The behavioral Done condition
("completes without touching stdin") passes with `auto_approve=True`. The grep Done condition
fails unless all `input()` is removed.

**Resolution**: Discrepancy between the two Done conditions. Two options:
(a) Accept the behavioral test only — leave `_prompt_yes_no`/`_prompt_choice` untouched
    (they are needed for interactive use, gated by `auto=True`).
(b) Strictly satisfy the grep by converting those helpers to accept an optional
    `io_fn` injectable (larger change, not described in spec).

Flag for implementer: use `grep "input()" ... | grep -v "_prompt_yes_no\|_prompt_choice"` as
the practical Done condition, or confirm with the spec owner which interpretation is intended.

---

## Pass 4.3 — novel_pipeline cli.py Update

### Decision 21
**Situation**: `cli.py`'s `_build_parser()` already defines `--auto-approve` at line 47.
`main()` already calls `run_session()` without an `approve_chapter` argument.
The spec deviation note says: do NOT add `--auto-approve` again.

**Action**: Add `_prompt_user(chapter_num: int, draft_text: str) -> bool` inside `cli.py`.
After `args = _build_parser().parse_args(argv)`, construct `approve_fn` based on
`args.auto_approve`. Pass `approve_chapter=approve_fn` to `run_session()`.

**Why**: After Pass 4.2, `run_session()` accepts `approve_chapter`. The CLI now supplies it
instead of `session.py` reading stdin directly.

**Resolution**: `_prompt_user` prints first 500 chars of `draft_text` and reads `[y/n/q]`.
The `q` path should return `False` and rely on the caller (session loop) to quit — or
`_prompt_user` raises a sentinel. Clarify that the callback returning `False` means "reject"
(which loops back for regeneration), not "quit". The `q` path needs to be handled separately
— one option: `_prompt_user` raises `KeyboardInterrupt` on `q`, which is already caught by
`run_session()`'s exception handler.

---

## Pass 4.4 — Fiction Endpoint Wrapper

### Decision 22
**Situation**: `src/fiction/pipeline/novel_pipeline.egg-info/` exists — the package is
installed in editable mode. Package imports (`from novel_pipeline.config import load_config`,
`from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult`) should work
if the venv with that install is active.

**Action**: Attempt the package import first. If it fails, fall back to the path-insert
pattern given in the spec. In practice, since the egg-info is present, the package import
path is correct.

**Why**: The editable install makes the package importable by name, avoiding fragile
path manipulation.

**Resolution**: The spec's `load_config_toml()` alias reference is confirmed as incorrect —
`novel_pipeline/config.py` exports `load_config(path)`. Do not create an alias. Use
`load_config(str(config_path))` directly.

---

## Pass 4.5 — Fiction CLI Shim

### Decision 23
**Situation**: `src/cli/fiction.py` does not exist. It must mirror the exact flag set from
`src/fiction/pipeline/novel_pipeline/cli.py`: `--config`, `--auto-approve`, `--dry-run`,
`--resume`, `--chapter-start`, `--ignore-cost-limit`.

**Action**: Create `src/cli/fiction.py`. Add the same `_prompt_user()` function as Pass 4.3
(exact duplicate). Construct `approve_fn`. Call `run_novel_session()` from
`src/endpoints/fiction.py`.

**Why**: `src/cli/fiction.py` is the user-facing entry point replacing the internal
`novel_pipeline/cli.py` for external callers.

**Resolution**: The `_prompt_user` function appears in both `novel_pipeline/cli.py` (Pass 4.3)
and `src/cli/fiction.py` (this pass). This is intentional per the spec. A future cleanup could
extract it to `src/util/`, but that is out of scope here.

---

## Pass 5.1 — Remove Private Config Loaders

### Decision 24
**Situation**: Pass 1.1 migrated all four files to `from config import load_config` and renamed
call sites. The `_load_config()` function definitions remain as dead code in each file.

**Action**: Delete the `_load_config()` function definitions from all four files.

**Why**: Pre-condition requires Pass 1.1 to be complete and verified with a four-hit grep
before proceeding. This pass is purely dead-code removal.

**Resolution**: Straightforward deletion. Done condition: `grep -rn "_load_config" src/` returns
empty. The definitions are 7–9 lines each; no callers remain after Pass 1.1.

---

## Pass 5.2 — Delete run_simple.py

### Decision 25
**Situation**: `src/fiction/run_simple.py` exists and is a fully standalone script (hardcoded
`PROJECT_DIR`, no exports, no imports from the rest of the project). The pre-check
`grep -rn "run_simple" src/` returns empty — nothing in the codebase imports it.

**Action**: Verify the pre-check, then delete the file.

**Why**: It is an orphaned prototype for an earlier version of the novel pipeline, superseded
by `src/fiction/pipeline/novel_pipeline/`. Keeping it creates confusion about which pipeline
to use.

**Resolution**: The file uses `sys.exit()`, `input()`, hardcoded global config — none of which
need cleanup before deletion. Delete outright.

---

## Pass 5.3 — Shim run_chapter.py and run_book.py

### Decision 26
**Situation**: `run_book.py` currently does `import run_chapter as rc` at line 143 and calls
`rc.run_llm()`, `rc.run_local()`, `rc.run_tts()` (lines 166–172). After both files are shimmed,
those symbols no longer exist in `run_chapter.py`'s namespace (the shim exposes only `main`
from `cli.podcast`).

**Action**: Apply both shims simultaneously as the spec requires. Before doing so, verify that
`generate_book_podcast()` in `endpoints/podcast.py` calls `generate_chapter_podcast()` directly
— not `rc.run_llm` etc. — so the endpoint is not broken by the shim.

**Why**: The spec explicitly flags the ordering risk: "Apply BOTH shims in the same pass."
The underlying reason is that `run_book.py` depends on `run_chapter.py`'s helpers which
disappear at shim time.

**Resolution**: This pass is safe ONLY if Decision 11 (Pass 2.3) was resolved by moving
`run_local`, `run_llm`, `run_tts` into `endpoints/podcast.py`. If they were left in
`run_chapter.py`, the endpoint breaks here. Confirm the move was done before marking Pass 5.3
as actionable.

---

### Decision 27
**Situation**: After shimming, `run_chapter.py` becomes:
```python
from cli.podcast import main; main()
```
`run_book.py` becomes the same. Both files are in `src/`. `cli/podcast.py` is also in `src/`.
The import resolves because `src/` is on `sys.path` (or the shim inherits it from the runner).

**Action**: Verify both shims produce identical output to their CLI equivalents using the Done
condition fixture runs.

**Why**: The shim's import `from cli.podcast import main` must find `src/cli/podcast.py`.
Since `run_chapter.py` is in `src/` and Python adds the script's directory to `sys.path`,
this resolves correctly.

**Resolution**: No path manipulation needed in the shim bodies. The two-liner is sufficient.

---

## Pass 5.4 — Update initial_readme.md

### Decision 28
**Situation**: `src/initial_readme.md` exists (added in a recent commit). It describes the
project's entry points. After Phases 2–5, the primary CLIs are `src/cli/podcast.py` and
`src/cli/fiction.py`, with `run_chapter.py` and `run_book.py` reduced to shims.

**Action**: Update the Entry Points section to list `src/cli/podcast.py` and `src/cli/fiction.py`
as the primary CLIs. Document `run_chapter.py` and `run_book.py` as shims that forward to
`src/cli/podcast.py`.

**Why**: Stale documentation causes incorrect usage patterns. The Done conditions for this pass
are two greps: one for `src/cli/podcast.py` and one for the word `shim`.

**Resolution**: Mechanical documentation update. No code impact. Can be done independently of
any other pass as long as the CLI files described actually exist (i.e., after Pass 2.5 at
minimum).

---

## Cross-Phase Findings Summary

| Finding | Affects | Severity |
|---------|---------|----------|
| `run_local`/`run_llm`/`run_tts` not moved in spec (Decision 11) | Pass 2.3 → Pass 5.3 | High — breaks endpoint at shim time if not addressed |
| `input()` in `_prompt_yes_no`/`_prompt_choice` survives Pass 4.2 (Decision 20) | Pass 4.2 Done condition | Medium — grep fails; runtime passes with auto_approve=True |
| `toc_page` prompt not in endpoint (Decision 13) | Pass 2.4 | Medium — silent if caller doesn't pass toc_page; should raise |
| `_load_config()` call sites need renaming, not just definition removal (Decision 2) | Pass 1.1 | Low — implied, not stated |
| `q` path in `_prompt_user` callback needs quit semantic (Decision 21) | Pass 4.3 | Low — design clarification needed |
