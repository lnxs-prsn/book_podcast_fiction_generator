# Phase 06 — AI Context

## Goal

Add `fiction_meta` podcast mode: given a technical PDF chapter and its corresponding fiction
adaptation, produce a podcast episode that examines the translation between them — what
concepts survived intact, what was abstracted into metaphor, and where the fiction had to
simplify or distort.

## Architecture summary

Fiction_meta mode is different from all other modes in one key way: it needs **two** content
inputs, not one. Every other mode embeds the PDF content via `call_api`'s separator append.
For fiction_meta, both the technical content (PDF) and the fiction content must be in the
prompt itself so the LLM can reason about them side-by-side.

**Data flow:**

```
run_chapter.py main()
  └─ loads fiction file from --fiction-dir / chapter_NN.md
  └─ run_llm(pdf_path, mode="fiction_meta", fiction_content=<loaded text>)
       ├─ extract_pdf(pdf_path)             → pdf_text
       ├─ read_prompt(path, fiction_content=<text>)
       │    └─ substitutes {FICTION_CONTENT} → returns prompt with fiction embedded
       ├─ prompt.replace("{TECHNICAL_CONTENT}", pdf_text)
       │    → both placeholders now resolved
       └─ call_api("", prompt)              → empty pdf_text, no separator appended
```

**Other modes** (2person, 4person, code, realworld) are unchanged:
```
call_api(pdf_text, prompt)  → prompt + "\n\n---\n\n" + pdf_text
```

## Files touched

| File | What changed |
|------|-------------|
| `src/run_chapter.py` | Added `--fiction-dir` flag; fiction_meta guard block in `main()`; `run_llm()` new `fiction_content` param and fiction_meta branch |
| `podcast_script_generator/llm/read_prompt.py` | Added `fiction_content` param; substitutes `{FICTION_CONTENT}` |
| `podcast_script_generator/llm/call_api.py` | `user_message` skips pdf separator when `pdf_text` is empty |
| `podcast_script_generator/llm/prompts/mode_fiction_meta.txt` | Full prompt replacing placeholder stub |

## Chapter number matching

PDF stems follow the pattern: `01_chapter_Chapter_1_...`  
Fiction canonical files: `chapter_01.md` (default from `canonical_chapter_name_format` in fiction pipeline config)

Matching logic in `run_chapter.py main()`:
1. `re.match(r"^(\d+)", pdf_path.stem)` → leading digits (e.g. `"01"`)
2. Primary: look for `fiction_dir / f"chapter_{chapter_num:02d}.md"`
3. Fallback: glob `fiction_dir.glob(f"*{leading}*.md")`, take first sorted match
4. If nothing found: exit with clear error

## Key decisions

- **Both contents in prompt body, not separator**: `call_api`'s `\n\n---\n\n` append was designed
  for a single content source. Fiction_meta needs the LLM to know which is which. Embedding both
  with labelled headers (`SOURCE: TECHNICAL CHAPTER` / `SOURCE: FICTION CHAPTER`) is cleaner
  than passing two content arguments through the chain.

- **`read_prompt` handles `{FICTION_CONTENT}`, `run_llm` handles `{TECHNICAL_CONTENT}`**:
  `read_prompt` already handles string substitution (it does `{CURRENT_EVENT}`). Fiction content
  goes there. Technical content substitution happens in `run_llm` after `extract_pdf` runs,
  keeping the data flow explicit at the call site.

- **`parse_args.py` (llm module) not updated**: That module is for direct invocation of the
  podcast_script_generator. Fiction_meta is a `run_chapter.py`-level feature — the fiction file
  loading belongs at the integration layer, not inside the generator module.

## What to check first if something breaks

1. **`{TECHNICAL_CONTENT}` not substituted**: Check `run_llm()` — the replace happens after
   `extract_pdf()` returns. If PDF extraction fails, pdf_text is empty/raises before we get there.

2. **`{FICTION_CONTENT}` not substituted**: Check `read_prompt()` — verify `fiction_content` is
   non-None when passed in. Check that `main()` correctly loaded the file.

3. **Chapter file not found**: The fiction pipeline canonical format is `chapter_NN.md`. If the
   fiction pipeline config uses a different `canonical_chapter_name_format`, the primary lookup
   will fail and fall through to glob. Adjust the glob pattern if needed.

4. **API gets double content**: Verify `call_api` receives `pdf_text=""` for fiction_meta.
   The mode branch in `run_llm()` is `if mode == "fiction_meta":` — if that check is missed,
   the PDF text will be appended as a third block after the prompt.
