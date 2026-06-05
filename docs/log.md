# AI Agent Log — harnessv2
**Project:** Multi-Angle Learning Engine  
**Purpose of this file:** Running notes for AI agents. Cold-start this entire project in under 5 minutes by reading this file + `project_state.md`.

---

## Entry — 2026-05-28 — Claude Sonnet 4.6

### What I did
Full directory scan. Read every significant file. No code was run. No changes were made except writing this log and `project_state.md`.

### Summary in one paragraph
This is a pipeline project that processes books (PDFs) into multiple parallel learning formats: podcast scripts, a pedagogical cultivation novel, and eventually audio + animation. The main source book is "Mastering NLP from Foundations to LLMs," fully sliced into chapters. The podcast generator works locally (template-based). A full production-grade fiction pipeline (novel_pipeline v0.3.0, Python package) is implemented but has never completed a real run because the template content files (`world_laws.md`, `curriculum.md`, `style_contract.md`, `full_map.md`) are stubs. The actual design content for those templates exists in `.docx` and `.html` files inside `System design cultivation idea/` and needs to be converted.

---

## Key Paths — Memorize These

| Thing | Path |
|-------|------|
| Root | `/home/mr/Desktop/python/harness_design/harnessv2/` |
| Main code repo | `initial/` |
| Chapter PDFs (sliced) | `initial/chapters/` |
| Chapter slicer code | `initial/pdfslicer/pdf_splitter.py` |
| Local podcast generator | `initial/podcast_generator.py` |
| LLM-based podcast generator | `initial/pdf_to_api/` |
| Fiction pipeline package | `initial/fiction_automation/generic_novel_automatio/novel_pipeline/` |
| Fiction pipeline config | `initial/fiction_automation/generic_novel_automatio/novel_pipeline/config.toml` |
| Fiction pipeline templates (STUBS) | `initial/fiction_automation/generic_novel_automatio/novel_pipeline/templates/` |
| Novel design source docs | `System design cultivation idea/` |
| Simple one-file novel runner | `initial/fiction_automation/cultivation-novel/run.py` |
| Pipeline run log | `initial/fiction_automation/generic_novel_automatio/novel_pipeline/pipeline.log` |
| API keys (OpenRouter + WaveSpeed) | `api_keys.txt` |
| Full project state report | `project_state.md` |

---

## Architecture Rules (never violate these)

From `initial/harnessfiles/agents.md`:
1. Stages are scripts, not services. Input files → output files.
2. Stages never import each other. Communication is filesystem only.
3. All generators (podcast, fiction, animation) read from `data/processed/chapters/` — never from each other's output.
4. All paths are passed as arguments. No hardcoded paths.
5. Cloud API calls require explicit human confirmation before execution.
6. Never hardcode API keys — read from env vars.
7. Never commit processed data or outputs to git.

---

## What Is Confirmed Working (from file evidence)

- **Chapter slicer**: `initial/chapters/` has 100+ real sliced PDFs — it ran successfully.
- **Local podcast generator**: `initial/podcast_script_output/output.txt` is real podcast output from a run.
- **LLM podcast generator**: `initial/pdfslicer/output.txt` contains LLM-generated output from pdf_to_api/.

---

## What Is Confirmed NOT Working

- **novel_pipeline**: `pipeline.log` records 3 failed attempts on 2026-05-17, all crashing before any API call due to missing/empty templates.

---

## The One Critical Blocker

`initial/fiction_automation/generic_novel_automatio/novel_pipeline/templates/` contains stub/placeholder files:
- `world_laws.md` = "asfasfwetwetrasdfasdfasfasdf" (gibberish)
- `curriculum.md` = "todo"
- `style_contract.md` = "todo"
- `full_map.md` = "todo"
- `living_doc.md` = section headers only (required structure present, but no content)

The real content for these files lives in:
- `System design cultivation idea/Seed_1/Pass always_.docx` — world bible + concept curriculum + style contract
- `System design cultivation idea/Html/cultivation_system_design_full_map.html` — full system design map
- `System design cultivation idea/Seed_1/memory_palace_seed_document.docx` — living document template

**Fix:** Extract content from those .docx and .html files, convert to the required markdown format, write into the templates directory. Then re-run `novel-pipeline --config config.toml --dry-run` to validate.

---

## Two Different "Product Lines"

**Confusing aspect:** This project has two parallel output targets that share infrastructure but are about different subjects:

1. **NLP Book Processing** — Takes "Mastering NLP from Foundations to LLMs" → podcast scripts for each chapter → (eventually) audio files. This is the "learning about NLP" track.

2. **Cultivation Novel Generation** — Writes a pedagogical fantasy novel (xianxia/cultivation genre) that teaches system design concepts through a character named Amina. This is the "learning about distributed systems through fiction" track.

They use the same pipeline architecture and the same API infrastructure but are entirely different content. The chapter PDFs in `initial/chapters/` are from the NLP book. The novel template docs in `System design cultivation idea/` are for the cultivation novel.

---

## Novel Pipeline — How It Works (when templates are filled)

```
User runs: novel-pipeline --config config.toml
```

1. Loads 4 static template docs + living_doc.md
2. Shows pre-session summary (cost, tokens)
3. For N chapters per session:
   a. Sends all docs → OpenRouter → gets chapter text back
   b. Saves draft to `.rejected/chapter_NN__timestamp.md`
   c. Shows user: path + word count + first 200 chars
   d. User: [y]approve / [n]reject / [q]quit
   e. On approve: `os.replace` draft → `chapter_NN.md`
   f. Updates `.pipeline_state.json`
   g. Sends all docs + new chapter → OpenRouter → gets updated living doc
   h. Validates living doc structure (all required headers present and in order)
   i. Saves living doc atomically with timestamped backup
4. Exits, asks human to review, then re-run with `--resume`

State is tracked in `.pipeline_state.json` so any Ctrl-C is recoverable.

---

## Fiction Pipeline Code Status

| Module | Status | Notes |
|--------|--------|-------|
| `api.py` | Complete | Retries, cost gate, overflow detection, truncation detection |
| `cli.py` | Complete | argparse, exit codes |
| `config.py` | Complete | TOML loader, all knobs exposed |
| `cost.py` | Complete | Session + lifetime spend tracking |
| `docs.py` | Complete | Load/save/promote/validate |
| `exceptions.py` | Complete | 9-class hierarchy |
| `logging_.py` | Complete | JSONL |
| `prompts.py` | Complete | Configurable wrap/order |
| `requests_.py` | Complete | Chapter + living-doc request wrappers |
| `session.py` | Complete | Full loop with resume/interrupt handling |
| `state.py` | Complete | Gap-scan, state file, resume detection |
| `tokens.py` | Complete | tiktoken with fallback |
| `tests/test_pipeline.py` | Complete | 1349 lines, comprehensive coverage |
| **Templates** | **STUB** | **This is the only blocker** |

---

## TTS Pipeline — What Needs to Be Built

SESSION spec exists at: `initial/text_to_voice_api_calls/session.md`  
API: WaveSpeed VibeVoice  
Input: Two-speaker dialogue `.txt` file (same format as podcast scripts)  
Output: `.mp3` audio file  
SDK: `wavespeed` Python package  

The spec describes 5 functions: `read_script`, `build_api_payload`, `send_to_api`, `get_audio_url`, `download_and_save`. Build them in `text_to_voice_api_calls/main.py`.

---

## Harness Methodology (for new AI agents)

This project uses a "two-file harness" approach for AI sessions:
- `SESSION.md` — active task brief, loaded into AI context at start of session
- `AGENTS.md` — permanent constitution, never changes without deliberate amendment

Historical harness files in `initial/harnessfiles/` show the session history:
- `session_pdf_slicer.md` — session that built Stage 1
- `podcast_session.md` — session that built Stage 2a
- `agents.md` — current AGENTS.md constitution

The harness is designed for "most constrained case first": works for a chat AI with one context window and no file access. If it works there, it works everywhere.

---

## API Keys Present

- **OpenRouter**: `sk-or-v1-ed967f...` (in `api_keys.txt`)
- **WaveSpeed**: `64a68b8c7ccaafdb...` (in `api_keys.txt`)
- File is in the root, outside the git repo's `.gitignore` scope — **do not commit**

---

## Git Repository

Only `initial/` is a git repo. The root `harnessv2/` is NOT a git repo.  
The git repo in `initial/` has a `.gitignore`.

---

## Versions

- **novel_pipeline package**: v0.3.0
- **Python requirement**: 3.11+ (uses stdlib `tomllib`)
- **Primary model configured**: `anthropic/claude-opus-4` (in config.toml)
- **Dependencies**: requests, tiktoken, python-docx (in pyproject.toml of novel_pipeline)
