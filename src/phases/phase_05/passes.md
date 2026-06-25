# Phase 05 — Real-world context podcast mode

## Pass 1 — Design the context injection interface

**Commit:** Phase 05 Pass 1+2: document context interface and write realworld prompt

**Changed:**
- `podcast_script_generator/llm/prompts/mode_realworld.txt` — replaced placeholder stub with:
  1. Header comment block documenting the `--context` / `--context-file` interface and design rationale
  2. Full production prompt (realworld mode) including `{CURRENT_EVENT}` placeholder

**Design decisions recorded in header:**
- `--context "..."` for short inline text (headline, sentence, one-paragraph summary)
- `--context-file path.txt` for longer documents (CVE advisories, press releases, articles)
- Both map to the same substitution: value replaces `{CURRENT_EVENT}` verbatim
- If `--mode realworld` and neither flag provided, runner exits with error (wired in Pass 3)

**Verified:**
- File is non-empty and non-placeholder ✓
- `{CURRENT_EVENT}` placeholder present ✓
- Header documents both `--context` and `--context-file` interfaces ✓
- 2-person HOST/EXPERT format specified ✓
- Speaker 0: / Speaker 1: output format specified ✓
- Cold open anchored to current event ✓
- Chapter content used as explanatory lens ✓
- `resolve_prompt_path("realworld")` resolves correctly (file exists) ✓

**May have broken / misaligned:** Nothing. Only the placeholder stub was replaced.

---

## Pass 2 — Write the real-world context prompt

See Pass 1 above — both passes were completed in a single file write since Pass 1's header and Pass 2's prompt body are in the same file.

---

## Pass 3 — Add --context / --context-file to CLI and wire substitution

**Commit:** Phase 05 Pass 3: wire --context/--context-file and {CURRENT_EVENT} substitution

**Changed:**
- `podcast_script_generator/llm/read_prompt.py` — added `context: str | None = None` param; substitutes `{CURRENT_EVENT}` when context is provided
- `podcast_script_generator/llm/parse_args.py` — added `--context` / `--context-file` flags; returns 4-tuple `(pdf_path, prompt_path, output_dir, context)`; validates realworld mode requires context
- `podcast_script_generator/llm/main.py` — unpacks 4-tuple; passes context to `read_prompt()`
- `run_chapter.py` — added `--context` / `--context-file` flags; guard: realworld without context exits with clear error; passes context through `run_llm()`
- `prompts/mode_realworld.txt` — fixed header comments: changed `{CURRENT_EVENT}` in documentation to `{{ CURRENT_EVENT }}` so only the body placeholder gets substituted

**Verified (all PASS):**
- `read_prompt()` substitutes `{CURRENT_EVENT}` exactly once (in body, not header comments) ✓
- `read_prompt()` with `context=None` leaves `{CURRENT_EVENT}` placeholder untouched ✓
- All 5 modes resolve to existing prompt files ✓
- `2person`, `4person`, `code` modes still reach API call (no regression) ✓
- `realworld` without `--context` or `--context-file` → "requires --context or --context-file" error, exit 1 ✓
- `realworld --context "..."` reaches API call (fails only on missing OPENROUTER_API_KEY) ✓
- `realworld --context-file path.txt` reaches API call (fails only on missing key) ✓

**May have broken / misaligned:**
- `parse_args()` now returns 4-tuple; `main.py` updated accordingly. Old callers that unpacked 3 values would break — no such callers remain.
- `test_all.py` was already broken before Phase 5 (parse_args module-level code calls argparse which exits on the old 3-positional test argv). Phase 5 does not fix this.
