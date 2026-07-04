# DOCUMENT 4: LIVING DOCUMENT
*The session save file. Updated after every approved chapter by `refresh_living_doc.py`. The human never edits this file.*

*The Extractor reads this file when filling update_brief.json, for narrative-level continuity context that the raw state JSON does not carry. After the chapter is written and approved, `refresh_living_doc.py` rewrites this file from the approved chapter text, closing the cycle for the next iteration.*

---

## HOW THIS DOCUMENT WORKS IN THE AGENT LOOP

This document is NOT pasted into sessions manually. It is read by the Extractor when filling update_brief.json, and written by `refresh_living_doc.py` at the end of every loop.

The human only interacts with this document to:
- Check current story state via the `show living document` command
- Correct an error the Updater made
- Set the initial state before the first chapter

Everything else is automatic.

---

## CURRENT STATE

| Field | Value |
|---|---|
| Story title | The Sankofa Gates |
| Last updated | After Chapter 3 |
| Last chapter completed | 3 |
| Current arc | Arc 1 — Gate Grade 1-2 |
| Active focal characters | Kwabena Asante |
| Mystery person last appeared | Chapter 3 (Outside Achimota depot / Notebook entry observed) |
| Macro mystery evidence count | 3 |

---

## PROCESS STATE SUMMARY
*Compressed view. Full detail in /state/process_state.json.*

| Operation | Touch | Last Context | Next Due |
|---|---|---|---|
| Identify unknown / data / condition | 2 | Gate (Grade 2) / Workplace | Chapter 4 — Touch 3 |
| What is missing (absence over presence) | 1N | Gate (Grade 1) / Domestic | Chapter 3 — Touch 2 |
| Separate parts of condition | 1 | Gate (Grade 2) / Workplace | Chapter 4 — Touch 2 |
| Look at the unknown | 1 | Gate (Grade 2) / Workplace | Chapter 4 — Touch 2 |
| Did you use all the data? | 0 | — | Chapter 4 — Touch 1N |
| Can you check the result? | 0 | — | Chapter 4 — Touch 1N |
| Can you derive the result differently? | 0 | — | Arc 3 |
| Do you know a related problem? | 1 | Gate (Grade 2) / Workplace | Chapter 4 — Touch 1N |
| Here is a problem related to yours | 0 | — | Chapter 4 — Touch 1N |
| Analogy — simpler analogous problem | 0 | — | Arc 3 |
| Looking back / transfer | 1 | Gate (Grade 2) / Workplace | Chapter 4 — Touch 2 |
| Decompose condition | 0 | — | Arc 3 |
| Introduce auxiliary elements | 0 | — | Arc 3 |
| Can you use the result? | 0 | — | Arc 4 |
| Auxiliary problem (invented) | 0 | — | Arc 4 |
| Specialisation | 0 | — | Arc 4 |
| Working backwards | 0 | — | Arc 5 |
| Generalisation | 0 | — | Arc 5 |
| Inventor's Paradox | 0 | — | Arc 5 |
| Reductio ad absurdum | 0 | — | Arc 5 |
| Variation / restatement | 0 | — | Arc 6 |
| Heuristic vs proof | 0 | — | Arc 7 |
| Subconscious work | 0 | — | Arc 7 |
| Auxiliary problem chains | 0 | — | Arc 8 |
| The sitting down (physical marker) | 2 | Gate (Grade 2) | Chapter 4 — Touch 3 |

---

## FAILURE MODES NOT YET SHOWN

*All wrong approach types must appear across Arcs 1-4. Types introduced per arc per concept_curriculum.md.*

**Arc 2 (must appear before Arc 3 begins):**
- The confident specialist (applies domain expertise to wrong problem type)
- The hypothesis tester (tests systematically without naming what is being tested)

**Arc 3-4 (introduced as operations expand):**
- The executor on complex condition (acts on first part, ignores others)
- The system builder on complex condition (processes all parts equally, finds no path)
- The force applier (pushes harder when path does not appear)
- The perfectionist (refuses heuristic, waits for certainty before reasoning)

**Arc 5-6 (tied to restatement and working backwards):**
- The variation-tester (tests restatements of wrong statement, all fail)
- The single-step auxiliary solver (invents stepping stone but treats it as destination)
- The planner without synthesis (builds chain forward, cannot reverse)

**Arc 7+ (tied to heuristic/proof distinction):**
- The heuristic-only solver (finds method, cannot account for it, cannot distinguish where it applies)
- The guild verifier (demands proof before acting, paralysed by heuristic evidence)

---

## POPULATION INDEX
*One line per character. Full detail in /cards/characters/[id].json.*

| ID | Name | Occupation | City | Comprehension Level | Last Seen |
|---|---|---|---|---|---|
| char_001 | Yejide Adeyemi | Fabric Checker / Seamstress | Lagos | 1 (Touch 1/1N) | Chapter 1 |
| char_002 | Kwabena Asante | Dispatch Clerk (Promoted) | Accra | 2 (Touch 2) | Chapter 3 |
| char_002a | Ama Serwah | Plantain Seller | Accra | 1 (Touch 1) | Chapter 2 |

---

## MYSTERY PERSON THREAD
*Observable log summary. Full detail in /state/mystery_anchor.json.*

Appearances: 3
Last location: Outside Achimota depot / Observed speaking to cleaner, recording notebook entry
Reader can suspect: The anchor is now observing both inside and outside gates, tracking not just mirror content but also post-gate behavior and social echoes. Their notation has become more precise, explicitly identifying "threshold naming" as the correct approach and logging register transitions by minute.

---

## MACRO MYSTERY EVIDENCE
*What the reader can suspect but not confirm.*

Evidence count: 3
Current state: The anchor’s notebook entry confirms they are now tracking multiple wrong approaches within a single gate (executor and information gatherer) and noting the exact moment the right question forms ("threshold naming"). This suggests the anchor understands that the core failure is not action but misidentification of the problem structure—reinforcing that gates are diagnostic mirrors, not tests.

---

## ACTIVE FORESHADOWING

- The anchor now observes ordinary life echoes directly, questioning witnesses about solver demeanor after exit ("came out calm").
- Kwabena’s internal monologue explicitly names the operation for the first time: “Before acting, name what you seek. Name what you have. Name what ties them.”
- The gate’s mirror for the information gatherer showed *no change*—highlighting that completeness without purpose produces no feedback.
- The chalkboard condition (“contains the key”) was literal, not metaphorical—emphasizing that gates respond to precise reading of the condition, not interpretation.

---

## NEXT CHAPTER TARGET

| Field | Value |
|---|---|
| Chapter | 004 |
| Type | new_focal_character |
| City | [ To be determined by Orchestrator — African city, contemporary ] |
| Gate grade | [ To be determined ] |
| Gate problem structure | [ To be determined ] |
| Wrong approach 1 | the confident specialist |
| Wrong approach 2 | the hypothesis tester |
| Right question | [ To be determined ] |
| Operation Touch | Do you know a related problem?: Touch 1N |
| Sitting down | Must appear. After both wrong approaches are exhausted. Physical. |
| Mystery person appears | Yes |
| Ordinary life echo | [ To be determined ] |
| Focal character | [ To be determined ] |
| Emotional beat | [ To be determined ] |
| Foreshadowing to plant | [ To be determined ] |

---

## NOTES FOR AI — CURRENT SESSION

- African names only. No Arabic names. (Yejide, Fadeke, Kwabena, Ama, Owusu, Mensah, Esi established. Continue this rule).
- The wrong approaches must feel competent and reasonable before they fail.
- Gate register and mirror behaviour must be shown for all wrong approaches.
- Mirror prose rule: describe the room's arrangement. Never state what it is showing.
- Do not name the operation in the chapter until the experience is complete.
- The fourth wall never breaks. No direct address to reader.
- The sitting down must be preceded by exhaustion of wrong approaches.
- The solution after the right question arrives is fast and quiet. The gate closes without ceremony.
- Mystery person notebook format: Gate grade. Approach type. Mirror content (one precise physical description). Underlined: the gap the mirror showed. Register log time-stamped. Nothing else.
- Ordinary life echo: same question applied to ordinary problem. Never labelled as connected. At least one other person goes still or conversation changes register.
- Chapter length: 2000-3000 words.
- Chapter 3 completed Arc 1’s core operations. Chapter 4 must introduce Arc 2 operations: confident specialist and hypothesis tester as wrong approaches, with “related problem” as the hard operation.
- Kwabena’s promotion shows institutional recognition of process-based problem-solving.
- The anchor’s observation of the ordinary life echo (“came out calm”) signals they are now tracking transfer beyond the gate.
- The phrase “checking the frame” is now in-world terminology for “identify unknown/data/condition.”