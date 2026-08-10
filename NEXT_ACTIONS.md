# NEXT_ACTIONS — the work queue, and the reasoning behind it

**Two jobs.** (1) What is next. (2) **Why** — so the owner can audit the agent's judgment
on the many calls that never rise to a decision.

Most work does not need an owner ruling: what order to do things in, what to defer, how
to narrow a scope, when to strike a ticket. Those are made by the agent, silently, and
the owner never sees the reasoning. **§3 is where that reasoning is written down so it can
be challenged.** An objection there is cheap; discovering a bad call three chapters later
is not.

**Not to be confused with `fiction_loop/human_decision.md`** — that file holds forks that
need YOUR ruling before work can proceed (`grep -n "^## .*\[PROPOSED\]"` finds them).
This file holds calls the agent already made and is accountable for.

**Authority:** ticket files in `tickets/` own their own state; `progress/handoff-*` owns
project state. This file owns *ordering and rationale*. Where it disagrees with a ticket
about that ticket's status, the ticket wins.

**Update rule:** in the same sitting as the work. A judgment call made and not written in
§3 is the failure this file exists to prevent.

---

## 1. Next up — in order, with why now

1. **Re-derive ch9's stale `failure_mode_to_show` pointer.** *Why now:* one of two things
   holding a paid milestone, and the only one that needs nobody else. *Caveat:* output is
   **provisional** — if the open ch9 fork is ruled B, the selector's source may change and
   this needs redoing. Cheap either way. Zero-paid, senior.
2. **C3 "shown" design pass.** *Why now:* the long pole. It gates ADV-2/RDR-2 correctness
   in later arcs AND the bulk of the factory — more downstream work than ch9 — and it is
   startable precisely because ch9 is held. Deadline is before arc 3. Zero-paid, senior +
   owner ruling at the end.
3. **T-020** (anchor-description leak → `mystery_anchor.json`) and **T-023** (curriculum §9
   de-dup). *Why now:* both drafted, dry-run-verified, independent of everything above.
   Dispatchable the moment there is an implementer free. Zero-paid.
4. **T-022 Phase-A ticket** (pre-writer gate validator). *Why now:* its blockers T-024 and
   T-026 have both landed, so it is writable today; it is the factory spec's designated
   first build. Zero-paid, senior writes.

## 2. Deferred on purpose — with why not now

- **ch9 re-run (PAID).** Blocked on the open fork in `human_decision.md` plus item 1
  above. Standing instruction: no override of the gate, no blind redo — both causes are
  upstream of the Writer, so a redo reproduces the FAIL and burns tokens.
- **T-019** (`QUOTA_BY_ARC` leak). Offline, so it *could* run now. Deferred because it
  guards no ch9-class failure — no reason to spend attention before the milestone.
- **T-022 Phase B** (generative gate). Post-ch9 by design (DECISION 14); additive.
- **Widening T-024's canonicity check.** Deliberately not started: the shape of the fix is
  different under each option of the open ch9 fork. Starting it now is guessing.
- **B3, RDR-3** design work. Real, but C3 outranks both on leverage.
- **Backlog, unstarted and not urgent:** ADV-5 Updater idempotency stamp (D11-B1); P2
  calibration organ (ch1–8 are its seed data, so it wants to exist soon-ish); P3 fire
  `anchor_interlude` (PAID); the paid Stage-5 one-way-door read.
- **Stale-constraint sweep** of specs + drafted tickets. Not yet a ticket; assign with the
  next dispatch batch.

## 3. Judgment calls made without asking you — the auditable record

**Newest 5 only.** Each is a call the agent made alone. **Object to any of them.** When a
6th arrives the oldest is MOVED (not copied) to the ledger — one home per entry, so
nothing can drift.

**Ledger:** `progress/agent-decisions.jsonl` — append-only, one JSON object per line.
Read it with stdlib, no dependencies:

```
.venv/bin/python -c "import json;[print(f\"{r['date']}  {r['summary']}\") for r in map(json.loads, open('progress/agent-decisions.jsonl'))]"
```

Filter it — e.g. every call that contradicted a written project claim, or every
irreversible one:

```
grep '"contradicts-handoff"' progress/agent-decisions.jsonl
grep '"reversible": false' progress/agent-decisions.jsonl
```

Record fields: `date · id · type · by · summary · reasoning · reversible · flags · refs`.
`reversible` is `true` / `false` / `"cheap"`. Useful `flags`: `scope-narrowed`,
`scope-corrected`, `ticket-struck`, `contradicts-handoff`, `assumption-falsified`,
`sequencing`, `schema-change`.

**2026-08-10 — Reverted `OPEN_DECISIONS.md` into `human_decision.md`.** Open forks now
append to the existing ledger and flip status in place, found by grep. *Reasoning:* a
separate file needed three constitutional amendments and a move-on-ruling step that would
eventually be forgotten; keeping forks in the ledger meant LAW 13 and the document map
needed no change at all, and only one word of `CONTRIBUTING.md` §4 step 7 actually
conflicted ("stop" → file-and-continue). *Reversible:* yes, trivially.

**2026-08-10 — Made "Analogy" optional in the decision schema.** *Reasoning:* a forced
analogy on a decision that does not need one smuggles in a wrong intuition, which is
worse than no analogy. Every other schema field is mandatory.

**2026-08-10 — Treating the ch9 pointer re-derivation as provisional, not independent.**
The handoff asserts the two ch9 causes are independent. *Reasoning:* the pointer is
produced by the T-026 selector; if the open fork is ruled B, that selector's source may
change. Cheap-to-redo is not the same as independent, so the claim is flagged rather than
trusted. *This contradicts a handoff claim* — worth your eye.

**2026-08-10 — Ranked C3 above ch9 for attention.** *Reasoning:* ch9 is a milestone but
gates only itself; C3 gates later-arc correctness plus most of the factory. Stated in
DECISION 12-C2 that the factory build follows ch9, so this is a sequencing call within
that, not a contradiction of it.

**2026-08-10 — Filed the ch9 wrong-approach fork with three options, not the two the
handoff framed.** *Reasoning:* reading the state files showed both the operation pool and
the book-wide pool are exhausted, so neither original option answers the general case; the
union option follows DECISION 13's already-ruled selector shape.

*(3 earlier calls — T-024 acceptance correction, T-025 scope narrowing, T-021 struck —
rotated to the ledger 2026-08-10.)*

## 4. Recently done — newest 5 only

- **T-025** prose name-presence guard — `f8225f7`
- **T-026** selector earned-pool fallback + `"none"` guard — `c0dcade`
- **T-024** gate cross-field integrity — `7dbc237`
- **ch9 attempt** — run PAID, blocked at gate 11.5, held safely. The gate caught two
  upstream defects it was built to catch; not a failed run.
