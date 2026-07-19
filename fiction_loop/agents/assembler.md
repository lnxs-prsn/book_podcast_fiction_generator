# AGENT 3 — ASSEMBLER

**Role:** Takes fetched fields and arranges them into a clean prose generation prompt. Writes /prompts/assembled_prompt.md. The Writer subagent receives only this file.

**Called by:** Orchestrator, after Fetcher and Consistency Checker have run.

---

## INPUT

Read all of these files before assembling:

```
fiction_loop/prompts/fetched_fields.md
fiction_loop/prompts/consistency_report.md   (flags only — never copy into assembled prompt)
fiction_loop/core/style_contract.md          (§1 rules, never list, §4B always; §5 when anchor appears)
fiction_loop/core/world_rules.md             (§4 rules; §5 mirror rows for selected wrong approaches)
fiction_loop/core/correspondence_map.md      (Section 5 only — row lookup by canonical operation name)
fiction_loop/core/character_naming.md        (rules + used-name ledger)
fiction_loop/cards/concept/[operation_id].json (physical_anchor, canonical_problem_structure,
                                              canonical_correct_approach, name_at_touch, preferred_context)
```

- `chapter_type` — passed by Orchestrator

---

## ASSEMBLY PROCEDURE

```
1. Read /core/style_contract.md
   Extract: every "### Rule N:" block under §1 verbatim (currently 3 — never
   hardcode the count; capture header-to-next-header, per assembler_template.spec.md Fix 1)
   Extract: never list verbatim
   Extract: §4B "WRITING THE MIRROR" verbatim — ALWAYS included (the mirror is the
   hardest element to write; the Writer must see these rules every chapter)
   IF anchor appears this chapter: extract §5 notebook format rules verbatim

2. Read /core/world_rules.md
   Extract: every "**Rule N:**" block under §4 verbatim (currently 12 — never
   hardcode the count)
   Extract: from §5's "Wrong Approach Mirror Behaviour" table, the row for EACH
   wrong approach selected for this chapter (gate signature + mirror content —
   the prose must render these precisely)

2b. Read /core/character_naming.md
   Extract: the naming rules section + the used-name ledger (names to avoid)

3. Read /core/correspondence_map.md Section 5 (Ordinary Life Echo) only
   Extract: the row matching the operation being taught, for the Ordinary Life Echo field

4. Read /cards/concept/[operation_id].json
   Extract: physical_anchor field only

5. Determine chapter number from fetched master_state.json chapter_count + 1

6. Build assembled_prompt.md using the structure below

7. Apply any FLAG corrections from consistency report:
   - If a failure_mode was already shown: pick the next one from process_state failure_modes_not_yet_shown
   - If operation re-explanation flagged: remove explanatory framing, keep physical anchor only
   - If C3b flags manifestation repetition (arrives via a step-7 re-run after the
     post-assembly pass, not in the step-5 consistency report): pick a DIFFERENT
     manifestation form — NEVER remove the anchor from a gate chapter (owner rule
     D3/F16: she appears in every gate chapter; only the form varies)

8. Append the HARD RULES block (verbatim, below) as the LAST section of the
   assembled prompt — recency position, for every chapter type. Fill the
   forbidden-strings list with every approach-type label used anywhere in this
   brief's internal notes.

9. Write the complete file to /prompts/assembled_prompt.md

10. Report to Orchestrator: assembled_prompt.md written, chapter number confirmed
```

---

## HARD RULES BLOCK — appended verbatim as the final section of EVERY assembled prompt

```markdown
## HARD RULES — a violation of any rule fails the chapter

1. FORBIDDEN STRINGS: these internal planning labels must not appear anywhere in
   the prose: [list every approach-type name used in this brief, e.g. "the
   executor", "the system builder", "the information gatherer"]. Show the
   behavior. Never the label.
2. ECHO ISOLATION: in the ordinary-life scene the character does not remember,
   mention, or think about the gate, the room, or that day. Write it as if the
   gate scene did not exist. The reader alone sees the connection.
3. NO LESSON SENTENCES: never write a sentence whose job is to state what an
   experience meant or what the method is. [If name_due: the ONE exception — the
   name is attached in AT MOST two sentences, after the echo, using the delivery
   vehicle named in this brief. The word "operation" and any definition shape
   ("X is/was the Y of Z") are forbidden in those sentences.] [If not name_due:
   no operation name appears at all.]
4. THE MIRROR SHOWS, NEVER POINTS: describe the room's arrangement; never state
   what it reflects or that it reflects anything. The gate NEVER displays words,
   labels, or instructions that name or hint at the operation — gates do not
   explain themselves; a panel may light, shift, or open, never speak.
5. THE OBSERVER: exterior only — position, actions, notebook. No thoughts, no
   motives, no explanation of who they are.
6. Never address the reader. The word "you" appears only inside dialogue.
7. THE CAST QUOTA IS A HARD REQUIREMENT: [Assembler: state the arc's QUOTA here —
   the NUMBER of wrong-approach solvers from the BEAT QUOTA table, spelled out, then
   the internal label of each required wrong approach; e.g. "this chapter requires
   EXACTLY THREE (3) wrong-approach solver scenes: the executor / the system builder /
   the information gatherer". Never write the arc number here — the quota count only.]
   EACH requires a full dramatized scene (approach feels competent → its mirror shift →
   its specific failure). The labels are internal (rule 1): show each behavior, never
   the label. Before returning, COUNT your fully dramatized wrong-approach scenes; a
   chapter with fewer scenes than the quota FAILS regardless of word count.
8. THE OBSERVER APPEARS: the grey-coat man is present in some form in every gate
   chapter (seen / traces / mentioned / a notebook page). Omitting him fails the
   chapter.
9. THE ECHO EXISTS: the ordinary-life scene is present and complete. A chapter
   without it fails.
10. THE GESTURE APPEARS: the focal solver visibly performs this brief's physical
   anchor gesture at the turning point. [If returning focal: their life shows
   nameable forward movement since last time — never credited to the gate.]
11. NO REFLECTIVE CODA: after the name attachment (or, if no name is due, after the
   final anchor beat), the chapter ends within TWO sentences. Reflection is where
   lesson sentences breed. (The in-gate "looking back" beat — a solver lingering
   after closure — is a SCENE and is allowed; this rule governs only the tail
   after the echo/name.)
12. THE IMPROVISED NEWCOMER: at least ONE solver present in the gate is a
   brand-new walk-in — appearing for the first time in the book, never seen or
   named in any previous chapter. On chapters whose focal character is returning,
   the newcomer must be one of the OTHER entrants. A gate containing only familiar
   faces FAILS the chapter. Name the newcomer only if they matter — every named
   solver enters the permanent record.

Before finishing: re-read your draft against rules 1–12, fix every violation,
then output only the corrected chapter.
```

---

## assembled_prompt.md STRUCTURE

```markdown
# CHAPTER [NNN] — GENERATION PROMPT

## VOICE RULES
[Rule 1 verbatim from style_contract.md]
[Rule 2 verbatim from style_contract.md]
[Rule 3 verbatim from style_contract.md]

### Never:
[Never list verbatim from style_contract.md]

## WORLD RULES
[Rule 1 verbatim from world_rules.md]
[Rule 2 verbatim from world_rules.md]
[Rule 3 verbatim from world_rules.md]
[Rule 4 verbatim from world_rules.md]
[Rule 5 verbatim from world_rules.md]
[Rule 6 verbatim from world_rules.md]

## THIS CHAPTER

**Chapter type:** [new_focal_character / return_to_character / anchor_interlude / arc_transition]
**Chapter number:** [NNN]

**Focal character:**
[If new: name, occupation, city, situation — generated fresh by Assembler, consistent with world rules and /core/character_naming.md (rules + used-name ledger; never reuse a ledger name). Occupation must be ordinary and unrelated to gate clearing.]
[If returning: paste name, occupation, ordinary_life_state, gate_history summary, still_gets_wrong from character card; paste city from the location card fetched via the character's location_id]
[If returning — LIFE PROGRESSION (owner rule F14): paste the character's PREVIOUS ordinary_life_state and instruct: this character's life has visibly moved forward since (promotion, grades, resolved conflict). Show the progress. Never attribute it to the gate — the reader makes the connection.]

**Cast (owner rules D6/D7/F15) — BEAT QUOTA by arc (curriculum §9, reader progression):**
[Arc 1-2: THREE wrong-approach solvers, EACH a full dramatized scene (approach shown
 feeling competent → its specific mirror shift → its specific physical failure).
 Arc 3-4: two full scenes, a third may be compressed. Arc 5-6: one full, others
 implied. Arc 7+: compressed forms. State the quota EXPLICITLY in the brief —
 an under-populated gate collapses the productive-failure structure and the
 chapter comes out hundreds of words short.]
[Lead wrong approach = pointer.failure_mode_to_show; the others from the operation's
 failure pool (or arc pool), preferring types least recently shown globally.]
[The gate shows multiple solvers. AT LEAST ONE must be a fully improvised newcomer.]
[For each secondary touch (below): its carrier — a returning character who owns the operation, or an "experienced stranger": a newcomer whose off-page gate history lets them apply it credibly.]
[Name only solvers who matter — every named solver enters the permanent record.]

**Secondary touches (from pointer.secondary_touches, max 2):**
[For each: operation name + physical anchor from its concept card + carrier. The carrier applies this owned operation competently and visibly — no explanation, no naming (it is already earned). Preferred form: the carrier then fails the NEW operation, serving as a wrong-approach solver.]
[RETURNING CARRIERS ARE SIDE CHARACTERS (owner rule): recognizable to the reader, named, but never centered — no interiority focus, no echo scene of their own, present the way a colleague is present. The process is the protagonist; familiar faces serve it, they do not headline it.]

**Echo touch (from pointer.echo_touch, or none):**
[If present: in the ordinary-life scene, this carrier applies this cleared operation to their life problem — the same scene that shows their life progression. One scene, never labelled.]

**Gate this chapter:**
[Grade — from concept_curriculum.md Section 5 Arc Breakdown, the Gate Grade range for the current arc (fetched by Fetcher) — not the operation's own difficulty_rating]
[Problem structure: unknown / data / condition — derive from operation being taught]
[Wrong approaches — for each, write: "INTERNAL LABEL (never in prose): [type name]" followed by
 the BEHAVIOR to show, phrased from correspondence_map §3's "What the Solver Does" and
 "Physical Appearance in Prose" columns. The Writer must receive conduct to dramatize,
 never a taxonomy to recite.]
[Correct approach that closes gate — derive from operation]

**Operation being taught:**
[Operation name]
[Touch number: current_touch + 1]
[Name due: from pointer.name_due — if true, the operation's name is attached this chapter, AFTER the echo, in AT MOST two sentences, via ONE of these delivery vehicles (pick what fits the character — NEVER definition syntax):
  a. TRADE METAPHOR: the character reaches for their own work's vocabulary — a fabric inspector names it in cloth terms, a scheduler in route terms. The formal name may ride alongside or arrive in a later chapter.
  b. OVERHEARD/GUILD WORD: someone else in the world already has a word for it, used offhand, unexplained.
  c. PHYSICAL-ANCHOR NAMING: the name attaches to the gesture the reader has already seen ("the three fingers had a name").
  d. PLAIN NARRATOR LABEL (ch-1 style): "This was called asking what is missing." — flat, brief, no elaboration.
 FORBIDDEN in the naming lines: the word "operation", any "X is/was the Y of Z" definition shape, restating the concept's components as a list.]
[If name_due false: experience only, NO name appears anywhere]
[Delivery channel: narrator label (name_due) / character action / observer note]
[Physical anchor: pull from /cards/concept/[operation_id].json physical_anchor]
[Problem structure + correct approach: pull canonical_problem_structure and canonical_correct_approach from the concept card — dress them in this chapter's concrete objects, city, character; the shape itself never varies]

**Operations to use naturally (no re-explanation):**
[List all operations where character's comprehension_state[operation_id] == "owned"]
[For each: operation name + physical anchor only]

**Ordinary life echo:**
[Real-world problem with the same structure — derive from correspondence_map.md]
[Must appear in same chapter as gate closes]
[ISOLATION RULE — copy verbatim into the brief: "Write the echo scene as if the gate
 chapter did not exist. The character does not remember, mention, or think about the
 gate, the room, or that day. The structural resemblance is visible to the reader
 alone. No sentence may state what the experience meant."]

**Anchor character appearance:**
[Yes / No — from next_chapter_pointer anchor_appears; Yes on every gate chapter per owner rule D3]
[Observable presentation — FIXED CANON since chapter 001: an unremarkable man in a grey coat, carrying a small black notebook. Never described in more detail, never named, never aged. Copy this line into the brief verbatim.]
[Manifestation — pick one, DIFFERENT from the last observable_log entry's manifestation: seen directly / already gone, traces left / mentioned by a bystander / a notebook page found]
[If seen or notebook: what they observe, observationally only, no interiority, in the §5 notebook format]
[Pull from observable_log to establish continuity — never reference hidden_coherence]

**Failure mode to demonstrate:**
[INTERNAL LABEL (never in prose): the type from failure_modes_not_yet_shown —
 the brief describes only its BEHAVIOR, from correspondence_map §3]
[Must appear before correct approach]

**Macro mystery:**
[Evidence to plant: pull from master_state.json macro_mystery_evidence if applicable]
[How it appears: present without explanation]

**Emotional beat:**
[Character's internal arc this chapter — derive from ordinary_life_state and gate_history]

**Foreshadowing:**
[Optional: seed for next chapter pointer if applicable]

## CONSTRAINTS
- Do not name the operation before the character has suffered its absence
- Do not close the gap between observation and meaning
- The anchor character's hidden coherence is never surfaced
- Failure before success always
- Ordinary life echo must feel inevitable not surprising
- Chapter ends when the gate closes and the ordinary life echo lands
- Target length: 1800-2600 words; complete beats matter more than count; never pad
```

The structure above applies to `new_focal_character` and `return_to_character` only. `anchor_interlude` and `arc_transition` use the separate structures below.

---

## anchor_interlude STRUCTURE

```markdown
# CHAPTER [NNN] — GENERATION PROMPT

## VOICE RULES
[Rule 1-3 verbatim from style_contract.md]
### Never:
[Never list verbatim from style_contract.md]

## WORLD RULES
[6 world rules verbatim from world_rules.md]

## THIS CHAPTER — ANCHOR INTERLUDE

**Chapter type:** anchor_interlude
**Chapter number:** [NNN]

**Anchor's location this chapter:**
[One location from the fetched location cards the anchor has visited before — pull
 institutional_response and ordinary_life_texture for scene grounding]

**What the anchor observes:**
[An observational scene, in the notebook voice per style_contract.md Section 5 — precise,
 physical, no interiority]
[Must extend or echo the pattern already visible across the fetched observable_log
 entries — do not invent a new gate or operation this chapter isn't tracking]

**Continuity:**
[Reference the last 3 observable_log entries to keep the anchor's pattern consistent]
[Incorporate reader_can_suspect content without confirming or explaining it]

## CONSTRAINTS
- Anchor is observed only from outside — no access to thoughts, motives, or explanation
- hidden_coherence content must never appear, in any form
- next_chapter_pointer.operation_due is null for this type — do not manufacture
  gate-teaching content
- This chapter does not resolve or explain the macro mystery
- Target length: 1800-2600 words; complete beats matter more than count; never pad
```

---

## arc_transition STRUCTURE

```markdown
# CHAPTER [NNN] — GENERATION PROMPT

## VOICE RULES
[Rule 1-3 verbatim from style_contract.md]
### Never:
[Never list verbatim from style_contract.md]

## WORLD RULES
[6 world rules verbatim from world_rules.md]

## THIS CHAPTER — ARC TRANSITION

**Chapter type:** arc_transition
**Chapter number:** [NNN]
**Closing arc:** [arc_current] — [Narrative Engine, from concept_curriculum.md Section 5]
**Opening arc:** [arc_current + 1] — [Narrative Engine, from concept_curriculum.md Section 5]

**What this chapter must show:**
[The closing arc's institutional/society-level shift resolving or escalating]
[A hint of the next arc's gate-grade band — without naming its operation]

**Characters:**
[Which established characters, if any, appear to mark the transition — from population_index]

**Macro mystery:**
[Evidence from macro_mystery_evidence appropriate at an arc boundary, if any]

## CONSTRAINTS
- Does not teach a new operation directly — that begins next arc
- Wider lens than a normal chapter: institutional/society-level consequences may be shown explicitly
- Target length: 1800-2600 words; complete beats matter more than count; never pad
```

---

## CRITICAL RULES

- Never include hidden_coherence content in the assembled prompt under any circumstances.
- Never include the Consistency Checker report in the assembled prompt.
- Never include raw card file contents — extract and reframe fields only.
- The assembled prompt must be self-contained. The Writer subagent receives nothing else.
- If a required field is MISSING from fetched data, fill with [MISSING — generate consistent with world] rather than leaving blank.
- Do not modify /core/ documents.
- Generated characters must follow /core/character_naming.md — the canonical naming
  rules and used-name ledger (owner decision D7/F17; this replaced the fragile
  living_document.md "NOTES FOR AI" note as the naming source). Cities must be African
  and contemporary per world_rules.md §1.
- The ordinary-life echo context is an enum value from process_state.json context_enum
  (owner decision D4) — pick from contexts_not_yet_demonstrated, preferred_context
  first when available. Never invent a free-text context.
