# book_podcast_fiction_generator

Turn a non-fiction book into **fiction that teaches its concepts** — or into a
multi-speaker **podcast**. Two subsystems share one Python codebase: a batch
pipeline that ingests and converts books, and an agentic loop that writes a
novel chapter by chapter under deterministic quality gates.

---

## The idea

Most "explain this book" tools summarise. This one does something else: it reads a
non-fiction book, extracts 15–25 teachable concepts from it, then invents a fictional
world whose **physics are those concepts** — so the reader learns by following a story,
not by reading a definition.

The clearest demonstration is [`1.docx`](1.docx), an early prototype chapter that teaches
distributed-systems concepts through a cultivation/xianxia story:

| In the story | The concept |
|---|---|
| "Your body is a village, not a throne room" | decentralization |
| A cultivator's Golden Core locks; heart, lungs and thought all block waiting on it | single point of failure |
| A fever: the skin demands `HEAT`, the sweat response arrives late | scheduling error / race condition |
| Food backing up because the intestines downstream are still busy | backpressure, flow control |
| "The opposite of asynchrony is death" | asynchrony |

The current book, *The Sankofa Gates*, applies the same method to a different domain
across a multi-arc curriculum of 24 concepts.

---

## Two subsystems

### 1. `src/` — the ingestion and conversion pipeline

Batch Python. Book in, script or chapters out.

- **Ingest** PDF and EPUB, dispatched through a format-adapter registry.
- **Split into chapters** with a five-stage cascade that degrades gracefully:
  PDF bookmarks → text extraction → OCR → LLM structure analysis → content heading scan.
  Each stage only runs if the previous one failed, so a clean PDF costs zero tokens and a
  scanned one still works.
- **Convert** via an LLM into a podcast script (2- or 4-speaker, plus `code`, `realworld`
  and `fiction_meta` modes) or into novel chapters.
- **Synthesise audio** through WaveSpeed VibeVoice — multi-speaker, async submit-and-poll,
  with a recovery path that resumes an interrupted job by `request_id` rather than
  re-submitting and paying twice.

### 2. `fiction_loop/` — the agentic writing loop

The novel writer is not a program; it is an AI coding-agent session that reads
[`fiction_loop/agents/orchestrator.md`](fiction_loop/agents/orchestrator.md) and drives a
numbered pipeline over a shared state machine. Seven role-specialised agents, each with a
written contract:

| Agent | Job |
|---|---|
| Orchestrator | drives the run; never writes prose |
| Fetcher | pulls only the state fields this chapter needs |
| Consistency Checker | pre- and post-assembly contradiction pass |
| Assembler | builds the writer prompt from contracts and cards |
| Writer | generates prose (one of only two steps that call Python) |
| Extractor | reads the finished chapter back into a structured brief |
| Updater | applies the brief to canonical state |

**The interesting part is what surrounds the LLM.** Generation is non-deterministic, so
every state mutation is guarded by deterministic, stdlib-only checks that cost zero tokens:

- **Structural gate** ([`tools/structural_gate.py`](fiction_loop/tools/structural_gate.py))
  runs *before* any state is written. Word-count floors catch truncation; this catches
  under-population, which word counts cannot see. It is receipt-guarded: a PASS records a
  SHA256 of the brief it approved, so state cannot be applied against a brief that changed
  afterwards.
- **Name-presence guard** — no character name may enter canonical state unless it actually
  appears in the prose.
- **Label-leak checks** — scaffolding vocabulary must never reach the reader.
- **Regression harness** ([`tools/regression/run.py`](fiction_loop/tools/regression/run.py))
  — 23 behavioural assertions over fixtures, the mandatory gate for any shared tool change.
- **Cost governance** — preflight estimates, per-call spend receipts, gates-before-spend.
- **Crash recovery** — interrupted runs are detected and resumable;
  [`tools/analyst.py`](fiction_loop/tools/analyst.py) reports pipeline health for zero tokens.

---

## Architecture notes

- **`Protocol`-based interfaces** (`LLMClient`, `LLMTransport`, `ScriptEngine`,
  `AudioEngine`, `SplitterEngine`) with runtime `isinstance` validation in the factories —
  structural typing rather than inheritance, so engines are swappable and trivially mocked.
- **Factory + registry patterns** for engine selection and format dispatch.
- **Provider-agnostic LLM client.** Selection goes through `BOOKGEN_LLM_PROVIDER`;
  OpenRouter is the implemented adapter, with retry, exponential backoff, and 429
  handling that honours `Retry-After` headers and provider JSON hints.
- **Atomic writes and resume state** — `.pipeline_state.json` is checked against filesystem
  reality on resume to detect an interrupt mid promote/update cycle.
- **Token budgeting** with tiktoken before spend.

### Development process

The `fiction_loop/` subsystem is built with AI coding assistants (Claude Code, Codex,
Qwen) under an explicit process: work is dispatched as tickets in
[`tickets/`](tickets/), designs are ruled in
[`fiction_loop/human_decision.md`](fiction_loop/human_decision.md), and recurring
practices are written up in [`innovations/`](innovations/). Implementers stay inside a
declared write-set and stop rather than improvise. That discipline is itself part of the
project.

---

## Quickstart

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). **uv only — no pip.**

```bash
git clone git@github.com:lnxs-prsn/book_podcast_fiction_generator.git
cd book_podcast_fiction_generator
uv sync

cp .env.example .env      # then add your keys
```

Environment (`.env` at the repo root, gitignored):

```bash
PYTHONPATH=src
BOOKGEN_LLM_API_KEY=...
BOOKGEN_LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
BOOKGEN_LLM_MODEL=openrouter/auto
WAVESPEED_API_KEY=...          # only needed for audio
```

Interactive launcher:

```bash
python menu.py
```

Or drive the pipelines directly:

```bash
# Book -> chapters -> podcast scripts (+ audio unless --skip-audio)
PYTHONPATH=src python src/cli/podcast.py --book mybook.pdf --mode 2person

# Single chapter, script only
PYTHONPATH=src python src/cli/podcast.py chapter.pdf --skip-audio

# Novel pipeline
PYTHONPATH=src python src/cli/fiction.py --config src/fiction/pipeline/config.toml
```

Zero-token diagnostics — safe to run any time, no API calls:

```bash
PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py     # pipeline health
PYTHONPATH=src .venv/bin/python fiction_loop/tools/progress.py    # curriculum progress
```

To run the writing loop itself, see
[`fiction_loop/RUN.md`](fiction_loop/RUN.md) — it contains the kickoff prompt to paste
into a fresh agent session.

## Tests

```bash
PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q
PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py
```

331 unit tests pass; one legacy failure in
`test_default_splitter_engine_passes_openrouter_timeout_seconds` is known and predates
the current signature. `pytest` is intentionally not a project dependency — it is
supplied per-run via `--with`.

## Repo map

| Path | What |
|---|---|
| [`src/`](src/) | ingestion, LLM client, engines, TTS, CLIs (~12k LOC) |
| [`fiction_loop/`](fiction_loop/) | the agentic writing loop: agent contracts, state, tools, specs |
| [`fiction_loop/CONTRIBUTING.md`](fiction_loop/CONTRIBUTING.md) | the 17 laws — binding before any change under `fiction_loop/` |
| [`tickets/`](tickets/) | dispatched work orders |
| [`innovations/`](innovations/) | documented engineering practices |
| [`progress/`](progress/) | dated handoffs; newest wins |
| [`1.docx`](1.docx) | prototype chapter — the prose quality benchmark |

## Status

Active work in progress, not a packaged product. Eight chapters of *The Sankofa Gates* are
committed (arc 2 of a multi-arc curriculum). The `src/` pipeline is the older, more
settled half; `fiction_loop/` is where current development happens.

**On documentation trust:** `HANDOFF.md` at the root points to the current dated handoff
and carries a trust map of which documents are live. Several root-level and `docs/`
files describe an earlier shape of the project and carry staleness banners — start from
`HANDOFF.md`, not from them.
