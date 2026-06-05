# Fiction Pipeline — State of Existence

Audit date: 2026-06-05

---

## Vision (from vision.md)

```
2. turns book or chapter to fiction
A. first section of the process is human dependent world rules, living document etc
B. this section just automates the fiction generation using files section 2.A produced
```

---

## 2A — Human-dependent seed documents

**Status: in place, ready.**

Two seed sets exist:

### Seed_1 — Systems Cultivation novel
`System design cultivation idea/Seed_1/`
- `Pass always_.docx` — world bible + curriculum + style contract (combined)
- `Seed_document_clean_african_names.docx` — protagonist naming pass
- `Seed_document_update_used_term_count.docx` — term tracking pass
- `Ds_chapters/1.docx` through `10.docx` — draft chapters 1–10
- `Ds_chapters/LD_6.docx` — living doc snapshot at chapter 6
- `Ds_chapters/Seed_doc.docx`

### Seed_2 — Memory Palace novel
`System design cultivation idea/Seed_2/`
- `memory_palace_seed_document.docx`

### Extracted templates
The Seed_1 content has been broken out into 5 pipeline-ready template files at `src/fiction/pipeline/templates/`:

| File | Purpose |
|---|---|
| `world_laws.md` | World bible — cultivation stages map to system architecture |
| `curriculum.md` | Concept curriculum — which systems concepts taught in which arc |
| `style_contract.md` | Writing voice rules (declarative, physical-before-philosophical) |
| `full_map.md` | System design ↔ cultivation full mapping reference |
| `living_doc.md` | Template structure for the mutable living doc |

All 5 templates are populated. `full_map.md` is 160 lines of dense content: infrastructure tables, realm-progression mapping, combat/operations equivalences, failure modes, time-scaling chart, and concrete prose examples with the system-design metaphors applied.

### Live working copy
`src/fiction/pipeline/living_doc.md` is seeded and current:
- Protagonist: Amina
- Current chapter: 0 (not yet started)
- Arc 1 target terms set: decentralization, asynchrony, single point of failure
- Chapter 1 target written in `--- NEXT CHAPTER TARGET ---`
- No chapters produced yet

---

## 2B — Automated fiction generation

**Status: fully implemented, zero chapters produced.**

The `novel_pipeline` package lives at `src/fiction/pipeline/novel_pipeline/`. It is a complete, production-grade CLI installable via `pip install -e .`.

### Entry point
```bash
export OPENROUTER_API_KEY=sk-or-...
novel-pipeline --config src/fiction/pipeline/config.toml
```

Subsequent sessions:
```bash
novel-pipeline --config src/fiction/pipeline/config.toml --resume
```

### What it does per chapter cycle
1. Loads all 5 static templates + living doc into prompt
2. Calls OpenRouter API (`claude-opus-4` configured, any model works)
3. Validates response ≥ 1500 words; rejects silently short chapters
4. Saves draft to `.rejected/` (staging)
5. Shows human: path + word count + first 200 chars
6. Human approval gate `[y/n/q]`
7. On approval: atomically promotes draft to `chapter_NN.md`
8. Calls API for living doc update
9. Validates all required section headers present and in order
10. Atomically saves updated living doc with timestamped backup

### Safety features
| Guarantee | Mechanism |
|---|---|
| No silent fresh-starts | Aborts if chapters exist without `--resume` |
| No silent truncation | Checks `finish_reason`; rejects `length` stops |
| No silent context overflow | `ContextOverflowError` with per-doc token breakdown |
| No silent cost overruns | Pre-flight + post-call cost gating (session + lifetime) |
| No narrative drift | Structural validation of living doc headers after every update |
| Interrupt recovery | `.pipeline_state.json` tracks `last_promoted` vs `last_doc_updated`; mismatch detected on `--resume` |
| Bounded rejection loop | `max_rejection_retries = 5` cap |

### Flags
| Flag | Effect |
|---|---|
| `--resume` | Continue from existing chapters; detects interrupt-mid-cycle |
| `--auto-approve` | Skip all interactive prompts |
| `--dry-run` | Full run without API calls or file writes |
| `--chapter-start N` | Force next chapter number (warns on gaps) |
| `--ignore-cost-limit` | Bypass cost gates |

### Output layout produced
```
src/fiction/pipeline/chapters/
  chapter_01.md
  chapter_02.md
  .rejected/
    chapter_03__<timestamp>.md    ← rejected drafts kept as audit trail
living_doc.md
living_doc.md.bak.<timestamp>     ← one backup per approved chapter
pipeline.log                      ← JSONL events
.pipeline_spend.json
.pipeline_state.json
```

### Config
`src/fiction/pipeline/config.toml` — live config, points at the templates above.
`src/fiction/pipeline/config.example.toml` — annotated reference with all knobs.

Current model: `anthropic/claude-opus-4`
Session cost limit: $5.00 | Lifetime limit: $50.00
Chapters per session: 3

### Also present
`src/fiction/run_simple.py` — earlier standalone script, same loop but no approval gate, no cost gating, no atomic writes. Superseded by `novel_pipeline`.

### Module layout
```
novel_pipeline/
  cli.py          argparse + exit-code mapping
  config.py       TOML load, defaults, env overrides, validation
  session.py      run_session: the conductor
  requests_.py    request_chapter / request_living_doc_update
  api.py          call_api: retries, pre-flight, cost gate, finish_reason
  prompts.py      build_prompt (config-driven wrapping)
  docs.py         load/save docs, draft staging, promote, validation
  state.py        .pipeline_state.json, find_next_chapter_number, detect_resume_state
  cost.py         estimate_cost, track_spend
  tokens.py       count_tokens (tiktoken + configurable fallback)
  logging_.py     JSONL event log
  exceptions.py   PipelineError + subclasses
```

---

## 2C — TTS for fiction

**Status: does not exist. Not described in vision.md either.**

The podcast pipeline has a TTS layer (`src/tts/`). Nothing equivalent exists for fiction output.

---

## What's needed before first run

The pipeline dry-runs cleanly (all docs load, cost estimate fires). Only one thing is missing:

1. Set `OPENROUTER_API_KEY`
2. Run from `src/fiction/pipeline/`: `novel-pipeline --config config.toml`

(`novel_pipeline` is already installed — `__pycache__` confirms it has been run.)
