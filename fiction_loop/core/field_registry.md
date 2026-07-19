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
| `living_document.md` (whole doc) | `refresh_living_doc.py` (Orchestrator step 10, after structural-gate PASS) | **Assembler (step 7 read list — canon context for every chapter)**; Orchestrator user command `show living document`. T-008 removed the Extractor consumer and moved refresh behind the gate, closing rejected-draft pollution |
| arc cast quota (wrong-approach scenes per gate chapter) | `concept_curriculum.md` §9 (declared source of truth) | THREE copies that must change together: assembler.md BEAT QUOTA table + HARD RULE 7 fill-in; `structural_gate.py` `QUOTA_BY_ARC`. Tuning §9 without the copies makes the gate fail chapters the prompt correctly ordered |
| `update_brief.json.process_updates.failure_modes_shown_this_chapter` | Extractor (labels scenes from prose — see open item on "shown") | `structural_gate.py` step 11.5 (counts against arc quota); Updater STEP 3 (→ event card `wrong_approaches_demonstrated`); downstream recency rotation (Assembler picks least-recently-shown) |
| `update_brief.json` gate-consumed booleans (`anchor_update.appeared`, `process_updates.context_demonstrated`, `focal_character.is_new`, `focal_character.life_progression_shown`, `other_entrants[].is_new`) | Extractor | `structural_gate.py` step 11.5 (rules D3/F16, echo, F14, F15) + Updater |
| `prompts/.gate_pass.json` | `structural_gate.py` (written on PASS, deleted on FAIL or gate error) | Orchestrator step 12.0 (`structural_gate.py --verify`). Protects the invariant that state mutates only after a gate PASS on the byte-identical `update_brief.json`. Evidence it can fire: T-009 FAIL/hash-tamper acceptance runs and the ch8 attempt-2 incident it would have stopped |
| forbidden-label narration check (`LabelLeakError`) | `invoke_writer.py`, deriving its label set at runtime from every operation's `process_state.json.failure_modes_shown` + `failure_modes_not_yet_shown` arrays | Orchestrator step-8 error handling. Protects HARD RULE 1; its LAW 5 prevention twin already exists in the Writer prompt's HARD RULES block, so no prompt change was needed. Evidence it fires: T-010 fixture A (`chapters/chapter_008.md`) rejects its three narration labels while treating the italic artifact lines as WARN; fixture B (`chapters/chapter_007.md`) passes |
| `prompts/prose_deficiencies.json` | `invoke_writer.py --check-prose` (structured deterministic prose checks) | Orchestrator revision ladder; `invoke_writer.py --revise`. Transient prompt-stage artifact, never state. T-012 evidence: the ch8 attempt-2 fixture emits label deficiencies and the clean ch7/attempt-3 fixtures emit `[]` |
| `mystery_anchor.json.reader_can_suspect` | Extractor (diffs what chapter prose newly supports against the current `mystery_anchor.json.reader_can_suspect` array) → Updater STEP 5 | Assembler (gate/anchor prompt content), Consistency Checker (A2). Provenance changed by T-008 from the refresh model's living-doc paraphrase to chapter prose + `mystery_anchor.json` |
| `cards/events/*.json.problem_structure` | Extractor SECTION: gate_details → Updater STEP 3 | Assembler ("Gate this chapter" section derives from operation, but closed-gate history is read via `problem_structure` on archived event cards for continuity) |
| `cards/events/*.json.wrong_approaches_demonstrated` | Extractor SECTION: process_updates (`failure_modes_shown_this_chapter`) → Updater STEP 3 | Consistency Checker (C1), Assembler (`failure_modes_not_yet_shown` selection) |
| `cards/events/*.json.correct_approach` | Extractor SECTION: gate_details → Updater STEP 3 | *(no current reader — see note below)* |
| `cards/events/*.json.characters_entered` | Updater STEP 3 (`[focal_character.id]`, single character only) | *(no current reader)* |
| `next_chapter_pointer.failure_mode_to_show` | Extractor (least-recently-LED selection vs `failure_mode_lead_history`; shown-recency tiebreak) → Updater STEP 7 | Consistency Checker (V1, C1); Assembler ("Lead wrong approach" — the featured type the anchor observes); Extractor next chapter (copies it into `lead_failure_mode`) |
| `update_brief.json.process_updates.lead_failure_mode` | Extractor (verbatim copy of the pointer that steered this chapter) | Updater STEP 7 (archives to `failure_mode_lead_history`) |
| `master_state.json.failure_mode_lead_history` | Updater STEP 7 (append per gate chapter; seeded ch 001–004 by hand 2026-07-04) | Extractor (`failure_mode_to_show` selection — least recently led). Exists because shown-recency saturates when arc quota = pool size (arc 1: 3 of 3 → permanent tie; executor led ch 1–3 undetected) |
| `master_state.json.arc_current` | Source of truth: `arcs/arc_N_summary.md`, written once per arc_transition by Updater STEP 9. This field is the registered cached copy, invariant `arc_current = 1 + count(summaries)`. Producers: `tools/init_state.py` (seed 1), Updater STEP 9 (advance), `analyst.py --repair` (deterministic reconcile). | Fetcher (curriculum arc section); Assembler (closing/opening arc block); Extractor (`arc_effective` deficit window); Orchestrator (status read); Analyst (invariant check). Case law T-006: it stuck at 1 after ch7 because no advancing producer existed. |
| `mystery_anchor.json.observable_log[].manifestation` | Extractor (`anchor_update.manifestation`, drawn from the assembled prompt's chosen form) → Updater (observable_log append + "Last appeared" summary) | Assembler (anchor section: "pick one, DIFFERENT from the last entry's manifestation"); Consistency Checker C3b at step 7.5 (anti-formula backstop — moved out of pre-assembly C3 2026-07-10 after the ch-006 SpecGap block: the pre-pass has no manifestation to compare, Assembler chooses it at step 7) |
| `chapter_type_contract.md` | (static, hand-authored) | Extractor, Updater, Consistency Checker (branch guards) |

## Known orphans / open items

- **"Shown" is undefined for `failure_modes_shown_this_chapter`** (found 2026-07-04,
  ch4 v2): the structural gate counts the Extractor's *labels*, not scenes. A solver
  whose behavior blends two approach types gets ONE label (ch4 v2's first solver blended
  executor + system-builder → labeled system builder only), so 3 written scenes can
  count as 2 (false FAIL), and a mislabel corrupts the least-recently-shown rotation
  that selects future chapters' failure modes. Arc 3–4's "third scene may be compressed"
  sharpens the question. Needs one written definition (in extractor.md + gate) of what
  counts as a shown failure mode — at latest before arc 3.
- **F14 gate check is null-blind** (found 2026-07-04): `structural_gate.py` fires only
  on `life_progression_shown is False`. The Extractor currently emits `null` (ch4 brief).
  Required semantics, not yet written into extractor.md: for a RETURNING focal the
  Extractor must emit `true`/`false` (never null); `null` is only valid when
  `is_new: true`. Until then a returning focal with no progression slips the gate.
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
