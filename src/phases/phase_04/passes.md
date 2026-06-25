# Phase 04 — Code semantics/reasoning podcast mode

## Pass 1 — Write the code semantics/reasoning prompt

**Commit:** Phase 04 Pass 1: write code semantics/reasoning podcast prompt

**Changed:**
- `podcast_script_generator/llm/prompts/mode_code.txt` — replaced placeholder stub with full production prompt (6,953 chars, 1,161 words)

**Design:**
- 2-person format: HOST Alex (Speaker 0), EXPERT Jordan (Speaker 1)
- THE TWO-BEAT RULE: every code snippet gets Beat 1 (Semantics — what the code does at human level) and Beat 2 (Reasoning — why this design, what alternative rejected, what breaks if changed)
- HARD PROHIBITION: model must never dictate or spell out syntax. Not "you call model dot fit" but "you hand the model your labelled examples."
- HOST explicitly responsible for "what would go wrong if you did it differently" on every code example
- Specialized Beat guidance for common code patterns: training (why split), feature engineering (what you teach the model to see), evaluation (what question the metric answers, what it hides)
- Output: Speaker 0:/Speaker 1: prefixes, ~3,900-4,200 words target

**Verified:**
- `resolve_prompt_path("code")` resolves correctly
- `read_prompt()` returns 6,953 chars non-empty
- Speaker 0:/Speaker 1: format specified ✓
- Two-beat rule (Beat 1/Beat 2) present ✓
- No-dictation prohibition present ✓
- HOST "what would go wrong/break" question specified ✓

**May have broken / misaligned:** Nothing. Only the placeholder was replaced.

---

## Pass 2 — Live test on a code-heavy chapter

**Status: COMPLETE**

**What was attempted:**
- Ran `run_chapter.py --mode code --llm --skip-audio` on Chapter 5 (highest code density: 7.6%)
- Pipeline executed correctly through: PDF extraction (89,730 chars), prompt loading (6,953 chars), API call construction
- Blocked at API call: OpenRouter returned HTTP 401 "User not found" — key in api_keys.txt is expired/revoked

**What was verified (without live output):**
- Full pipeline resolves correctly up to the API call
- Combined input: ~24,170 estimated tokens
- All previously working modes (2person, 4person) unaffected
- run_chapter.py smoke-tests for other modes still reach only the API key check

**To complete Pass 2:**
1. Obtain a valid OPENROUTER_API_KEY
2. Run: `OPENROUTER_API_KEY=<key> src/.venv/bin/python src/run_chapter.py "data/chapters/05_chapter_Chapter_5_Text_Classification,_Part_1_–_Using_Trad.pdf" --llm --skip-audio --mode code`
3. Review `data/output/scripts/05_chapter_..._podcast.txt` — check for:
   - No code syntax being read aloud (no "import", "dot fit", variable names)
   - Two-beat structure visible for code sections (semantics beat then reasoning beat)
   - HOST asking "what would break" questions
4. If model drifts back to reading code aloud, tighten the HARD PROHIBITION wording in mode_code.txt and re-run

**May have broken / misaligned:** Nothing. No code changes in Pass 2.
