# Phase 07 — Batch whole-book runner

## Pass 1 — Build the basic batch runner

**Commit:** Phase 07 Pass 1+2+3: batch runner — run_book.py with skip-existing, --force, and summary

**Changed:**
- `src/run_book.py` (new file) — full batch runner implemented in one pass:
  - Reads all PDFs from `data/chapters/` sorted by leading numeric prefix
  - Imports `run_chapter` directly and calls `run_llm()` / `run_local()` / `run_tts()`
  - Catches `(Exception, SystemExit)` so inner `sys.exit()` calls (e.g. missing pypdf) don't abort the whole batch
  - Accepts `--llm`, `--skip-audio`, `--mode`, `--context`, `--context-file` flags; passes them through
  - Prints `[ok]`, `[skip]`, or `[fail]` per chapter

**Verified:**
- `python src/run_book.py --help` shows all flags correctly ✓
- Import + `_sorted_pdfs([01, 09, 10, 100])` returns correct numeric order ✓
- `--mode realworld` without `--context` exits with clear error ✓

---

## Pass 2 — Skip-existing / resume logic

**Changed:**
- `src/run_book.py` — same file as Pass 1; skip/force logic is part of the same implementation:
  - Before processing: checks `data/output/scripts/<stem>_podcast.txt` exists
  - If exists and `--force` not set: prints `[skip]` and continues
  - `--force` flag bypasses the check

**Verified:**
- Without `--force`: ch01 and ch05 (already have scripts) printed `[skip]`, total skipped=2 ✓
- With `--force`: ch01 and ch05 showed `[fail]` (attempted, failed due to missing pypdf) — skip correctly bypassed ✓

---

## Pass 3 — Progress reporting and error summary

**Changed:**
- `src/run_book.py` — same file; tracking and summary logic included from the start:
  - Tracks `ok`, `skipped`, `failed` lists across the loop
  - Prints summary table at end: `total=N  ok=N  skipped=N  failed=N`
  - Lists failed chapters with their error message
  - Writes summary to `data/output/run_summary.txt`

**Verified:**
- Summary table printed at end of run ✓
- `data/output/run_summary.txt` written and contains summary + failed list ✓
- `run_summary.txt` goes to `data/output/` (alongside scripts/audio output) ✓

**May have broken / misaligned:**
- Nothing. `run_book.py` is a new file; all existing paths untouched.
- `run_chapter.py` is imported but not modified — all existing `run_chapter.py` behaviour preserved.
- `data/output/run_summary.txt` is a new output file; no prior output depends on it.
