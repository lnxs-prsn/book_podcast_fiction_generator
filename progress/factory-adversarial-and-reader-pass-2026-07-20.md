# ADVERSARIAL + READER-OUTCOME PASS — two NEW lenses (2026-07-20)

**Why this exists.** The three prior treatments (individual/spec, interaction/company,
WIP/part) were all one *method* — situation-personification — cast three ways: three
vocabularies, one family, all **introspective/descriptive**. This pass runs two
structurally different lenses to surface problems that family *couldn't* see:

1. **ADVERSARIAL / failure-injection** — not "what could go wrong" but "I am an
   attacker (a bad Extractor output, or a state that induces a wrong-but-passing
   brief); how do I get corruption *past the gate*?" Grounded in the actual
   `structural_gate.py`, `extractor.md`, `updater.md`, and live `master_state.json`.
2. **READER / product-outcome** — sit in the seat of the person *reading the finished
   teaching-novel*, and rank defects by damage to *their* experience, not internal
   tidiness.

**Discipline.** Every finding carries a concrete break (input → wrong output) or a
concrete reader consequence, plus a code/state anchor. UNCOMMITTED, propose-and-correct.
Companion to `factory-open-problems-synthesis-2026-07-20.md`; tags here are **ADV-n**
and **RDR-n** (distinct from WIP-n / CH8-n / Q-n so nothing is double-counted).

**Live-state facts these findings lean on (verified this session):**
- `char_008` is really named **"Nantale Namakula"** — the treatments' "Nantale"
  example is a real character, not a toy.
- ch9 pointer (in `master_state.json`): `return_to_character`, `char_id: char_004`
  (Wanjiku Mwangi), `operation_due: op_separate_condition`, `touch_due: 2`,
  `name_due: true`, `failure_mode_to_show: "none"`, `secondary_touches: []`.
- `structural_gate.py` fires its quota check for **both** `new_focal_character` **and**
  `return_to_character` (`structural_gate.py:74`).

---

## ADVERSARIAL findings

### ADV-1 — The gate never binds `focal_character.id` to the pointer or to population_index (a FREE check left on the table)
- **The break:** ch9 is a return; the Extractor sets `focal_character.id`. Nothing
  checks that it equals the pointer's `char_id` (`char_004`) or that a return's id
  exists in `population_index`. If the Extractor writes `char_005`, or wrongly sets
  `is_new: true` with a fresh `char_009` for a character who is actually a return, the
  gate passes. Then Updater STEP 1: `is_new=false` → reads/updates the **wrong**
  character's card; `is_new=true` (wrong) → **creates a duplicate** card + a duplicate
  `population_index` row.
- **Anchor:** `structural_gate.py` checks quota/anchor/echo/life-progression/newcomer —
  never id-vs-pointer or id-∈-population. `updater.md` STEP 1 branches on `is_new`
  with no reconciliation.
- **Why the personifications missed it:** WIP-1/2 framed the risk as "prose is never
  re-read" (a *paid* problem). This is different and sharper — the gate **already holds
  the pointer and population_index deterministically** and simply doesn't cross-check
  them. It's a FREE guard the one-way-door framing walked right past.
- **Severity:** HIGH, imminent (fires on ch9). Cheapest possible fix.

### ADV-2 — The anti-under-population gate counts list *length*, not *distinct valid* approaches
- **The break:** the gate's core purpose is catching under-population (docstring: "ch4
  passed the floor with a third of its ordered cast"). It checks
  `len(failure_modes_shown_this_chapter) < quota`. A brief with
  `["the executor", "the executor"]` — a duplicate, or an invalid/uncanonical string —
  satisfies `len == 2 >= 2` for arc 2 while the prose showed only **one** wrong
  approach. Under-population passes.
- **Anchor:** `structural_gate.py:76-82` (`len(shown)` only); Extractor's canonical
  closed list (`extractor.md:89-98`) is never re-validated at the gate.
- **Why missed:** the treatments treated the gate as "honest but shallow (counts, not
  meaning)." True — but they never adversarially *fed it a padded list*. Distinctness +
  canonical-membership are deterministic checks the gate could do and doesn't.
- **Severity:** MEDIUM. Free fix (set-length + membership against the closed list).

### ADV-3 — ch9's arc-2 quota-2 structurally collides with a correct-applying return focal
- **The break (imminent, ch9-specific):** the gate requires
  `len(failure_modes_shown_this_chapter) >= 2` for `return_to_character` too. But ch9's
  pointer says the **focal** shows `failure_mode_to_show: "none"` — Wanjiku returns to
  *correctly* apply and **name** (`name_due: true`) op_separate_condition. So both
  required wrong-approach scenes must be carried entirely by **newcomers**, on the
  *same* taught operation (`failure_modes_shown_this_chapter` is scoped to the taught
  op). A clean, emotionally-focused return chapter that imports fewer than two fresh
  failers on op_separate_condition **fails the gate** — after the paid Writer run.
- **Anchor:** `structural_gate.py:74` (return included in quota check);
  `master_state.json` ch9 pointer; `extractor.md:234-238` (field scoped to the taught op).
- **Why missed:** every treatment analyzed *ch8* (a new_focal gate) retrospectively.
  None simulated *ch9 forward*. The quota rule was designed around new_focal chapters;
  its interaction with a name-payoff return was never exercised.
- **Severity:** HIGH, imminent. This is a design question (should quota apply, or apply
  differently, to a touch-2+ return?), not just a code fix — it needs an owner ruling
  *before* ch9 is written, or the paid run risks a designed-in gate FAIL.

### ADV-4 — The receipt is byte-tamper-evident but not freshness-bound to the chapter
- **The break:** `verify_receipt()` confirms `verdict == PASS` and that the brief's
  sha256 still matches. It does **not** compare `receipt["chapter"]` (which it stores!)
  against the chapter the Updater is about to apply, nor against master_state. A stale
  PASS receipt + its brief surviving from chapter N into an N+1 run that reaches step
  12.0 without regenerating → `--verify` passes on the **old** brief → the Updater
  re-applies chapter N.
- **Anchor:** `structural_gate.py:35-61` (no chapter/freshness comparison);
  `receipt` stores `chapter` (`:112`) but nothing reads it back.
- **Why missed:** WIP-4 **celebrated** the receipt seal as "the thing built right."
  It is — against *byte tampering between gate and Updater in one run*. The adversarial
  lens finds its boundary: it says nothing about *cross-run staleness*. A one-line
  `receipt["chapter"] == expected` check closes it.
- **Severity:** MEDIUM (guarded today by the orchestrator regenerating; latent if that
  discipline ever slips). Free fix.

### ADV-5 — The Updater is non-idempotent with no per-step recovery guard (crash mid-fan-out double-applies)
- **The break:** the Updater writes ~10 files across STEP 1–9 sequentially and is "the
  only non-idempotent agent." A crash at, say, STEP 5 leaves character card / concept
  card / event card / location card **already written**, but chapter_count (STEP 7) not
  yet incremented. On re-run the receipt still verifies (brief unchanged), so the
  Updater re-executes from STEP 1 → **double-appends** gate_history, **double-increments**
  `current_touch` (STEP 2 "Increment current_touch by 1"), double-appends
  teaching_history, etc.
- **Anchor:** `updater.md:18-21` (precondition is only `--verify` exit 0),
  STEP 1/2/7 are unconditional appends/increments; no "already applied this chapter?"
  check.
- **Why missed:** all three treatments modeled a *wrong-but-complete* brief. None
  modeled a *correct brief, partial write* — an orthogonal failure axis. The one-way
  door is about content; this is about atomicity.
- **Severity:** MEDIUM-HIGH (silent count corruption; hard to detect after the fact).
  Fix = an idempotency stamp (e.g. "last_applied_chapter" guard) or a transaction.

---

## READER / PRODUCT-OUTCOME findings

### RDR-1 — The highest-damage bug breaks a character's *continuity of learning* — and ch9 is exactly that payoff
- **Reader consequence:** ch9 is Wanjiku's return to finally *name* op_separate_condition
  (`name_due: true`) — five chapters after her ch4 touch-1 setup. If ADV-1 fires (mis-id
  → duplicate/mis-card), the reader meets "a new Wanjiku" with no memory of ch4; her
  touch-2 progression never lands on her card; the emotional payload of a return — the
  whole reason returns exist — is silently severed.
- **Why this matters for ranking:** it converts ADV-1 from "a data bug" into "the single
  worst *reader* outcome available right now," because the damage lands on a
  *named-payoff* return, not an ordinary chapter. The reader lens says: guard **returns**
  first, and among returns, **name-due** returns first.
- **Anchor:** `master_state.json` ch9 pointer (`name_due: true`, char_004 last_seen 004).

### RDR-2 — Anti-formula machinery is *recorded*, never *enforced* against the prose
- **Reader consequence:** the `failure_mode_to_show` least-recently-led rotation exists
  so the reader doesn't experience the same featured failure repeatedly. But the
  Extractor only **records** `lead_failure_mode` from what the Writer wrote — it cannot
  *force* variety. `failure_mode_lead_history` shows "the executor" led ch1, ch2, **and**
  ch3 (`master_state.json:25-27`) — three consecutive chapters of the same archetype
  actually shipped. Nothing ranks or blocks prose that repeats the featured failure.
- **Why the personifications missed it:** they read the rotation as working machinery
  (it computes the *right* next lead). The reader lens asks whether the *prose obeyed*
  — and finds the loop is descriptive, not prescriptive. Formula-repetition is a
  top-tier quality defect in a teaching novel (samey chapters stop teaching), and it is
  entirely unguarded.
- **Anchor:** `master_state.json:24-31` (executor ×3); `extractor.md:369-383` (records,
  doesn't enforce).
- **Severity:** MEDIUM (quality, cumulative). No deterministic check possible on
  "featured-ness," but a *repeat-lead warning* (same lead N chapters running) is cheap.

### RDR-3 — Mystery-fairness is entirely unguarded — and *cannot* be guarded by the current design
- **Reader consequence:** for a *mystery*, the payoff must be fair — accumulated clues
  must stay consistent with the hidden solution. `macro_mystery_evidence` has grown to 8
  entries (ch1–8). But **no stage checks the planted evidence against the hidden answer**,
  because the one file holding the answer — `mystery_anchor.json`'s `hidden_coherence` —
  is walled off from *every* agent ("Do not read hidden_coherence under any circumstances",
  `extractor.md:24, 538`). The mystery can drift into incoherence and no stage will
  catch it; the reader discovers the betrayal at the end of the book.
- **Why no internal lens could see it:** the personifications never took the
  *reader-of-a-mystery* seat. And it's structurally invisible from inside: the coherence
  authority is deliberately unreadable, so the pipeline has *no* organ that can verify
  fairness. This is a design gap, not a bug — the fairness check would need a privileged
  reader that today does not exist.
- **Anchor:** `extractor.md:24` + `:538`; `master_state.json:89-118` (8 evidence entries,
  never cross-checked against a solution).
- **Severity:** HIGH but long-horizon (bites at book-end, not per-chapter). The deepest
  finding of this pass.

### RDR-4 — Cumulative world-thinning via silent nulls/defaults (minor)
- **Reader consequence:** "never invent" fields (age → null, `extractor.md:69-70`) and
  Updater defaults (location `institutional_response` / `characters_based_here` "left at
  schema defaults — not derivable", `updater.md:131-132`) accumulate. Over a book the
  world's texture thins and no stage measures cumulative richness.
- **Severity:** LOW. Noted for completeness; a reader-lens-only observation.

---

## What this pass changes (vs the personification queue)

**Two findings are imminent and land on the very next chapter (ch9):**
- **ADV-3** (arc-2 quota-2 vs correct-applying return) needs an **owner ruling before
  ch9 is written** — otherwise the paid Writer run risks a *designed-in* gate FAIL.
- **ADV-1 + RDR-1** (focal-id not cross-checked; the damage lands on a name-due return)
  is the concrete, FREE, highest-reader-value guard — and it is a *deterministic* check
  the gate can already do, distinct from (and cheaper than) the paid one-way-door read.

**Net:** the earlier queue's lead candidate — "free verify-from-source name-presence
check" — is *correct but under-specified*. This pass sharpens it into two concrete,
free, deterministic gate checks that should ship together, and surfaces a **design
question (ADV-3) that must be answered before ch9 at all:**

1. **Gate cross-field integrity check (free):** `focal_character.id == pointer.char_id`
   on a return; return-ids ∈ population_index; new-ids ∉ population_index;
   `failure_modes_shown` entries distinct + ∈ the canonical closed list (ADV-1, ADV-2).
2. **Gate freshness bind (free, one line):** `receipt["chapter"]` must match the chapter
   being applied (ADV-4).
3. **Updater idempotency stamp (small):** refuse to re-apply an already-applied chapter
   (ADV-5).
4. **OWNER DECISION needed pre-ch9:** does the arc-2 wrong-approach quota apply to a
   touch-2+ *return* whose focal correctly applies — and if so, is it satisfied by
   newcomers on the taught op, or should the check be relaxed for returns? (ADV-3.)
5. **Longer-horizon, design:** a privileged mystery-fairness reader (RDR-3);
   a repeat-lead anti-formula warning (RDR-2).

**Genuinely new vs. re-framed:** ADV-1..5 and RDR-1..3 are **new problems** — none
appear in the WIP/CH8/Q registers. They cluster on two axes the introspective family
structurally could not reach: *deterministic checks the gate already could do but
doesn't* (ADV-1/2/4), *atomicity/crash* (ADV-5), and *the reader's experience of the
finished artifact* (RDR-1/2/3). The single most valuable output of the whole pre-build
pass is now concrete: **ch9 has both a free guard gap AND an unresolved design question,
and both fire on the next run.**
