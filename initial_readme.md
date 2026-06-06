# Harness V3 — Comprehensive Project Reference

> This document is the authoritative source of truth for AI sessions and developers.
> It describes everything: architecture, data flow, modules, config keys, CLIs, APIs.
> Written from source code on 2026-06-06. Update it when code changes.

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
│   ├── run_book.py                ← Batch podcast runner (entry point)
│   ├── run_chapter.py             ← Single-chapter podcast runner (entry point)
│   │
│   ├── slicer/
│   │   └── pdf_splitter.py        ← 4-stage PDF chapter splitter
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
│   │       ├── parse_output.py    ← Script parser
│   │       ├── save_output.py     ← Output writer
│   │       ├── read_prompt.py     ← Prompt loader
│   │       └── main.py            ← Module entry
│   │
│   └── fiction/
│       ├── run_simple.py          ← Standalone novel runner (simple, no gates)
│       │
│       ├── seed_gen/              ← Interactive seed project generator
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   ├── cli.py
│       │   └── templates/         ← Template files copied to new seed projects
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
│   │   └── directive_templates/
│   └── ...
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

**Single chapter:**
```bash
python src/run_chapter.py <chapter.pdf> [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--llm` | off | Call LLM to generate script (required for script generation) |
| `--skip-audio` | off | Skip TTS, produce script only |
| `--mode MODE` | `2person` | Script style (see Modes below) |
| `--context "..."` | — | Extra context injected into prompt |
| `--context-file file.txt` | — | Load context from file |
| `--fiction-dir ./` | — | Path to fiction pipeline output (for `fiction_meta` mode) |

**Full book (batch):**
```bash
python src/run_book.py [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--book whole.pdf` | — | Source PDF; triggers PDF slicing first |
| `--toc-page N` | — | TOC page number (required with `--book`) |
| `--no-ocr` | off | Skip OCR fallback in slicer |
| `--slice-only` | off | Only slice PDF, don't run podcast pipeline |
| `--llm` | off | Call LLM for script generation |
| `--skip-audio` | off | Skip TTS |
| `--mode MODE` | `2person` | Script style |
| `--force` | off | Reprocess chapters that already have output |

### Script Modes

| Mode | Speakers | Description |
|------|----------|-------------|
| `2person` | HOST (Alex) + EXPERT (Jordan) | 4000-word technical deep-dive, ~30 min |
| `4person` | 4 voices | Debate format |
| `code` | 2 voices | Engineering *why* focus |
| `realworld` | 2 voices | Connects to user-supplied current event |
| `fiction_meta` | 2 voices | Meta-commentary on fiction chapter output |

### Speaker Normalization

`run_chapter.py` normalizes script speaker labels before saving:
- `ALEX` / `JORDAN` → `Speaker 0` / `Speaker 1`
- `HOST` / `EXPERT` → `Speaker 0` / `Speaker 1`
- Standalone speaker label lines merged with following content line

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
    pdf_path="book.pdf",
    output_dir="data/chapters/",
    toc_page=8,       # 1-indexed TOC page
    no_ocr=False,
    verbose=False,
)
```

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
| `--chapter-start N` | Start from chapter N (requires `--auto-approve` to confirm) |
| `--ignore-cost-limit` | Bypass cost gates |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User abort / cost limit reached / rejection limit reached |
| 2 | Config error |
| 3 | API error |

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
max_rejection_retries = 5              # Max rejections before session aborts
cost_limit_usd_per_session = 5.00      # Per-session spend cap (USD)
cost_limit_usd_total = 50.00           # Lifetime spend cap (USD)
expected_output_tokens_chapter = 4000  # Pre-flight estimate for chapters
expected_output_tokens_update = 2000   # Pre-flight estimate for living_doc updates
log_path = "./pipeline.log"
state_file_path = "./.pipeline_state.json"
spend_file_path = "./.pipeline_spend.json"
required_living_doc_sections = [...]   # Section headers that must exist in living_doc

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
| `save_chapter_draft()` | Saves to `.rejected/chapter_NN__TIMESTAMP.md` |
| `promote_chapter()` | Atomic move to `chapter_NN.md`; raises `PromotionCollisionError` if exists |
| `save_living_doc()` | Atomic write + timestamped backup |
| `validate_living_doc_structure()` | Checks required headers present and ordered |

#### `state.py` — State File Manager

State file schema (`.pipeline_state.json`):
```json
{
  "last_chapter_promoted": 3,
  "last_chapter_living_doc_updated": 3,
  "last_chapter_drafted": 3,
  "updated_at": "2026-06-06T12:00:00Z"
}
```

Key functions:
- `find_next_chapter_number()` — scans filesystem, returns first gap
- `detect_resume_state()` — compares filesystem to state, offers recovery prompts
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
- `track_spend()` — post-call actual recording

#### `tokens.py` — Token Counter

- Uses `tiktoken` with per-model fallback encoding
- Falls back to chars-per-token heuristic (default: 4) if tiktoken offline
- Accounts for chat-template overhead (~4 tokens/message + ~3 priming)

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

**Output — ready-to-run project:**
```
<output_dir>/
├── config.toml       ← Pre-populated with genre, protagonist, concepts
└── templates/
    ├── world_laws.md
    ├── curriculum.md
    ├── style_contract.md
    ├── full_map.md
    └── living_doc.md
```

Run with: `python -m novel_pipeline --config <output_dir>/config.toml`

---

## Pipeline E: Simple Runner (Standalone)

`src/fiction/run_simple.py` — Stateless alternative to novel-pipeline for quick runs.

- No approval gates; trust-the-disk model
- Single session = 3 chapters per pause
- Reference docs: `pass_always.md`, `full_map.md`, `living_document.md`
- Outputs: `chapters/`, `backups/`, `session_notes.md`, `run_log.txt`

---

## Configuration Reference

### src/config.json

Controls LLM provider and TTS voice selection for the podcast pipeline.

```json
{
  "api_url": "https://openrouter.ai/api/v1/chat/completions",
  "model": "openrouter/free",
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
cd harnessv3
export OPENROUTER_API_KEY=sk-...
export WAVESPEED_API_KEY=ws-...
python src/run_chapter.py data/chapters/01_intro.pdf --llm --mode 2person
# Script: data/output/scripts/01_intro_podcast.txt
# Audio:  data/output/audio/01_intro/1.mp3
```

### Slice a whole book and run all chapters

```bash
export OPENROUTER_API_KEY=sk-...
python src/run_book.py --book books/mybook.pdf --toc-page 5 --llm
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
├── phase_01.md
├── phase_02.md
├── ...
└── phase_NN.md   ← Most recent
```

Each phase log documents what was built, why, and key decisions made. Read the latest before starting new work.

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
