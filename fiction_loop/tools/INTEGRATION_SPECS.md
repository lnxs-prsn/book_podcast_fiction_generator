# FICTION LOOP — SRC/ INTEGRATION SPECS

> **DRIFT NOTE 2026-07-03:** this build-time spec has drifted from the living
> system. Where it disagrees with `pipeline_config.toml`, `agents/writer.md`,
> or `agents/orchestrator.md`, THOSE are authoritative. Known drift: §3 example
> values (model/prices are per-deployment now), §3.1–3.2 prompt texts (TOML has
> newer versions incl. HARD RULES self-check), §6 invocation (bridge calls now
> run in the BACKGROUND with poll — see writer.md), and both scripts load
> repo-root .env as fallback.

**Purpose:** Defines everything needed to give fiction_loop agents access to the LLM and pipeline tools in `src/`. Covers contracts, config schema, business logic, and edge cases.

---

## 1. OVERVIEW

fiction_loop agents are AI coding-agent sessions (any harness with file, shell, and subagent tools) directed by markdown specs. `src/` contains Python tools: LLM transport (`src/llm/`), API call layer with cost/token management (`src/novel_pipeline/api.py`), and config loading (`src/novel_pipeline/config.py`).

The bridge is a pair of Python scripts in `fiction_loop/tools/` that the Writer and Living Doc Refresh agents invoke via the shell tool. The agent runs the script, reads the output file, and continues the loop.

```
fiction_loop agents (AI coding agent)
          │
          │  Bash: python fiction_loop/tools/invoke_writer.py ...
          ▼
fiction_loop/tools/invoke_writer.py
          │
          │  Python import (PYTHONPATH=src)
          ▼
src/novel_pipeline/api.call_api()
          │
          │  HTTP
          ▼
OpenRouter API → chapter text
```

---

## 2. FILES TO CREATE

```
fiction_loop/tools/
  invoke_writer.py          — chapter generation bridge
  refresh_living_doc.py     — living document LLM update bridge
  pipeline_config.toml      — TOML config wiring fiction_loop into src/ tools
```

---

## 3. pipeline_config.toml — SCHEMA SPEC

**Location:** `fiction_loop/tools/pipeline_config.toml`

**Consumed by:** `novel_pipeline.config.load_config()` — validates and applies defaults.

### Required fields (no defaults exist)

| Field | Type | Fiction loop value | Notes |
|---|---|---|---|
| `model` | string | e.g. `"anthropic/claude-opus-4-8"` | OpenRouter model ID |
| `static_doc_paths` | list[string] | `[]` | Empty — invoke_writer builds its own messages |
| `living_doc_path` | string | `"../core/living_document.md"` | Relative to config file location |
| `output_dir` | string | `"../chapters"` | Where promoted chapters are saved |
| `context_limit` | integer | e.g. `200000` | Must match model's actual context window |
| `price_per_1m_input_tokens` | float | e.g. `15.00` | USD per 1M input tokens |
| `price_per_1m_output_tokens` | float | e.g. `75.00` | USD per 1M output tokens |

### Required overrides (defaults exist but wrong for fiction_loop)

| Field | Type | Fiction loop value | Why override |
|---|---|---|---|
| `spend_file_path` | string | `"../state/.pipeline_spend.json"` | Keep spend tracking inside fiction_loop dir |
| `state_file_path` | string | `"../state/.pipeline_state.json"` | Keep pipeline state inside fiction_loop dir |
| `log_path` | string | `"../logs/pipeline.log"` | Keep logs inside fiction_loop dir |
| `min_chapter_words` | integer | `2000` | fiction_loop target is 2000–3000 words |
| `expected_output_tokens_chapter` | integer | `4000` | ~3000 words ÷ 0.75 words/token |
| `api_default_max_tokens_chapter` | integer | `5000` | Buffer above expected_output_tokens |
| `system_prompt_generate_chapter` | string | (see section 3.1) | Custom prompt for fiction_loop style |
| `system_prompt_update_living_doc` | string | (see section 3.2) | Custom prompt for fiction_loop living_doc format |
| `required_living_doc_sections` | list[string] | (see section 3.3) | Must match fiction_loop/core/living_document.md headers |

### Optional tuning

| Field | Type | Default | Notes |
|---|---|---|---|
| `temperature` | float | null (omit) | Leave null to use model default |
| `timeout_seconds` | float | `120` | Increase for long chapters on slow models |
| `cost_limit_usd_per_session` | float | `5.00` | Adjust per use pattern |
| `cost_limit_usd_total` | float | `50.00` | Adjust per budget |
| `max_retries` | integer | `3` | Transport-level HTTP retries |
| `retry_backoff_seconds` | list[float] | `[2, 8, 32]` | Exponential backoff on 429/5xx |

### 3.1 system_prompt_generate_chapter

The default novel_pipeline prompt specifies 1500–2500 words. Override for fiction_loop:

```toml
system_prompt_generate_chapter = """
You are a fiction-writing assistant. You receive a self-contained chapter generation prompt.
Write the chapter exactly as specified. Length: 2000–3000 words. Both limits are hard requirements.
Output the chapter text only — no preamble, no commentary, no meta-discussion.
Begin with the chapter heading.
"""
```

### 3.2 system_prompt_update_living_doc

The default prompt targets novel_pipeline's living_doc format. Override for fiction_loop's table-based format:

```toml
system_prompt_update_living_doc = """
You are a continuity-tracking assistant for a fiction loop. You receive:
- The fiction loop's core documents (world rules, style contract, concept curriculum)
- The current living_document.md
- The chapter just written

Produce an updated living_document.md that reflects the new state after this chapter.
Preserve ALL section headers verbatim and in the same order. Update only the content within sections.
Output the complete updated living_document.md only — no preamble, no commentary, no diff.
The document must begin with: # DOCUMENT 4: LIVING DOCUMENT
"""
```

### 3.3 required_living_doc_sections

These headers are validated by `request_living_doc_update()` after the LLM call:

```toml
required_living_doc_sections = [
  "# DOCUMENT 4: LIVING DOCUMENT",
  "## CURRENT STATE",
  "## PROCESS STATE SUMMARY",
  "## FAILURE MODES NOT YET SHOWN",
  "## POPULATION INDEX",
  "## MYSTERY PERSON THREAD",
  "## MACRO MYSTERY EVIDENCE",
  "## ACTIVE FORESHADOWING",
  "## NEXT CHAPTER TARGET",
  "## NOTES FOR AI — CURRENT SESSION",
]
```

### 3.4 Path resolution

`load_config()` resolves relative paths against the config file's directory. All paths in `pipeline_config.toml` must be relative to `fiction_loop/tools/`. Double-dot prefixes navigate up to the fiction_loop root.

---

## 4. invoke_writer.py — CONTRACT SPEC

**Location:** `fiction_loop/tools/invoke_writer.py`

### CLI interface

```
PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py
  --prompt   PATH    # assembled_prompt.md (required)
  --config   PATH    # pipeline_config.toml (required)
  --output   PATH    # where to write chapter_draft.md (required)
  --ignore-cost-limit  # flag, passed through to call_api
```

### Module boundary

```python
# imports (all from src/ via PYTHONPATH=src)
from novel_pipeline.config   import load_config
from novel_pipeline.api      import call_api
from novel_pipeline.exceptions import (
    ContextOverflowError, CostLimitError,
    ChapterValidationError, APIResponseError, APIRateLimitError,
)
from llm.factory  import create_transport
from llm.env      import resolve_from_env
```

### Function contracts

```python
def build_messages(assembled_prompt: str, config: dict) -> list[dict]:
    """
    Build the messages list for call_api.

    Input:
      assembled_prompt — full text of assembled_prompt.md
      config           — loaded config dict

    Returns:
      [
        {"role": "system", "content": config["system_prompt_generate_chapter"]},
        {"role": "user",   "content": assembled_prompt},
      ]

    Never raises.
    """

def validate_word_count(text: str, min_words: int) -> None:
    """
    Raise ChapterValidationError if len(text.split()) < min_words.
    """

def main() -> None:
    """
    Entry point. Exits 0 on success, 1 on any error.
    All errors print a human-readable message to stderr before exiting.
    """
```

### Execution sequence

```
1.  parse_args()
2.  config = load_config(args.config)
3.  env    = resolve_from_env()
4.  config = {**config, **{k: v for k, v in env.items() if k in config}}
5.  transport = create_transport(
        api_key=config.get("api_key"),
        model=config["model"],
        api_url=config.get("api_url"),
        max_retries=config["max_retries"],
        backoff_seconds=tuple(config["retry_backoff_seconds"]),
        jitter_max=config["retry_jitter_seconds_max"],
    )
6.  assembled = Path(args.prompt).read_text(encoding="utf-8")
7.  messages  = build_messages(assembled, config)
8.  chapter   = call_api(
        messages,
        config["model"],
        config,
        client=transport,
        timeout=config.get("timeout_seconds"),
        expected_output_tokens=config.get("expected_output_tokens_chapter"),
        ignore_cost_limit=args.ignore_cost_limit,
        task_label="generate_chapter",
    )
9.  validate_word_count(chapter, int(config.get("min_chapter_words", 2000)))
10. Path(args.output).write_text(chapter, encoding="utf-8")
11. print(f"OK: {len(chapter.split())} words → {args.output}", file=sys.stderr)
12. sys.exit(0)
```

### Error exits

| Condition | stderr message | exit code |
|---|---|---|
| `ContextOverflowError` | Full exception text (includes token breakdown by document) | 1 |
| `CostLimitError` | Full exception text (includes current spend + limit) | 1 |
| `APIRateLimitError` | "Rate limit: {e}. All retries exhausted." | 1 |
| `APIResponseError` | "API error: {e}" | 1 |
| `ChapterValidationError` | Full exception text | 1 |
| `ConfigError` | "Config error: {e}" | 1 |
| `LLMConfigError` | "LLM config error: {e}. Check BOOKGEN_LLM_API_KEY." | 1 |
| `FileNotFoundError` (prompt) | "assembled_prompt.md not found at {path}. Run Assembler first." | 1 |
| `FileNotFoundError` (config) | "Config not found: {path}" | 1 |
| Any unexpected exception | "Unexpected error: {traceback}" | 1 |

### Business logic rules

- `static_docs` and `living_doc` args to `call_api()` are both `None` — the assembled_prompt.md is self-contained. Token overflow errors will not include per-document breakdown; this is acceptable because the entire prompt is a single document.
- If `api_default_max_tokens_chapter` is set in config, `call_api()` uses it as `max_tokens` in the API payload. Always set this to give the model room to reach 2000–3000 words.
- `call_api()` handles transport-level retries internally via the injected transport. `invoke_writer.py` does NOT implement retry logic.
- Cost is tracked to `config["spend_file_path"]` inside `call_api()`. `invoke_writer.py` does not call `track_spend()` directly.

### Edge cases

| Scenario | Behaviour |
|---|---|
| `assembled_prompt.md` is empty | `call_api()` will send an empty user message. The model will likely produce a short or confused response. `validate_word_count()` will catch this. Exit 1. |
| Output path parent directory does not exist | `Path.write_text()` raises `FileNotFoundError`. Propagates as unexpected error. Output dir should always be `fiction_loop/prompts/` which exists. |
| Output path already exists | Overwrite silently. Orchestrator always reads the latest file. |
| `pipeline_config.toml` has wrong `context_limit` for the model | `call_api()` will not catch this — it trusts the config. If `context_limit` is set too high, the overflow guard will never fire even when the model's true limit is exceeded. Set `context_limit` to the model's actual documented context window. |
| API key missing from env | `create_transport()` raises `LLMConfigError`. Exit 1 with "Check BOOKGEN_LLM_API_KEY." |
| Model returns `finish_reason="content_filter"` | `call_api()` raises `APIResponseError`. Exit 1. assembled_prompt.md likely contains content the model refuses. Orchestrator must flag for human review. |

---

## 5. refresh_living_doc.py — CONTRACT SPEC

**Location:** `fiction_loop/tools/refresh_living_doc.py`

**Purpose:** After a chapter is approved, use the LLM to update `fiction_loop/core/living_document.md` to reflect new story state. Uses `request_living_doc_update()` from `src/novel_pipeline/requests_.py`.

**When called:** Orchestrator calls this AFTER the structural gate passes (step 11.5) and BEFORE the Updater (step 12).

This step is optional but recommended. If skipped, living_document.md will drift from story state until manually updated.

### CLI interface

```
PYTHONPATH=src .venv/bin/python fiction_loop/tools/refresh_living_doc.py
  --chapter   PATH   # the approved chapter file (e.g. fiction_loop/chapters/chapter_001.md)
  --config    PATH   # pipeline_config.toml
  --ignore-cost-limit  # optional flag
```

The script overwrites `config["living_doc_path"]` in place (i.e. `fiction_loop/core/living_document.md`).

### Module boundary

```python
from novel_pipeline.config     import load_config
from novel_pipeline.requests_  import request_living_doc_update
from novel_pipeline.exceptions import (
    LivingDocValidationError, APIResponseError,
    ContextOverflowError, CostLimitError,
)
from novel_pipeline.docs       import load_static_docs, load_living_doc, save_living_doc
from llm.factory               import create_transport
from llm.env                   import resolve_from_env
```

### Execution sequence

```
1.  parse_args()
2.  config    = load_config(args.config)
3.  env       = resolve_from_env()
4.  config    = {**config, **{k: v for k, v in env.items() if k in config}}
5.  transport = create_transport(...)  # same as invoke_writer.py
6.  static_docs = {}
    IF config["static_doc_paths"] is non-empty:
      static_docs = load_static_docs(config["static_doc_paths"])
    ELSE:
      Load manually:
        static_docs = {
          "world_rules":    Path("fiction_loop/core/world_rules.md").read_text(),
          "style_contract": Path("fiction_loop/core/style_contract.md").read_text(),
          "curriculum":     Path("fiction_loop/core/concept_curriculum.md").read_text(),
        }
7.  living_doc  = load_living_doc(config["living_doc_path"])
8.  chapter_text = Path(args.chapter).read_text(encoding="utf-8")
9.  new_living = request_living_doc_update(
        static_docs,
        living_doc,
        chapter_text,
        config["model"],
        config,
        client=transport,
        timeout=config.get("timeout_seconds"),
        ignore_cost_limit=args.ignore_cost_limit,
    )
    # request_living_doc_update validates required_living_doc_sections.
    # Raises LivingDocValidationError if any section is missing or out of order.
10. save_living_doc(config["living_doc_path"], new_living, config)
    # save_living_doc writes atomically (backup then overwrite, per I7).
11. print("OK: living_document.md updated.", file=sys.stderr)
12. sys.exit(0)
```

### Static docs for the living doc update

`request_living_doc_update()` wraps `static_docs` + `living_doc` + chapter text into a prompt using `build_prompt(task="update_living_doc")`. For this to work correctly, `static_doc_paths` in `pipeline_config.toml` should point to fiction_loop's core documents:

```toml
static_doc_paths = [
  "../core/world_rules.md",
  "../core/style_contract.md",
  "../core/concept_curriculum.md",
]

static_doc_order = ["world_rules", "style_contract", "concept_curriculum"]
```

The keys in the `static_docs` dict are derived from the filenames without extension. `build_prompt()` uses `static_doc_order` to set inclusion order.

Note: `static_doc_paths` is shared between `invoke_writer.py` and `refresh_living_doc.py`. In `invoke_writer.py`, static_docs are not used (messages are built manually). In `refresh_living_doc.py` they are loaded and passed to `build_prompt()`. Having them in config is correct in both cases.

### Error exits

| Condition | stderr message | exit code |
|---|---|---|
| `LivingDocValidationError` | Full text including missing sections and diff | 1 |
| `ContextOverflowError` | Token breakdown | 1 |
| `CostLimitError` | Current spend + limit | 1 |
| `APIResponseError` | API error text | 1 |
| `FileNotFoundError` (chapter) | "Chapter not found: {path}" | 1 |
| `FileNotFoundError` (living_doc) | "living_document.md not found: {path}" | 1 |

### Edge cases

| Scenario | Behaviour |
|---|---|
| `living_document.md` is empty | `load_living_doc()` returns empty string. `build_prompt()` replaces with `"(empty — first chapter)"`. Update will produce a fresh living_doc from the chapter content alone. Acceptable on first run. |
| Validation fails with missing section | `LivingDocValidationError` carries `missing` list and a unified diff. Print to stderr. Do NOT overwrite living_document.md with invalid content. Orchestrator should alert user and offer retry. |
| Chapter file is the draft path (not promoted yet) | Acceptable — Orchestrator may call refresh after saving draft but before final promotion. The chapter content is what matters. |
| `save_living_doc()` creates a `.bak.{ts}` backup | Expected behaviour per config `living_doc_backup_format`. Backup files accumulate in the same directory as `living_document.md`. |

---

## 6. HOW ORCHESTRATOR INTEGRATES THE TOOLS

Orchestrator step 8 (Writer), step 9, step 11 (Extractor), step 11.5
(structural gate), and step 10 (refresh; step labels retained):

```
8. Run Writer bridge:
    PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py \
      --prompt fiction_loop/prompts/assembled_prompt.md \
      --config fiction_loop/tools/pipeline_config.toml \
      --output fiction_loop/prompts/chapter_draft.md

    Check exit code:
      0 → proceed to step 9
      1 → read stderr for error type:
          ContextOverflowError → ask Assembler to trim assembled_prompt.md, retry
          CostLimitError       → alert user, wait for --ignore-cost-limit confirmation
          ChapterValidationError (too short) → retry once, then alert user
          Any other error      → alert user, do not continue

9. Read chapter_draft.md
    Save chapter to /chapters/chapter_[NNN].md

11. Run Extractor to write update_brief.json.

11.5. Run the deterministic structural gate:
    .venv/bin/python fiction_loop/tools/structural_gate.py

    Check exit code:
      0 → proceed to step 10 (Living Doc refresh).
      1 → stop; no paid refresh or state mutation has run.

10. Run Living Doc refresh bridge:
    PYTHONPATH=src .venv/bin/python fiction_loop/tools/refresh_living_doc.py \
      --chapter fiction_loop/chapters/chapter_[NNN].md \
      --config fiction_loop/tools/pipeline_config.toml

    Check exit code:
      0 → living_document.md updated. Proceed to step 12 (Updater).
      1 → alert user. living_document.md is unchanged (stale).
          Orchestrator may continue with stale doc or abort.
          If continuing stale: note in status report that living_doc was not updated.
```

---

## 7. ENVIRONMENT VARIABLES

`llm.env.resolve_from_env()` reads these (set in `.env` at project root or shell environment):

| Variable | Purpose | Required |
|---|---|---|
| `BOOKGEN_LLM_API_KEY` | API key — any OpenAI-compatible provider (project-owned name, renamed 2026-07 in T-003) | Yes |
| `BOOKGEN_LLM_API_URL` | Endpoint override for non-OpenRouter OpenAI-compatible providers | No |
| `BOOKGEN_LLM_PROVIDER` | Transport to use (default: `openrouter`) | No |
| `BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS` | Overrides `timeout_seconds` in config | No |
| `NOVEL_MODEL` | Overrides `model` in config | No |

Both bridge scripts load the repo-root `.env` as a **fallback** at startup
(`_load_dotenv_fallback()`): any `KEY=VALUE` line is applied only if that variable is
not already in the shell environment — shell env always wins. This mirrors the
codebase's existing entry-point convention (`menu.py` and `src/settings.py` both call
`load_dotenv()` for their flows). So for normal use nothing needs exporting; exported
variables override the file when present.

---

## 8. COST AND SPEND TRACKING

Both scripts inherit cost tracking from `call_api()` and `request_living_doc_update()`. All spend is appended to `config["spend_file_path"]` (set to `fiction_loop/state/.pipeline_spend.json` in `pipeline_config.toml`).

fiction_loop's spend file is separate from the novel_pipeline spend file. Do not point both at the same path.

`call_api()` enforces:
- `cost_limit_usd_per_session` — cumulative cost in the current process run
- `cost_limit_usd_total` — cumulative lifetime cost from the spend file

A chapter generation call (invoke_writer) and a living_doc refresh call (refresh_living_doc) both count against the same session and lifetime limits when run in the same process or share the same spend file.

---

## 9. TOKEN COUNTING

`call_api()` uses tiktoken encoding for token counting. The fallback is `cl100k_base` (compatible with most OpenRouter models). If the target model uses a different tokenizer, set:

```toml
tokenizer_encoding_fallback = "cl100k_base"  # already the default
```

For Claude models via OpenRouter, `cl100k_base` is a reasonable approximation. Set `context_safety_margin` conservatively (default 8000 tokens) to compensate for any counting inaccuracy.

---

## 10. DIRECTORY SETUP

Before running the scripts for the first time, ensure these directories exist (scripts do not create them):

```
fiction_loop/chapters/         — output_dir for promoted chapters
fiction_loop/logs/             — log_path parent
fiction_loop/state/            — spend_file_path and state_file_path parent
fiction_loop/prompts/          — assembled_prompt.md and chapter_draft.md live here
```

`fiction_loop/prompts/` and `fiction_loop/state/` already exist. Create `fiction_loop/chapters/` and `fiction_loop/logs/` before first run:

```bash
mkdir -p fiction_loop/chapters fiction_loop/logs
```
