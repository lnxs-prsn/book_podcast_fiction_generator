# Phase 04 — AI Context

## Goal
Write a prompt that makes the LLM discuss code as a record of decisions rather than
a sequence of syntax. Every code snippet gets two beats: what it does (Semantics) and
why it was written that way (Reasoning). The listener never hears code read aloud.

## Core design decision — the Two-Beat Rule

The two-beat rule is the defining structure of this mode. It forces the LLM to:
1. Translate code into human consequence (Semantics)
2. Surface the decision behind the design (Reasoning)

Without the two-beat rule, LLMs default to walking through code line by line
(dictation), which is useless in audio format.

The HARD PROHIBITION section reinforces this from the negative direction — it names
exactly what is forbidden with concrete examples of forbidden phrasing.

## Files touched

| File | Why |
|------|-----|
| `podcast_script_generator/llm/prompts/mode_code.txt` | Full production prompt, replaced placeholder |

## Pass 2 pending

Pass 2 requires live LLM output to check for prompt compliance. The API key in
api_keys.txt expired (HTTP 401). The pipeline is fully wired — no code changes needed.

**What to check if LLM drifts back to code dictation:**
- Strengthen the HARD PROHIBITION with more concrete forbidden examples
- Add a "CHECK BEFORE SUBMITTING" section at the end of the prompt instructing the LLM to scan its own output for forbidden patterns before outputting
- Reduce MAX_TOKENS pressure — GLM-4.5-air at 4096 tokens may be cutting off at ~3,000 words and rushing to finish, which causes the model to revert to efficient (but forbidden) syntax-reading

## What to check first if something breaks

1. **mode_code.txt not found:** check PROMPTS_DIR in read_prompt.py
2. **LLM reads code aloud:** tighten HARD PROHIBITION, add self-check instruction
3. **Output too short:** MAX_TOKENS=4096 in call_api.py may need increasing for code-heavy chapters (more content per PDF page)
4. **Two-beat structure absent:** add explicit section markers like "Beat 1 for [concept]:" to prompt structure guidance
