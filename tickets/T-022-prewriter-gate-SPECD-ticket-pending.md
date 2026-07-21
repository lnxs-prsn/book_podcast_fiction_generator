# T-022 — pre-writer prompt gate — SPEC'D; implementation ticket PENDING

**This is a status marker, NOT a dispatchable work order.** (Same role as
`T-012-PLAN-SUPERSEDED.md` — it holds the T-022 slot so the number is discoverable
from `tickets/`.)

## Where the design lives
- **Spec:** `fiction_loop/specs/prewriter_gate.spec.md` — the single-source
  `gate_check_registry` + bidirectional parity guard; Phase A (validator) → Phase B
  (generative).
- **Decision:** `fiction_loop/human_decision.md` **DECISION 14**.
- **Queue:** current handoff `progress/handoff-2026-07-21-compacted-state.md` §5–§6.

## Why no work-order ticket yet (intentional)
The Phase-A registry seed = the full structural-gate check-set, which **T-024 and
T-026 extend**. Writing the ticket before they land would build the seed + parity
guard twice. So:

- **Blocked-until:** T-024 **and** T-026 land (ideally T-019 too — it finalizes the
  quota value's source).
- **When unblocked:** write the **Phase-A** ticket (read-only pre-writer validator +
  `gate_check_registry` + parity regression), implementing the spec. Recommended slot:
  after T-024→T-026→T-025→T-019, **before ch9** (it's free insurance against a paid
  gate failure on the ch9 run).
- **Phase B** (assembler + gate generate from the registry): a separate later ticket,
  **post-ch9** (it refactors chassis code). It is the DECISION 11 B2 consumer-map organ
  — build them as one.

## Do NOT
- Do not dispatch this file. Do not write the Phase-A ticket until T-024/T-026 land.
- When you write it, delete/replace this marker with the real ticket.
