# MULTI_AGENT_PROTOCOL — running several AI agents on one repo

Portable: copy the `conventions/` folder to any project (entry pointers like
`AGENTS.md` stay at that project's root and point here); deltas go in
the last section only. Git mechanics (message format, trailers, staging rules,
push gate) live in `GIT_CONVENTIONS.md`; this file governs WHO works WHERE and
WHEN.

## 0. Direction — the owner runs the process

**All agents are directed by the owner.** There are no standing roles: what an
agent is (implementer, spec-writer, reviewer, coordinator) is whatever the
owner's dispatch says, for that dispatch only. Any duty not explicitly
assigned belongs to the owner. An agent must not assume it holds a role —
including "reviewer" or "coordinator" — because it held it last time. When a
dispatch is ambiguous about role, mode, or scope: **ask the owner; never fill
the gap with an assumption.**

Named duties the owner may delegate per dispatch (any of them, to any agent):
- **implement** a ticket/spec;
- **write specs/tickets** (no code);
- **review** a queued range or branch against its ticket (re-run the
  acceptance checks — a log is a claim, not proof);
- **coordinate a group**: verify write-set disjointness, create worktrees,
  keep `BOARD.md` current, merge branches serially.

## 1. Modes — the owner's switch

Every dispatch names a mode, in the prompt ("you operate ALONE" / "you are in
a GROUP") or in the ticket header. **No mode named = ALONE.**

| | ALONE (default) | GROUP |
|---|---|---|
| Where you work | The root checkout | Your own worktree (path is in your ticket/dispatch) |
| Branch | `main` directly | The worktree's branch (never switch it) |
| Write scope | The ticket's write-set | The ticket's write-set, STRICTLY — disjointness is what keeps the group safe |
| Foreign dirty files in `git status` | Stop, report, wait for owner | Inside YOUR worktree only your changes may exist; anything else: stop, report |
| Full test suite | Run freely | Inside your worktree only; if the machine is small, the ticket says when |
| Merging / pushing | Never, unless your dispatch says so | Never, unless your dispatch says so |
| Done means | Commits on main + ticket log updated | Commits on your branch + ticket log updated |

An agent that cannot tell which mode it is in must read `BOARD.md`; if still
unclear, stop and ask the owner. Never guess "alone."

## 2. The board

`BOARD.md` (in this `conventions/` folder) is the single coordination surface. Whoever the owner has
coordinating (the owner themself by default) writes it; working agents read
it. One row per active ticket:

```
| ticket | agent | mode | worktree | write-set | state |
```

`state`: dispatched → in-progress → ready-for-review → merged/abandoned.
Dispatch adds the row; merge closes it. Implementing agents NEVER edit the
board — their status channel is the implementer log inside their own ticket.

## 3. Ticket header (extends the TICKET_*.md format)

```
Mode: alone | group
Worktree: <path>            # group only
Write-set: <dirs/globs the implementer may create or modify>
Hot-files: <shared files this ticket is allowed to touch, if any>
State-access: none | reads <what> | writes <what>
Paid-calls: forbidden | budgeted via <mechanism>
```

The write-set is a promise, checked at review: commits touching paths outside
it are grounds for revert without discussion.

## 4. Invariants — always true, anyone may verify

- **I1 — one agent per working tree.** Two agents in one tree corrupt the
  shared index and make every test result unattributable.
- **I2 — concurrent write-sets are disjoint.** Proven BEFORE dispatch (the
  specs' file footprints must not intersect), never discovered at merge time.
- **I3 — hot files are single-owner.** Registry files, package
  `__init__`/exports, `pyproject.toml`, lockfiles, shared configs: at most one
  active ticket may list them, all others must not touch them.
- **I4 — shared mutable state is single-writer.** Databases, user profiles,
  budget/state files: at most one active ticket declares `State-access:
  writes`; every other concurrent ticket is pure code+tests.
- **I5 — integration is serial.** Branches merge one at a time and the full
  suite runs on `main` AFTER EACH merge, before the next.
- **I6 — every commit is attributed** (trailers per `GIT_CONVENTIONS.md`).
- **I7 — one heavy process at a time on a small machine.** Full suites,
  installs, and builds are staggered (schedule-level; files can't enforce it).
- **I8 — paid/API budget is single-writer**; implementers default to
  `Paid-calls: forbidden`.

## 5. Race conditions this protocol kills (and the one it can't)

| Race | Without protocol | Killed by |
|---|---|---|
| Same-file concurrent edits | last-writer-wins data loss | I2 |
| Shared git index (`add` vs `commit`) | one agent's files inside another's commit | I1 (worktrees have separate indexes) |
| Registry/lockfile both-append | textual or semantic merge conflict | I3 |
| DB/state/budget concurrent writes | corrupted state, unaccountable spend | I4, I8 |
| Concurrent full suites | RAM exhaustion, flaky results | I7 |
| **Semantic conflict** (each branch green alone, red combined) | broken main | NOT preventable — CAUGHT by I5's per-merge suite run |

## 6. Stalls and rate limits

Design principle: **every handoff is asynchronous through files and commits;
no agent ever waits live on another agent.** Therefore:

- A rate-limited implementer stalls only its own ticket. Its worktree + ticket
  log are the complete resumable state — the same or a DIFFERENT agent can
  resume from them later. Nothing else in the system notices.
- A rate-limited reviewer/coordinator stalls only the review/merge queue —
  finished branches wait as files; other agents keep working; nothing is lost.
- The owner is the only true serial point (direction, decisions, pushes) — by
  design.
- Recovery rule: an agent resuming any ticket reads the ticket's implementer
  log FIRST and trusts the files over the log where they diverge.

## 7. Choosing a mode (owner guidance)

Default to ALONE, sequential dispatch — coordination has a real cost (worktree
setup, per-worktree environments, staggered suites) that only pays off when a
ticket is long-running AND a second independent direction is urgent. Before a
GROUP dispatch, someone (owner, or an agent the owner directs) must: verify
write-set disjointness, create the worktrees, update the board. Telling agents
to "just work in parallel" without that setup recreates every race in §5.

## 7b. Merge checklist — for whoever the owner directs to merge

Merging is never the implementer's job (it cannot see the other trees and
would be grading its own homework). The directed merger runs, in order:

1. Confirm the direction: the owner asked YOU to merge THIS branch.
2. Main checkout `git status` clean. Unrelated dirt gets resolved or committed
   separately FIRST — never swept into a merge.
3. Review the branch: diff vs merge-base touches ONLY the ticket's write-set;
   re-run the ticket's acceptance checks yourself (the implementer log is a
   claim, not proof).
4. One branch at a time (I5): `git merge --no-ff wt/<slug>` — the merge
   message must itself pass the commit hook.
5. AFTER each merge, before the next: affected test suites green on `main`,
   plus any acceptance steps the ticket deferred to review time.
6. Close the board row (→ History) and update the handoff if the state change
   warrants it (`HANDOFF_RULES.md` trigger 1).
7. `git worktree remove <dir>` and `git branch -d wt/<slug>`.
8. Anything red at any step: STOP — no further merges; fix or revert on
   `main` before touching the next branch.

## 8. Project-specific deltas (FILL IN for your project)

- Environment: <how a worktree gets a runnable env, e.g. `uv sync` at its root>
- Stateful zones (I4): <databases, user data, budget/state files — single-writer>
- Known hot files (I3): <registry __init__ files, pyproject/lockfiles, shared configs>
- Paid calls: <default forbidden; name the budgeted wrapper if one exists>
