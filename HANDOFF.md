# HANDOFF — front door (stable path; content lives in progress/)

> **CURRENT handoff: `progress/handoff-2026-07-18-all-tickets-landed-ch7-next.md`**
> — read its §5 ADDENDUM first: chapter 007 (arc_transition) committed
> `0b3b362` and senior-verified; T-006 (arc_current self-managing: updater
> STEP 9 advance, extractor arc_effective, analyst drift check + `--repair`)
> LANDED `b128773`+`76185c2` and ACCEPTED — state reads arc=2. Then §§6–7:
> ch8 attempt 1 gate-rejected (anchor absent; LAW 7 pollution fired,
> living doc restored); attempt 2 INCIDENT — driver skipped 10/11/11.5 and
> ran the Updater on the gate-FAILED brief; killed by owner, state undone
> by senior (receipts §7); attempt-2 prose ALSO fails HARD RULE 1. **Ch8
> parked awaiting a third redo generation (driver checklist in §7). FIVE
> tickets queued, BETWEEN runs, in order: T-007 → T-008 → T-009
> (gate pass-receipt blocks Updater) → T-010 (deterministic label check) →
> T-011 (role fence: run driver = Orchestrator ONLY, owner decision — §8).**
> Earlier that day: T-002/004/005/003 all landed and accepted.
> Day detail:
> `handoff-2026-07-18-ch6-landed-open-queue.md` §§5–8 and
> `handoff-2026-07-18-deepseek-switch-404.md` §3b–3d. Background: the two
> 2026-07-17 handoffs (conduct hardening; roles/environment/queue). One hop
> from here to current truth; do not orient from any other document.

**Scope: maintainer sessions only.** A session running the fiction_loop
pipeline (RUN.md kickoff) must NOT orient here — its complete world is
`fiction_loop/RUN.md` + the two specs it names. If you were kicked off to
run a chapter, close this file now and report that you read it.

This file is a pointer, not a ledger. Dated handoffs are appended in
`progress/handoff-YYYY-MM-DD-*.md`; the newest wins. Files always override
handoff claims — the handoff's job is to point at them accurately. Update
rules: `innovations/handoff-discipline/kit/HANDOFF_RULES.md`.

## Read-first order for a cold session

1. `progress/handoff-2026-07-18-all-tickets-landed-ch7-next.md` — current
   state + open queue; then `handoff-2026-07-18-ch6-landed-open-queue.md`
   (§§5–8, day record), `handoff-2026-07-18-deepseek-switch-404.md`, and the
   two 2026-07-17 handoffs — conduct hardening, roles, state
2. `fiction_loop/CONTRIBUTING.md` — the 16 laws; binding BEFORE any change
   under `fiction_loop/`
3. `fiction_loop/specs/intake_factory.spec.md` — the factory spec (design
   complete, unbuilt; its §2 build list is the work map)
4. `fiction_loop/core/agent_conduct.md` — binding DURING any chapter run
5. `tickets/` — dispatched work orders (roles: see current handoff §0)

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
