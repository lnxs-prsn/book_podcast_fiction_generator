# Paid-call governance — caps before spend, receipts always, one budget writer

## What it is
A spend governor for LLM/API calls: every paid path routes through one tool
that (1) checks a per-purpose cap BEFORE the call — refusal is free; (2)
writes a receipt row (purpose, cycle/ticket id, timestamp) for EVERY call,
including $0 ones; (3) is the single writer of the spend ledger. Purposes get
their own cap keys (`ask`, `evaluate`, `probe`, ...); anything without a
declared budget is refused honestly rather than attempted.

## Problem it solves
Silent spend and unreconstructable provenance. Agents that can call paid APIs
will call them — in retries, in tests, in helpful extra passes. Later, nobody
can answer "what did this verdict cost and which call produced it?" The
origin's stance: the RECEIPT, not the price, is what makes a result's
provenance reconstructable — so even free-tier calls get receipted.

## How to use it
1. One `paid.py`-style wrapper owns all paid calls: `--cap-key <purpose>`
   +cycle/ticket id; it loads `spend_caps.json`, refuses over-cap with a
   nonzero exit and NO call made, else calls and appends to `spend.json`.
2. Degraded/failed responses are still receipted (the attempt cost money);
   withheld results are logged with reasons.
3. New paid features add a cap key + route through the wrapper as part of
   their spec — a paid path outside the wrapper is a review-blocking defect.
4. Implementer agents default to `Paid-calls: forbidden` in their tickets;
   proving a cap-block path must itself be free (refusal happens before
   spend — test it and assert the ledger did not grow).
5. Backends not yet authorized return None and the caller refuses cleanly —
   "honest refusal" beats a stubbed fake.

## Fits projects like
Anything where AI agents can trigger metered APIs; multi-agent setups
(single-writer budget is what prevents concurrent overspend); free-tier
projects that will someday have real bills and want the discipline installed
before the money matters.

## Proven in
Origin project, 2026: all paid paths (ask, evaluate, AI-adjudicate, probe,
live golden check) receipted through one wrapper with per-key caps; live
verification included a third call refused at cap 2 with exit 3 and a
receipts-grew/spend-didn't assertion; a receipting gap found in review
([P0]) was closed BEFORE any real adjudication use was allowed.

## Kit (deployable files in `kit/`)
`kit/STARTER.md` — spend_caps.json shape + the wrapper contract + the self-tests worth having.
