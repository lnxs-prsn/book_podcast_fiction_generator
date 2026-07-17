# Ticket dispatch — self-contained work orders with author-verified preconditions

## What it is
A `TICKET_<slug>.md` file at the repo root that a junior AI agent can execute
cold: scoped header (mode, write-set, state access, paid-call policy),
problem statement with verified facts, exact fix locations, numbered
acceptance checks, constraints, and an implementer log the agent appends to.
The author (senior agent or human) **dry-runs every precondition before
dispatch**.

## Problem it solves
Two expensive failure loops: (1) a junior burns a run on a spec bug (an
acceptance command that could never pass), then the senior must amend and
re-dispatch; (2) a junior improvises around an obstacle and does damage
outside its task. The ticket kills both: verified preconditions prevent the
first, hard scope + "stop and log, don't improvise" prevents the second.

## How to use it
Template skeleton:
```
# TICKET: <imperative title>
Mode: alone | group        Worktree: <path, group only>
Write-set: <exact files/globs the implementer may touch>
Hot-files: <shared files allowed, if any>   State-access: none|reads|writes
Paid-calls: forbidden | budgeted via <mechanism>

## 1. Problem (preconditions verified <date> by the ticket author)
## 2. Fix (exact files/lines; what to preserve)
## 3. Acceptance (numbered, machine-checkable, ALL must pass)
## 4. Commit (exact message format + required trailers)
## 5. Constraints (environment, bans, "on failure: stop and log")
## 6. Implementer log (append-only; checkboxes + dated notes)
```
Author's discipline — the part that makes it work:
- **Dry-run every acceptance step's preconditions**: does the binary exist, is
  the dependency declared, does the path resolve, can each step pass without
  violating §5? Grep first, dispatch second.
- Write-set is a promise checked at review; commits outside it are reverted
  without discussion.
- When a junior stops at a red check (correct behavior): diagnose, AMEND the
  ticket in place (strikethrough + dated amendment), and resume — the ticket
  accumulates the true history of the work.

## Fits projects like
Any senior/junior agent split (expensive model designs, cheap models
implement); human tech-lead + AI implementers; even human contractors. Needs
nothing but a file convention.

## Proven in
Origin project, 2026-07: four tickets in one day (uv workspace, venv checks,
commit hook, conformance sandbox), implemented by two different junior agents.
Both spec-bug incidents (undeclared pytest; an acceptance step broken by an
unrelated pre-existing failure) were caught by juniors correctly stopping,
fixed by dated amendments, and completed — and both produced the "dry-run
preconditions" rule now baked into §1's required header line.

## Kit (deployable files in `kit/`)
`kit/TICKET_TEMPLATE.md` — copy per ticket, fill every section, dry-run §3 before dispatch.
