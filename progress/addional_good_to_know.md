# ADDITIONAL GOOD-TO-KNOW — the generalization plan (any book → teaching fiction)

Compiled 2026-07-09 by the fiction_loop session, for whoever picks this up next.
Provenance: the genre/factory design is from the 2026-07-03 owner+Claude session and
is FULLY WRITTEN DOWN in two artifacts (read them, they are short and current):

- `fiction_loop/specs/intake_factory.spec.md` (195 lines; improvement pass 1c8b51c,
  2026-07-10 — absorbed ch1–ch6 lessons: generation rules, leak debt, concrete
  validation gate + parallel tracks) — the whole plan
- `fiction_loop/specs/genre_derivation.md` (72 lines) — the genre-shapes method

This file does NOT restate them; it maps them, adds what later sessions contributed,
and lists what must stay true for the plan to survive. Items marked SETTLED / OPEN.

## 1. The goal in one line (SETTLED, owner 2026-07-03)

User gives the system a knowledge book → gets a serialized teaching novel — without
authoring templates and **without being interviewed**. fiction_loop as it exists IS
the factory's first worked example, run manually (Pólya → The Sankofa Gates); every
factory stage names the Sankofa artifact that exemplifies its output.

## 2. The load-bearing architectural split (SETTLED)

**Chassis** (book-agnostic, already built): pipeline, agents, scheduler, cards,
checks, conduct, logging, bridges. **Pedagogy pack** (knowledge-type specific,
swappable): chapter-structure template, failure-pool semantics, transfer-proof
mechanism, externalization requirement. Pack boundary = *documents the machinery
reads*, never code. Installed pack: process fiction. Thing-fiction pack (concept
becomes world physics; precedent = old novel_pipeline / the 1.docx cultivation
exemplar) is v2.

## 3. Genre shapes — what we actually found (SETTLED, specs/genre_derivation.md)

The findings worth remembering even without opening the file:

1. **Genre is DERIVED, not chosen.** Requirements pin the structure; the remaining
   freedom is only the skin. The method reproduced the owner's gate-fiction choice
   from first principles and killed the alternatives he'd tried (detective) or
   floated (absurdist school with resets).
2. **Classify the book by what MASTERY behaviorally looks like** — process / thing /
   perception / relational / discipline — each maps to a distinct fiction strategy
   (experience-through-failure / concept-as-world-physics / contrast-pair worlds /
   legible-minds encounters / time-lapse compounding).
3. **The book's own failure catalog is the strictest genre filter.** The genre must
   make THOSE failures dramatizable with physical consequences; most candidates die
   here or on "playable without domain expertise."
4. **Seven near-invariant requirements** (playable-without-expertise, guaranteed
   solvability, externalized mental state, episodic variety + ensemble, adjacency to
   ordinary life, real stakes, serial macro-mystery scaffold) — candidates are
   stress-tested against them; a kill-table for 9 genres is recorded with the exact
   requirement each dies on.
5. **Convergence:** for process books, ANY world with bounded fair solvable problem
   spaces inside ordinary life with a reflective surface for the solver's mind IS
   gate fiction, whatever the costume.
6. **The one non-derivable step: inventing the externalization mechanism** (Sankofa:
   the mirror/register mechanic — the project's actual original invention). No genre
   catalog supplies it; it is the taste-bearing step, handled via taste flights.
7. **Proof of generality:** worked outputs exist for 5 books (Pólya, Atomic Habits →
   cultivation, Never Split the Difference → creature-bonding, Kahneman → distortion
   districts, Design of Everyday Things → appraiser fiction) — same method, different
   books, derived not backfit.

## 4. The factory pipeline + owner UX (SETTLED, intake_factory.spec.md)

Six stages: ingest/classify → requirements → genre+mechanism (taste-bearing) →
template generation (correspondence map FIRST; hard sourcing rule: every domain claim
carries a located quote) → three automated verifications (fidelity / cross-model
logic / IS-not-LIKE correspondence audit) → **propose-and-correct owner UX**: default-
forward never blocking, decisions ledger with reversibility tags, taste flights
(differences rendered as tasteable samples, never option descriptions), free-text
corrections that propagate via a consumer map. Build list + sequencing are in the
spec (§2–3). Honest limit recorded (§4): coherent + faithful + audited can still be
artistically dead — the taste flights exist so a human smells that early.

## 5. What later sessions added that serves this plan (2026-07-04/05)

- **`fiction_loop/CONTRIBUTING.md` — the constitution — is CHASSIS.** 15 laws with
  incident case law, layer model, backtest rule ("every bug must map to a law or the
  constitution gets amended"). LAW 14 is the generalization insurance: chassis and
  pack never mix, and *"if generalizing forces a law change, there's a chassis/pack
  leak — find it first."* The extension procedure's last entry is literally "New
  book (the real goal): nothing in this file changes."
- **Known chassis/pack leaks, recorded as debt (OPEN — must be fixed before or
  during factory build):** the anchor's physical description hardcoded in
  assembler.md; wrong-approach mirror content quoted into assembler.md instead of
  fetched from world_rules §5; `QUOTA_BY_ARC` hardcoded in structural_gate.py
  (arc cast quotas are pedagogy — pack content living in chassis code).
- **field_registry.md is the manual precursor of the factory's Stage-6 consumer
  map** — the spec says so explicitly. Every registry row and case-law entry added
  now is factory calibration data, not just maintenance.
- **LAW 15 (no shadow/decorative machinery) + the pending machinery inventory
  sweep (OPEN)** — the factory cannot generate packs against a chassis whose actual
  machinery is partly unwritten (.gitignore incident) or non-firing (CR3, F14).
- **progress.py / analyst.py** were built explicitly as the future SaaS product face
  and support surface (owner: "where are we / how much left" beats diagnostics for
  average users).

## 6. Gates between here and building the factory (the honest checklist)

Sequencing is owner-agreed: **validate book 1 first** — the factory must encode a
PROVEN recipe. Status updated 2026-07-19 (ch8 committed); the canonical, most
detailed version now lives in `intake_factory.spec.md` §3 — keep the two in sync
(SG-14):

1. More teaching chapters at accepted quality (prose bar: 1.docx) — **8 committed**.
2. The never-exercised machinery: **arc_transition ✓ (ch7)**; **arc-1→2 boundary ✓
   (ch8 — failure pool grew, new-type cards wired)**; **return chapter F14 +
   correct_approach ✓ (ch6; again ch9)**; STILL OPEN: **anchor_interlude** (never
   fired) and **compression at scale**.
3. Transaction integrity trio: **gitignore prose exclusion ✓ (FI-1)**; pathspec-
   limited chapter commit + redo-guard hardening — confirm status.
4. The gate/refresh reorder (mapped, 6 consumers) — **✓ DONE (T-008)**.
5. Machinery inventory sweep (LAW 15) — **STILL OPEN**.

## 7. One meta-rule that made all of this work (SETTLED, owner-empirical)

PROPOSE-AND-CORRECT, never interview. The owner makes every good creative call by
correcting a visible artifact, and no good ones by answering abstract questions.
This is written into intake_factory Stage 6 as the product's UX law — and it applies
equally to any future session working with him directly.
