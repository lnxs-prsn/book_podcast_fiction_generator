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
  Added since this spec was written (2026-07-04/05): deterministic structural gate
  (tools/structural_gate.py, pre-state per-chapter check), per-chapter git
  transactions + staged undo ladder (S1–S4), progress.py / analyst.py (receipts-
  driven status + zero-token diagnosis — the future product face), and the
  constitution (`fiction_loop/CONTRIBUTING.md`, 15 laws with case law; LAW 14 is
  the chassis/pack insurance: "if generalizing forces a law change, there's a
  chassis/pack leak — find it first").
- **Pedagogy pack (knowledge-type specific):** chapter-structure template, failure-pool
  semantics, transfer-proof mechanism, externalization requirement. The installed pack
  is **process fiction** (failure-first, echo scenes, mirror). A **thing-fiction pack**
  (concept-as-world-physics; precedent: the old novel_pipeline / 1.docx cultivation
  exemplar) is v2. Perception/relational/discipline packs are variants.
- Pack boundary = documents the machinery reads (curriculum chapter structure,
  correspondence map §3, failure pools), NOT code. Packs are template sets.
- **Known boundary violations (recorded debt — fix before or during factory
  build; all three are chapter-independent work):** the anchor's physical
  description hardcoded in assembler.md; wrong-approach mirror content quoted
  into assembler.md instead of fetched from world_rules §5; `QUOTA_BY_ARC`
  hardcoded in structural_gate.py (arc cast quotas are pedagogy — pack content
  living in chassis code).

---

## 1. PIPELINE (six stages, three automated verifications, zero mandatory questions)

### Stage 1 — Ingest & classify
Extract book text (format_adapters/ already exists for pdf/epub). Classify the knowledge by
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
*Worked example: gates + the mirror/register mechanic. The full method + kill-table +
worked outputs: `specs/genre_derivation.md` (lifted 2026-07-04).*

### Stage 4 — Template generation
Draft the full template set, correspondence map FIRST (its audit governs the rest):
correspondence_map, world_rules, style_contract, concept_curriculum (incl. difficulty-
scaled touch map per D9 defaults), character_naming, living_document initial state,
operation manifest (ids, schedules, prerequisites, anchors, canonical problem
structures, context enum, failure pools) → consumed by init_state.py.
**Sourcing rule (hard):** every domain claim carries a supporting quote located in the
book text at draft time. *Worked example: content_for_review.md + init_state.py's
OPERATIONS/PREREQS tables.*

**Generation rules learned the expensive way (worked-example incidents, ch1–ch6 —
the factory's template generator MUST emit templates that satisfy these):**

1. **Compliance hierarchy.** Writer models obey the HARD RULES block (last section
   of the assembled prompt) near-100%; mid-brief prose is treated as suggestions
   (ch4 single-solver; ch6 missing improvised newcomer). Every enforceable
   constraint goes into the hard-rules channel — with literal values spelled out,
   never fill-in placeholders (the ambiguous "[fill in the arc's number]" rule-7
   incident produced "Arc 1." instead of "THREE").
2. **Gate↔rule pairing (LAW 5 corollary).** Every deterministic gate check must
   have a matching hard rule in the prompt; a check without a rule detects failures
   it never prevented — a paid draft per catch (F15/ch6 incident; as of ch6 all 5
   gate checks are covered by rules 7/8/9/10/12).
3. **Check placement.** Any consistency check that reads a choice made at assembly
   time must run POST-assembly, never pre (the V3/C4/A2b migration + the C3
   sub-clause missed inside it, ch6). When generating checks, classify each clause
   by which stage produces the data it reads — audit sub-clauses, not check IDs.
4. **Prevention over detection.** Internal vocabulary (operation labels, check
   names, schedule mechanics) must be quarantined at the prompt layer (forbidden-
   strings + self-verify), not caught in review (ch1's three never-list violations
   were all induced by the brief itself).

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
5. **Correction propagation IS an automated rule-change audit.** Every correction
   changes a rule/template that other artifacts consume. The factory must maintain a
   CONSUMER MAP per template section (who reads this rule: which agent specs, which
   checks, which card fields) and, on any correction, enumerate consumers →
   re-derive or explicitly exempt each — never apply a rule change point-wise.
   This is the machinery form of the manual habit recorded in
   `fiction_loop/core/field_registry.md` § RULE-CHANGE AUDIT, with four incidents of
   case law showing why point-wise edits fail even when the editor knows better
   (speed skips the audit; machinery can't).

### Stage 7 — Init & run
init_state.py generalized to read the Stage-4 operation manifest instead of embedded
tables → process_state, concept cards, registry. Then the existing loop (RUN.md).

---

## 2. BUILD LIST (what does not exist yet)

| Item | Notes |
|---|---|
| Stage-1 intake agent spec + knowledge-type rubric | new |
| genre_derivation reference doc | DONE — specs/genre_derivation.md |
| Meta-templates: required sections/contracts per core doc | derive from the Sankofa docs' structure |
| Fidelity checker agent (claim → quote or flag) | new; simple |
| Cross-model logic reviewer harness | new; simple |
| Taste-flight generator (render divergent options as samples) | new |
| Decisions ledger format + propagation rules | generalize human_decision.md |
| Consumer map per template section (rule → its consumers) + propagation enforcement | new; the case law is in core/field_registry.md §RULE-CHANGE AUDIT |
| init_state.py: split OPERATIONS/PREREQS into a manifest file it loads | small refactor |
| Fix the 3 chassis/pack leaks (§0: anchor description, mirror content, QUOTA_BY_ARC) | chapter-independent; precondition for any second pack |
| Machinery inventory sweep (LAW 15: no shadow/decorative machinery) | chapter-independent; the factory can't generate packs against a chassis whose machinery is partly unwritten or non-firing |
| Thing-fiction pedagogy pack (v2) | promote novel_pipeline patterns into the chassis |

## 3. SEQUENCING (owner-agreed)
Validate book 1 first (target ~8 Sankofa chapters — the factory must encode a
PROVEN recipe). Then build Stages 1–6 for process books (v1). Thing pack v2.
Each processed book leaves a worked example that calibrates the next — the second
book is much cheaper than the first; the fifth is near-turnkey.

**What "validated" concretely requires (as of ch6; projected proven ~ch 8–9, the
arc-1→2 boundary):** the never-exercised machinery must fire for real at least
once — arc_transition and anchor_interlude chapter types, the arc boundary (does
the failure pool actually grow? are new-type cards wired?), a return chapter
exercising F14 life progression + correct_approach continuity (first exercise =
ch6, in flight), compression at scale — plus the transaction-integrity trio
(prose in git, pathspec-limited chapter commits, redo-guard hardening) before any
unattended operation, and the LAW 15 machinery sweep.

**Chapter-INDEPENDENT tracks (can start while chapters accrue, in this order of
value):** the 3 chassis/pack leak fixes (§0), the transaction trio, and factory
Stages 1–2 (intake rubric + requirements instantiation — both are calibratable
today against the five worked genre-derivation examples in
`specs/genre_derivation.md` without a single new chapter).

## 4. NON-AUTOMATABLE RESIDUE (honest limits)
The mechanism invention (Stage 3) and correspondence audit can be drafted and checked
but not *guaranteed* — a coherent, source-faithful, well-audited book can still be
artistically dead. The taste flights exist precisely so a human can smell that early.
The factory's defaults carry real authorial weight; the ledger is what keeps that
honest.
