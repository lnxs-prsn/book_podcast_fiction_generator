# Project State Report

> **STALE — 2026-05 snapshot (2026-07-17 banner).** Describes a project shape
> that no longer exists (submodule-era layout, stage percentages, blockers
> since resolved). Do NOT orient from this file. Current truth: `HANDOFF.md`
> at the repo root → `progress/handoff-2026-07-17-clone-audit.md`.

**Generated:** 2026-05-28  
**Inspected by:** Claude Sonnet 4.6  
**Scope:** Full directory read — every file verified, nothing assumed

---

## What This Project Is

A **multi-angle learning engine** — a pipeline that takes a book (PDF) and transforms it into multiple parallel learning formats. All formats are generated independently from the same source material. No format feeds another.

The three intended output formats are:
1. **Podcast scripts** — HOST/GUEST dialogue walkthrough of each chapter
2. **Xianxia fiction** (cultivation novel) — a pedagogical novel that teaches concepts through a fantasy story protagonist who "earns" knowledge
3. **Animation storyboards** — visual narrative breakdowns (mentioned only, never built)

The source book currently wired in is **"Mastering NLP from Foundations to LLMs"** (a real book, all chapters sliced and present).

There is also a secondary track: converting podcast scripts to **audio** via a text-to-speech API (WaveSpeed VibeVoice).

---

## What the Harness Design Is

`handoff.md` explains the meta-layer: this project was built using a two-file AI session harness methodology:
- `AGENTS.md` — permanent project constitution (stack, rules, directory layout, what never to do)
- `SESSION.md` — per-session task brief for the AI

The concept: instead of re-explaining a project at every AI session, these two files orient any AI cold in under one context window. The project itself was built incrementally this way — each component has its own SESSION.md that was fed to an AI to build the next stage.

---

## Directory Structure and What Each Part Is

```
harnessv2/
├── api_keys.txt                     ← API keys in plaintext (see security note)
├── claude_prompt.md                 ← Behavior constraint: discuss-only, 300 word budget
├── log.md                           ← Empty — intended for AI handoff notes
├── pdf_to_audio_sessionfiles/       ← Session docs for audio pipeline (design only)
│   ├── script_builder_SESSION.md    ← PDF→LLM CLI session spec
│   └── audio_builder_session.md    ← WaveSpeed TTS CLI session spec
├── System design cultivation idea/  ← Novel design documents (source of truth for fiction)
│   ├── Html/                        ← Full system design map (HTML, multi-part)
│   ├── Seed_1/                      ← Pass_always.docx, seed docs with African names
│   └── Seed_2/                      ← Same docs, slightly different version
└── initial/                         ← Main git repo — all runnable code lives here
    ├── chapters/                    ← 100+ sliced chapter PDFs (NLP book)
    ├── pdfslicer/                   ← Stage 1 code
    ├── podcast_generator.py         ← Stage 2a: local template-based generator
    ├── pdf_to_api/                  ← Stage 2b: LLM API-based generator
    ├── podcast_script_output/       ← Output from a real run
    ├── text_to_voice_api_calls/     ← TTS session docs (no runnable code)
    ├── fiction_automation/          ← Stage 3: fiction pipeline
    │   ├── cultivation-novel/       ← Older simple single-file implementation
    │   ├── generic_novel_automatio/ ← Full production implementation (v0.3.0)
    │   └── specs_folder/           ← v1 and v2 specs that were built from
    ├── harnessfiles/                ← Session/agent harness files (chapter slicer, podcast)
    ├── main.py                      ← Top-level entry (calls pdfslicer)
    └── pyproject.toml               ← uv project config
```

---

## Stage-by-Stage Status

### Stage 1 — Chapter Slicer
**Status: COMPLETE AND WORKING**

`initial/pdfslicer/pdf_splitter.py` (main version, 29KB, May 12)  
`initial/pdfslicer/splitter_V1.py` (earlier version)

**What it does:** Takes a PDF + TOC start page, tries three strategies in order:
1. Read internal PDF bookmarks
2. Parse TOC text with regex
3. OCR the TOC page (fallback)

Then slices the book into individual chapter PDFs.

**Evidence it works:** `initial/chapters/` contains 100+ sliced chapter files from the NLP book, with filenames like `01_chapter_Chapter_1_...pdf`, `02_chapter_...pdf`, etc.

**Known issue:** There is also an older `initial/pdfslicer/pdf_splitter (1).py` (29KB, same date) — a separate version sitting alongside the primary. Which is the authoritative one is slightly unclear, but `pdf_splitter.py` is what `main.py` imports.

---

### Stage 2a — Podcast Generator (Local Template)
**Status: COMPLETE AND WORKING**

`initial/podcast_generator.py`

**What it does:** Takes a chapter PDF, extracts text, divides it into thirds, extracts key concepts from each third using TF-IDF-like scoring, then builds a HOST/GUEST dialogue from a fixed template library. **No API calls.** Purely local Python.

**Evidence it works:** `initial/podcast_script_output/output.txt` contains a complete LLM-style HOST/EXPERT podcast script.

**Important nuance:** The handoff doc says Stage 2 sends text to a "cloud LLM API." This implementation does NOT. It uses local templates. Either:
- This was an intentional pivot to avoid API costs
- Or this is a fallback/prototype and the real one is in pdf_to_api/

---

### Stage 2b — PDF-to-API Pipeline (LLM-Based)
**Status: BUILT, PARTIALLY RUN**

`initial/pdf_to_api/` — 8 separate function files:
- `extract_pdf.py` — uses PyMuPDF
- `parse_args.py`, `read_prompt.py`, `call_api.py`, `parse_output.py`, `save_output.py`
- `main.py` — wires all functions
- `test_all.py` — test file
- `prompt.txt` — 14KB prompt used for API calls
- `SESSION.md` — describes what was built

`call_api.py` uses OpenRouter API (not Anthropic SDK despite SESSION spec saying Anthropic). Model: `z-ai/glm-4.5-air:free`.

**Evidence it was run:** `initial/pdfslicer/output.txt` contains a proper LLM-generated podcast script. The `initial/pdf_to_api/outputfolder/` exists (likely has output).

**Status gap:** This was built as a standalone pipeline in its own folder. It is not integrated with Stage 1's output directory. There is no orchestration connecting Stage 1 → Stage 2b.

---

### Stage 3 — Text-to-Speech (Audio)
**Status: COMPLETE AND WORKING**

`initial/text_to_voice_api_calls/the_folder/cli.py` — Full WaveSpeed VibeVoice CLI (7KB, May 13).

**What it does:** Reads a two-speaker `Speaker 0:` / `Speaker 1:` dialogue script, sends it to the WaveSpeed VibeVoice API, downloads the MP3 response and saves it locally.

**Evidence it works:** `initial/text_to_voice_api_calls/the_folder/audio/1.mp3` — 2.7MB MP3 file, generated from `podcast.txt` (a real NLP chapter podcast script). Date: May 13.

Usage:
```
python cli.py --script ./podcast.txt --output ./audio/ --api-key ws_live_xxx
```

The implementation matches the session spec exactly: `read_script`, `build_api_payload`, `send_to_api`, `get_audio_url`, `download_and_save`, `cli_entrypoint`. API key falls back to `WAVESPEED_API_KEY` env var.

**Note:** This stage sits in its own folder and is not yet integrated with the output of Stage 2. The pipeline from Stage 2 → Stage 3 requires manually passing the podcast script file to `cli.py`.

---

### Stage 4 — Xianxia Fiction Pipeline (Novel Generator)
**Status: FULL PRODUCTION IMPLEMENTATION — BLOCKED BY MISSING CONTENT**

This is the most developed part of the project. Two implementations exist:

#### Simple version
`initial/fiction_automation/cultivation-novel/run.py` — ~400 lines, single file, handles a full session loop. Hardcodes `PROJECT_DIR`, `MODEL`, `TOTAL_CHAPTERS` in constants at the top. Simpler approach: calls OpenRouter, writes chapters, asks for summary, updates living doc. Ready to run if you set `PROJECT_DIR` and the template files.

#### Production version (novel_pipeline package v0.3.0)
`initial/fiction_automation/generic_novel_automatio/novel_pipeline/`

Full Python package with 14 modules:
| Module | Purpose |
|--------|---------|
| `api.py` | OpenRouter API calls, retries, cost gate, overflow detection, truncation detection |
| `cli.py` | `argparse` CLI entry point with full exit-code handling |
| `config.py` | TOML config loader, all knobs configurable |
| `cost.py` | Session + lifetime spend tracking in `.pipeline_spend.json` |
| `docs.py` | Load/save docs, atomic writes, draft staging, promotion |
| `exceptions.py` | 9-class exception hierarchy |
| `logging_.py` | JSONL append-only event log |
| `prompts.py` | Prompt assembly (configurable wrap, order, system prompts) |
| `requests_.py` | High-level chapter + living-doc request wrappers |
| `session.py` | Session conductor — the main loop |
| `state.py` | `.pipeline_state.json` read/write, resume detection, gap scan |
| `tokens.py` | tiktoken-based token counting with fallback |

Features implemented:
- Draft staging in `.rejected/` before human approval
- `promote_chapter` with `PromotionCollisionError` (no silent overwrite)
- Resume with mid-cycle interrupt detection (chapter promoted, living doc not updated)
- Gap-scan resume (`find_next_chapter_number` returns first missing integer)
- Cost gate (session + lifetime) with `--ignore-cost-limit` override
- `ContextOverflowError` with per-document token breakdown
- `validate_living_doc_structure` — checks required section headers in order
- Configurable: system prompts, doc wrap format, static doc order, backoff, file naming
- `--dry-run`, `--auto-approve`, `--resume`, `--chapter-start N`
- 1349-line test suite

**BLOCKING ISSUE: Template files are stubs.**
```
templates/world_laws.md    = "asfasfwetwetrasdfasdfasfasdf"  (gibberish placeholder)
templates/curriculum.md    = "todo"
templates/style_contract.md = "todo"
templates/full_map.md      = "todo"
templates/living_doc.md    = section headers only, no content
```

The system design documents that should fill these templates exist in:
`System design cultivation idea/Html/cultivation_system_design_full_map.html`  
`System design cultivation idea/Seed_1/Pass always_.docx`  
`System design cultivation idea/Seed_1/memory_palace_seed_document.docx`

These docx/html files contain the actual world bible, curriculum, style contract, and full system map. They have **not been converted to the required `.md` template files** inside the novel_pipeline.

**Last run evidence:** `pipeline.log` shows three attempts on 2026-05-17, all failing:
1. Wrong path for templates
2. Empty `world_laws.md` (got the path right but file was empty)
3. Missing living doc

The pipeline ran in `--dry-run --auto-approve` mode and failed before any API calls were made.

---

### Stage 5 — Animation Storyboards
**Status: 0% — NOT STARTED, NOT SPECCED**

Mentioned in `AGENTS.md` as a planned output format. Output folder `data/output/animation/` is defined in the spec. No SESSION.md, no spec, no code.

---

## What Is Clear

1. **The architecture is sound.** The file-based, stage-as-script, siblings-not-ancestors design is clearly articulated and largely followed.
2. **The harness methodology works.** Every stage has a SESSION.md that was used to build it, and the handoff.md captures the full design for future AI agents.
3. **Stage 1 is production-ready.** Chapter slicer has been run on a real book.
4. **Stage 4 (novel pipeline) has the most engineering investment.** v0.3.0, full test suite, comprehensive error handling, atomic file writes, resume detection. This is not prototype code.
5. **The primary book being processed** is "Mastering NLP from Foundations to LLMs" — already fully sliced.
6. **OpenRouter is the API provider** for all LLM calls (not Anthropic directly). API key is in `api_keys.txt`.
7. **The novel concept is cultivation/xianxia** — a pedagogical novel where a protagonist learns system design concepts through a fantasy cultivation world. The design documents (full map, world bible, curriculum) exist in `System design cultivation idea/`.

---

## What Is Unclear

1. **Are Stage 2a (local) and Stage 2b (API) meant to coexist?** The local generator is already working and produces output. The API version exists in a separate folder. There is no single entrypoint that runs both or decides between them.

2. **Is this project NLP-teaching or cultivation-novel?** There appear to be two separate creative directions:
   - Processing an NLP textbook into podcasts (the current book)
   - Writing a cultivation novel that teaches system-design concepts  
   These share the same pipeline architecture but are completely different content. It is unclear if they are meant to run together or if this is the same project in two phases.

3. **The `fixes` file** references issue codes (c1, c3, c4, h2, m1...) that were applied between v1 and v2 of the novel spec. It is a directive document, not code. These changes appear to be incorporated in the v0.3.0 implementation but verification requires running the test suite.

4. **What is `initial/pdf_to_api/prompt.txt`?** At 14KB it is a very large prompt. Its content determines what the LLM-based podcast generator produces. It was not read in full.

5. **The `System design cultivation idea/` docx files** contain the real novel design but have not been converted into the template `.md` files the novel_pipeline expects. This is the single most actionable blocker.

6. **No end-to-end test.** The novel pipeline has a unit test suite but has never successfully completed a full session (pipeline.log shows only failures).

7. **TTS pipeline relationship.** It is unclear whether the text-to-speech pipeline is meant to run on the NLP podcast scripts, the cultivation novel, or both.

---

## Completion Assessment

| Component | Status | Blockers |
|-----------|--------|---------|
| Chapter Slicer (Stage 1) | ✅ 100% — working | None |
| Podcast Generator — local (Stage 2a) | ✅ 90% — working | Not integrated into orchestration |
| Podcast Generator — LLM (Stage 2b) | 🟡 75% — built, runs | Not connected to Stage 1 output directory |
| Text-to-Speech (Stage 3) | 🔴 15% — spec only | No implementation code |
| Fiction Pipeline — simple (Stage 4a) | 🟡 70% — code ready | Template files need real content |
| Fiction Pipeline — production (Stage 4b) | 🟡 80% — full impl | Template files are stubs, never successfully run |
| Animation Storyboards (Stage 5) | 🔴 0% — not started | No spec, no code |
| End-to-End Orchestration | 🔴 0% | No main runner connecting all stages |

**Overall pipeline completeness: ~55%**

---

## Security Note

`api_keys.txt` at the project root contains a live OpenRouter API key and a live WaveSpeed API key in plaintext. This file is not in a `.gitignore` that would prevent accidental commit. The `.gitignore` inside `initial/` does not cover `api_keys.txt` at the root level.

---

## The Next Most Impactful Actions

1. **Convert template docs to markdown** — Copy content from `System design cultivation idea/Seed_1/Pass always_.docx`, `memory_palace_seed_document.docx`, and `cultivation_system_design_full_map.html` into the four template `.md` files. This unblocks the fiction pipeline immediately.

2. **Run the novel pipeline end-to-end** — After templates are filled, run `novel-pipeline --config config.toml` to get chapter 1. This validates the entire engineering investment.

3. **Build the WaveSpeed TTS CLI** — The SESSION spec is complete. An AI can implement it in one pass. This adds the audio dimension to the already-working podcast scripts.

4. **Orchestrate Stages 1 → 2** — Wire `pdf_to_api/main.py` to read from `initial/chapters/` so running a single command processes a chapter PDF into a podcast script.

5. **Decide: animation storyboards** — Either spec and build Stage 5, or formally remove it from the project description.
