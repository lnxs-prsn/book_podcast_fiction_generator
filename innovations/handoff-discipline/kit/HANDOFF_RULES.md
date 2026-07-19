# HANDOFF_RULES — when and how the handoff file gets updated

The handoff is the orientation document a cold session reads first — put it
at a stable, findable path (e.g. `HANDOFF.md` at the repo root) and point your
agent entry files at it. These rules keep it trustworthy.

## What the handoff IS (and is not)

It is a dated summary-and-pointer document: what state the project is in, what
changed recently, where the authoritative files are. It is NOT a ledger —
status lives in STATUS files, decisions in the decisions ledger, code truth in
code. **Files always override the handoff**; the handoff's job is to point at
them accurately.

## WHEN to update (the triggers)

1. **You changed project state.** Anything merged/committed that a cold
   session would need to know: environment changes, process/convention
   changes, a spec built, a blocker cleared or created. Update in the SAME
   sitting, committed with or right after the change.
2. **You found something.** A discovery that the handoff (or any doc it points
   to) is wrong or stale — even if you changed nothing. A found staleness that
   goes unrecorded WILL be repeated by the next reader.
3. **End of a working session** that did either of the above: re-read the
   handoff's current top section once and check it still tells the truth.

No trigger fired → no update. Do not churn the handoff for work that STATUS
files or tickets already record; add a pointer at most.

## HOW to update

- **Append dated sections; never silently rewrite history.** Older sections
  are records of what was believed then. When one is wrong, mark it in place
  (`~~strikethrough~~ **STALE — <what's true>; see <dated section>**`) and put
  the correction in the current dated section.
- **Verify before you write — and before you repeat.** Any claim you carry
  forward from the handoff into a new section must be re-verified against the
  authoritative file (STATUS, decisions ledger, code) at that moment. Copying
  an unverified claim forward is how staleness compounds (case law from the origin
  project: a GOLD-6 "still pending" claim was repeated 6 days after the ledger
  said ACCEPTED).
- **Name your evidence.** A state claim cites the file/commit it was verified
  against ("verified against decisions.md 2026-07-11T00:00Z").
- **Keep the front door current.** The banner at the top of the handoff points
  to the newest dated section; a cold reader must reach current truth in one
  hop, not by reading past sections in order.
- **Commit it** as `docs: HANDOFF <what changed>` with trailers per
  `GIT_CONVENTIONS.md`.

## WHO

Whoever made the change or found the staleness — any agent, any role, owner
included. Updating the handoff needs no dispatch or permission: recording true
state is never out of scope. (Implementing agents with a tight write-set:
record the finding in your ticket's implementer log instead, and the reviewer
carries it into the handoff.)

## Compaction (when the running ledger gets too big to be a front door)

The handoff is append-only by design, so the current file grows
(dated addenda accumulate). When reaching current truth stops being a
one-hop read — rule of thumb ~10+ addenda / a few hundred lines — COMPACT,
don't keep appending:

1. **Write a fresh `handoff-YYYY-MM-DD-compacted-state.md`** containing ONLY
   live current truth: state, roles, still-binding facts, the open queue,
   and a read-first order. **Re-verify every carried-forward fact against
   its authoritative file/commit as you write it** (same rule as any new
   section — compaction is the highest-risk moment for copying staleness).
   Cite the commit you verified at.
2. **Do NOT delete the old ledger.** It stays in `progress/` as the archived
   detailed *why*; the compacted file names it as such. Files override the
   handoff, and the ledger is still a file of record.
3. **Repoint the front door** (`HANDOFF.md` banner + read-first item 1) at
   the new compacted file; demote the old ledger to "archived detail."
4. Commit as `docs: HANDOFF compaction — <date>`.

This is the lightweight method. A heavier factory-scale rotation (auto-
archiving landed tickets, a state-snapshot tool) is a separate, later concern
— do not build it pre-emptively (priced-guardrails: compact by hand until the
by-hand cost actually hurts).
