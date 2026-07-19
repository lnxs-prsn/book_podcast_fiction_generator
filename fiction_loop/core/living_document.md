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
| Last updated | After Chapter 8 |
| Last chapter completed | 8 |
| Current arc | Arc 2 — Gate Grade 2–3 |
| Active focal characters | Yejide Adeyemi, Kwabena Asante, Wanjiku Mwangi, Fatou Ndiaye, Nantale Namakula |
| Mystery person last appeared | Chapter 8 (Kampala, Nakasero market — described by merchants as an unremarkable man in a grey coat; left a torn notebook page inside the gate) |
| Macro mystery evidence count | 7 |

---

## PROCESS STATE SUMMARY
*Compressed view. Full detail in /state/process_state.json.*

| Operation | Touch | Last Chapter | Status |
|---|---|---|---|
| Identify unknown / data / condition | owned | — | — |
| What is missing (absence over presence) | owned | — | — |
| Separate parts of condition | 1 | 004 | Touch 2 pending |
| Look at the unknown | 1 | 005 | Touch 2 pending |

All other operations are at touch 0 and will be introduced in later arcs as scheduled in /state/process_state.json.

---

## FAILURE MODES NOT YET SHOWN

*All wrong approach types must appear across Arcs 1-4. Types introduced per arc per concept_curriculum.md.*

**Arc 2 (introduced as operations expand):**
*All Arc 2 failure modes have now been shown (the confident specialist, the hypothesis tester — both in chapter 008).*

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
| char_001 | Yejide Adeyemi | Fabric Checker / Seamstress | Lagos | 2 (Touch 2) | Chapter 6 |
| char_002 | Kwabena Asante | Dispatch Clerk (Promoted) | Accra | 2 (Touch 2) | Chapter 7 |
| char_002a | Ama Serwah | Plantain Seller | Accra | 1 (Touch 1) | Chapter 2 |
| char_003a | Kojo Acheampong | Depot Supervisor | Accra | 1 (Touch 1) | Chapter 3 |
| char_003b | Akosua Osei | Cleaner | Accra | 1 (Touch 1) | Chapter 3 |
| char_004 | Wanjiku Mwangi | Hospital Records Officer | Nairobi | 2 (Touch 2) | Chapter 7 |
| char_005 | Fatou Ndiaye | Land Registry Clerk | Dakar | 1 (Touch 1) | Chapter 7 |

---

## MYSTERY PERSON THREAD
*Observable log summary. Full detail in /state/mystery_anchor.json.*

Appearances: 8  
Last location: Kampala, near Nakasero market — an unremarkable man in a grey coat observed the gate event; a torn notebook page was found inside the dispensary gate wedged between the counter and the wall, containing precise register timestamps and mirror-content descriptions of Dr. Akello’s specialist approach and the young man’s tester approach. The page was read by Nantale before the gate fully vanished. The guild coordinator later received merchant descriptions but filed the incident without follow-up.  
Reader can suspect: The anchor is aware of every gate where a non-guild solver succeeds and is leaving pages deliberately — the terminology “specialist approach” and “tester approach” match the anchor’s diagnostic categories, and the anchor is tracking the specific gap each wrong approach misses. The anchor is also present before the guild can verify.

---

## MACRO MYSTERY EVIDENCE
*What the reader can suspect but not confirm.*

Evidence count: 7  
Current state: The anchor’s notebook page from the Kampala gate documents two wrong approaches in a Grade 2 gate, each with mirror content and register timestamps, and underlines the gap each missed — the specialist ignored the reference chart, the tester never activated the verification panel. The page ends with “No closure.” The anchor’s diagnostic precision, combined with the fact that the page was left inside the gate for anyone to find, suggests the anchor is not merely observing — the anchor is building a record that, if assembled, would articulate the process the guild refuses to see. Meanwhile, Nantale Namakula, a pharmacist with no gate training, closes the gate by reading the chart, using the panel, and waiting for confirmation — a procedure that matches what the anchor documented as the missing steps.

---

## ACTIVE FORESHADOWING

- Nantale’s instinct — to look at the chart, to check the panel, to wait for the result — is a direct application of “look at the unknown,” “find what is missing,” and “can you check the result?” to a gate problem. She has performed these operations for twelve years without naming them. The reader sees the operations transferring before the character knows what to call them.
- The guild coordinator files the report with the word “anomalous closure” and the marginal note “checking,” indicating that the guild is beginning to notice the pattern but lacks the vocabulary to integrate it. The anchor’s pages contain that vocabulary; the guild is still not reading them.
- The junior dispenser Moses writes something on a scrap of paper after watching Nantale re-check the prescription — the instinct is spreading to those who observe the solvers, not only to the solvers themselves.
- Dr. Akello’s failure as a confident specialist shows that domain expertise without the willingness to look outside the domain boundary cannot solve the new gate structures. The guild, which trains specialists to trust their domain, is structurally producing this failure mode.
- The anchor’s page explicitly lists what both wrong approaches missed, and the missing steps are the ones Nantale performed. The anchor is effectively writing the solution; the world is catching up to the pages being left behind.
- The phrase “The stool was cold. The surface of the verification panel was wiped clean” hints that the anchor may have sat at that counter, used the panel, and prepared the scene before the gate opened — a degree of foreknowledge or methodical preparation that the guild would find terrifying if it understood.

---

## NEXT CHAPTER TARGET

| Field | Value |
|---|---|
| Chapter | 008 |
| Type | new_focal_character |
| City | To be determined — contemporary African city |
| Gate grade | 2 |
| Gate problem structure | Requires recalling a structurally similar prior gate to solve; data appears unrelated until memory of a previous gate is activated |
| Wrong approach 1 | the confident specialist (applies domain expertise to wrong problem type) |
| Wrong approach 2 | the hypothesis tester (tests systematically without naming what is being tested) |
| Right question | “Have I seen a problem like this before?” / “What does this remind me of?” |
| Operation Touch | Do you know a related problem?: Touch 1 (experience without name); possibly Touch 1N for name attachment later |
| Sitting down | Must appear — preceded by both wrong approaches exhausted |
| Mystery person appears | Yes (likely) |
| Ordinary life echo | To be determined — the focal character applying the related-problem instinct outside a gate |
| Focal character | To be determined — new or returning from population |
| Emotional beat | The relief of recognition — the moment the solver realises they are not facing something entirely new |
| Foreshadowing to plant | The guild begins to hear about solvers who succeed by “remembering” something from a past gate; the concept of related problems enters the institutional conversation as an anomaly |

---

## NOTES FOR AI — CURRENT SESSION

- Chapter 008 introduces Nantale Namakula, a pharmacist from Kampala, as the new focal character. Her ordinary-life habit of checking the patient record before dispensing — a form of “did you use all the data?” and “can you check the result?” — maps directly onto the gate problem and produces a quiet closure.
- The gate problem is a Grade 2 pharmacy-dispensary layout: order slip, reference chart, verification panel, and multiple drug containers. The correct solution requires reading the chart (the unused datum) and activating the panel (the verification step) — both steps that the specialist and hypothesis tester ignored.
- Dr. Akello (the confident specialist) sorted by chemical category, matched the protocol, and stopped when her domain ran out. The gate mirrored her categorisation and dimmed the chart. The gap between clusters widened — the mirror drawing attention to what she was not looking at.
- The young man (the hypothesis tester) tested twelve configurations systematically but never activated the panel. The gate mirrored each configuration, always showing the panel unactivated. He sat down — but from collapse, not stillness — and the gate did not respond.
- Nantale sat down deliberately, looked at the room (not the containers), saw the chart and panel, cross-referenced, made the correction, placed the tray on the panel, and waited. The gate closed. The sitting down was earned and quiet.
- The chapter demonstrates “can you check the result?” (Touch 1, name attached through the ordinary-life echo when the narration mentions “She had learned to check the result. That was what the waiting was for” — a narrator observation, not a lecture).
- The operation “Do you know a related problem?” is faintly present in Nantale’s recognition of the reference chart as analogous to the cross-reference charts she uses daily, but the chapter’s primary taught operation is “can you check the result?” The related-problem instinct is seeded but not yet given weight.
- The anchor’s notebook page is the first one a protagonist reads before it vanishes, giving the reader a direct look at the anchor’s format: grade, approach type, mirror content, underlined gap, register log. This is a turning point in how the macro mystery is presented.
- The ordinary-life echo shows Nantale checking a warfarin interaction by pulling the patient record — a datum the protocol omitted — and another customer going still as the right question forms. The echo is unobtrusive and directly parallels the gate behaviour.
- The guild’s marginal note “checking” hints that the vocabulary for this operation is trying to surface inside the institution. The anchor’s pages name it already; the guild is still circling.
- For chapter 009, the next target should shift to “Do you know a related problem?” (Touch 1, possibly Name Attachment), using the confident specialist and hypothesis tester wrong approaches again in a different context to show the operation’s cost and reward. The focal character could be another new person in a different city. The ordinary-life echo would show the character drawing on a past experience to solve a current problem, without naming the move.