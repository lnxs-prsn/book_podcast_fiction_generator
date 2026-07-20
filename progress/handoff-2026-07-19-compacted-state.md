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

## 12. Pre-build multi-perspective pass + `starting_factory` tag + the "one-way door" problem (2026-07-19, LATEST — read this for current state)

**Supersedes §11's "QUEUE NOW".** No commits this session except the tag; nothing
dispatched, no spec edits landed, chapter state untouched (HEAD still `fe2e20d`,
`chapter_count`=8, next=009). Owner directive this session: **take multiple
perspectives BEFORE building** — avoid obvious issues, don't let one lens set the
build agenda.

- **Restore point tagged:** annotated git tag **`starting_factory` → `fe2e20d`**
  (local only, NOT pushed; branch is 2 commits ahead of origin). Marks the working
  1-book flow before any factory-build work. Restore: `git reset --hard starting_factory`.

- **THIRD personification run (UNCOMMITTED):**
  `progress/factory-wip-personification-2026-07-19.md` — the **work-in-progress /
  part's-eye** angle (a chapter's `update_brief.json` narrating its trip down the
  line), companion to the individual (spec) and interaction (company) treatments.
  Findings WIP-1..8, each mechanics-checked. **Shape-fit verdict on the company lens
  (owner asked):** the firm/org lens fits *partially* — great on overload/blame/
  redundancy, but native to *roles* not *flow*; its "hire the empty chairs" is an org
  sentence that the line-native reading translates to "close the belt gap / the part
  passes one checkpoint that only weighs it." The WIP lens saw three flow facts the
  org lens structurally couldn't (WIP-1 single bridge, WIP-5 doubled pointer, WIP-6
  wiped-every-chapter) and credited one built-right positive (WIP-4 receipt seal).

- **THE crystallized problem (plain form) — the "one-way door":** the Extractor
  (step 11) is the ONLY stage that reads chapter prose after the Writer; it writes
  the summary `update_brief.json`; the Updater then builds ~10 card/state files from
  that summary **and is forbidden to re-read prose**. The one downstream guard (the
  Structural Gate, 11.5) only **counts** (len/booleans) — it never verifies the
  summary against the story. So a wrong summary field (e.g. a mis-transcribed name,
  "Nantale"→"Nantare") passes the count-gate and becomes canon in ~10 files, uncaught,
  because nothing looks at the story again. **Highest-damage class = wrong/lost names
  on RETURNS** — and **ch9 is a return** (Wanjiku, char_004), where a slipped id/name
  duplicates or orphans an existing character. This is the WIP-1/WIP-2 finding in
  concrete terms; it is the single real problem the pre-build pass surfaced.

- **Emerging fix direction (owner instinct, endorsed; NOT yet ticketed):** "verify
  from the fresh source — the story." Two depths, distinct costs:
  1. **FREE / deterministic** — a prose text-search that every name/place the summary
     asserts actually *occurs in the chapter file*. Reads the fresh source (the story),
     zero tokens, catches transcription/hallucination slips (the Nantale case). The
     highest-value, cheapest guard; a deterministic *slice* of the unbuilt Stage-5
     Fidelity Inspector. **Distinct from** an earlier-floated self-consistency check
     that never reopens the story (weaker — cannot catch a wrong name).
  2. **PAID** — a second model re-reads the chapter and verifies the summary's *meaning*
     (operation taught, correct_approach true to scene). The real Stage-5 cross-read;
     costs a call/chapter; unbuilt.

- **Dropped after scrutiny (do NOT re-raise as problems):** WIP-5 **doubled
  `next_chapter_pointer`** (brief + master_state) — by-design (single author →
  canonical store, no drift path), NOT a `QUOTA_BY_ARC`-class leak; worth at most a
  one-line `field_registry` "not-a-leak" note before any leak-sweep so it isn't
  false-fixed. WIP-4 receipt seal — a positive, not a problem.

- **Open owner decisions (propose-and-correct; nothing applied):** (1) react to the
  three treatments — which findings fold into the spec; discipline clarified this
  session: the **fact-layer folds immediately** (spec-sync already did, e.g.
  `QUOTA_BY_ARC` PROVEN LIVE), the **judgment/priority/design layer waits** for owner;
  (2) a possible one-line refinement of the spec-readiness rule (§3 lines 307-312) to
  say exactly that — offered, not written; (3) the risk-boundary framing for any
  build: **factory-spec edits are design docs (zero chassis-risk); anything under
  `fiction_loop/` touches the `starting_factory`-tagged chassis** (CONTRIBUTING-bound,
  regression-guarded) — so low-regret = spec/doc notes now, chassis changes via ticket.

- **QUEUE NOW (refined):** still (a) factory Tier-1 tickets vs (b) ch9 (paid), **but**
  the pre-build pass promoted a sharpened lead candidate: a **verify-from-source guard**
  (free name-presence check first) as the highest-value, lowest-cost protection — most
  relevant precisely because the next chapter (ch9) is a return. Owner to pick the fix
  depth; no ticket drafted yet.

## 13. Two more lenses (ADVERSARIAL + READER) + first tickets DRAFTED (2026-07-20, LATEST — read this for current state)

**Supersedes §12's "QUEUE NOW".** HEAD is now `9d0966c` "factory specing" —
**docs-only** (committed the open-problems synthesis + WIP personification + prior
handoff edits; NO chassis code touched, so §12's dry-run facts still hold). Chapter
state untouched (`chapter_count`=8, next=009). Nothing dispatched. Two new artifacts +
three ticket files added this session, all UNCOMMITTED.

- **Two NEW lenses run** (a *different kind* of perspective than the three
  personifications, which were all one introspective method):
  `progress/factory-adversarial-and-reader-pass-2026-07-20.md` — **ADVERSARIAL**
  (ADV-1..5: how to get corruption past the gate) + **READER/product-outcome**
  (RDR-1..4: rank defects by damage to the person reading the finished novel).
  Grounded in the real `structural_gate.py`/`extractor.md`/`updater.md` + live
  `master_state.json`. Found **8 genuinely new problems** (none in the WIP/CH8/Q
  registers). Key live facts confirmed: `char_008` really is "Nantale Namakula"
  (the one-way-door example is real); the leftover ch8 brief still returns
  `--verify` PASS (ADV-4 stale-receipt surface is real and reachable).

- **A ch9-BLOCKING owner decision surfaced — ADV-3:** the gate requires ≥2
  wrong-approach scenes for `return_to_character` too, but ch9's pointer has the
  focal showing `failure_mode_to_show: "none"` (Wanjiku returns to correctly apply +
  name op_separate_condition). So both required failure scenes must be carried by
  newcomers on the taught op — a clean name-payoff return can be designed straight
  into a gate FAIL after the paid Writer run. **Needs an owner ruling BEFORE ch9:**
  does the arc-2 quota apply to a touch-2+ return, and if so how is it satisfied?
  No ticket resolves this (bucket-C open decision); T-024 explicitly does NOT touch it.

- **Understanding-completeness estimate (owner asked):** excluding implementation
  and spec-writing, **~75–80% of the surfaced problems have a clear solution
  direction** (waiting mainly on spec/ticket writing), ~15% need a small design pass
  first, ~8–10% are genuinely open. The open minority is small in count but heavy:
  ADV-3 (blocks ch9) and RDR-3 (mystery-fairness — no stage checks planted evidence
  against the hidden solution, and the design walls the solution off from every agent,
  so it is structurally unguardable today). Full breakdown in
  `progress/factory-open-problems-synthesis-2026-07-20.md` (also the consolidated
  root: *a truth kept in two copies, synced by human memory* — leaks + spec-drift +
  4-layer re-verify + doubled pointer).

- **THREE tickets DRAFTED (not dispatched; senior dry-ran each STOP-condition
  against HEAD `fe2e20d`, 2026-07-20):**
  - **T-024** `gate-cross-field-integrity` — binds brief focal-id / chapter /
    failure-list to the schedule (ADV-1/2/4). Highest ch9 value, free, no state
    schema change. Reads population_index + pointer + process_state pools (membership
    derived from pack, NOT hardcoded — avoids a new leak).
  - **T-025** `prose-name-presence-guard` — the FREE verify-from-source slice: every
    name the summary asserts must occur in the chapter prose (the Nantale/Nantare
    catch). New standalone tool, READ-ONLY. Leaves a senior TODO: wire the Orchestrator
    step 11.4 (RUN.md is outside the chassis write-set).
  - **T-019** `retire-quota-by-arc-leak` — the ripest LAW-14 leak: the gate reads the
    per-arc quota from a new pack manifest `state/arc_quota.json` (init_state emits it;
    Stage-4 down payment) instead of the hardcoded dict. Scoped to the GATE copy; the
    two assembler copies are flagged as remaining (follow-on).

- **Remaining CLEAR-bucket items — direction known, each needs its OWN
  source-verification pass before a dispatch-ready ticket (senior discipline), so NOT
  written this session:** T-020 anchor-description leak (`assembler.md:229` hardcoded —
  needs a pack source decided); T-021 mirror-content leak (**may be partly stale** —
  `assembler.md:44` already fetches §5 mirror rows; verify before ticketing); T-022
  pre-writer prompt gate (the spec's designated first build — more spec than ticket);
  T-023 curriculum-consistency regression fixture (rule-5 one-quantity-one-table);
  **P2** calibration organ (`calibration/` create + archive briefs + backfill ch1–8);
  **P6** spec-staleness check; **P9** doubled-pointer "not-a-leak" `field_registry` note
  (do BEFORE any leak sweep so it isn't false-fixed).

- **Suggested dispatch order** (all zero-paid, chapter-independent, sharpened by ch9
  being a return): resolve **ADV-3** (owner, free) → **T-024** → **T-025** → **T-019**,
  then the remaining clear items. ch9 (paid) should not run until ADV-3 is ruled and
  ideally T-024/T-025 land (they guard the exact return-chapter failure classes).
