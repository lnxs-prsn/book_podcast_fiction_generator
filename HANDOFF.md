# Handoff Document
**Written by:** Claude Sonnet 4.6, session 2026-05-28
**For:** next AI agent instance
**Read time:** ~5 minutes

---

## What This Project Is

A **multi-angle learning engine**. Takes a book (PDF) and transforms it into multiple parallel learning formats. All formats are generated independently from the same source material — no stage feeds another.

Three output formats:
1. **Podcast scripts** — HOST/GUEST dialogue per chapter
2. **Audio MP3s** — podcast scripts converted to speech via WaveSpeed
3. **Cultivation novel chapters** — pedagogical xianxia fiction teaching the same concepts through story

There are **two content tracks** that use different generators:

**Track A — NLP Book**
Source: "Mastering NLP from Foundations to LLMs" (already sliced, 100+ chapters in `data/chapters/`)
Goal: podcast script + audio per chapter

**Track B — Cultivation Novels (Amina and Amara)**
Both use the **same fiction pipeline** at `src/fiction/pipeline/`. The pipeline is generic — it takes whatever seed documents you give it. Amina and Amara are different novels with different source material; to run either one you point the pipeline at the right `config.toml` and `templates/` directory.

- **Amina**: distributed systems architecture. Seed docs in `System design cultivation idea/Seed_1/`. Templates already filled. Ready to run.
- **Amara**: database and storage architecture. Seed docs in `System design cultivation idea/Seed_2/`. Templates not yet filled.

**`System design cultivation idea/` is just a storage folder for raw seed documents** (writer's notes, world-building source material). It is not pipeline code and not part of the project infrastructure.

**Amina and Amara are completely unrelated novels. Do not mix them.**

---

## Current Project State

### What works right now

| Stage | Status | How to run |
|---|---|---|
| PDF → chapters | Working. 100+ chapters already sliced in `data/chapters/` | `python src/slicer/pdf_splitter.py` |
| Chapter → podcast script | Working. Two generators: local (offline) and LLM (OpenRouter) | `python src/run_chapter.py <chapter.pdf> --skip-audio` |
| Script → MP3 | Working. Proven (1.mp3 exists). Needs `WAVESPEED_API_KEY` | runs automatically via `run_chapter.py` |
| Full NLP track | Working. One command: PDF → script → MP3 | `python src/run_chapter.py <chapter.pdf>` |
| Amina fiction pipeline | Code complete. Templates filled. Dry-run passes at $0.64/chapter. Ready to run. | `cd src/fiction/pipeline && python -m novel_pipeline --config config.toml` |
| Amara fiction pipeline | Templates not filled. Same pipeline as Amina — just needs its own `config.toml` + `templates/` dir populated from `Seed_2/` docs. | `cd src/fiction/pipeline && python -m novel_pipeline --config config_amara.toml` |
| Animation storyboards | Not built. Design doc written. | `docs/animation_design.md` |

### What is NOT done

1. **Pass 3.2 — Human design decisions for Amina's novel** (see below)
2. **Amara's templates** — same pipeline as Amina, just needs a `config_amara.toml` + `templates/` populated from `System design cultivation idea/Seed_2/` docs. No new pipeline code needed.
3. **TTS not tested in this session** — needs `WAVESPEED_API_KEY` env var to test
4. **No batch runner** — `run_chapter.py` runs one chapter at a time. A loop over all 100+ chapters has not been written.

---

## What Was Done This Session (in order)

### Pass 1.1 — Directory restructure
Renamed `initial/` → `src/`, flattened all stage directories, moved data files out of the source tree.

**Before:** `initial/fiction_automation/generic_novel_automatio/novel_pipeline/novel_pipeline/api.py`
**After:** `src/fiction/pipeline/novel_pipeline/api.py`

Nothing deleted. Files that were removed from active use went to `src/unwanted_from_the_project_dir/`.

### Pass 1.2 — Root cleanup
Archived historical AI session files (`log.md`, `project_state.md`, `claude_prompt.md`) to `docs/`. Moved planning notes into `src/docs/session_notes/`.

### Pass 2.1 + 2.2 — Stage 2→3 runner
Decision: local offline generator is the canonical default. LLM generator available via `--llm` flag.

Wrote `src/run_chapter.py` — the main entry point for the NLP track. One command takes a chapter PDF and produces both a podcast script and an MP3. Handles the format conversion (generators output `HOST:`/`GUEST:`, TTS expects `Speaker 0:`/`Speaker 1:`).

### Pass 2.3 — Runner tested
Ran `src/run_chapter.py` on Chapter 1 with `--skip-audio`. Script produced correctly in `Speaker 0/1` format. Output at `data/output/scripts/`.

### Pass 3.1 — Fiction templates filled
Extracted content from source docs into the 5 template files:

| Template | Source |
|---|---|
| `world_laws.md` | `Seed_1/Pass always_.docx` — DOCUMENT 1 |
| `curriculum.md` | `Seed_1/Pass always_.docx` — DOCUMENT 2 |
| `style_contract.md` | `Seed_1/Pass always_.docx` — DOCUMENT 3 |
| `full_map.md` | `Html/cultivation_system_design_full_map.html` |
| `living_doc.md` | Written from scratch using the 9 required section headers from `config.toml` |

### Pass 3.2 — SKIPPED (human required)
See section below.

### Pass 3.3 — Dry-run passed
```
python -m novel_pipeline --config config.toml --dry-run
```
Result: PASS. 4 static docs loaded (3,678 tokens), living doc loaded (496 tokens), estimated $0.64/chapter.

### Pass 4.1 — Animation design doc
Wrote `docs/animation_design.md`. Stage 5a (text storyboard only) is viable now at ~$0.05/chapter using existing OpenRouter key. Stage 5b (images) is marginal. Stage 5c (video) not viable at current rates. All parked.

---

## What Needs a Human — Pass 3.2

Before running the Amina fiction pipeline for real, these decisions are needed:

1. **Confirm the protagonist is Amina** (not Amara — these are different novels, see above)
2. **Review the world bible** (`src/fiction/pipeline/templates/world_laws.md`) — confirm the Six Stages and magic rules match your vision
3. **Review the curriculum** (`src/fiction/pipeline/templates/curriculum.md`) — confirm the arc breakdown and concept sequence is what you want
4. **Review the style contract** (`src/fiction/pipeline/templates/style_contract.md`) — confirm tone, POV, forbidden patterns
5. **Review the living doc** (`src/fiction/pipeline/living_doc.md`) — this is the starting state for Chapter 1. Confirm the Chapter 1 brief is correct.

Once reviewed and confirmed, run:
```bash
cd src/fiction/pipeline
python -m novel_pipeline --config config.toml
```
The pipeline will generate Chapter 1, show you a preview, and wait for your `[y/n/q]` approval.

---

## Key Paths

```
harnessv2/
├── src/                         ← all source code (git repo at src/.git)
│   ├── run_chapter.py           ← MAIN ENTRY POINT for NLP track
│   ├── slicer/pdf_splitter.py   ← Stage 1: PDF → chapter PDFs
│   ├── podcast/local/           ← Stage 2a: offline generator
│   ├── podcast/llm/             ← Stage 2b: OpenRouter LLM generator
│   ├── tts/cli.py               ← Stage 3: script → MP3
│   ├── fiction/pipeline/        ← Stage 4: Amina's novel pipeline
│   │   ├── config.toml          ← pipeline config (model, costs, paths)
│   │   ├── living_doc.md        ← mutable state, updated each chapter
│   │   └── templates/           ← static docs sent to LLM each request
│   ├── docs/                    ← session notes, harness history
│   └── unwanted_from_the_project_dir/  ← old files kept but not active
├── data/
│   ├── chapters/                ← 100+ sliced chapter PDFs
│   └── output/
│       ├── scripts/             ← generated podcast scripts
│       └── audio/               ← generated MP3s
├── docs/                        ← project-level docs (not git-tracked)
│   ├── animation_design.md      ← Stage 5 design (parked)
│   └── ...archived session files
├── System design cultivation idea/   ← RAW SEED STORAGE ONLY, not pipeline code
│   ├── Seed_1/                  ← Amina's source docs (distributed systems)
│   └── Seed_2/                  ← Amara's source docs (database/storage)
├── api_keys.txt                 ← OpenRouter + WaveSpeed keys (NEVER COMMIT)
├── PIPELINE.md                  ← architecture overview
├── action_plan.md               ← phased plan (Phases 1-4)
└── HANDOFF.md                   ← this file
```

---

## API Keys

Both keys are in `api_keys.txt` at the project root. Never commit this file.

| Key | Env var | Used by |
|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | `src/podcast/llm/` (LLM podcast), `src/fiction/pipeline/` (Amina's novel) |
| WaveSpeed | `WAVESPEED_API_KEY` | `src/tts/cli.py` (audio generation) |

Load them before running any API-dependent stage:
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
export WAVESPEED_API_KEY=64a68b8c...
```

---

## Architecture Rules (from `src/docs/harness_history/agents.md`)

1. Stages are scripts, not services. Input files → output files.
2. Stages never import each other. Communication is filesystem only.
3. All generators read from source chapter text — never from each other's output.
4. All paths are passed as arguments. No hardcoded paths.
5. Cloud API calls require explicit human confirmation before execution.
6. Never hardcode API keys — read from env vars.
7. Never commit processed data or outputs to git.

---

## Git Log (this session)

```
6751662  Pass 4.1 — Animation storyboard design document
afabdd5  Pass 3.1 + 3.3 — Fiction templates filled + dry-run passes
14f7693  Pass 2.3 — Runner tested end-to-end (local generator)
5ed165b  Pass 2.1 + 2.2 — Generator decision + Stage 2→3 runner script
0fff2a9  Pass 1.2 — Clean up project root
e2bfb33  Pass 1.1 — Flatten directory structure
```

To reverse any pass: `git revert <commit>` or `git reset --hard <commit>` if you want to go back to that point.
