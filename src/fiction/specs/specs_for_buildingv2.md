# Pipeline Specification — Complete (Patched v2)

## Overview

CLI tool. Calls OpenRouter API. Automates the manual loop of: load templates → request chapter → approve → request living doc update → save → repeat until session is full → exit so human can start fresh session.

Modular. Stateless API assumption. Atomic writes. Cost-gated. Token-budget-gated. Approval-gated staging.

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
- `ResumeStateError` *(Patched v2)*

---

## File Layout Produced

```
output_dir/
  chapter_01.md                          (approved only)
  chapter_02.md
  ...
  .rejected/
    chapter_03__20260515T142301Z.md      (rejected drafts archived here)
    chapter_03__20260515T143812Z.md
living_doc.md
living_doc.md.bak.{timestamp}            (kept indefinitely)
pipeline.log                             (JSONL)
.pipeline_spend.json
.pipeline_state.json                     (Patched v2: tracks last chapter for which living doc was updated)
```

---

## Pipeline State File *(Patched v2)*

`./.pipeline_state.json` — single source of truth for cross-file consistency on resume.

Schema:
```json
{
  "last_chapter_promoted": 5,
  "last_chapter_living_doc_updated": 5,
  "updated_at": "2026-05-15T14:23:01Z"
}
```

- Written atomically (tmp + fsync + replace) after each successful living doc save.
- Also written after `promote_chapter` succeeds, with `last_chapter_promoted` advanced but `last_chapter_living_doc_updated` unchanged. This is the window during which an interrupt leaves the mismatch detectable.
- Missing file on resume → treated as fresh start; if canonical chapters exist on disk, `ResumeStateError` with message instructing human to either delete the chapters or reconstruct the state file manually.
- Malformed JSON → `ResumeStateError`.

---

## Functions

### `load_static_docs(paths: list[str]) -> dict[str, str]`
Opens the template files and holds their text in memory so we don't re-read them every time.

- UTF-8 strict. Decode errors → `DocumentLoadError`.
- Missing file → `FileNotFoundError` with full path.
- Empty file → `DocumentLoadError("empty: {path}")`.
- Returns `{filename_without_ext: content}`. Collision → `ValueError`.
- Extension dispatch:
  - `.md`, `.txt`, `.markdown` → raw UTF-8.
  - `.docx` → `python-docx`, paragraph breaks as `\n\n`.
  - `.pdf` → `DocumentLoadError("PDF not supported in v1: {path}. Convert to .md or .docx.")`.
  - Other / missing → `DocumentLoadError("unsupported extension: {ext} at {path}")`.

### `load_living_doc(path: str) -> str`
Opens the one file that changes between chapters.

- UTF-8 strict.
- Missing → return empty string, log warning (first run).
- Returns raw text, trailing whitespace stripped.

### `save_living_doc(path: str, content: str) -> None`
Writes the updated living doc back to disk.

- Atomic: write to `{path}.tmp`, fsync, `os.replace`.
- Backup: before replace, copy existing to `{path}.bak.{timestamp}`. **Keep all backups indefinitely.** (Patched: was 10.)
- Empty content → `ValueError("refusing to save empty living doc")`.

### `save_chapter_draft(path_dir: str, chapter_num: int, content: str) -> str`
**(New, patched.)** Writes a draft chapter to staging, *before* human approval.

- Writes to `{output_dir}/.rejected/chapter_{N:02d}__{timestamp}.md`. The `.rejected/` directory exists by convention; on approval, the file is moved out. On rejection, it stays.
- Atomic write. Returns path written.
- Empty content → `ValueError`.

### `promote_chapter(draft_path: str, output_dir: str, chapter_num: int) -> str`
**(New, patched.)** Moves an approved draft from staging to canonical location.

- Target: `{output_dir}/chapter_{N:02d}.md`.
- If target exists (resume edge case) → write as `chapter_{N:02d}__{timestamp}.md` and log warning.
- Uses `os.replace`. Returns final path.
- *(Patched v2)* After successful `os.replace`, caller must update `.pipeline_state.json` to advance `last_chapter_promoted`. This is documented as a caller responsibility, not done inside `promote_chapter` itself, to keep the function single-purpose.

### `count_tokens(text: str, model: str) -> int`
Estimates token count so we know if the prompt fits in the AI's context window.

- `tiktoken` with `cl100k_base` fallback (±10% accepted).

### `build_prompt(static_docs: dict, living_doc: str, task: str, extra: str = "") -> list[dict]`
Glues all documents together into the message bundle exactly the way you currently paste them by hand.

- `task` must be `"generate_chapter"` or `"update_living_doc"`. Else `ValueError`.
- Returns OpenRouter-compatible message list.
- Fixed concatenation order: world_bible → curriculum → style_contract → full_map → living_doc → task instruction.
- Each doc wrapped: `=== {NAME} ===\n{content}\n=== END {NAME} ===\n\n`.

**System prompt for `generate_chapter`:**
```
You are a fiction-writing assistant working inside a strict pedagogical novel pipeline. The user has provided immutable reference documents (world bible, concept curriculum, style contract, full system-design map) and a mutable living document tracking the current state of the novel. Your job is to write the next chapter only. Follow the style contract exactly: declarative, physical-before-philosophical, experience-before-label. Respect the curriculum: introduce only the concepts scheduled for this chapter. Honor the living doc: continue from the exact state described, use only vocabulary the protagonist has earned, and execute the planned key event and emotional beat. Output the chapter text only — no preamble, no commentary, no meta-discussion. Begin with the chapter heading.
```

**System prompt for `update_living_doc`:**
```
You are a continuity-tracking assistant for a pedagogical novel pipeline. The user will provide the immutable reference documents, the current living document, and the chapter that was just written and approved. Your job is to produce an updated living document reflecting the new state after this chapter. Preserve the exact section headers and structure of the living document template. Increment touch counts for terms used. Move terms between sections as they earn higher status. Update CURRENT STATE, ACTIVE VOCABULARY, FORESHADOWING, LENS, and NEXT CHAPTER TARGET. Output the updated living document only — no preamble, no commentary, no diff, no explanation. Begin with the first line of the living doc.
```

### `validate_living_doc_structure(content: str, required_sections: list[str]) -> tuple[bool, list[str]]`
**(New, patched.)** Checks that the updated living doc preserves required sections in order.

- `required_sections` comes from config. *(Patched v2)* Default uses generic character-agnostic header names — see `load_config` for the new default list.
- Returns `(ok: bool, missing_or_reordered: list[str])`.
- Each section header must appear in the document, and they must appear in the listed order. Substring match (case-sensitive) on a line basis.
- Failure → `LivingDocValidationError` raised by caller, with the failing section list and a diff against the previous living doc shown to the human.

### `find_next_chapter_number(output_dir: str) -> int`
***(New, Patched v2.)*** Determines which chapter number to write next using gap-scan semantics.

- Scans `output_dir` for files matching `chapter_NN.md` (canonical only, ignores `.rejected/`).
- Returns the first missing positive integer in the sequence starting at 1.
- Empty directory → returns 1.
- No gaps, chapters 1..N present → returns N+1.
- Gap mid-sequence (e.g. 01, 03 present, 02 missing) → returns 2.
- Does not consult `.pipeline_state.json`; this function answers only "where does the next file go" based on filesystem reality.

### `detect_resume_state(output_dir: str, state_file_path: str) -> dict`
***(New, Patched v2.)*** Cross-checks filesystem state against `.pipeline_state.json` to detect interrupt-mid-cycle conditions.

- Reads `.pipeline_state.json`. Missing or malformed → see Pipeline State File section.
- Computes `next_chapter_number` via `find_next_chapter_number`.
- Returns:
  ```python
  {
      "next_chapter": int,
      "last_promoted": int,        # from state file
      "last_doc_updated": int,     # from state file
      "consistent": bool,          # True iff last_promoted == last_doc_updated
      "gaps_present": list[int],   # canonical chapter numbers missing below max
  }
  ```
- Caller (`run_session`) decides what to do with inconsistency or gaps. This function does not prompt or raise.

### `call_api(messages: list[dict], model: str, config: dict) -> str`
The one place that talks to OpenRouter.

- Endpoint: `https://openrouter.ai/api/v1/chat/completions`.
- API key from `config["api_key"]` or env `OPENROUTER_API_KEY`. Missing → `ConfigError`.
- Timeout: `config.get("timeout_seconds", 120)`.
- **Retries (patched):** up to `config.get("max_retries", 3)`. Retry on 429, 500, 502, 503, 504, connection errors, timeouts. Do *not* retry 400, 401, 403.
  - If response has `Retry-After` header → honor it (parse seconds or HTTP date).
  - Otherwise exponential backoff: 2s, 8s, 32s.
- **Token pre-flight:**
  - `prompt_tokens = count_tokens(full_prompt, model)`.
  - If `prompt_tokens + safety_margin > context_limit` → `ContextOverflowError` with per-document breakdown:
    ```
    Context overflow: prompt is {prompt_tokens} tokens, limit is {context_limit}, safety margin {margin}.
    Document sizes:
      world_bible:     {N} tokens
      curriculum:      {N} tokens
      style_contract:  {N} tokens
      full_map:        {N} tokens
      living_doc:      {N} tokens  <-- largest mutable document
    Suggestions:
      1. Manually compress living_doc (remove resolved foreshadowing, collapse Touch 2+ entries).
      2. Switch to a model with larger context window.
    No automatic truncation — that would corrupt pedagogical tracking.
    ```
- Cost pre-flight (see cost gate).
- Malformed JSON or missing `choices[0].message.content` → `APIResponseError`.
- Empty content → retry; final empty → raise.
- Post-call: read `usage`, compute actual cost, `track_spend`.
- Returns assistant text, stripped.

### `estimate_cost(prompt_tokens: int, expected_output_tokens: int, config: dict) -> float`
Multiplies token counts by configured per-million prices, returns dollars.

### `track_spend(amount: float, config: dict) -> dict`
Appends spend to `./.pipeline_spend.json` with session and lifetime totals.

### `request_chapter(static_docs, living_doc, model, config) -> str`
Asks the AI for the next chapter.

- Builds prompt with `task="generate_chapter"`.
- Task instruction appended as `extra`:
  ```
  === TASK ===
  Write the next chapter following the NEXT CHAPTER TARGET section of the living document above. Output the chapter only.
  ```
- Calls `call_api`.
- **Validates response ≥ `config.get("min_chapter_words", 1500)` words** (patched: was 500). Below → `ChapterValidationError`. Surface to human.
- Returns chapter text.

### `request_living_doc_update(static_docs, old_living_doc, new_chapter, model, config) -> str`
Asks the AI to update the living doc after a chapter is approved.

- New chapter passed via `extra`, labeled `=== NEW CHAPTER JUST WRITTEN ===\n{chapter}\n=== END NEW CHAPTER ===`.
- Task instruction in `extra`:
  ```
  === TASK ===
  Produce the updated living document reflecting the chapter just written. Preserve all section headers from the template. Output the updated living document only.
  ```
- **Structural validation (patched):** calls `validate_living_doc_structure`. Failure → `LivingDocValidationError` with diff against `old_living_doc` shown to human.
- Returns updated living doc text.

### `run_session(config: dict, *, auto_approve: bool = False, dry_run: bool = False, resume: bool = False, chapter_start: int | None = None) -> None`
The conductor.

- Loads static docs and living doc up front. Failure → abort before any API call.

- **Determine starting chapter number *(Patched v2, replaces v1 resume logic):***
  - If `chapter_start` is provided:
    - Compute `next_chapter = find_next_chapter_number(output_dir)`.
    - If `chapter_start != next_chapter`, warn loudly:
      ```
      --chapter-start {chapter_start} specified.
      Natural next chapter (first gap or append point) would be {next_chapter}.
      Canonical chapters present: {list}.
      Missing in sequence: {gaps}.
      Proceeding with --chapter-start {chapter_start} will skip these.
      Continue? [y/N]
      ```
    - Skippable with `--auto-approve`.
    - `chapter_start` wins after confirmation.
  - Else if `resume`:
    - `state = detect_resume_state(output_dir, state_file_path)`.
    - If `state["gaps_present"]` is non-empty, print one-line notice: `Chapters present: 01..NN with gaps at {gaps}. Resuming at chapter {state["next_chapter"]}.`
    - If `not state["consistent"]` (i.e. `last_promoted > last_doc_updated`):
      - Print:
        ```
        Interrupted state detected:
          Chapter {last_promoted} was promoted but living doc was not updated.
          Living doc currently reflects state through chapter {last_doc_updated}.
        Options:
          [r] Regenerate living doc from chapter {last_promoted} (calls API, costs tokens)
          [c] Continue anyway — living doc will be stale; next chapter prompt will use outdated context
          [a] Abort
        Choice:
        ```
      - On `r`: read `chapter_{last_promoted:02d}.md`, call `request_living_doc_update`, validate, save, update state file. Then proceed.
      - On `c`: log `resumed_with_stale_living_doc`, proceed.
      - On `a`: exit clean.
  - Else (no `chapter_start`, no `resume`):
    - Compute `next_chapter = find_next_chapter_number(output_dir)`.
    - If `next_chapter > 1` (chapters already exist but `--resume` not passed), warn:
      ```
      Output directory contains chapters but --resume not specified.
      Next chapter would be {next_chapter}. Re-run with --resume to continue, or with --chapter-start to override.
      Aborting.
      ```
      Exit code 2.

- **Pre-session summary (patched):**
  ```
  Model: {model}
  Static docs: {N} files, {tokens} tokens
  Living doc: {tokens} tokens  (grows ~{avg_delta} tokens/chapter)
  Estimated cost — next chapter (gen + update): ${X}
  Session budget: ${Y}
  Lifetime spent: ${W} / ${total_limit}
  Note: Per-chapter cost grows as living doc grows. Estimate is for the *next* chapter only.
  Proceed? [y/N]
  ```
  Skippable with `auto_approve`.

- Loop `config["chapters_per_session"]` times (default 3):
  1. Call `request_chapter`. On failure: `[r]etry / [s]kip / [a]bort`.
  2. **(Patched.)** Save draft via `save_chapter_draft` to `.rejected/`. Show path and word count.
  3. Prompt: `Approve and update living doc? [y/n/q]`.
     - `n` = draft stays in `.rejected/`, log `chapter_rejected`, loop back to step 1.
     - `q` = save state, exit clean. Draft remains in `.rejected/`.
     - `y` = continue to step 4.
  4. `promote_chapter` moves draft to canonical `chapter_NN.md`.
  5. ***(Patched v2.)*** Atomically update `.pipeline_state.json` with `last_chapter_promoted = N`.
  6. Call `request_living_doc_update`. On failure (including structural validation): `[r]etry / [k]eep old living doc / [a]bort`. On `k`, chapter stays promoted but living doc unchanged — log `chapter_approved_but_living_doc_unchanged`. State file shows mismatch; next resume will detect it.
  7. Save living doc atomically.
  8. ***(Patched v2.)*** Update `.pipeline_state.json` with `last_chapter_living_doc_updated = N`.
  9. **Re-print cost estimate for next iteration using current actual token counts.**

- `auto_approve` skips approval prompts.
- `dry_run` does everything except write files and call API.

- **KeyboardInterrupt *(Patched v2, replaces v1 interrupt section):***
  - Interrupt *before* draft saved → nothing on disk this iteration.
  - Interrupt *after* draft saved, *before* approval → draft in `.rejected/`, no canonical chapter, state file unchanged. Resume picks up cleanly.
  - Interrupt *after* `promote_chapter` but *before* state file update for promotion → canonical chapter exists, state file still shows previous `last_chapter_promoted`. On resume, `find_next_chapter_number` sees the new chapter and advances; `detect_resume_state` sees state file lagging. Inconsistency is detected and prompted.
  - Interrupt *after* promotion-state-update but *before* living doc save → state file shows `last_promoted > last_doc_updated`. Resume detects, offers regenerate/continue/abort.
  - Interrupt *after* living doc save but *before* doc-state-update → state file shows `last_promoted > last_doc_updated` even though disk is consistent. Resume will offer to regenerate, which is wasteful but not incorrect (regenerating produces the same living doc). Acceptable: the window is microseconds (one atomic write apart).
  - Prints: `Interrupted. State preserved. Last saved: {path}. Exit code 1.`

### `load_config(path: str) -> dict`
Reads settings.

- TOML. Missing → `FileNotFoundError`.
- Required: `model`, `static_doc_paths`, `living_doc_path`, `output_dir`, `context_limit`, `price_per_1m_input_tokens`, `price_per_1m_output_tokens`.
- Optional with defaults (patched values marked):
  - `chapters_per_session=3`
  - `max_retries=3`
  - `timeout_seconds=120`
  - **`min_chapter_words=1500`** (patched: was 500)
  - `log_path="./pipeline.log"`
  - `context_safety_margin=8000`
  - `cost_limit_usd_per_session=5.00`
  - `cost_limit_usd_total=50.00`
  - `expected_output_tokens_chapter=4000`
  - `expected_output_tokens_update=2000`
  - **`required_living_doc_sections`** — *(Patched v2)* default now uses generic character-agnostic header names:
    ```
    ["=== LIVING DOCUMENT ===",
     "--- CURRENT STATE ---",
     "--- ACTIVE VOCABULARY ---",
     "--- TERMS LEARNED BUT NOT YET OWNED ---",
     "--- TERMS INTRODUCED THIS ARC ---",
     "--- ACTIVE FORESHADOWING ---",
     "--- PROTAGONIST LENS ---",
     "--- NEXT CHAPTER TARGET ---",
     "--- NOTES FOR AI ---"]
    ```
    Section names in this config must match the living doc template verbatim. Novel-specific config overrides with project-specific names (e.g. `--- main character'S ACTIVE VOCABULARY`, `--- main character'S LENS RIGHT NOW ---`). Library defaults are generic; application config specializes.
  - ***(Patched v2)*** `state_file_path="./.pipeline_state.json"`
- Env overrides: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`.
- Unknown keys logged as warning.

### `log_event(event: str, data: dict) -> None`
Writes one line to the logbook.

- JSONL, append-only. Created on first call.
- Logging failure → stderr, never crashes pipeline.

### `main(argv: list[str] | None = None) -> int`
CLI entry point.

- `argparse` flags: `--config PATH`, `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start N`, `--ignore-cost-limit`.
- Exit codes: 0 success, 1 user abort / KeyboardInterrupt, 2 config error *(Patched v2: also `ResumeStateError`)*, 3 API error after retries.

---

## Cost Gate (cross-cutting)

Pre-flight in `call_api`:
1. Count prompt tokens.
2. Estimate cost.
3. Session limit exceeded → `CostLimitError`. Override: `--ignore-cost-limit`.
4. Lifetime limit exceeded → same.
5. After response, read actual `usage`, compute real cost, `track_spend`.

State: `./.pipeline_spend.json`.

---

## Patches Summary

**v1 patches:**

1. **Discard Pollution fixed:** drafts go to `.rejected/`, only promoted to canonical on `y`. `save_chapter_draft` + `promote_chapter` replace direct save. Resume scans canonical only.
2. **Context Death Spiral mitigated (not auto-fixed):** `ContextOverflowError` now reports per-document token breakdown and suggests manual remediation. No silent summarization.
3. **Living Doc Structural Blindness fixed:** `validate_living_doc_structure` checks all required sections present and in order. Config-driven section list.
4. **Cost estimate honesty:** pre-session summary notes growth, re-prints per-iteration.
5. **Rate limits:** honor `Retry-After` when present.
6. **`min_chapter_words`:** raised to 1500.
7. **Backup rotation:** keep all backups, not just 10.

**v2 patches:**

1. **Resume gap-scan:** `find_next_chapter_number` returns first missing integer ≥ 1, not max+1. Empty dir → 1. Mid-sequence gaps detected and filled. `--chapter-start` overrides but warns loudly on skipped gaps.
2. **Generic section defaults:** `required_living_doc_sections` default uses character-agnostic header names. Project config overrides with novel-specific names. Spec notes the verbatim-match requirement.
3. **Interrupt-mid-cycle detection via state file:** new `.pipeline_state.json` tracks `last_chapter_promoted` and `last_chapter_living_doc_updated`. `detect_resume_state` compares filesystem against state file. On mismatch, human is prompted to regenerate, continue stale, or abort. New `ResumeStateError` exception.
4. **No-resume safety:** if `output_dir` contains chapters but `--resume` not passed and no `--chapter-start`, abort with instructions rather than silently starting fresh.

---
