# Phase 03 — 4-person podcast format

## Pass 1 — Write the 4-person prompt

**Commit:** Phase 03 Pass 1: write 4-person podcast prompt

**Changed:**
- `podcast_script_generator/llm/prompts/mode_4person.txt` — replaced placeholder stub with full production prompt (6,355 chars)

**Design:**
- 4 speakers: HOST Alex (Speaker 0), EXPERT Jordan (Speaker 1), CRITIC Sam (Speaker 2), NEWCOMER Riley (Speaker 3)
- Defines roles, interaction rules (no voice speaks 4+ consecutive lines), audio constraints, structure (~30 min, 3,900-4,200 words), output format (Speaker N: prefixes), SHOW NOTE convention
- Single-shot design to match call_api.py's one-call model
- Section headers use ** for readability in the prompt body — these are instructions, not output; the prompt explicitly prohibits markdown in LLM output

**Verified:**
- `resolve_prompt_path("4person")` resolves correctly
- `read_prompt()` returns non-empty content (6,355 chars)
- All 4 `Speaker N:` prefixes mentioned in output format section

**May have broken / misaligned:** Nothing. Only the placeholder was replaced.

---

## Pass 2 — Update _to_speaker_format() for 4-person output and wire 4 voices

**Commit:** Phase 03 Pass 2: extend speaker label map and wire 4 voices to TTS

**Changed:**
- `run_chapter.py` `_to_speaker_format()`: added `CRITIC:` → `Speaker 2:` and `NEWCOMER:` → `Speaker 3:` substitutions. Legacy labels (HOST, GUEST, EXPERT, **H:**, **E:**) unchanged.
- `run_chapter.py` `run_tts()`: added `mode` parameter (default `"2person"`). When mode is `"4person"`, passes `en-Maya_woman` (speaker_3) and `en-Frank_man` (speaker_4); otherwise passes `None` for both (unchanged 2-person behaviour).
- `run_chapter.py` `main()`: passes `args.mode` to `run_tts()`.

**Voices for 4-person:** en-Alice_woman (HOST), en-Carter_man (EXPERT), en-Maya_woman (CRITIC), en-Frank_man (NEWCOMER). All confirmed real WaveSpeed voice IDs from session docs.

**Verified:**
1. `_to_speaker_format()` converts HOST→Speaker 0, EXPERT/GUEST→Speaker 1, CRITIC→Speaker 2, NEWCOMER→Speaker 3, **H:**→Speaker 0, **E:**→Speaker 1. All 7 label forms confirmed.
2. `build_api_payload()` accepts 4-voice dict without error; raises ValueError for 2-person dict when script contains Speaker 2/3 (correct protective behaviour).
3. `run_chapter.py --mode 4person --llm --skip-audio` reaches only OPENROUTER_API_KEY error — all config, imports, and voice resolution are correct.

**May have broken / misaligned:**
- 2-person scripts processed through `_to_speaker_format()` are unaffected (CRITIC/NEWCOMER labels simply never appear in 2-person output).
- `run_tts()` signature changed (added `mode`); only caller is `main()` in the same file, already updated.
