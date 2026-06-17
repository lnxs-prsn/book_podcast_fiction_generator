# Friendly User Guide — Book to Podcast

This tool turns any PDF book chapter into a real podcast episode with two voices talking about it.
You give it a PDF. It gives you an MP3.

This guide assumes you have never done this before. Every step is explained.

---

## What you will end up with

You put a PDF in a folder. You run one command. You get:

- A podcast script (a text file with two people having a conversation about your chapter)
- An MP3 audio file (those two people, voiced by AI, actually talking)

The whole thing takes about 10–15 minutes per chapter.

---

## What you need before you start

You need two things: an OpenRouter account and a WaveSpeed account. Both are free to sign up for.

### 1. OpenRouter API key (for the AI that writes the script)

1. Go to [openrouter.ai](https://openrouter.ai) and create a free account
2. Once logged in, go to **Keys** in the top menu
3. Click **Create Key**
4. Copy the key — it looks like `sk-or-v1-abc123...`
5. Save it somewhere safe (a text file on your desktop is fine)

### 2. WaveSpeed API key (for the AI that speaks the script)

1. Go to [wavespeed.ai](https://wavespeed.ai) and create a free account
2. Go to your account settings and find **API Keys**
3. Create a new key
4. Copy the key — it looks like `wsk_live_abc123...`
5. Save it somewhere safe

> **Note on costs:** OpenRouter has free models you can use at no charge. WaveSpeed charges a small amount per audio generation (typically a few cents per chapter). Make sure you have some credit loaded before running audio generation.

---

## One-time setup (you only do this once)

### Step 1 — Open a terminal

On Linux or Mac, open the **Terminal** app.
On Windows, open **Command Prompt** or **PowerShell**.

### Step 2 — Go to the project folder

Type this and press Enter (replace the path with wherever you saved the project):

```bash
cd /home/mr/Desktop/python/harness_design/harnessv3
```

### Step 3 — Check everything is installed

```bash
cd src
uv run python run_chapter.py --help
```

If you see a list of options, you are ready. If you see an error, check that `uv` is installed on your system.

---

## Putting your PDF in the right place

Find the folder called `data/chapters/` inside the project. Put your PDF file in there.

That is it. The tool will find it automatically.

If you have a whole book split into chapters, put all the chapter PDFs in that same folder. Name them with numbers at the start so they process in order — for example:

```text
01_chapter_introduction.pdf
02_chapter_getting_started.pdf
03_chapter_advanced_topics.pdf
```

---

## Running it — one chapter at a time

Open your terminal, go to the `src` folder, and run this command. Replace the parts in `< >` with your actual values.

```bash
OPENROUTER_API_KEY=<your-openrouter-key> WAVESPEED_API_KEY=<your-wavespeed-key> \
  uv run python run_chapter.py ../data/chapters/<your-file.pdf> --llm
```

**Example with a real file:**

```bash
OPENROUTER_API_KEY=sk-or-v1-abc123 WAVESPEED_API_KEY=wsk_live_xyz789 \
  uv run python run_chapter.py ../data/chapters/01_chapter_introduction.pdf --llm
```

### What you will see

The terminal will show you progress as it runs:

```text
Chapter  : 01_chapter_introduction.pdf
Generator: LLM (OpenRouter)
Mode     : 2person
Script   : data/output/scripts/01_chapter_introduction_podcast.txt
TTS submitted  request_id=abc123...
Recovery file  data/output/audio/01_chapter_introduction/tts_job.json
Polling for completion (status every 30s)...
  [35s] status=processing...
  [69s] status=processing...
  [done] 360s
Audio    : data/output/audio/01_chapter_introduction/1.mp3
```

This takes roughly 10–20 minutes. Leave the terminal open while it runs.

### Where to find your files when it is done

- **The script (text):** `data/output/scripts/01_chapter_introduction_podcast.txt`
- **The audio (MP3):** `data/output/audio/01_chapter_introduction/1.mp3`

---

## Running it — from a single whole-book PDF

If you have one big PDF of the entire book, you do not need to split it manually. Pass it with `--book` and the tool splits it into chapters automatically, then processes each one:

```bash
OPENROUTER_API_KEY=<your-openrouter-key> WAVESPEED_API_KEY=<your-wavespeed-key> \
  uv run python run_book.py --book /path/to/whole_book.pdf --llm
```

The slicer drops front matter (cover, copyright, table of contents, preface) and keeps only the real chapters.

If the table of contents in your book is not on page 8, tell it which page it is on:

```bash
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_book.py --book whole_book.pdf --toc-page 12 --llm
```

The chapter PDFs are saved to `data/chapters/` so you can inspect them before audio is generated.

### Recommended: check the chapters before spending any credits

Add `--slice-only` to slice the book and stop immediately — no AI calls, no cost. Open the files in `data/chapters/` and make sure each chapter looks right. Then run the full pipeline as a separate step:

```bash
# Step 1 — slice only, zero cost, inspect the results
uv run python run_book.py --book /path/to/whole_book.pdf --slice-only

# Step 2 — everything looks good? Now run the full pipeline
OPENROUTER_API_KEY=<your-openrouter-key> WAVESPEED_API_KEY=<your-wavespeed-key> \
  uv run python run_book.py --llm
```

The second command skips slicing automatically because the chapters are already there.

---

## Running it — a whole book at once (pre-split chapters)

If you have multiple chapter PDFs already in the `data/chapters/` folder, you can process them all in one go:

```bash
OPENROUTER_API_KEY=<your-openrouter-key> WAVESPEED_API_KEY=<your-wavespeed-key> \
  uv run python run_book.py --llm
```

It will go through every PDF in order. Chapters that have already been processed are skipped automatically, so you can safely run this again if something interrupted it.

When finished, a summary file is written to `data/output/run_summary.txt` showing which chapters succeeded and which (if any) failed.

**If you want to reprocess chapters that already have a script** (for example, you changed the mode or want a fresh take), add `--force`:

```bash
OPENROUTER_API_KEY=<your-openrouter-key> WAVESPEED_API_KEY=<your-wavespeed-key> \
  uv run python run_book.py --llm --force
```

**Real world mode for the whole book** — apply the same event context to every chapter:

```bash
# Inline event text
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_book.py --llm --mode realworld \
  --context "The EU just passed new AI regulations"

# Or from a file
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_book.py --llm --mode realworld \
  --context-file /home/mr/Desktop/event.txt
```

---

## Choosing a format (optional)

The default format is two people — a host and an expert — having a deep conversation about the chapter. You can change this with `--mode`:

| Mode | What it sounds like |
| --- | --- |
| `2person` | Host and expert, deep conversation (default) |
| `4person` | Four voices debating and discussing the content |
| `code` | Two voices focused on understanding the code and *why* it was written that way |
| `realworld` | The chapter connected to something happening in the world right now |
| `fiction_meta` | Two voices commenting on a fiction chapter from a novel pipeline |

> **Note:** `fiction_meta` is only available for single chapters (`run_chapter.py`), not the batch book runner.

**Example — 4 person format:**

```bash
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_chapter.py ../data/chapters/01_chapter.pdf --llm --mode 4person
```

**Example — real world mode, typing the event directly:**

```bash
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_chapter.py ../data/chapters/01_chapter.pdf --llm --mode realworld \
  --context "The EU just passed new regulations requiring AI transparency in hiring decisions"
```

**Example — real world mode, loading the event from a text file:**

If your event description is long, save it to a `.txt` file (e.g. `event.txt` on your desktop) and point to it instead:

```bash
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_chapter.py ../data/chapters/01_chapter.pdf --llm --mode realworld \
  --context-file /home/mr/Desktop/event.txt
```

**Example — fiction meta mode:**

This mode requires a matching fiction chapter file produced by the fiction pipeline. Point `--fiction-dir` at the folder containing those files:

```bash
OPENROUTER_API_KEY=... WAVESPEED_API_KEY=... \
  uv run python run_chapter.py ../data/chapters/01_chapter.pdf --llm --mode fiction_meta \
  --fiction-dir ../data/fiction_output/
```

The tool automatically matches the chapter number from the PDF filename to the correct fiction file in that folder.

---

## Checking the script before spending audio credits

Audio generation costs money. If you want to check what the script looks like before paying for audio, add `--skip-audio`:

```bash
OPENROUTER_API_KEY=<your-openrouter-key> \
  uv run python run_chapter.py ../data/chapters/01_chapter.pdf --llm --skip-audio
```

This is fast (1–2 minutes) and free. Open the `.txt` file in `data/output/scripts/` and read through it. If you are happy with it, run the full command without `--skip-audio` to generate the MP3.

---

## If something goes wrong

### "The terminal closed while audio was being generated"

Do not worry — the audio job is still running on WaveSpeed's servers. You do not need to resubmit it. Run this to download the finished audio:

```bash
WAVESPEED_API_KEY=<your-wavespeed-key> \
  uv run python src/tts/recover.py data/output/audio/<chapter-folder>/tts_job.json
```

Replace `<chapter-folder>` with the name of your chapter (it matches the PDF filename without the `.pdf`).

### "I get an error about OPENROUTER_API_KEY"

You forgot to include your API key in the command. Make sure the command starts with `OPENROUTER_API_KEY=your-key-here`.

### "I get a 401 error"

Your API key is wrong or has been revoked. Go back to your OpenRouter account, create a new key, and use that one.

### "I get a 429 error (rate limited)"

The free model you are using is very busy. The tool will retry automatically up to 4 times. If it still fails, wait a few minutes and try again.

### "The script is too short"

Some free AI models do not produce very long scripts even when asked. This is a known limitation of certain free-tier models. The script will still be a valid podcast episode — just shorter than the 30-minute target. You can try again later when a different model is automatically selected, or ask for help choosing a better model.

---

## Quick reference card

Copy-paste these commands, filling in your keys:

```bash
# One chapter — full run (script + audio)
cd src
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_chapter.py ../data/chapters/YOUR_FILE.pdf --llm

# One chapter — script only (no audio cost)
OPENROUTER_API_KEY=YOUR_KEY \
  uv run python run_chapter.py ../data/chapters/YOUR_FILE.pdf --llm --skip-audio

# One chapter — choose a format
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_chapter.py ../data/chapters/YOUR_FILE.pdf --llm --mode 4person

# One chapter — real world mode (inline event)
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_chapter.py ../data/chapters/YOUR_FILE.pdf --llm --mode realworld \
  --context "YOUR EVENT TEXT HERE"

# One chapter — real world mode (event from file)
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_chapter.py ../data/chapters/YOUR_FILE.pdf --llm --mode realworld \
  --context-file /path/to/event.txt

# One chapter — fiction meta mode
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_chapter.py ../data/chapters/YOUR_FILE.pdf --llm --mode fiction_meta \
  --fiction-dir ../data/fiction_output/

# Whole book — from a single PDF (auto-slice + process)
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_book.py --book /path/to/whole_book.pdf --llm

# Whole book — from pre-split chapters in data/chapters/
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_book.py --llm

# Whole book — force reprocess all (even already done chapters)
OPENROUTER_API_KEY=YOUR_KEY WAVESPEED_API_KEY=YOUR_KEY \
  uv run python run_book.py --llm --force

# Whole book — scripts only, no audio
OPENROUTER_API_KEY=YOUR_KEY \
  uv run python run_book.py --llm --skip-audio

# Recover audio after terminal closed
WAVESPEED_API_KEY=YOUR_KEY \
  uv run python src/tts/recover.py data/output/audio/CHAPTER_FOLDER/tts_job.json
```

---

## Still stuck?

Read the technical README at `src/README.md` for deeper details on configuration and all available options.
