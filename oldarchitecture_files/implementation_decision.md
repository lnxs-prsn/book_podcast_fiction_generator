# Implementation Decisions — Build Specs v10

> This document records design/implementation choices the implementing agent had to make because `build_specsv10.md` was silent, ambiguous, or left multiple valid options.

---

## 1. Documentation location: root `initial_readme.md` vs. `src/initial_readme.md`

**Spec instruction (Pass 7.4):**

> `| src/initial_readme.md | modify — update Entry Points section |`

**Decision:** The update was applied to the project-root `initial_readme.md`; `src/initial_readme.md` was never created.

**Why:** The root directory already contained an `initial_readme.md` that served as the project-level README. The implementing agent appears to have treated it as the natural target rather than creating a duplicate inside `src/`. The content is correct, but the spec's file path is not satisfied.

**Trade-off:** Correct content, wrong location. Future readers looking at `src/initial_readme.md` will not find the updated instructions.

---

## 2. `parse_args.py` and `test_all.py` were left unchanged

**Spec instruction:** Pass 1.2 modified `main.py`, `tts/cli.py`, and `run_chapter.py`. Pass 1.3 modified `call_api.py`, `save_output.py`, `tts/cli.py`, `run_chapter.py`, and `run_book.py`. Neither pass listed `parse_args.py` or `test_all.py`.

**Decision:** These two files retained their original `print(...)` and `sys.exit(1)` calls.

**Why:** They were outside the explicit file list, so the agent did not touch them. However, the spec's done-conditions use broad `grep` commands over `src/podcast_script_generator/`, so the conditions fail.

**Trade-off:** Minimal, safe edits, but the pass-level invariants are not met. A follow-up should either (a) refactor these files or (b) narrow the done-condition to exclude legacy test/standalone scripts.

---

## 3. Validation order in `generate_chapter_podcast`

**Spec body (Pass 4.1):**

```python
pdf_path = Path(pdf_path).resolve()
if not pdf_path.exists():
    return PodcastResult(error=FileNotFoundError(...))

if mode == "realworld" and not context:
    return PodcastResult(error=ValueError(...))
```

**Decision:** Implemented exactly as shown: PDF existence check first, then mode-specific validation.

**Consequence:** The Phase 8.1 smoke test that calls `generate_chapter_podcast(Path('/nonexistent/file.pdf'), mode='fiction_meta')` expects an error containing `'fiction_dir'`. Because the nonexistent PDF is caught first, the returned error is `FileNotFoundError`. This is arguably more correct behavior, but it fails the spec's own test.

**Trade-off:** Earlier, cheaper validation for missing files, but divergence from the literal verification script.

---

## 4. Chapter sorting in `generate_book_podcast`

**Spec instruction (Pass 4.2):**

> 7. Sort PDFs numerically; for each, call `generate_chapter_podcast(...)` ...

**Decision:** Implemented as `sorted(resolve_dir.glob("*.pdf"), key=lambda p: p.stem)`.

**Why:** The spec said "numerically" but did not specify the exact key. The agent chose alphabetical sorting by stem, which works for zero-padded filenames (`01_`, `02_`, ..., `10_`) but not for raw numbers (`1_`, `2_`, `10_`).

**Trade-off:** Simple implementation, but not strictly numeric. For most real inputs the result is identical; for un-padded names the order will be wrong.

---

## 5. Missing `toc_page` error scope

**Spec rule (Pass 4.2):**

> 2. If `toc_page is None`: load from `config.json`; if still `None`, raise `ValueError`.

**Decision:** The implementation only raises `ValueError` when `book_pdf is not None` and `toc_page` remains `None`.

**Why:** If no `book_pdf` is provided, the splitter is never invoked and `toc_page` is irrelevant. The agent interpreted the rule as "required when splitting" rather than unconditionally required.

**Trade-off:** More lenient API, but stricter callers that pass neither may be surprised the function does not raise.

---

## 6. `slice_only` behavior when no `book_pdf` is supplied

**Spec rule (Pass 4.2):**

> 5. If `slice_only`, return `[PodcastResult()]` after splitting.

**Decision:** The implementation returns `[PodcastResult()]` whenever `slice_only=True`, even if `book_pdf is None` (i.e., no splitting actually occurred).

**Why:** The function treats `slice_only` as a short-circuit return flag independent of whether a split happened.

**Trade-off:** Consistent return type, but potentially misleading: the caller receives a success result for a no-op.

---

## 7. Type annotation for `splitter_engine`

**Spec signature (Pass 4.2):**

```python
splitter_engine: SplitterEngine | None = None,
```

**Decision:** Implemented as `splitter_engine=None` with no type annotation.

**Why:** Unknown; likely an oversight. The runtime behavior is identical because the factory returns a `SplitterEngine` anyway.

**Trade-off:** Loses static-typing clarity but no runtime impact.

---

## 8. Exception handling in `src/cli/fiction.py`

**Spec body (Pass 6.5):** Provides the guard, parser, `approve_fn`, and a call to `run_novel_session()` with a print on completion.

**Decision:** The CLI wraps the call in `try/except KeyboardInterrupt` and `except Exception`, printing to stderr and exiting with code 1.

**Why:** The spec did not define boundary error handling. The agent added defensive handling so the CLI exits cleanly instead of dumping a traceback.

**Trade-off:** Better user experience, but the exit-code mapping was invented here (not specified in the spec).

---

## 9. `@runtime_checkable` on protocols

**Spec body (Pass 3.1):** Protocol definitions without decorators.

**Decision:** Added `@runtime_checkable` to `ScriptEngine`, `AudioEngine`, and `SplitterEngine`.

**Why:** This allows `isinstance(engine, ScriptEngine)` checks, which can be useful for factories and tests.

**Trade-off:** Harmless addition; the spec's import tests still pass.

---

## 10. Default `approve_chapter` behavior in `run_session()` vs. `run_novel_session()`

**Spec instruction (Pass 6.2):**

> Add `approve_chapter: ApproveChapterFn = lambda n, text: True` to `run_session()`.

**Decision:** Implemented exactly. Additionally, `run_novel_session()` defaults `approve_chapter` to `None` and then replaces it with `lambda n, t: True`.

**Why:** The endpoint wrapper wanted a clean public signature where callers can omit the callback entirely.

**Trade-off:** Slight duplication of the default, but clear separation of concerns.

---

## 11. `SessionResult.completed` semantics

**Spec instruction (Pass 6.2):** Return `SessionResult(..., completed=True, ...)` at the normal post-loop fall-through.

**Decision:** The post-loop return always sets `completed=True`, even if zero chapters were written.

**Why:** The spec defined `completed` as a boolean for the normal exit path, not a count-derived predicate. The agent followed that literally.

**Trade-off:** A session that exits normally without writing any chapters reports `completed=True`. Callers must check `chapters_written` for real progress.

---

## 12. `normalize_speakers` implementation expanded beyond the spec

**Spec instruction (Pass 2.1):** Extract `_to_speaker_format()` from `run_chapter.py` and rename to `normalize_speakers`.

**Decision:** `src/util/normalize.py` contains a more elaborate normalizer than the original helper, handling markdown-bold labels, timestamp markers, named experts, HOST/GUEST/CRITIC/NEWCOMER aliases, and merging of standalone label lines.

**Why:** This appears to be a behavioral bug-fix carried over from earlier work (the `src/phases/phase_07/bugfix_speaker_normalisation.md` file exists). The spec did not prescribe the exact algorithm.

**Trade-off:** Better TTS output, but the function does more than the spec's minimal description.

---

## 13. No validation that `--book` and positional `pdf` are mutually exclusive

**Spec instruction:** Not explicitly discussed.

**Decision:** `src/cli/podcast.py` checks `if args.book:` first; if false, it requires `args.pdf`. If both are provided, `--book` wins and the positional `pdf` is silently ignored.

**Why:** Simple routing logic.

**Trade-off:** User error (providing both) is not surfaced. A clearer behavior would be to error when both are given.

---

## 14. `tts/cli.py` exception remapping details

**Spec instruction (Pass 1.2):** Delete local `AuthError`; remap `AuthError`, `RuntimeError`, and `ConnectionError` to `TTSSubmissionError`/`TTSTimeoutError`; catch `(PodcastError, ValueError, OSError)`.

**Decision:** Implemented a more nuanced remap inside `send_to_api()`: inspect the lower-cased error message for auth/connection keywords and raise the appropriate typed exception.

**Why:** The original exceptions are not always raised as Python types by the `wavespeed` client; message inspection is more robust.

**Trade-off:** Slightly more complex than the spec's literal mapping, but catches real-world error shapes better.

