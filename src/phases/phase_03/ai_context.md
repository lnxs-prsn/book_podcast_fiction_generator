# Phase 03 — AI Context

## Goal
Write the 4-person podcast prompt and complete the full Speaker 0-3 pipeline path:
LLM output → `_to_speaker_format()` → TTS with 4 configured voices.

## Architecture decisions

**Why single-shot prompt:**
`call_api.py` makes one API call — prompt + PDF text concatenated. The 4-person prompt
is a self-contained set of instructions the LLM executes in one shot.

**Speaker label → Speaker N: mapping (complete):**

| Label in LLM output | `_to_speaker_format()` output |
|---------------------|-------------------------------|
| HOST:               | Speaker 0:                    |
| EXPERT:             | Speaker 1:                    |
| GUEST:              | Speaker 1:                    |
| CRITIC:             | Speaker 2:  ← added Phase 03  |
| NEWCOMER:           | Speaker 3:  ← added Phase 03  |
| **H:**              | Speaker 0:                    |
| **E:**              | Speaker 1:                    |

**Voice assignment for 4-person:**
- Speaker 0 (HOST Alex):    en-Alice_woman
- Speaker 1 (EXPERT Jordan): en-Carter_man
- Speaker 2 (CRITIC Sam):   en-Maya_woman
- Speaker 3 (NEWCOMER Riley): en-Frank_man

Source: session docs in `src/docs/session_notes/audio_builder_session.md`.
All 4 are confirmed real WaveSpeed VibeVoice IDs.

**Why `run_tts()` is mode-aware (not the TTS layer):**
The TTS layer (`cli.py`) already supports 4 speakers via its `speakers` dict — it just
requires non-None values for any Speaker N it encounters in the script. The mode-to-voice
mapping lives in `run_chapter.py` because that is the entry point that knows the mode.

## Files touched

| File | Why |
|------|-----|
| `podcast_script_generator/llm/prompts/mode_4person.txt` | Wrote production 4-person prompt |
| `run_chapter.py` `_to_speaker_format()` | Added CRITIC → Speaker 2, NEWCOMER → Speaker 3 |
| `run_chapter.py` `run_tts()` | Added mode param, 4-voice dict for 4person mode |
| `run_chapter.py` `main()` | Passes args.mode to run_tts() |

## What to check first if something breaks

1. **Speaker N: not appearing in TTS input:** check `_to_speaker_format()` regex — CRITIC/NEWCOMER labels must have no trailing space before the colon in LLM output.
2. **TTS ValueError "no voice configured for speaker_3":** check `run_tts()` mode arg — `main()` must pass `args.mode`, not a hardcoded string.
3. **Wrong voice for CRITIC/NEWCOMER:** voice IDs are in `run_tts()` dict — `"en-Maya_woman"` for speaker_3, `"en-Frank_man"` for speaker_4.
4. **4-person prompt not found:** check `PROMPTS_DIR` in `read_prompt.py` and that `prompts/mode_4person.txt` exists in the llm directory.
