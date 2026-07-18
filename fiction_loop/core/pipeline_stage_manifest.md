# PIPELINE STAGE DATA-AVAILABILITY MANIFEST

Maintainer reference, not read by agents at chapter-generation time.

Before writing or editing any check in `consistency_checker.md`, or any read in another
agent spec, confirm here that the field you're checking is actually guaranteed to exist
at the step your agent runs. Step numbers match `orchestrator.md`'s STEPS section.
Step labels are retained, while execution order is 8→9→11→11.5→10→12; see
`orchestrator.md` for the authoritative order.

| Orchestrator step | Agent | Produces | Guaranteed available at this step |
|---|---|---|---|
| 4 | Fetcher | `fetched_fields.md` | pointer/card/state data per `fetcher.md`'s per-type fetch logic — **no chapter prose exists yet** |
| 5 | Consistency Checker | `consistency_report.md` | `fetched_fields.md`, `style_contract.md` — runs **before** Assembler and Writer. Any check here may only reference pointer/state/card data, never prose or the assembled prompt. |
| 7 | Assembler | `assembled_prompt.md` | `fetched_fields.md`, `consistency_report.md`, `style_contract.md` (incl. §4B, §5), `world_rules.md` (incl. §5 mirror rows), `correspondence_map.md` §5, `character_naming.md`, concept card canonical fields |
| 7.5 | Consistency Checker (post-assembly pass) | post-assembly FLAG line | `assembled_prompt.md`, `process_state.json`, `mystery_anchor.json` — V3, C4, A2b, C3b run HERE, not at step 5 (their inputs are Assembler outputs) |
| 8 | Writer | `chapter_draft.md` | **chapter prose now exists** for the first time in the pipeline |
| 9 | (bash copy) | `chapters/chapter_[NNN].md` | prose persisted |
| 10 | `refresh_living_doc.py` | updated `living_document.md` | runs after structural-gate PASS; produces prose-derived narrative state for downstream Updater reference |
| 11 | Extractor | `update_brief.json` | prose (chapter file), `assembled_prompt.md`, `master_state.json`, `process_state.json`, `mystery_anchor.json`, `concept_curriculum.md` — this is the **first and only** stage prose is read by anything other than the Writer |
| 12 | Updater | card/state file writes | `update_brief.json` only — never reads prose (see `updater.md` CRITICAL RULES) |

## Why this exists

Consistency Checker runs at step 5, before Assembler (step 7) and Writer (step 8). A
check written against prose-derived data (e.g. "is the prose's chapter ordering
correct") cannot run at step 5 — that data doesn't exist until step 8. Any such check
must instead be reframed against the pointer/state data that *is* real at step 5 (e.g.
`next_chapter_pointer.failure_mode_to_show`, as V1 does).

The same reasoning bounds `updater.md`: it must never assume a step like "Orchestrator
confirms arc is complete" ran before it, because no such step exists in
`orchestrator.md`'s STEPS — Updater's own STEP 9 is conditioned purely on
`chapter_type = arc_transition`, not on any upstream confirmation.
