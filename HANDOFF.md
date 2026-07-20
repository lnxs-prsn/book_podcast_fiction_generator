# HANDOFF — front door (stable path; content lives in progress/)

> **CURRENT handoff: `progress/handoff-2026-07-19-compacted-state.md` — read its
> §13 first (latest state), then §12.** As of 2026-07-20: two more pre-build
> lenses ran (ADVERSARIAL + READER, `progress/factory-adversarial-and-reader-pass-2026-07-20.md`)
> and **three tickets were DRAFTED (not dispatched): T-019, T-024, T-025**. A
> ch9-blocking OWNER DECISION surfaced (**ADV-3** — does the arc-2 quota apply to
> a correct-applying return?). As of latest 2026-07-19: **8 chapters
> committed, arc 2, ch8 landed + accepted** (`8935458`); next = ch9
> (return_to_character, char_004). T-016 + T-018 landed; **DECISION 10** (arc-2
> cast quota 3→2, §9 self-contradiction) fixed (`6d15c30`); **factory spec-sync
> pass** done (`3ff7c43`). Git tag **`starting_factory` → `fe2e20d`** marks the
> working 1-book flow (local, unpushed). A **pre-build multi-perspective pass**
> ran a THIRD personification (WIP/part's-eye, uncommitted) and crystallized the
> **"one-way door"** problem (summary built once from prose, ~10 files trust it,
> nothing re-reads the story) — fix direction "verify from the fresh source"
> (free name-presence check → paid meaning re-read), not yet ticketed. The two
> earlier story-treatments (individual + CAST & FIT) were committed in `fe2e20d`;
> a factory Tier-1 action queue (leak fixes / pre-writer prompt gate) is proposed,
> not dispatched.
> The "govern change" operating model is live (ticket Upstream/Downstream, LAW
> 16/17, CAST & FIT lens). §§1–5 are the initial-compaction snapshot; §§8–11 are
> the current addenda (§11 newest). The prior running ledger
> `handoff-2026-07-18-all-tickets-landed-ch7-next.md` (§§1–14) is ARCHIVED — the
> detailed *why*, not the front door. Do not orient from any other document.

**Scope: maintainer sessions only.** A session running the fiction_loop
pipeline (RUN.md kickoff) must NOT orient here — its complete world is
`fiction_loop/RUN.md` + the two specs it names. If you were kicked off to
run a chapter, close this file now and report that you read it.

This file is a pointer, not a ledger. Dated handoffs are appended in
`progress/handoff-YYYY-MM-DD-*.md`; the newest wins. Files always override
handoff claims — the handoff's job is to point at them accurately. Update
rules: `innovations/handoff-discipline/kit/HANDOFF_RULES.md`.

## Read-first order for a cold session

1. `progress/handoff-2026-07-19-compacted-state.md` — current state + open
   queue (COMPACTED front door). For the *why* behind any claim, the archived
   ledger `handoff-2026-07-18-all-tickets-landed-ch7-next.md` §§1–14, then the
   older 2026-07-18 and 2026-07-17 handoffs
2. `fiction_loop/CONTRIBUTING.md` — the 17 laws; binding BEFORE any change
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
