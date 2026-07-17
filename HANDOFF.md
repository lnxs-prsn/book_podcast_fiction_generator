# HANDOFF — front door (stable path; content lives in progress/)

> **CURRENT handoff: `progress/handoff-2026-07-18-deepseek-switch-404.md`**
> (DeepSeek model switch, step-8 404 diagnosis + one remaining check, resume
> steps). Background: `handoff-2026-07-17-ch6-postmortem-fixes.md` (conduct
> hardening) and `handoff-2026-07-17-clone-audit.md` (roles, environment,
> open queue). One hop from here to current truth; do not orient from any
> other document.

This file is a pointer, not a ledger. Dated handoffs are appended in
`progress/handoff-YYYY-MM-DD-*.md`; the newest wins. Files always override
handoff claims — the handoff's job is to point at them accurately. Update
rules: `innovations/handoff-discipline/kit/HANDOFF_RULES.md`.

## Read-first order for a cold session

1. `progress/handoff-2026-07-18-deepseek-switch-404.md` — current blocker +
   resume steps; then the two 2026-07-17 handoffs — conduct hardening, roles,
   state, open queue
2. `fiction_loop/CONTRIBUTING.md` — the 15 laws; binding BEFORE any change
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
