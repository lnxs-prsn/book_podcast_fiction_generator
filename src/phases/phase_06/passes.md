# Phase 06 — Fiction meta-commentary podcast mode

## Pass 1 — Design the fiction input interface

**Commit:** Phase 06 Pass 1+2+3: fiction_meta mode — --fiction-dir flag, prompt, and injection

**Changed:**
- `src/run_chapter.py` — added `--fiction-dir` CLI flag with help text documenting the chapter-number matching logic (leading digits from PDF stem → `chapter_NN.md` in fiction dir)

**Verified:**
- `python run_chapter.py --help` shows `--fiction-dir` flag with description ✓
- Flag parses to `args.fiction_dir` ✓

**May have broken / misaligned:** Nothing. Flag is additive and defaults to None.

---

## Pass 2 — Write the fiction meta-commentary prompt

**Changed:**
- `podcast_script_generator/llm/prompts/mode_fiction_meta.txt` — replaced placeholder stub with:
  1. Header comment block documenting both placeholders and the `--fiction-dir` interface
  2. Full production prompt: HOST Alex and EXPERT Jordan examine the technical-to-fiction translation

**Prompt structure:**
- Cold open: the central tension of two documents about the same thing
- What translated intact (5 min): fidelity analysis with specific quotes
- What was abstracted into metaphor (7 min): precision vs. feeling tradeoffs
- Where the fiction had to simplify or distort (6 min): hardest cases
- What the fiction could do that the text could not (4 min): emotional register
- Closing (2 min): earned comparison insight

**Design decisions recorded in header:**
- `{TECHNICAL_CONTENT}` substituted from extracted PDF text by `run_llm()`
- `{FICTION_CONTENT}` substituted from the loaded fiction chapter file by `read_prompt()`
- Both are embedded in the prompt body; `call_api` is called with empty `pdf_text` for this mode
- `--fiction-dir <path>`: runner extracts leading number from PDF stem, finds `chapter_NN.md`

**Verified:**
- File is non-empty and non-placeholder ✓
- Both `{TECHNICAL_CONTENT}` and `{FICTION_CONTENT}` placeholders present in body ✓
- Header documents both placeholders and `--fiction-dir` interface ✓
- 2-person HOST/EXPERT format specified ✓
- Capstone structure: translation analysis, not content re-teaching ✓
- `resolve_prompt_path("fiction_meta")` resolves correctly ✓

**May have broken / misaligned:** Nothing. Only the placeholder stub was replaced.

---

## Pass 3 — Wire fiction content injection in run_chapter.py

**Changed:**
- `podcast_script_generator/llm/read_prompt.py` — added `fiction_content: str | None = None` param; substitutes `{FICTION_CONTENT}` when provided
- `podcast_script_generator/llm/call_api.py` — `user_message` assembly now skips `\n\n---\n\n{pdf_text}` when `pdf_text` is empty (fiction_meta passes both contents inside the prompt itself)
- `src/run_chapter.py`:
  - `run_llm()` — added `fiction_content` param; for `fiction_meta` mode: extracts pdf_text, substitutes `{TECHNICAL_CONTENT}`, calls `call_api("", prompt)`; other modes unchanged
  - `main()` — fiction_meta guard: requires `--fiction-dir`, validates dir exists, extracts chapter number from PDF stem via `re.match(r"^(\d+)")`, looks for `chapter_NN.md`, falls back to glob `*NN*.md`, loads file, passes content through to `run_llm()`

**Verified (all PASS):**
- `{FICTION_CONTENT}` substituted in prompt when `fiction_content` is provided ✓
- `{FICTION_CONTENT}` left intact when `fiction_content=None` ✓
- `call_api("", prompt)`: `user_message` is prompt only, no separator appended ✓
- `call_api("PDF", prompt)`: `user_message` still appends pdf_text for non-empty (no regression) ✓
- `run_llm(mode="fiction_meta")`: `pdf_text` replaced in prompt, empty string passed to `call_api` ✓
- `run_llm(mode="2person")`: `pdf_text` still passed to `call_api` (no regression) ✓
- `--mode fiction_meta` without `--fiction-dir` → "requires --fiction-dir" error, exit 1 ✓
- `--fiction-dir /nonexistent` → "fiction directory not found" error, exit 1 ✓
- No matching chapter file → "no fiction chapter found" error, exit 1 ✓

**May have broken / misaligned:**
- `read_prompt()` signature changed from 2 to 3 params; `main.py` in `podcast_script_generator/llm/` passes only 2 (context), which is fine — `fiction_content` defaults to None.
- `call_api` behavior change: previously `""` pdf_text would produce `prompt\n\n---\n\n`; now it produces `prompt` only. This only affects the internal user_message string — no external API contract change.

---

## Post-phase follow-up — call_api.py retry logic (commits ec59a50, 9b888e5)

Discovered during end-to-end testing of Phase 6: free-tier upstream providers return transient
429s with an explicit `retry_after_seconds` field. Previously `call_api` raised immediately,
causing the caller to burn daily quota switching models unnecessarily.

**Additional changes to `podcast_script_generator/llm/call_api.py`:**

- Retries up to 4 times on 429
- Wait time priority: `OPENROUTER_RETRY_AFTER` env var → `retry_after_seconds` in `config.json`
  → `retry_after_seconds` from API error body → exponential backoff (30s, 60s, 120s, 240s)
- Non-429 errors still raise immediately
- Prints wait time to stdout so the user can see what's happening

**Verified:** unit tests for all four priority levels and the exhaust-retries case.
