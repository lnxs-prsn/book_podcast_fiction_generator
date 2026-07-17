# Machine-enforced laws — every rule that matters gets a check

## What it is
The principle that a rule existing only as prose is a wish: each law the
project depends on gets a machine enforcement point — a git commit-msg hook
for commit format, a session start checklist that refuses to proceed on a
broken environment, gate scripts that judge work products against declared
criteria, spend caps checked BEFORE money moves. Plus self-tests for the
enforcers themselves.

## Problem it solves
Agents (and humans) violate written rules within hours — usually by accident,
under time pressure, or via a helpful shortcut. Detection by review is slow
and unreliable; detection by machine is instant and impartial. The origin
project watched its own reviewer break a staging rule it had written that
same day — prose alone does not hold.

## How to use it
1. Inventory the rules the project actually depends on (commit format, clean
   tree, no unreceipted spend, "done" criteria). For each, ask: what is the
   cheapest machine check that refuses or flags violations?
2. Typical enforcement points: `commit-msg` hook (format; install via a
   script that computes paths so it survives repo reshaping); a `session`/
   `preflight` script every work session runs first (env, health, venv, tree
   clean, hooks installed) — refusing with a REMEDY pointer, not just failing;
   `gate` scripts for acceptance; a spend governor for paid calls.
3. Distinguish gating from warning: a missing hook should WARN (a fresh clone
   must boot far enough to tell you to install it); a dirty tree should GATE.
4. Enforcers get self-tests, and changes to them are reviewed like product
   code — a wrong law does more damage than a wrong feature.
5. When a rule changes (new commit areas, new layout), change the enforcer in
   the same ticket — the origin's hook once would have rejected the repo's own
   recent history after a convention update that skipped the hook.

## Fits projects like
Anything multi-agent or long-lived; any repo where "we agreed to X" must
survive contributor turnover — human or AI. Cost is small: each enforcer is
tens of lines of stdlib scripting.

## Proven in
Origin project, 2026: ENF-numbered enforcement (hook, session checklist,
gates, paid.py caps) with self-tests, kept green through a monorepo migration
that briefly broke two enforcers — both failures were caught by the checks
themselves going red, ticketed, and fixed. The commit hook's reinstall commit
was validated by the hook it installed.

## Kit (deployable files in `kit/`)
`kit/commit-msg` — working POSIX hook, install instructions inside; edit its area list in lockstep with your conventions. `kit/PREFLIGHT.md` — design spec for the session start checklist (~100 lines of stdlib to implement).
