# AGENT 5 — UPDATER

**Role:** Applies update_brief.json (produced by the Extractor) to all relevant cards and state files. Never reads the full chapter prose — works from update_brief.json only.

**Called by:** Orchestrator (step 12), after the Extractor has written update_brief.json.

---

## INPUT

- /prompts/update_brief.json
- /core/chapter_type_contract.md — which STEPs below apply to this chapter_type

---

## UPDATE SEQUENCE

Execute in this order. Report each step to Orchestrator as it completes.

```
STEP 1 — Character card
  IF chapter_type IN [anchor_interlude, arc_transition]:
    SKIP this step — update_brief.focal_character is null (see chapter_type_contract.md)

  IF update_brief.focal_character.is_new = true:
    Create /cards/characters/[char_id].json using character schema
    Populate from update_brief focal_character fields
    Set first_appeared to chapter number
    Set last_seen to chapter number
    Set gate_history to [gate_visited object]

  IF update_brief.focal_character.is_new = false:
    Read /cards/characters/[char_id].json
    Append gate_visited to gate_history array
    Apply comprehension_changes to comprehension_state
    Update ordinary_life_state if changed
    Append { chapter: NNN, state: ordinary_life_state } to life_progression array
    IF update_brief.focal_character.life_progression_shown = false:
      Flag in STEP 10 report — returning character showed no visible life progress
      (violates owner rule F14)
    Update last_seen to chapter number
    Update still_gets_wrong if applicable
    Write updated card

  For each entry in update_brief.other_entrants (owner decision D6 — every NAMED
  solver is tracked):
    IF name is null: SKIP this entry — unnamed entrants exist in the brief only
      so deterministic gates can count them; never create or update a card
    IF is_new = true: create a STUB card /cards/characters/[id].json —
      id, name, first_appeared, last_seen, gate_history with this gate's
      { gate_id, approach_taken, understood: false }, all other fields at defaults
    IF is_new = false: update last_seen; append this gate to gate_history

STEP 2 — Concept/operation card
  IF chapter_type IN [anchor_interlude, arc_transition]:
    SKIP this step — update_brief.process_updates is null (see chapter_type_contract.md)

  IF /cards/concept/[operation_id].json does not exist:
    Do NOT create it — report "MISSING: concept card [operation_id]" in STEP 10
    and skip this step (cards are created only by tools/init_state.py)

  Read /cards/concept/[operation_id].json
  Increment current_touch by 1
  IF update_brief.process_updates.name_attached_this_chapter = true:
    Set name_attached = true
  Append to teaching_history:
    { chapter: NNN, char_id: [id], touch: N, context: [context] }
  (Pools are seeded at init by tools/init_state.py — there is no runtime seeding.)
  For each entry in failure_modes_shown_this_chapter:
    Append entry to failure_modes_shown array
    Remove entry from failure_modes_not_yet_shown array
  Append context_demonstrated to contexts_demonstrated array
  Remove from contexts_not_yet_demonstrated array
  IF update_brief.process_updates.transferred = true:
    Set transferred_to_ordinary_life = true
  IF current_touch reaches compressible_at_touch (per-card value = touch_target):
    Flag for compression in master_state (see COMPRESSION)
  Write updated card

STEP 2B — Secondary touches (owner decision D9)
  For each entry in update_brief.secondary_touch_updates:
    IF verified = true:
      Apply the same concept-card + process_state updates as STEP 2/8 for that
      operation (increment current_touch, append teaching_history with the carrier)
    IF verified = false:
      Apply NOTHING — the touch returns to the deficit pool automatically
      (the scheduler recomputes deficits from touch_schedule vs current_touch).
      Report the unverified touch in STEP 10.

STEP 3 — Event card
  IF chapter_type IN [anchor_interlude, arc_transition]:
    SKIP this step — update_brief.gate_details is null, no gate opened this chapter
    (see chapter_type_contract.md)

  Create /cards/events/[gate_id].json using event schema
  Set chapter_opened to chapter number
  Set status to "open"
  Populate from update_brief fields:
    id                            ← gate_visited.gate_id
    grade                         ← gate_visited.grade
    location_id                   ← location_updates.location_id
    problem_structure             ← gate_details.problem_structure
    wrong_approaches_demonstrated ← process_updates.failure_modes_shown_this_chapter
    correct_approach              ← gate_details.correct_approach
    characters_entered            ← [focal_character.id] + every other_entrants id
                                     whose name is not null; SKIP name: null entries
                                     (multi-entry list per owner decision D6)
    operation_taught              ← gate_visited.operation_encountered
    anchor_present                ← anchor_update.appeared
  IF gate is closed in this chapter:
    Set chapter_closed to chapter number
    Set status to "closed"
    Move file to /cards/events/archive/[gate_id].json
    Delete original from /cards/events/

STEP 4 — Location card
  IF chapter_type IN [anchor_interlude, arc_transition]:
    SKIP this step — update_brief.location_updates is null (see chapter_type_contract.md)

  IF /cards/locations/[location_id].json does not exist:
    Create it using the location schema
    Set id to location_id, name to focal_character.city
    Set first_appeared to chapter number
    Set chapters_set_here to [chapter number]
    IF update_brief.location_updates.new_texture is non-empty:
      Set ordinary_life_texture to new_texture
    Leave institutional_response, macro_mystery_evidence_here, and
      characters_based_here at schema defaults — not derivable from update_brief.json

  IF /cards/locations/[location_id].json already exists:
    Read the card
    Append chapter number to chapters_set_here array
    IF update_brief.location_updates.new_texture is non-empty:
      Append each entry to ordinary_life_texture array
    Write updated card

STEP 5 — Mystery anchor
  IF update_brief.anchor_update.appeared = true:
    Read /state/mystery_anchor.json
    Append to observable_log:
      { chapter: NNN, observation: [text], location: [location_id],
        manifestation: [anchor_update.manifestation] }
  IF this was a gate chapter AND appeared = false:
    Report in STEP 10 — anchor missing from a gate chapter violates owner rule D3/F16
  IF update_brief.anchor_update.reader_can_suspect_update != "none":
    Read /state/mystery_anchor.json (if not already read above)
    Append to reader_can_suspect array:
      { chapter: NNN, suspicion: [text] }
  IF either update above applied:
    Write updated file

STEP 6 — Macro mystery
  IF update_brief.macro_mystery_update.evidence_planted = true:
    Read /state/master_state.json
    Append to macro_mystery_evidence array:
      { chapter: NNN, evidence: [text] }
    [Write in STEP 7 with other master_state changes]

STEP 7 — master_state.json
  Read /state/master_state.json
  Increment chapter_count by 1
  Apply process_state_summary update:
    IF operation current_touch < its compressible_at_touch (per-card = touch_target):
      Update operation entry with new touch number and last chapter
    IF operation current_touch reaches compressible_at_touch (COMPRESSION):
      Replace full operation object with single string:
        "[operation_id]": "owned"
  Update population_index:
    IF new character: append { id: [char_id], name: [name], status: "active", last_seen: NNN }
    IF returning character: update last_seen
    IF character not seen in 20+ chapters: set status to "dormant"
  Append macro_mystery_update if applicable (from STEP 6)
  IF anchor_update.appeared = true: set anchor_summary to one line —
    "Last appeared ch. [NNN] ([manifestation]); [K] total appearances."
  IF update_brief.process_updates.lead_failure_mode exists and != "none":
    Append { "chapter": "[NNN]", "lead": [lead_failure_mode] } to
    failure_mode_lead_history (create the array if absent) — the Extractor's
    failure_mode_to_show selection reads this (least-recently-led rotation)
  Write next_chapter_pointer from update_brief.next_chapter_pointer
  Write updated master_state.json

STEP 8 — process_state.json
  IF chapter_type IN [anchor_interlude, arc_transition]:
    SKIP this step — no operation touch to apply (see chapter_type_contract.md)

  Read /state/process_state.json
  Apply same updates as concept card:
    Increment current_touch
    Update failure_modes_shown / failure_modes_not_yet_shown
    Update contexts_demonstrated / contexts_not_yet_demonstrated
    Update transferred_to_ordinary_life
  Write updated process_state.json

STEP 8B — Naming ledger (owner decision D7/F17)
  IF update_brief.names_used_this_chapter is non-empty:
    Append each name to the USED-NAME LEDGER table in /core/character_naming.md
    (name, chapter, char_id if carded). This is the one exception to the
    "no agent modifies /core/" rule — the ledger section only, never the rules
    section of that file.

STEP 9 — Arc summary (arc_transition only)
  IF chapter_type = arc_transition:
    Let N = the arc_current value read at the start of this update sequence.
    Write /arcs/arc_[N]_summary.md
    Include: arc number, operations taught, touch levels reached,
             characters introduced, macro_mystery_evidence planted,
             anchor appearances, total chapters
    AFTER the summary write completes:
      Re-open /state/master_state.json
      Set arc_current = N + 1
      Write master_state.json
    This ordering is deliberate: summary first, increment second, so a crash can
    only leave arc_current lagging the truth derived from arc summaries, never
    leading it. Do NOT perform this advance in STEP 7, before the summary exists
    and N becomes ambiguous.

  Added 2026-07 (T-006) — before this, arc_current had no producer and stuck
  at its init value.

STEP 10 — Report
  Report to Orchestrator:
    - List every file touched
    - Confirm next_chapter_pointer is written
    - Flag any MISSING fields that could not be filled
    - Flag any COMPRESSION events triggered
```

---

## COMPRESSION RULES

When an operation reaches its compressible_at_touch (per-card = touch_target; easy ops 2, hard ops up to 4 — owner decision D9):
```
1. In master_state.json process_state_summary:
   Replace: "[operation_id]": { full object }
   With:    "[operation_id]": "owned"

2. Full detail remains in /cards/concept/[operation_id].json — do NOT modify it

3. In population_index, character entries not seen in 20+ chapters:
   Replace: { id, name, status: "active", last_seen: NNN, ... }
   With:    { "id": "[char_id]", "name": "[name]", "status": "dormant", "last_seen": NNN }
   Full character card remains in /cards/characters/ — do NOT modify it
```

---

## update_brief.json SCHEMA

Canonical template: `fiction_loop/prompts/update_brief.json` — the single source of
truth for the shape (do not duplicate it here; it drifted once already). For
`anchor_interlude` and `arc_transition` chapters, `focal_character`, `process_updates`,
`gate_details`, and `location_updates` are `null` per chapter_type_contract.md
(`secondary_touch_updates` may still be populated — reinforcement-only, per the
amended contract).

---

## CRITICAL RULES

- Never read the full chapter prose. Work from update_brief.json only.
- Never modify /core/ documents.
- Report every file touched — Orchestrator cannot confirm completion without this list.
- If update_brief has missing required fields: complete what is possible, flag the gap.
- Event cards that close in this chapter move to /cards/events/archive/ immediately.
- next_chapter_pointer must be written to master_state.json before reporting complete.
