# ASSEMBLER TEMPLATE SPEC

> **UNBLOCKED 2026-07-03.** Everything this spec was blocked on is done:
> correspondence_map §5 has 24 rows with canonical labels (name-keyed lookup
> works); `canonical_problem_structure` / `canonical_correct_approach` exist,
> authored and owner-approved, on all 24 concept cards; assembler.md's '6 world
> rules' line was corrected to dynamic extraction (12 today); the HARD RULES
> block (assembler.md, 2026-07-02) must be appended by the implementation as
> the prompt's final section.

Covers: the mechanical half of `agents/assembler.md` — pulling fixed reference material
and fetched fields into `assembled_prompt.md`. This is the file where the three
previously-mislabeled-as-code steps were found, so this spec resolves each one before
treating the function as implementable. The other half of Assembler (new-character
generation) stays out of scope — see `specs/README.md`.

**Function:** `assemble_prompt(fetched, consistency_flags, chapter_type, chapter_number, operation_card) -> str`

**Implement literally against `agents/assembler.md` ASSEMBLY PROCEDURE steps 3–6, 8–9
and the three STRUCTURE templates:** pulling `physical_anchor` off the concept card (a
plain JSON field read), indexing `failure_modes_not_yet_shown[0]` for "wrong approach to
show first," computing chapter number, and filling in the fixed markdown skeleton — these
are direct lookups with no open questions.

**Not a direct lookup as originally assumed — `correspondence_map.md` Section 5's row by
operation name:** Section 5's "Gate Operation" column uses different wording than the
operation names used everywhere else in the pipeline (`concept_curriculum.md` Section 3,
`process_state.json`), and has only 22 rows against 24 operations — two rows each
silently cover two distinct operations. A string-equality lookup keyed on operation name
will fail for most rows as the documents stand today. This is not a code gap this spec
can close — see the "Known orphans" entry in `core/field_registry.md`, which records the
decision already made: split the two merged rows so every operation gets its own row,
not an alias table. Do not implement this lookup until that content work is done —
authoring it requires reading the source text (Pólya, *How to Solve It*) first; see the
field_registry.md entry for what was tried and reverted, and why.

---

## Fix 1 — one extraction rule, replacing two broken ad hoc ones

Both of the following were the same underlying bug: an instruction to "extract N
[rules/sections] verbatim" where nothing defines where one unit stops and the next
starts, or where the stated count (`6`) doesn't match what's actually in the source
document (`12`, confirmed by inspection of `world_rules.md` Section 4).

**One general rule, applied everywhere "verbatim" is used in these specs:**

```
extract_sections_verbatim(markdown_text, header_pattern) -> list[str]:
  For each line matching header_pattern:
    capture everything from that line up to, but not including, the next line
    matching header_pattern OR the next line at the same-or-higher heading level
    (## or #), whichever comes first.
  Return the captured blocks, in document order.
  Never hardcode an expected count — the number of returned blocks is however many
  exist in the source document at read time.
```

**Applied to `world_rules.md`:**
`extract_sections_verbatim(doc, r"^\*\*Rule \d+:")` scoped to `## 4. WORLD RULES`.
Confirmed by reading the file: this returns 12 blocks today (Rule 1–12), each already a
clean bold-header-line + one paragraph. Replaces `agents/assembler.md`'s current line
`Extract: the 6 world rules verbatim` — that line is stale (the document grew from 6 to
12 rules at some point and this spec was never updated) and must be corrected to
reference this dynamic extraction, not a fixed number, so the next time the document
changes the extraction is still correct with no spec edit required.

**Applied to `style_contract.md`:**
`extract_sections_verbatim(doc, r"^### Rule \d+:")` scoped to `## 1. VOICE — THREE
ABSOLUTE RULES`. Confirmed by reading the file: headers are at lines 10, 19, 34, with
the next `##` header at line 45 — so this cleanly returns exactly 3 blocks, matching
`assembler.md`'s "Rule 1, Rule 2, Rule 3" as currently worded. The fix here isn't the
count, it's the boundary: each returned block now includes Rule 2's full Physical
Anchor table and every rule's WRONG/RIGHT examples in full, because "everything until
the next header" requires no partial-inclusion decision — there is no longer a version
of this instruction where an LLM (or a person) has to guess how much of Rule 2's section
counts as "the rule."
The "never list" (`Extract: the never list verbatim`) uses the same function scoped to
`## 6. THE NEVER LIST` — this one was already unambiguous (a single table with a clear
boundary) but now uses the same general rule instead of being a special case, so future
sections extracted "verbatim" don't need a new one-off decision each time.

**Cost note, not a correctness concern:** this makes the fixed template portion of every
`assembled_prompt.md` longer (full text of 12 rules + Rule 2's table + all three rules'
examples). This content is static per chapter — it doesn't grow with story length and
doesn't change unless `world_rules.md` or `style_contract.md` themselves change — so it
should be rendered once and cached, not re-parsed from markdown on every chapter. If
token cost later becomes a real problem, the correct fix is a human-authored condensed
companion document (e.g. `world_rules_compact.md`), maintained deliberately alongside
the source — not a runtime decision about what to omit, which would reintroduce the
exact judgment call this fix just removed.

**Not yet applied:** `agents/assembler.md`'s own ASSEMBLY PROCEDURE steps 1–2 still say
"the 6 world rules" and "Rule 1, Rule 2, Rule 3 verbatim." I haven't edited that file —
this spec and the live prompt file are currently out of sync on this point, the same
kind of drift `core/field_aliases.md` exists to catch. Say if you want me to correct
`assembler.md` to reference this extraction rule directly.

---

## Fix 2 — `problem_structure` / `correct_approach` have no canonical source to derive from

Confirmed by reading `cards/concept/_schema.json` directly: the only pre-authored,
per-operation field is `physical_anchor`. There is no stored problem-structure or
correct-approach text per operation, so `assembler.md`'s "derive from operation being
taught" instruction currently asks for fresh synthesis every chapter — genuinely
AI-shaped as the system exists today, not a lookup.

**Proposed schema addition to `cards/concept/_schema.json`**, following the exact
pattern `physical_anchor` already uses (one-time authored per operation, read-only at
generation time):

```json
"canonical_problem_structure": { "unknown": "[ ]", "data": [], "condition": "[ ]" },
"canonical_correct_approach": "[ ]"
```

After this addition, the two Assembler instructions become plain lookups, identical in
shape to the existing `physical_anchor` pull:

```
problem_structure ← concept_card.canonical_problem_structure
correct_approach  ← concept_card.canonical_correct_approach
```

**This does not remove creative work — it relocates it.** Today, "derive from
operation" asks for the abstract problem shape to be invented fresh, per chapter, under
time pressure, with no review step. After this change, the abstract shape is authored
once per operation (23 operations total, per `concept_curriculum.md`'s operation list),
outside the chapter-generation loop, reviewable before it goes live — and only the
concrete character/city/scene-specific dressing is left to the Writer per chapter, which
is already Writer's job and doesn't change.

**Naming note:** don't confuse this with the *existing* `problem_structure` /
`correct_approach` fields on the **event card** schema (`cards/events/_schema.json`) —
those record what actually happened in one specific chapter's specific gate instance,
extracted post-hoc by Extractor. The new fields proposed here are operation-level
templates, not instance records. I've named them `canonical_*` specifically to avoid
this collision; recommend adding a row to `core/field_aliases.md` documenting the
distinction once this lands, since it's exactly the kind of near-duplicate name that
caused the `wrong_approaches_demonstrated` / `failure_modes_shown_this_chapter`
confusion earlier.

**Not yet applied:** no concept card instances exist yet (`cards/concept/` currently has
only `_schema.json`, confirmed by listing the directory), so this is a zero-risk,
additive schema change with nothing to backfill — but the 23 actual values still need
authoring before the first real concept card is created. That's content work, same
category as CR3's missing prerequisite graph: not something to auto-populate silently.
I can draft a first pass against `concept_curriculum.md`'s operation list if useful, but
it needs your review — it's creative/pedagogical content specific to this story.
