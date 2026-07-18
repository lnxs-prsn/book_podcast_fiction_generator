## FETCHED FIELDS — Chapter 006 — return_to_character:char_001

### SOURCE: /state/master_state.json
process_state_summary:
```json
{
  "op_what_is_missing": {
    "touch": 1,
    "last_chapter": "001"
  },
  "op_identify_unknown": "owned",
  "op_separate_condition": {
    "touch": 1,
    "last_chapter": "004"
  },
  "op_look_at_unknown": {
    "touch": 1,
    "last_chapter": "005"
  }
}
```

macro_mystery_evidence:
```json
[
  {
    "chapter": "001",
    "evidence": "The same figure appeared on the street before the gate opened and afterward recorded that the empty niche stayed visually constant across three different solver approaches, as if the gate were tracking what the solvers failed to see."
  },
  {
    "chapter": "002",
    "evidence": "A torn notebook page in unfamiliar handwriting is found on the floor inside the Achimota depot gate, using the same concise notation as the Lagos observation and recording Kwabena's wrong approach as the executor approach."
  },
  {
    "chapter": "004",
    "evidence": "A trace inside the gate room records three different solver approaches, the gap each missed, and the exact minute the condition was read clause by clause."
  },
  {
    "chapter": "005",
    "evidence": "The anchor's notebook logs all three wrong-approach solvers' entries side by side within the same gate event, each with precise register timestamps, before recording the correct approach — extending the simultaneous-approaches pattern first seen in chapter 004's trace."
  }
]
```

next_chapter_pointer:
```json
{
  "chapter": "006",
  "type": "return_to_character",
  "char_id": "char_001",
  "operation_due": "op_what_is_missing",
  "touch_due": 2,
  "name_due": false,
  "failure_mode_to_show": "none",
  "secondary_touches": [],
  "echo_touch": null,
  "anchor_appears": true
}
```

### SOURCE: /state/process_state.json — operation_due: op_what_is_missing

```json
{
  "name": "What is missing (absence over presence)",
  "difficulty_rating": 2,
  "arc_introduced": 1,
  "current_touch": 1,
  "name_attached": true,
  "name_at_touch": 1,
  "touch_schedule": {
    "1": 1,
    "2": 2
  },
  "touch_target": 2,
  "prerequisite": [],
  "teaching_history": [
    {
      "chapter": "001",
      "char_id": "char_001",
      "touch": 1,
      "context": "family_domestic"
    }
  ],
  "failure_modes_shown": [
    "the executor",
    "the system builder",
    "the information gatherer"
  ],
  "failure_modes_not_yet_shown": [],
  "contexts_demonstrated": [
    "family_domestic"
  ],
  "contexts_not_yet_demonstrated": [
    "workplace",
    "professional",
    "civic_institutional",
    "teaching_mentoring",
    "negotiation",
    "project_management",
    "creative",
    "argument_debate"
  ],
  "preferred_context": "family_domestic",
  "transferred_to_ordinary_life": true,
  "compressible_at_touch": 2
}
```

### SOURCE: /cards/characters/char_001.json
```json
{
  "id": "char_001",
  "name": "Yejide Adeyemi",
  "age": 0,
  "occupation": "fabric quality inspector at a garment factory",
  "location_id": "loc_lagos",
  "first_appeared": 1,
  "gate_history": [
    {
      "gate_id": "G-001",
      "grade": 2,
      "operation_encountered": "op_what_is_missing",
      "approach_taken": "the executor",
      "understood": true,
      "looked_back": true,
      "transferred_to_life": true
    }
  ],
  "comprehension_state": {
    "op_what_is_missing": "understood"
  },
  "still_gets_wrong": [],
  "ordinary_life_state": "Yejide shares a Lagos household with her younger sister Fadeke, who is trying to register for university, and their argument over missing paperwork and fees is resolved when Yejide asks what Fadeke actually needs.",
  "life_progression": [],
  "ordinary_life_transfers": [],
  "anchor_observed": false,
  "last_seen": 1,
  "next_planned_appearance": null
}
```

### SOURCE: /cards/locations/loc_lagos.json
```json
{
  "id": "loc_lagos",
  "name": "Lagos, Nigeria",
  "first_appeared": 1,
  "institutional_response": {
    "primary_body": "",
    "approach": "",
    "failure_mode": ""
  },
  "ordinary_life_texture": [
    "A kitchen table is covered with university registration forms, receipts, and pen caps during a morning argument.",
    "Sisters negotiate money for school fees, transport, and late penalties in a Lagos household."
  ],
  "macro_mystery_evidence_here": [],
  "characters_based_here": [],
  "chapters_set_here": [
    1
  ]
}
```

### SOURCE: /core/concept_curriculum.md — Arc 1 Section 4 (Wrong Approach Sequencing)

| Arc | Gate Grade | Wrong Approaches | Gate Signature Sequence | Mirror Content | Right Question | Why |
|---|---|---|---|---|---|---|
| Arc 1 | 1-2 | 1. The executor (acts immediately on obvious pattern) 2. The system builder (applies method regardless of fit) 3. The information gatherer (catalogues everything, asks nothing) | 1. Register 1 holds — contact, nothing. 2. Register flickers false 3, never holds. 3. Register 1, undisturbed — as if solver not yet present. Then Register 2 shift after sitting down. | 1. Room emphasises the obvious pattern — makes it cleaner, more legible. One element outside the pattern not receding. 2. Room mirrors the method's structure: everything categorised. Categorisation perfect. Gate elsewhere. 3. Room gives complete data. Still. The catalogue is the mirror. | What is the unknown here, really? What is missing rather than what is present? | Three visibly distinct mirrors. Reader learns to read them as a sequence. By the third they recognise what the mirror is showing before the solver does. |

### SOURCE: /core/concept_curriculum.md — Arc 1 Section 5 (Arc Breakdown)

| Arc | Gate Grade | Hard Operation | Easy Pairing | New Wrong Approach Type | Narrative Engine |
|---|---|---|---|---|---|
| 1 | 1-2 | Look at the unknown / what is missing (4) | Identify unknown / data / condition (2). Separate parts of condition (3). | Executor. System builder. Information gatherer. | First gates open. Society scrambling. Most survive Grade 1 by luck. Grade 2 begins killing those who got lucky on Grade 1. |

### SOURCE: /state/mystery_anchor.json — observable_log (last 3 entries)

```json
[
  {
    "chapter": "003",
    "observation": "Grade 2. Executor approach. Room emphasised sequential testing — jars aligned, labels clarified, spacing even. Underlined: chalkboard condition ignored. Register 2 at minute 8. Register 3 at minute 14.\n\nInformation gatherer approach. Room gave complete catalogue — no movement, no shift. Underlined: no question of purpose. Register 1 throughout.\n\nCorrect approach: threshold naming. Wanted/given/binding spoken before entry. Register 3 confirmed at utterance. Gate closed minute 19.",
    "location": "loc_accra",
    "manifestation": "bystander_mention"
  },
  {
    "chapter": "004",
    "observation": "Grade 2. Executor approach. Room organised by size sequence — large, medium, small files grouped, spacing even. Underlined: one file outside sequence. Solver did not look at it. Register 2 at minute 8. Register 3 at minute 10.\nSystem builder. Room mirrored categorical grid — six columns, chronological rows. Perfect assignment. Underlined: condition not in categories. Register flicker 1/3 throughout. No true Register 2.\nInformation gatherer. Room gave complete inventory — all objects logged, all surfaces noted. Underlined: no question asked of data. Register 1 entire session.\nCorrect approach: condition read clause by clause. Hand covered extraneous text. Register 3 at minute 52. Gate closed minute 53.",
    "location": "loc_nairobi",
    "manifestation": "traces"
  },
  {
    "chapter": "005",
    "observation": "Grade 1–2 / executor / room emphasises sequential file order; gap: unstamped envelope (slot L7); Reg 1 throughout; closure attempt min 10 — failed\nGrade 1–2 / system builder / room mirrors categorical grid; gap: categorisation ignores evidentiary type; Reg flicker 1→3→1; closure attempt min 14 — failed\nGrade 1–2 / information gatherer / room yields complete audit; gap: no question asked of data; Reg 1 undisturbed; closure attempt min 18 — failed\nGrade 1–2 / correct / Reg 2 at threshold-standing (min 19:03); Reg 3 at right question (min 19:47); gate closed min 20",
    "location": "loc_dakar",
    "manifestation": "seen"
  }
]
```
