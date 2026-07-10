# HANDOFF — 09-how-to-write-specs.md — 2026-07-09

## CORRECTION 2026-07-09, later same evening (from the owner — supersedes the provenance story below)

The premise this handoff was commissioned under is WRONG. The owner clarified:

- `09-how-to-write-specs.md` was **added by the owner himself on 2026-07-09**. It was
  NOT written by the rate-limited session, nor by any session in this project. It is a
  new spec-writing method from outside this project.
- Whether the method **fits this project at all is UNDECIDED** — the owner explicitly
  does not know yet. Do not treat the doc as project canon, do not "ingest" it, and do
  not apply M-numbers as binding rules here until the owner decides.
- Consequently, every "LOST" item below that assumes a lost *authoring* conversation
  (rejected alternatives, what prompted the doc, what "first use" was, what
  "ingest/library/harness" concretely mean) is not lost-in-a-session — the doc's
  origin is simply outside this repo. **Ask the owner directly**; there is no
  transcript to mourn.
- What the rate-limited session actually discussed ("specs designs", per the owner)
  remains unrecovered — but it was about something other than authoring this doc.

Still valid below: the SETTLED artifact observations (doc untracked; skill = near-
verbatim copy; drift fixed once; two-skill split) and the OPEN tasks §3.1–3.2, now
reframed: committing the doc and declaring source-of-truth only matter **if the owner
adopts the method**. §3.5's fiction_loop/CONTRIBUTING.md observation stands as a
genuine open question.

## Provenance — read this first (SUPERSEDED — see correction above)

This handoff was NOT written by the session that produced the spec method. That
session hit the user's rate limit on 2026-07-09 before saving its context; its
design discussion is **lost**. This file was written afterwards by a different
instance (the fiction_loop session), reconstructing only what is verifiable from
three surviving artifacts:

1. `09-how-to-write-specs.md` (repo root, 156 lines, still UNTRACKED in git)
2. `~/.claude/skills/spec-driven-ai-projects/SKILL.md` (near-verbatim copy of
   the doc + frontmatter)
3. `~/.claude/skills/writing-specs/SKILL.md` (separate, smaller: one-page specs
   for single features in existing projects)
plus one memory note the interrupting session's successor saved
(`memory/spec-method-doc.md`).

Everything below is marked SETTLED (evident in an artifact), OPEN (known task,
no recorded decision), or LOST (existed only in the cut conversation — ask the
owner, do not guess).

## 1. Decisions made, and why — including rejected alternatives

Decisions **evident in the artifacts** (SETTLED, with the artifact as proof):

- **Append-only numbering for principles.** M-15..M-17 were appended after
  first use rather than renumbering/reordering — M-15's own text says
  "(Numbered append-only; added after first use of this method.)". So the
  method was field-tested at least once and extended from that experience.
  WHICH project that first use was: LOST (plausibly this repo's own work, but
  not recorded — do not assert it).
- **Two-skill split.** Full method (`spec-driven-ai-projects`, whole new
  AI-implemented projects, also refactors/migrations/extensions) vs
  single-feature one-pager (`writing-specs`, <60-line specs, `specs/<name>.md`,
  2-3 questions max, explicit agreement before code). The split itself is
  deliberate — each skill's description names the other as the alternative.
- **The doc is written AS a library heuristic**: header declares "cue +
  guidance body" format and portability ("lift it into any repo unchanged").
  This shapes the ingestion plan (see §4).

**Rejected alternatives: LOST.** No record survives of what was considered and
discarded (e.g., why four sections, why RFC 2119, why a separate one-pager skill
instead of one skill with two modes). If the next instance needs a rationale,
ask the owner — do not reverse-engineer one and present it as history.

## 2. Discussed but not yet written into the doc or skills

**Honest answer: unknown — the discussion is lost.** Only two omissions are
*observable* rather than remembered:

- The doc is **untracked in git** (SETTLED fact, OPEN task). Note the coherence
  failure (the doc's own M-14): a method whose M-8 says "no agent's context may
  be load-bearing" currently has its canonical copy outside version control.
- **Doc↔skill drift already occurred once** (SETTLED fact): the skill's intro
  said "M-1…M-14" while containing M-15..M-17 (stale line from before the
  append). Fixed 2026-07-09 by the handoff-writing instance. No sync rule
  exists (OPEN, §3.2).

## 3. Open questions / next steps, in priority order

1. **OPEN — Commit `09-how-to-write-specs.md`.** Highest priority and trivial;
   every other step assumes the canonical copy can't be lost. (Owner's call
   whether it belongs in this repo long-term or moves; committing now loses
   nothing.)
2. **OPEN — Declare source of truth between doc and skill copy.** They are two
   full copies of the same method and have already drifted once. Options: doc
   is master + skill is a synced snapshot (state this in both headers), or the
   skill body becomes a pointer that reads the doc. NOT DECIDED — pick with the
   owner.
3. **OPEN — Execute the ingestion** (§4) once its precondition (the harness
   running) is met. Cannot be scheduled from here; harness status unknown to
   the writing instance.
4. **LOST/OPEN — Recover the surrounding design intent** from the owner if it
   ever matters: what prompted the doc on 2026-07-09, what the first use
   (M-15's trigger) was, and whether more principles were planned.
5. **OBSERVATION by the writing instance (not from the specs session — clearly
   attributed):** fiction_loop independently evolved a constitution of the same
   species (`fiction_loop/CONTRIBUTING.md`, 15 laws + case law + backtest
   rule); M-3 ("tiny constitution") and several M-principles have direct
   fiction_loop analogues. Whether the two documents should reference each
   other was NEVER DISCUSSED anywhere — a genuine new question, not a lost
   decision.

## 4. What "ingest into the library once the harness runs" was supposed to mean

**Concrete meaning: LOST.** The phrase is the doc's own header sentence; the
conversation that would define "the library", "the harness", and "ingest"
operationally was cut. What can be said honestly:

- SETTLED (textual): the doc self-describes as "deliberately, a heuristic in
  this project's own sense: cue + guidance body" — implying the harness project
  defines a heuristic format of cue (when to fire) + guidance (what to do), and
  a library of such heuristics. The doc is pre-formatted to become one entry:
  its blockquoted **Cue:** paragraph is the trigger, the rest is the guidance
  body.
- SETTLED (prior instance's memory note): "the harness" = this repo's broader
  harness-design work (the repo is `harness_design/harnessv9`), NOT
  fiction_loop.
- INFERENCE ONLY (unverified — confirm with owner before acting): "ingest"
  likely means registering the doc in whatever heuristic store/retrieval
  mechanism the harness uses when it becomes operational, so agents get it by
  cue rather than by being told. The Claude Code skill created the same day may
  have been an interim substitute for exactly this (the skill system IS a
  cue+guidance library). If so, ingestion may reduce to: port the doc into the
  harness's native heuristic format when that format exists. DO NOT act on
  this paragraph without owner confirmation.
