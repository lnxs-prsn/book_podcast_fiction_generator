# User Manual — How to Solve It Learning Engine

## What This Project Is

A pipeline that takes a book (PDF) and transforms it into two parallel learning formats:

1. **Podcast Pipeline** — generates HOST/GUEST dialogue scripts from book chapters
2. **Fiction Pipeline** — writes a pedagogical cultivation novel (Systems Cultivation) that teaches systems design concepts

Audio generation (TTS) exists in the codebase but was not run (expensive API costs).

---

## Prerequisites

**Python packages required:**
- `pymupdf` (fitz) — PDF extraction
- `requests` — HTTP API calls
- `pdf2image` + `pytesseract` — OCR for scanned PDFs (used in book slicer)
- `Pillow` — image handling for OCR
- `tomllib` (stdlib in Python 3.11+) — TOML config parsing

**Missing packages (install before running):**
- `pdfplumber` — listed in pyproject.toml but not used in critical paths
- `tiktoken` — optional; falls back to character-based heuristic if absent

**Install from `src/pyproject.toml`:**
```bash
pip install pymupdf requests pdf2image pytesseract pillow
```

**Environment setup:**

1. Copy the example file to create your local `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and replace the placeholder values with your real API keys:
   ```bash
   OPENROUTER_API_KEY=your-openrouter-api-key
   WAVESPEED_API_KEY=your-wavespeed-api-key
   ```
3. The application loads `.env` automatically when it starts. If you need to use a
   different env file (for example, per-environment secrets), set `DOTENV_PATH`:
   ```bash
   DOTENV_PATH=/path/to/secrets.env python menu.py
   DOTENV_PATH=/path/to/secrets.env python src/cli/podcast.py --help
   ```

> Note: The `.env` file is ignored by Git and must never be committed. If you previously
> committed real keys, rotate them immediately in the provider dashboards.
> The `src/config.json` default `api_url` is used only when `OPENROUTER_URL` is not set;
> explicit env vars or values in `.env` take precedence.

---

## Project Layout

```
harnessv7_migrated/
├── books/                              ← Source PDFs go here
│   └── George_Polya_How_To_Solve_It_.pdf
├── split_chapters/                     ← Pre-sliced chapter PDFs (from a prior run)
├── data/
│   ├── chapters/                       ← Where the slicer writes chapter PDFs
│   └── output/
│       └── scripts/                    ← Generated podcast scripts land here
│           └── 2person/<run_id>/<name>_podcast.txt
├── src/
│   ├── cli/
│   │   ├── podcast.py                  ← Podcast pipeline entry point
│   │   └── fiction.py                  ← Fiction pipeline entry point
│   ├── fiction/
│   │   ├── pipeline/                   ← Fiction pipeline working directory
│   │   │   ├── config.toml             ← Fiction pipeline configuration
│   │   │   ├── living_doc.md           ← Mutable novel state (updated after each chapter)
│   │   │   ├── templates/              ← Static world bible, curriculum, etc.
│   │   │   └── chapters/               ← Generated fiction chapters output here
│   │   └── seed_gen/                   ← Tool to generate templates from a source PDF
│   ├── novel_pipeline/                 ← Fiction pipeline engine (Python package)
│   └── ...
└── docs/                               ← Design documents
```

---

## Pipeline 1: Podcast Script Generation

### How It Works

1. **Optionally slices a book PDF** into chapters using a 5-stage TOC extractor:
   - Stage 1: Internal PDF bookmarks
   - Stage 2: Text-based TOC parsing
   - Stage 3: OCR on the TOC page
   - Stage 4: LLM identifies structure from OCR'd front matter
   - Stage 5: Content scan (verifies page positions for scanned books)

2. **For each chapter PDF**, extracts text and sends it to the LLM with a mode-specific prompt to generate a dialogue script.

3. **Optionally converts the script to audio** via WaveSpeed TTS API (skip with `--skip-audio`).

### Running: Single Chapter

```bash
cd /path/to/harnessv7_migrated/src

OPENROUTER_API_KEY=<key> \
OPENROUTER_MODEL=openrouter/auto \
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions \
uv run python cli/podcast.py ../split_chapters/01_chapter_PART_I._IN_THE_CLASSROOM.pdf --skip-audio
```

Output written to: `data/output/scripts/2person/<run_id>/01_chapter_PART_I._IN_THE_CLASSROOM_podcast.txt`

### Running: Full Book (Slice + Generate All Chapters)

```bash
cd /path/to/harnessv7_migrated/src

OPENROUTER_API_KEY=<key> \
OPENROUTER_MODEL=openrouter/auto \
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions \
uv run python cli/podcast.py \
  --book ../books/George_Polya_How_To_Solve_It_.pdf \
  --toc-page 12 \
  --skip-audio
```

> The slicer detects existing chapters in `data/chapters/` and skips re-slicing if they exist (unless `--force` is given).
> For the Polya book (scanned PDF, no internal bookmarks): slicing uses OCR + LLM interpretation (Stages 4+5). This takes 10–20 minutes for a 284-page book.

**Speed tip:** Copy pre-sliced chapters to `data/chapters/` before running `--book` to skip the slicer:
```bash
mkdir -p data/chapters
cp split_chapters/*.pdf data/chapters/
```

### Podcast Script Modes

Pass `--mode <mode>` to change the dialogue format:

| Mode | Description |
|------|-------------|
| `2person` | HOST + GUEST (default) |
| `4person` | Four-speaker panel |
| `code` | Code-focused technical discussion |
| `realworld` | Applies concepts to a real-world event (requires `--context`) |
| `fiction_meta` | Requires `--fiction-dir` with pre-written fiction chapters |

### Actual Run Output (This Session)

**Single chapter test:**
```
script: data/output/scripts/2person/20260622_150517/01_chapter_PART_I._IN_THE_CLASSROOM_podcast.txt
```

**Full book test (2 staged chapters):**
```
Book complete: 2 ok, 0 failed
  script: data/output/scripts/2person/20260622_150622/01_chapter_PART_I._IN_THE_CLASSROOM_podcast.txt
  script: data/output/scripts/2person/20260622_150622/02_chapter_PART_II._HOW_TO_SOLVE_IT_podcast.txt
```

---

## Pipeline 2: Fiction (Novel Generator)

### How It Works

1. Loads 4 static template files (world bible, curriculum, style contract, full map) from `src/fiction/pipeline/templates/`
2. Loads the mutable living document from `src/fiction/pipeline/living_doc.md`
3. For each chapter in the session:
   - Calls the LLM to write the next chapter
   - Validates the chapter (word count ≥ `min_chapter_words`)
   - Saves draft to `chapters/.rejected/`
   - Approves the chapter (auto or interactively)
   - Promotes draft to `chapters/chapter_NN.md`
   - Calls the LLM to update the living document
   - Saves the updated living doc
4. Repeats for `chapters_per_session` chapters

### Configuration: `src/fiction/pipeline/config.toml`

Key settings for this run:
```toml
model = "openrouter/auto"       # Changed from openrouter/free
chapters_per_session = 1        # Number of chapters per session
min_chapter_words = 200         # Minimum word count (see Known Issues)
price_per_1m_input_tokens = 2.0
price_per_1m_output_tokens = 8.0
```

> **CRITICAL**: The `model` field in `config.toml` is what actually gets sent in the API request payload. Setting `OPENROUTER_MODEL` env var does NOT override the config model for the fiction pipeline (see `errors_found.md`). Update `config.toml` directly.

### Running: Generate Chapters

```bash
cd /path/to/harnessv7_migrated/src

OPENROUTER_API_KEY=<key> \
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions \
uv run python cli/fiction.py \
  --config fiction/pipeline/config.toml \
  --auto-approve \
  --ignore-cost-limit \
  --chapter-start 1
```

### Running: Resume After Interruption

If a session is interrupted mid-cycle (chapter promoted but living doc not updated):

```bash
cd /path/to/harnessv7_migrated/src

OPENROUTER_API_KEY=<key> \
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions \
uv run python cli/fiction.py \
  --config fiction/pipeline/config.toml \
  --resume
```

On resume without `--auto-approve`, you will be prompted:
- `[r]` Regenerate living doc from the promoted chapter (calls API)
- `[c]` Continue with stale living doc (no API call, next chapter may have outdated context)
- `[a]` Abort

### Handling Living Doc Update Failure

The model sometimes generates a living doc update that fails structural validation (missing required section headers). When this happens interactively:

```
What now?
  [r] retry the update
  [k] keep the OLD living doc (chapter stays promoted; session stops)
  [a] abort session
```

- Press `r` to retry (may succeed on the next attempt)
- Press `k` to keep the old living doc — the chapter is saved but the living doc is stale. Re-run with `--resume` next time.

**Non-interactive workaround** (pipe 'k' to stdin):
```bash
cd /path/to/harnessv7_migrated/src
echo 'k' | uv run python cli/fiction.py --config fiction/pipeline/config.toml --auto-approve --chapter-start N --ignore-cost-limit
```

### Actual Run Output (This Session)

```
Chapter 01: Generated (408 words) → Promoted → Living doc update FAILED (model format error)
Chapter 02: Generated (311 words) → Promoted → Living doc update SUCCEEDED
```

Generated files:
- `data/fiction/chapters/chapter_01.md` — Chapter 1 of the cultivation novel
- `data/fiction/chapters/chapter_02.md` — Chapter 2 of the cultivation novel
- `src/fiction/pipeline/living_doc.md` — Updated living document (reflects through chapter 2)

### Seeding a New Novel (for a Different Book)

To generate a new world bible and curriculum from a source PDF:

```bash
cd /path/to/harnessv7_migrated/src

OPENROUTER_API_KEY=<key> \
OPENROUTER_MODEL=openrouter/auto \
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions \
uv run python fiction/seed_gen/__main__.py \
  ../books/<your_book>.pdf \
  <output_dir>
```

This runs a 2-pass interactive process:
1. **Pass 1**: LLM proposes genre options based on the book's concepts
2. You select a genre, protagonist name/background, and concept list
3. **Pass 2**: LLM generates the full template set

Review and edit the output files, then run the fiction pipeline with the new config.

---

## Key CLI Flags Summary

### Podcast Pipeline (`src/cli/podcast.py`)

```
pdf                     Single chapter PDF to process
--book PDF              Full book PDF (slice then generate)
--toc-page N            TOC page number for the slicer (needed for scanned books)
--skip-audio            Skip TTS audio generation (saves cost)
--skip-script           Skip LLM script generation (use with --script-file)
--script-file PATH      Use existing script file (requires --skip-script)
--mode MODE             2person|4person|code|realworld|fiction_meta
--context TEXT          Context for realworld mode
--context-file PATH     Read context from file
--fiction-dir DIR       Directory of fiction chapters for fiction_meta mode
--slice-only            Only slice the book, do not generate scripts
--force                 Re-slice even if chapters already exist
--no-ocr                Skip OCR stages (fast but fails for scanned books)
--scripts-out PATH      Override output directory for scripts
--chapters-dir PATH     Override input directory for chapter PDFs
```

### Fiction Pipeline (`src/cli/fiction.py`)

```
--config PATH           Path to TOML config file (required)
--auto-approve          Auto-approve all chapters without prompting
--dry-run               Run without API calls (placeholder chapters)
--resume                Resume from interrupted state
--chapter-start N       Start from chapter N (overrides auto-detection)
--ignore-cost-limit     Bypass USD cost gates
```
