# Phase 02 — Podcast mode selection architecture

## Pass 1 — Split prompt into per-mode files

**Commit:** Phase 02 Pass 1: create prompts/ dir with mode_2person.txt and stubs

**Changed:**
- Created `src/podcast_script_generator/llm/prompts/`
- Copied `prompt.txt` → `prompts/mode_2person.txt` (14,415 chars, original content preserved)
- Added placeholder stubs: `mode_4person.txt`, `mode_code.txt`, `mode_realworld.txt`, `mode_fiction_meta.txt`
- `prompt.txt` kept in place (run_chapter.py:68 referenced it until Pass 3)

**Smoke-test result:** run_chapter.py import path still resolved; reached API key check as expected.

**May have broken / misaligned:** Nothing. Only additions. Old prompt.txt untouched.

---

## Pass 2 — Add --mode flag to the script generator

**Commit:** Phase 02 Pass 2: add --mode flag to parse_args, resolve_prompt_path to read_prompt

**Changed:**
- `read_prompt.py`: added `PROMPTS_DIR`, `VALID_MODES`, `resolve_prompt_path(mode)`. Existing `read_prompt(path)` function unchanged.
- `parse_args.py`: rewrote from 3-positional-arg sys.argv parsing to argparse with 2 positional args (`pdf_path`, `output_dir`) and `--mode` flag. Return type `(pdf_path, prompt_path, output_dir)` preserved — `main.py` untouched.

**Verified:**
- `resolve_prompt_path` resolves all 5 modes correctly, raises `ValueError` on unknown mode.
- `parse_args()` with default argv resolves to `mode_2person.txt`.
- `parse_args()` with `--mode code` resolves to `mode_code.txt`.
- `run_chapter.py` smoke-test still reaches API key check.

**May have broken / misaligned:**
- `main.py`'s CLI interface changed (old 3-positional args now invalid). Anyone calling `python main.py pdf prompt outdir` directly must update to `python main.py pdf outdir [--mode MODE]`. `run_chapter.py` never used this CLI, so unaffected.

---

## Pass 3 — Wire mode through run_chapter.py

**Commit:** Phase 02 Pass 3: wire --mode flag through run_chapter.py

**Changed:**
- `run_chapter.py` `run_llm()`: added `mode: str = "2person"` parameter, replaced hardcoded `prompt.txt` path with `resolve_prompt_path(mode)`.
- `run_chapter.py` `main()`: added `--mode` argparse flag with all 5 choices; passes `args.mode` to `run_llm()`; prints `Mode: <mode>` when `--llm` is active.

**Verified:**
- Default (no --mode): reaches API key check with `Mode: 2person` printed.
- `--mode code`: reaches API key check with `Mode: code` printed.
- `--mode badmode`: rejected by argparse with usage error before any code runs.

**May have broken / misaligned:**
- `prompt.txt` is now orphaned (still exists on disk but nothing references it). Safe to delete in a future cleanup pass.
- `run_local()` ignores `--mode` (by design). Mode is LLM-only.
