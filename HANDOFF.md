# HANDOFF — front door (stable path; content lives in progress/)

> **CURRENT handoff: `progress/handoff-2026-07-21-compacted-state.md` — a fresh
> COMPACTION; read it first (single-hop current truth).** It supersedes the running
> `handoff-2026-07-19-compacted-state.md` (§§1–17), now ARCHIVED as the detailed *why*.
>
> Current state (2026-07-21): **8 chapters, arc 2, next = ch9** (`return_to_character`,
> char_004 Wanjiku, op_separate_condition, touch 2, name_due). Design review RULED
> (`fiction_loop/human_decision.md` DECISIONS 10–15). **T-024, T-026, T-025 are LANDED**
> (`7dbc237`, `c0dcade`, `f8225f7`) — the "no chassis code changed since `fe2e20d`" claim
> is now FALSE (the gate changed). Still DRAFTED: T-019, T-020, T-023. **ch9 (PAID) was run
> and is BLOCKED at the structural gate — HOLD**: a stale pre-T-026 pointer (`"none"`) needs
> deterministic re-derivation, and an arc-vs-operation wrong-approach label conflict needs
> an owner ruling (do NOT override/redo). Ticket-writing now has a method
> (`10-how-to-write-tickets.md`). Still open (design): **"shown"/C3 pass**, B3/RDR-3/B2.
> **Read the dated handoff §1 (UPDATE + ch9-block) for the authoritative current truth** —
> do not orient from any other document.

**Scope: maintainer sessions only.** A session running the fiction_loop
pipeline (RUN.md kickoff) must NOT orient here — its complete world is
`fiction_loop/RUN.md` + the two specs it names. If you were kicked off to
run a chapter, close this file now and report that you read it.

This file is a pointer, not a ledger. Dated handoffs are appended in
`progress/handoff-YYYY-MM-DD-*.md`; the newest wins. Files always override
handoff claims — the handoff's job is to point at them accurately. Update
rules: `innovations/handoff-discipline/kit/HANDOFF_RULES.md`.

## Read-first order for a cold session

1. `progress/handoff-2026-07-21-compacted-state.md` — current state + open
   queue (COMPACTED front door). For the *why* behind any claim, the archived
   running ledger `handoff-2026-07-19-compacted-state.md` §§1–17, then the older
   2026-07-18 and 2026-07-17 handoffs
2. `fiction_loop/CONTRIBUTING.md` — the 17 laws; binding BEFORE any change
   under `fiction_loop/`
3. `fiction_loop/specs/intake_factory.spec.md` — the factory spec (design
   complete, unbuilt; its §2 build list is the work map)
4. `fiction_loop/core/agent_conduct.md` — binding DURING any chapter run
5. `tickets/` — drafted work orders (roles: see current handoff §2)

## Trust map — which documents are live

| Document | Status |
|---|---|
| `progress/handoff-2026-07-17-*` and newer | LIVE |
| `fiction_loop/` (CONTRIBUTING, RUN.md, specs/, core/, tools/, state/) | LIVE — the working system |
| `tickets/`, `innovations/` | LIVE |
| `09-how-to-write-specs.md` | LIVE — spec-writing method |
| `10-how-to-write-tickets.md` | LIVE — ticket-writing method (companion to 09; acceptance-execution rule T-6/7/8) |
| `progress/handoff-2026-07-10-*` and older handoffs | dated records; carry staleness notes |
| `docs/project_state.md`, `docs/log.md`, `user_manual.md` | **STALE (2026-05 era)** — describe a project shape that no longer exists; banners added 2026-07-17 |
| `build_specs.md`, `initial_build.md`, `docs/fiction/`, `src/phases/` | historical design/build records; do not implement from them |

## Environment invariants (verified 2026-07-17, commit f3ed1b5)

- ONE Python project at the repo root: `pyproject.toml` + `uv.lock` +
  `.venv/`. Interpreter: `.venv/bin/python` from the repo root, usually with
  `PYTHONPATH=src`. **uv only — never pip, never `python -m venv`.**
- Secrets: `.env` at root (gitignored; recreate from `.env.example`).
- This machine is a Raspberry Pi: nothing heavy in parallel, especially
  during a pipeline run.
