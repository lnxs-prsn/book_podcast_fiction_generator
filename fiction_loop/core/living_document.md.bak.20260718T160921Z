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
| Last updated | After Chapter 7 |
| Last chapter completed | 7 |
| Current arc | Arc 2 — Gate Grade 2–3 |
| Active focal characters | Yejide Adeyemi, Kwabena Asante, Wanjiku Mwangi, Fatou Ndiaye |
| Mystery person last appeared | Chapter 7 (Accra guildhall archives — junior clerk finds five torn notebook pages from gates in Achimota, Kumasi, Lagos, and Dakar; pages record solver approaches using terms “executor,” “system builder,” “information gatherer”; pages are copied and filed away without further action) |
| Macro mystery evidence count | 6 |

---

## PROCESS STATE SUMMARY
*Compressed view. Full detail in /state/process_state.json.*

| Operation | Touch | Last Context | Next Due |
|---|---|---|---|
| Identify unknown / data / condition | owned | — | Arc 2 — Touch 3 |
| What is missing (absence over presence) | owned | — | Arc 2 — Touch 3 |
| Separate parts of condition | 1 | Chapter 004 | Chapter 7 — Touch 2 |
| Look at the unknown | 1 | Chapter 005 | Chapter 7 — Touch 2 |

All other operations are at touch 0 and will be introduced in later arcs as scheduled in /state/process_state.json.

---

## FAILURE MODES NOT YET SHOWN

*All wrong approach types must appear across Arcs 1-4. Types introduced per arc per concept_curriculum.md.*

**Arc 2 (introduced as operations expand):**
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
| char_001 | Yejide Adeyemi | Fabric Checker / Seamstress | Lagos | 2 (Touch 2) | Chapter 7 |
| char_002 | Kwabena Asante | Dispatch Clerk (Promoted) | Accra | 2 (Touch 2) | Chapter 7 |
| char_002a | Ama Serwah | Plantain Seller | Accra | 1 (Touch 1) | Chapter 2 |
| char_003a | Kojo Acheampong | Depot Supervisor | Accra | 1 (Touch 1) | Chapter 3 |
| char_003b | Akosua Osei | Cleaner | Accra | 1 (Touch 1) | Chapter 3 |
| char_004 | Wanjiku Mwangi | Hospital Records Officer | Nairobi | 2 (Touch 2) | Chapter 7 |
| char_005 | Fatou Ndiaye | Land Registry Clerk | Dakar | 1 (Touch 1) | Chapter 7 |

---

## MYSTERY PERSON THREAD
*Observable log summary. Full detail in /state/mystery_anchor.json.*

Appearances: 7  
Last location: Accra guildhall archives — five torn notebook pages recovered from gate interiors (Achimota, Kumasi, Lagos, Dakar) and filed by a junior clerk under “Unidentified Documents—Gates.” Pages record solver approaches using the anchor’s consistent terminology (executor, system builder, information gatherer) with register timestamps. The clerk photocopied the pages, sent them to the senior coordinator, and they were shelved unread.  
Reader can suspect: The anchor has been present at every major gate event across cities, leaving physical records that the guild is not yet equipped to interpret. The terms “executor,” “system builder,” “information gatherer” are the anchor’s diagnostic categories for wrong approaches — and the guild, who has not yet recognised these patterns, is losing trained solvers at an accelerating rate.

---

## MACRO MYSTERY EVIDENCE
*What the reader can suspect but not confirm.*

Evidence count: 6  
Current state: The discovery of the five notebook pages establishes that the anchor has been systematically observing multiple gates across different cities and recording solver mental frames in identical notation from the beginning. None of the pages have been studied; the guild’s internal systems file them as anomalies. Meanwhile, the guild’s data shows that untrained solvers are closing Grade 2 gates at a far higher rate than guild-trained ones — and none of the twelve deaths are among the untrained. The anchor’s documentation and the guild’s statistics converge on the same truth: the guild trains solvers in a method that works only when the problem matches the method, and the gates are now presenting problems that require a new mental move.

---

## ACTIVE FORESHADOWING

- Kuuku Dadzie’s failure in the Dakar gate demonstrates the guild method’s limits: thorough cataloguing and spatial reorganisation produce no response when the gate’s solution lies in a relationship between objects, not in the objects themselves — and recognising that relationship requires recalling a prior gate, which the method does not teach.
- The unnamed woman who closes the Dakar gate does so by recalling a Grade 1 gate from Kumasi two weeks earlier — the first clear instance of “Do you know a related problem?” (Touch 1) appearing in the story. She sits down, studies the table as a whole, finds the structural resemblance, and the gate closes. The guild will never know.
- Yaw Boateng’s realisation — “Maybe we’re training them wrong” — and the guild’s internal review showing a mortality split between trained and untrained solvers signals an institutional crisis that will deepen as more solvers emerge outside the guild.
- The junior clerk’s photocopied pages reach the senior coordinator’s office and are filed without review — a time-delay fuse; the reader knows those records contain the diagnosis the guild needs and is not yet capable of reading.
- Yejide, Kwabena, Wanjiku, and Fatou are shown in ordinary-life echoes at the chapter’s end, each applying gate-honed perception to their work without naming the connection — they are the silent population of solvers the guild cannot track, whose accumulated instinct will eventually overtake the institutions.
- The arc closes with the phrase “The next gate opened at dawn,” establishing a world where the rate of gate events continues to accelerate and the guild’s window for adapting its training is narrowing.

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

- Chapter 7 closed Arc 1 and opened Arc 2. All Arc 1 wrong‐approach types (executor, system builder, information gatherer) have now been demonstrated with distinctive gate signatures and mirror content.
- The “Do you know a related problem?” operation was experienced — not named — through the unnamed solver in the Dakar gate. This is Touch 1. The gate rewarded structural recall: the same relationship between objects that had appeared in a Kumasi Grade 1 gate was the key to the Dakar Grade 2 gate. The solver did not articulate the principle; she simply remembered and the gate closed.
- Kuuku Dadzie’s failure models the guild’s current training ceiling: cataloguing, arranging, and pattern-matching within the present data set produces no effect when the required move is to reach outside the present gate entirely.
- The guild’s internal data now shows a statistically impossible mortality split — all twelve dead are guild-trained — but the guild has no conceptual framework for why. The answer (the missing operation is “what does this resemble?”) is already recorded in the anchor’s pages, which are sitting unread in a file in Accra.
- The ordinary-life echoes at the end of the chapter are subtle: Yejide, Kwabena, Wanjiku, and Fatou each solve a real-world problem by perceiving what is missing, without acknowledging any connection to their gate experiences. The reader sees the instinct spreading; the characters do not.
- The junior clerk’s discovery of the five pages is a new macro-mystery milestone. The pages explicitly name the wrong-approach types that the curriculum’s Arc 1 and Arc 2 failure sequences are built around. The terms “executor,” “system builder,” “information gatherer” are now in-world textual artefacts, visible to characters who might eventually understand them.
- Next chapter: introduce the “confident specialist” and “hypothesis tester” wrong approaches, and give the reader a focal character who experiences the “related problem” instinct. The name may be attached (Touch 1N) if the experience is complete by the chapter’s end — otherwise defer to chapter 009. The sitting down must be fully earned.
- The “empty hook” physical emblem remains available for reuse in later arcs, but the new structural emblem for Arc 2 is likely to be a recognisable configuration of objects that repeats across gates.
- African names only. No Arabic names. Continue the established pattern of ordinary-life echoes within the same chapter or the one that follows.