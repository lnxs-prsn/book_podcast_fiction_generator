# INTAKE FACTORY SPEC — knowledge book in, teaching fiction out

Goal (owner, 2026-07-03): a user gives the system a knowledge book and gets a
serialized teaching novel — without authoring any core templates and **without being
interviewed**. Everything downstream of the templates already exists and is
book-agnostic (the fiction_loop chassis). This spec defines the front half: how the
templates, state, and decisions get *derived* from the book.

Calibration source: this repo IS the factory's first worked example, run manually with
a human in the loop (Pólya → The Sankofa Gates). Every stage below names the artifact
from that run that exemplifies its output.

---

## 0. TWO-LAYER ARCHITECTURE (what generalizes, what swaps)

- **Chassis (book-agnostic, BUILT):** orchestrator pipeline + agents, state cards,
  map-deficit scheduler with prerequisite gating, touch ladder, living document,
  consistency checks (pre + post-assembly), conduct rules, per-chapter logging,
  bridge scripts, init_state generation. Reads whatever the cards/templates say.
- **Pedagogy pack (knowledge-type specific):** chapter-structure template, failure-pool
  semantics, transfer-proof mechanism, externalization requirement. The installed pack
  is **process fiction** (failure-first, echo scenes, mirror). A **thing-fiction pack**
  (concept-as-world-physics; precedent: the old novel_pipeline / 1.docx cultivation
  exemplar) is v2. Perception/relational/discipline packs are variants.
- Pack boundary = documents the machinery reads (curriculum chapter structure,
  correspondence map §3, failure pools), NOT code. Packs are template sets.

---

## 1. PIPELINE (six stages, three automated verifications, zero mandatory questions)

### Stage 1 — Ingest & classify
Extract book text (format_adapters/已 exists for pdf/epub). Classify the knowledge by
what MASTERY looks like behaviorally:
process (executes moves under pressure) / thing (sees the concept everywhere) /
perception (discriminates) / relational (process on other minds) / discipline
(compounds over time). Extract the book's own **failure catalog** — how it says people
get it wrong (Pólya's bad solvers → the 14 wrong-approach types). Select pedagogy pack.
*Worked example: concept_curriculum.md §3–§4 content.*

### Stage 2 — Requirements derivation
Instantiate the requirements list (near-invariant, weighted by type):
(1) problems playable without domain expertise, (2) guaranteed solvability = the
reader's contract, (3) externalized mental state, (4) episodic variety + ensemble,
(5) adjacency to ordinary life for transfer proof, (6) real stakes, (7) serial
macro-mystery scaffold.

### Stage 3 — Genre derivation + mechanism invention  ← TASTE-BEARING
Stress-test candidate genres against Stage-2 requirements; most die on (1) or (5)
(domain-expertise import; sealed worlds). Derive the surviving skeleton, pick the skin
with the most free infrastructure, then INVENT the externalization mechanism (the
mirror-equivalent — never supplied by any genre catalog; always custom).
*Worked example: gates + the mirror/register mechanic; the derivation table lives in
the 2026-07-03 conversation and should be lifted into a `genre_derivation` reference.*

### Stage 4 — Template generation
Draft the full template set, correspondence map FIRST (its audit governs the rest):
correspondence_map, world_rules, style_contract, concept_curriculum (incl. difficulty-
scaled touch map per D9 defaults), character_naming, living_document initial state,
operation manifest (ids, schedules, prerequisites, anchors, canonical problem
structures, context enum, failure pools) → consumed by init_state.py.
**Sourcing rule (hard):** every domain claim carries a supporting quote located in the
book text at draft time. *Worked example: content_for_review.md + init_state.py's
OPERATIONS/PREREQS tables.*

### Stage 5 — Verification (all automated; humans don't read piles)
- **Fidelity check:** a checker agent re-locates a supporting quote for every domain
  claim in the generated templates; anything unsupported is flagged, not shipped.
  (Origin: the reverted from-memory echo rows; validated 2026-07-03 when the owner
  disclosed he never read the review docs — the machine check found all claims
  faithful.)
- **Logic check:** a DIFFERENT model cross-reviews for contradictions and broken
  chains (prerequisite graph acyclicity etc. — partly plain code).
- **Correspondence audit:** IS-not-LIKE; every story element traces to a book
  mechanic with the same failure mode (correspondence_map §8 checklist; half
  mechanical, half the strongest available LLM).

### Stage 6 — Owner experience: PROPOSE-AND-CORRECT (never interview)
Owner's empirical behavior (this project): never answered abstract questions well
("I don't understand your question"), never read long review docs, made every good
creative call by CORRECTING a visible proposal (B+C secret combo, Sankofa title,
co-hosted touches). Questions eject owners from creative flow into problem-solving
mode; corrections keep them in reader-mode. Therefore:

1. **Default-forward, never blocking.** The factory picks the recommended option on
   every taste axis itself and keeps moving. The nine owner decisions of the worked
   example (human_decision.md D1–D9) ship as recorded defaults.
2. **Decisions ledger.** Every inherited default is logged with rationale + a
   REVERSIBILITY tag (title: cheap anytime; genre skin: expensive after ~ch. 5;
   secret: expensive after first anchor scenes). "AI proposed and I let it stand" is
   visible, never baked in silently.
3. **Taste flights.** Where options genuinely diverge, render the difference as
   something a reader can TASTE — half a page of the observer under secret A vs B, a
   sample opening in two skins — never a paragraph describing options. Choices are
   made through artifacts, in reader-mode, by pointing.
4. **Free-text corrections, anytime, propagating.** "The coat is wrong" / "more
   menace" / silence (= consent). The system re-derives dependents and updates the
   ledger. A user who wants "just fiction" touches nothing and gets a coherent
   all-defaults book.

### Stage 7 — Init & run
init_state.py generalized to read the Stage-4 operation manifest instead of embedded
tables → process_state, concept cards, registry. Then the existing loop (RUN.md).

---

## 2. BUILD LIST (what does not exist yet)

| Item | Notes |
|---|---|
| Stage-1 intake agent spec + knowledge-type rubric | new |
| genre_derivation reference doc (requirements table + candidate stress-test method) | lift from 2026-07-03 conversation |
| Meta-templates: required sections/contracts per core doc | derive from the Sankofa docs' structure |
| Fidelity checker agent (claim → quote or flag) | new; simple |
| Cross-model logic reviewer harness | new; simple |
| Taste-flight generator (render divergent options as samples) | new |
| Decisions ledger format + propagation rules | generalize human_decision.md |
| init_state.py: split OPERATIONS/PREREQS into a manifest file it loads | small refactor |
| Thing-fiction pedagogy pack (v2) | promote novel_pipeline patterns into the chassis |

## 3. SEQUENCING (owner-agreed)
Validate book 1 first (several more Sankofa chapters — the factory must encode a
PROVEN recipe). Then build Stages 1–6 for process books (v1). Thing pack v2.
Each processed book leaves a worked example that calibrates the next — the second
book is much cheaper than the first; the fifth is near-turnkey.

## 4. NON-AUTOMATABLE RESIDUE (honest limits)
The mechanism invention (Stage 3) and correspondence audit can be drafted and checked
but not *guaranteed* — a coherent, source-faithful, well-audited book can still be
artistically dead. The taste flights exist precisely so a human can smell that early.
The factory's defaults carry real authorial weight; the ledger is what keeps that
honest.
