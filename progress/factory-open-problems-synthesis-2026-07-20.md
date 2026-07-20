# FACTORY OPEN-PROBLEMS SYNTHESIS — draftable inventory (2026-07-20)

**Purpose.** Consolidate every problem the pre-build personification pass surfaced
that has **no ticket** (not even a proposed one), plus the cross-cutting analysis
(overlap, resolve-vs-intensify, ordering, and which *existing* assets already point
at each fix), into one place a spec or ticket can be drafted from directly.

**Provenance / trust.** Built from the three 2026-07-19 treatments —
`factory-spec-personification-2026-07-19.md` (INDIVIDUAL, tags CH8-n),
`factory-cast-and-fit-2026-07-19.md` (INTERACTION, Q1–Q5),
`factory-wip-personification-2026-07-19.md` (WIP, tags WIP-n) — and this session's
synthesis. Every problem carries its source tag + a code/spec anchor that was
mechanics-checked in the source treatment. **UNCOMMITTED, propose-and-correct.**
Nothing here is dispatched. The *fact layer* folds into the spec immediately; the
*judgment/priority/design layer* waits for owner (handoff §12 discipline).

**Out of scope here (already PROPOSED as tickets, listed only for completeness):**
T-019 retire `QUOTA_BY_ARC` leak · T-020 anchor leak · T-021 mirror leak ·
T-022 pre-writer prompt gate (spec's designated FIRST build) · T-023 regression
fires the gate's own checks incl. a rule-5 curriculum-consistency fixture.

---

## 0. The consolidated root (read this first)

Root-cause-laddering across the no-ticket list plus the proposed leak tickets lands
on **one fault** under a whole cluster:

> **A truth is kept in two copies, and the copies are held in sync by human memory
> instead of by one owning source + a check.**

This single root generates: the three leaks (private copies of pack content), **P6**
(spec drifts from recipe — *literally how `QUOTA_BY_ARC` drifted silently for a
year*), **P7** (four half-layers each remembering the "re-verify downstream" duty),
and **P9** (the doubled `next_chapter_pointer` — a *benign* instance of the same
shape). The WIP treatment stated it plainly: *"the factory's whole recurring wound
is values kept in two copies."*

The remaining problems split into two other families:
- **Unbuilt organs** — P1 (Stage-5 inspectors), P2 (calibration), P8 (upstream
  Stages 0–6), and P5 (the deterministic-code substrate everything runs on).
- **Validation gates** — P3 (anchor_interlude never fired), P4 (LAW 15 sweep).

So the nine "separate" items are really **one root (sync-by-memory) + two
unbuilt-organ stacks + two validation gates**.

---

## 1. The nine no-ticket problems (each a draftable record)

Numbering matches the list handed to the owner this session. Category ∈ {SYNC-ROOT,
UNBUILT-ORGAN, VALIDATION-GATE, BOOKKEEPING}.

### P1 — Semantic-verification gap / the "one-way door"
- **Category:** UNBUILT-ORGAN (it *is* the Stage-5 inspector wing).
- **Source:** WIP-1, WIP-2; CH8 Stage-5; company Q2.
- **What:** The Extractor (step 11) is the ONLY stage that reads chapter prose after
  the Writer. It writes `update_brief.json`; the Updater fans that into ~10 files and
  is *forbidden to re-read prose*; the Structural Gate (11.5) only **counts**
  (`len()`/booleans), never checks the summary against the story. A wrong summary
  field (mis-transcribed name, "Nantale"→"Nantare") becomes canon in ~10 files
  uncaught. **Highest-damage class = wrong/lost names on RETURNS.**
- **Anchor:** manifest "first and only stage prose is read"; `updater.md` CRITICAL
  RULES ("never read prose; work from update_brief only"); `structural_gate.py` reads
  only `len(shown)`/booleans; spec Stage-5 Fidelity/Logic/Correspondence = build 0.
- **Existing asset that guides the fix:** the **receipt-seal pattern** (WIP-4,
  proven-built) — "compute a hash / refuse to proceed unless it matches" transfers
  directly to "assert every summary name occurs in the prose / refuse to fan out
  otherwise." Spec already designs the paid depth (Stage-5). The free guard is
  described in-spec as *a deterministic slice of the Stage-5 Fidelity Inspector*.
- **Candidate fix (two depths):** (a) **FREE/deterministic** — prose text-search that
  every name/place the summary asserts occurs in the chapter file (zero tokens);
  (b) **PAID** — a second model re-reads the chapter, verifies the summary's *meaning*
  (real Stage-5 cross-read).
- **Draftable as:** ticket (the free slice, now) → spec build row (paid Stage-5).
- **Note:** distinct from an earlier self-consistency check that never reopens the
  story (weaker — cannot catch a wrong name).

### P2 — Calibration / learning organ does not exist
- **Category:** UNBUILT-ORGAN (the Archivist chair).
- **Source:** WIP-6; CH8-7 (descendant of SG-11); company Q2.
- **What:** The organ that stores worked examples so book N+1 learns from book N is
  **defined in spec but the `calibration/` directory does not exist.** Briefs are
  overwritten every chapter, no archive. The factory "claims it learns" with no floor.
- **Anchor:** `extractor.md` OUTPUT "overwrite completely"; `calibration/` absent;
  SG-11 closed by *definition* only.
- **Existing asset that guides the fix:** SG-11 already specifies the organ (what it
  holds, when it's read). **Chapters 1–8 exist NOW as seed data.**
- **Candidate fix:** create the organ + write ch1–8 as its first entries; have the
  Extractor archive each brief instead of only overwriting.
- **Draftable as:** ticket (create dir + archive-on-write + backfill 1–8) — but see
  §4: value decays every chapter it's deferred.

### P3 — `anchor_interlude` chapter type has never fired
- **Category:** VALIDATION-GATE.
- **Source:** WIP-7; CH8-5; company Q2.
- **What:** One of four chapter types has never once run. Its **null-bodied brief
  shape** (`focal_character`/`gate_details`/`process_updates`/`location_updates` all
  `null`) is real branch code in both Extractor and Updater but has **never been born,
  inspected, or consumed in production.** A whole configuration is untested track.
- **Anchor:** Extractor/Updater null-section guards real; validation checklist
  "anchor_interlude never fired."
- **Existing asset that guides the fix:** the type is fully designed; firing it is a
  scheduling/trigger action, not a build.
- **Candidate fix:** fire one anchor_interlude (scheduled or deliberate trigger)
  **behind P1's guard** (see §4 — it exercises the untested null shape through the
  one-way door). Gate any "recipe proven" claim on it.
- **Draftable as:** validation task (paid, owner-started), sequenced late.

### P4 — LAW 15 machinery sweep is undone
- **Category:** VALIDATION-GATE.
- **Source:** CH8-6.
- **What:** The LAW 15 machinery sweep has been "pending" since before the last spec
  revision and has never run. Blocks the milestone→proven transition.
- **Anchor:** spec §3; CH8-6 register.
- **Existing asset that guides the fix:** the **regression suite (T-016)** is the
  bench this sweep runs on; LAW 15/16 already framed.
- **Candidate fix:** run the sweep; register any gaps as regression fixtures.
- **Draftable as:** validation task; overlaps the regression bench.

### P5 — The chassis is agent-prose, not deterministic code (Force 5)
- **Category:** UNBUILT-ORGAN / SUBSTRATE.
- **Source:** CH8-4.
- **What:** `deterministic_pipeline.spec.md` and `assembler_template.spec.md` both
  still say "not yet implemented." So "chassis BUILT" actually means **"RUNS as
  loosely-interpreted agent prose,"** not the deterministic functions the blueprints
  call for. Force 5 (deterministic steps run by LLMs) is still true of the foundation.
- **Anchor:** both sub-specs "not implemented"; CH8-4 register.
- **Existing asset that guides the fix:** **the two sub-specs are already-written
  blueprints** — design done, only build remains.
- **Candidate fix:** implement `deterministic_pipeline` / `assembler_template` — OR
  state plainly the chassis is agent-driven by design. **Building
  `assembler_template` also dissolves the assembler leaks** (T-020/021) by pulling the
  "filing-cabinet half" out into code that reads the pack.
- **Draftable as:** spec build rows (large); the leak tickets are down payments on it.

### P6 — Spec-drift enforcement is human-memory only
- **Category:** SYNC-ROOT.
- **Source:** CH8-8 (descendant of SG-14).
- **What:** SG-14's rule (any recipe change updates the spec the same session) has
  **no mechanical check** — which is exactly how `QUOTA_BY_ARC` drifted from the
  curriculum silently for a year. A single source of truth kept faithful by memory and
  goodwill is one forgotten session from lying again.
- **Anchor:** CH8-8; DECISION 10 root cause; SG-14 is a human habit.
- **Existing asset that guides the fix:** **LAW 16** ("a new rule ships its check or
  its excuse") dictates the fix shape; the **regression suite (T-016)** is where the
  check plugs in.
- **Candidate fix:** a mechanical staleness check — last-recipe-change (e.g. mtime/
  hash of recipe files) vs last-spec-touch — as a regression fixture.
- **Draftable as:** ticket (regression fixture); systemic version of the leak fixes.

### P7 — The "re-verify downstream" duty is spread across four half-layers
- **Category:** SYNC-ROOT (redundancy / not-yet-collapsed).
- **Source:** company Q1.
- **What:** One job — "a change re-verifies everything downstream of it" — is held by
  four people at four maturity levels: field_registry RULE-CHANGE AUDIT (manual
  habit), LAW 17 (constitutional rule), the Regression Suite (automatic slice), and
  the Stage-6 consumer map (supposed-to-be running code). Not bloat *yet* — one role
  maturing across four layers — but the warning is: **collapse into one consumer-map
  organ**, don't staff four who each half-remember the duty.
- **Anchor:** all four named in field_registry / CONTRIBUTING / intake_factory §6;
  they genuinely overlap in intent.
- **Existing asset that guides the fix:** **LAW 17 + field_registry's Downstream
  field is already the design** for the consumer map. The fix is to make LAW 17
  *executable* as one organ.
- **Candidate fix:** a Stage-6 consumer-map organ that subsumes the manual audit;
  keep LAW 17 as its constitutional statement, the regression suite as its teeth.
- **Draftable as:** spec build row (Stage-6); do it *ahead of* more P8 build (see §4).

### P8 — Seven empty chairs: the entire upstream (Stages 0–6) is unbuilt
- **Category:** UNBUILT-ORGAN (the superset).
- **Source:** company Q2/Q4; CH8-1.
- **What:** Receptionist (Stage 0), Classifier (1), Estimator (2), Architect (3),
  Draftsman (4), three Inspectors (5), Account-Manager-as-code (6), Archivist — all
  job descriptions on vacant desks. **The human silently works every one.** Build
  list = 14+ rows, built = 0. This is the factory-build itself; P1, P2, P7 are
  specific chairs *inside* it.
- **Anchor:** intake_factory §2 build list; company Q2/Q4 ("the automated factory
  currently contains an artisan").
- **Existing asset that guides the fix:** the **full intake_factory spec build list
  is the work map**; `genre_derivation.md` (5 worked books) is the Architect's manual;
  the spec names the **pre-writer prompt gate (T-022) as the designated FIRST row.**
- **Candidate fix:** incremental — highest-value chair = whichever removes the most
  human overtime; intake wing (Receptionist/Classifier) makes the front door real;
  Draftsman (Stage 4) is the biggest rock and the real leak-fix.
- **Draftable as:** the standing spec build program; individual chairs = tickets.

### P9 — Doubled `next_chapter_pointer` "not-a-leak" note
- **Category:** BOOKKEEPING (NOT a defect).
- **Source:** WIP-5.
- **What:** The pointer lives in both the brief (transient) and master_state
  (canonical). By design — single author → canonical store, no drift path. Worth **at
  most a one-line `field_registry` "not-a-leak" note** so a future leak-sweep does not
  false-fix it.
- **Anchor:** `update_brief.json:93–104` == `master_state.json:119–130`; Updater STEP 7
  copies it; single-author no-drift argument.
- **Candidate fix:** the one-line note. **Must precede any leak-sweep.**
- **Draftable as:** trivial doc edit.

---

## 2. Overlap map

| Problem | Overlaps | Relationship |
|---|---|---|
| P1 semantic verification | P8 | P1 *is* the Stage-5 inspector wing — a subset of the empty chairs |
| P2 calibration organ | P8 | The Archivist — another empty chair; not independent |
| P7 four-layer re-verify | P8 | The 4th layer (Stage-6 consumer map) is itself an empty chair |
| P5 agent-prose substrate | all builds | Everything above runs as prose until P5; dissolves assembler leaks |
| P3 / P4 | each other | Sibling VALIDATION-GATEs; mechanically independent |
| P6 / P7 | the leaks | Same sync-by-memory root; the *systemic* form of the per-tool leak fixes |
| P9 | the leaks | A *benign* instance of the two-copies shape; note-not-fix |

**P8 is the superset.** P1, P2, P7 are specific chairs inside it; fixing them
piecemeal *is* the incremental build of P8.

---

## 3. Resolve vs intensify (do-one-affect-others)

**Resolves (do-one-get-others):**
- **P5 dissolves the assembler leaks.** Building `assembler_template` pulls the
  filing-cabinet half into code that reads the pack → T-020/021 become down payments,
  not separate work.
- **Building P8's Stage-4 Draftsman (with the manifest) resolves the leaks AND
  produces P2's calibration inputs.** The pack becomes the single source the chassis
  reads. T-019 is explicitly "a Stage-4 manifest down payment."
- **Fixing P6/P7 systemically prevents the NEXT leak.** Fixing leaks case-by-case does
  not resolve P6/P7; fixing P6/P7 (a mechanical staleness / consumer check)
  generalizes across all future hoards.

**Intensifies (sequencing traps — the important part):**
- **Firing anchor_interlude (P3) without P1's guard intensifies risk** — P3 exercises
  the never-shipped null-bodied brief shape (WIP-7) through the same one-way door that
  has no semantic check. New shape × no guard = worst place to discover the door open.
- **ch9 intensifies P1 right now** — ch9 is a *return*; P1's highest-damage class is
  wrong/lost names on returns. Running ch9 before the free guard walks the open door.
- **Building more upstream (P8) without P7's consumer-map organ multiplies the sync
  surface** — more chairs, more copies, more human sync-passes. P7 should *lead* the
  P8 build, not trail it.

---

## 4. Chronological / dependency order

Driven by dependency and by "guard before you exercise":

1. **P9 first** (one-line not-a-leak note) — trivial, and must exist *before* any
   leak-sweep so the sweep doesn't false-fix a by-design value.
2. **P1's free slice** (verify-from-source name-presence check) — *before* ch9 and
   *before* P3, because both exercise the door.
3. **Leak stopgaps (T-019 first) and/or the P5 substrate build** — leaks are the
   tactical fix; P5 is the strategic one that dissolves them. **P7's consumer-map
   organ belongs here, ahead of more P8 build.**
4. **P2 calibration seeding** — wants to exist *soon*: ch1–8 are the seed data and
   accrue value now; every chapter run without the organ throws a worked example away.
5. **P8 upstream build** — the big rock; spec names **T-022 (pre-writer prompt gate)
   as the designated first row.**
6. **P3 and P4 last** — these are the *proof* steps; you fire anchor_interlude and run
   the LAW 15 sweep to *declare* book-1 validated, so they close the sequence.

---

## 5. Existing assets → fix mapping (why almost nothing needs net-new invention)

The treatments' unanimous verdict: **"design closed, build didn't."** What we already
hold that points directly at each fix:

| Asset (exists today) | Guides |
|---|---|
| **LAW 14** (generalization pain = chassis/pack leak; look there) | names the leak class; predicted ch8's shape correctly |
| **LAW 16** (a new rule ships its check or its excuse) | the fix *shape* for P6, P7, rule-5 |
| **LAW 17 + field_registry Downstream** | *is* the design for P7 (consumer map) |
| **Receipt-seal pattern** (WIP-4, proven-built) | reference implementation for P1's guard |
| **Regression suite** (T-016) | the bench P6's staleness check + P4 sweep + rule-5 fixture plug into |
| **`deterministic_pipeline` + `assembler_template` specs** | written blueprints for P5 |
| **`intake_factory.spec.md` Stage-5** | full design of P1's paid depth |
| **`intake_factory.spec.md` §2 build list** | the work map for P8 |
| **`genre_derivation.md`** (5 worked books) | the Architect's manual (P8, Stage 3) |
| **Chapters 1–8** | seed data for P2's calibration organ |
| **innovations/** (situation-personification, root-cause-laddering, ticket-dispatch Upstream/Downstream, handoff-discipline) | the method that found + will scope these |
| **analyst.py / progress.py** | diagnostics; "consult the doctor before blaming the loud worker" (Q5) |

**One-line guide:** the **17 laws** (esp. 14/16/17) give the *shape* of every
sync-family fix; the **intake_factory spec + its two deterministic sub-specs** are the
*blueprints* for the unbuilt organs; the **regression bench + receipt-seal** are
*working references to copy*; **field_registry** is the *consumer-map seed*.

---

## 6. What is draftable now, and as what

- **Tickets, ready now (zero-paid, chapter-independent):** P9 note · P1 free
  name-presence guard · P6 spec-staleness fixture. (Plus the already-proposed
  T-019/020/021/023.)
- **Spec build rows (larger, owner-prioritized):** P5 (deterministic substrate) ·
  P7 (Stage-6 consumer-map organ) · P8 (the upstream program; T-022 first) · P1's
  paid Stage-5 depth · P2 (calibration organ).
- **Validation tasks (sequenced late, gate "recipe proven"):** P3 fire
  anchor_interlude (behind P1's guard) · P4 LAW 15 sweep.

**Lead candidates for the *next* move** (both zero-paid, both sharpened by ch9 being a
return): **P1's free name-check** (highest-value/lowest-cost, most relevant now) and
**T-019** (ripest proven-live leak, starts retiring the human sync-pass burden).
