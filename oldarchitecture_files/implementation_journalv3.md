Implementation Journal v3 — Paper Run

---

## Pass 1.1 — Shared Config Loader

### Decision 1
**Situation**: `src/config.py` does not exist. `src/config.json` exists at the correct location.
All four target files have private `_load_config()` definitions that each compute a path to
`config.json` relative to their own `__file__`.

**Action**: Create `src/config.py` with the exact body from the spec.

**Why**: Single source of truth for config loading; the `_DEFAULT_PATH` anchored to
`Path(__file__).parent / "config.json"` resolves to `src/config.json` regardless of
caller working directory.

**Resolution**: Straightforward create. No collision with the TOML-based
`src/fiction/pipeline/novel_pipeline/config.py` — independent module.

---

### Decision 2
**Situation**: The spec explicitly lists call-site renames for `tts/cli.py` (3 sites) and
`call_api.py` (4 sites). Confirmed in source:
- `tts/cli.py` — `_load_config()` called in `build_api_payload()` (line 68),
  `send_to_api()` (line 98), `cli_entrypoint()` (line 233). Count: 3. ✓
- `call_api.py` — called in `_resolve_model()` (line 32), `_resolve_max_tokens()` (line 40),
  `_resolve_api_url()` (line 47), `_resolve_retry_after()` (line 63). Count: 4. ✓

**Action**: Rename all 7 sites from `_load_config()` → `load_config()` after removing definitions
and adding imports.

**Why**: The Done condition `grep -rn "_load_config" ...` catches call sites, not just definitions.
Removing the definition without renaming the calls breaks both files at runtime.

**Resolution**: Counts match spec. No ambiguity.

---

### Decision 3
**Situation**: The spec treats `run_chapter.py` and `run_book.py` as "remove definition + add
import" without explicitly listing call sites needing rename. But both files contain call sites
beyond the definition:
- `run_chapter.py` line 157: `cfg_speakers = _load_config().get("speakers", {})` inside
  `run_tts()`.
- `run_book.py` line 97: `toc_page = args.toc_page or _load_config().get("toc_page")` inside
  `main()`.

The Done condition `grep -rn "_load_config" src/run_chapter.py src/run_book.py ...` would catch
both of these and return non-empty, failing the gate.

**Action**: Rename both call sites to `load_config()` as part of Pass 1.1. This is implied by the
Done condition even though the spec text does not list them explicitly (unlike the v3 note for
tts/cli.py and call_api.py).

**Why**: A working Done condition requires zero hits for `_load_config` anywhere in the four files.
These two are call sites that survive definition removal.

**Resolution**: Two additional renames beyond what the spec text says — one in each top-level
runner. Low risk but easy to miss.

---

## Pass 1.2 — Podcast Exception Hierarchy

### Decision 4
**Situation**: `src/podcast_script_generator/llm/exceptions.py` does not exist — must be created.
`main.py` has a `__main__` guard at line 44 (`if __name__ == "__main__": main()`) but no
try/except wrapper around the `main()` call. The spec says to add one.

Current `main.py` has 4 `sys.exit(1)` calls inside `main()` itself (lines 30, 33, 37, 41),
all inside a single try/except chain. After the refactor, those exits become typed raises and the
`__main__` guard catches `PodcastError`.

**Action**: Create `exceptions.py`. Rewrite the `main()` body to raise typed exceptions instead of
`sys.exit(1)`. Replace the `__main__` guard with the wrapped version from the spec.

**Why**: `main()` must be callable without triggering `sys.exit()` when used as a library. The
`__main__` guard is the only place `sys.exit(1)` is permitted for this module.

**Resolution**: Straightforward. The exception → sys.exit mapping is: FileNotFoundError →
PDFExtractionError, ValueError/KeyError → ScriptGenerationError, catch-all Exception →
PodcastError. Note: KeyError here is OPENROUTER_API_KEY missing from env, which maps to
ScriptGenerationError by spec, though semantically a missing-key error is closer to a
configuration error. Builder follows spec mapping without deviating.

---

### Decision 5
**Situation**: `tts/cli.py` must import `PodcastError`, `TTSSubmissionError`, and
`TTSTimeoutError` from `exceptions.py`. The exceptions file lives at
`src/podcast_script_generator/llm/exceptions.py`. Pass 1.1 added
`sys.path.insert(0, str(Path(__file__).parent.parent))` to `tts/cli.py`, which puts `src/`
on the path. From `src/`, the import path is `podcast_script_generator.llm.exceptions`.

**Action**: Add to `tts/cli.py`:
```python
from podcast_script_generator.llm.exceptions import (
    PodcastError, TTSSubmissionError, TTSTimeoutError
)
```
Delete the local `AuthError` class. Remap raises and the `cli_entrypoint()` catch as spec says.

**Why**: The path insert from Pass 1.1 makes `src/` importable. The full dotted path is needed
because `podcast_script_generator/` has no `__init__.py` at `src/` level — checking confirms the
package structure is accessed via `src/podcast_script_generator/llm/`.

**Resolution**: The spec does not spell out the import path for `tts/cli.py`'s use of exceptions,
only that the remapping must happen. Builder must derive the import path from the file location.
Not a blocker, but a gap in the spec.

---

## Pass 1.3 — Structured Logging Migration

### Decision 6
**Situation**: The spec lists 4 prints to convert in `send_to_api()`: submission confirmation,
recovery-file notice, polling start, per-poll status. But inspecting `send_to_api()` reveals a
5th print at line 135–136: `print(f"  [done] {elapsed:.0f}s")` inside the
`if status == "completed":` branch.

The Done condition `grep -rn "^\s*print(" src/podcast_script_generator/ src/tts/cli.py`
catches all print calls. If the 5th print is not converted it would return non-empty, failing the
gate.

**Action**: Convert all 5 prints in `send_to_api()` to logger calls. The 5th ("done" confirmation)
maps naturally to `logger.info(...)`.

**Why**: The Done condition is authoritative. All prints in the listed scopes must be converted
regardless of whether the spec prose names them explicitly.

**Resolution**: Builder cannot rely solely on the spec's prose count. Must inspect the function
body directly and satisfy the grep Done condition.

---

## Pass 2.1 — Speaker Normalization Extract

### Decision 7
**Situation**: `src/util/` directory does not exist. The spec requires creating two files:
`src/util/__init__.py` (empty) and `src/util/normalize.py`. The `__init__.py` must come first so
that `from util.normalize import normalize_speakers` is resolvable as a package import.

Three call sites of `_to_speaker_format()` confirmed in `run_chapter.py`:
- Line 127: inside `run_local()`
- Line 145: inside `run_llm()`, fiction_meta branch
- Line 146: inside `run_llm()`, default branch

**Action**: Create `src/util/__init__.py` (empty), then `src/util/normalize.py` with
`normalize_speakers` as the extracted+renamed body of `_to_speaker_format()`. Delete the
definition from `run_chapter.py`. Update the 3 call sites to `normalize_speakers(...)`.

**Why**: `run_chapter.py` is in `src/` — no path insert needed for `from util.normalize import
normalize_speakers`. The empty `__init__.py` establishes the package.

**Resolution**: Straightforward extraction and rename. Note that `_to_speaker_format` takes only
`text: str` — same signature as `normalize_speakers`. No interface change needed.

---

## Pass 2.2 — Canonical Types

### Decision 8
**Situation**: `src/endpoints/` directory does not exist. The spec introduces `ScriptMode` and
`PodcastResult` in a new `src/endpoints/podcast.py`. `PodcastResult` uses the union type syntax
`Path | None` and `Exception | None` — available natively only in Python 3.10+.

Checking existing `session.py` (which already uses `str | None` in function signatures at line 644
and `list[PodcastResult]` in the spec) confirms the project targets Python 3.10+.

**Action**: Create `src/endpoints/__init__.py` (empty) and `src/endpoints/podcast.py` with
`ScriptMode` and `PodcastResult` exactly as specified. No compatibility shim needed.

**Why**: The codebase already uses 3.10+ union syntax throughout; `PodcastResult` is consistent
with this convention. Adding `from __future__ import annotations` would be unnecessary overhead.

**Resolution**: Straightforward create. `ScriptMode` values (`2person`, `4person`, `code`,
`realworld`, `fiction_meta`) match `run_chapter.py`'s `--mode` choices exactly. ✓

---

## Pass 2.3 — generate_chapter_podcast()

### Decision 9
**Situation**: `run_local()`, `run_llm()`, and `run_tts()` in `run_chapter.py` reference two
module-level constants: `ROOT = Path(__file__).parent.parent` and `SRC = Path(__file__).parent`.
When `__file__` is `src/run_chapter.py`, these resolve to `harnessv3/` and `src/` respectively.

After moving these helpers to `src/endpoints/podcast.py`, `__file__` becomes
`src/endpoints/podcast.py`:
- `Path(__file__).parent` = `src/endpoints/`
- `Path(__file__).parent.parent` = `src/`
- `Path(__file__).parent.parent.parent` = `harnessv3/`

The spec says "move helpers" but does not mention updating the path constants.

**Action**: In `endpoints/podcast.py`, define:
```python
_SRC  = Path(__file__).parent.parent       # src/
_ROOT = Path(__file__).parent.parent.parent # harnessv3/
```
Use `_SRC` and `_ROOT` (prefixed to avoid collision with any future caller names). Update all
three helper bodies to use `_SRC` and `_ROOT` instead of the bare `ROOT`/`SRC` names. Also update
`SCRIPTS_OUT` and `AUDIO_OUT` references.

**Why**: Without this correction the helpers compute wrong paths — `run_local()` would look for
`src/endpoints/../decide_later/local` which is `src/decide_later/local` instead of
`harnessv3/decide_later/local`.

**Resolution**: Gap in spec. Builder must derive the path fix from the move. Not complex once
noticed, but easy to overlook.

---

### Decision 10
**Situation**: `run_tts()` in `run_chapter.py` calls `load_config()` (after Pass 1.1 renames it).
When `run_tts()` moves to `endpoints/podcast.py`, the import `from config import load_config`
must also come along. `endpoints/podcast.py` is at `src/endpoints/` — one level below `src/` —
so a `sys.path.insert(0, str(Path(__file__).parent.parent))` is required before the import.

**Action**: Add to `endpoints/podcast.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # adds src/ to path
from config import load_config
```

**Why**: `endpoints/podcast.py` is not in `src/` itself; Python will not find `config` without
the path insert. Same pattern as `tts/cli.py` from Pass 1.1.

**Resolution**: Gap in spec — the spec details path-insert patterns for Pass 1.1 files but does
not revisit the pattern for the newly created `endpoints/podcast.py`. Builder must apply the
same rule.

---

### Decision 11
**Situation**: `run_book.py` at line 143 does `import run_chapter as rc` and at lines 166–172
calls `rc.run_llm()`, `rc.run_local()`, `rc.run_tts()`. After Pass 2.3, these functions are
removed from `run_chapter.py`. Until Pass 5.3 shims `run_book.py`, this breaks `run_book.py`.

The spec covers this: add a temporary import to `run_book.py`:
```python
from endpoints.podcast import run_llm, run_local, run_tts
```
`run_book.py` is at `src/` — `endpoints` is importable without a path insert.

**Action**: Add the temporary re-import to `run_book.py` as part of Pass 2.3. Keep the
`import run_chapter as rc` line for any other `rc.*` references — audit shows `rc.run_llm`,
`rc.run_local`, `rc.run_tts` are the only uses; no other `rc.*` calls exist.

**Why**: `run_book.py` must remain functional throughout the refactor. Removing `run_chapter.py`'s
helpers without patching `run_book.py` would break batch processing immediately.

**Resolution**: Spec explicitly covers this. Builder action: remove the `import run_chapter as rc`
line entirely and use the direct endpoint imports in the 3 call sites.

---

### Decision 12
**Situation**: `generate_chapter_podcast()` has signature
`fiction_content: str | None = None` (already-loaded string). But the spec also says:
"Keep: context-file loading logic and fiction-dir discovery logic — they belong in the endpoint,
not the CLI wrapper."

The fiction-dir discovery logic in `run_chapter.py`'s `main()` (lines 207–231) resolves a
chapter number from the PDF stem, constructs `chapter_XX.md` path, and reads the file. If this
logic stays in the endpoint, the endpoint must receive a `fiction_dir: Path` — not a
pre-loaded `fiction_content: str`. But the given signature takes `fiction_content: str`.

These two statements are in direct conflict.

**Action**: Follow the given function signature (`fiction_content: str | None`). The discovery
logic must therefore move to the CLI wrapper (Pass 2.5), which resolves `fiction_dir` →
`fiction_content` before calling the endpoint. The spec prose is inaccurate on this point.

**Why**: The function signature is machine-enforceable and the Done condition tests the signature.
The prose statement about discovery belonging in the endpoint is contradicted by the actual
interface. Signatures win over prose.

**Resolution**: Inconsistency in spec. Builder follows the signature. The CLI wrapper (Pass 2.5)
does the `fiction_dir` → `fiction_content` file resolution.

---

## Pass 2.4 — generate_book_podcast()

### Decision 13
**Situation**: `run_book.py` line 97 computes `toc_page` in one expression:
`toc_page = args.toc_page or _load_config().get("toc_page")`. The endpoint spec splits this
into two guarded checks:
```python
if toc_page is None:
    toc_page = load_config().get("toc_page")
if toc_page is None:
    raise ValueError("toc_page is required...")
```

The `or` pattern in `run_book.py` has a subtle difference: `args.toc_page or ...` treats a
`toc_page=0` as falsy and falls through to config. The `is None` pattern in the spec correctly
handles `toc_page=0` (which would be an invalid value anyway for a real page number, but the
semantic clarity is worth noting).

**Action**: Use the two-step `is None` checks as given in the spec.

**Why**: `is None` is the correct idiom for optional parameters. The `or` fallback from
`run_book.py` is a latent bug (would treat page 0 as "not provided"). The spec fixes this.

**Resolution**: No action beyond following the spec. Good catch in v3.

---

## Pass 2.5 — Podcast CLI Wrapper

### Decision 14
**Situation**: `run_book.py`'s `--mode` choices are `["2person", "4person", "code", "realworld"]`
— `fiction_meta` is explicitly excluded from batch processing. The new `cli/podcast.py` merges
chapter and book routing in one file. The `--mode` flag applies to both paths.

If `fiction_meta` is included in the full choices list, a user can technically invoke
`python cli/podcast.py --book whole_book.pdf --mode fiction_meta`. The spec does not address
whether this combination is valid.

**Action**: Mirror `run_chapter.py`'s full mode choices (`2person`, `4person`, `code`,
`realworld`, `fiction_meta`) for the `--mode` flag. The `generate_book_podcast()` endpoint
passes `mode` to `generate_chapter_podcast()` which supports all modes. Do not restrict book
mode to the subset. Relying on the endpoint to handle unexpected combinations is acceptable.

**Why**: Adding a silent exclusion (`fiction_meta` only valid for chapter mode) would require
conditional validation in the wrapper that the spec doesn't specify. The cleaner choice is to
allow all modes uniformly and let the endpoint enforce constraints.

**Resolution**: Spec gap on mode intersection. Builder makes a judgment call. Documenting the
decision here for review.

---

### Decision 15
**Situation**: The CLI wrapper handles `--context-file` by passing the file content to the
endpoint as `context: str | None`. The `--fiction-dir` flag requires file discovery (see
Decision 12). Both are CLI wrapper responsibilities.

The fiction-dir discovery logic is about 20 lines in `run_chapter.py`'s `main()`. The builder
must copy this logic into `cli/podcast.py` (not import from the old location, since
`run_chapter.py` will be shimmed in Pass 5.3).

**Action**: Copy the fiction-dir discovery block into `cli/podcast.py` — extract chapter number
from PDF stem, resolve `chapter_XX.md`, read content. Pass the resulting string as
`fiction_content` to `generate_chapter_podcast()`.

**Why**: After Pass 5.3 shims `run_chapter.py`, the CLI wrapper is the only place with this
logic. It must be present in `cli/podcast.py` before that shim lands.

**Resolution**: Explicit consequence of Decision 12. Not complex, but must be done.

---

## Pass 3.1 — TTS Engine Boundary

### Decision 16
**Situation**: `tts/cli.py` has `import argparse` at module level (line 6), alongside the other
stdlib imports. The spec says to move it into `cli_entrypoint()`. `argparse` is used only inside
`cli_entrypoint()` — no other function references it.

**Action**: Cut line 6 (`import argparse`) and paste it as the first line inside
`cli_entrypoint()`. No other changes to the function body.

**Why**: Moving the import confines argparse to the CLI boundary. `main()` becomes importable
without triggering argument parsing setup at import time.

**Resolution**: Mechanical one-line move. The Done condition `grep "argparse" src/tts/cli.py`
confirming hits only inside `cli_entrypoint()` is sufficient to verify.

---

## Pass 3.2 — Slicer Import Anchor

### Decision 17
**Situation**: `src/slicer/pdf_splitter.py` exists (confirmed). `src/endpoints/slicer.py`
does not. After creating it, `endpoints/podcast.py` must replace the temporary direct import
from Pass 2.4 with `from endpoints.slicer import run_splitter`.

`endpoints/slicer.py` itself needs the `sys.path.insert` because `endpoints/` is not `src/` —
without it Python looks for `harnessv3/slicer/` which does not exist.

**Action**: Create `src/endpoints/slicer.py` exactly as specified. Update
`endpoints/podcast.py`: remove the temporary `TODO: replace after Pass 3.2` import block
and add `from endpoints.slicer import run_splitter`.

**Why**: The slicer module lives at `src/slicer/` — accessible only via a path insert or by
being in `src/`. The re-export wrapper in `endpoints/slicer.py` provides a stable import path
for all consumers.

**Resolution**: Straightforward. Verify the TODO comment grep returns empty as the Done
condition specifies.

---

## Pass 4.1 — SessionResult Dataclass + Callback Type

### Decision 18
**Situation**: `session.py` currently imports nothing from `typing` and nothing from
`dataclasses`. Two new imports are needed for `Callable` and `dataclass`. `Path` is already
imported at line 3. `current_totals` is already imported from `.cost` (line 26) — its return
dict has a `"session_total"` key confirmed in `cost.py`.

**Action**: Add to `session.py` imports:
```python
from dataclasses import dataclass
from typing import Callable
```
Then add `ApproveChapterFn` alias and `SessionResult` dataclass exactly as specified.

**Why**: These are type-annotation-only additions in this pass. No behavior changes. The Done
condition import test verifies both are accessible.

**Resolution**: Straightforward. `SessionResult.cost_usd` sourced from
`current_totals(config)["session_total"]` ✓ and `state_path` from
`Path(config["state_file_path"])` ✓ — both keys already in use throughout the file.

---

## Pass 4.2 — session.py Callback Injection

### Decision 19
**Situation**: The approval block in `_run_one_chapter()` (lines 718–729) currently has two
paths: `auto_approve` fast-path prints `[auto-approve] approving draft` and sets
`approval = "y"`, then the `else` branch reads `input(...)`. After replacing both with
`approved = approve_chapter(chapter_num, chapter_text)`, the `[auto-approve]` print
disappears entirely.

The spec does not mention this print. It is not in the "draft-preview prints (lines ~709–712)"
that the spec says to convert to `logger.info`. However the Done condition for Pass 1.3
(`grep -rn "^\s*print("`) was already applied — by Pass 4.2 these prints have already been
converted. No residual print survives.

**Action**: Replace the entire approval block (auto_approve fast-path + input block) with:
```python
approved = approve_chapter(chapter_num, chapter_text)
if not approved:
    # rejected: log and continue loop
    ...
    continue
# approved: break out of rejection loop
break
```
The `approval == "q"` quit path is now handled by the callback raising `KeyboardInterrupt`
(from `_prompt_user`). The `approval == "n"` reject path maps to `approved = False`.

**Why**: The callback owns the approval decision. The old three-value `y/n/q` string is
replaced by `bool` return (approved/rejected) + exception (quit). The `auto_approve` parameter
stays in `_run_one_chapter()` — it still governs the `_prompt_choice` calls elsewhere in the
function.

**Resolution**: The mapping is clean. One subtlety: the current code default for empty input
is `or "n"` → reject. Under the callback, the `_prompt_user` function in Pass 4.3 explicitly
returns `choice == "y"` — an empty input returns `False` (reject). Behavior preserved.

---

### Decision 20
**Situation**: `run_session()` currently returns `None` at every exit point. The spec says to
return `SessionResult` at all exit points. Auditing `run_session()` finds:
- Line 492: `if not should_continue: return` — early return 1
- Lines 497–499: `if not _prompt_yes_no("Proceed?"...): return` — early return 2
- Post-loop fall-through after `log_event("session_complete", ...)` — normal return

The spec says "minimum 3 early-exit points plus the fall-through". This appears to overcount
— there are only 2 explicit early return statements in the current code. The
`except KeyboardInterrupt:` block becomes `raise KeyboardInterrupt` (not a return). The user-quit
`break` and keep-old-living-doc `break` inside the loop both fall through to the normal
post-loop code — they are not additional return statements.

**Action**: Add `SessionResult(...)` returns at the 2 early-exit points and at the post-loop
completion point. Do not create additional return points beyond what the code has.

**Why**: The Done condition is behavioral correctness, not return-count matching. The spec's "3
early exits" language is an overcount. Only 2 early returns exist.

**Resolution**: Spec prose mismatch vs. actual code structure. Follow the code, not the count.

---

## Pass 4.3 — novel_pipeline cli.py Update

### Decision 21
**Situation**: `cli.py` at line 47 has `--auto-approve` defined:
```
p.add_argument("--auto-approve", action="store_true", ...)
```
Confirmed present. The spec note "Do NOT add it again" is correct. No action on this flag.

Current `run_session()` call at lines 103–110 does not pass `approve_chapter`. After Pass 4.2,
`run_session()` has a default of `lambda n, t: True` for `approve_chapter` — so the existing
call still compiles. But Pass 4.3 requires wiring `_prompt_user` or the auto-approve lambda.

**Action**: Add `_prompt_user()` as defined in the spec (raises `KeyboardInterrupt` on `q`).
Build `approve_fn` conditionally on `args.auto_approve`. Add `approve_chapter=approve_fn` to
the `run_session()` call at line 103.

**Why**: The `q` → `raise KeyboardInterrupt` path in `_prompt_user` propagates through
`_run_one_chapter()` → `run_session()`'s `except KeyboardInterrupt` → which now does
`raise KeyboardInterrupt` → caught by `cli.py`'s own `except KeyboardInterrupt: return 1`.
The quit chain is intact.

**Resolution**: Clean wiring. Verify that after this pass, `--auto-approve` runs with zero
stdin reads.

---

## Pass 4.4 — Fiction Endpoint Wrapper

### Decision 22
**Situation**: `src/endpoints/fiction.py` does not exist. The spec offers two import paths:
1. Direct package import (`from novel_pipeline.session import ...`) — works if the venv has the
   package installed.
2. Fallback `sys.path.insert` to `src/fiction/pipeline/` — works regardless of venv state.

`src/fiction/pipeline/novel_pipeline.egg-info/` exists, indicating the package was installed
in development mode (`pip install -e .`). The direct package import should work with the venv
active.

**Action**: Try the direct import first. If import fails at verification time, switch to the
fallback path insert. Document whichever path was used.

**Why**: The egg-info presence strongly suggests the package is importable. The fallback is
provided precisely for environments where the venv is absent or the install is stale.

**Resolution**: Spec correctly provides both paths. Builder should test with the Done condition
import: `python -c "from src.endpoints.fiction import run_novel_session; print('ok')"`.

---

## Pass 4.5 — Fiction CLI Shim

### Decision 23
**Situation**: `src/cli/fiction.py` is new. The spec explicitly calls out that `_prompt_user()`
is intentionally duplicated between `cli/fiction.py` and `novel_pipeline/cli.py` — extraction
to `src/util/` is out of scope.

The flag set must mirror `novel_pipeline/cli.py` exactly: `--config` (required),
`--auto-approve`, `--dry-run`, `--resume`, `--chapter-start`, `--ignore-cost-limit`.

**Action**: Create `src/cli/fiction.py` with the argparse wrapper, `_prompt_user()` copy, and
the call to `run_novel_session()` from `src/endpoints/fiction.py`. Verify flag set matches.

**Why**: `src/cli/fiction.py` is the new stable entry point. The existing `novel_pipeline/cli.py`
is the old entry point that remains functional. Both are valid for the duration of the
refactor.

**Resolution**: Straightforward new file. The `src/cli/__init__.py` was already created in
Pass 2.5 — no second creation needed.

---

## Pass 5.1 — Remove Private Config Loaders

### Decision 24
**Situation**: Pre-condition: Pass 1.1 must be complete and all four files must use
`from config import load_config`. The 4-hit grep must pass before proceeding. This pass
is purely deletion — no functional change.

After Pass 1.1, the `_load_config()` definitions still exist (Pass 1.1 adds the import and
renames call sites, but does not delete the old definition). Pass 5.1 is the cleanup pass that
removes the dead definition bodies.

**Action**: Delete the `_load_config()` function bodies from all four files. No call-site
changes needed (those were done in Pass 1.1).

**Why**: The definitions are dead code after Pass 1.1. Keeping them until Pass 5.1 reduces
risk — if any call site was missed in Pass 1.1, the old definition still covers it. Pass 5.1
is the final confirmation.

**Resolution**: Verify the Done condition `grep -rn "_load_config" src/` returns empty.

---

## Pass 5.2 — Delete run_simple.py

### Decision 25
**Situation**: `src/fiction/run_simple.py` exists. A grep for `run_simple` across `src/` returns
no hits — the file is not imported anywhere. It is safe to delete.

The spec notes it uses `sys.exit()`, `input()`, and hardcoded global config — none need cleanup
before deletion since it is an orphaned prototype.

**Action**: Delete `src/fiction/run_simple.py`.

**Why**: Orphaned file confirmed by grep. No consumers.

**Resolution**: Straightforward. Run the grep pre-condition, then delete.

---

## Pass 5.3 — Shim run_chapter.py and run_book.py

### Decision 26
**Situation**: The spec is explicit: apply BOTH shims in the same pass. The reason is that
after shimming `run_chapter.py`, it no longer defines `run_llm`, `run_local`, `run_tts`.
`run_book.py` still has `import run_chapter as rc` (or the temporary re-import from Pass 2.3)
at the module level. If `run_chapter.py` is shimmed first and `run_book.py` still references it
via the old import, `run_book.py` breaks immediately.

Three pre-conditions must be verified before proceeding:
1. `src/cli/podcast.py` has `--book` flag.
2. `run_local`, `run_llm`, `run_tts` definitions are in `endpoints/podcast.py` (3 hits) and
   NOT in `run_chapter.py` (0 hits).
3. Passes 2.3, 2.4, 2.5 are complete.

**Action**: Verify all three pre-conditions. Then in a single edit session, replace the entire
body of `run_chapter.py` with `from cli.podcast import main; main()` AND replace the entire
body of `run_book.py` with `from cli.podcast import main; main()`. Both in the same change.

**Why**: The spec warns this explicitly: "If `run_chapter.py` is shimmed first alone, `run_book.py`
breaks at its `import run_chapter as rc` line." Atomic application avoids an intermediate
broken state.

**Resolution**: Follow spec strictly. Pre-condition verification is mandatory before shimming.

---

## Pass 5.4 — Update initial_readme.md

### Decision 27
**Situation**: `src/initial_readme.md` exists. The Entry Points section must list
`src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs and document `run_chapter.py`
and `run_book.py` as forwarding shims.

**Action**: Update the Entry Points section as specified. Done conditions are both grep checks
returning hits.

**Why**: Documentation must reflect the new CLI surface so users reach the correct entry points.

**Resolution**: Straightforward documentation update. No code impact.

---

## Cross-Phase Summary of Undocumented Gaps

| # | Gap | Affects |
|---|-----|---------|
| 1 | `run_chapter.py` (line 157) and `run_book.py` (line 97) each have one `_load_config()` call site not named in spec prose — caught by Done condition grep | Pass 1.1 |
| 2 | `tts/cli.py` exceptions import path not given (`podcast_script_generator.llm.exceptions`) | Pass 1.2 |
| 3 | 5th print in `send_to_api()` ("[done]") not named in spec but caught by Done condition grep | Pass 1.3 |
| 4 | `ROOT`/`SRC` path constants must be recomputed in `endpoints/podcast.py` after helper move | Pass 2.3 |
| 5 | `endpoints/podcast.py` needs its own `load_config` import (path insert + from config) | Pass 2.3 |
| 6 | Spec says "keep fiction-dir discovery in endpoint" but endpoint signature takes `str` — contradiction; discovery belongs in CLI wrapper | Pass 2.3 / 2.5 |
| 7 | `fiction_meta` mode eligibility in book mode not addressed — builder must decide | Pass 2.5 |
| 8 | Spec counts "minimum 3 early-exit returns" in `run_session()` but only 2 exist — do not add spurious returns | Pass 4.2 |
