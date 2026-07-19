# Handoff discipline — a dated, stale-marked orientation doc with update triggers

## What it is
One orientation document (`HANDOFF.md`) that any cold session — new AI agent,
new machine, the owner after a month away — reads first, plus written rules
for keeping it truthful: explicit update triggers, dated append-only sections,
stale-marking instead of silent rewrites, and a verify-before-repeat rule.

## Problem it solves
Orientation docs rot. Worse: a stale claim in a trusted doc gets *repeated
forward* by each new reader (including AI agents summarizing it), compounding
into false institutional memory. And after a machine dies or a session resets,
undocumented context is simply gone.

## How to use it
1. The handoff is a **summary-and-pointer** doc, never a ledger: status lives
   in STATUS files, decisions in the decision ledger, truth in code. Files
   always override the handoff.
2. Update triggers (no trigger → no update): (a) you changed state a cold
   session needs — update in the same sitting; (b) you FOUND a doc telling
   lies — record it even if you changed nothing; (c) session end after either
   — re-read the top section once.
3. Method: append dated sections; never silently rewrite history — mark wrong
   passages in place (`~~struck~~ STALE — <truth>; see <dated section>`);
   **verify every claim against its authoritative file before writing OR
   repeating it**; name the evidence ("verified against decisions.md <ts>");
   keep a top banner pointing at the newest section so a cold reader reaches
   current truth in one hop.
4. Anyone may update it — recording true state is never out of scope. An
   implementer with a tight write-set logs the finding in its ticket instead,
   and the reviewer carries it over.
5. **Compact when the ledger stops being a one-hop read** (append-only means
   it grows; rule of thumb ~10+ dated sections). Write a fresh
   `*-compacted-state` doc holding ONLY live current truth (state, roles,
   still-binding facts, open queue, read-first order), **re-verifying every
   carried-forward fact against its source as you write it** — compaction is
   the highest-risk moment for copying staleness. Never delete the old ledger;
   it stays as the archived *why*. Repoint the front door at the compacted
   file. Keep this by-hand until the by-hand cost hurts; do not pre-build a
   heavier rotation.

## Fits projects like
Anything with disposable AI sessions, long gaps between work sessions,
machine migrations, or multiple agents. The smaller the team's shared memory,
the more load this one file carries.

## Proven in
Origin project, 2026-07: a machine death was survived cleanly — the next
session reconstructed full state from handoff + STATUS files and was working
within minutes. The rules themselves were forged by a real failure: a
"decision still pending" claim was repeated 6 days after the ledger said
ACCEPTED, by a reviewer who copied the handoff without checking — that
incident is cited inside the rules as case law, and the verify-before-repeat
rule exists because of it.

First transplant, 2026-07-17, host repo (book_podcast_fiction_generator,
commit 71ea7ea): adopted after an OS migration + fresh clone left a cold
agent orienting from two confidently-stale 2026-05 docs (one literally
promising "cold-start in under 5 minutes"). Root `HANDOFF.md` front door +
STALE banners on the three trap docs + agent entry pointers. Known delta
from the kit: dated handoff sections live as separate files in `progress/`
(the host repo's pre-existing convention) instead of appended sections in
HANDOFF.md itself; HANDOFF.md holds only the banner, read-order, and trust
map.

Compaction proven 2026-07-19, same host repo: a running ledger reached 14
dated sections / 426 lines — no longer a one-hop read — and was compacted into
a 119-line current-state front door, every carried fact re-verified against
state/code at the compaction commit, the old ledger archived (not deleted).
That exercise forged the compaction rule (step 5) now in the kit.

## Kit (deployable files in `kit/`)
`kit/HANDOFF_RULES.md` + `kit/HANDOFF_TEMPLATE.md` — copy both; start the handoff from the template on day one.
