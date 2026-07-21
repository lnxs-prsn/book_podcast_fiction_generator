# HANDOFF — front door (stable path; content lives in progress/)

> **CURRENT handoff: `progress/handoff-2026-07-21-compacted-state.md` — a fresh
> COMPACTION; read it first (single-hop current truth).** It supersedes the running
> `handoff-2026-07-19-compacted-state.md` (§§1–17), now ARCHIVED as the detailed *why*.
>
> Current state (2026-07-21, HEAD `2abd2a9`, tree clean): **8 chapters, arc 2, next =
> ch9** (`return_to_character`, char_004 Wanjiku, op_separate_condition, touch 2,
> name_due). The full A/B/C pre-build design review is RULED (`fiction_loop/human_decision.md`
> DECISIONS 10–14); **ADV-3 resolved (D13)**; **pre-writer gate spec'd (D14)** =
> `specs/prewriter_gate.spec.md`. **FIVE tickets DRAFTED (not dispatched): T-024, T-026,
> T-025, T-019, T-020** (order T-024 → T-026 → T-025 → T-019; T-020 independent). **ch9
> (paid) awaits T-026** landing (ideally T-024/T-025 too). Restore tag `starting_factory`
> → `fe2e20d` — **no chassis code has changed since.** Still open (design): the
> **"shown"/C3 pass** (before arc 3), B3/RDR-3/B2. Do not orient from any other document.

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
