# AGENT 6 — WRITER

**Role:** Receives `assembled_prompt.md` from Orchestrator. Invokes the LLM via src/ tools. Returns chapter prose. Writes nothing to state or cards. Does no analysis.

**Called by:** Orchestrator (step 8). Only after Assembler has confirmed `assembled_prompt.md` is written.

---

## INPUT

Single file: `fiction_loop/prompts/assembled_prompt.md`

Writer reads no other document. No card files. No core documents. No state files.

---

## INVOCATION

Run the bridge script from the project root. The script reads `BOOKGEN_LLM_API_KEY`
from the shell environment, falling back to the repo-root `.env` automatically
(shell env wins if both are set).

**Before invoking the bridge (ARTIFACT FRESHNESS, LAW 9):** run
`rm -f fiction_loop/prompts/chapter_draft.md` so that a draft file existing
after this step means exactly one thing: THIS run's bridge succeeded. A stale
draft (previous run, or resurrected by a git clone — case law 2026-07-17) must
never be mistakable for fresh output.

**Run it in the background — this is the DEFAULT, not a fallback.** A chapter call
legitimately takes 5–10+ minutes on slower endpoints (per-request timeout is 180 s
× up to 4 attempts + backoffs), and foreground Bash tool timeouts (often 300 s)
kill it mid-generation from outside. Never run it foreground.

```bash
( PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py \
    --prompt fiction_loop/prompts/assembled_prompt.md \
    --config fiction_loop/tools/pipeline_config.toml \
    --output fiction_loop/prompts/chapter_draft.md ; \
  echo "BRIDGE_EXIT:$?" ) \
  > fiction_loop/logs/chapter_[NNN]/08_writer_bridge.out 2>&1 &
```

Then poll `fiction_loop/logs/chapter_[NNN]/08_writer_bridge.out` (about once per
minute, give up after 20 minutes and report BLOCKED):
- no `BRIDGE_EXIT` line yet → still running; keep waiting
- `BRIDGE_EXIT:0` → success; the `OK: [N] words` line is in the same file
- `BRIDGE_EXIT:1` → read the same file for the error type, handle per the ERROR
  HANDLING table below (documented cases only), else BLOCKED per agent_conduct.md

If your harness offers a native run-in-background Bash option, it is equally
acceptable — poll the same output file.

To override cost limits when explicitly needed:

```bash
PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py \
  --prompt fiction_loop/prompts/assembled_prompt.md \
  --config fiction_loop/tools/pipeline_config.toml \
  --output fiction_loop/prompts/chapter_draft.md \
  --ignore-cost-limit
```

---

## WHAT THE SCRIPT DOES

The script (`fiction_loop/tools/invoke_writer.py`) calls src/ tools in this sequence:

```
1. novel_pipeline.config.load_config(pipeline_config.toml)
   → validated config dict with all defaults applied

2. llm.env.resolve_from_env()
   → env overrides (BOOKGEN_LLM_API_KEY, BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS, etc.)

3. llm.factory.create_transport(...)
   → LLMTransport instance (OpenRouter)

4. Read assembled_prompt.md → string

5. Build messages:
   [
     {"role": "system", "content": config["system_prompt_generate_chapter"]},
     {"role": "user",   "content": assembled_prompt_text}
   ]

6. novel_pipeline.api.call_api(messages, model, config, client=transport, ...)
   → Token pre-flight (ContextOverflowError if over context_limit - safety_margin)
   → Cost pre-flight (CostLimitError if over session/lifetime limits)
   → HTTP call with retry (handled by transport)
   → Truncation detection (finish_reason="length" → ChapterValidationError)
   → Actual cost tracked in config["spend_file_path"]
   → Returns stripped assistant text

7. Word count validation:
   len(text.split()) >= config["min_chapter_words"]
   Fail → ChapterValidationError

8. Write chapter text to --output path
```

---

## OUTPUT

On success: chapter prose written to `fiction_loop/prompts/chapter_draft.md`.

Orchestrator reads this file and proceeds with step 9 (save to `/chapters/chapter_[NNN].md`).

Exit code 0 = success, chapter ready.
Exit code 1 = error (see stderr for detail).

---

## ERROR HANDLING

| Exception | Source | Writer action |
|---|---|---|
| `ContextOverflowError` | `call_api` — prompt too large | Print token breakdown per document to stderr. Exit 1. Report to Orchestrator: assembled_prompt.md must be trimmed. |
| `CostLimitError` | `call_api` — session or lifetime limit | Print current spend totals to stderr. Exit 1. Report to Orchestrator: user must re-run with `--ignore-cost-limit` or wait for session reset. |
| `APIRateLimitError` | `call_api` — 429 from provider | Transport retries per `retry_backoff_seconds`. If all retries exhausted: exit 1, report rate limit and retry delay. |
| `APIResponseError` | `call_api` — 5xx or bad response | Exit 1. Print raw error to stderr. Report to Orchestrator: retry or check API status. |
| `ChapterValidationError` (truncation) | `call_api` — finish_reason=length | Exit 1. Report: increase `api_default_max_tokens_chapter` in pipeline_config.toml. |
| `ChapterValidationError` (too short) | word count check | Exit 1. Report word count vs minimum. Orchestrator may retry. |
| `FileNotFoundError` (assembled_prompt.md) | read step | Exit 1. Assembler must run first. |
| `FileNotFoundError` (pipeline_config.toml) | load_config | Exit 1. Config file missing — see INTEGRATION_SPECS.md for required fields. |
| `ConfigError` | load_config | Exit 1. Print exact field missing or invalid. |
| `LLMConfigError` | create_transport | Exit 1. Check BOOKGEN_LLM_API_KEY env var is set. |

---

## CRITICAL RULES

- STOP-DON'T-GUESS (core/agent_conduct.md §1): the ONLY self-healing permitted is
  the error table above. An error not in that table → log BLOCKED, return the Error
  line, STOP. Never read or modify src/. Never vary parameters, models, or prompts
  experimentally — every invocation costs money; report instead.
- On ANY error, the final terminal status line MUST begin `BLOCKED` — never
  `DONE — Error:` or any other `DONE` variant.
- Writer reads ONLY `assembled_prompt.md` (plus core/agent_conduct.md for conduct). Never reads cards, state files, or core documents.
- Writer writes ONLY `fiction_loop/prompts/chapter_draft.md`. Never touches cards or state.
- Writer never receives or passes `mystery_anchor.json` content.
- All token counting, cost tracking, and overflow checks run inside `src/novel_pipeline/api.call_api()`. Writer does not reimplement these.
- Writer does not approve or reject the chapter. Orchestrator handles that (steps 9+).
- The `--ignore-cost-limit` flag is only passed when the Orchestrator receives explicit user instruction to override.
