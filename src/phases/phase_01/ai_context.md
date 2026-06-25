# Phase 01 — AI Context

## Goal
Fix the broken LLM integration path so `run_chapter.py --llm` can reach the script generator without an ImportError.

## Root cause
`run_llm()` in `src/run_chapter.py` used `SRC / "podcast" / "llm"` as both the `sys.path` insertion and the `prompt.txt` base path. The actual directory is `src/podcast_script_generator/llm/`. The subdirectory `src/podcast/` does not exist.

## Files touched

| File | Why |
|------|-----|
| `src/run_chapter.py` | Two path strings on lines 64 and 68 corrected from `"podcast"` to `"podcast_script_generator"` |

## Key decisions
- Only the path strings changed; no imports, no logic, no signatures altered.
- Verified with `src/.venv/bin/python` because `fitz` (pymupdf) lives in the project venv, not system Python.

## What to check first if something breaks
1. Confirm `src/podcast_script_generator/llm/` exists and contains `call_api.py`, `extract_pdf.py`, `read_prompt.py`, `prompt.txt`.
2. Re-run the import smoke-test: `src/.venv/bin/python -c "import sys; sys.path.insert(0,'src/podcast_script_generator/llm'); from extract_pdf import extract_pdf; from read_prompt import read_prompt; from call_api import call_api; print('ok')"`.
3. A real end-to-end run still requires `OPENROUTER_API_KEY` in env — that is not a bug.
