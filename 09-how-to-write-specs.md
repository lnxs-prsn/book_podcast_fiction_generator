# 09 — How to Write Specs for AI-Implemented Projects

Status: settled · **Portable: this file is self-contained — lift it into any
repo unchanged.** It is also, deliberately, a heuristic in this project's own
sense: cue + guidance body. Ingest it into the library once the harness runs.

> **Cue:** starting any project that AI agents will implement — possibly several
> different agents, possibly interrupted at any moment, with a human gating
> quality but not writing the code.

The method has four parts: shape of the **spec**, of the **work**, of the
**data**, of the **collaboration**. Numbers are principles (M-1…M-17,
numbered append-only); the checklist at the end is the operational summary.

## A. Shape of the spec

- **M-1 — Number the requirements; give them normative force.** MUST/SHOULD/MAY
  (RFC 2119) plus stable IDs (`INV-3`, `TOOL-5`). A spec you can only agree
  with is prose; a spec you can *audit* maps every MUST to a check. Tests,
  commits, and reviews reference the IDs, so coverage is a query, not a vibe.
- **M-2 — One concern per file, sized for a context window, with a declared
  reading order.** The readers are AI agents with finite context: an
  implementer should load 2–3 files, not a monolith. Monoliths get skimmed,
  and skimmed specs get violated. State each file's dependencies in its header.
- **M-3 — Write a tiny constitution.** One short file of invariants that every
  other file defers to and every session must read first. Only
  expensive-to-reverse decisions belong in it. When anything conflicts with it,
  it wins; if it is wrong, change it explicitly first, then act.
- **M-4 — Name what NOT to build, everywhere.** AI implementers fail by
  initiative, not disobedience: they helpfully add databases, caches,
  configurability. Every file ends with "Do NOT build". Per-phase not-yet
  lists gate scope creep over time. The standing rule: work not attributable
  to a declared unit is out of scope until the spec changes.
- **M-5 — Acceptance criteria everywhere.** "Done" must be a verdict from a
  checklist ("kill the process mid-write; the log contains only complete
  lines"), never an impression. The human gate reviews against criteria, which
  is fast; reviewing against intuition is slow and drifts.
- **M-15 — Write the user manual before the implementation; derive user
  stories from it.** (Numbered append-only; added after first use of this
  method.) The manual, written from the specs alone, is a verification
  artifact twice over: if a behavior is hard to explain to its user, the
  design is wrong — fix the spec before the code. Then extract the manual's
  promises as numbered user stories and wire them into phase/pass acceptance:
  stories are *walked live*, never verified by reading code, and a
  technically-green pass that fails its story is not done. Stories catch what
  unit-level criteria structurally miss — the system being correct but not
  the thing the user was promised.
- **M-16 — On an existing system, the manual co-evolves; its diff classifies
  the change.** (Numbered append-only.) Any spec for work on an existing
  project must state its manual delta up front. An extension grows the manual;
  a migration may reword operational sections but never promises; a refactor's
  manual delta is *empty* — and that emptiness is an acceptance criterion
  (M-5), not an omission. A change whose manual delta cannot be stated isn't
  understood yet; a "refactor" that needs manual edits is a behavior change
  traveling under a false name (M-14 applies).
- **M-17 — Write stories for every role that will touch the system, not only
  the end user.** (Numbered append-only.) End-user stories (M-15) catch
  missing value; role stories catch missing qualities: the maintainer
  extending it, the migrator moving its data, the refactorer needing safe
  seams, the packager containerizing it, the operator deploying it and reading
  its logs at 3am. Enumerate the roles the project will actually meet over its
  life, give each a small numbered story set, and wire them into the same
  acceptance machinery as user stories. Keep the cast honest: a role the
  project will never meet earns no stories — M-4 applies to personas too.
  One role is exempt from that pruning: every project meets its maintainer,
  so the maintainer's stories are never optional — a system whose maintainer
  story can't be written is a maintenance nightmare by specification.

## B. Shape of the work

- **M-6 — Phases are a trust ladder, not a calendar.** Each phase automates
  only what the previous phase *proved by logged evidence* the human was
  rubber-stamping. Define graduation signals up front, answerable from data
  the system already collects. Autonomy is earned, never scheduled.
- **M-7 — Decompose into atomic passes.** A pass: independently completable in
  one sitting, independently verifiable, leaves the tree clean — else split it.
  Declare per pass: ID, requirement IDs covered, dependencies, parallel-safety
  (disjoint file footprint). This forces the question "what is the smallest
  whole thing?" and makes every pass boundary a safe power-cut and handoff
  point. Claim a pass by committing the status change — the commit is the lock.
- **M-8 — Externalize all build state; assume every session dies mid-step.**
  A STATUS file keyed to requirement/pass IDs (done = commit hash, not a
  claim); an append-only build journal with a **write-ahead rule** — journal
  intent *before* acting, outcome after, decisions with reasons; a session
  start ritual (read overview + constitution + status + journal tail = full
  onboarding) and end ritual (clean tree or journaled dirty state). Plain
  markdown only: no agent memory, IDE state, or todo tool may be the sole home
  of anything. No agent's context, uptime, or rate limit may be load-bearing.
- **M-9 — Keep one record outside the primary store.** An append-only,
  machine-local flight recorder (sessions, claims, attempted commands, errors)
  living *outside* the repo, untouched by any VCS operation — because the
  record of failures must not live inside the thing that fails. Recovery
  order: status → journal → VCS history → flight recorder.

## C. Shape of the data

- **M-10 — Plain files under version control are canonical; everything else is
  derived and rebuildable.** Databases, indexes, statistics are views. Future
  migrations become loader scripts, never conversions of truth. This single
  rule is what makes the endgame reachable by addition instead of rewrite.
- **M-11 — Stable IDs, never reused; logs append-only, generous,
  schema-versioned.** Supersede, don't rename — history stays joinable
  forever. Log more than the current phase needs (losers, not just winners;
  raw inputs, not just summaries): data you didn't record is the only thing no
  future phase can recover. Count absent outcomes as their own bucket —
  silence is survivorship bias.
- **M-12 — Run the expensive-later sweep before writing code.** Hunt
  specifically for costs that are structurally high later: secrets that reach
  synced history (redact at write time); free-text join keys that can't be
  re-described (mandate their format on day one); baselines that can't be
  re-run (capture a control period before go-live); licenses that can't be
  retrofitted (before the first external contribution); interface names that
  freeze on first publication (version them, evolve additively).

## D. Shape of the collaboration

- **M-13 — Divide by comparative advantage; gate through an airlock.** Humans
  hold expertise tacitly (can recognize, can't enumerate); AI articulates
  fluently but forgets. So: AI drafts, human recognizes and passes through.
  All machine writes land in a staging area; promotion is a human act until a
  graduation (M-6) delegates a scoped slice. Keep proposals scarce enough to
  actually be read — rubber-stamping is the gate silently ceasing to exist,
  and it is detected in review behavior, then fixed by reducing volume, not by
  widening autonomy.
- **M-14 — The coherence test.** The build process must obey the system's own
  principles (and this method must obey itself: this document is numbered,
  scoped, has a cue, names its non-goals). If the way you're building
  something violates the way it works, one of the two designs is wrong — find
  out which before proceeding.

## Operational checklist (start of any new project)

1. Write the overview (what/why/roles/glossary/reading order) and the
   constitution (M-3). Keep both short.
2. Data model with IDs + log schema (M-10, M-11) — before any behavior spec.
3. Component specs with numbered requirements, acceptance criteria, non-goals
   (M-1, M-4, M-5).
4. Write the user manual from the specs; extract user stories; wire them into
   acceptance (M-15). A spec that can't produce its manual isn't finished.
   Enumerate the roles the project will meet and give each its story set
   (M-17). For work on an existing project, state the manual delta first
   (M-16).
5. Phase ladder with graduation signals; decompose each phase into declared
   passes (M-6, M-7).
6. Build-process file: status format, journal protocol, rituals, flight
   recorder (M-8, M-9).
7. Expensive-later sweep; put survivors in the constitution (M-12).
8. Scaffold `progress/` (status + journal) and initialize the VCS **before**
   the first line of implementation — the plan living in one agent's context
   window is itself a violation of M-8.

## Do NOT

- Do not write one big spec document. Do not skip non-goals. Do not let "done"
  be self-reported without a criterion. Do not start implementation while the
  plan exists only in a conversation.
