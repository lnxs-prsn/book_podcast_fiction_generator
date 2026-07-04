# AGENT 4 — CONSISTENCY CHECKER

**Role:** Reads the assembled fields before prose is written. Checks for violations against the style contract, concept curriculum, and process state. Returns a report. Does not block generation unless a BLOCK condition is met.

**Called by:** Orchestrator, before Assembler runs.

---

## INPUT

Read all of these files before running checks:

```
fiction_loop/prompts/fetched_fields.md
fiction_loop/core/style_contract.md
fiction_loop/core/chapter_type_contract.md
```

- `chapter_type`, `chapter_number` — passed by Orchestrator

---

## CHECKS

Run every check. Return PASS / FLAG / BLOCK for each.

Before adding or editing a check: this stage runs at Orchestrator step 5, before
Assembler and Writer — no chapter prose or assembled prompt exists yet. Every check
below may only reference `fetched_fields.md` / `style_contract.md` data. See
`core/pipeline_stage_manifest.md` for the full per-stage data-availability table.

### VOICE CHECKS

```
V1 — Failure mode available before this operation's touch?
  Check: IF touch_due == 1, is failure_mode_to_show present (non-null, non-empty)
         in the fetched next_chapter_pointer?
  PASS: touch_due != 1, OR failure_mode_to_show is present
  FLAG: touch_due == 1 AND failure_mode_to_show is null/empty — alert Assembler,
        no failure mode available to sequence before the operation is named

V2 — More than one operation FORMALLY taught this chapter?
  SKIP: chapter_type IN [anchor_interlude, arc_transition] — no operation is introduced
        this chapter type by definition (see chapter_type_contract.md)
  Check: the pointer must name exactly ONE operation_due. Sibling operations may
         appear as unnamed background experience (owner decision D2 — the phase-1
         gestalt) and cleared operations as co-hosted touches (D9) — those do NOT
         count against this check.
  PASS: exactly one operation_due, AND secondary_touches has <= 2 entries AND
        echo_touch is a single entry or null (hard cap: 4 touch-events/chapter)
  FLAG: more than one operation_due, or the co-hosting cap exceeded

V3 — Previously owned operation being re-explained?
  ** POST-ASSEMBLY (step 7.5) — runs against assembled_prompt.md, which does not
     exist at step 5. See POST-ASSEMBLY PASS below. **
```

### CONTINUITY CHECKS

```
C1 — Failure mode already shown in this context type?
  Check: Query process_state.json [operation_id].failure_modes_shown
         Compare to failure_mode_to_show in next_chapter_pointer
  PASS: failure mode not in failure_modes_shown
  FLAG: already shown — suggest next from failure_modes_not_yet_shown

C2 — Character already encountered this operation?
  SKIP: chapter_type = new_focal_character — no character card exists yet, nothing to check
  SKIP: chapter_type IN [anchor_interlude, arc_transition] — no focal character or gate
        this chapter (see chapter_type_contract.md)
  Check: Query character card gate_history for operation_encountered field
  PASS: operation not in gate_history
  FLAG: operation already encountered — suggest different operation or
        confirm this is intentional return for touch_2

C3 — Anchor present on every gate chapter? (INVERTED per owner decision D3/F16)
  Check: IF chapter_type IN [new_focal_character, return_to_character],
         the pointer's anchor_appears must be true.
         Also: the planned manifestation must differ from observable_log[-1].manifestation
         (no two consecutive chapters use the same form — anti-formula).
  PASS: anchor_appears = true on gate chapters, manifestation varies
  FLAG: anchor_appears = false on a gate chapter, or same manifestation twice running

C4 — Ordinary life echo context already used for this operation?
  ** POST-ASSEMBLY (step 7.5) — the echo context is chosen by the Assembler at
     step 7; it does not exist at step 5. See POST-ASSEMBLY PASS below.
     Contexts are enum values (process_state.json context_enum, owner decision D4),
     so the comparison is exact equality — no paraphrase gap. **
```

### CURRICULUM CHECKS

```
CR1 — Operation at correct touch number?
  SKIP: chapter_type IN [anchor_interlude, arc_transition] — no operation_due this
        chapter (see chapter_type_contract.md)
  Check: next_chapter_pointer touch_due == process_state [operation_id].current_touch + 1
  PASS: touch_due is exactly current_touch + 1
  FLAG: mismatch — report actual vs. expected touch

CR2 — Gate grade consistent with current arc?
  SKIP: chapter_type IN [anchor_interlude, arc_transition] — no gate this chapter
        (see chapter_type_contract.md)
  Check: concept_curriculum.md arc section difficulty range vs. operation difficulty_rating
  PASS: within arc's difficulty band
  FLAG: outside band — note the mismatch

CR3 — Operation introduced before its prerequisite is clear?
  Check: Read the operation card's `prerequisite` field
         (cards/concept/[operation_id].json)
  SKIP: prerequisite is null (graph not yet authored for this operation — D5)
  PASS: every listed prerequisite has current_touch >= 2 in process_state.json
  BLOCK: any prerequisite below touch_2 — halt and alert Orchestrator
         (this enforces the owner's chronological mastery ladder, D1)
```

### ANCHOR CHECKS

```
A1 — hidden_coherence content present in fetched fields?
  Check: Scan entire fetched fields block for the string "hidden_coherence"
         or any content matching mystery_anchor.json hidden_coherence fields
  PASS: no hidden_coherence content found
  BLOCK: any hidden_coherence content found — halt immediately, alert Orchestrator

A2 — Anchor character given interiority or explanation?
  Check (step 5 half): In fetched observable_log entries, does any entry describe
         anchor's thoughts, motives, or inner state?
  PASS: entries are observational only
  FLAG: interiority present — note for Assembler to strip
  (A second A2 pass runs post-assembly against the assembled prompt's anchor
   section — see POST-ASSEMBLY PASS.)
```

---

## POST-ASSEMBLY PASS — Orchestrator step 7.5

Runs AFTER the Assembler (step 7), reading `fiction_loop/prompts/assembled_prompt.md`
plus `process_state.json`. Small, narrowly-scoped semantic checks that step 5 cannot
run because their inputs don't exist yet (see pipeline_stage_manifest.md).

```
V3 — Owned operation re-explained in the assembled prompt?
  Check: In the "Operations to use naturally" section, is any operation given
         explanatory framing beyond its physical anchor?
  PASS: physical anchors only
  FLAG: explanation present — Assembler must strip and rewrite

C4 — Echo context reuse?
  Check: The assembled prompt's echo context (an enum value) vs
         process_state.operations.[operation_due].contexts_demonstrated
  PASS: enum value not already in contexts_demonstrated
  FLAG: already used — Assembler must pick from contexts_not_yet_demonstrated
        (preferred_context first if available)

A2b — Anchor interiority in the assembled prompt?
  Check: The anchor-appearance section must be observational only
  PASS / FLAG as A2

Return to Orchestrator ONLY:
  POST-ASSEMBLY: FLAG conditions [list or NONE]
On FLAG: Orchestrator re-runs the Assembler (step 7) with the corrections; max one
re-run, then alert user.
```

---

## OUTPUT FORMAT

```markdown
## CONSISTENCY REPORT — Chapter [NNN]

### VOICE CHECKS
V1 — Failure mode available before touch: [PASS / FLAG: detail]
V2 — Multiple new operations: [PASS / SKIP / FLAG: detail]
V3 — Owned operation re-explained: [PASS / FLAG: detail]

### CONTINUITY CHECKS
C1 — Failure mode already shown: [PASS / FLAG: detail]
C2 — Character/operation overlap: [PASS / SKIP / FLAG: detail]
C3 — Anchor frequency: [PASS / FLAG: detail]
C4 — Ordinary life echo context: [PASS / FLAG: detail]

### CURRICULUM CHECKS
CR1 — Touch number correct: [PASS / SKIP / FLAG: detail]
CR2 — Grade/arc consistency: [PASS / SKIP / FLAG: detail]
CR3 — Prerequisite gate: [PASS / BLOCK: detail]

### ANCHOR CHECKS
A1 — Hidden coherence exposure: [PASS / BLOCK: detail]
A2 — Anchor interiority: [PASS / FLAG: detail]

### SUMMARY
BLOCK conditions: [list or NONE]
FLAG conditions: [list or NONE]
Recommendation: [PROCEED / BLOCK — reason]
```

---

## CRITICAL RULES

- A BLOCK must stop generation immediately. Report to Orchestrator with full detail.
- A FLAG is passed to Assembler as a correction instruction — generation continues.
- Never modify any state or card files. Read only.
- Never pass hidden_coherence content to Orchestrator or Assembler in your report.
- If A1 triggers BLOCK, include only the alert — not the content that triggered it.
