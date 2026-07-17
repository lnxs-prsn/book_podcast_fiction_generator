# PIPELINE FIXES SPEC — 2026-07 AUDIT

Findings from a full read of `fiction_loop/` cross-checked against `src/`, the Pólya
source text (`books/…epub` — all 24 curriculum operations verified present in the
source; no hallucinated operations), and a live smoke test of the bridge scripts.

Ordered by severity: **BLOCKER** (chapter 1 cannot be produced at all), **LOOP-BREAKER**
(chapter 1 may work, the loop corrupts or stalls within a few chapters), **QUALITY /
DRIFT** (works, but violates the project's own design intent).

Each fix states: evidence, the change, and where an owner call was required.

> **STATUS 2026-07-03: F1–F17 ARE APPLIED** (agent specs, schemas, state init,
> tools, prerequisite graph, prevention layer). This file is now the record of
> why, not a to-do list. Remaining open: the deterministic code layer
> (deterministic_pipeline / assembler_template as Python).

---

## BLOCKERS

### F1 — Both bridge scripts drop `OPENROUTER_API_KEY` (code bug, verified live)

`invoke_writer.py` line 101 and `refresh_living_doc.py` line 79:

```python
config = {**config, **{k: v for k, v in env.items() if k in config}}
```

`resolve_from_env()` returns `{"api_key": ...}` when `OPENROUTER_API_KEY` is set, but
`load_config()` never puts an `api_key` key into the config dict (the TOML has none;
`"api_key"` is only in the *known-keys* set). So `k in config` is always False for
`api_key` and the key is discarded. `create_transport(api_key=config.get("api_key"))`
then receives `None` → `LLMConfigError: api_key is required` **even when the env var is
set**. Verified by running the merge with a dummy key: `merged api_key: None`.

**Fix:** in both scripts replace the filtered merge with `config = {**config, **env}`.
`resolve_from_env()` already only returns non-empty values and env-wins-over-config is
its documented contract (see its docstring). The extra keys it may add (`max_tokens`,
`retry_after_override`) are harmless — config is already validated by this point.

**Acceptance:** `OPENROUTER_API_KEY=x PYTHONPATH=src .venv/bin/python
fiction_loop/tools/invoke_writer.py …` gets past transport creation (fails later at the
HTTP call with an auth error, not at `create_transport`).

### F2 — No initialization was ever performed; no init procedure exists in fiction_loop

`build_specs.md` INITIALIZATION SEQUENCE says a human fills `master_state.json`,
`process_state.json`, `mystery_anchor.json`, and creates concept cards before the first
run. None of that happened:

- `master_state.json` — all `"[ ]"` placeholders (`story_title`, `operation_due`, …).
- `process_state.json` — literally the template: one operation keyed `"[operation_id]"`.
- `mystery_anchor.json.hidden_coherence` — all `"[ ]"`.
- `cards/concept/`, `cards/locations/`, `cards/characters/` — only `_schema.json`.
- No canonical `operation_id` exists anywhere. State files key by `[operation_id]`,
  concept cards are named `[operation_id].json`, but the curriculum names operations by
  long prose strings ("Identify unknown / data / condition"). Nothing maps one to the
  other.

**Fix (two parts):**

1. **New doc `core/operation_registry.md`** — one row per operation in
   `concept_curriculum.md` §3 (there are **24**; note `correspondence_map.md` §8's "23"
   and `assembler_template.spec.md`'s "23" are both miscounts):
   `operation_id` (snake_case, e.g. `op_identify_unknown`) | curriculum §3 name |
   correspondence_map §4 label | correspondence_map §5 label | arc introduced |
   difficulty. This registry also becomes the alias table `field_registry.md` left as an
   open recommendation for §5's non-matching labels.

2. **New deterministic script `tools/init_state.py`** (no LLM). Reads the registry +
   curriculum and writes:
   - `state/process_state.json`: all 24 operations at `current_touch: 0`, with
     `failure_modes_not_yet_shown` seeded from curriculum §4's per-arc wrong-approach
     sequences and `contexts_not_yet_demonstrated` seeded from correspondence_map §5
     domains (after the §5 row-split lands — see field_registry.md Known orphans).
     Seeding at init **replaces** the Extractor's runtime `failure_modes_seed`
     mechanism (extractor.md SECTION: process_updates, updater.md STEP 2) — delete
     that field once init seeding exists; one seeding path, not two.
   - `cards/concept/[operation_id].json`: one card per operation, `physical_anchor`
     left `"[ ]"` for the human authoring pass.
   - `state/master_state.json`: `chapter_count: 0`, `arc_current: 1`, and a first
     `next_chapter_pointer` consistent with F7's reconciliation below.
   - Idempotency guard: refuse to overwrite any file whose placeholders are already
     filled.

3. **Human authoring pass (content, cannot be scripted):** `physical_anchor` per
   operation (partial source: style_contract §1 Rule 2 table; verify wording against
   the Pólya text per specs/README's sourcing rule), `hidden_coherence`, `story_title`
   / `genre` / `source_material`.

**Acceptance:** `grep -r '\[ \]' fiction_loop/state/` returns nothing;
`jq keys state/process_state.json.operations | length` = 24; every registry row has a
concept card.

### F3 — Documented invocation uses an interpreter that lacks the dependencies

`writer.md`, `orchestrator.md` step 10, and `INTEGRATION_SPECS.md` all say
`PYTHONPATH=src python …`. On this machine bare `python` (and the root `./.venv`) lacks
`requests`; only `.venv` has the pipeline deps. Verified: root venv →
`ModuleNotFoundError: requests`; `.venv` → runs.

**Fix:** change all three docs to `PYTHONPATH=src .venv/bin/python …` (or a
`uv run --project src` form). One canonical command string, quoted identically in all
three places.

---

## LOOP-BREAKERS

### F4 — `char_id` is computed but never persisted → return_to_character chapters cannot run

`extractor.md` DECISION LOGIC Condition 2 produces `char_id` (line 303), but the
`next_chapter_pointer` output field list (lines 246–255) omits it, as do the pointer
blocks in `master_state.json` and `update_brief.json`. `orchestrator.md` line 66 then
expects "char_id from next_chapter_pointer" — a field that never exists. Separately,
orchestrator line 56 encodes it as a combined string (`return_to_character:[char_id]`)
— a second, incompatible representation.

**Fix:** add `"char_id": null` to the pointer schema in `master_state.json`,
`update_brief.json`, extractor's SECTION: next_chapter_pointer, and updater STEP 7.
Rule: non-null iff `type == "return_to_character"`. Drop the combined-string form from
orchestrator.md line 56 (valid values become the four bare types). Add a row to
`core/field_aliases.md` retiring the old form.

### F5 — DECISION LOGIC has no fallback and no path past touch 2; anchor scheduling is starved

Three separate defects in `extractor.md` DECISION LOGIC:

1. **No fallback.** "Use the first condition that is true" — if none is true (e.g. all
   arc ops at touch 1, none with `chapters_since_last_touch >= 3`, anchor appeared
   recently), the pointer is undefined and the loop halts.
2. **Touch ceiling.** Condition 2 only schedules `touch_due: 2`. The spaced-repetition
   map (curriculum §7) schedules touches 3 and 4, and compression triggers at touch 3
   (`compressible_at_touch: 3`) — unreachable as written. Operations stall at 2 forever,
   which also permanently blocks Condition 4's arc-transition test from being the only
   thing left, i.e. the arc can transition while the curriculum is unfinished by its own
   map.
3. **Anchor starvation.** Condition 3 (anchor interlude) is shadowed by Conditions 1–2,
   which are true whenever any operation is due — nearly always. And `anchor_appears:
   true` is only ever set for interludes, so the design's "anchor appears briefly at a
   gate exterior every ≤5 chapters" (world_rules §3, consistency check C3, assembler's
   "Anchor character appearance" section, living_document's chapter-1 target) can never
   be scheduled by this logic.

**Fix (RESOLVED by owner, 2026-07-02 — see `human_decision.md` D1 and D3):**

The scheduling model is now **map-driven with a chronological gate**:

- The spaced-repetition map (curriculum §7) becomes machine-readable (part of the F2
  operation registry: per operation, per arc, target touch). The scheduler picks the
  operation with the largest deficit between its target touch for `arc_current` and
  its `current_touch` (tie-break: registry/process order).
- **Chronological gate (owner's teaching model):** an operation may not receive its
  first touch until its `prerequisite` operation (F13/CR3 graph — now decided, will be
  authored) is "clear": experienced, named, and applied once (touch ≥ 2). The process
  is cumulative — step N+1 only begins once step N flows.
- **Nothing is ever dropped:** every cleared operation joins a cumulative
  "apply naturally" list included in every subsequent chapter's assembled prompt.
  The Extractor also records *ambient* uses it observes in prose (they inform, but do
  not replace, the map's schedule).
- **Touches 3–4 are scheduled (not merely hoped for) but may be co-hosted** (owner
  refinement, 2026-07-02): the pointer gains a `secondary_touches` list (max 2):
  `[{ operation_id, touch, carrier }]` where `carrier` is a returning character who
  owns the operation or `"experienced_stranger"` (a newcomer with off-page gate
  history — world-coherent and simultaneously satisfies F15's newcomer rule). The
  scheduler fills secondary slots from map deficits of *cleared* operations only.
  Preferred dramatic form: the carrier applies the owned operation competently, then
  fails the chapter's NEW operation — serving as the productive-failure structure's
  first solver. The Extractor verifies each scheduled secondary touch actually
  appeared in prose (and which character carried it) before the Updater counts it;
  unverified secondaries return to the deficit pool, not silently counted.
  Compression stays at touch 3 (or the operation's final scheduled touch if lower —
  see difficulty scaling below), after that touch is verified.
- **Compression levers (owner decision D9, 2026-07-02 — all four adopted; see
  `human_decision.md`):**
  1. *Echo-carried touch*: the pointer gains one `echo_touch` slot — the mandatory
     ordinary-life echo may carry a reinforcement touch for a different cleared
     operation, carried by a returning character; doubles as the F14 life-progression
     scene. Sanctioned by style_contract §3's touch-2 definition.
  2. *Difficulty-scaled touch targets*: map targets become easy (2–3) → 2 touches,
     medium (4–5) → 3, hard (6–8) → 4. Applied as column edits in the machine-readable
     map when the F2 registry is authored (~96 → ~75 touch-events).
  3. *Phase clusters*: when one solving sequence chains sibling operations in process
     order, the Extractor may verify one touch per sibling actually exercised —
     subject to the same prose-verification rule as secondaries.
  4. *Structural absorption*: `anchor_interlude` and `arc_transition` may carry
     ambient reinforcement (never new operations). **Amends
     `chapter_type_contract.md`:** `process_updates` for those two types changes from
     strictly null to an optional reinforcement-only list; the guards in Extractor /
     Updater / Consistency Checker change accordingly.
  **Hard cap:** 4 verified touch-events per chapter (1 formal + 2 in-gate + 1 echo).
  Unplaceable touches return to the pool — never forced.
  Projection: ~75 touch-events at ~4/chapter ≈ 19–22 teaching chapters + ~4–6
  structural chapters → **~23–28 total** (owner target: 20–30).
- Fallback when no deficit exists and no other condition fires: pick the arc_current
  operation with the lowest `current_touch` (tie-break: registry order).
- **Anchor scheduling is deleted from the cadence logic entirely** — superseded by
  F16 (she appears in every gate chapter; the pointer's `anchor_appears` is `true` for
  every gate-bearing chapter type by rule, and C3 inverts).

### F6 — The 1N touch level has no representation in the state model

Curriculum §7 and style_contract §3 define five levels: 1, 1N, 2, 3, 4 — where 1N
("name attached") is a distinct teaching event, and some operations *start* at 1N
(e.g. "What is missing" in Arc 1). The state model has only an integer `current_touch`,
and CR1 checks `touch_due == current_touch + 1`. Integer arithmetic cannot express
"touch 1 happened, 1N has not," so either the name-attachment event is lost or every
count downstream (spacing, compression, CR1) is off by one for ops whose map includes
a separate 1N.

**Fix:** keep integer `current_touch`; add `name_attached: bool` to the concept-card /
process_state operation object and `name_due: bool` to `next_chapter_pointer`.
Semantics: "1N" in the map = the touch at which `name_due` is true (same integer touch
as the experience for ops whose map cell is `1N` at first appearance). Extractor sets
`name_attached` from the prose (the narrator-label sentence is present); Assembler
selects the delivery channel (style_contract §4) from `name_due` instead of inferring
from touch number. Add both fields to `field_aliases.md`.

### F7 — living_document.md and the state JSONs are two sources of truth that already disagree

`living_document.md` duplicates PROCESS STATE SUMMARY, POPULATION INDEX, and NEXT
CHAPTER TARGET — all owned by the Updater in the JSONs — and is rewritten *wholesale by
an LLM* every chapter (`refresh_living_doc.py`). The two will diverge, and are already
contradictory at init:

- Living doc NEXT CHAPTER TARGET: "Mystery person appears: **Yes**" vs
  `master_state.next_chapter_pointer.anchor_appears: false`.
- Living doc plans **four** operations touched in chapter 1 vs consistency check V2
  (flag on >1 new operation) and DECISION LOGIC (schedules exactly one `operation_due`).

**Fix (mechanical part):** `refresh_living_doc.py` should inject the current
`master_state.json` + `process_state.json` into the update prompt with the instruction
that PROCESS STATE SUMMARY / POPULATION INDEX / NEXT CHAPTER TARGET are **copied from
this data, never inferred from prose**. That demotes the living doc to a derived
narrative view, which is what `field_registry.md` already lists as its only consumed
role (reader_can_suspect diffing + narrative context).

**Chapter-1 reconciliation (RESOLVED by owner, 2026-07-02 — see `human_decision.md`
D2):** the living-document plan wins, per the owner's directive that pacing follows
Pólya's own teaching guidance (the understanding phase is one gestalt) and per D3
(the anchor appears in every gate chapter). Concretely: pointer becomes
`operation_due: op_what_is_missing`, `touch_due: 1`, `anchor_appears: true`; the other
three phase-1 operations appear as experience-only background and are **not** counted
as touches in state; check V2 is reworded to count the formal `operation_due` only.

### F8 — Consistency checks reference data that does not exist at step 5

`pipeline_stage_manifest.md` states checks may only use fetched/state data, but:

- **V1, C1** need `next_chapter_pointer` — `fetcher.md` only fetches it for
  `new_focal_character`. Fix: fetch the pointer for **all** chapter types.
- **CR2** needs `difficulty_rating` — absent from fetcher's OUTPUT FORMAT for
  operations. Fix: add it to the per-operation fetched fields.
- **C4** compares against "the ordinary_life_echo context in fetched fields" — the echo
  context is *chosen by the Assembler* at step 7 from correspondence_map §5; it does not
  exist at step 5 in any file. **V3** checks "operations to use naturally" — a list the
  Assembler builds at step 7. Fix: split the checker into the existing step-5 mechanical
  pass and a new step 7.5 post-assembly pass (reads `assembled_prompt.md`; runs V3, A2,
  C4). This matches `deterministic_pipeline.spec.md`'s existing decision to keep V3/A2
  as a separate small LLM call. Update the stage manifest table accordingly.
  **C4 upgrade (owner decision D4, 2026-07-02):** echo contexts become a fixed
  pick-list (enum seeded from correspondence_map §5's domain column; add the enum to
  the concept-card schema and `field_aliases.md`). The Extractor classifies each echo
  into one enum value; C4 becomes exact equality on enum values — the paraphrase
  limitation documented in `deterministic_pipeline.spec.md` is thereby closed, not
  merely tolerated.

### F9 — Updater STEP 2 reads a concept card that nothing creates

`cards/concept/_schema.json` says cards are "created by human during init or by
Updater," but no Updater step creates one — STEP 2 starts with "Read
/cards/concept/[operation_id].json." With F2's init creating all 24 cards this becomes
consistent; still add a guard to STEP 2: if the card is missing, report
`MISSING: concept card [operation_id]` in STEP 10 instead of failing silently.

### F10 — Living-doc refresh will start truncating within a few chapters

`call_api()` uses `api_default_max_tokens_update` if set, else
`expected_output_tokens_update` as the payload `max_tokens`
(`src/novel_pipeline/api.py` lines 216–222). The TOML sets
`expected_output_tokens_update = 3000` and no `api_default_max_tokens_update`. The
living doc is already ~1,500 words (≈2,000+ tokens) at init and grows every chapter
(population index, foreshadowing, evidence log) → output hits the 3,000-token cap →
truncated doc → `LivingDocValidationError` on every subsequent refresh.

**Fix:** add `api_default_max_tokens_update = 8000` to `pipeline_config.toml` and raise
`expected_output_tokens_update` to 4000 so the cost pre-flight estimate stays honest.

---

## QUALITY / DRIFT

### F11 — The Writer never sees the mirror-writing or notebook-voice rules

The assembled-prompt templates (assembler.md) include only style_contract §1 Rules 1–3
and §6 (never list), and world_rules §4. The Writer therefore never receives:

- style_contract **§4B "WRITING THE MIRROR"** — which the contract itself calls "the
  hardest element to write correctly";
- style_contract **§5 mystery-person notebook format** — required whenever
  `anchor_appears` is true and for every interlude;
- world_rules **§5 register tables / per-approach mirror content** — the chapter's
  wrong approaches each have a specified gate signature and mirror content that the
  prose "must render precisely" (style_contract §4B), but the Writer is never told
  what they are.

**Fix:** extend the assembled_prompt structure: always include §4B verbatim; include §5
notebook format when anchor appears; include, per selected wrong approach, that
approach's row from world_rules §5 "Wrong Approach Mirror Behaviour" (row lookup keyed
by the registry from F2). While editing assembler.md, also apply
`assembler_template.spec.md` Fix 1's pending correction: "the 6 world rules" → the
dynamic header-bounded extraction (there are 12).

### F12 — Stale cross-references and miscounts (batch cleanup, all one-line edits)

- `writer.md`: "Called by: Orchestrator (step 11)" → step 8; "proceeds with step 12
  (save to /chapters/)" → step 9.
- `updater.md`: "Receives update_brief.json from Orchestrator after chapter is
  written" / "Called by: Orchestrator, after Writer subagent returns" → produced by
  the Extractor, called at step 12.
- `INTEGRATION_SPECS.md` §5: `static_doc_order = [... "curriculum"]` → the actual stem
  is `concept_curriculum` (the TOML is already correct; the doc would break a reader
  who copies it).
- `correspondence_map.md` §8 audit: "23 operations mapped in Section 4/5" → §5 has 22
  rows covering 24 operations (two merged rows — already tracked in field_registry.md);
  the audit's YES rows overstate completion.
- `world_rules.md`: two sections are both numbered "6" (PRODUCTIVE FAILURE STRUCTURE,
  TERMS BECOME LENSES). Renumber and re-check inbound references.
- `fetcher.md` new_focal_character: "location specified in pointer" — the pointer has
  no location field; delete the phantom branch or add the field deliberately.

### F13 — Already-tracked content gaps (listed for completeness, decisions on file)

Not new findings; blocked on content authoring per existing docs, restated so this spec
is a complete worklist:

- correspondence_map §5: split the two merged rows (Related problem; Generalisation /
  Inventor's Paradox) — decision recorded in `field_registry.md`; requires reading the
  source text first.
- `prerequisite` field for CR3 — **owner decided (D5, 2026-07-02): author it.** Basis:
  Decision 1's chronological chain (most operations' prerequisite is the preceding
  process step), verified against the source text per the sourcing rule. Schema field
  added to `cards/concept/_schema.json`; 24 values authored during init (F2), reviewed
  by the owner. CR3 then goes live (remove the always-SKIP).
- `canonical_problem_structure` / `canonical_correct_approach` — proposed in
  `assembler_template.spec.md` Fix 2, values unauthored (24, not 23).
- Neither spec in this directory is implemented as code.

---

## NEW REQUIREMENTS FROM OWNER DECISIONS (2026-07-02)

Source: `human_decision.md`, all DECISION lines resolved. These are additions, not
bug fixes — the audit above didn't know about them because they're design intent the
owner supplied when deciding.

### F14 — Visible life progression for returning characters (owner: "at all cost")

The book's thesis must be *perceivable*: people who solve gates get better at life.
When a past character returns, their ordinary life has moved forward (promotion,
grades, resolved conflict) because the thinking transferred.

- `cards/characters/_schema.json`: `ordinary_life_state` gains a companion
  `life_progression` array — one entry per appearance: `{ chapter, state }` — so the
  trajectory is queryable, not just the latest snapshot.
- Assembler (return_to_character): the prompt must include the character's *previous*
  ordinary_life_state with the instruction to show visible progress from it, never
  explained as gate-caused (style rule: reader makes the connection).
- Extractor: record the new state; flag `UNDETERMINED` if the prose showed no
  progression (so a stagnant return is caught, not silently accepted).

### F15 — Cast mixing rule: always ≥1 improvised newcomer per gate

Owner decision D7: early arcs improvise everyone; later arcs mix returning solvers
and failers (the accumulated population is the "curated pool"); **every gate chapter
contains at least one fully improvised newcomer** so the world never closes.

- Assembler: gate-chapter prompts state the cast mix explicitly: focal solver (new or
  returning per pointer), optional returning failer(s), and at least one newcomer.
- Extractor/Updater: per F-item on D6 (below), all *named* entrants are recorded.

### F16 — Anchor omnipresence (supersedes all anchor-cadence logic)

Owner decision D3: the mystery person appears in **every gate chapter**, briefly, in
relation to the gate. Her cross-city omnipresence is physically impossible — this is
a deliberate planted clue (she bridges book 1 → book 2) and must be encoded in
`hidden_coherence` when authored, and never explained in book 1.

- Pointer: `anchor_appears: true` for every gate-bearing chapter type, by rule — no
  cadence computation.
- **Form must vary** (anti-formula, owner's D4 priority): the Assembler rotates the
  manifestation — seen directly / already gone, traces left / mentioned by a bystander
  / a notebook page — tracked in `mystery_anchor.json` (add `manifestation` to
  observable_log entries) so the same form doesn't repeat consecutively.
- Check C3 **inverts**: FLAG when a gate chapter has *no* anchor presence (was: FLAG
  when she appears too often). anchor_interlude remains a chapter type, rare in book 1.

### F17 — Character naming moves to stable data

Owner decision D7 keeps LLM improvisation for newcomers, so the original drift risk
(the "no Arabic names" incident) still needs its durable fix:

- New `core/character_naming.md`: naming rules (African names, region/language notes,
  exclusions) + a used-name ledger appended by the Updater each chapter.
- Assembler reads it every chapter instead of relying on the LLM-rewritten living
  document's "NOTES FOR AI" section surviving each rewrite.
- `assembler.md`'s CRITICAL RULES citation updates to point here (it currently cites
  living_document.md as the naming source).

### Ensemble rule (D6 formalization — no new mechanism, one doc line)

The story has **no single protagonist**; each gate has a focal solver but the book is
an ensemble. Add this sentence to `world_rules.md` §3 (protagonist role) so no future
agent "helpfully" promotes a recurring character to protagonist. `characters_entered`
becomes a real multi-entry list and named failed solvers get stub cards (F-item
detail under D6 in `human_decision.md`); `correct_approach` gets its consumer:
return-chapter continuity in the Assembler.

---

## SUGGESTED ORDER OF EXECUTION

All owner decisions are in (`human_decision.md`, 2026-07-02) — no judgment calls
remain in this list.

1. F1, F3, F10 — three small mechanical edits; unblocks any end-to-end test.
2. F2 (registry incl. machine-readable repetition map + init script + authoring
   pass) — nothing real can run before it.
3. F4, F5, F6, F7, F8, F9, F16 — agent-spec/state-schema changes; do together, they
   touch the same files, then re-audit `field_aliases.md` / `field_registry.md` /
   `chapter_type_contract.md` in one pass.
4. F11, F12, F14, F15, F17 + the ensemble rule — prompt-quality, new design rules,
   doc hygiene.
5. F13 — content authoring against the source text (now includes the prerequisite
   graph and the echo-context enum), per specs/README sourcing rule; owner reviews.
