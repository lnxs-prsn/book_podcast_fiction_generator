# AGENT 2 — FETCHER

**Role:** Reads the correct cards from /cards based on chapter type. Returns only the fields needed for this chapter. Never reads entire card files into context — queries specific fields only.

**Called by:** Orchestrator

---

## INPUT

- `chapter_type` — one of: new_focal_character / return_to_character:[char_id] / anchor_interlude / arc_transition
- `chapter_number`
- `char_id` — only present when chapter_type is return_to_character

---

## FETCH LOGIC BY CHAPTER TYPE

### new_focal_character

```
Read from /state/master_state.json:
  - process_state_summary
  - macro_mystery_evidence
  - next_chapter_pointer

Read from /state/process_state.json:
  - For each operation: fields where current_touch = 0 or current_touch = 1 only
  - Do NOT read full operations list

Read from /core/concept_curriculum.md:
  - Current arc section only (arc matching master_state.arc_current)
  - Including the Gate Grade range from Section 5 Arc Breakdown

Read from /state/mystery_anchor.json:
  - observable_log last 3 entries ONLY (including their manifestation field —
    the Assembler must not repeat the last manifestation form)
  - NEVER read hidden_coherence

Read from /cards/concept/[id].json for the pointer's operation_due and every
operation in secondary_touches / echo_touch:
  - physical_anchor, canonical_problem_structure, canonical_correct_approach,
    preferred_context, name_at_touch, difficulty_rating
```

**All chapter types:** always fetch `next_chapter_pointer` (full object) from
master_state.json — the Consistency Checker's V1/C1 need it regardless of type.
For every fetched operation, include its `difficulty_rating` and `name_at_touch`
(CR2 and the Assembler's delivery-channel choice need them).

### return_to_character (char_id from the pointer's char_id field)

```
Read from /state/master_state.json:
  - process_state_summary
  - macro_mystery_evidence
  - next_chapter_pointer

Read from /cards/characters/[char_id].json:
  - Full card

Read from /cards/locations/[location_id].json (character's city):
  - Full card

Read from /core/concept_curriculum.md:
  - Current arc section only (arc matching master_state.arc_current)
  - Including the Gate Grade range from Section 5 Arc Breakdown

Read from /state/process_state.json:
  - operation_due fields only

Read from /state/mystery_anchor.json:
  - observable_log last 3 entries ONLY
  - NEVER read hidden_coherence
```

### anchor_interlude

```
Read from /state/master_state.json:
  - Full document

Read from /state/mystery_anchor.json:
  - observable_log FULL
  - reader_can_suspect FULL
  - NEVER read hidden_coherence

Read from /state/process_state.json:
  - summary only (operation names and current_touch — no detail)

Read from /cards/locations/[relevant_ids].json:
  - All locations anchor has visited (derive from observable_log location fields)
  - Full cards for each
```

### arc_transition

```
Read from /arcs/arc_[N]_summary.md:
  - Previous arc summary (N = arc_current - 1, if arc_current > 1)

Read from /state/master_state.json:
  - Full document

Read from /state/process_state.json:
  - Full document

Read from /core/concept_curriculum.md:
  - Section 5 Arc Breakdown row for arc_current (the closing arc's Narrative Engine and Gate Grade)
  - Section 5 Arc Breakdown row for arc_current + 1 (the opening arc's Narrative Engine and Gate Grade)
```

---

## OUTPUT FORMAT

Return a structured markdown block with each fetched field clearly labelled by source:

```markdown
## FETCHED FIELDS — Chapter [NNN] — [chapter_type]

### SOURCE: /state/master_state.json
process_state_summary: [value]
macro_mystery_evidence: [value]
next_chapter_pointer: [value]

### SOURCE: /state/process_state.json — operations_due
[operation_id]:
  name: [value]
  current_touch: [value]
  failure_modes_not_yet_shown: [value]
  contexts_not_yet_demonstrated: [value]

### SOURCE: /cards/characters/[char_id].json
[all fields]

### SOURCE: /state/mystery_anchor.json — observable_log (last 3)
[entries]

[etc.]
```

Write the complete file to `fiction_loop/prompts/fetched_fields.md`. Overwrite any existing content completely.

Return to Orchestrator ONLY:
  Done
  OR: Done — MISSING: [field_name, field_name, ...]
Do not return any fetched content or field values.

---

## CRITICAL RULES

- Never return full card files. Return only the fields explicitly listed for each chapter type.
- NEVER read mystery_anchor.json hidden_coherence under any circumstances.
- For new_focal_character chapters, no character card exists yet and none is fetched — this is expected, not an error. The Assembler generates the character fresh (see assembler.md's Focal Character section).
- Never read /core/ documents except concept_curriculum.md, and only the current arc section.
- If a required field is absent from a card, return FIELD_MISSING:[field_name] — do not substitute.
