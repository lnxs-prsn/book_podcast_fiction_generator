# HANDOFF — 2026-07-19 (COMPACTED current-state)

**This is a COMPACTION.** It snapshots current truth and replaces the
2026-07-18 running ledger (`handoff-2026-07-18-all-tickets-landed-ch7-next.md`,
§§1–14) as the front door. That ledger is ARCHIVED — still the detailed
*why* behind any claim here, but read this first. Compaction method: see
`innovations/handoff-discipline/kit/HANDOFF_RULES.md` §Compaction.
All claims below verified against git/state/code at commit `f739452`,
tree clean.

## 1. State (verified against master_state.json + git, 2026-07-19)

> **STALE as of later 2026-07-19 — see §11 for current state (8 chapters, ch8
> COMMITTED, factory spec-sync done). §1 below is the initial-compaction snapshot.**

- **7 chapters committed, `arc_current` = 2**, next pointer = `008`
  (new_focal_character, op_check_result). Analyst: state sync OK.
- **Chapter 008 is PARKED.** Three attempts were abandoned (handoff-archived
  §§6–9); the run restarts only after the queued tool tickets land (§5),
  then paid + owner-started, re-entering at the revision rung.
- **FINDING — stale file:** `fiction_loop/chapters/chapter_008.md` IS
  committed (at `d91e558`) but is the rejected **attempt-2 draft** (HARD
  RULE 1 label leak); `chapter_count`=7 correctly excludes it. The ch8 run
  overwrites it at step 9, so it self-resolves on restart — but nothing
  should treat it as canon meanwhile.

## 2. Roles (unchanged)

Owner assigns. Senior writes tickets in `tickets/`, re-runs acceptance
independently, updates this handoff, **never implements** — except
owner-delegated small tasks. Codex/Qwen implement, stay in the write-set,
**STOP-not-improvise** on any ambiguity or discrepancy. Harness-block
precedent: when an implementer's harness blocks a step (read-only uv cache,
git index, classifier false-positive), the senior runs it externally and
commits on their behalf with `Implemented-by:`.

## 3. Binding facts a cold session must know

1. **pytest is NOT a project dependency.** Sanctioned command:
   `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q`.
   Expected baseline: **`1 failed, 331 passed`** — the one failure
   (`test_default_splitter_engine_passes_openrouter_timeout_seconds`) is a
   known pre-existing legacy-subsystem failure, NOT a regression.
2. **Interpreter:** `.venv/bin/python` from repo root, usually
   `PYTHONPATH=src`. **uv only — never pip.** This machine is a Raspberry
   Pi: nothing heavy in parallel. **No paid calls unless a ticket/run
   budgets them.**
3. **Env namespace is `BOOKGEN_LLM_*`** everywhere incl. `.env` (T-003).
4. **Thinking tax ~2.5× billed-vs-visible tokens (deepseek-v4-pro) is
   EXPECTED**; the analyst WARNs at that ratio by design. Keep `max_tokens`
   ≥ ~2.5× expected output.
5. **Pipeline order (post-T-008): 8 Writer → 9 save → 11 Extractor → 11.5
   structural gate → 10 living-doc refresh → 12 Updater.** Gate runs BEFORE
   any paid post-writer call. Step numbers kept, position moved.
6. **The structural gate (11.5) is the anchor authority** and is
   receipt-guarded: it writes a brief-hash receipt on PASS / deletes on
   FAIL, and the Updater is unreachable without a fresh PASS (T-009). The
   prose anchor pre-check was RETIRED (T-017) — do not re-add it.
7. **arc_current self-manages** (T-006): the Updater advances it; the
   analyst enforces `arc_current = 1 + count(arc summaries)` and has an
   opt-in `--repair`.
8. **The run driver operates as Orchestrator ONLY** (T-011) — it runs the
   loop and improvises nothing; governance docs are out of its scope.

## 4. Operating model (adopted 2026-07-19 — the "govern change" layer)

- **Ticket template** (`innovations/ticket-dispatch/kit/TICKET_TEMPLATE.md`)
  now requires **Upstream** (preconditions the author dry-ran) and
  **Downstream** (consumers to re-verify, from field_registry) + acceptance
  item 4 (re-verify consumers). Kills the T-008/T-012/T-014 bounce class at
  authoring time.
- **LAW 16** — a new hard rule ships its check or its excuse. **LAW 17** —
  a shared-surface change re-verifies its consumers ("know who eats your
  output"); its enforcement is the Downstream field + the regression suite.
- **CAST & FIT lens** (`innovations/situation-personification/cast-and-fit.md`)
  — a reusable five-question personification diagnostic for fit/redundancy.
- **Pipeline capabilities now live:** deterministic label check +
  structured `--check-prose` (T-010/T-012); targeted-revision rung
  `--revise` with a 0.25 diff-guard (T-012, revise surgical misses, redo
  whole-scene omissions); truthful redo ladder + living-doc restore (T-007);
  unnamed-newcomer gate contract (T-004); single-outcome extractor pointer
  (T-005).

## 5. Open queue (all BETWEEN runs, offline, zero paid calls)

**Implementation order — T-018 → T-016** (both touch CONTRIBUTING.md;
serialize):
1. **T-018** — LAW 17 into CONTRIBUTING (constitution first).
2. **T-016** — tool regression suite (freezes the post-T-017 label-only
   contract; registers a LAW 15 line under LAW 17). The factory's first
   immune cell.

**Landed + senior-accepted this session:** T-017 (anchor-check retired;
`--check-prose` label-only restored; anchor machinery zero across
fiction_loop; baseline green). **Withdrawn:** T-015 (subsumed by T-017).

**Then — PRODUCT:** chapter 008 restart (paid, owner-started), after
T-018 + T-016 land.

## 6. Deferred (deliberately, not now)

- Full boundary-enforcement architecture — let the T-016 suite reveal the
  real seams first (priced-guardrails; don't zone before the roads prove
  themselves).
- A mechanical Upstream preflight — the template field + author dry-run
  cover it for now.
- Factory-scale handoff rotation + ticket archiving structure — see
  HANDOFF_RULES §Compaction for the current lightweight method; the heavier
  version is a post-ch8 concern.

## 7. Read-first order (cold session) + archived detail

1. **This file** — current state + queue.
2. Archived detail (the *why*): `handoff-2026-07-18-all-tickets-landed-ch7-next.md`
   §§1–14, then the older 2026-07-18 and 2026-07-17 handoffs.
3. `fiction_loop/CONTRIBUTING.md` — the laws (now 16, +LAW 17 pending T-018);
   binding before any change under `fiction_loop/`.
4. `fiction_loop/core/agent_conduct.md` — binding during any chapter run.
5. `tickets/` — active work orders (T-016, T-018 open; rest landed).

Diagnostics (zero tokens): `PYTHONPATH=src .venv/bin/python
fiction_loop/tools/analyst.py` and `.../progress.py`.

## 8. Since compaction (2026-07-19, later) — governance changes + T-018 status

Recorded so a cold session's front door stays current (handoff discipline):
- **AGENTS.md §1 standing exemption** (`af970c4`): appending to a ticket's OWN
  implementer-log section is always allowed and is NOT counted against its
  write-set or any "only the write-set changed" acceptance. No ticket lists
  itself. (Fixed a template-inherited contradiction that made a strict
  implementer STOP.)
- **Innovations extracted** (`ef7ebf5`): two new patterns —
  `situation-personification` (CAST & FIT) and `root-cause-laddering`; two
  enhancements (ticket-dispatch Upstream/Downstream; handoff compaction); one
  incubating (meta-layer regression net). `innovations/` is now 13 patterns.
- **T-018 (LAW 17) in redispatch, UNBLOCKED, pending implementation.** Two
  valid implementer STOPs, both senior-resolved (`af970c4`, `c49bbc5`):
  (1) the implementer-log exemption above; (2) write-set expanded to include
  `fiction_loop/specs/intake_factory.spec.md` for the "16 laws"→"17" count
  bump — the original Downstream wrongly said "none" (the law COUNT is a
  shared value). **At T-018 acceptance the SENIOR bumps `HANDOFF.md:29`
  "16 laws"→"17"** (out of implementer scope, T-013 precedent).
- Queue unchanged: **T-018 → T-016 → ch8 restart** (paid, owner-started).

## 9. T-018 LANDED + ACCEPTED (2026-07-19)

LAW 17 is live (`c55110a`, senior-verified: purely additive, spec bumped to
"17 laws", baseline green). Senior-owned `HANDOFF.md` count bump 16→17 done.
**Queue now: T-016 (tool regression suite) → then ch8 restart** (paid,
owner-started). T-016 is unblocked (its dep T-017 landed) and is the last
tool ticket before the product resumes.

## 10. T-016 LANDED + ch8 arc-2 quota bug FIXED (2026-07-19, later)

- **T-016 landed** (`12ed7b9`) — tool regression suite live. §5/§9 queue text
  above is now STALE on this point: no offline tool tickets remain.
- **ch8 run resumed** (paid, owner-started) and hit a **structural gate FAIL at
  step 11.5**: "2 of 3 wrong-approach scenes for arc 2". Root cause was NOT the
  chapter — `concept_curriculum.md` §9 held **two contradictory count statements**
  (Section 4 designs arc 2 = 2; the reader-progression table said "arc 1-2 three
  minimum"), and both copies (`QUOTA_BY_ARC`, assembler BEAT QUOTA) followed the 3.
  Latent since the curriculum's first commit; dormant through arc 1 (reads 3 both
  ways); fired on the first arc-2 gate chapter (ch8).
- **Owner DECISION 10 → Option A** (Section 4 is sole count owner). Fix landed
  `6d15c30` (senior, owner-delegated small task, pathspec-limited governance
  commit — NOT in the chapter transaction, LAW 8): gate arc 2 `3→2`; assembler
  BEAT QUOTA split "Arc 1: THREE / Arc 2: TWO"; reader-progression table now defers
  on count; field_registry case law; human_decision.md DECISION 10; a
  `QUOTA_BY_ARC` freeze assertion in `tools/regression/run.py` (LAW 15/16).
  Verified: regression **12/12**, gate **PASS (arc 2, quota 2)** on the existing
  draft (receipt written + `--verify` green), no rewrite, no paid call.
- **ch8 is UNBLOCKED at step 11.5.** The Orchestrator can proceed straight into
  its normal step-10 living-doc refresh + step-12 Updater (ordinary chapter cost,
  not a redo). The run's working state (chapter_008.md, prompts/*, spend,
  `.gate_pass.json`) remains uncommitted for the Orchestrator's own step-12
  chapter transaction.

## 11. ch8 COMMITTED + factory spec-sync + story-treatment (2026-07-19, LATEST — read this for current state)

**Supersedes §1's "7 chapters / ch8 parked" — that is now stale.**

- **Chapter 008 COMMITTED + senior-accepted** (`8935458`): new_focal_character,
  op_check_result, the two DECISION-10 arc-2 wrong approaches (confident specialist
  + hypothesis tester). **`chapter_count`=8, `arc_current`=2**, next pointer =
  **009** (return_to_character, char_004 Wanjiku Mwangi, op_separate_condition,
  touch 2). Clean one-chapter transaction; governance fixes stayed out (LAW 8);
  analyst green, tree clean.
- **Factory spec-sync pass** (`3ff7c43`, per SG-14): the factory specs had drifted
  on hold through T-004..T-018 + DECISION 10; reconciled — `intake_factory.spec.md`
  §3 validation status (arc-1→2 boundary now CROSSED at ch8, not projected),
  Stage-4 **generation rule 5** (one quantity, one owning table), §0 `QUOTA_BY_ARC`
  leak marked **PROVEN LIVE**, build-list rows marked (T-016 partial);
  `deterministic_pipeline`/`assembler_template` drift notes extended;
  `addional_good_to_know.md` §6 refreshed. **No design change — LAW 14 validated.**
- **Story treatment run on the factory spec** (spec-readiness instrument) — TWO
  artifacts, **UNCOMMITTED pending owner reaction** (propose-and-correct):
  - `progress/factory-spec-personification-2026-07-19.md` — **INDIVIDUAL** angle
    ("the spec speaks a third time"); findings CH8-1..8, theme "design closed,
    build didn't" (its own unbuilt diagnoses) + a foreseen-issues register.
  - `progress/factory-cast-and-fit-2026-07-19.md` — **INTERACTION** angle (CAST &
    FIT lens): factory as a company. Key findings — the 3 chassis/pack leaks are
    ONE bad hire ×3 with the human as sync-pass babysitter (Q3); the human is the
    overloaded worker covering 7 empty chairs (Q4); the Gate got blamed while the
    Curriculum was guilty (Q5).
- **Factory action queue (PROPOSED from the findings, NOT dispatched):** a Tier-1
  thrust to cut per-chapter human burden — **T-019** retire the `QUOTA_BY_ARC`
  leak (introduce a pack-owned `arc_quota` data source the Gate reads — also a
  Stage-4 manifest down payment); **T-020/021** anchor + mirror leaks; **T-022**
  pre-writer prompt gate (the spec's designated FIRST build); **T-023** regression
  suite fires the gate's own checks (incl. a rule-5 curriculum-consistency check).
  Still-OPEN validation gaps (chapter-independent except the first): **anchor_interlude
  never fired**; **LAW 15 machinery sweep** undone; `calibration/` organ unbuilt.
- **QUEUE NOW:** owner deciding between (a) the factory Tier-1 action tickets
  (chapter-independent, zero paid — leads with T-019 or T-022) and (b) **ch9**
  (return_to_character, char_004 — paid, owner-started; pointer already staged).
