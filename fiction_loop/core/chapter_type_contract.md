# CHAPTER TYPE FIELD CONTRACT

Canonical source for which `update_brief.json` sections apply to each `chapter_type`.
Extractor, Updater, and Consistency Checker must consult this table instead of each
re-deciding, locally and inconsistently, whether a section applies. When a new
`chapter_type` is ever added, update this table first — every guard in the three
consuming specs below is derived from it, not the other way around.

## Table

| Section | new_focal_character | return_to_character | anchor_interlude | arc_transition |
|---|---|---|---|---|
| focal_character | required | required | **null** | **null** |
| gate_details (event card) | required | required | **null** | **null** |
| process_updates (operation/touch) | required | required | **null** | **null** |
| secondary_touch_updates (reinforcement only) | optional (max 2 + echo) | optional (max 2 + echo) | optional (ambient only) | optional (ambient only) |
| location_updates | required | required | **null** | **null** |
| anchor_update | always evaluated | always evaluated | always evaluated | always evaluated |
| macro_mystery_update | always evaluated | always evaluated | always evaluated | always evaluated |
| next_chapter_pointer | always computed | always computed | always computed | always computed |
| arc summary (Updater STEP 9) | n/a | n/a | n/a | required |

## Rationale

`anchor_interlude` and `arc_transition` chapters use their own STRUCTURE blocks in
`assembler.md` and never introduce a focal character, gate, or operation —
`assembler.md`'s own CONSTRAINTS already forbid it:
- anchor_interlude: "next_chapter_pointer.operation_due is null for this type — do not
  manufacture gate-teaching content."
- arc_transition: "Does not teach a new operation directly — that begins next arc."

A step that unconditionally fills focal_character / gate_details / process_updates /
location_updates for these two types will either fabricate data that doesn't exist in
the prose, or silently write `"UNDETERMINED — ..."` noise into cards that shouldn't be
touched this chapter at all.

**Amendment (owner decision D9, 2026-07-02):** `anchor_interlude` and `arc_transition`
may carry *ambient reinforcement* — `secondary_touch_updates` entries for already-
cleared operations, verified in prose like any other secondary touch. They still never
introduce a new operation (`process_updates` stays null; `operation_due` stays null).

## Required guard pattern

Any section in Extractor's FILL PROCEDURE, any step in Updater's UPDATE SEQUENCE, or
any check in Consistency Checker's CHECKS that reads or writes a **null** cell above
must open with:

```
IF chapter_type IN [anchor_interlude, arc_transition]:
  SKIP — see chapter_type_contract.md
```

before running that section's normal logic.
