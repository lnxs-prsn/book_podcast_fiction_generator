# Verify, don't trust — a log is a claim, not proof

## What it is
A verification culture with two teeth: (1) **reviewers re-run, never read**:
any agent's "all tests pass" is a claim until the reviewer executes the same
checks; (2) **engines verify LLM output before it becomes state**: an LLM may
propose (a quote, a recipe, a probe question, a candidate answer), but a
deterministic engine re-checks the proposal against the real artifact, and
only verified results are cached or acted on.

## Problem it solves
Confident wrong reports. LLMs (and tired humans) produce plausible summaries
of work not actually done, tests not actually run, quotes not actually in the
text. Every unverified claim that enters shared state (docs, ground truth,
caches) compounds — later work builds on it and the error becomes structural.

## How to use it
1. Review rule: before reporting a junior's result as true, re-run its
   acceptance checks yourself. Before repeating a doc's claim, check the
   authoritative source. Budget for this — it's the reviewer's actual job.
2. Propose→verify seam for LLM-derived data: design every LLM call so its
   output is *checkable* (verbatim quotes → substring check against source;
   extraction recipes → run them and compare; generated tests → must fail
   before the fix, pass after). Reject-and-log unverifiable output; never
   store it.
3. Fail-first proof: anything claiming to detect X must be shown detecting a
   planted X (a tampered record, a broken fixture) before its green is
   trusted.
4. Precondition dry-runs: before handing work to anyone, execute the commands
   you're about to require of them (see ticket-dispatch).

## Fits projects like
Everything with AI in the loop; especially systems whose OUTPUT becomes
training/ground truth for later stages, and any senior/junior agent split.

## Proven in
Origin project, 2026: caught a stale "decision pending" claim (repeated by a
reviewer without checking the ledger), a junior's premature "excluded from
both commits" log line (commits didn't exist yet), and an environment failure
misattributed to a code change (pre-existing monorepo break — proven by
re-running against the untouched line). On the engine side: grounded rubric
verdicts require verbatim-quote verification, probe questions are re-verified
for grounding before display, and tampered golden records make the checker
exit nonzero — all exercised live.

## Kit (deployable files in `kit/`)
`kit/REVIEW_CHECKLIST.md` — run top-to-bottom before reporting any work as done.
