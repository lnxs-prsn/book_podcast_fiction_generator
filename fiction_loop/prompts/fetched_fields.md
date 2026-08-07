## FETCHED FIELDS — Chapter 009 — return_to_character:char_004

### SOURCE: /state/master_state.json

process_state_summary:
```json
{
  "op_what_is_missing": "owned",
  "op_identify_unknown": "owned",
  "op_separate_condition": {
    "touch": 1,
    "last_chapter": "004"
  },
  "op_look_at_unknown": {
    "touch": 1,
    "last_chapter": "005"
  },
  "op_check_result": {
    "touch": 1,
    "last_chapter": "008"
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
  },
  {
    "chapter": "006",
    "evidence": "A torn notebook page found inside the Lagos fabric-inspection gate records all four solver approaches with register timestamps at second-level precision, showing the anchor can observe multiple solvers within the same gate event and diagnose their mental frames in real time across different approaches."
  },
  {
    "chapter": "007",
    "evidence": "Five torn notebook pages from the anchor, recovered from gates in Achimota, Kumasi, Lagos, and Dakar, are discovered by a junior clerk in the Accra guildhall archives. The pages use consistent diagnostic terminology (executor, system builder, information gatherer) to classify solver approaches across different gates and cities. The pages are photocopied and sent to the senior coordinator, then shelved without review."
  },
  {
    "chapter": "008",
    "evidence": "The Kampala notebook page records two Arc 2 wrong-approach types (specialist, tester) using the anchor's diagnostic framework, expanding the taxonomy across five cities; the guild files the gate report as an 'anomalous closure' with the word 'checking' written unconsciously in the margin, continuing the pattern of the guild noticing but failing to interpret the anchor's accumulating records."
  }
]
```

next_chapter_pointer:
```json
{
  "chapter": "009",
  "type": "return_to_character",
  "char_id": "char_004",
  "operation_due": "op_separate_condition",
  "touch_due": 2,
  "name_due": true,
  "failure_mode_to_show": "none",
  "secondary_touches": [],
  "echo_touch": null,
  "anchor_appears": true
}
```

### SOURCE: /cards/characters/char_004.json — FULL CARD

```json
{
  "id": "char_004",
  "name": "Wanjiku Mwangi",
  "age": null,
  "occupation": "medical records clerk at a public hospital in Nairobi",
  "location_id": "loc_nairobi",
  "first_appeared": 4,
  "gate_history": [
    {
      "gate_id": "G-004",
      "grade": 2,
      "operation_encountered": "op_separate_condition",
      "approach_taken": "none — applied correctly",
      "understood": true,
      "looked_back": true,
      "transferred_to_life": true
    }
  ],
  "comprehension_state": {
    "op_separate_condition": "encountered"
  },
  "still_gets_wrong": [],
  "ordinary_life_state": "Back at her hospital desk, Wanjiku faces a fused memo with ten requests and three signatures, then rewrites each requirement separately and solves them one by one.",
  "life_progression": [],
  "ordinary_life_transfers": [],
  "anchor_observed": false,
  "last_seen": 4,
  "next_planned_appearance": null
}
```

### SOURCE: /cards/locations/loc_nairobi.json — FULL CARD

```json
{
  "id": "loc_nairobi",
  "name": "Nairobi, Kenya",
  "first_appeared": 4,
  "institutional_response": {
    "primary_body": "",
    "approach": "",
    "failure_mode": ""
  },
  "ordinary_life_texture": [
    "Fused memos stamped URGENT — ACTION REQUIRED land on clerks' desks with multiple supervisor signatures.",
    "A billing colleague across the aisle notices when someone stops treating the whole memo as one problem and goes still.",
    "Office noise dips for a breath when a clerk changes register before anyone has spoken."
  ],
  "macro_mystery_evidence_here": [],
  "characters_based_here": [],
  "chapters_set_here": [
    4
  ]
}
```

### SOURCE: /core/concept_curriculum.md — Arc 2 SECTION ONLY

#### Section 5 Arc Breakdown — Arc 2 row:

| Arc | Gate Grade | Hard Operation | Easy Pairing | New Wrong Approach Type | Narrative Engine |
|---|---|---|---|---|---|
| 2 | 2-3 | Do you know a related problem? / Here is a problem related to yours (4) | Did you use all the data? (3). Can you check the result? (3). Looking back / transfer (4). | Confident specialist. Hypothesis tester. | Guild methods failing on Grade 2-3. Characters with wide ordinary-life experience solving gates specialists cannot. |

#### Section 4 Wrong Approach Sequencing — Arc 2 row:

| Arc | Wrong Approaches to Show (in sequence) | Gate Signature Sequence | Mirror Content Shown | Right Question That Arrives | Why This Sequence |
|---|---|---|---|---|---|
| Arc 2 | 1. The confident specialist (applies domain expertise to wrong problem type) 2. The hypothesis tester (tests systematically without naming what is being tested) | 1. Register 2 touched briefly, then lost — domain runs out. 2. Register flickers rapidly — signal noise. Then Register 2 shift after sitting down. | 1. Room organises by domain boundary. Domain elements grouped. Gap between groups contains the unknown. Solver looks inside the groups. 2. Room mirrors each hypothesis in sequence. Sequence of endings has a shape — visible only if you stop and look at all of them together. | What does this remind me of? What did I do last time the unknown looked like this? | Arc 2 mirrors show domain limits and hypothesis sequences. Reader who can read them sees the gap before the solver does. |

### SOURCE: /state/process_state.json — operation_due (op_separate_condition) FIELDS ONLY

```json
{
  "name": "Separate the parts of the condition",
  "difficulty_rating": 3,
  "arc_introduced": 1,
  "current_touch": 1,
  "name_attached": false,
  "name_at_touch": 2,
  "touch_schedule": {
    "1": 1,
    "2": 2
  },
  "touch_target": 2,
  "prerequisite": [
    "op_identify_unknown"
  ],
  "teaching_history": [
    {
      "chapter": "004",
      "char_id": "char_004",
      "touch": 1,
      "context": "workplace"
    }
  ],
  "failure_modes_shown": [
    "the executor",
    "the system builder",
    "the information gatherer"
  ],
  "failure_modes_not_yet_shown": [],
  "contexts_demonstrated": [
    "workplace"
  ],
  "contexts_not_yet_demonstrated": [
    "professional",
    "family_domestic",
    "civic_institutional",
    "teaching_mentoring",
    "negotiation",
    "project_management",
    "creative",
    "argument_debate"
  ],
  "preferred_context": "workplace",
  "transferred_to_ordinary_life": true,
  "compressible_at_touch": 2
}
```

### SOURCE: /state/mystery_anchor.json — observable_log LAST 3 ENTRIES ONLY

```json
[
  {
    "chapter": "006",
    "observation": "Gate G-006 (Grade 2)\nEntrants: four.\nApproach A (executive pattern-match) — Register 1 throughout. Room sorts by colour; hook 4 remains empty, not receding.\nApproach B (grid taxonomy) — Register 1 with false 3 flicker on completion. Room mirrors categorical grid; hook 4 sits in cell 'unmatched'.\nApproach C (full audit) — Register 1 undisturbed. Room yields complete catalogue; item 4 listed as 'empty', no query.\nTimeout at 14:02:17 — no closure.\nApproach D (threshold-standing, gaze-to-gaps) — Register 2 at sit. Hand on hook 4 at 14:03:51. Latch at 14:04:03. Gate closed 14:04:05.\n— Gap: absence unnamed by A, B, C. Named by D.",
    "location": "loc_lagos",
    "manifestation": "notebook_page"
  },
  {
    "chapter": "007",
    "observation": "UNDETERMINED — no verbatim notebook entry in chapter prose; a junior clerk at the Accra guildhall discovers five torn notebook pages in a folder labelled 'Unidentified Documents—Gates'. Three share the same notebook stock. Each page records gate events with solver approaches, register timestamps, and missed observations. The terms 'executor', 'system builder', and 'information gatherer' recur across all five pages. The pages were recovered from gates in Achimota, Kumasi, Lagos, and Dakar. The clerk photocopies them and sends them to the senior coordinator, where they are filed without review.",
    "location": "loc_accra",
    "manifestation": "notebook_page"
  },
  {
    "chapter": "008",
    "observation": "Grade 2. Specialist approach. Room organised by chemical category — all analgesics grouped, all antibiotics grouped, all cardiovascular agents grouped. Reference chart outside groups, dim. Domain boundary visible as gap between analgesic and cardiovascular clusters. Underlined: gap between groups contained the correct formulation. Solver did not look at the gap. Register 2 at minute 8, lost at minute 11. No closure.\n\nGrade 2. Tester approach. Room mirrored each configuration in sequence — twelve arrangements, each ending at panel. Panel present in every configuration, unactivated. Underlined: panel was the test. Solver never asked what was being tested. Register flicker throughout. No sitting down. No closure.",
    "location": "loc_kampala",
    "manifestation": "notebook_page"
  }
]
```
