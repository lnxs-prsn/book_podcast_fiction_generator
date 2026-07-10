# DETERMINISTIC PIPELINE SPEC

> **DRIFT NOTE 2026-07-03 — read before implementing.** Since this spec was
> written: (1) extractor.md's DECISION LOGIC was rewritten — 'Conditions 1–4'
> below no longer exist; implement against the current STEP A–E map-deficit
> scheduler. (2) CR3 is no longer blocked: `prerequisite` exists on every
> concept card (owner-approved graph) — drop the always-SKIP. (3) C4's
> paraphrase limitation is closed: contexts are a fixed enum
> (`process_state.json` context_enum); implement exact enum equality, and C4
> runs post-assembly (step 7.5), not step 5.

Covers: Orchestrator, Fetcher, Updater, Consistency Checker's mechanical checks, and
Extractor's DECISION LOGIC. Each of these is already written as unambiguous pseudocode
in its `agents/*.md` file — this spec does not restate that logic (restating it here
would create a second copy that can drift from the first, the exact bug class this
whole exercise started from). Instead it names the function boundary, points at the
existing section that IS the algorithm, and calls out only the places where that
existing text was incomplete.

---

## 1. Orchestrator → `run_chapter_cycle(override_chapter_type=None)`

**Type:** pure control flow. No LLM call itself; sequences calls to the pieces below.

**Implement literally against:** `agents/orchestrator.md` STEPS 1–3, 6, 9, 10, 13, 14,
and the USER COMMANDS section. All of it is already read-a-file / compute-an-arithmetic
value / dispatch-on-a-string-value with no interpretation required.

**What changes from the current spec:** STEPS 4, 5, 7, 8, 11, 12 ("SPAWN X subagent with
this prompt") become direct calls — to a plain function for the pieces this spec set
covers, to an LLM call for the pieces that stay in `agents/`. The sequencing, file
paths, and error-dispatch table (`ContextOverflowError` / `CostLimitError` /
`ChapterValidationError` / other) carry over unchanged from STEP 8.

**Input validation, not free-text parsing:** `override_chapter_type`, if provided, must
be validated against the literal enum (`new_focal_character`, `return_to_character`,
`anchor_interlude`, `arc_transition`) and rejected otherwise — do not attempt to infer a
chapter type from arbitrary user phrasing. That would reintroduce a judgment call this
spec is explicitly trying to keep out of the control-flow layer.

---

## 2. Fetcher → `fetch_fields(chapter_type, chapter_number, char_id=None) -> FetchedFields`

**Implement literally against:** `agents/fetcher.md` FETCH LOGIC BY CHAPTER TYPE. This
is already a per-type lookup table naming exact file paths and exact field names — zero
interpretation at any branch.

**Output shape:** a typed structure (dataclass / TypedDict) mirroring the OUTPUT FORMAT
block in `fetcher.md`, keyed the same way, so downstream consumers (the checks and
Assembler spec below) get typed fields instead of parsing markdown.

---

## 3. Consistency Checker (mechanical subset) → `run_mechanical_checks(fetched, chapter_type) -> list[CheckResult]`

**In scope, implement literally against `agents/consistency_checker.md`:** V1, V2, C1,
C2, C3, C4, CR1, CR2, A1. Each is already a boolean comparison, count, or string scan.
(C3 is presence-only since 2026-07-10 — its manifestation-variety clause is now C3b in
the POST-ASSEMBLY PASS and is out of this function's scope: its input is
`assembled_prompt.md`, which doesn't exist at step 5.)
The `SKIP: chapter_type IN [anchor_interlude, arc_transition]` guards already present on
V2, C2, CR1, CR2 (per `core/chapter_type_contract.md`) carry over unchanged.

**Not in scope, remain a separate small LLM call:** V3, A2. Do not fold these into this
function — they require reading text for tone/content, which this function's contract
(pure structured-data in, structured-data out) cannot honestly satisfy.

**Not in scope, blocked on missing schema:** CR3. Return
`SKIP: no prerequisite field exists in cards/concept/_schema.json or concept_curriculum.md
— schema gap, not a data-entry gap` for every operation, rather than omitting the check.
An omitted check and a check that always reports SKIP look identical in the output unless
you make the SKIP explicit — silently dropping it would recreate exactly the kind of
invisible gap this whole investigation started with. See `core/field_registry.md`'s
"Known orphans" section for the tracked gap.

**New — CR2's grade-range parser (previously undefined):** `concept_curriculum.md`'s
Arc Breakdown "Gate Grade" column contains four distinct string formats, verified against
all 9 rows: `"N-M"` (bounded range, e.g. `"3-4"`), `"N+"` (open lower bound, e.g. `"6+"`),
a bare integer (e.g. Arc 8's `"8"`), and `"Unknown"` (the Finale row). CR2 must parse all
four:

```
parse_gate_grade(s: str) -> (min: int, max: int | None):
  IF s matches r"^(\d+)-(\d+)$":      return (int(g1), int(g2))
  IF s matches r"^(\d+)\+$":          return (int(g1), None)   # None = unbounded above
  IF s matches r"^(\d+)$":            return (int(g1), int(g1)) # bare integer, e.g. Arc 8 = "8"
  IF s == "Unknown":                  return (None, None)      # no band to violate — CR2 PASSes unconditionally
  ELSE: raise ValueError              # malformed data, not a judgment call — fail loudly
```

This is a complete parser for a fixed, closed set of formats verified against every row
of the actual document, not an inference.

**New — A1's match definition (previously undefined):** `agents/consistency_checker.md`
specifies "scan for the string `hidden_coherence`... or any content matching
`mystery_anchor.json` hidden_coherence fields," which as written doesn't say what
"matching" means — that ambiguity would have made A1 non-mechanical despite being listed
above as in-scope. Resolve it as literal substring containment against the concrete
secret values, not semantic similarity:

```
scan_for_hidden_coherence_leak(fetched_text: str, hidden_coherence: dict) -> CheckResult:
  IF "hidden_coherence" is a substring of fetched_text: return BLOCK
  FOR each key, value in hidden_coherence.items():
    IF key == "access": continue                       # metadata field, not a secret value
    IF value not in ("[ ]", "", None) AND value is a substring of fetched_text:
      return BLOCK
  return PASS
```

This is genuinely zero judgment — literal containment of a fixed set of known secret
strings — once the ambiguous "matching" language is replaced with a concrete definition.

**Caveat, not fully mechanical as scoped — C4:** `consistency_checker.md`'s C4 compares
`process_state.json`'s `[operation_id].contexts_demonstrated` against the fetched
`ordinary_life_echo` context by what the spec above calls "a boolean comparison... or
string scan." That undersells it: per `extractor.md`, `contexts_demonstrated` entries are
free-text phrases (e.g. "engineering project handover"), not values drawn from a fixed
enum, so two entries can describe the same context in different words and an exact-string
lookup will miss the match (false PASS) or a coincidental phrase overlap could produce a
false FLAG. Implement C4 as literal string equality only — do not attempt fuzzy or
semantic matching inside this function, that would violate the "pure structured-data in,
structured-data out" contract this spec set relies on — and record this as a known
limitation (silent under-flagging on paraphrased contexts) rather than a solved check.
Closing the gap for real would mean constraining `contexts_demonstrated` to a fixed
pick-list at the schema level, which is a content/design decision outside this spec's
scope.

---

## 4. Extractor's DECISION LOGIC → `compute_next_chapter_pointer(process_state, master_state, mystery_anchor, concept_curriculum) -> NextChapterPointer`

**Implement literally against:** `agents/extractor.md` DECISION LOGIC, Conditions 1–4.
Pure arithmetic and list/JSON lookups — no chapter prose is an input to this function.

**New — Condition 2's tie-break (previously undefined):** "pick the one with the
highest `chapters_since_last_touch`" doesn't say what happens on an exact tie between
two qualifying operations. Resolve with a deterministic secondary key, in the same
spirit as Condition 1's existing tie-break ("pick the one listed first in
concept_curriculum.md"):

```
IF tie on chapters_since_last_touch:
  → pick the operation with the lexicographically smaller operation_id
```

Arbitrary, but total and stable — the point is that the same state always produces the
same output, not that the tie-break is meaningful.

**Split from the rest of Extractor:** today, one Extractor LLM call does this
computation *and* reads the chapter prose. Splitting this function out means the LLM
call that remains only has to do prose-reading — it no longer needs to also get
`current_touch` arithmetic right, which is exactly the kind of task an LLM is unreliable
at and a function is not.

---

## 5. Updater → `apply_update_brief(update_brief) -> UpdateReport`

**Implement literally against:** `agents/updater.md` STEP 1–10 and COMPRESSION RULES.
Already pure JSON mutation over fields that arrive pre-resolved from `update_brief.json`
— nothing in this function ever reads free text. The `IF chapter_type IN
[anchor_interlude, arc_transition]: SKIP` guards on STEP 1, 2, 3, 4, 8 (added per
`core/chapter_type_contract.md`) carry over unchanged. No open items — this one was
already spec-complete.
