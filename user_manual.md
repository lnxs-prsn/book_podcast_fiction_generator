# Harness V4 — User Manual

**Version:** 4.0 (v10 build)
**Last updated:** 2026-06-13

This manual explains how to use Harness V4 to turn books and textbooks into parallel learning materials: podcast episodes, pedagogical novels, and seed fiction projects.

---

## Table of Contents

1. [What Harness V4 Does](#what-harness-v4-does)
2. [Before You Start](#before-you-start)
3. [Project Layout](#project-layout)
4. [Installation & Setup](#installation--setup)
5. [The Podcast Pipeline](#the-podcast-pipeline)
6. [The Fiction / Novel Pipeline](#the-fiction--novel-pipeline)
7. [The Seed Project Generator](#the-seed-project-generator)
8. [The PDF Slicer](#the-pdf-slicer)
9. [Configuration Reference](#configuration-reference)
10. [Troubleshooting](#troubleshooting)
11. [Quick Command Reference](#quick-command-reference)

---

## What Harness V4 Does

Harness V4 reads a source PDF (usually a textbook or technical book) and produces up to three independent outputs from it:

| Output | Description | Typical use |
|--------|-------------|-------------|
| **Podcast episodes** | Dialogue-style scripts between AI hosts, synthesized into multi-speaker MP3 audio | Learn on the go, share episodes |
| **Pedagogical fiction** | Xianxia/cultivation-style novels that teach the book's concepts through story | Make dense material memorable |
| **Seed projects** | A ready-to-run scaffold for a new novel, generated from a source book | Bootstrap new fiction worlds |

The pipelines are **siblings**, not a chain. Each pipeline reads independently from the source PDFs; the podcast pipeline does not depend on the fiction pipeline and vice versa.

The canonical workflow is:

```text
book PDF  →  PDF slicer  →  chapter PDFs  →  run podcast / fiction / seed pipelines
```

---

## Before You Start

You need two free/third-party accounts:

### 1. OpenRouter API key (for writing scripts and fiction)

1. Go to [openrouter.ai](https://openrouter.ai) and create an account.
2. Open **Keys** → **Create Key**.
3. Copy the key. It looks like `sk-or-v1-...`.
4. Export it in every terminal session, or add it to a project `.env` file:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### 2. WaveSpeed API key (for podcast audio only)

1. Go to [wavespeed.ai](https://wavespeed.ai) and create an account.
2. Open **API Keys** and create a new key.
3. Copy the key. It looks like `wsk_live_...`.
4. Export it before generating audio:

```bash
export WAVESPEED_API_KEY="wsk_live_..."
```

> **Cost note:** OpenRouter offers free models you can use at no charge. WaveSpeed charges a small amount per audio job (typically a few cents per chapter). Load a small credit balance before generating audio.

---

## Project Layout

```text
harnessv4/
├── books/                      # Drop whole-book PDFs here
├── data/
│   ├── chapters/               # Individual chapter PDFs (input)
│   ├── output/                 # Podcast outputs
│   │   ├── scripts/
│   │   │   └── <mode>/
│   │   │       └── <run_id>/   # e.g. 2person/20260613_143000/
│   │   │           └── *.txt   # Generated scripts
│   │   └── audio/
│   │       └── <mode>/
│   │           └── <run_id>/
│   │               └── <chapter>/
│   │                   └── *.mp3
│   ├── neon_sprawl/            # Example novel project
│   └── seed_run2/              # Another example novel project
├── src/                        # All source code
│   ├── cli/
│   │   ├── podcast.py          # Main podcast CLI
│   │   └── fiction.py          # Main fiction CLI
│   ├── slicer/
│   │   └── pdf_splitter.py     # PDF chapter splitter
│   ├── tts/
│   │   ├── cli.py              # WaveSpeed TTS client
│   │   └── recover.py          # Recover killed TTS jobs
│   ├── podcast_script_generator/
│   │   └── llm/                # LLM script generation modules
│   ├── fiction/
│   │   ├── seed_gen/           # Interactive seed generator
│   │   └── pipeline/           # Production novel pipeline
│   ├── config.json             # Podcast / TTS config
│   └── pyproject.toml          # uv project config
├── .env                        # PYTHONPATH=src
├── user_manual.md              # This file
├── initial_readme.md           # Authoritative developer reference
└── podcast_friendly_user_guide.md  # Beginner podcast guide
```

---

## Installation & Setup

Harness V4 uses [uv](https://github.com/astral-sh/uv) for Python and dependency management.

### 1. Install uv

Follow the official instructions for your operating system: <https://docs.astral.sh/uv/getting-started/installation/>

### 2. Sync dependencies

```bash
cd /home/mr/Desktop/python/harness_design/harnessv4/src
uv sync
```

This installs all packages listed in `src/pyproject.toml`, including PDF libraries, the WaveSpeed SDK, and the `novel-pipeline` fiction package.

> **Note:** `uv sync` should be run from the `src/` directory because that is where the project `pyproject.toml` and `uv.lock` live.

### 3. Set PYTHONPATH

Most Python commands need `PYTHONPATH=src` so sibling packages resolve correctly.

The project already contains a `.env` file at the repository root with:

```text
PYTHONPATH=src
```

`uv run` reads this automatically when invoked from the repository root. If you run plain `python`, prefix commands yourself:

```bash
PYTHONPATH=src python src/cli/podcast.py --help
```

### 4. Verify the install

```bash
PYTHONPATH=src python src/cli/podcast.py --help
PYTHONPATH=src python src/cli/fiction.py --help
```

Both should print help text without errors.

---

## The Podcast Pipeline

The podcast pipeline turns a PDF chapter into a dialogue script, then (optionally) into a multi-speaker MP3.

**Main CLI:** `src/cli/podcast.py`

> Older tutorials may reference `src/run_chapter.py` or `src/run_book.py`. These still work as thin shims, but new commands should use `src/cli/podcast.py`.

### Single chapter

```bash
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf --mode 2person
```

Outputs are organised by mode and a timestamp run ID:

- Script: `data/output/scripts/2person/<run_id>/01_intro_podcast.txt`
- Audio:  `data/output/audio/2person/<run_id>/01_intro/1.mp3`

Each run gets its own `<run_id>` folder (format `YYYYMMDD_HHMMSS`) so previous runs are never overwritten.

### Script only, no audio

```bash
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf --skip-audio
```

This is fast and costs nothing. Read the script before paying for audio.

### Audio only from an existing script

If you already have a script — written externally or saved from a previous run — you can skip LLM generation entirely and go straight to audio:

```bash
PYTHONPATH=src python src/cli/podcast.py \
  --skip-script \
  --script-file speculative_podcast_scripts/01_chapter_PART_I._IN_THE_CLASSROOM_podcast.txt \
  --mode 2person
```

- `--skip-script` bypasses the LLM; no `OPENROUTER_API_KEY` needed.
- `--script-file` points at any `.txt` file using the `Speaker 0:` / `Speaker 1:` dialogue format.
- No PDF argument is required.
- The audio output directory is derived from the script filename: `data/output/audio/<mode>/<run_id>/<script_stem>/`.
- Use `--audio-out` to redirect where audio lands.

### Whole book from one PDF

```bash
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5
```

`--toc-page` is optional. If omitted, the slicer uses the value from `src/config.json` or prompts you interactively.

The tool:

1. Splits the PDF into chapter PDFs.
2. Generates a script for each chapter.
3. Generates audio for each chapter (unless `--skip-audio`).

If `data/chapters/` already contains PDFs, the slice step is skipped automatically.

### Slice only, inspect first

```bash
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5 --slice-only
```

This writes chapter PDFs to `data/chapters/` and stops. Inspect them, then run the full pipeline:

```bash
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5
```

### Pre-split chapters in a folder

```bash
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5
# or, if chapters already exist:
# PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf
# for each chapter
```

To process every PDF already in `data/chapters/`, pass `--book` with the source PDF or point `--chapters-dir` to your folder.

### Podcast modes

| Mode | Speakers | Description |
|------|----------|-------------|
| `2person` | Host + Expert | Deep technical dive; default; ~4,000 words / ~30 min |
| `4person` | 4 voices | Debate format with multiple perspectives |
| `code` | 2 voices | Focuses on what code does and why it was written that way |
| `realworld` | 2 voices | Connects the chapter to a real-world event you provide |
| `fiction_meta` | 2 voices | Commentary on a fiction chapter from the novel pipeline |

Choose a mode with `--mode`:

```bash
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf --mode 4person
```

### Real-world context

```bash
# Inline
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf \
  --mode realworld \
  --context "The EU just passed new AI hiring regulations"

# From a file
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf \
  --mode realworld \
  --context-file ./event.txt
```

### Fiction meta mode

Requires a fiction chapter file matching the PDF chapter number:

```bash
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf \
  --mode fiction_meta \
  --fiction-dir data/neon_sprawl/chapters/
```

The tool matches `chapter_NN.md` in the fiction directory to the chapter number in the PDF filename.

### Force reprocessing

By default, chapters that already have output are skipped. Add `--force` to regenerate:

```bash
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5 --force
```

### Path overrides

You can redirect outputs without editing config:

```bash
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf \
  --scripts-out /tmp/scripts \
  --audio-out /tmp/audio
```

---

## The Fiction / Novel Pipeline

The novel pipeline writes a multi-chapter pedagogical novel from a set of world-building documents. It includes human approval gates, cost tracking, resume on interrupt, and atomic file writes.

**Main CLI:** `src/cli/fiction.py`

### Run an existing novel project

```bash
PYTHONPATH=src python src/cli/fiction.py --config data/neon_sprawl/config.toml
```

The example configs live in `data/neon_sprawl/` and `data/seed_run2/`. To run your own project, copy and edit the config file.

### Start with the seed generator

The fastest way to create a new novel project is from a source PDF:

```bash
PYTHONPATH=src python -m fiction.seed_gen books/mybook.pdf data/my_novel/
```

This interactive tool will:

1. Extract genre/concept proposals from the PDF.
2. Ask you to pick a genre, name a protagonist, and select key concepts.
3. Generate world-building files and a `config.toml`.

Then run the novel pipeline from the project root:

```bash
PYTHONPATH=src python -m novel_pipeline --config data/my_novel/config.toml
```

Or, if you prefer to work inside the novel directory:

```bash
cd data/my_novel
PYTHONPATH=/home/mr/Desktop/python/harness_design/harnessv4/src python -m novel_pipeline --config config.toml
```

### Common flags

| Flag | Purpose |
|------|---------|
| `--config path` | Required. Path to the TOML config. |
| `--auto-approve` | Skip human approval gates. |
| `--dry-run` | Test config, prompts, and cost estimates without API calls. |
| `--resume` | Resume an interrupted session from saved state. |
| `--chapter-start N` | Force starting chapter number. |
| `--ignore-cost-limit` | Bypass cost gates. |

### Typical session

```bash
# 1. Estimate cost without spending anything
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml --dry-run

# 2. Run with approval gates
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml

# 3. Resume after an interrupt
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml --resume
```

Because `novel-pipeline` is now installed by `uv sync`, you can also run the package directly from the project root:

```bash
PYTHONPATH=src python -m novel_pipeline --config data/my_novel/config.toml
```

### How approval works

Unless you pass `--auto-approve`, the pipeline shows the first 500 characters of each chapter draft and asks:

```text
[y/n/q]
```

- `y` — promote the draft to `chapter_NN.md`.
- `n` — regenerate (up to `max_rejection_retries` times).
- `q` — quit and preserve state for resume.

### Output layout

```text
data/my_novel/
├── chapter_01.md              # Approved chapters
├── chapter_02.md
├── .rejected/                 # Rejected drafts (kept forever)
│   ├── chapter_01__20260606T120000.md
│   └── ...
├── .pipeline_state.json       # Resume state
├── .pipeline_spend.json       # Cost tracking
└── pipeline.log               # Session log
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User abort, cost limit reached, or rejection limit reached |
| 2 | Config error, document load error, resume state error, or promotion collision |
| 3 | API error after retries, context overflow, or unexpected error |

---

## The Seed Project Generator

The seed generator bootstraps a complete novel project from a source PDF.

```bash
PYTHONPATH=src python -m fiction.seed_gen <source_pdf> <output_dir>
```

Example:

```bash
PYTHONPATH=src python -m fiction.seed_gen books/George_Polya_How_To_Solve_It_.pdf data/polya_novel/
```

It produces:

```text
data/polya_novel/
├── config.toml
├── world_laws.md
├── curriculum.md
├── style_contract.md
├── full_map.md
└── living_doc.md
```

You can then edit these files and run:

```bash
cd data/polya_novel
PYTHONPATH=/home/mr/Desktop/python/harness_design/harnessv4/src python -m novel_pipeline --config config.toml
```

---

## The PDF Slicer

The slicer splits a whole-book PDF into individual chapter PDFs.

### CLI

```bash
PYTHONPATH=src python src/slicer/pdf_splitter.py \
  -i books/mybook.pdf \
  -p 10 \
  --chapters-only
```

### Python API

```python
from endpoints.slicer import run_splitter

result = run_splitter(
    input_path="books/mybook.pdf",
    toc_page=10,
    output_dir="data/chapters/",
    chapters_only=True,
)
```

### How TOC extraction works

The slicer runs up to five stages and combines the best results automatically.

**Stages 1–3 (fast, no API key needed):**

1. **Internal PDF bookmarks** — exact, instant. Used when the PDF has embedded bookmarks.
2. **Text extraction** from the TOC page you specify — parses the raw text of that page.
3. **OCR fallback** — OCRs the TOC page if Stage 2 finds no text.

**Stages 4–5 (for books where 1–3 fail, typically scanned PDFs):**

4. **LLM analysis** — OCRs the first 20 pages plus three sample pages deeper in the book, then asks the LLM to identify section titles and compute their PDF page positions. Requires `OPENROUTER_API_KEY`. Result is validated; if page numbers cluster suspiciously the offset correction is attempted automatically.

5. **Content scan** — OCRs the top quarter of every page looking for `PART / CHAPTER / SECTION` headings. Requires no API key. Slower on large books but always returns verified PDF page positions.

**Stage 4+5 combination (scanned PDFs with API key set):**

When the slicer detects that a PDF has no native text (i.e. it is scanned / image-based), it runs **both** Stage 4 and Stage 5 and merges the results:

- Stage 4 contributes **rich chapter titles** from the TOC.
- Stage 5 contributes **verified PDF page positions** from the physical scan.
- For matched entries the Stage 4 title replaces the coarser Stage 5 heading.
- For Stage 4-only entries (finer sections the content scan cannot see) the slicer applies a median page offset computed from the matched pairs and includes them if their corrected position is valid.

The source used is printed in the summary line, e.g. `Stage 4+5 (LLM titles + content scan positions)`.

**Granularity limits:**

The slicer reliably finds any heading that uses the words PART, CHAPTER, or SECTION. It cannot automatically find:

- Numbered sections without a keyword (`1.`, `2.`, …) — common in older academic books.
- Dictionary-style entries introduced by a bold term — bold is invisible to OCR.

For books with these structures (e.g. Polya's *How to Solve It*) the four top-level PARTs are the correct and natural granularity for podcast episodes.

**To force Stage 5 only** (fastest reliable option for scanned books, no API call):

```bash
OPENROUTER_API_KEY="" PYTHONPATH=src python src/slicer/pdf_splitter.py \
  -i books/mybook.pdf -p 10 -o data/chapters/
```

Output files look like:

```text
data/chapters/01_chapter_PART_I._IN_THE_CLASSROOM.pdf
data/chapters/02_chapter_PART_II._HOW_TO_SOLVE_IT.pdf
```

---

## Configuration Reference

### `src/config.json` — Podcast and TTS

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

You can override JSON values with environment variables:

| Env var | Overrides config key |
|---------|----------------------|
| `OPENROUTER_URL` | `api_url` |
| `OPENROUTER_MODEL` | `model` |
| `OPENROUTER_MAX_TOKENS` | `max_tokens` |
| `WAVESPEED_SCALE` | `tts_scale` |
| `WAVESPEED_MODEL` | `wavespeed_model` |

### Novel pipeline `config.toml`

A minimal config:

```toml
model = "openrouter/free"
context_limit = 200000
price_per_1m_input_tokens = 0.001
price_per_1m_output_tokens = 0.001

static_doc_paths = [
    "./templates/world_laws.md",
    "./templates/curriculum.md",
    "./templates/style_contract.md",
    "./templates/full_map.md",
]

living_doc_path = "./living_doc.md"
output_dir = "./chapters"
```

See `src/fiction/pipeline/config.example.toml` for the full annotated reference, including cost limits, retry tuning, prompt overrides, and file-naming formats.

### Required environment variables

| Variable | Required for | Notes |
|----------|--------------|-------|
| `OPENROUTER_API_KEY` | All LLM features | Podcast scripts, slicer Stage 4, fiction pipeline, seed generator |
| `WAVESPEED_API_KEY` | Podcast audio | Not needed if you always pass `--skip-audio` |

---

## Troubleshooting

### "PYTHONPATH is not set correctly"

Run every Python command with `PYTHONPATH=src`:

```bash
PYTHONPATH=src python src/cli/podcast.py --help
```

Or use `uv run`, which reads the `.env` file automatically:

```bash
cd src
uv run python ../src/cli/podcast.py --help
```

### "OPENROUTER_API_KEY not set"

You forgot the API key. Export it first:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### 401 error from OpenRouter

Your key is wrong or revoked. Create a new key in OpenRouter and try again.

### 429 error (rate limited)

The free model is busy. The tool retries automatically. If it keeps failing, wait a few minutes or switch models via `OPENROUTER_MODEL`.

### Audio job interrupted

If your terminal closed while audio was generating, the WaveSpeed job may still be running. Recover it:

```bash
PYTHONPATH=src python src/tts/recover.py data/output/audio/<chapter_name>/tts_job.json
```

### "The script is too short"

Some free-tier models do not produce long outputs even when asked. The script will still be valid, just shorter. Try a different model via `OPENROUTER_MODEL` or `config.json`.

### Novel pipeline won't resume

Check that:

- The config path is correct.
- `.pipeline_state.json` exists and is valid JSON.
- You are passing `--resume`.
- The `output_dir` and `living_doc_path` in the config point at the same files.

### Podcast pipeline fails on a scanned PDF ("No extractable text")

The podcast pipeline now handles scanned / OCR PDFs automatically — it falls back to pytesseract for any page that contains no embedded text. No extra steps or flags are needed. If you see this error with an older build, update `src/podcast_script_generator/llm/extract_pdf.py` to the current version.

### Slicer produces wrong chapter boundaries

Try a different `--toc-page` value first. For scanned books the slicer now automatically runs Stage 4+5 (LLM titles combined with content scan positions) — this is the most reliable path. If results are still wrong:

- **Too few chapters found:** the book may use numbered sections (`1.`, `2.`) or bold dictionary terms instead of PART/CHAPTER headings. The slicer cannot detect those automatically; the top-level PARTs are the correct granularity for that book.
- **Wrong page boundaries:** force Stage 5 only by running without `OPENROUTER_API_KEY` — it scans every physical page and never relies on computed offsets.
- **Duplicate or out-of-order files:** clear `data/chapters/` before re-running to avoid mixing old and new outputs.

---

## Quick Command Reference

### Podcast

```bash
# Single chapter, full run
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf

# Single chapter, script only
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf --skip-audio

# Audio only from an existing script (no PDF, no LLM)
PYTHONPATH=src python src/cli/podcast.py \
  --skip-script \
  --script-file path/to/my_script.txt \
  --mode 2person

# Single chapter, 4-person mode
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf --mode 4person

# Single chapter, real-world context
PYTHONPATH=src python src/cli/podcast.py data/chapters/01_intro.pdf \
  --mode realworld --context "Your event text here"

# Whole book from single PDF
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5

# Slice only, inspect chapters
PYTHONPATH=src python src/cli/podcast.py --book books/mybook.pdf --toc-page 5 --slice-only

# Recover killed audio job
PYTHONPATH=src python src/tts/recover.py data/output/audio/01_intro/tts_job.json
```

### Fiction / Novel

```bash
# Generate seed project from a book
PYTHONPATH=src python -m fiction.seed_gen books/mybook.pdf data/my_novel/

# Dry run (via CLI wrapper)
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml --dry-run

# Run with approval gates (via CLI wrapper)
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml

# Auto-approve
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml --auto-approve

# Resume
PYTHONPATH=src python src/cli/fiction.py --config data/my_novel/config.toml --resume

# Run the novel pipeline package directly
PYTHONPATH=src python -m novel_pipeline --config data/my_novel/config.toml
```

### PDF Slicer

```bash
PYTHONPATH=src python src/slicer/pdf_splitter.py \
  -i books/mybook.pdf -p 10 --chapters-only
```

---

## Further Reading

- `initial_readme.md` — Authoritative developer reference.
- `podcast_friendly_user_guide.md` — Beginner-focused podcast walkthrough.
- `src/fiction/pipeline/config.example.toml` — Full novel config reference.
- `src/phases/` — Development phase notes.

