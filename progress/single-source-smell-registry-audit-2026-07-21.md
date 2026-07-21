# Single-source smell — row-by-row registry audit (2026-07-21)

Classifies every `fiction_loop/core/field_registry.md` row under DECISION 15's ladder
(**eliminate → guard → discipline**). Zero-paid, offline. Feeds T-023 scope.

## The headline finding

**Most registry rows are NOT the smell.** The registry mixes two different things:
- **(D) Dataflow lineage** — producer writes a field, one/more consumers read it. No
  value is *duplicated*; this is healthy plumbing, not a single-source copy. Nothing to
  guard.
- **(C) Genuine copy** — the *same value* deliberately lives in ≥2 places. This is the
  only thing LAW 2 / the smell is about.

Of ~19 rows, **only 3 are genuine copies**, and **one of those already has its machine
guard.** So at the `field_registry` level the answer to "is there a lot more to fix?" is
**no — the copy surface is small and mostly already handled.** The fractal recurrence
(DECISION 15 archaeology) lives in the *other* discipline ledgers (`field_aliases`,
`pipeline_stage_manifest`, RULE-CHANGE AUDIT), not in this table's data rows.

## Genuine copies (the smell surface)

| Row | Value copied | Copies | Class | Action |
|---|---|---|---|---|
| arc cast quota | wrong-approach count per arc | `QUOTA_BY_ARC` (Python), assembler.md BEAT QUOTA + HARD RULE 7 | **Guard (irreducible) + Eliminate (partial)** | `QUOTA_BY_ARC` must be a Python value at gate time → irreducible → **guard** (done: regression freeze, `run.py:200`). The **assembler prompt count is a candidate for elimination** — the prompt is assembled by code, which could inject the count from the single source instead of the prompt restating it. Flag for T-023 review. |
| `arc_current` | `1 + count(arc summaries)` | `master_state.json.arc_current` cached copy | **Guard — ALREADY DONE** | Invariant `arc_current == 1 + count(summaries)`, machine-checked by `analyst.py --repair` (`field_registry.md:30`). **This is the owner's question-3 idea already built once** — the precedent to generalize, not new work. |
| `lead_failure_mode` | the next-chapter pointer | `update_brief.json.process_updates.lead_failure_mode` = "verbatim copy of the pointer" | **Guard (cheap) or accept** | An intentional archival snapshot for `failure_mode_lead_history`. Low stakes (write-once per chapter, immediately archived). A one-line "copy == pointer" assertion would close it; otherwise accept as a bounded snapshot. |

## Dataflow rows — NOT the smell (no action)

Producer→consumer plumbing, no duplicated value: `living_document.md`,
`failure_modes_shown_this_chapter`, the gate-consumed booleans, `.gate_pass.json`,
`prose_deficiencies.json`, the regression fixtures, `reader_can_suspect`, the four event-
card fields, `failure_mode_to_show`, `failure_mode_lead_history`,
`observable_log[].manifestation`, `chapter_type_contract.md`.

**Exemplar of elimination done right:** the forbidden-label check (`field_registry.md:19`)
*derives* its label set at runtime from `process_state` arrays — no copy exists to drift.
This is the pattern rows on the "eliminate" path should reach.

## What this means for T-023

T-023 is small and well-bounded:
1. **Guard the irreducible copy** already guarded (`QUOTA_BY_ARC`) — no new work, already
   frozen in `run.py`.
2. **Try to eliminate** the assembler-prompt quota restatement (inject from source at
   assembly time). If irreducible, guard it too.
3. **Optionally guard** `lead_failure_mode` with a one-line equality assertion.
4. **Generalize the `arc_current` freshness-invariant** as the reusable mechanism (stored
   derived value + source fingerprint) for any *future* copy that must persist — this is
   the machine-verifiable pattern from owner question 3, not invented, already live once.

No general parser (old Option B) and no big mechanization build — those stay factory-era
per DECISION 15 / D8 / D12.
