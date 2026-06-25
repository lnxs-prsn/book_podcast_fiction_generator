# Phase 01 — Fix broken integration path

## Pass 1 — Correct import path in run_chapter.py

**Commit:** Fix `run_chapter.py` import path: `podcast/llm` → `podcast_script_generator/llm`

**Changed:**
- `src/run_chapter.py` lines 64 and 68: `SRC / "podcast" / "llm"` corrected to `SRC / "podcast_script_generator" / "llm"` in `run_llm()`

**Smoke-test result:**
- Import resolution confirmed via venv python: all three imports (`extract_pdf`, `read_prompt`, `call_api`) and `prompt.txt` path resolved without error.
- Full dry-run with `--llm --skip-audio` got past the import stage and halted only on missing `OPENROUTER_API_KEY` — correct behavior.

**May have broken / misaligned:**
- Nothing: this was a typo fix. No logic changed. The old path `src/podcast/llm/` never existed, so no code depended on it.
