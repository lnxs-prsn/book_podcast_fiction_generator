# STORY GENERATION SYSTEM — BUILD SPECS

> **HISTORICAL (2026-07-03):** original design document for what became
> `fiction_loop/`. The built system has diverged in places (init is now
> `fiction_loop/tools/init_state.py`, not a manual human sequence; scheduling is
> map-deficit driven; see `fiction_loop/specs/` + `fiction_loop/human_decision.md`
> for current truth). Do not implement from this file.
## For Claude Code in VS Code

---

## OVERVIEW

A genre-agnostic agentic story generation system. The system manages state, continuity, and context window automatically. A human provides the core documents once. The loop runs autonomously after that.

The system separates three concerns:
- **State management** — JSON cards track everything that happened
- **Prompt assembly** — markdown files assembled fresh each chapter from fetched card data
- **Prose generation** — subagent receives clean assembled prompt, writes only, returns chapter

The system works for any story where:
- A process or concept is being taught through fiction
- Multiple focal characters appear across many chapters
- Continuity must be maintained across sessions potentially months apart

---

## FILE STRUCTURE

```
/[story-root]/
  /core/
    world_bible.md
    style_contract.md
    correspondence_map.md
    concept_curriculum.md
    living_document.md
  /agents/
    orchestrator.md
    fetcher.md
    assembler.md
    consistency_checker.md
    updater.md
  /state/
    master_state.json
    process_state.json
    mystery_anchor.json
  /cards/
    /characters/
      [char_id].json
    /locations/
      [location_id].json
    /events/
      [event_id].json
    /concept/
      [operation_id].json
  /chapters/
    chapter_[NNN].md
  /arcs/
    arc_[N]_summary.md
  /prompts/
    assembled_prompt.md
    update_brief.json
```

---

## AGENT SPECS

### AGENT 1 — ORCHESTRATOR
**File:** `/agents/orchestrator.md`
**Role:** Entry point. Reads master state. Decides what comes next. Coordinates all other agents. Never writes prose.

**Trigger:** User types `generate next chapter` or `generate chapter [type]` in Claude Code.

**Steps the Orchestrator follows:**

```
1. Read /state/master_state.json
2. Read next_chapter_pointer field
3. Determine chapter type:
   - new_focal_character
   - return_to_character:[char_id]
   - anchor_interlude
   - arc_transition
4. Call Fetcher with chapter type and required card IDs
5. Receive fetched fields from Fetcher
6. Call Consistency Checker with assembled fields + style_contract.md
7. Receive consistency report
8. If violations flagged: resolve or log and proceed
9. Call Assembler with fetched fields + chapter type + consistency report
10. Receive assembled_prompt.md from Assembler
11. Delegate to Writer subagent with assembled_prompt.md
12. Receive chapter prose from Writer subagent
13. Save chapter to /chapters/chapter_[NNN].md
14. Generate update_brief.json from chapter content
15. Call Updater with update_brief.json
16. Confirm all cards updated
17. Set next_chapter_pointer in master_state.json
18. Report completion to user
```

**Decision logic for next_chapter_pointer:**

```
IF process_state has operation at touch_0 AND arc requires it:
  → new_focal_character chapter introducing that operation
IF operation at touch_1 AND 3+ chapters since last touch:
  → return or new character showing operation in new context
IF mystery_anchor last appeared more than 5 chapters ago:
  → anchor_interlude
IF all arc operations at touch_2+:
  → arc_transition
```

**Output:** assembled_prompt.md + update_brief.json skeleton

---

### AGENT 2 — FETCHER
**File:** `/agents/fetcher.md`
**Role:** Reads the correct cards from /cards based on chapter type. Returns only the fields needed for this chapter. Never reads entire card files into context — queries specific fields only.

**Called by:** Orchestrator

**Input:** chapter_type, list of required card IDs, list of required fields per card

**Fetch logic by chapter type:**

```
new_focal_character:
  - /state/master_state.json → process_state_summary, macro_mystery_evidence, next_chapter_pointer
  - /state/process_state.json → operation_due fields only
  - /core/concept_curriculum.md → current arc section only
  - /cards/locations/[location_id].json → if location specified
  - /state/mystery_anchor.json → observable_log last 3 entries only

return_to_character:[char_id]:
  - /state/master_state.json → process_state_summary, macro_mystery_evidence
  - /cards/characters/[char_id].json → full card
  - /cards/locations/[location_id].json → their city card
  - /state/process_state.json → operation_due fields only
  - /state/mystery_anchor.json → observable_log last 3 entries only

anchor_interlude:
  - /state/master_state.json → full
  - /state/mystery_anchor.json → observable_log full
  - /state/process_state.json → summary only
  - /cards/locations/[relevant_ids].json → locations anchor has visited

arc_transition:
  - /arcs/arc_[N]_summary.md → previous arc
  - /state/master_state.json → full
  - /state/process_state.json → full
  - /core/concept_curriculum.md → next arc section
```

**Output:** A structured markdown block of fetched fields, clearly labelled by source. Passed to Assembler.

**Critical rule:** Fetcher never reads /state/mystery_anchor.json hidden_coherence layer. That field is never fetched for any chapter type under any circumstances.

---

### AGENT 3 — ASSEMBLER
**File:** `/agents/assembler.md`
**Role:** Takes fetched fields and arranges them into a clean prose generation prompt. Writes assembled_prompt.md. The Writer subagent receives only this file — nothing else.

**Called by:** Orchestrator, after Fetcher and Consistency Checker have run.

**Input:** Fetched fields block + chapter_type + consistency_checker flags

**assembled_prompt.md structure:**

```markdown
# CHAPTER [NNN] — GENERATION PROMPT

## VOICE RULES
[Paste style_contract.md Rule 1, Rule 2, Rule 3 verbatim]
[Paste the never list verbatim]

## WORLD RULES
[Paste the 6 world rules from world_bible.md verbatim]

## THIS CHAPTER

**Chapter type:** [new_focal_character / return_to_character / anchor_interlude / arc_transition]
**Chapter number:** [NNN]

**Focal character:**
[If new: name, occupation, city, situation — generated fresh]
[If returning: paste relevant fields from character card]

**Gate this chapter:**
[Grade, problem structure: unknown / data / condition]
[Wrong approach to show first]
[Correct approach that closes gate]

**Operation being taught:**
[Operation name]
[Touch number]
[Delivery channel: narrator label / character action / observer note]
[Physical anchor for this operation]

**Operations to use naturally (no re-explanation):**
[List of owned operations with their physical anchors]

**Ordinary life echo:**
[The real-world problem that mirrors the gate structure]
[Must appear in same chapter]

**Anchor character appearance:**
[Yes/No]
[If yes: what they observe, described observationally only]
[Observable log entries they connect to — never the hidden layer]

**Failure mode to demonstrate:**
[Specific failure mode from process_state.json failure_modes_not_yet_shown]
[Must appear before correct approach]

**Macro mystery:**
[One piece of evidence to plant if applicable]
[How it appears — never explained, just present]

**Emotional beat:**
[Character's internal arc this chapter]

**Foreshadowing:**
[Optional: what to seed]

## CONSTRAINTS
- Do not name the operation before the character has suffered its absence
- Do not close the gap between observation and meaning
- The anchor character's hidden coherence is never surfaced
- Failure before success always
- Ordinary life echo must feel inevitable not surprising
- Chapter ends when the gate closes and the ordinary life echo lands
- Length: 2000-3000 words
```

**Output:** /prompts/assembled_prompt.md

---

### AGENT 4 — CONSISTENCY CHECKER
**File:** `/agents/consistency_checker.md`
**Role:** Reads the assembled fields before prose is written. Checks for violations against the style contract, concept curriculum, and process state. Returns a report. Does not block generation — flags for Orchestrator to resolve.

**Called by:** Orchestrator, before Assembler runs.

**Checks to run:**

```
VOICE CHECKS
□ Is the operation being named before the cost has been felt?
□ Is more than one hard operation being introduced this chapter?
□ Is a previously owned operation being re-explained?

CONTINUITY CHECKS  
□ Has this failure mode already been shown in this context type?
  → Query process_state.json failure_modes_shown
□ Has this character already encountered this operation?
  → Query character card gate_history
□ Has the anchor character appeared in the last 5 chapters?
  → Query mystery_anchor.json observable_log
□ Is the ordinary life echo in a context already used for this operation?
  → Query process_state.json contexts_demonstrated

CURRICULUM CHECKS
□ Is the operation due at the correct touch number?
  → Query process_state.json current_touch
□ Is the gate grade consistent with the current arc?
  → Query master_state.json arc_current
□ Is a harder operation being introduced before the prerequisite is at touch_2?
  → Query process_state.json for prerequisite operation touch

ANCHOR CHECKS
□ Is any hidden_coherence content present in the fetched fields?
  → If yes: BLOCK and alert Orchestrator immediately
□ Is the anchor character being given interiority or explanation?
  → Flag as style violation
```

**Output:** Consistency report with PASS / FLAG / BLOCK per check. Passed to Orchestrator.

---

### AGENT 5 — UPDATER
**File:** `/agents/updater.md`
**Role:** Receives update_brief.json from Orchestrator after chapter is written. Updates all relevant cards. Updates master_state.json. Sets next_chapter_pointer. Never reads the full chapter prose — works from the update brief only.

**Called by:** Orchestrator, after Writer subagent returns chapter.

**Input:** /prompts/update_brief.json + list of affected card IDs

**update_brief.json schema:**

```json
{
  "chapter": "NNN",
  "chapter_type": "new_focal_character",
  "focal_character": {
    "id": "char_XXX",
    "is_new": true,
    "name": "[ ]",
    "occupation": "[ ]",
    "city": "[ ]",
    "gate_visited": {
      "gate_id": "G-XXX",
      "grade": 1,
      "operation_encountered": "[ ]",
      "approach_taken": "[ ]",
      "understood": false,
      "looked_back": false,
      "transferred_to_life": false
    },
    "comprehension_changes": {},
    "ordinary_life_state": "[ ]"
  },
  "process_updates": {
    "operation": "[ ]",
    "new_touch": 1,
    "failure_mode_shown": "[ ]",
    "context_demonstrated": "[ ]",
    "transferred": false
  },
  "location_updates": {
    "location_id": "[ ]",
    "new_chapter_added": "NNN",
    "new_texture": []
  },
  "anchor_update": {
    "appeared": false,
    "observation": "[ ]",
    "location": "[ ]"
  },
  "macro_mystery_update": {
    "evidence_planted": false,
    "evidence": "[ ]"
  },
  "next_chapter_pointer": {
    "chapter": "NNN+1",
    "type": "[ ]",
    "operation_due": "[ ]",
    "touch_due": 0,
    "failure_mode_to_show": "[ ]",
    "anchor_appears": false
  }
}
```

**Update sequence:**

```
1. If is_new character: create /cards/characters/[char_id].json
2. If returning character: update gate_history array, update comprehension_state
3. Update /cards/concept/[operation_id].json:
   - Increment touch count
   - Add entry to teaching_history
   - Add to failure_modes_shown
   - Add to contexts_demonstrated
   - If touch reaches 3: flag for compression in master_state
4. Update /cards/locations/[location_id].json:
   - Add chapter to chapters_set_here
   - Add any new texture entries
5. If anchor appeared: append to /state/mystery_anchor.json observable_log
6. If macro mystery evidence: append to master_state.json macro_mystery_evidence
7. Update /state/master_state.json:
   - Increment chapter_count
   - Update process_state_summary
   - Update population_index entry
   - If operation at touch_3: compress entry to single word
   - Write next_chapter_pointer
8. Report all updates complete to Orchestrator
```

---

## JSON SCHEMAS

### /state/master_state.json
```json
{
  "story_title": "[ ]",
  "genre": "[ ]",
  "source_material": "[ ]",
  "chapter_count": 0,
  "arc_current": 1,
  "process_state_summary": {},
  "failure_modes_not_yet_shown": [],
  "population_index": [],
  "anchor_summary": "[ ]",
  "macro_mystery_evidence": [],
  "next_chapter_pointer": {
    "chapter": 1,
    "type": "new_focal_character",
    "operation_due": "[ ]",
    "touch_due": 1,
    "failure_mode_to_show": "[ ]",
    "anchor_appears": false
  }
}
```

### /state/process_state.json
```json
{
  "operations": {
    "[operation_id]": {
      "name": "[ ]",
      "difficulty_rating": 0,
      "current_touch": 0,
      "teaching_history": [],
      "failure_modes_shown": [],
      "failure_modes_not_yet_shown": [],
      "contexts_demonstrated": [],
      "contexts_not_yet_demonstrated": [],
      "transferred_to_ordinary_life": false,
      "compressible_at_touch": 3
    }
  }
}
```

### /state/mystery_anchor.json
```json
{
  "observable_log": [],
  "reader_can_suspect": [],
  "hidden_coherence": {
    "access": "PLANNING_ONLY_NEVER_IN_CHAPTER_PROMPT",
    "true_identity": "[ ]",
    "what_they_know": "[ ]",
    "what_they_are_investigating": "[ ]",
    "answer_pointing_toward": "[ ]"
  }
}
```

### /cards/characters/[char_id].json
```json
{
  "id": "[ ]",
  "name": "[ ]",
  "age": 0,
  "occupation": "[ ]",
  "location_id": "[ ]",
  "first_appeared": 0,
  "gate_history": [],
  "comprehension_state": {},
  "still_gets_wrong": [],
  "ordinary_life_state": "[ ]",
  "ordinary_life_transfers": [],
  "anchor_observed": false,
  "last_seen": 0,
  "next_planned_appearance": null
}
```

### /cards/locations/[location_id].json
```json
{
  "id": "[ ]",
  "name": "[ ]",
  "first_appeared": 0,
  "institutional_response": {
    "primary_body": "[ ]",
    "approach": "[ ]",
    "failure_mode": "[ ]"
  },
  "ordinary_life_texture": [],
  "macro_mystery_evidence_here": [],
  "characters_based_here": [],
  "chapters_set_here": []
}
```

### /cards/events/[event_id].json
```json
{
  "id": "[ ]",
  "type": "gate",
  "grade": 0,
  "location_id": "[ ]",
  "chapter_opened": 0,
  "chapter_closed": 0,
  "status": "open",
  "problem_structure": {
    "unknown": "[ ]",
    "data": [],
    "condition": "[ ]"
  },
  "wrong_approaches_demonstrated": [],
  "correct_approach": "[ ]",
  "characters_entered": [],
  "operation_taught": "[ ]",
  "failure_mode_shown": "[ ]",
  "anchor_present": false,
  "notes": "[ ]"
}
```

### /cards/concept/[operation_id].json
```json
{
  "id": "[ ]",
  "name": "[ ]",
  "source_text": "[ ]",
  "difficulty_rating": 0,
  "current_touch": 0,
  "teaching_history": [],
  "failure_modes_shown": [],
  "failure_modes_not_yet_shown": [],
  "contexts_demonstrated": [],
  "contexts_not_yet_demonstrated": [],
  "transferred_to_ordinary_life": false,
  "physical_anchor": "[ ]",
  "compressible_at_touch": 3
}
```

---

## INITIALIZATION SEQUENCE

When a new story is started:

```
1. Human provides /core/ documents:
   - world_bible.md
   - style_contract.md
   - correspondence_map.md
   - concept_curriculum.md
   - living_document.md

2. Human fills master_state.json:
   - story_title
   - genre
   - source_material
   - Sets chapter_count to 0
   - Sets arc_current to 1
   - Sets first next_chapter_pointer manually

3. Human fills process_state.json:
   - All operations from concept_curriculum.md
   - All at touch_0 initially
   - All failure_modes_not_yet_shown populated
   - All contexts_not_yet_demonstrated populated

4. Human fills mystery_anchor.json:
   - hidden_coherence layer only
   - observable_log starts empty

5. System is ready. Human types: generate next chapter
```

---

## COMPRESSION RULES

When an operation reaches touch_3 in process_state.json:

```
1. Updater flags the operation in master_state.json process_state_summary
2. Entry in master_state.json compresses from full object to single string:
   "identify_unknown": "touch_3_owned"
3. Full detail remains in /cards/concept/[operation_id].json
4. Fetcher still queries concept card when operation appears in a chapter
5. Master state entry never expands again unless operation reaches touch_4
```

When a character has not appeared in 20+ chapters:

```
1. Population index entry compresses to:
   {"id": "char_XXX", "name": "[ ]", "status": "dormant", "last_seen": NNN}
2. Full character card remains in /cards/characters/
3. Recalled to active when next_chapter_pointer targets them
```

---

## CRITICAL RULES FOR ALL AGENTS

These rules apply to every agent without exception:

```
1. mystery_anchor.json hidden_coherence is NEVER passed to any chapter prompt
2. An operation is NEVER named in prose before the character has suffered its absence
3. The Consistency Checker runs BEFORE the Assembler every time
4. The Updater works from update_brief.json only — never reads full chapter prose
5. The Fetcher returns fields, not full card files
6. The Writer subagent receives assembled_prompt.md only — no other files
7. No agent modifies /core/ documents
8. Arc summary is written to /arcs/ only after Orchestrator confirms arc is complete
9. Closed event cards move to /cards/events/archive/ immediately after closing
10. The next_chapter_pointer is always set before the session ends
```

---

## USER COMMANDS

```
generate next chapter
  → Full loop. Orchestrator reads pointer, runs all agents, writes chapter, updates state.

generate chapter [type]
  → Override pointer. Types: new_character / return:[char_id] / anchor / arc_transition

show master state
  → Print master_state.json formatted

show character [char_id or name]
  → Print character card formatted

show process state
  → Print process_state.json formatted, highlight what is due next

show anchor log
  → Print mystery_anchor.json observable_log only. Never hidden_coherence.

compress [operation_id]
  → Manually trigger compression for an operation

status
  → Print: current chapter count, current arc, next chapter pointer, 
     operations due, last anchor appearance
```

---

## AGNOSTIC ADAPTATION NOTES

To use this system with any story:

```
/core/ documents change completely — provide your own
/state/process_state.json operations change — populate from your source material
/state/mystery_anchor.json hidden_coherence changes — fill with your anchor character's truth
Event card type field can be changed from "gate" to any event type your story uses
Location cards work for any setting — city, spaceship, village, institution
The system has no hardcoded genre assumptions outside the /core/ documents
```

The only constants across all stories:
- The five agent roles and their sequence
- The JSON schemas
- The compression rules
- The critical rules list
- The hidden coherence protection on the anchor character