## FETCHED FIELDS — Chapter 003 — return_to_character

### SOURCE: /state/master_state.json

`process_state_summary`:
```json
{
  "op_what_is_missing": {
    "touch": 1,
    "last_chapter": "001"
  },
  "op_identify_unknown": {
    "touch": 1,
    "last_chapter": "002"
  }
}
```

`macro_mystery_evidence`:
```json
[
  {
    "chapter": "001",
    "evidence": "The same figure appeared on the street before the gate opened and afterward recorded that the empty niche stayed visually constant across three different solver approaches, as if the gate were tracking what the solvers failed to see."
  },
  {
    "chapter": "002",
    "evidence": "A torn notebook page in unfamiliar handwriting is found on the floor inside the Achimota depot gate, using the same concise notation as the Lagos observation and recording Kwabena's wrong approach as the executor approach."
  }
]
```

`next_chapter_pointer`:
```json
{
  "chapter": "003",
  "type": "return_to_character",
  "char_id": "char_002",
  "operation_due": "op_identify_unknown",
  "touch_due": 2,
  "name_due": true,
  "failure_mode_to_show": "the information gatherer",
  "secondary_touches": [],
  "echo_touch": null,
  "anchor_appears": true
}
```

---

### SOURCE: /state/process_state.json — operation_due

`op_identify_unknown`:
- `name`: Identify unknown / data / condition
- `current_touch`: 1
- `failure_modes_not_yet_shown`: ["the information gatherer"]
- `contexts_not_yet_demonstrated`: ["professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"]
- `difficulty_rating`: 2
- `name_at_touch`: 2

---

### SOURCE: /cards/characters/char_002.json

Full card:
- `id`: char_002
- `name`: Kwabena Asante
- `age`: null
- `occupation`: bus depot scheduler
- `location_id`: loc_accra
- `first_appeared`: 2
- `gate_history`:
  ```json
  [
    {
      "gate_id": "G-002",
      "grade": 2,
      "operation_encountered": "op_identify_unknown",
      "approach_taken": "the executor",
      "understood": true,
      "looked_back": true,
      "transferred_to_life": true
    }
  ]
  ```
- `comprehension_state`:
  ```json
  { "op_identify_unknown": "encountered" }
  ```
- `still_gets_wrong`: []
- `ordinary_life_state`: Kwabena works in the Achimota bus depot dispatch office, where a missing afternoon roster assignment for Bus 404 on the Tema route forces him to stop before opening any file and ask what they are actually trying to find.
- `life_progression`: []
- `ordinary_life_transfers`: []
- `anchor_observed`: true
- `last_seen`: 2
- `next_planned_appearance`: null

---

### SOURCE: /cards/locations/loc_accra.json

Full card:
- `id`: loc_accra
- `name`: Accra, Ghana
- `first_appeared`: 2
- `institutional_response`:
  ```json
  {
    "primary_body": "",
    "approach": "",
    "failure_mode": ""
  }
  ```
- `ordinary_life_texture`:
  - A dispatch office ceiling fan turns overhead with a low, rhythmic clicking sound.
  - A depot manager and a roster clerk reconcile a missing bus assignment using sign-out logs and filing cabinets.
  - Driver claims about a bus being in the yard are checked against the official roster log.
- `macro_mystery_evidence_here`: []
- `characters_based_here`: []
- `chapters_set_here`: [2]

---

### SOURCE: /core/concept_curriculum.md — Arc 1 (current arc)

#### Section 4 — Wrong Approach Sequencing (Arc 1)

| Arc | Wrong Approaches to Show (in sequence) | Gate Signature Sequence | Mirror Content Shown | Right Question That Arrives | Why This Sequence |
|---|---|---|---|---|---|
| Arc 1 | 1. The executor (acts immediately on obvious pattern) 2. The system builder (applies method regardless of fit) 3. The information gatherer (catalogues everything, asks nothing) | 1. Register 1 holds — contact, nothing. 2. Register flickers false 3, never holds. 3. Register 1, undisturbed — as if solver not yet present. Then Register 2 shift after sitting down. | 1. Room emphasises the obvious pattern — makes it cleaner, more legible. One element outside the pattern not receding. 2. Room mirrors the method's structure: everything categorised. Categorisation perfect. Gate elsewhere. 3. Room gives complete data. Still. The catalogue is the mirror. | What is the unknown here, really? What is missing rather than what is present? | Three visibly distinct mirrors. Reader learns to read them as a sequence. By the third they recognise what the mirror is showing before the solver does. |

#### Section 5 — Arc Breakdown (Arc 1)

| Arc | Gate Grade | Hard Operation | Easy Pairing | New Wrong Approach Type | Narrative Engine |
|---|---|---|---|---|---|
| 1 | 1-2 | Look at the unknown / what is missing (4) | Identify unknown / data / condition (2). Separate parts of condition (3). | Executor. System builder. Information gatherer. | First gates open. Society scrambling. Most survive Grade 1 by luck. Grade 2 begins killing those who got lucky on Grade 1. |

---

### SOURCE: /state/mystery_anchor.json — observable_log (last 3 entries)

Entry 1:
- `chapter`: 001
- `observation`: Grade 2.

  Approach sequence: executor → system builder → information gatherer.

  Mirror content: Room first emphasised the visible pattern among the birds (size, then posture), then sorted them into perfect categories, then offered a complete still catalogue. In all three arrangements the empty niche remained at the same height, same size, same shadow. It did not recede.

  Underlined: the empty niche was the unknown. Every mirror showed it. None of the solvers looked at it.

  Register 2 at minute 38. Register 3 at minute 41. Three minutes from sitting down to right question.
- `location`: loc_lagos
- `manifestation`: seen

Entry 2:
- `chapter`: 002
- `observation`: Grade 2. Executor approach. Room arranged the visible route data into a cleaner sequence — edges aligned, spacing even, the obvious pattern made more obvious. Underlined: the solver never named what was wanted before acting. Register 2 at minute 33. Register 3 at minute 36. Three minutes from sitting down to right question.
- `location`: loc_accra
- `manifestation`: notebook_page
