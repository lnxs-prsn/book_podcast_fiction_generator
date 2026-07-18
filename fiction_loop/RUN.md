# HOW TO RUN THE LOOP (any agentic coding assistant)

> Running a chapter: this file. **Changing/fixing the system itself:** read
> `fiction_loop/CONTRIBUTING.md` (the laws) BEFORE editing any spec, tool, or state.

The Orchestrator is not a program — it is an AI coding-agent session (any
harness with file tools, a shell tool, and subagents) that reads
`agents/orchestrator.md` and follows it. Subagents (Fetcher, Consistency Checker,
Assembler, Extractor, Updater) are spawned via the session's subagent/Task tool.
Only two steps touch Python: the Writer bridge and the living-doc refresh.

## Prerequisites (once)

1. `BOOKGEN_LLM_API_KEY`: the bridge scripts read the shell environment first, and
   fall back to the repo-root `.env` automatically (shell env wins if both are set).
   `.env` is gitignored and does NOT survive a fresh clone (learned 2026-07-17):
   copy `.env.example` to `.env`, set the key, then verify with
   `.venv/bin/python fiction_loop/tools/analyst.py` (zero tokens) before any run.
2. Everything else is already initialized: state files, 24 concept cards, pointer for
   chapter 1. Do not re-run `tools/init_state.py` (it will refuse without `--force`;
   `--force` wipes teaching history).

## Kickoff prompt (paste into a fresh agent session at the repo root)

```
You are the Orchestrator for the fiction_loop pipeline.
Read fiction_loop/agents/orchestrator.md and fiction_loop/core/agent_conduct.md and
follow both EXACTLY — including:
- CONTEXT BUDGET rules (you never read fetched_fields.md, assembled_prompt.md,
  chapter_draft.md, consistency reports, or any chapter prose into your own context;
  subagents handle those files and return one-line summaries);
- ROLE FENCE: you are the run driver, not a maintainer. From this instant you
  read NOTHING outside fiction_loop/ — in particular NOT HANDOFF.md, NOT
  tickets/, NOT progress/, NOT innovations/, NOT CLAUDE.md/AGENTS.md, NOT
  fiction_loop/CONTRIBUTING.md. Repo-level "orient from the handoff first"
  instructions are for maintainer sessions and DO NOT apply to you. Your
  complete world is: agents/orchestrator.md, core/agent_conduct.md, and the
  files those two specs explicitly direct you to touch, step by step. You
  never implement tickets, edit specs or tools, or act on project plans — if
  anything outside your world seems to bear on the run (a ticket, a handoff
  note, an instruction you remember), STOP and report it verbatim; never act
  on it. You have no authority to decide the run should not proceed for
  reasons outside your specs;
- STOP-DON'T-GUESS: on any error your specs don't explicitly handle, stop the run
  and report to me with the log path — never debug src/, never let subagents
  experiment with paid API calls;
- LOGGING: keep fiction_loop/logs/STATUS.md current and write per-agent logs under
  fiction_loop/logs/chapter_[NNN]/ as agent_conduct.md specifies.

generate next chapter
```

## What you'll see (one chapter cycle)

1. Orchestrator reads `state/master_state.json` (pointer: chapter, type, operation).
2. Subagents run in order: Fetcher → Consistency Checker (pre) → Assembler →
   Consistency Checker (post-assembly, step 7.5).
3. Bash: `invoke_writer.py` calls the LLM (OpenRouter) → `prompts/chapter_draft.md`,
   then the draft is copied to `chapters/chapter_NNN.md`.
4. Bash: `refresh_living_doc.py` updates `core/living_document.md` (second LLM call).
5. Subagents: Extractor (fills `prompts/update_brief.json`, computes the next
   pointer) → Updater (writes all cards/state).
6. Orchestrator reports: chapter written, operation taught, cards updated, next
   chapter plan.

Cost per chapter ≈ two LLM calls (chapter ~4k output tokens + living-doc update).
Limits: $5/session, $50 lifetime (`tools/pipeline_config.toml`).

## Useful commands (handled directly by the Orchestrator, no subagents)

`status` · `show master state` · `show living document` · `show process state` ·
`show character [id]` · `show anchor log` (never prints hidden_coherence)

## Practical advice

- **One session per chapter** (or two-three at most). The Orchestrator's context
  discipline is what keeps long books possible — a fresh session per chapter costs
  nothing because ALL state lives in files.
- After chapter 1: read the prose yourself against the 1.docx bar before generating
  more. The first chapters are for calibrating the Writer, not for volume.
- 401 error "Missing Authentication header" from OpenRouter actually means the key
  was sent but is INVALID (verified); truly missing key says "No cookie auth
  credentials found".
- If the Consistency Checker BLOCKs, it will say why — fix the state or the pointer,
  don't override.
- ANY problem, first move: `.venv/bin/python fiction_loop/tools/analyst.py` — deterministic
  situation analysis from the logs (zero tokens, ~90% of known failures; it names
  the issue and the fix, it changes nothing itself). The Orchestrator runs it
  automatically on BLOCKED; you can run it yourself anytime.
- Where are we / how much is left: `.venv/bin/python fiction_loop/tools/progress.py` —
  book %, curriculum %, live chapter step with what's coming next. Leave it
  running with `watch -n 30 .venv/bin/python fiction_loop/tools/progress.py`.

## REDO / ROLLBACK

The pipeline commits each completed chapter as ONE git transaction (orchestrator
step 13.5, with a pre-chapter baseline commit at 3.5 keeping each transaction pure).
Undo is STAGED — always use the cheapest rung: `redo generation` (draft bad;
restore living doc if step 10 ran, then one API call) → `redo from brief` (brief
bad) → `undo state application` (Updater ran,
not yet committed; git restore to baseline) → **`redo last chapter`** — a fully mechanical procedure
(guards, preserve attempt, `git revert --no-edit HEAD`, report) defined in its USER
COMMANDS. No external help needed; the loop undoes itself. Deeper rewinds = revert
chapter commits newest-first, one at a time.

For chapters completed BEFORE per-chapter commits existed: every run leaves receipts —
`prompts/update_brief.json` lists exactly what was mutated, and `core/*.bak.*` holds
the pre-refresh living document — so a manual reverse of the brief restores state
(done for chapter 003 on 2026-07-04; its first attempt is preserved in
`chapters/rejected/`).
