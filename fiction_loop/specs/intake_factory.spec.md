# INTAKE FACTORY SPEC — knowledge book in, teaching fiction out

Goal (owner, 2026-07-03): a user gives the system a knowledge book and gets a
serialized teaching novel — without authoring any core templates and **without being
interviewed**. Everything downstream of the templates already exists and is
book-agnostic (the fiction_loop chassis). This spec defines the front half: how the
templates, state, and decisions get *derived* from the book.

Calibration source: this repo IS the factory's first worked example, run manually with
a human in the loop (Pólya → The Sankofa Gates). Every stage below names the artifact
from that run that exemplifies its output.

2026-07-10: gaps found by the user-story exercise (`progress/factory-user-manual.md` +
`progress/factory-user-stories.md`, findings SG-1..SG-14) folded in below — each
addition cites its SG. Defaults introduced by that pass are owner-correctable.

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

## 1. PIPELINE (stages 0–7, three automated verifications, zero mandatory questions)

### Stage 0 — Intake surface, instancing, budget (SG-1 / SG-5 / SG-6 / SG-12)
- **Front door = MENU (owner correction 2026-07-10):** the kickoff opens a menu
  with two choices — **(a) CONTINUE an existing fiction generation** (lists the
  provisioned instances, each with its progress-view line: chapters done,
  curriculum bar, current step; resumes the chosen one) or **(b) START NEW**
  (user provides one book file, pdf/epub, + optional free-text wishes). Nothing
  else is accepted or required. Precedent: the repo's own menu.py interactive
  launcher — same entry-point pattern, extended with instance awareness.
- **Instancing:** 1 book = 1 provisioned instance (own state dir + chassis clone) —
  the chassis state is a singleton per instance BY DESIGN. Multiple books queue
  sequentially; concurrency is out of scope for v1.
- **Budget:** intake emits a cost + time estimate BEFORE any paid stage runs; every
  paid stage sits behind a spend gate (constitution: gates-before-spend); budget
  exhaustion halts and notifies, never silently continues.
- **Delivery contract:** chapters are delivered as files as the gates accept them;
  the progress view is the user-facing status face. Nothing already delivered is
  ever silently rewritten (see Stage 6, correction economics).

### Stage 1 — Ingest & classify
Extract book text (format_adapters/ already exists for pdf/epub). Classify the knowledge by
what MASTERY looks like behaviorally:
process (executes moves under pressure) / thing (sees the concept everywhere) /
perception (discriminates) / relational (process on other minds) / discipline
(compounds over time). Extract the book's own **failure catalog** — how it says people
get it wrong (Pólya's bad solvers → the 14 wrong-approach types). Select pedagogy pack.
*Worked example: concept_curriculum.md §3–§4 content.*

**Intake contract (SG-2 / SG-3; outcome set corrected by owner 2026-07-10 — the
taxonomy is EXTENSIBLE, never a dead end):** classification ends in exactly one of
three user-visible outcomes — **accept** (the type's pack exists), **queue** (type
valid, pack not built yet; user told which pack, no date promised), or **defer**
(the factory has not yet figured out how to classify this book). There is no
unclassifiable book — only a taxonomy that hasn't caught up. The five types are the
CURRENT catalog, not a closed one: a deferred book is logged as a taxonomy-extension
case (what WAS observed: candidate mastery behaviors, failure-catalog findings) and
the user is told the limitation is the factory's, not the book's. An empty failure
catalog defers the same way — some books need a pedagogy the factory hasn't invented
yet. Each new type resolved from the defer log = a new pack variant (§0). Hybrid books: primary type = the type
whose mastery behavior the failure catalog mostly attacks; the hybrid call is
recorded in the decisions ledger, never made silently. (The ambiguity is real:
genre_derivation.md's own table lists Thinking, Fast and Slow as perception/process.)

### Stage 2 — Requirements derivation
Instantiate the requirements list (near-invariant, weighted by type):
(1) problems playable without domain expertise, (2) guaranteed solvability = the
reader's contract, (3) externalized mental state, (4) episodic variety + ensemble,
(5) adjacency to ordinary life for transfer proof, (6) real stakes, (7) serial
macro-mystery scaffold.

**Sizing is derived, not inherited (SG-7):** touch targets, difficulty ladder, and
chapter projection are re-derived from the extracted curriculum's size (operations ×
touch ladder → events → chapters). D9's numbers (71 events, ~20–30 chapters) are the
Pólya worked example of the formula, not constants.

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

**Repair loop (SG-8):** a flag triggers auto-repair (re-derive the claim from a
located quote) → re-verify; after 2 failed repairs (default) the item surfaces to
the user as a correction proposal in the ledger. A book never ships with an open
flag — and never stalls silently on one either.

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
6. **Default deadness reviewer (SG-9).** The taste flights are the only defense
   against a coherent-but-artistically-dead book — and the all-defaults user never
   opens them. When the user is silent, the factory itself runs one flight review
   (strongest available model, distinct from the generator) and ledgers the verdict
   as "unreviewed by human." Mandatory for the factory, still optional for the user.
7. **Correction economics (SG-10).** Reversibility tags carry behavior, not just a
   warning: *cheap* → apply + propagate everywhere; *expensive* → forward-only
   (future chapters comply; delivered chapters stand) or refuse-with-explanation —
   the factory states which, in the ledger, at correction time. Delivered chapters
   are never silently rewritten.

### Stage 7 — Init & run
init_state.py generalized to read the Stage-4 operation manifest instead of embedded
tables → process_state, concept cards, registry. Then the existing loop (RUN.md).

**Redo-rung policy (SG-4 — keeps "zero mandatory questions" true through gate
failures):** on a structural-gate failure the orchestrator auto-runs S1 (redo
generation) once, then S2 (redo from brief) once; only after both fail does it
halt-and-notify, with the analyst's verdict attached. Defaults owner-correctable.

**Calibration pack (SG-11 — the organ behind "the fifth book is near-turnkey"):**
every processed book leaves a defined artifact set — classification, derivation +
kill-table verdicts, invented mechanism, decisions ledger, incident list — in
`calibration/<book>/`; Stages 1–3 of the next run read all existing packs.

---

## 2. BUILD LIST (what does not exist yet)

| Item | Notes |
|---|---|
| Stage-0 menu (continue existing / start new) + instance provisioning + budget estimator/spend gates | new (SG-1/5/6); extend menu.py pattern |
| Stage-1 intake agent spec + knowledge-type rubric + accept/queue/defer contract + taxonomy-extension (defer) log | new (SG-2/3) |
| Redo-rung auto policy in orchestrator | small (SG-4) |
| Calibration pack format + read path | new (SG-11) |
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

**Spec-sync rule (SG-14):** any recipe change during validation (spec fix, promoted
rule, new gate) must update THIS file in the same session — it is the factory's
single source of truth and drifts silently otherwise.

**Chapter-INDEPENDENT tracks (can start while chapters accrue, in this order of
value):** the 3 chassis/pack leak fixes (§0), the transaction trio, and factory
Stages 1–2 (intake rubric + requirements instantiation — both are calibratable
today against the five worked genre-derivation examples in
`specs/genre_derivation.md` without a single new chapter).

## 4. NON-AUTOMATABLE RESIDUE (honest limits)
The mechanism invention (Stage 3) and correspondence audit can be drafted and checked
but not *guaranteed* — a coherent, source-faithful, well-audited book can still be
artistically dead. The taste flights exist precisely so a human can smell that early
(and Stage 6 item 6 puts a default reviewer where a silent user isn't). The factory's
defaults carry real authorial weight; the ledger is what keeps that honest.

Also honest: rights/licensing of input books and ownership of output novels are
UNDECIDED — recorded as open owner decision **D10** (SG-13). The factory must not
ship to third parties before that call is made.
