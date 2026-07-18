## FETCHED FIELDS — Chapter 007 — arc_transition

### SOURCE: /arcs/arc_0_summary.md
arc_current = 1, so no previous arc summary exists (spec: "if arc_current > 1" — condition false). Expected: not fetched.

### SOURCE: /state/master_state.json — FULL DOCUMENT
```json
{
  "story_title": "The Sankofa Gates",
  "genre": "African gate-clearing process fiction — contemporary Africa, in the Korean/Japanese gate-fiction tradition",
  "source_material": "Pólya, G. — How to Solve It: A New Aspect of Mathematical Method (2nd ed.) — books/How to Solve It_ A New Aspect  - Polya, G._7564 (1).epub",
  "chapter_count": 6,
  "arc_current": 1,
  "process_state_summary": {
    "op_what_is_missing": "owned",
    "op_identify_unknown": "owned",
    "op_separate_condition": {
      "touch": 1,
      "last_chapter": "004"
    },
    "op_look_at_unknown": {
      "touch": 1,
      "last_chapter": "005"
    }
  },
  "failure_modes_not_yet_shown": [],
  "failure_mode_lead_history": [
    { "chapter": "001", "lead": "the executor" },
    { "chapter": "002", "lead": "the executor" },
    { "chapter": "003", "lead": "the executor" },
    { "chapter": "004", "lead": "the system builder" },
    { "chapter": "005", "lead": "the information gatherer" }
  ],
  "population_index": [
    { "id": "char_001", "name": "Yejide Adeyemi", "status": "active", "last_seen": "006" },
    { "id": "char_002", "name": "Kwabena Asante", "status": "active", "last_seen": "003" },
    { "id": "char_002a", "name": "Ama Serwah", "status": "active", "last_seen": "002" },
    { "id": "char_003a", "name": "Kojo Acheampong", "status": "active", "last_seen": "003" },
    { "id": "char_003b", "name": "Akosua Osei", "status": "active", "last_seen": "003" },
    { "id": "char_004", "name": "Wanjiku Mwangi", "status": "active", "last_seen": "004" },
    { "id": "char_005", "name": "Fatou Ndiaye", "status": "active", "last_seen": "005" }
  ],
  "anchor_summary": "Last appeared ch. 006 (notebook_page); 6 total appearances.",
  "macro_mystery_evidence": [
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
    }
  ],
  "next_chapter_pointer": {
    "chapter": "007",
    "type": "arc_transition",
    "char_id": null,
    "operation_due": null,
    "touch_due": null,
    "name_due": false,
    "failure_mode_to_show": "none",
    "secondary_touches": [],
    "echo_touch": null,
    "anchor_appears": false
  }
}
```

### SOURCE: /state/process_state.json — FULL DOCUMENT
```json
{
  "context_enum": [
    "workplace", "professional", "family_domestic", "civic_institutional",
    "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"
  ],
  "operations": {
    "op_identify_unknown": {
      "name": "Identify unknown / data / condition",
      "difficulty_rating": 2,
      "arc_introduced": 1,
      "current_touch": 2,
      "name_attached": true,
      "name_at_touch": 2,
      "touch_schedule": { "1": 1, "2": 2 },
      "touch_target": 2,
      "prerequisite": [],
      "teaching_history": [
        { "chapter": "002", "char_id": "char_002", "touch": 1, "context": "workplace" },
        { "chapter": "003", "char_id": "char_002", "touch": 2, "context": "professional" }
      ],
      "failure_modes_shown": ["the executor", "the system builder", "the information gatherer"],
      "failure_modes_not_yet_shown": [],
      "contexts_demonstrated": ["workplace", "professional"],
      "contexts_not_yet_demonstrated": ["family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "workplace",
      "transferred_to_ordinary_life": true,
      "compressible_at_touch": 2
    },
    "op_what_is_missing": {
      "name": "What is missing (absence over presence)",
      "difficulty_rating": 2,
      "arc_introduced": 1,
      "current_touch": 2,
      "name_attached": true,
      "name_at_touch": 1,
      "touch_schedule": { "1": 1, "2": 2 },
      "touch_target": 2,
      "prerequisite": [],
      "teaching_history": [
        { "chapter": "001", "char_id": "char_001", "touch": 1, "context": "family_domestic" },
        { "chapter": "006", "char_id": "char_001", "touch": 2, "context": "workplace" }
      ],
      "failure_modes_shown": ["the executor", "the system builder", "the information gatherer"],
      "failure_modes_not_yet_shown": [],
      "contexts_demonstrated": ["family_domestic", "workplace"],
      "contexts_not_yet_demonstrated": ["professional", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "family_domestic",
      "transferred_to_ordinary_life": true,
      "compressible_at_touch": 2
    },
    "op_separate_condition": {
      "name": "Separate the parts of the condition",
      "difficulty_rating": 3,
      "arc_introduced": 1,
      "current_touch": 1,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 1, "2": 2 },
      "touch_target": 2,
      "prerequisite": ["op_identify_unknown"],
      "teaching_history": [
        { "chapter": "004", "char_id": "char_004", "touch": 1, "context": "workplace" }
      ],
      "failure_modes_shown": ["the executor", "the system builder", "the information gatherer"],
      "failure_modes_not_yet_shown": [],
      "contexts_demonstrated": ["workplace"],
      "contexts_not_yet_demonstrated": ["professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "workplace",
      "transferred_to_ordinary_life": true,
      "compressible_at_touch": 2
    },
    "op_use_all_data": {
      "name": "Did you use all the data?",
      "difficulty_rating": 3,
      "arc_introduced": 2,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 2, "2": 3 },
      "touch_target": 2,
      "prerequisite": ["op_separate_condition"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the hypothesis tester"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 2
    },
    "op_check_result": {
      "name": "Can you check the result?",
      "difficulty_rating": 3,
      "arc_introduced": 2,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 2, "2": 3 },
      "touch_target": 2,
      "prerequisite": ["op_identify_unknown"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the hypothesis tester"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 2
    },
    "op_derive_differently": {
      "name": "Can you derive the result differently?",
      "difficulty_rating": 3,
      "arc_introduced": 3,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 3, "2": 4 },
      "touch_target": 2,
      "prerequisite": ["op_looking_back"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the executor on complex condition", "the system builder on complex condition"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "creative",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 2
    },
    "op_look_at_unknown": {
      "name": "Look at the unknown",
      "difficulty_rating": 4,
      "arc_introduced": 1,
      "current_touch": 1,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 1, "2": 2, "3": 3 },
      "touch_target": 3,
      "prerequisite": ["op_identify_unknown"],
      "teaching_history": [
        { "chapter": "005", "char_id": "char_005", "touch": 1, "context": "civic_institutional" }
      ],
      "failure_modes_shown": ["the executor", "the system builder", "the information gatherer"],
      "failure_modes_not_yet_shown": [],
      "contexts_demonstrated": ["civic_institutional"],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "civic_institutional",
      "transferred_to_ordinary_life": true,
      "compressible_at_touch": 3
    },
    "op_related_problem": {
      "name": "Do you know a related problem?",
      "difficulty_rating": 4,
      "arc_introduced": 2,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 2, "2": 3, "3": 4 },
      "touch_target": 3,
      "prerequisite": ["op_look_at_unknown"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the hypothesis tester"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_use_related_problem": {
      "name": "Here is a problem related to yours and solved before",
      "difficulty_rating": 4,
      "arc_introduced": 2,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 2, "2": 3, "3": 4 },
      "touch_target": 3,
      "prerequisite": ["op_related_problem"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the hypothesis tester"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "teaching_mentoring",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_analogy": {
      "name": "Analogy — simpler analogous problem",
      "difficulty_rating": 4,
      "arc_introduced": 3,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 3, "2": 4, "3": 5 },
      "touch_target": 3,
      "prerequisite": ["op_related_problem"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the executor on complex condition", "the system builder on complex condition"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "teaching_mentoring",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_looking_back": {
      "name": "Looking back / transfer",
      "difficulty_rating": 4,
      "arc_introduced": 2,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 2, "2": 3, "3": 4 },
      "touch_target": 3,
      "prerequisite": ["op_check_result"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the hypothesis tester"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_decompose_condition": {
      "name": "Decompose condition / keep part drop part",
      "difficulty_rating": 5,
      "arc_introduced": 3,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 3, "2": 4, "3": 5 },
      "touch_target": 3,
      "prerequisite": ["op_separate_condition"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the executor on complex condition", "the system builder on complex condition"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "negotiation",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_auxiliary_elements": {
      "name": "Introduce auxiliary elements",
      "difficulty_rating": 5,
      "arc_introduced": 3,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 3, "2": 4, "3": 5 },
      "touch_target": 3,
      "prerequisite": ["op_use_related_problem"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the executor on complex condition", "the system builder on complex condition"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "family_domestic",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_use_result": {
      "name": "Can you use the result?",
      "difficulty_rating": 5,
      "arc_introduced": 4,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 4, "2": 5, "3": 6 },
      "touch_target": 3,
      "prerequisite": ["op_looking_back"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the force applier"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_auxiliary_problem": {
      "name": "Auxiliary problem",
      "difficulty_rating": 6,
      "arc_introduced": 4,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 4, "2": 5, "3": 6, "4": 7 },
      "touch_target": 4,
      "prerequisite": ["op_auxiliary_elements"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the force applier"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "project_management",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 4
    },
    "op_generalisation": {
      "name": "Generalisation",
      "difficulty_rating": 6,
      "arc_introduced": 5,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 5, "2": 6, "3": 7, "4": 8 },
      "touch_target": 4,
      "prerequisite": ["op_specialisation"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the information gatherer", "the perfectionist"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 4
    },
    "op_specialisation": {
      "name": "Specialisation",
      "difficulty_rating": 5,
      "arc_introduced": 4,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 4, "2": 5, "3": 6 },
      "touch_target": 3,
      "prerequisite": ["op_analogy"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the force applier"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "teaching_mentoring",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_working_backwards": {
      "name": "Working backwards / analysis",
      "difficulty_rating": 7,
      "arc_introduced": 5,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 5, "2": 6, "3": 7, "4": 8 },
      "touch_target": 4,
      "prerequisite": ["op_auxiliary_problem"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the information gatherer", "the perfectionist"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "civic_institutional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 4
    },
    "op_variation_restatement": {
      "name": "Variation of the problem / restatement",
      "difficulty_rating": 7,
      "arc_introduced": 6,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 6, "2": 7, "3": 8, "4": 9 },
      "touch_target": 4,
      "prerequisite": ["op_working_backwards"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the confident specialist", "the variation-tester"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "civic_institutional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 4
    },
    "op_inventors_paradox": {
      "name": "Inventor's Paradox",
      "difficulty_rating": 7,
      "arc_introduced": 5,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 5, "2": 6, "3": 7, "4": 8 },
      "touch_target": 4,
      "prerequisite": ["op_generalisation"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the information gatherer", "the perfectionist"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "civic_institutional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 4
    },
    "op_reductio": {
      "name": "Reductio ad absurdum",
      "difficulty_rating": 7,
      "arc_introduced": 5,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 5, "2": 6, "3": 7, "4": 8 },
      "touch_target": 4,
      "prerequisite": ["op_working_backwards"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the information gatherer", "the perfectionist"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "argument_debate",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 4
    },
    "op_heuristic_vs_proof": {
      "name": "Heuristic reasoning vs proof distinction",
      "difficulty_rating": 8,
      "arc_introduced": 7,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 2,
      "touch_schedule": { "1": 7, "2": 8, "3": 9 },
      "touch_target": 3,
      "prerequisite": ["op_variation_restatement"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the heuristic-only solver", "the guild verifier"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "professional",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_subconscious_work": {
      "name": "Subconscious work",
      "difficulty_rating": 8,
      "arc_introduced": 7,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 7, "2": 8, "3": 9 },
      "touch_target": 3,
      "prerequisite": ["op_variation_restatement"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the heuristic-only solver", "the guild verifier"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "creative",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    },
    "op_auxiliary_chains": {
      "name": "Auxiliary problem chains",
      "difficulty_rating": 8,
      "arc_introduced": 8,
      "current_touch": 0,
      "name_attached": false,
      "name_at_touch": 1,
      "touch_schedule": { "1": 8, "2": 9 },
      "touch_target": 2,
      "prerequisite": ["op_auxiliary_problem", "op_working_backwards"],
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": ["the single-step auxiliary solver", "the planner without synthesis"],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": ["workplace", "professional", "family_domestic", "civic_institutional", "teaching_mentoring", "negotiation", "project_management", "creative", "argument_debate"],
      "preferred_context": "project_management",
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 2
    }
  }
}
```

### SOURCE: /core/concept_curriculum.md — Section 5 Arc Breakdown

**Closing arc (arc_current = 1):**

| Arc | Gate Grade | Hard Operation | Easy Pairing | New Wrong Approach Type | Narrative Engine |
|---|---|---|---|---|---|
| 1 | 1-2 | Look at the unknown / what is missing (4) | Identify unknown / data / condition (2). Separate parts of condition (3). | Executor. System builder. Information gatherer. | First gates open. Society scrambling. Most survive Grade 1 by luck. Grade 2 begins killing those who got lucky on Grade 1. |

**Opening arc (arc_current + 1 = 2):**

| Arc | Gate Grade | Hard Operation | Easy Pairing | New Wrong Approach Type | Narrative Engine |
|---|---|---|---|---|---|
| 2 | 2-3 | Do you know a related problem? / Here is a problem related to yours (4) | Did you use all the data? (3). Can you check the result? (3). Looking back / transfer (4). | Confident specialist. Hypothesis tester. | Guild methods failing on Grade 2-3. Characters with wide ordinary-life experience solving gates specialists cannot. |
