# Phase 02 — AI Context

## Goal
Build mode-switching plumbing without writing new mode prompts. After this phase,
`run_chapter.py --llm --mode <mode>` selects a prompt file; everything else flows
through the existing pipeline unchanged.

## Architecture decisions

**Why keep `parse_args()` return type unchanged:**
`main.py` unpacks `pdf_path, prompt_path, output_dir = parse_args()`. Rather than
touch `main.py` (which the spec forbids for Pass 2), `parse_args()` still returns
the same 3-tuple but now derives `prompt_path` internally from `--mode`.

**Where mode resolution lives:**
`resolve_prompt_path(mode)` lives in `read_prompt.py` alongside `read_prompt()`.
`parse_args.py` imports it. `run_chapter.py` also imports it directly (bypasses
`parse_args` entirely since it doesn't use `main.py`'s CLI).

**prompt.txt:**
Still exists on disk — orphaned after Pass 3 but harmless. Can be deleted in a
future cleanup. Do not reference it in any new code.

## Files touched

| File | Why |
|------|-----|
| `podcast_script_generator/llm/prompts/mode_2person.txt` | Original prompt content |
| `podcast_script_generator/llm/prompts/mode_4person.txt` | Placeholder stub |
| `podcast_script_generator/llm/prompts/mode_code.txt` | Placeholder stub |
| `podcast_script_generator/llm/prompts/mode_realworld.txt` | Placeholder stub |
| `podcast_script_generator/llm/prompts/mode_fiction_meta.txt` | Placeholder stub |
| `podcast_script_generator/llm/read_prompt.py` | Added PROMPTS_DIR, VALID_MODES, resolve_prompt_path() |
| `podcast_script_generator/llm/parse_args.py` | Rewrote to use argparse + --mode |
| `run_chapter.py` | Added --mode flag, wired through run_llm(mode) |

## What to check first if something breaks

1. **Wrong mode file resolved:** check `PROMPTS_DIR` in `read_prompt.py` — must be `Path(__file__).parent / "prompts"`.
2. **parse_args returns wrong tuple:** verify it still returns `(pdf_path, prompt_path, output_dir)` in that order.
3. **run_chapter.py ignores mode:** verify `run_llm()` signature is `run_llm(pdf_path, mode)` and `main()` passes `args.mode`.
4. **Stub file triggers empty-content error:** `read_prompt()` raises `ValueError` on empty content — the stubs have non-empty placeholder text to prevent this.
