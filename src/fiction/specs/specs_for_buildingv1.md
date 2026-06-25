# Pipeline Specification — Complete

## Overview

CLI tool. Calls OpenRouter API. Automates the manual loop of: load templates → request chapter → approve → request living doc update → save → repeat until session is full → exit so human can start fresh session.

Modular. Stateless API assumption. Atomic writes. Cost-gated. Token-budget-gated.

---

## Custom Exceptions

All inherit from base `PipelineError`:
- `DocumentLoadError`
- `ConfigError`
- `APIResponseError`
- `ChapterValidationError`
- `LivingDocValidationError`
- `ContextOverflowError`
- `CostLimitError`

---

## Functions

### `load_static_docs(paths: list[str]) -> dict[str, str]`
Opens the template files and holds their text in memory so we don't re-read them every time.

- Encoding: UTF-8 strict. Decode errors → `DocumentLoadError`.
- Missing file → `FileNotFoundError` with full path. No silent skipping.
- Empty file → `DocumentLoadError("empty: {path}")`.
- Returns `{filename_without_ext: content}`. Filename collision → `ValueError`.
- Extension dispatch:
  - `.md`, `.txt`, `.markdown` → raw UTF-8 read.
  - `.docx` → `python-docx` extraction, paragraph breaks preserved as `\n\n`.
  - `.pdf` → `DocumentLoadError("PDF not supported in v1: {path}. Convert to .md or .docx.")`.
  - Other / missing extension → `DocumentLoadError("unsupported extension: {ext} at {path}")`.

### `load_living_doc(path: str) -> str`
Opens the one file that changes between chapters and holds its current text in memory.

- UTF-8 strict.
- Missing file → return empty string and log warning (first-ever run case). Does *not* raise.
- Returns raw text, trailing whitespace stripped.

### `save_living_doc(path: str, content: str) -> None`
Writes the updated living doc back to disk.

- Atomic write: write to `{path}.tmp`, fsync, `os.replace` over original.
- Backup: before replacing, copy existing to `{path}.bak.{timestamp}`. Keep last 10, delete older.
- Empty content → `ValueError("refusing to save empty living doc")`.
- Overwrite is default. No prompt.

### `save_chapter(path: str, chapter_num: int, content: str) -> str`
Writes a finished chapter to disk with a clear filename.

- Filename: `chapter_{chapter_num:02d}.md` inside configured output dir.
- Never overwrite. If exists, write to `chapter_{N:02d}__{timestamp}.md` and log warning. Returns actual path written.
- Empty content → `ValueError`.
- Atomic write.

### `count_tokens(text: str, model: str) -> int`
Estimates how many tokens a piece of text will use, so we know if it fits in the AI's context window.

- Uses `tiktoken` with `cl100k_base` as default for non-OpenAI models (±10% error accepted).

### `build_prompt(static_docs: dict, living_doc: str, task: str, extra: str = "") -> list[dict]`
Glues all documents together into the message bundle exactly the way you currently paste them by hand.

- `task` must be `"generate_chapter"` or `"update_living_doc"`. Else `ValueError`.
- Returns OpenRouter-compatible:
  ```
  [
    {"role": "system", "content": <task-specific system prompt>},
    {"role": "user", "content": <concatenated docs + task instruction + extra>}
  ]
  ```
- Fixed concatenation order: world_bible → curriculum → style_contract → full_map → living_doc → task instruction.
- Each doc wrapped: `=== {NAME} ===\n{content}\n=== END {NAME} ===\n\n`.
- `extra` appended verbatim. Empty by default.

**System prompt for `generate_chapter`:**
```
You are a fiction-writing assistant working inside a strict pedagogical novel pipeline. The user has provided immutable reference documents (world bible, concept curriculum, style contract, full system-design map) and a mutable living document tracking the current state of the novel. Your job is to write the next chapter only. Follow the style contract exactly: declarative, physical-before-philosophical, experience-before-label. Respect the curriculum: introduce only the concepts scheduled for this chapter. Honor the living doc: continue from the exact state described, use only vocabulary the protagonist has earned, and execute the planned key event and emotional beat. Output the chapter text only — no preamble, no commentary, no meta-discussion. Begin with the chapter heading.
```

**System prompt for `update_living_doc`:**
```
You are a continuity-tracking assistant for a pedagogical novel pipeline. The user will provide the immutable reference documents, the current living document, and the chapter that was just written and approved. Your job is to produce an updated living document reflecting the new state after this chapter. Preserve the exact section headers and structure of the living document template. Increment touch counts for terms used. Move terms between sections as they earn higher status. Update CURRENT STATE, ACTIVE VOCABULARY, FORESHADOWING, LENS, and NEXT CHAPTER TARGET. Output the updated living document only — no preamble, no commentary, no diff, no explanation. Begin with the first line of the living doc.
```

### `call_api(messages: list[dict], model: str, config: dict) -> str`
The one place that talks to OpenRouter. Sends the bundle, waits, returns the AI's reply as text.

- Endpoint: `https://openrouter.ai/api/v1/chat/completions`.
- API key from `config["api_key"]` or env `OPENROUTER_API_KEY`. Missing → `ConfigError`.
- Timeout: `config.get("timeout_seconds", 120)` connect+read.
- Retries: up to `config.get("max_retries", 3)`. Exponential backoff: 2s, 8s, 32s. Retry on 429, 500, 502, 503, 504, connection errors, timeouts. Do *not* retry 400, 401, 403 — raise immediately.
- Pre-flight token check:
  - `prompt_tokens = count_tokens(full_prompt, model)`
  - If `prompt_tokens + config["context_safety_margin"] > config["context_limit"]` → `ContextOverflowError` with token counts per document. No auto-truncation.
- Pre-flight cost check (see cost gate below).
- Malformed response (invalid JSON, missing `choices[0].message.content`) → `APIResponseError` with raw body.
- Empty content → treat as failure, retry. Final empty → raise.
- Post-call: read `usage` field, compute actual cost, call `track_spend`.
- Returns assistant text, stripped.
- Logs every attempt (model, token counts, duration, status).

### `estimate_cost(prompt_tokens: int, expected_output_tokens: int, config: dict) -> float`
Multiplies token counts by configured prices, returns dollars.

### `track_spend(amount: float, config: dict) -> dict`
Appends spend to `./.pipeline_spend.json` with running totals per session and lifetime. Returns current totals.

### `request_chapter(static_docs, living_doc, model, config) -> str`
Asks the AI for the next chapter.

- Builds prompt with `task="generate_chapter"`.
- Task instruction appended as `extra`:
  ```
  === TASK ===
  Write the next chapter following the NEXT CHAPTER TARGET section of the living document above. Output the chapter only.
  ```
- Calls `call_api`.
- Validates response ≥ `config.get("min_chapter_words", 500)` words. Below → `ChapterValidationError`. No auto-retry; surface to human.
- Returns chapter text.

### `request_living_doc_update(static_docs, old_living_doc, new_chapter, model, config) -> str`
Asks the AI to update the living doc after a chapter is approved.

- New chapter passed via `extra`, labeled `=== NEW CHAPTER JUST WRITTEN ===\n{chapter}\n=== END NEW CHAPTER ===`.
- Task instruction also in `extra`:
  ```
  === TASK ===
  Produce the updated living document reflecting the chapter just written. Preserve all section headers from the template. Output the updated living document only.
  ```
- Sanity check: response must contain expected headers (`=== LIVING DOCUMENT ===`, `--- CURRENT STATE ---`). Missing → `LivingDocValidationError`. Surface to human.
- Returns updated living doc text.

### `run_session(config: dict, *, auto_approve: bool = False, dry_run: bool = False, resume: bool = False, chapter_start: int | None = None) -> None`
The conductor. Runs the manual loop for you.

- Loads static docs and living doc up front. Any load failure → abort before any API call.
- Pre-session summary printed:
  ```
  Model: {model}
  Static docs: {N} files, {tokens} tokens
  Living doc: {tokens} tokens
  Estimated cost per chapter (gen + update): ${X}
  Session budget: ${Y} ({Z} chapters possible)
  Lifetime spent: ${W} / ${total_limit}
  Proceed? [y/N]
  ```
  Skipped with `auto_approve`.
- Loop `config["chapters_per_session"]` times (default 3):
  1. Call `request_chapter`. On failure: `[r]etry / [s]kip / [a]bort`.
  2. Save chapter immediately on success.
  3. Show path and word count.
  4. Prompt: `Approve and update living doc? [y/n/q]`. `n` = discard, back to step 1. `q` = save state, exit clean.
  5. On `y`: call `request_living_doc_update`. On failure: `[r]etry / [k]eep old living doc / [a]bort`.
  6. Save living doc atomically (backup auto).
- `auto_approve` skips approval prompts.
- `dry_run` does everything except write files and call API.
- `resume` skips chapters already on disk in output dir.
- KeyboardInterrupt handling:
  - HTTP request mid-flight is not cleanly interruptible. Response lost on Ctrl-C.
  - Each iteration wrapped in try/except.
  - Interrupt *before* chapter saved → nothing saved, previous state intact.
  - Interrupt *after* chapter saved but *before* living doc update → chapter on disk, living doc unchanged, log `interrupted_between_chapter_and_update`. Next `--resume` detects orphan.
  - Prints: `Interrupted. State preserved. Last saved: {path}. Exit code 1.`

### `load_config(path: str) -> dict`
Reads the small settings file that tells the tool which model, where the documents live, where to save chapters, etc.

- Format: TOML. Missing → `FileNotFoundError`.
- Required keys: `model`, `static_doc_paths` (list), `living_doc_path`, `output_dir`, `context_limit`, `price_per_1m_input_tokens`, `price_per_1m_output_tokens`. Missing any → `ConfigError` listing what's missing.
- Optional with defaults: `chapters_per_session=3`, `max_retries=3`, `timeout_seconds=120`, `min_chapter_words=500`, `log_path="./pipeline.log"`, `context_safety_margin=8000`, `cost_limit_usd_per_session=5.00`, `cost_limit_usd_total=50.00`, `expected_output_tokens_chapter=4000`, `expected_output_tokens_update=2000`.
- Env overrides for `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`.
- Unknown keys logged as warning, not error.

### `log_event(event: str, data: dict) -> None`
Writes one line to the logbook so you can see what the tool did.

- Format: JSONL. Fields: `timestamp` (ISO 8601 UTC), `event`, plus `data` contents.
- Append-only. Created on first call if missing.
- Logging failure prints to stderr, never crashes pipeline.

### `main(argv: list[str] | None = None) -> int`
CLI entry point. Parses arguments and calls `run_session`.

- `argparse` flags: `--config PATH`, `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start N`, `--ignore-cost-limit`.
- Calls `load_config`, then `run_session(config, auto_approve=..., dry_run=..., resume=...)`.
- Exit codes: 0 success, 1 user abort / KeyboardInterrupt, 2 config error, 3 API error after retries.

---

## Cost Gate (cross-cutting)

Config keys: `cost_limit_usd_per_session`, `cost_limit_usd_total`, `price_per_1m_input_tokens`, `price_per_1m_output_tokens`, `expected_output_tokens_chapter`, `expected_output_tokens_update`.

Pre-flight in `call_api`:
1. Count prompt tokens.
2. Estimate cost via `estimate_cost`.
3. `session_spend + estimate > session_limit` → `CostLimitError`. Override: `--ignore-cost-limit`.
4. `lifetime_spend + estimate > total_limit` → `CostLimitError`. Same override.
5. After response, read actual `usage`, compute real cost, `track_spend`.

Spend state stored in `./.pipeline_spend.json`.

---

## Document Concatenation Order (fixed contract)

1. world_bible
2. curriculum
3. style_contract
4. full_map
5. living_doc
6. `extra` (task instruction; for living doc updates, also includes the new chapter)

Each wrapped in `=== {NAME} ===` / `=== END {NAME} ===` markers.

---

## File Layout Produced

```
output_dir/
  chapter_01.md
  chapter_02.md
  ...
living_doc.md
living_doc.md.bak.{timestamp}   (rotating, keep 10)
pipeline.log                     (JSONL)
.pipeline_spend.json
```

---

Send `BUILD` on a line by itself to authorize implementation.