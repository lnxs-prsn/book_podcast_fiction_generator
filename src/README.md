# Book-to-Podcast Pipeline

Converts PDF book chapters into fully produced podcast episodes: PDF → LLM script → MP3 audio.

---

## How it works

1. **PDF extraction** — text is pulled from the chapter PDF
2. **Script generation** — an LLM (via OpenRouter or any OpenAI-compatible provider) writes a podcast script in your chosen format
3. **TTS synthesis** — WaveSpeed VibeVoice converts the script to a multi-speaker MP3

---

## Prerequisites

| Requirement | Purpose |
| --- | --- |
| Python 3.11+ with [uv](https://github.com/astral-sh/uv) | Runtime and dependency management |
| OpenRouter API key | LLM script generation |
| WaveSpeed API key | Text-to-speech audio |

Get keys at [openrouter.ai](https://openrouter.ai) and [wavespeed.ai](https://wavespeed.ai).

---

## Project layout

```text
harnessv3/
├── data/
│   ├── chapters/          # Input: drop your PDF chapters here
│   └── output/
│       ├── scripts/       # Generated podcast scripts (.txt)
│       ├── audio/         # Generated MP3s (one folder per chapter)
│       └── run_summary.txt
└── src/
    ├── config.json        # Model, voice, and API configuration
    ├── run_chapter.py     # Single chapter runner
    ├── run_book.py        # Batch runner (all chapters)
    └── tts/
        └── recover.py     # Recover audio if process is killed mid-run
```

---

## Configuration — `src/config.json`

```json
{
  "api_url":       "https://openrouter.ai/api/v1/chat/completions",
  "model":         "openrouter/free",
  "max_tokens":    8192,
  "speakers": {
    "speaker_1":   "en-Alice_woman",
    "speaker_2":   "en-Carter_man",
    "speaker_3":   "en-Maya_woman",
    "speaker_4":   "en-Frank_man"
  },
  "wavespeed_model": "microsoft/vibevoice",
  "tts_scale":     1.3
}
```

All fields can also be overridden with environment variables (highest priority):

| Field | Env var override |
| --- | --- |
| `api_url` | `OPENROUTER_URL` |
| `model` | `OPENROUTER_MODEL` |
| `max_tokens` | `OPENROUTER_MAX_TOKENS` |

### Switching LLM provider

Any OpenAI-compatible API works — just update `api_url` and `model`:

```json
"api_url": "https://api.groq.com/openai/v1/chat/completions",
"model":   "llama-3.3-70b-versatile"
```

No code changes required.

---

## Running a single chapter

```bash
cd src

# LLM script + TTS audio (full pipeline)
OPENROUTER_API_KEY=sk-or-... WAVESPEED_API_KEY=wsk_live_... \
  uv run python run_chapter.py ../data/chapters/03_chapter_foo.pdf --llm

# Script only — skip TTS (useful for checking word count first)
OPENROUTER_API_KEY=sk-or-... \
  uv run python run_chapter.py ../data/chapters/03_chapter_foo.pdf --llm --skip-audio

# Choose a mode (default: 2person)
OPENROUTER_API_KEY=sk-or-... WAVESPEED_API_KEY=wsk_live_... \
  uv run python run_chapter.py ../data/chapters/03_chapter_foo.pdf --llm --mode 4person
```

Output written to:

- `data/output/scripts/<stem>_podcast.txt`
- `data/output/audio/<stem>/1.mp3`

---

## Running the full book

```bash
cd src

OPENROUTER_API_KEY=sk-or-... WAVESPEED_API_KEY=wsk_live_... \
  uv run python run_book.py --llm --mode 2person
```

Chapters that already have a script are skipped unless you pass `--force`.

```bash
# Force reprocess everything
uv run python run_book.py --llm --force

# Scripts only, no audio
uv run python run_book.py --llm --skip-audio
```

A summary is written to `data/output/run_summary.txt` after each run.

### Starting from a whole-book PDF

Pass `--book` to slice the PDF into chapters first (chapters-only, front matter dropped), then process all chapters in one command:

```bash
OPENROUTER_API_KEY=sk-or-... WAVESPEED_API_KEY=wsk_live_... \
  uv run python run_book.py --book /path/to/whole_book.pdf --llm

# If the Table of Contents is not on page 8, specify it:
uv run python run_book.py --book whole_book.pdf --toc-page 12 --llm

# Preview what the slicer would produce without writing files:
uv run python run_book.py --book whole_book.pdf --llm --skip-audio

# Skip OCR (faster on text-native PDFs):
uv run python run_book.py --book whole_book.pdf --no-ocr --llm
```

If `data/chapters/` already contains PDFs, the slice step is skipped automatically. Add `--force` to re-slice.

### Dry-run before spending API credits

Use `--slice-only` to slice and stop — no LLM or TTS calls made. Inspect the chapter PDFs in `data/chapters/` before committing to API usage:

```bash
# Step 1 — slice only, check the chapters
uv run python run_book.py --book whole_book.pdf --slice-only

# Step 2 — satisfied? Run the full pipeline (slicing skipped automatically)
OPENROUTER_API_KEY=sk-or-... WAVESPEED_API_KEY=wsk_live_... \
  uv run python run_book.py --llm
```

---

## Modes

| Mode | Speakers | Description |
| --- | --- | --- |
| `2person` | HOST Alex + EXPERT Jordan | Technical deep-dive, storytelling format. Target ~4,000 words / 30 min. |
| `4person` | 4 voices | Same content with debate and tension across multiple perspectives. |
| `code` | 2 voices | Code-dense material — focuses on the *why* behind engineering decisions, not just the *what*. |
| `realworld` | 2 voices | Connects the chapter to a current real-world event you provide. |
| `fiction_meta` | 2 voices | Meta-commentary on a fiction chapter (requires separate fiction pipeline output). |

### realworld mode

You supply the event — the model has no internet access.

```bash
# Inline
uv run python run_chapter.py chapter.pdf --llm --mode realworld \
  --context "OpenAI just released GPT-5 with native code execution"

# From file
uv run python run_chapter.py chapter.pdf --llm --mode realworld \
  --context-file ./event.txt
```

### fiction_meta mode

Requires a matching fiction chapter file from a separate fiction pipeline run.

```bash
uv run python run_chapter.py chapter.pdf --llm --mode fiction_meta \
  --fiction-dir ./data/fiction_output/
```

The runner matches the PDF chapter number to the corresponding `chapter_NN.md` file automatically.

---

## Recovering a killed TTS job

TTS generation takes 6–20 minutes. If the process is killed mid-run, the WaveSpeed job keeps running. Recover the audio without resubmitting:

```bash
WAVESPEED_API_KEY=wsk_live_... \
  uv run python src/tts/recover.py data/output/audio/<chapter_stem>/tts_job.json
```

`tts_job.json` is written immediately after submission, before polling begins.

---

## Voice options

WaveSpeed VibeVoice voices used by default:

| Role | Default voice |
| --- | --- |
| Speaker 0 (HOST) | `en-Alice_woman` |
| Speaker 1 (EXPERT) | `en-Carter_man` |
| Speaker 2 (4-person only) | `en-Maya_woman` |
| Speaker 3 (4-person only) | `en-Frank_man` |

Change voices in `src/config.json` under `speakers`.

---

## Environment variables reference

| Variable | Required | Description |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Yes (LLM) | OpenRouter API key |
| `WAVESPEED_API_KEY` | Yes (audio) | WaveSpeed API key |
| `OPENROUTER_URL` | No | Override `api_url` from config.json |
| `OPENROUTER_MODEL` | No | Override `model` from config.json |
| `OPENROUTER_MAX_TOKENS` | No | Override `max_tokens` from config.json |
| `OPENROUTER_RETRY_AFTER` | No | Fixed retry wait in seconds |
| `WAVESPEED_SCALE` | No | Override `tts_scale` from config.json |
