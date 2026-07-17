# GIT_CONVENTIONS — how commits work in this repo

One repo, one `.git`, at this root — every commit, from any agent, lands here.
Multiple agents plus the owner may share ONE checkout on one machine; these
rules optimize for that reality. Branches isolate commits, but the actual risk
is agents colliding in the shared WORKING TREE — solved by sequential dispatch
(and worktrees for true parallelism), not branch ceremony.

## The model: trunk + push-gate

Everyone commits directly on `main`. **`git push` is the review gate**, and
only the owner (or an agent the owner tells to) pushes:

- `origin/main` = blessed, reviewed state.
- Local commits ahead of `origin/main` = the review queue. Whoever the owner directs to review checks
  the whole range (`git log origin/main..main`, `git diff origin/main...`),
  re-runs the ticket's acceptance checks, and fixes/reverts on main if needed.
- Owner says "push" → the queue is published. Nothing is ever force-pushed;
  a bad commit that already reached origin is undone by `git revert`.

## Direction

The owner directs all agents; roles are per-dispatch, never standing (see
`MULTI_AGENT_PROTOCOL.md` §0). Whatever its role, an agent implements at most
ONE ticket/spec at a time, commits with trailers, never pushes, and never
reverts another agent's commits unless the owner's dispatch says to. Duties
not assigned in the dispatch stay with the owner.

## One agent at a time (the load-bearing rule)

Only ONE agent works the tree at a time — the owner enforces this by simply
not running two agents at once. Before starting, an agent runs `git status`;
dirty files it didn't create belong to someone else: leave them alone, report
them, and if the tree looks mid-operation, stop and ask the owner.

If two agents genuinely must run in parallel, someone the owner directs sets up
`git worktree add ../wt-<agent> main` first — separate directories, separate
tree state. Do not attempt parallelism in one checkout.

## Ticket flow

1. An agent the owner directs writes `TICKET_<slug>.md` at the repo root (acceptance criteria, constraints,
   expected commits) — or points at an existing `SPEC_*.md`.
2. Owner dispatches ONE implementing agent with it (mode per MULTI_AGENT_PROTOCOL.md).
3. The implementer commits on `main` (explicit paths only), updates the
   ticket's implementer log, stops. It does not push.
4. The owner's designated reviewer checks the queued range against the ticket, amends via follow-up
   commits or reverts (never rewrites), and reports.
5. Owner pushes (or tells an agent to).

Escape hatch: work that is experimental, likely to be thrown away, or touches
the loop chassis broadly goes on a `ticket/<slug>` branch — decided at
dispatch, stated in the ticket. Default is trunk.

## Commit messages

Format: `<area>: <imperative summary>` + body when the "why" isn't obvious.

Areas (EDIT for your project — keep them few and stable): `feat(<pkg>)`,
`fix(<pkg>)`, `test(<pkg>)`, `docs`, `build` (env/deps/lock), `spec`
(tickets/specs), plus any domain-specific prefixes your tooling recognizes.

Required trailers:

```
Ticket: TICKET_<slug>.md            # or Spec: <path>, when applicable
Implemented-by: codex | qwen | claude | owner
Reviewed-by: <agent|owner>           # review/fixup commits only
```

`git log --format='%h %s %(trailers:key=Implemented-by,valueonly)'` then shows
who did what at a glance.

## Staging rules (the hard ones)

- **NEVER `git add .`, `git add -A`, or `git commit -a`.** Stage explicit
  paths only. Another agent's uncommitted work WILL be in the tree at times;
  sweeping it into your commit is the failure mode this file exists to prevent.
- NEVER commit: `.env` files, any file containing a key/token, `.venv/`,
  agent scratch dirs (`.qwen/`, `.codex/` — gitignored). `example.env`-style
  templates must contain names only, zero values.
- <YOUR stateful/user-data paths> change ONLY through their owning workflow,
  never in a ticket's commits.
- No force-push, no history rewrites, no rebase of anything already pushed.
- Push only when the owner says push.
