# Trunk + push-gate — the unpushed range IS the review queue

## What it is
A git workflow where every agent commits directly to `main`, but pushing is
manual and owner-gated. `origin/main` is the blessed, reviewed state; the
local range `origin/main..main` is the standing review queue. A reviewer
(whoever the owner directs) audits that range, fixes or reverts in place, and
the owner's push publishes it.

## Problem it solves
Branch-per-task ceremony is designed for human teams on shared remotes — AI
agents fumble branch state (wrong checkouts, stale branches, merge messes),
and in a single shared checkout branches don't even protect the working tree.
Meanwhile fully unreviewed trunk work publishes mistakes instantly. This
pattern keeps trunk simplicity AND a hard review gate.

## How to use it
1. Rule: agents commit on `main` with attribution trailers
   (`Implemented-by:`, `Reviewed-by:`, `Ticket:`); they NEVER push. Explicit
   staging only — `git add <paths>`; `add -A`/`commit -a` banned (they sweep
   other agents' in-flight files).
2. Review = `git log origin/main..main` + `git diff origin/main...` checked
   against the tickets; corrections are follow-up commits or reverts, never
   history rewrites.
3. The owner pushes when told the queue is clean. A bad commit that already
   reached origin gets `git revert`, not force-push.
4. Escape hatch: genuinely risky/experimental work goes on a branch (decided
   at dispatch); parallel work uses worktree branches — both merge back
   serially through review.

## Fits projects like
Solo-owner + AI-agent repos; any setup where the remote is the publication
boundary and the local machine is the workshop. Poor fit for teams pushing
continuously to shared remotes (use PRs there — this pattern is the
single-checkout answer to the same need).

## Proven in
Origin project, 2026-07: review queues of up to 16 commits accumulated,
reviewed, and pushed in batches; two junior implementation commits and one
--no-ff worktree merge flowed through the queue in one day. The one violation
(a reviewer using `git add -u`) was caught by self-audit and reported —
which is also why the staging rule is now machine-checkable at review time
(diff the commit against the ticket's write-set).

## Kit (deployable files in `kit/`)
`kit/GIT_CONVENTIONS.md` — edit the Areas list and stateful paths, drop at repo root (or a conventions/ dir), point agent entry files at it.
