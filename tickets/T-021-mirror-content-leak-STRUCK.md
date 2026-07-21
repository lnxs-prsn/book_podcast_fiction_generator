# T-021 — mirror-content leak — STRUCK (not a leak)

**This is a status marker (tombstone), NOT a work order.** It holds the T-021 slot so
there is no gap in the ticket order. (Same role as `T-012-PLAN-SUPERSEDED.md`.)

## Verdict: struck 2026-07-20 — the suspected leak does not exist
The originally-proposed T-021 was "wrong-approach **mirror content** is hardcoded in the
chassis." Source-verification showed it is **not**:
- The Assembler **fetches** each wrong approach's mirror row from `world_rules.md` §5
  "Wrong Approach Mirror Behaviour" (`assembler.md:42-44`) and the mirror rules from
  §4B (`assembler.md:35`). Nothing mirror-related is hardcoded in any agent prompt.

So there is no leak to fix. Recorded as case law:
- **`fiction_loop/core/field_registry.md`** → "Known orphans / open items" → the
  **NOT-A-LEAK** note (do not re-raise).
- Current handoff `progress/handoff-2026-07-21-compacted-state.md` §5.

## Residual (separate, NOT this item)
`world_rules.md` lives in `core/`; in the multi-book factory it must become pack-scoped.
That is a Stage-level factory-build task, not a hardcode leak — do not conflate it with
T-021.

## Do NOT
Do not resurrect this as a leak-fix ticket. If `world_rules` pack-scoping is needed,
that is a factory-build item, tracked separately.
