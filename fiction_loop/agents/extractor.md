# AGENT 7 — EXTRACTOR

**Role:** Reads the finished chapter and the assembled prompt. Fills `update_brief.json` completely from what the chapter actually shows. Computes `next_chapter_pointer` using the decision logic below. Never summarises or quotes prose back to the Orchestrator.

**Called by:** Orchestrator (step 11), after `refresh_living_doc.py` has run and the chapter has been saved to `fiction_loop/chapters/`.

---

## INPUT

Read these files before filling any field (curriculum is NOT among them — the
schedule lives in each card's touch_schedule inside process_state.json; reading the
6k-word curriculum made this step slow enough to hit harness timeouts):

```
fiction_loop/chapters/chapter_[NNN].md       — what actually happened in the prose
fiction_loop/prompts/assembled_prompt.md     — what was planned (operation, character, location, gate)
fiction_loop/state/master_state.json         — chapter_count, arc_current, population_index
fiction_loop/state/process_state.json        — touch counts, touch_schedule, pools (the ENTIRE scheduling input)
fiction_loop/state/mystery_anchor.json       — observable_log (for anchor condition and appearance text)
fiction_loop/core/living_document.md         — "MYSTERY PERSON THREAD" section only (reader_can_suspect diff)
fiction_loop/core/chapter_type_contract.md   — which sections below apply to this chapter_type
```

Do not read hidden_coherence from mystery_anchor.json under any circumstances.

---

## FILL PROCEDURE

Work section by section through `fiction_loop/prompts/update_brief.json`.

For every field: derive from the chapter prose and the assembled prompt.
If a field cannot be determined from either source: write `"UNDETERMINED — [reason]"`.
Do not leave `[ ]` in any field — that is the template placeholder only.

---

### SECTION: top-level fields

```
chapter      → NNN (zero-padded, from assembled_prompt chapter number)
chapter_type → the chapter_type from the assembled prompt
```

---

### SECTION: focal_character

```
IF chapter_type IN [anchor_interlude, arc_transition]:
  SKIP this entire section — no focal character exists for this chapter type
  (see chapter_type_contract.md). Write focal_character: null in update_brief.json.

id
  IF is_new = true:
    → "char_[NNN]" where NNN matches the chapter number (e.g. char_001 for chapter 001)
  IF is_new = false:
    → char_id from the assembled prompt's focal character section

is_new
  → true if the character does not appear in master_state.json population_index
  → false if they do

name, occupation, city
  → Read from the chapter prose for new characters
  → Read from the assembled prompt for returning characters (confirm against prose)

age
  → Only if the prose states or clearly implies it; otherwise null — never invent
    and never write the schema placeholder 0

gate_visited.gate_id
  → "G-[NNN]" where NNN matches the chapter number (e.g. G-001 for chapter 001)

gate_visited.grade
  → From the assembled prompt's "Gate this chapter" section

gate_visited.operation_encountered
  → The operation ID from the assembled prompt's "Operation being taught" section

gate_visited.approach_taken
  → The wrong approach the focal character used first, as shown in the prose
  → Use the wrong approach type name from concept_curriculum.md
    (e.g. "the executor", "the system builder", "the information gatherer")
  → "none — applied correctly" is a VALID value for returning characters who
    apply the operation without a wrong approach (the expected shape of a
    touch-2+ return: newcomers in other_entrants carry the failure modes).
    Do not write UNDETERMINED for this case.
  → CANONICAL NAMES (complete closed list — use these strings EXACTLY, for this
    field, other_entrants.approach_taken, and failure_modes_shown_this_chapter;
    never invent a variant): "the executor", "the system builder",
    "the information gatherer", "the hypothesis tester", "the confident
    specialist", "the force applier", "the executor on complex condition",
    "the system builder on complex condition", "the perfectionist",
    "the variation-tester", "the single-step auxiliary solver", "the planner
    without synthesis", "the heuristic-only solver", "the guild verifier".
    If the prose shows an approach genuinely outside this list, write
    "UNDETERMINED — unlisted approach: [brief description]" — do not coin a name.

gate_visited.understood
  → true if the character found the right question and the gate closed in this chapter
  → false if the gate remained open (unusual — flag with note)

gate_visited.looked_back
  → true if the ordinary life echo scene is present in this chapter
  → false if not (ordinary life echo may appear in the next chapter)

gate_visited.transferred_to_life
  → true if the ordinary life echo shows the character applying the operation outside the gate
  → false if the echo is present but the connection is not yet made

comprehension_changes
  → Map of operation_id to new comprehension level for this character.
  → Format: { "[operation_id]": "encountered" | "understood" | "owned" }
  → "encountered": character met the operation this chapter, experienced the cost, has not yet named it
  → "understood": character reached the right question and can name what they did (touch 1N or 2)
  → "owned": character applies it without prompting in an ordinary life context (touch 3+)
  → Only include operations whose level changed in this chapter.

ordinary_life_state
  → One sentence describing the character's ordinary life situation as shown in the echo scene
  → If no echo scene: "No ordinary life scene this chapter"

life_progression_shown
  → null if is_new = true (no prior state to progress from)
  → true if the prose shows visible forward movement from the character's previous
    ordinary_life_state (promotion, grades, resolved conflict — per the character card)
  → false if the character returned but no progression was visible — this is a
    quality failure to surface, not to hide: also list it under UNDETERMINED
```

---

### SECTION: other_entrants

```
Every OTHER solver present in the gate scene gets an entry (the failed solvers of
the productive-failure structure, experienced strangers, etc. — not
crowd/bystanders), whether the prose names them or leaves them unnamed.

For each NAMED solver:
  { "id": existing char_id if they are in population_index, else "char_[NNN][a/b/c]",
    "name": ..., "is_new": ..., "approach_taken": wrong approach type shown,
    "operations_applied": [operation_ids they visibly used, for secondary touch
    verification] }

For each UNNAMED solver:
  { "id": null, "name": null, "is_new": true/false,
    "approach_taken": wrong approach type shown,
    "operations_applied": [operation_ids they visibly used, for secondary touch
    verification] }
For an unnamed solver, set is_new = true when the prose presents them as a first
appearance and supplies no continuity marker to any prior chapter; otherwise set
is_new = false.

WRONG — chapter 006's unnamed information-gatherer is omitted:
  "other_entrants": []
RIGHT — the same unnamed solver reaches the structural gate:
  "other_entrants": [
    { "id": null, "name": null, "is_new": true,
      "approach_taken": "the information gatherer", "operations_applied": [] }
  ]

LAW 4 producer/consumer registration: Extractor produces
other_entrants[].is_new; structural_gate.py consumes it to count F15 newcomers;
Updater consumes other_entrants and skips name: null entries so they remain
gate-only signals rather than permanent character records.
```

---

### SECTION: secondary_touch_updates

```
For each entry in the assembled prompt's "Secondary touches" and "Echo touch" plans:
  → VERIFY against the prose: did the named carrier actually apply the operation,
    visibly, in the chapter?
  → { "operation": operation_id, "carrier": char_id or "experienced_stranger",
      "touch": N, "verified": true/false, "context": enum value or "in_gate" }
  → verified: false entries are returned to the deficit pool by the Updater —
    NEVER mark verified on inference; the operation must be visible in the prose.
Empty list if the assembled prompt scheduled none.
```

---

### SECTION: names_used_this_chapter

```
Every personal name the chapter's prose introduces for the first time
(focal character, other entrants, named bystanders).
→ List of strings. The Updater appends these to core/character_naming.md's ledger.
```

---

### SECTION: gate_details

```
IF chapter_type IN [anchor_interlude, arc_transition]:
  SKIP this entire section — no gate opens this chapter (see chapter_type_contract.md).
  Write gate_details: null in update_brief.json.

problem_structure.unknown
  → One phrase describing what the gate's unknown was, as shown in the "gate opens" prose

problem_structure.data
  → A short list of phrases describing the key data given, as shown in the prose

problem_structure.condition
  → One phrase describing the condition/constraint, as shown in the prose

correct_approach
  → One or two sentences describing the right question and approach that actually
    closed the gate, as shown in the "right question" / "gate closes" prose
  → Summarise the approach — do not copy prose verbatim
```

---

### SECTION: process_updates

```
IF chapter_type IN [anchor_interlude, arc_transition]:
  SKIP this entire section — no operation is taught this chapter
  (see chapter_type_contract.md). Write process_updates: null in update_brief.json.

operation
  → The operation ID from the assembled prompt

new_touch
  → process_state.operations.[operation_id].current_touch + 1

failure_modes_shown_this_chapter
  → ALL wrong approach types demonstrated in the chapter prose for this operation,
    in the order shown (a chapter typically shows 2-3 per concept_curriculum.md's
    Chapter-Level Structure — do not record only the first one)
  → Use the exact name as it appears in process_state (e.g. "the executor")
  → List, not a single value

lead_failure_mode
  → REQUIRED for every gate chapter; never omit it.
  → Set it to the FIRST wrong approach dramatized in the prose, using the exact
    name from process_state.
  → Producer: Extractor. Consumers: Updater STEP 7 (appends it to
    failure_mode_lead_history) and Extractor's failure_mode_to_show selection
    (least-recently-led rotation).
  → "none" only for anchor_interlude / arc_transition (whose process_updates is
    null under the section guard above).

name_attached_this_chapter
  → true if the prose attaches the operation's name (the one-sentence narrator label
    per style_contract.md §3/§4) this chapter
  → false otherwise
  → Compare against the pointer's name_due: if name was due but not attached, list
    under UNDETERMINED

context_demonstrated
  → The enum value from process_state.json context_enum that best matches the
    ordinary life context where the operation was demonstrated
    (e.g. "workplace", "family_domestic" — never free text; the enum is the
    canonical pick-list per owner decision D4)
  → "none" if no ordinary life echo in this chapter

transferred
  → true if gate_visited.transferred_to_life = true
  → false otherwise
```

---

### SECTION: location_updates

```
IF chapter_type IN [anchor_interlude, arc_transition]:
  SKIP this entire section — no new/returning focal-character location this chapter
  (see chapter_type_contract.md). Write location_updates: null in update_brief.json.

location_id
  → Check if fiction_loop/cards/locations/loc_[city_slug].json exists
  → If yes: use that ID
  → If no: "loc_[city_slug]" where city_slug is the city name, lowercase, underscores
    e.g. "loc_lagos", "loc_nairobi", "loc_accra", "loc_dakar"

new_chapter_added
  → NNN

new_texture
  → List of new ordinary life observations from the chapter's echo scene
  → Each entry: one sentence describing something concrete about daily life in this location
  → Pull only new observations not already in the location card (if it exists)
  → Empty list if no new texture or no echo scene this chapter
```

---

### SECTION: anchor_update

```
appeared
  → true if the mystery anchor character appears anywhere in the chapter prose,
    in ANY manifestation (seen directly / already gone, traces left / mentioned by
    a bystander / a notebook page found)
  → Note: per owner decision D3 she appears in EVERY gate chapter — appeared: false
    on a gate chapter is a defect to surface, not normal
  → false if not

manifestation
  → Which form her presence took: "seen" | "traces" | "bystander_mention" |
    "notebook_page" | "none"
  → The Updater records this so the Assembler can avoid repeating the same form
    in consecutive chapters (anti-formula)

observation
  → If appeared = true:
    The exact notebook entry text from the prose (what the anchor observed)
    Pull verbatim from the chapter — this is what goes into observable_log
  → If appeared = false: "none"

location
  → If appeared = true: the location_id where the anchor appeared
  → If appeared = false: "none"

reader_can_suspect_update
  → Compare living_document.md's "Reader can suspect" line (MYSTERY PERSON THREAD
    section) to mystery_anchor.json's current reader_can_suspect array
  → If the living document describes a suspicion not already recorded there:
    one sentence capturing the new suspicion
  → "none" if unchanged from what's already recorded
```

---

### SECTION: macro_mystery_update

```
evidence_planted
  → true if the chapter contains a macro mystery observation
    (something that raises the question of why gates exist, or shows a pattern)
  → false if not — most chapters will be false

evidence
  → If evidence_planted = true:
    One sentence describing the evidence as the reader can observe it
    Write observationally — do not state what it means
  → If evidence_planted = false: "none"
```

---

### SECTION: next_chapter_pointer

Compute using the DECISION LOGIC section below.

```
chapter      → NNN + 1 (next chapter number, zero-padded)
type         → from decision logic
char_id      → from decision logic (non-null iff type = return_to_character, else null)
operation_due → from decision logic (null for anchor_interlude)
touch_due    → from decision logic
name_due     → true iff touch_due == operations.[operation_due].name_at_touch
               AND name_attached is still false
failure_mode_to_show
  → From process_state.operations.[operation_due].failure_modes_not_yet_shown,
    picking the entry LEAST RECENTLY LED: the type whose latest chapter in
    master_state.json failure_mode_lead_history is OLDEST — and a type absent
    from that history entirely ranks first of all. Tiebreak: least recently
    SHOWN across all operations (scan teaching_history/failure_modes_shown by
    chapter). Never simply [0].
  → WHY LED, NOT SHOWN (owner ruling 2026-07-04): in arcs where the scene quota
    equals the pool size (arc 1: 3 of 3), every chapter shows every type — 
    shown-recency is then a permanent three-way tie and the lead can silently
    repeat (executor led ch1–3; the system builder nearly led ch4–5 back to
    back). The LEAD is what the reader experiences as the chapter's featured
    failure — the anchor observes it, the notebook entry names it — so rotation
    must track leads (owner rule D4, anti-formula). A useful side effect: a
    newly introduced arc type has never led, so it is auto-featured on arrival.
  → "none" if operation_due is null or list is empty
secondary_touches
  → from decision logic (up to 2; empty list for anchor_interlude/arc_transition)
echo_touch
  → from decision logic (one entry or null)
anchor_appears
  → true for EVERY gate-bearing chapter type (new_focal_character,
    return_to_character) and for anchor_interlude — per owner decision D3
    (she appears at every gate; her omnipresence is a planted clue)
  → false only for arc_transition chapters with no gate scene
```

---

## ID CONVENTIONS

```
Character ID   → char_[NNN]   where NNN = chapter number of first appearance (zero-padded)
Gate ID        → G-[NNN]      where NNN = chapter number the gate appears in (zero-padded)
Location ID    → loc_[slug]   where slug = city name, lowercase, spaces to underscores
                               Reuse existing loc_ ID if the location card already exists
```

---

## DECISION LOGIC — next_chapter_pointer

Owner decisions D1/D3/D9 (see `../human_decision.md`): map-driven scheduling with a
chronological gate, co-hosted touches, and anchor omnipresence.

Read `process_state.json` and `master_state.json`. Each operation card carries its own
schedule: `touch_schedule` (touch → arc), `touch_target`, `name_at_touch`,
`prerequisite`, `arc_introduced`.

**Definitions:**
```
deficit(X)   = number of touches in X.touch_schedule whose arc <= arc_current
               and whose touch number > X.current_touch
eligible(X)  = X.prerequisite is null
               OR every operation in X.prerequisite has current_touch >= 2
               (the chronological gate: step N+1 waits until step N is clear —
                experienced, named, applied once)
spacing(X)   = master_state.chapter_count - X.teaching_history[-1].chapter
               (infinity if teaching_history is empty)
cleared(X)   = X.current_touch >= 2
```

**STEP A.0 — arc-transition precedence:**
```
IF every ELIGIBLE operation has deficit = 0:
  → go directly to STEP D (arc transition).

Gate-blocked operations do not hold the arc open; their deficit carries per
STEP D.
```

Precedence fixed 2026-07 (T-005) after the ch5/ch6 divergence.

**STEP A — formal operation_due (the chapter's one taught operation):**
```
1. Candidates: all eligible operations with deficit > 0.
2. Exclude candidates with spacing < 3 (unless no candidate has spacing >= 3).
3. Pick the candidate with the largest deficit;
   tie-break: lowest current_touch; then registry order (operation_registry.md).
4. touch_due = current_touch + 1.
```

**STEP B — chapter type and char_id (owner rule: the process is the protagonist):**
```
IF touch_due == 1:
  → type: new_focal_character, char_id: null
ELSE (touch 2+ due):
  FOCAL RETURN IS THE EXCEPTION, NOT THE DEFAULT. A recurring focal character
  becomes a main-character trope that competes with the process itself.
  → PREFER: keep type new_focal_character (fresh focal learning an eligible
    touch-1 operation as the formal teaching) and satisfy the due touch 2+ as a
    SECONDARY TOUCH carried by the returning character in a SIDE role (STEP C) —
    present, recognizable, demonstrating the operation, never centered.
  → Choose type return_to_character (focal) ONLY when one of:
      - name_due is true for this touch (the 1N moment lands best focally), or
      - no eligible touch-1 introduction exists to give a fresh focal (fallback), or
      - the story fit demands it (owner override).
  → HARD RULE: never the same character focal twice in a row; a character who
    has been focal twice is side-role-only thereafter unless the owner overrides.
  → When focal return IS chosen: prefer a character whose gate_visited.understood
    = false — the failed solver returning to finally get it.
```

**STEP C — co-hosted touches (owner D9; hard cap 4 touch-events per chapter):**
```
secondary_touches (max 2):
  From cleared operations with deficit > 0, excluding operation_due, pick up to 2
  by largest deficit. For each:
    { "operation": id, "touch": current_touch + 1,
      "carrier": an active population_index character who owns it,
                 else "experienced_stranger" }
echo_touch (max 1):
  From cleared operations with deficit > 0, not already used above:
    { "operation": id, "touch": current_touch + 1,
      "carrier": a returning character whose life progression scene can host it,
                 else null — if no natural carrier exists, echo_touch = null.
      Never force it. }
```

**STEP D — arc transition:**
```
IF every ELIGIBLE operation has deficit = 0
   (gate-blocked operations — prerequisite not yet at touch 2 — do NOT hold the
    arc open; their deficit carries into the next arc automatically, since
    deficit counts all schedule entries with arc <= arc_current, and gains
    priority as soon as the prerequisite clears):
  → type: arc_transition for the NEXT chapter
  → operation_due: null, touch_due: null
  → secondary_touches: from cleared operations with deficit > 0, by largest
    deficit, max 2. If none exist, an EMPTY list is valid. Ambient reinforcement
    is carried by the Assembler's cumulative "use naturally" list (owner D1
    hybrid + D9 lever 4), not by the pointer.
```

**STEP E — anchor (owner D3 — replaces all cadence logic):**
```
anchor_appears = true for every chapter whose type includes a gate
  (new_focal_character, return_to_character) and for anchor_interlude.
anchor_interlude remains available as a type but is scheduled only by user command
  in book 1 — the per-gate presence covers the thread.
```

---

## OUTPUT

Write the completed `update_brief.json` to `fiction_loop/prompts/update_brief.json`.
Overwrite the existing file completely.

Return to Orchestrator ONLY:
```
Done
OR: Done — UNDETERMINED: [field_path, field_path, ...]
```

Do not return any prose, any field values, or any summary of the chapter.

---

## CRITICAL RULES

- Never read or write mystery_anchor.json hidden_coherence.
- Never quote chapter prose in the return to Orchestrator.
- Every `[ ]` placeholder in update_brief.json must be replaced. No blanks allowed.
- If a field cannot be determined: write `"UNDETERMINED — [reason]"`, do not guess.
- next_chapter_pointer must always be computed and written, even if all other fields are UNDETERMINED.
- Do not modify any file other than `fiction_loop/prompts/update_brief.json`.
- Do not modify fiction_loop/core/ documents.
