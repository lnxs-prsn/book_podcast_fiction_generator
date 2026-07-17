# File-state machine — disposable AI sessions over durable file state

## What it is
An architecture where the SYSTEM is files and the AI sessions operating it are
disposable: all durable state lives in versioned plain files (registries,
queues, state docs, receipts); one session runs one *cycle* of declared work;
every cycle ends in exactly one commit. New kinds of work are added **by
declaration only** (a registry row + a cycle procedure doc) — if a new cycle
type requires changing the core machinery, that's a design leak to find, not
an edit to make.

## Problem it solves
Making any agent's context, memory, uptime, or rate limit load-bearing. When
state lives in a chat history or an agent's "memory," a crashed session, a
model swap, or a dead laptop loses work. Files + commits make every session
killable at any instant with bounded loss, and any agent (or human) resumable
from disk alone.

## How to use it
1. Define the chassis once: directory layout, a cycle registry (one row per
   cycle type: its gate, its owned state files), per-cycle procedure docs,
   session conduct rules (start ritual: read entry doc → run preflight; end
   ritual: clean tree or journaled dirty state).
2. Cycles are atomic: one unit of work, its receipts, one commit. The commit
   is the transaction boundary AND the claim/lock.
3. All writes go to files the cycle's registry row owns; cross-cycle state
   (queues, decisions) has exactly one writer at a time.
4. Growth = declaration: adding a work type touches only registry + its own
   doc + its own gate function slot. Validate this property deliberately —
   the origin ran a whole cycle type addition as a test that ZERO core files
   changed.
5. Keep prose truth and structured truth separate (BUILD_LOG.md for rationale,
   build_status.json for machine-readable state) — never duplicate one in the
   other.

## Fits projects like
Long-running AI-operated systems (automation loops, data pipelines, learning
tools); anything operated by rotating/disposable sessions across weeks. Less
useful for one-shot builds.

## Proven in
Origin project, 2026: the `autopsy_loop` chassis ran proto/learn/audit cycles
across dozens of disposable sessions and two machines; the audit cycle type
was added by declaration only (verified: zero core-file diffs); a full machine
death lost nothing that was committed — the new machine resumed the exact
in-flight learning exercise from files.

## Kit (deployable files in `kit/`)
`kit/STARTER.md` — the minimal chassis file set (RUN.md, cycle registry, cycle doc, journal, structured status) as copy-paste blocks.
