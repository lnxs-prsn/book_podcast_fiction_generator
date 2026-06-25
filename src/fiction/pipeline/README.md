# novel-pipeline

A CLI for running a pedagogical-novel writing pipeline against OpenRouter. Automates the manual loop of: load templates → request chapter → approve → request living-doc update → save → repeat until session budget is hit → exit.

Modular, stateless-API, atomic writes, cost-gated, token-gated, approval-gated.

## Install

From the project root:

```bash
cd src
uv sync
```

Python 3.14+. Requires `requests`, `tiktoken`, `python-docx`.

## Quick start

```bash
cd /path/to/harnessv7_migrated/src
export OPENROUTER_API_KEY=sk-or-...
cp fiction/pipeline/config.example.toml fiction/pipeline/config.toml
# edit model, prices, and any paths to match your project
uv run python cli/fiction.py --config fiction/pipeline/config.toml
```

Subsequent sessions:

```bash
uv run python cli/fiction.py --config fiction/pipeline/config.toml --resume
```

## Flags

| Flag | Meaning |
|---|---|
| `--config PATH` | TOML config (required) |
| `--resume` | Continue from existing chapters; detects interrupt-mid-cycle |
| `--chapter-start N` | Force the next chapter number; warns on skipped gaps |
| `--auto-approve` | Skip all interactive prompts (use with care) |
| `--dry-run` | Run the loop without writing files or calling the API |
| `--ignore-cost-limit` | Bypass session/lifetime cost gates |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | user abort / KeyboardInterrupt / cost limit hit / rejection limit reached |
| 2 | config error, `ResumeStateError`, or `PromotionCollisionError` (state drift) |
| 3 | API error after retries / context overflow / unexpected error |

## File layout produced

```
data/fiction/
  chapters/
    chapter_01.md                # approved chapters only
    chapter_02.md
    .rejected/
      chapter_03__20260515T142301Z.md    # rejected drafts, kept as audit trail
  pipeline.log                   # JSONL events
  .pipeline_spend.json           # session + lifetime spend
  .pipeline_state.json           # last promoted / last doc-updated / last drafted

src/fiction/pipeline/
  living_doc.md                  # mutable per-novel state (project-specific)
  living_doc.md.bak.{timestamp}  # one backup per save, kept indefinitely
```

## How the cycle works

For each chapter slot in `chapters_per_session`:

1. Call OpenRouter for the chapter, with `max_tokens` set so truncation surfaces as a hard error rather than a silently short chapter.
2. Save the draft to `.rejected/` immediately. Track `last_chapter_drafted` in the state file.
3. Show the human the path + word count + first 200 chars. Approve `[y/n/q]`.
4. On `y`: `os.replace` the draft into `chapter_NN.md` (canonical). If the target already exists, the pipeline aborts with `PromotionCollisionError` rather than silently writing a duplicate the state layer cannot see.
5. Atomic state-file update: `last_chapter_promoted = N`.
6. Call OpenRouter for the living-doc update.
7. Validate that all required headers appear in the right order; on failure, show a diff and offer retry / keep old / abort.
8. Atomic save of the new living doc (with timestamped `.bak`).
9. Atomic state-file update: `last_chapter_living_doc_updated = N`.

If a chapter is rejected, the loop retries up to `max_rejection_retries` times (default 5). Beyond that, the pipeline stops with `RejectionLimitReachedError` to prevent runaway spend.

If the human picks "keep old living doc" after a failed update, the session stops immediately rather than rolling forward with stale narrative context.

Interruption at any point is recoverable. On `--resume`:

- `find_next_chapter_number` scans `output_dir` and returns the first gap (or `max+1`).
- `detect_resume_state` compares the filesystem to `.pipeline_state.json`. If `last_promoted > last_doc_updated`, the user is offered: regenerate the living doc from the orphaned chapter, continue with a stale living doc, or abort. Under `--auto-approve` this prompt is **refused** (would silently spend money), and the run aborts with a clear message asking to drop `--auto-approve` for the recovery.
- Unpromoted drafts in `.rejected/` for the next chapter are surfaced so you can recover work manually.

## Safety guarantees

- **No silent fresh-starts.** If `output_dir` already has chapters and you forget `--resume`, the pipeline aborts with instructions.
- **No silent first-run trap.** If both `output_dir` and the living doc are empty, the pipeline aborts before any API call and asks you to seed the living doc with the required section headers. (Otherwise the very first living-doc-update would fail validation *after* you've already paid for a chapter generation.)
- **No silent truncation.** Every API call sends `max_tokens` and checks `finish_reason`. If the model hits the token limit, the result is rejected with `ChapterValidationError("finish_reason='length'")` rather than promoted as a too-short chapter.
- **No silent context-truncation.** A prompt that would exceed `context_limit - safety_margin` raises `ContextOverflowError` with a per-document token breakdown. Token counting accounts for chat-template overhead (~4 tokens per message plus ~3 priming tokens, both configurable).
- **No silent cost overruns.** Both pre-flight (estimated) and post-call (actual `usage`) are gated against session + lifetime limits.
- **No silent gap-skips under auto-approve.** `--chapter-start N` combined with `--auto-approve` refuses to skip missing chapters; you must drop `--auto-approve` to confirm the skip interactively.
- **No silent expensive recovery under auto-approve.** Inconsistent resume state combined with `--auto-approve` refuses to auto-pick the "regenerate" option (which would call the API); you must drop `--auto-approve` for the recovery prompt.
- **No silent narrative drift.** When the human picks "keep old living doc" after a failed update, the session stops; the next chapter would otherwise generate against stale context.
- **No silent promotion collisions.** If a canonical chapter already exists where a draft would be promoted, the pipeline raises `PromotionCollisionError` instead of writing a timestamped duplicate that the regex/state layer cannot see.
- **No structural drift in the living doc.** Required headers (configurable) are checked after every update; failure surfaces a diff before any write.
- **Bounded rejection loop.** The rejection-retry loop is iterative (not recursive) and capped at `max_rejection_retries` to prevent stack overflow and runaway spend.
- **Drafts always survive.** Rejected drafts stay in `.rejected/` indefinitely as an audit trail. Approved chapters move via `os.replace` (atomic on POSIX).

## Configuration

See `config.example.toml`. Required keys:

- `model` — OpenRouter model slug
- `static_doc_paths` — list of template files (`.md`, `.txt`, `.markdown`, or `.docx`)
- `living_doc_path` — the mutable per-novel state file
- `output_dir` — where canonical chapters go
- `context_limit` — model context window in tokens
- `price_per_1m_input_tokens` / `price_per_1m_output_tokens` — for cost gating

### Advanced / formerly-hardcoded knobs

Almost every previously-hardcoded detail is now overridable in the TOML config (defaults preserve v0.2 behaviour). See `config.example.toml` for the full annotated list. Highlights:

| Key | Default | Purpose |
|---|---|---|
| `temperature` / `top_p` / `seed` | unset | Creativity controls; only included in API payload when set |
| `api_default_max_tokens_chapter` / `_update` | follows `expected_output_tokens_*` | Explicit `max_tokens` override |
| `max_rejection_retries` | 5 | Cap on the regenerate-after-reject loop |
| `system_prompt_generate_chapter` | hardcoded default | Override the chapter-generation system prompt |
| `system_prompt_update_living_doc` | hardcoded default | Override the living-doc-update system prompt |
| `doc_wrap_open_format` / `_close_format` | `=== {name_upper} ===` etc. | Document section wrapping |
| `static_doc_order` | `["world_laws", "curriculum", "style_contract", "full_map"]` | Concatenation order in the prompt |
| `tokenizer_encoding_fallback` | `cl100k_base` | Tiktoken fallback encoder |
| `tokenizer_chars_per_token` | 4 | Heuristic when tiktoken can't load at all |
| `token_count_per_message_overhead` | 4 | Per-message token overhead in counting |
| `token_count_completion_priming` | 3 | Completion priming overhead |
| `retry_backoff_seconds` | `[2, 8, 32]` | Exponential backoff schedule |
| `retry_jitter_seconds_max` | 2.0 | Random jitter upper bound added to each backoff |
| `living_doc_backup_format` | `{name}.bak.{ts}` | Backup file naming template |
| `rejected_draft_name_format` | `chapter_{nn:02d}__{ts}.md` | Staged-draft naming template |
| `canonical_chapter_regex` | `^chapter_(\d{2,})\.md$` | Regex matching canonical chapters in `output_dir` |
| `canonical_chapter_name_format` | `chapter_{nn:02d}.md` | Format used when promoting drafts |
| `dry_run_chapter_template` | `Lorem ipsum dolor sit amet. ` | Repeated to size the dry-run placeholder |

## Module layout

```
novel_pipeline/
  __init__.py        # public exports
  __main__.py        # python -m novel_pipeline
  cli.py             # argparse + exit-code mapping
  config.py          # TOML load, defaults, env overrides, validation
  session.py         # run_session: the conductor
  requests_.py       # request_chapter / request_living_doc_update
  api.py             # call_api: retries, pre-flight, cost gate, finish_reason
  prompts.py         # build_prompt (config-driven prompts + wrap formats)
  docs.py            # load/save docs, draft staging, promote, validation
  state.py           # .pipeline_state.json, find_next_chapter_number,
                     # detect_resume_state (+ optional last_chapter_drafted)
  cost.py            # estimate_cost, track_spend
  tokens.py          # count_tokens (tiktoken + configurable fallback)
  logging_.py        # JSONL event log
  exceptions.py      # PipelineError + subclasses
```

## Limitations

- v1 only supports `.md`, `.txt`, `.markdown`, `.docx` for static docs. PDFs raise `DocumentLoadError` with a remediation hint.
- Token counting falls back to a chars-per-token heuristic if tiktoken cannot load at all. The spec accepts ±10% variance.
- Backups of the living doc are kept indefinitely. Disk usage grows linearly in the number of approved chapters.
- Cost tracking uses the configured per-1M prices for both pre-flight and post-call accounting. Provider-side cached-token discounts are not modelled — recorded spend is therefore an upper bound on what you'll actually be billed.
- The pipeline is single-user, single-shell by design. Two concurrent invocations against the same `output_dir` will race on `.pipeline_state.json`.
- Log files (`pipeline.log`) are append-only; use external `logrotate` if size matters.
- Context-window saturation halts the pipeline loudly with a per-doc breakdown rather than auto-compressing — automatic compression would corrupt pedagogical tracking.
