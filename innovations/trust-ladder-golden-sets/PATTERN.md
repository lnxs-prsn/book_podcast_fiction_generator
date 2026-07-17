# Trust ladder + golden sets — autonomy earned per-capability from logged evidence

## What it is
A governance pattern for growing AI autonomy safely: every automated judgment
starts as a *proposal* a human confirms or overturns; rulings are logged; a
capability may graduate to auto-confirm ONLY when its logged human-override
rate crosses a declared threshold (e.g. <10% over the last 50 real rulings) —
and even then graduation is *proposed* to the owner, never self-granted, is
scoped to that one capability, keeps logging, and auto-suspends if the rate
degrades. Confirmed-good cases freeze into a read-only **golden set**: the
regression ground truth every future change must re-pass.

## Problem it solves
The two standard AI-autonomy failures: granting it by schedule/optimism
("it's been fine for a week"), and never granting it at all (human
rubber-stamps forever, learning nothing). Also ground-truth poisoning: if
fabricated or unverified verdicts enter the reference set, every later
evaluation inherits the rot.

## How to use it
1. Every automated verdict lands in an adjudication queue as PENDING; a human
   confirms/overturns; superseding records (`.rN` revisions) never overwrite
   originals.
2. Freeze confirmed cases (with explicit consent) into read-only golden
   cases; a `golden check` re-runs current logic against frozen inputs and
   diffs against frozen human verdicts — green golden check becomes the
   change gate for the evaluating code.
3. Compute per-capability override rates from the ruling log; REPORT
   eligibility, never grant it. Graduation is a written proposal the owner
   answers; the accepted RULE (thresholds, scope, auto-suspend) is itself a
   ledger decision made once, in advance.
4. NEVER fabricate rulings/cases to reach a threshold — that poisons the
   ground truth the whole design rests on. If no human expert exists, a
   second AI may rule PROVISIONALLY — flagged as such everywhere, stamped
   into frozen cases, and superseded by a human path the moment one appears.
5. Distinguish drift from regression: a live-only mismatch on a clean tree is
   model/world drift (log + re-adjudicate), not a code block.

## Fits projects like
AI evaluation/grading systems, content moderation, medical/legal triage
assistants, any pipeline where AI judgments accumulate authority over time.

## Proven in
Origin project, 2026: full spine implemented and live-tested — adjudication
queue with queue-limit refusal, golden freeze/refreeze/retire with consent,
tamper detection (tampered frozen verdict exits nonzero naming the case),
per-type overturn stats reporting graduation ELIGIBILITY only, the
AI-provisional adjudicator with human supersede verb, and an owner-accepted
graduation rule recorded in the decision ledger before any capability was
eligible. Build phases beyond it stayed correctly blocked pending real
evidence (H-signals), resisting weeks of temptation to "just build ahead."

## Kit (deployable files in `kit/`)
`kit/GRADUATION_RULE_TEMPLATE.md` — the decide-the-rule-in-advance ledger entry; paste into your decision ledger and have the owner answer it while nothing is yet eligible.
