# Phase 07 AI Context — Batch whole-book runner

## Goal
Single entry point that processes all chapter PDFs end-to-end without manual intervention.

## Files introduced
- `src/run_book.py` — the entire phase lives here

## Files relied on (not modified)
- `src/run_chapter.py` — imported directly; `run_llm()`, `run_local()`, `run_tts()` called per chapter
- `data/chapters/` — scanned for `*.pdf`; filenames are expected to start with a numeric prefix
- `data/output/scripts/` — checked for existing `<stem>_podcast.txt` to determine skip/reprocess
- `data/output/run_summary.txt` — written after every run

## Key design decisions

**Import, not subprocess.** `run_book.py` does `sys.path.insert(0, str(SRC)); import run_chapter as rc`
and calls `rc.run_llm()` / `rc.run_local()` / `rc.run_tts()` directly. This avoids subprocess
overhead and keeps all Python state in one process.

**Catch `(Exception, SystemExit)`.** The local generator (`decide_later/local/podcast_generator.py`)
calls `sys.exit(1)` when pypdf is missing. `SystemExit` is a `BaseException`, not an `Exception`,
so a plain `except Exception` would let it kill the whole batch. Both are caught and recorded as
`[fail]` entries.

**Numeric sort.** `_sorted_pdfs()` extracts the leading integer from each PDF stem for sort order.
Non-numeric stems sort last (sort key = `float("inf")`).

**fiction_meta excluded.** The spec excludes `fiction_meta` from the batch mode choices because it
requires a per-chapter `--fiction-dir`. `realworld` is included — a single event context can apply
to all chapters in one batch run.

## What to check first if something breaks
1. Wrong order: check `_sorted_pdfs()` sort_key — leading digits, not lexicographic
2. All chapters `[fail]` unexpectedly: check that `sys.path.insert(0, str(SRC))` happens before
   `import run_chapter` and that the import succeeds
3. Summary not written: check that `data/output/` exists (created via `mkdir parents=True`)
4. `[skip]` not firing: verify the `SCRIPTS_OUT` path matches what `run_chapter.py` writes
   (`SCRIPTS_OUT / f"{pdf_path.stem}_podcast.txt"` — same formula in both files)
