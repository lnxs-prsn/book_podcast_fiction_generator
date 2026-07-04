# PRODUCER / CONSUMER FIELD REGISTRY

Maintainer reference, not read by agents at chapter-generation time.

Every schema field or document below must have both a producer (who writes it) and a
consumer (who reads it) listed. A field with a producer and no consumer is dead
work — it costs LLM generation and file-write time every chapter for no downstream
effect. A field with a consumer and no producer will always read as empty/default. Both
are bugs; add a row here whenever a new field is introduced, and check for an orphan
before merging.

| Field / document | Producer | Consumer |
|---|---|---|
| `living_document.md` (whole doc) | `refresh_living_doc.py` (Orchestrator step 10) | Extractor (`extractor.md` SECTION: reader_can_suspect_update) |
| `mystery_anchor.json.reader_can_suspect` | Extractor (diffs living_document.md) → Updater STEP 5 | Assembler (gate/anchor prompt content), Consistency Checker (A2) |
| `cards/events/*.json.problem_structure` | Extractor SECTION: gate_details → Updater STEP 3 | Assembler ("Gate this chapter" section derives from operation, but closed-gate history is read via `problem_structure` on archived event cards for continuity) |
| `cards/events/*.json.wrong_approaches_demonstrated` | Extractor SECTION: process_updates (`failure_modes_shown_this_chapter`) → Updater STEP 3 | Consistency Checker (C1), Assembler (`failure_modes_not_yet_shown` selection) |
| `cards/events/*.json.correct_approach` | Extractor SECTION: gate_details → Updater STEP 3 | *(no current reader — see note below)* |
| `cards/events/*.json.characters_entered` | Updater STEP 3 (`[focal_character.id]`, single character only) | *(no current reader)* |
| `next_chapter_pointer.failure_mode_to_show` | Extractor (DECISION LOGIC) → Updater STEP 7 | Consistency Checker (V1, C1) |
| `chapter_type_contract.md` | (static, hand-authored) | Extractor, Updater, Consistency Checker (branch guards) |

## Known orphans / open items

- **`correct_approach`** — RESOLVED (owner decision D6, 2026-07-02, see
  `../human_decision.md`): keep the field and wire its consumer — the Assembler reads
  it for return-to-character continuity. Not yet implemented; tracked as part of
  `specs/pipeline_fixes.spec.md` (D6/F15 cluster).
- **`characters_entered`** — RESOLVED (owner decision D6, 2026-07-02): becomes a real
  multi-entry list. Every gate has a focal solver but chapters show multiple named
  solvers (per world_rules productive-failure structure); each *named* solver gets at
  least a stub character card, and the return logic may select past failed solvers.
  The story is an ensemble with no single protagonist — now a stated design rule.
  Not yet implemented; tracked in `specs/pipeline_fixes.spec.md`.
- **`prerequisite`** (operation dependency graph, needed by Consistency Checker's CR3) —
  no such field exists in `cards/concept/_schema.json` or `concept_curriculum.md`. This
  blocks CR3 entirely. Deciding the prerequisite structure and authoring it for all 24
  operations is a content/design decision, not a wiring fix.
- **`correspondence_map.md` Section 5 ("Ordinary Life Echo")** — **RESOLVED and
  EXECUTED (2026-07-02).** The two merged rows were split (new rows authored for
  "Here is a problem related to yours and solved before" and "Inventor's Paradox",
  written against the source text — the recall/use distinction and the "more ambitious
  plan" passage were pulled from the epub during drafting, per the sourcing rule) and
  all Section 5 labels were renamed to match curriculum §3's canonical names verbatim
  (rename chosen over an alias table, owner-approved via
  `../content_for_review.md`). Section 5 now has 24 rows for 24 operations; a literal
  name-keyed lookup works. Note: Section 4 still has one merged row (Generalisation /
  Inventor's Paradox) — harmless today since nothing does a name-keyed lookup on §4,
  but recorded here in case that changes.


## RULE-CHANGE AUDIT — behavioral rules have consumers too

Schema fields aren't the only things with producers and consumers: BEHAVIORAL RULES
(checks, scope walls, cadence policies, delivery channels) are consumed by other
documents' instructions. When a rule changes, its old semantics can survive in a
consumer and silently contradict the new rule.

**The procedure, after ANY rule change:** ask "who consumed the old rule?" —
grep the rule's key phrases across agents/, core/, tools/, RUN.md; for every hit,
either update it or record here why it's exempt. Do this in the same sitting as the
rule change — the bug class is born precisely in the gap between "rule changed" and
"consumers audited later".

**Case law (all found in one self-audit, 2026-07-04 — all were fixes made in
response-mode where the audit step was skipped):**
1. C3 inverted (anchor must appear) → assembler step 7 still said "anchor too
   frequent: set to No" — would have deleted the anchor from a gate chapter.
2. Scope wall declared ("nothing outside fiction_loop/") → later-added git commit
   steps and .env reads violated it — a rule-literal agent would refuse to commit.
3. Extractor's curriculum read removed → its role as the wrong-approach NAME
   dictionary went with it — invented labels would break C1 string matching.
4. Orchestrator "reads exactly one file" claim went stale as conduct/analyst reads
   were added.
