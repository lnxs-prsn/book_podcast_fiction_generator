# Phase 05 — AI Context

## Goal

Add real-world context podcast mode. A user-provided current event (news, CVE, launch, incident) is injected into the prompt as `{CURRENT_EVENT}`. The event is the hook; the chapter content is the explanatory lens. 2-person format, Speaker 0/1 output.

## Files touched

| File | Why |
|------|-----|
| `prompts/mode_realworld.txt` | Pass 1+2: replaced placeholder stub with header docs + full prompt |
| `read_prompt.py` | Pass 3: added `context` param; substitutes `{CURRENT_EVENT}` when provided |
| `parse_args.py` (llm module) | Pass 3: added `--context` / `--context-file` flags; returns 4-tuple; validates realworld mode |
| `main.py` (llm module) | Pass 3: unpacks 4-tuple from parse_args; passes context to read_prompt |
| `run_chapter.py` | Pass 3: added `--context` / `--context-file` flags to main(); passes context to run_llm() |

## Key decisions

- `{CURRENT_EVENT}` substitution happens in `read_prompt.py`, not in `call_api.py` or the runner — keeps the substitution colocated with prompt loading.
- `run_llm()` gains a `context: str | None = None` parameter — existing callers without context work unchanged.
- Guard for missing context when mode=realworld lives in both `run_chapter.py` (user-facing runner) and `parse_args.py` (standalone llm module entry point).
- `--context-file` content is read and stripped; `--context` inline value is used as-is.

## Known pre-existing issue

`test_all.py` was already broken before Phase 5: its module-level `parse_args` test calls argparse with 3 positional args against a 2-positional parser, causing `sys.exit(2)` and aborting the entire test file. Phase 5 does not fix this (out of scope).

## What to check first if something breaks

- `{CURRENT_EVENT}` not substituted: check that `context` is being passed through `run_llm()` → `read_prompt()` chain
- realworld mode without context passes silently: check the guard in `run_chapter.py` main() and in `parse_args.py`
- Other modes broken: check that `context=None` default is preserved in `read_prompt()` — substitution only fires when `context is not None`
