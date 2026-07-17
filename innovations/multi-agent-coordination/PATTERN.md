# Multi-agent coordination — modes, board, invariants, worktrees

## What it is
A protocol for running several AI agents against one repository without them
corrupting each other's work. Core pieces: an owner-declared **mode** per
dispatch (ALONE = root checkout, GROUP = own git worktree); a **board** file
listing active work; eight **invariants** anyone can verify; a **merge
checklist** for whoever is directed to integrate. Roles are per-dispatch,
never standing — unassigned duties belong to the human owner.

## Problem it solves
Concrete races: two agents share one git index (one agent's staged files end
up inside the other's commit); test results become unattributable (whose code
was on disk?); registry files and lockfiles collide; budget/state files get
double-written; and the subtle one — two branches each green alone, red
combined.

## How to use it
1. Copy the protocol files (`MULTI_AGENT_PROTOCOL.md`, `BOARD.md`,
   `GIT_CONVENTIONS.md` — the origin keeps them in a `conventions/` folder)
   plus thin per-agent pointer files at the root that each agent's tooling
   auto-loads (`AGENTS.md`, `CLAUDE.md`, etc.).
2. Every dispatch names a mode. **No mode named = ALONE.** An agent that can't
   tell its mode reads the board; still unclear → asks the owner. Never guess.
3. The invariants that do the work: one agent per working tree; concurrent
   write-sets disjoint (proven BEFORE dispatch); hot files single-owner;
   shared mutable state single-writer; integration serial with the full suite
   after EACH merge; every commit attributed via trailers; heavy processes
   staggered on small machines; paid budget single-writer.
4. Parallelism = worktrees, not optimism: `git worktree add -b wt/<slug>
   ../<dir> main` gives each agent its own directory, index, and dirty state;
   branches reappear only as worktree plumbing, merged serially after review.
5. Handoffs are asynchronous through files/commits — no agent ever waits live
   on another, so a rate-limited agent stalls only its own ticket, and any
   agent can resume another's work from the ticket log + files.

## Fits projects like
Any repo where 2+ AI agents (or agents + humans) work concurrently; solo
owners juggling multiple AI tools on one machine. The mode system matters most
when the same checkout serves everyone (laptops, small SBCs).

## Proven in
Origin project, 2026-07: three agents (senior + two juniors) on one Raspberry
Pi checkout. A live blocked-parallel incident (second agent correctly refused
a dirty shared tree) was resolved by ALONE→GROUP conversion: worktree cut from
last commit, ticket amended on its branch, implemented in parallel with work
in the root checkout, merged --no-ff with post-merge suites green. The
refusing agent's stop-and-report was the protocol working, not failing.

Partial transplant, 2026-07-17, host repo (book_podcast_fiction_generator):
the agent-entry-pointer half of the kit adopted — root `AGENTS.md` plus thin
per-tool pointers (`CLAUDE.md`, `QWEN.md`) for a senior Claude + junior
Codex/Qwen roster, routing every agent to the repo's `HANDOFF.md`. The
protocol/board half (ALONE/GROUP modes, worktrees) not yet adopted: work is
currently dispatched one ticket at a time on one Raspberry Pi checkout.

## Kit (deployable files in `kit/`)
`kit/MULTI_AGENT_PROTOCOL.md` (fill §8 deltas), `kit/BOARD.md`, `kit/AGENTS.md` (root entry pointer — clone per agent tool as CLAUDE.md/QWEN.md/...). Pair with trunk-review-queue's kit for the git side.
