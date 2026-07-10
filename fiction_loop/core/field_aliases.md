# FIELD ALIASES

Maintainer reference, not read by agents at chapter-generation time.

Canonical field names and shapes live in the card schemas
(`fiction_loop/cards/*/_schema.json`). Where an internal document
(`update_brief.json`, an agent spec) uses a different name for the same data, or a
different value shape (e.g. string enum vs. boolean) for the same concept, it must be
listed here.

**Rule for editors:** before renaming a field in any agent spec or in
`update_brief.json`, check this table. If the rename creates a new alias, add a row. If
a field's name or shape drifts from its schema/consumer without a row here, that's a
producer/consumer mismatch bug — the exact failure mode this table exists to prevent.

| Internal name | Used in | Canonical name / shape | Canonical location |
|---|---|---|---|
| `process_updates.failure_modes_shown_this_chapter` | `update_brief.json`, `extractor.md` SECTION: process_updates, `updater.md` STEP 2/3 | `wrong_approaches_demonstrated` | `cards/events/_schema.json` |
| `comprehension_state[operation_id]` value | `extractor.md`, `assembler.md` | string enum: `"encountered" \| "understood" \| "owned"` (never boolean) | `cards/characters/_schema.json` |
| gate-chapter "Grade" | `assembler.md` "Gate this chapter" section | arc-level Gate Grade range (concept_curriculum.md Section 5 Arc Breakdown) — **not** the operation's own `difficulty_rating` | `core/concept_curriculum.md` §5 |
| character's "city" | `assembler.md` returning-character prose | sourced via `location_id` on the character card → the location card's `name`, not a `city` field on the character card | `cards/characters/_schema.json` (`location_id`), `cards/locations/_schema.json` (`name`) |
| "1N" (map notation) | `concept_curriculum.md` §7, style_contract §3 | NOT a separate integer touch — `name_due`/`name_attached` flag on the touch numbered `name_at_touch` (owner D1/F6) | `cards/concept/_schema.json` (`name_at_touch`, `name_attached`) |
| echo "context" | `extractor.md`, `assembler.md`, C4 | enum value from `process_state.json` `context_enum` — never free text (owner D4) | `state/process_state.json` (`context_enum`) |
| `secondary_touch_updates[].touch` | `update_brief.json`, `extractor.md`, `updater.md` STEP 2B | same semantics as `process_updates.new_touch` — applied only when `verified: true` | `cards/concept/_schema.json` (`current_touch`) |
| anchor "manifestation" | `update_brief.json`, `assembler.md`, C3b (post-assembly) | enum: `seen \| traces \| bystander_mention \| notebook_page \| none`; recorded on `observable_log` entries | `state/mystery_anchor.json` (`observable_log[].manifestation`) |
| `canonical_problem_structure` / `canonical_correct_approach` | concept cards, `assembler.md` | operation-level TEMPLATES — distinct from the event card's `problem_structure`/`correct_approach`, which are per-chapter instance records extracted post-hoc | `cards/concept/_schema.json` vs `cards/events/_schema.json` |
