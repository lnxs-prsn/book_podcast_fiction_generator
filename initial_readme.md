# Harness V3 — Comprehensive Project Reference

> This document is the authoritative source of truth for AI sessions and developers.
> It describes everything: architecture, data flow, modules, config keys, CLIs, APIs.
> Written from source code on 2026-06-06. Audited and corrected against source on 2026-06-06. Updated for Phase 7 (cleanup) on 2026-06-12. Update it when code changes.

---

## What This Project Is

**Harness V3** is a multi-format automated learning pipeline that transforms books into three parallel educational outputs:

1. **Podcast scripts** — dialogue-style scripts between hosts, plus synthesized MP3 audio
2. **Pedagogical fiction** — Xianxia-style cultivation novels that teach book concepts through narrative
3. **Seed projects** — scaffolded starting points for new fiction pipelines

All three outputs are **siblings** — each reads independently from the same source material. No pipeline feeds another.

The workflow is: take a textbook PDF → split into chapter PDFs → run any/all of the three output pipelines.

---

## Repository Structure

```
harnessv3/
├── initial_readme.md              ← THIS FILE (authoritative reference)
├── vision.md                      ← High-level project vision
├── pipeline.log                   ← Top-level run log
├── podcast_friendly_user_guide.md ← User-facing guide for podcast pipeline
│
├── data/
│   ├── chapters/                  ← Input: individual chapter PDFs (after slicing)
│   ├── output/
│   │   ├── scripts/               ← Podcast scripts (.txt)
│   │   └── audio/                 ← MP3s, nested by chapter stem
│   └── neon_sprawl/               ← Live example novel run
│       ├── config.toml
│       ├── living_doc.md
│       └── chapters/
│
├── src/                           ← All source code (git submodule)
│   ├── config.json                ← LLM provider + voice config
│   ├── pyproject.toml             ← Workspace pyproject
│   ├── README.md                  ← Submodule README
│   ├── run_book.py                ← Backward-compat shim → cli/podcast.py
│   ├── run_chapter.py             ← Backward-compat shim → cli/podcast.py
│   │
│   ├── cli/
│   │   ├── podcast.py             ← Primary podcast pipeline CLI (use this)
│   │   └── fiction.py             ← Primary fiction pipeline CLI (use this)
│   │
│   ├── slicer/
│   │   └── pdf_splitter.py        ← 4-stage PDF chapter splitter
│   │
│   ├── pdfslicer/                 ← Alternative/legacy slicer (separate from slicer/)
│   │
│   ├── tts/
│   │   ├── cli.py                 ← WaveSpeed VibeVoice TTS client
│   │   ├── recover.py             ← Recover killed TTS jobs
│   │   └── howtouse.md
│   │
│   ├── podcast_script_generator/
│   │   └── llm/
│   │       ├── call_api.py        ← OpenRouter LLM call
│   │       ├── extract_pdf.py     ← PyMuPDF text extraction
│   │       ├── parse_output.py    ← Script parser / file-list extractor
│   │       ├── save_output.py     ← Output writer
│   │       ├── read_prompt.py     ← Prompt loader
│   │       ├── parse_args.py      ← CLI argument parsing
│   │       ├── test_all.py        ← Module tests
│   │       └── main.py            ← Module entry
│   │
│   ├── phases/                    ← Development phase logs (phase_01/ … phase_07/ directories)
│   │   └── structure.md
│   │
│   └── fiction/
│       ├── run_simple.py          ← Standalone novel runner (simple, no gates)
│       │
│       ├── seed_gen/              ← Interactive seed project generator
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── cli.py
│       │   ├── prompts/           ← LLM prompt templates (pass1_genres.txt, pass2_files.txt)
│       │   └── templates/         ← Reference template files used as LLM context
│       │
│       └── pipeline/              ← novel-pipeline (full production novel writer)
│           ├── pyproject.toml
│           ├── config.toml        ← Active config (neon_sprawl example)
│           ├── config.example.toml
│           ├── living_doc.md      ← Mutable narrative state
│           │
│           ├── novel_pipeline/    ← Python package
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── cli.py
│           │   ├── config.py
│           │   ├── session.py
│           │   ├── requests_.py
│           │   ├── api.py
│           │   ├── prompts.py
│           │   ├── docs.py
│           │   ├── state.py
│           │   ├── cost.py
│           │   ├── tokens.py
│           │   ├── logging_.py
│           │   └── exceptions.py
│           │
│           ├── tests/
│           │   └── test_pipeline.py
│           │
│           └── templates/         ← Static world-building documents
│               ├── world_laws.md
│               ├── curriculum.md
│               ├── style_contract.md
│               ├── full_map.md
│               └── living_doc.md
│
├── docs/                          ← Project documentation
│   ├── fiction/
│   │   ├── fiction_pipe.md
│   │   ├── build_specs.md
│   │   ├── directive_templates/
│   │   └── directive_templates_polya/
│   └── ...                        (animation_design.md, claude_prompt.md, log.md, etc.)
│
├── books/                         ← Source PDF books
├── decide_later/                  ← Staging area for undecided files
└── "System design cultivation idea/"
```

---

## Pipeline A: PDF-to-Podcast

### What It Does

Takes a chapter PDF → extracts text → LLM writes a podcast dialogue script → WaveSpeed synthesizes multi-speaker MP3.

### Entry Points

**Invocation convention:** all Python runs require `PYTHONPATH=src` so modules resolve correctly. Do NOT add `sys.path` hacks inside scripts — use the env prefix instead:

```bash
PYTHONPATH=src python src/cli/podcast.py [OPTIONS]
```

**Primary CLI:** `src/cli/podcast.py`

This is the unified entry point for all podcast pipeline operations (single chapter and full book). Always prefer this over the legacy shims.

```bash
# Single chapter
PYTHONPATH=src python src/cli/podcast.py <chapter.pdf> [OPTIONS]

# Full book (slice + batch)
PYTHONPATH=src python src/cli/podcast.py --book whole.pdf [OPTIONS]
```

**Primary fiction CLI:** `src/cli/fiction.py`

Unified entry point for the fiction/novel pipeline.

**Backward-compat shims** — `src/run_chapter.py` and `src/run_book.py` are thin shims that forward to `cli.podcast.main`. They exist for backward compatibility only; new code and documentation should reference `src/cli/podcast.py` directly.

```python
# Both shims contain only:
from cli.podcast import main
if __name__ == "__main__":
    main()
```

**Script generation note:** LLM (OpenRouter) is the only script generation path. There is no local/offline generator mode. `OPENROUTER_API_KEY` is required for all script generation.

**Single chapter options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--skip-audio` | off | Skip TTS, produce script only |
| `--mode MODE` | `2person` | Script style (see Modes below) |
| `--context "..."` | — | Extra context injected into prompt |
| `--context-file file.txt` | — | Load context from file |
| `--fiction-dir ./` | — | Path to fiction pipeline output (for `fiction_meta` mode) |

**Full book (batch) options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--book whole.pdf` | — | Source PDF; triggers PDF slicing first |
| `--toc-page N` | — | TOC page number (required with `--book`) |
| `--no-ocr` | off | Skip OCR fallback in slicer |
| `--slice-only` | off | Only slice PDF, don't run podcast pipeline |
| `--skip-audio` | off | Skip TTS |
| `--mode MODE` | `2person` | Script style |
| `--force` | off | Reprocess chapters that already have output |

### Script Modes

| Mode | Speakers | Description | Batch? |
|------|----------|-------------|--------|
| `2person` | HOST (Alex) + EXPERT (Jordan) | 4000-word technical deep-dive, ~30 min | yes |
| `4person` | 4 voices | Debate format | yes |
| `code` | 2 voices | Engineering *why* focus | yes |
| `realworld` | 2 voices | Connects to user-supplied current event | yes |
| `fiction_meta` | 2 voices | Meta-commentary on fiction chapter output | **no** (run_chapter.py only) |

### Speaker Normalization

`run_chapter.py` normalizes script speaker labels before saving:
- `ALEX` / `JORDAN` → `Speaker 0` / `Speaker 1`
- `HOST` / `EXPERT` / `GUEST` → `Speaker 0` / `Speaker 1`
- `CRITIC` → `Speaker 2`, `NEWCOMER` → `Speaker 3`
- Markdown-bold variants handled (`**ALEX:**`, `**Speaker 0:**`, etc.)
- Standalone speaker label lines merged with following content line
- Lines that don't match `Speaker N:` after normalization are **dropped** (headers, word-count notes, noise)

### Data Flow

```
chapter.pdf
  ↓ extract_pdf.py (PyMuPDF)
raw text
  ↓ call_api.py (OpenRouter)
podcast script (.txt) → data/output/scripts/<stem>_podcast.txt
  ↓ tts/cli.py (WaveSpeed VibeVoice)
MP3 → data/output/audio/<stem>/1.mp3
```

### Output Files

- `data/output/scripts/<chapter_stem>_podcast.txt` — dialogue script
- `data/output/audio/<chapter_stem>/1.mp3` — synthesized audio
- `data/output/audio/<chapter_stem>/tts_job.json` — job ID for recovery

### TTS Recovery

If a TTS job is killed mid-synthesis:
```bash
python src/tts/recover.py data/output/audio/<stem>/tts_job.json
```
This uses the saved `request_id` to poll WaveSpeed and download the result.

---

## Pipeline B: PDF Splitter

### What It Does

Splits a whole-book PDF into individual chapter PDFs using a 4-stage TOC extraction strategy.

### Module

`src/slicer/pdf_splitter.py`

### 4-Stage TOC Extraction

1. **Stage 1** — PDF internal bookmarks (`PyMuPDF.get_toc()`)
2. **Stage 2** — Text extraction from specified TOC page number
3. **Stage 3** — OCR fallback (`pdf2image` + `pytesseract`) if text extraction fails
4. **Stage 4** — LLM analysis via OpenRouter (if `OPENROUTER_API_KEY` is set)

### TOC Parsing Patterns Recognized

- `Chapter 1: Title . . . . 42`
- `Chapter 1: Title   42` (multiple spaces)
- `1. Title 42`

### Python API

```python
from pdf_splitter import run_splitter
run_splitter(
    input_path="book.pdf",      # NOTE: parameter is input_path, not pdf_path
    output_dir="data/chapters/",
    toc_page=8,                 # 1-indexed TOC page
    prefix="chapter",           # filename prefix (default: "chapter")
    level=1,                    # TOC depth to extract (default: 1)
    no_ocr=False,
    dry_run=False,
    chapters_only=True,         # drop front matter, start at Chapter 1
    verbose=False,
    ocr_embed=False,            # OCR-embed scanned pages into output PDFs
)
```

Returns `{"success": bool, "source": str, "toc": [...], "files": [...], "output_dir": str, "dry_run": bool}`.

### Output

Individual chapter PDFs: `data/chapters/<N>_<sanitized_title>.pdf`

Only level-1 TOC entries are extracted (chapter level). Front matter is dropped.

---

## Pipeline C: Novel-Pipeline (Pedagogical Fiction)

### What It Does

A production-grade multi-chapter pedagogical novel writer with:
- Human approval gates per chapter
- Cost tracking and pre-flight estimation
- Resume on interrupt
- Atomic writes and collision prevention
- Bounded rejection loops
- Comprehensive state management

### Entry Point

```bash
cd src/fiction/pipeline
python -m novel_pipeline --config config.toml [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--config path` | Path to TOML config (required) |
| `--resume` | Resume from interrupted session |
| `--auto-approve` | Skip human approval gates |
| `--dry-run` | Test config/prompts without API calls |
| `--chapter-start N` | Start from chapter N; prompts for confirmation when it differs from the natural next chapter; **blocked under `--auto-approve` if it would skip gaps** |
| `--ignore-cost-limit` | Bypass cost gates |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User abort / KeyboardInterrupt / cost limit reached / rejection limit reached |
| 2 | Config error / document load error / resume state error / promotion collision |
| 3 | API error after retries / context overflow / unexpected error |

### config.toml Reference

```toml
# --- Required ---
model = "openrouter/free"               # Any OpenAI-compatible model string
context_limit = 200000                  # Model context window (tokens)
price_per_1m_input_tokens = 0.001       # USD per 1M input tokens
price_per_1m_output_tokens = 0.001      # USD per 1M output tokens
static_doc_paths = [                    # Templates loaded read-only each session
    "./templates/world_laws.md",
    "./templates/curriculum.md",
    "./templates/style_contract.md",
    "./templates/full_map.md",
]
living_doc_path = "./living_doc.md"     # Mutable narrative state file
output_dir = "./chapters"               # Where canonical chapters go

# --- Optional with defaults ---
context_safety_margin = 8000            # Token buffer before overflow error
chapters_per_session = 3                # Chapters to write per invocation
max_rejection_retries = 5               # Max rejections before session aborts
min_chapter_words = 1500                # Minimum word count; shorter chapters rejected
max_retries = 3                         # API call retry attempts
timeout_seconds = 120                   # HTTP timeout per API call
cost_limit_usd_per_session = 5.00       # Per-session spend cap (USD)
cost_limit_usd_total = 50.00            # Lifetime spend cap (USD)
expected_output_tokens_chapter = 4000   # Pre-flight estimate for chapters
expected_output_tokens_update = 2000    # Pre-flight estimate for living_doc updates
log_path = "./pipeline.log"
state_file_path = "./.pipeline_state.json"
spend_file_path = "./.pipeline_spend.json"
required_living_doc_sections = [...]    # Section headers that must exist in living_doc

# --- Optional format overrides ---
# static_doc_order = ["world_laws", "curriculum", "style_contract", "full_map"]
# doc_wrap_open_format  = "=== {name_upper} ==="
# doc_wrap_close_format = "=== END {name_upper} ==="
# canonical_chapter_regex      = "^chapter_(\\d{2,})\\.md$"
# canonical_chapter_name_format = "chapter_{nn:02d}.md"
# rejected_draft_name_format   = "chapter_{nn:02d}__{ts}.md"
# living_doc_backup_format     = "{name}.bak.{ts}"

# --- Optional retry tuning ---
# retry_backoff_seconds     = [2, 8, 32]
# retry_jitter_seconds_max  = 2.0

# --- Optional tokenizer tuning ---
# tokenizer_encoding_fallback = "cl100k_base"
# tokenizer_chars_per_token   = 4
# token_count_per_message_overhead = 4
# token_count_completion_priming   = 3

# --- Optional per-call token caps ---
# api_default_max_tokens_chapter = 4000
# api_default_max_tokens_update  = 2000

# --- Optional creativity controls ---
# temperature = 0.7
# top_p = 1.0
# seed = 42

# --- Optional prompt overrides ---
# system_prompt_generate_chapter = "You are..."
# system_prompt_update_living_doc = "You are..."
```

**Environment variable overrides:**

| Var | Overrides |
|-----|-----------|
| `OPENROUTER_API_KEY` | (required) |
| `OPENROUTER_MODEL` | `model` |

### Module Reference

#### `session.py` — Conductor

Runs the chapter-writing loop:
1. Detect fresh start vs. resume state
2. Check cost limits (pre-flight)
3. Check context window (per-document token breakdown)
4. Generate chapter draft
5. Show draft to user, await approval
6. Promote approved draft to `chapter_NN.md`
7. Generate living_doc update
8. Validate and save updated living_doc
9. Update state file
10. Repeat for `chapters_per_session` chapters

#### `api.py` — OpenRouter Client

- Token pre-flight with per-document breakdown
- Cost pre-flight (estimated) and post-call tracking
- Retry with `Retry-After` header honoring + backoff + jitter
- Truncation detection: rejects response if `finish_reason == "length"`
- Configurable `temperature`, `top_p`, `seed`

#### `docs.py` — Document Lifecycle

| Function | What It Does |
|----------|-------------|
| `load_static_docs()` | Loads template files (.md/.txt/.docx, rejects PDFs) |
| `load_living_doc()` | Loads mutable living doc; returns empty string if missing |
| `save_chapter_draft()` | Saves to `.rejected/chapter_NN__TIMESTAMP.md` |
| `promote_chapter()` | Atomic move to `chapter_NN.md`; raises `PromotionCollisionError` if exists |
| `save_living_doc()` | Atomic write + timestamped backup |
| `validate_living_doc_structure()` | Checks required headers present and ordered |
| `build_living_doc_diff()` | Unified diff of old vs new living doc (shown on validation failure) |
| `find_unpromoted_drafts()` | Lists `.rejected/` drafts for a chapter number (used on resume) |

#### `state.py` — State File Manager

State file schema (`.pipeline_state.json`):
```json
{
  "last_chapter_promoted": 3,
  "last_chapter_living_doc_updated": 3,
  "last_chapter_drafted": 3,   ← optional; omitted from file when null
  "updated_at": "2026-06-06T12:00:00Z"
}
```

Required keys: `last_chapter_promoted`, `last_chapter_living_doc_updated`. `last_chapter_drafted` is optional — older state files without it are accepted.

Key functions:

- `list_canonical_chapters()` — scans output_dir, returns sorted chapter numbers
- `find_next_chapter_number()` — returns first gap in chapter sequence
- `compute_gaps()` — returns chapter numbers missing below the current max
- `read_state()` — reads state file; `None` if missing, raises `ResumeStateError` on malformed JSON
- `write_state()` — atomically writes state file
- `detect_resume_state()` — cross-checks filesystem vs state file, returns resume dict
- All writes: atomic via temp + `os.replace`

#### `cost.py` — Spend Tracker

Spend file schema (`.pipeline_spend.json`):
```json
{
  "session_total": 0.42,
  "lifetime_total": 3.87,
  "session_started_at": "...",
  "entries": [{"ts": "...", "amount": 0.01, "note": "chapter 4"}]
}
```

- `estimate_cost()` — pre-flight USD estimate
- `track_spend()` — post-call actual recording; returns `{session_total, lifetime_total}`
- `current_totals()` — read current totals without writing
- `reset_session_spend()` — resets in-process session accumulator (used by tests)

#### `tokens.py` — Token Counter

- Uses `tiktoken` with per-model fallback encoding
- Falls back to chars-per-token heuristic (default: 4) if tiktoken offline
- Single function: `count_tokens(text, model, config)` — counts tokens in text only
- Chat-template overhead (~4 tokens/message + ~3 priming) is applied by `session.py`, not here

#### `prompts.py` — Prompt Builder

- `build_prompt()` assembles OpenRouter-compatible message list
- Wraps documents in configurable format
- Concatenates documents in config order

#### `exceptions.py` — Exception Hierarchy

```
PipelineError (base)
├── DocumentLoadError
├── ConfigError
├── APIResponseError
├── ChapterValidationError
├── LivingDocValidationError
├── ContextOverflowError
├── CostLimitError
├── ResumeStateError
├── PromotionCollisionError
└── RejectionLimitReachedError
```

### Chapter Output Layout

```
output_dir/
├── chapter_01.md              ← Canonical chapters (promoted)
├── chapter_02.md
├── .rejected/
│   ├── chapter_01__20260606T120000.md   ← All rejected drafts (kept forever)
│   └── ...
├── .pipeline_state.json
├── .pipeline_spend.json
└── pipeline.log
```

### Safety Guarantees

- **No silent fresh-starts** — Won't skip resume check if output_dir has chapters
- **No silent first-run trap** — Requires seeded living_doc before generation
- **No silent truncation** — Checks `finish_reason='length'`, rejects short chapters
- **No silent context overruns** — Per-document token breakdown on overflow
- **No silent cost overruns** — Pre-flight + post-call cost gating
- **No silent promotion collisions** — Existing chapters block overwrites
- **Bounded rejection loop** — Capped at `max_rejection_retries`
- **Drafts always survive** — `.rejected/` archive kept indefinitely
- **Atomic writes** — All file writes use temp + `os.replace`

---

## Pipeline D: Seed Generator

### What It Does

Interactive CLI that bootstraps a new pedagogical novel project from a source PDF.

### Entry Point

```bash
python -m fiction.seed_gen <source_pdf> <output_dir>
```

### Two-Pass Process

**Pass 1 — LLM genre/concept extraction:**
- Reads source PDF (truncated to 120k chars)
- Sends to LLM with all template files bundled as context
- Validates response contains `"Genre N:"` proposals
- Extracts concept list

**User interaction:**
1. User picks genre (1–N or "custom")
2. User names protagonist
3. User provides protagonist background
4. User confirms/edits extracted concepts (minimum 5 required)
5. User selects climax concept (must match one of the extracted concepts)
6. User provides optional additional notes

**Pass 2 — LLM file generation:**

- Sends user plan + Pass 1 output + bundled templates as context
- LLM generates the full set of world-building documents
- Files written via `parse_output()` + `save_output()`, then `config.toml` written

**Output — ready-to-run project:**
```
<output_dir>/
├── config.toml       ← Pre-populated (static_doc_paths point to ./ not ./templates/)
├── world_laws.md
├── curriculum.md
├── style_contract.md
├── full_map.md
└── living_doc.md
```

Note: template files are written directly in `<output_dir>/`, **not** in a `templates/` subdirectory. The generated `config.toml` uses `static_doc_paths = ["./world_laws.md", ...]`.

Run with: `python -m novel_pipeline --config <output_dir>/config.toml`

---

## Pipeline E: Simple Runner (Removed)

`src/fiction/run_simple.py` has been deleted as of Phase 7. It was a stateless alternative to novel-pipeline with no approval gates. Use `src/cli/fiction.py` or `novel_pipeline` directly.

---

## Configuration Reference

### src/config.json

Controls LLM provider and TTS voice selection for the podcast pipeline.

```json
{
  "api_url": "https://openrouter.ai/api/v1/chat/completions",
  "model": "openrouter/free",
  "toc_page": null,
  "max_tokens": 8192,
  "speakers": {
    "speaker_1": "en-Alice_woman",
    "speaker_2": "en-Carter_man",
    "speaker_3": "en-Maya_woman",
    "speaker_4": "en-Frank_man"
  },
  "wavespeed_model": "microsoft/vibevoice",
  "tts_scale": 1.3
}
```

All values can be overridden with environment variables (see below).

### src/fiction/pipeline/config.toml

Controls the novel-pipeline session. See full reference in Pipeline C section above.

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENROUTER_API_KEY` | Yes | — | OpenRouter authentication |
| `OPENROUTER_MODEL` | No | config value | Model override |
| `OPENROUTER_URL` | No | config value | API endpoint override |
| `OPENROUTER_MAX_TOKENS` | No | config value | Token cap override |
| `OPENROUTER_RETRY_AFTER` | No | — | Fixed retry delay (seconds) |
| `WAVESPEED_API_KEY` | Yes (for TTS) | — | WaveSpeed authentication |
| `WAVESPEED_SCALE` | No | config value | Audio speed scale |
| `WAVESPEED_MODEL` | No | config value | TTS model override |

---

## External APIs

### OpenRouter

- Endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Auth: `Authorization: Bearer $OPENROUTER_API_KEY`
- Any OpenAI-compatible model string works (e.g., `openrouter/free`, `anthropic/claude-opus-4`)
- Used by: podcast LLM script generation, PDF slicer Stage 4, novel-pipeline, seed_gen

### WaveSpeed VibeVoice

- Model: `microsoft/vibevoice` (default)
- Auth: `WAVESPEED_API_KEY`
- Voices available: `en-Alice_woman`, `en-Carter_man`, `en-Maya_woman`, `en-Frank_man`
- Async: submit job → poll for completion → download MP3
- Recovery: `request_id` saved to `tts_job.json` immediately after submission

---

## Python Dependencies

| Library | Purpose |
|---------|---------|
| `PyMuPDF` (fitz) | PDF text extraction |
| `pdf2image` | PDF→image for OCR |
| `pytesseract` | OCR engine |
| `pypdf` / `pypdf2` | PDF page manipulation |
| `pdfplumber` | Structured PDF parsing |
| `python-docx` | .docx template loading |
| `tiktoken` | Token counting for OpenAI-compatible models |
| `tomli` / `tomllib` | TOML config parsing |
| `requests` | HTTP client for all API calls |
| `wavespeed` | Official WaveSpeed SDK |

Package management: `uv` (see `uv.lock`, `.python-version`)

---

## Quick-Start Workflows

### Run podcast for a single chapter

```bash
cd harnessv4
export OPENROUTER_API_KEY=sk-...
export WAVESPEED_API_KEY=ws-...
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf --mode 2person
# Script: data/output/scripts/01_intro_podcast.txt
# Audio:  data/output/audio/01_intro/1.mp3
```

### Slice a whole book and run all chapters

```bash
export OPENROUTER_API_KEY=sk-...
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5
```

### Start a new pedagogical novel

```bash
export OPENROUTER_API_KEY=sk-...
# Step 1: Generate seed project from source book
python -m fiction.seed_gen books/mybook.pdf data/my_novel/

# Step 2: Run novel pipeline
cd data/my_novel
python -m novel_pipeline --config config.toml
```

### Resume an interrupted novel session

```bash
cd data/my_novel
python -m novel_pipeline --config config.toml --resume
```

---

## Testing

Novel-pipeline unit tests:

```bash
cd src/fiction/pipeline
python -m pytest tests/test_pipeline.py
```

Tests cover: config validation, token counting, prompt building, cost estimation. API calls are mocked.

Novel-pipeline dry run (no API calls):

```bash
python -m novel_pipeline --config config.toml --dry-run
```

---

## Phases Log

Development history is tracked in `src/phases/`:

```
src/phases/
├── structure.md       ← Overview of phase structure
├── phase_01/          ← Each phase is a directory (not a .md file)
├── phase_02/
├── ...
└── phase_07/          ← Most recent (as of last audit)
```

Each phase directory contains markdown files documenting what was built, why, and key decisions made. Read the latest before starting new work.

---

## Key Design Decisions

1. **Flat API design** — Modules are stateless functions, not classes. State lives in files.
2. **Siblings, not chain** — All output pipelines read from source independently; none feeds another.
3. **Atomic writes everywhere** — `temp file + os.replace` prevents partial writes.
4. **`.rejected/` archive** — Every rejected draft is kept; nothing is lost.
5. **Pre-flight gates** — Cost and context checked *before* API calls, not after.
6. **OpenRouter as proxy** — Any OpenAI-compatible provider works by swapping the model string.
7. **State file is ground truth** — Filesystem scan + state file comparison determines resume strategy.
8. **Config over code** — Prompt strings, file formats, cost limits, retry behavior all in TOML/JSON.
