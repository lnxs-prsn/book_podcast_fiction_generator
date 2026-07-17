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

## Kit (deployable files in `kit/`)
`kit/HANDOFF_RULES.md` + `kit/HANDOFF_TEMPLATE.md` — copy both; start the handoff from the template on day one.
