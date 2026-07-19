# HANDOFF — 2026-07-18 (session end) — T-002/004/005/003 ALL LANDED; next: ch7 kickoff

Written by the senior instance at session end; supersedes
`handoff-2026-07-18-ch6-landed-open-queue.md` (whose §§5–8 addenda remain the
detailed record of today's review/ticket cycle — read them for the *why*
behind any claim here). Every claim below verified against git/files at
commit `03a5d32`, working tree clean.

## 0. Roles (unchanged; precedent extended)

Owner assigns; senior writes tickets, re-runs acceptance independently,
updates the handoff, never implements — EXCEPT owner-delegated small tasks
(precedent today: the T-003 `.env` blind key rename, delegated explicitly).
Codex/Qwen implement. New precedent (T-003 §8): when the implementer's
harness blocks a step (read-only `~/.cache/uv`, git index writes), the
senior runs that step externally, commits on the implementer's behalf with
the `Implemented-by:` trailer, and logs it in the ticket — the
implementation credit stays with the implementer.

## 1. State

- **Chapter 006** committed `a77eec8`; prose review PASSED and owner
  ACCEPTED 2026-07-18 (record: prior handoff §5). 6 chapters exist;
  `arc_current` = 1.
- **Next pointer: 007 — arc_transition.** No gate, no anchor, no operation
  due; `secondary_touches: []` is valid (ambient reinforcement rides the
  Assembler's "use naturally" list). Pointer clean — RUN.md prompt as
  written, no resume note.
- **All four tickets merged AND senior-accepted:** T-002 (`aebc2ca`, URL
  normalization + 404 signature), T-004 (`58e4dbd`, unnamed newcomers reach
  the F15 gate), T-005 (`1063ff0`, extractor STEP A.0 arc-transition
  precedence + required lead_failure_mode), T-003 (`9abbd11`,
  `BOOKGEN_LLM_*` env namespace, clean break).
- **Env contract is now `BOOKGEN_LLM_*` everywhere, including `.env`**
  (3 keys renamed blind by senior per delegation). Analyst ran green
  end-to-end on the new names 2026-07-18 night (key present, state sync ok,
  tree clean). The Qwen-shell 404 collision class is closed at the root.
- `tickets/` files carry complete implementer + acceptance logs for each.

## 2. Binding facts (cold session must know)

1. **pytest is NOT a project dependency.** Sanctioned command:
   `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q`
   (serial — Raspberry Pi). Never add pytest to pyproject.
2. **Implementer-harness blocks are a known class:** safety-classifier
   false-positives (analyst.py), service outages, read-only uv cache, git
   index writes. Remedy: §0 precedent. Verify with receipts, not STATUS
   claims.
3. **F15 false-fail is RESOLVED** (T-004): the structural gate now counts
   unnamed newcomers via `other_entrants` `name: null` entries. The old
   grep-the-prose workaround is obsolete. Updater skips `name: null` for
   cards (permanent record stays named-only, D6).
4. **Extractor pointer logic is single-outcome** (T-005): STEP A.0 sends
   all-deficits-zero straight to arc transition; the FALLBACK is deleted;
   `lead_failure_mode` is REQUIRED for gate chapters ("none" only for
   structural types).
5. **Curriculum §7 map columns beyond an op's card `touch_target` are the
   AMBIENT layer, not scheduled chapters** (owner D9 lever 2; D1 hybrid).
   The D9-amendment note now sits above the map in
   `core/concept_curriculum.md`. Cards' `touch_schedule` is the machine
   truth. Do not re-open; ch6's "owned" compression was verified correct.
6. **Thinking tax (deepseek-v4-pro): ~2.5× billed vs visible tokens is
   EXPECTED**; analyst WARNs at that ratio by design. Keep the model — full
   ch6 cycle cost $0.028, cheapest to date. Keep `max_tokens` ≥ ~2.5×
   expected prose or reasoning eats the budget (empty-output smoke receipt
   2026-07-17).
7. **Ticket-authoring lesson (3 corrections on T-003 alone):** dry-run every
   acceptance command against HEAD when writing a ticket — check the grep's
   scope covers the write-set AND that its pattern still passes after a
   correct implementation (substring collisions with new names).
8. **Known pre-existing test failure, NOT a regression:**
   `src/engines/tests/test_factory.py::test_default_splitter_engine_passes_openrouter_timeout_seconds`
   (TypeError: missing `source`) — fails identically at pre-T-003 HEAD;
   engines/slicer are the out-of-scope legacy subsystem. Future ticket only
   if revived. Expect `1 failed, 331 passed` until then.

## 3. Open queue (in order)

1. **OWNER, before the next run:** confirm the Qwen companion session's live
   environment exports no `OPENROUTER_*` (repo and shell rc files verified
   clean; that session is the one place the senior cannot see). This is the
   last residual of the 404 saga.
2. **Chapter 007 kickoff** (arc_transition) — PAID RUN, owner starts it.
   RUN.md prompt as written. First run under the new env names and the
   T-004/T-005 contracts: watch step 0 (analyst must pass key-present on
   `BOOKGEN_LLM_API_KEY`) and expect the arc summary step (updater STEP 9)
   to fire for the first time.
3. Optional, owner-only (LAW 8 hand surgery, own commit): backfill
   `{"chapter": "006", "lead": "the executor"}` into
   `master_state.failure_mode_lead_history`. Documented, harmless if left —
   arc 2 rotates a fresh failure-mode pool.
4. Older queue: `handoff-2026-07-17-clone-audit.md` §5, unchanged.

## 4. How to continue (cold-start)

Read-first: this file → `handoff-2026-07-18-ch6-landed-open-queue.md`
(§§5–8) → `fiction_loop/CONTRIBUTING.md` → `tickets/` (all four have full
logs) → `fiction_loop/core/agent_conduct.md` before any chapter run.
Diagnostics (zero tokens): `PYTHONPATH=src .venv/bin/python
fiction_loop/tools/analyst.py` and `.../progress.py`. Conduct: never
cat/grep/print `.env` or `env | grep`; env inspection is `echo $VAR` for
non-secret vars only; interpreter is `.venv/bin/python` from repo root, uv
only, never pip; Raspberry Pi — nothing heavy in parallel.

## 5. ADDENDUM (2026-07-18, later) — ch7 ran; senior verification; T-006 dispatched; 008 BLOCKED

Chapter 007 (arc_transition) ran and committed at `0b3b362` (owner-started
paid run). Senior verification of the run's two flags plus full state audit:

- **Green:** analyst all-ok on the new `BOOKGEN_LLM_*` names (2.6× thinking
  tax = expected WARN); arc_1_summary.md written correctly on STEP 9's first
  firing; next pointer 008 `new_focal_character / op_check_result` sane;
  Kuuku Dadzie correctly ledger-only (arc_transition contract — no focal, no
  card); the UNDETERMINED anchor observation's CONTENT matches prose
  chapter_007.md:175–183 exactly (archive-discovery scene).
- **Defect found (blocks 008): `arc_current` stuck at 1 — NO producer
  exists.** Updater never advances it; fetcher would assemble 008 from arc
  1's curriculum section; extractor deficit math would fire a spurious
  second arc_transition for 009. Corollary: the committed 008 pointer is
  NOT derivable from a literal spec walk at arc_current=1 (receipt: T-005
  §6's own dry-run) — same defect class as T-005 §1A, one layer up.
- **Owner decision (this session): no hand surgery — the system manages
  itself.** Tool-mediated deterministic repair is the sanctioned LAW 8 path.
- **T-006 dispatched** (`tickets/T-006-arc-current-self-managing.md`):
  updater STEP 9 advances arc_current (summary-first ordering); extractor
  gets `arc_effective` (+1 during arc_transition extraction); analyst gains
  the invariant `arc_current = 1 + count(arc summaries)` as a CRITICAL drift
  check and an opt-in `--repair` reconcile (the ONLY sanctioned writer for
  the current 1→2 fix — two pathspec-limited commits, receipts in ticket
  §6); field_registry row; chapter_type_contract row; LAW 4 grep audit.
  Also (§2.7): extractor anchor-observation hygiene — marker prefixes never
  enter state; ch7's entry deliberately left as-is (LAW 12, ages out of the
  fetcher window after ch010).

**Revised queue:** (1) T-006 implement + senior acceptance — BLOCKS the ch8
kickoff; 008 must start only after master_state shows arc_current=2.
(2) Owner: Qwen companion-session env check (unchanged, §3.1 above).
(3) Chapter 008 kickoff (new_focal_character, op_check_result) — paid, owner
starts. (4) §3.3 optional lead-history backfill is WITHDRAWN as hand surgery
(superseded by this session's owner decision); if arc-1 history completeness
ever matters, it becomes a ticket with a deterministic path.

**UPDATE (same day, later): T-006 LANDED AND ACCEPTED** — Codex implemented
(`b128773` specs+tools, `76185c2` state reconcile 1→2 with receipts); senior
re-ran all nine §3 acceptance criteria independently — full record in the
ticket's §6. Analyst now reports `state sync OK (chapter_count=7, arc=2,
next=008 new_focal_character op_check_result)`; repair verified idempotent;
tests at the expected `1 failed, 331 passed`. Queue item (1) is DONE.
**Remaining queue: (a) owner's Qwen companion-session env check (§3.1);
(b) chapter 008 kickoff — paid, owner starts, RUN.md prompt as written.
First chapter of arc 2: watch the fetcher pull the ARC 2 curriculum section
(narrative engine + gate grade band) — first live consumer of the T-006
advance.**

## 6. ADDENDUM (2026-07-18, evening) — ch8 attempt 1 rejected; pollution class ticketed (T-007/T-008)

Chapter 008 run started (Qwen driver; step-0 analyst gate run externally by
senior — Qwen's classifier blocks Python, §0 precedent). **Structural gate
FAILED attempt 1: anchor absent** (HARD RULE 8 carried the full
manifestation; Writer delivered only the warm stool — the torn page with
the anchor's FIRST CONCLUDING LINE, the planned 7th macro-evidence piece,
is missing; owner override correctly rejected). Verdict: **redo generation**,
after `git restore --source=HEAD -- fiction_loop/core/living_document.md` —
because the step-10 paid refresh had already ingested the rejected draft:
the LAW 7 standing violation fired live for the first time, and the
`redo generation` rung's "nothing was mutated" claim proved false.

**Owner assigned both fixes; senior dispatched:**
- **T-007** (`tickets/T-007-truthful-redo-ladder.md`) — truthful ladder:
  redo-generation rung gains the conditional living-doc restore; gate FAIL
  output prints the hint; RUN.md ladder line amended. Small; lands first.
- **T-008** (`tickets/T-008-gate-before-refresh-reorder.md`) — the mapped
  LAW 7 reorder, done WHOLE: new order 8→9→11→11.5→**10**→12 (step numbers
  kept, M-15 precedent). The one real coupling is severed by design
  decision: `reader_can_suspect_update` now derives from chapter prose +
  mystery_anchor.json — the Extractor's living_document.md input is
  deleted. Kills both the wasted call and the pollution class at the root;
  also satisfies the intake-factory auto-redo precondition. Full §3.8
  LAW 4 audit list in the ticket.

**Both tickets are BETWEEN-runs (agents/ edits never mid-chapter): implement
only after ch8 commits or the run is abandoned. Serialize T-007 → T-008.**
Mid-run recovery for ch8 itself is manual per the receipts mechanism (the
restore command above, then redo generation; driver greps the new draft for
stool/torn/wiped + the concluding line before letting step 10 spend).

## 7. ADDENDUM (2026-07-18, night) — ch8 attempt-2 INCIDENT: driver ran the Updater on the gate-FAILED brief; undone; T-009/T-010 dispatched

Sequence (all receipt-verified): living doc restored by senior (owner
authorization); redo generation produced attempt 2 (1,891 words, bridge
exit 0, 19:42; traces present incl. the torn page + concluding line —
wiped panel absent, texture-only). THEN the driver session **skipped steps
10/11/11.5 and spawned the Updater (20:20) against the attempt-1 brief
(mtime 19:11 — extracted from REJECTED prose; the gate's only verdict on
it was FAIL)**. Owner killed the session mid-STEP-4; senior ran the staged
`undo state application` (owner-authorized): `git restore` of
fiction_loop/cards + deletion of the five contaminated new cards
(char_008/008a/008b, G-008, loc_kumasi). Spend file NOT reverted (LAW 9).
Post-undo analyst: state sync OK, chapter_count=7, arc=2, pointer intact.

**Attempt 2 is ALSO not acceptable:** senior prose review found a HARD
RULE 1 violation — the narration line ("The confident specialist… The
hypothesis tester… The executor…") uses all three forbidden planning
labels verbatim. (The torn-page ITALIC entries are artifact quotation —
ch7 precedent, acceptable.) Verdict: chapter 008 needs a THIRD
`redo generation`. Two consecutive hard-rule misses = stop rolling blind;
hence the new tickets.

**Dispatched (owner-assigned):**
- **T-009** (`tickets/T-009-gate-pass-receipt.md`): structural gate writes
  a brief-hash receipt on PASS / deletes it on FAIL; new step 12.0 runs
  `--verify` and the Updater is unreachable without it. Makes today's
  skip-to-updater IMPOSSIBLE, not forbidden (LAW 6/LAW 9).
- **T-010** (`tickets/T-010-forbidden-label-check.md`): deterministic
  forbidden-label check in invoke_writer.py — labels derived at runtime
  from process_state (LAW 14), italic-line artifact exemption calibrated
  so committed ch7 PASSES and today's attempt-2 draft FAILS (both fixtures
  on disk). LabelLeakError → auto one retry, then owner accept-or-redo.

**Ticket order (all BETWEEN runs): T-007 → T-008 → T-009 → T-010** (shared
write-sets: structural_gate.py, orchestrator.md, invoke_writer.py).

**Resuming ch8 (driver checklist, until the tickets land):** (1) redo
generation — third roll; (2) zero-token greps BEFORE anything else:
traces (stool/torn/wiped + "condition itself provides") AND no failure-mode
label in narration (labels in italic artifact lines OK); (3) then 10 → 11
→ 11.5 — the gate MUST re-run and PASS on the NEW brief; (4) only then 12
→ 13.5. Never run the Updater on a brief the gate has not just passed.

## 8. ADDENDUM (2026-07-18, late) — driver deadlock diagnosed; T-011 role fence dispatched

The driver session refused the documented ch8 resume, citing the four
dispatched tickets and proposing to implement them mid-run — a blocking
relationship no document states and the tickets' timing gates forbid.
Senior overrode with the §7 checklist. Root cause of BOTH driver
incidents: **two orientation systems, one front door.** agent_conduct §2
SCOPE WALLS already forbids reading anything outside fiction_loop/
(HANDOFF.md, tickets/, progress/ included), but AGENTS.md/CLAUDE.md order
every cold session to orient from the handoff, and the RUN.md kickoff
prompt never restates the wall (LAW 5: a MUST living only in a referenced
doc is advisory). The driver obeyed both masters and synthesized policy
from maintainer context.

**Owner decision: the agent that runs fiction_loop operates the loop as
Orchestrator, and ONLY that.** Dispatched **T-011**
(`tickets/T-011-orchestrator-role-fence.md`): ROLE FENCE inline in the
kickoff prompt (hard channel); CONTEXT BUDGET names governance docs;
agent_conduct §2 case law; HANDOFF.md gains a "maintainer sessions only"
scope paragraph; AGENTS.md a one-line exception. Write-set crosses the
fiction_loop/ boundary deliberately (the defect lives in the interaction).

**Queue order (all BETWEEN runs): T-007 → T-008 → T-009 → T-010 → T-011.**
Complementary split: T-009 makes the destructive step mechanically
unreachable; T-011 stops the driver improvising everywhere else. Ch8
resume per §7 checklist remains the immediate next action.

## 9. ADDENDUM (2026-07-18, late) — ch8 run ABANDONED (owner, Option 2); ticket queue UNLOCKED; T-012 plan on disk

Third redo roll ran (spend 19:10, $0.006) and ALSO failed pre-flight:
labels clean, stool+wiped present, torn-page anchor ABSENT (attempt 1's
miss again — three rolls, three different misses; the 40%-joint-rate
diagnosis confirmed live). Owner decision: **run abandoned** — the §6
timing trigger — so **T-007→T-008→T-009→T-010→T-011 implement NOW**, then
T-012 (targeted-revision station) and T-013 (rule-intake law), plan at
`tickets/T-012-PLAN-targeted-revision-station.md` (a PLAN, not a
dispatched ticket — expand to house style first, dry-run acceptance
commands). Attempt-3 draft preserved as the T-012 fixture at commit
`cf70a1b` (`fiction_loop/prompts/chapter_draft.md`). Ch8 restarts on the
post-ticket machine and enters at the revision rung (T-012 §2.5
existing-draft intake) — do NOT roll blind again.

## 10. ADDENDUM (2026-07-18, late) — T-008 redispatched (write-set defect, not an impl failure)

Codex began T-008, ran the §3.8 LAW 4 audit, and correctly STOPPED +
reverted: two live old-order contracts sat outside the write-set —
`tools/INTEGRATION_SPECS.md` (§5/§6 state refresh-before-Extractor) and
`core/pipeline_stage_manifest.md` (order table + Extractor input list).
Under LAW 7's all-or-nothing rule a partial reorder leaving those stale is
the forbidden failure, so the STOP was right. Senior redispatched at
`795a159`: both files ADDED to the write-set with exact edits (§3.9/§3.10)
and grep proofs (§6a/§6b); verified no OTHER out-of-write-set file states
the order. Queue order unchanged (T-008 still after T-007, which is merged
`b8f0b7c`). Re-run the FULL §3 from a clean tree — do not resume the
reverted partial.

## 11. ADDENDUM (2026-07-18, late) — T-007..T-011 all LANDED + verified; T-012 PLAN expanded into dispatched T-012/T-013/T-014

**Whole between-runs queue is DONE and senior-verified** (commits: T-007
`b8f0b7c`, T-008 `3ab5f5a` after redispatch `795a159`, T-009 `1e8b082`,
T-010 `1fa915b`, T-011 `23fe193`). Independent re-checks this session:
T-008 order-proof greps pass and both redispatch-added files
(INTEGRATION_SPECS.md, pipeline_stage_manifest.md) now state the new order;
T-009 `--verify` correctly returns "no receipt" / exit 1 with no receipt on
disk; T-010 label check green on all three fixtures (ch7 PASS, attempt-2
FAIL with 4 narration violations, attempt-3 PASS); tests `1 failed, 331
passed` (known engines failure only).

**T-012 was a PLAN, not a ticket — implementer correctly STOPPED.** Senior
expanded it into three DISPATCHED tickets (`1c2c917`):
- **T-012 targeted-revision rung** — `invoke_writer.py` gains
  `--check-prose` (structured deficiency JSON) and `--revise` (one targeted
  paid call, diff-size guard `REVISION_MAX_DIFF_RATIO=0.25`, re-check after).
  Ladder: prose-check FAIL → revise ≤2× → `redo generation`. Acceptance is
  ENTIRELY OFFLINE (`--dry-run` + the three on-disk fixtures); live proof
  that revision converges rides the next owner run (T-008 pattern).
- **T-013 LAW 16** — a new hard rule must ship its deterministic check or a
  written non-checkability note. Stops the rule-ratchet at the source.
- **T-014 (OPTIONAL/deferrable)** prose anchor-presence check — early catch
  of a missing anchor scene before the Extractor spend. The gate ALREADY
  catches anchor-absent authoritatively, so this is efficiency + driver-
  improvisation removal, not correctness. Derives the required phrase from a
  structured Assembler field (design fork (b)); a coarse grep FALSE-PASSES.

**Key correction captured during expansion:** all three ch8 failure modes
are already caught deterministically today (gate/label check), so the
station's real win is REVISE-NOT-REROLL for SURGICAL misses; whole-scene
omissions (anchor absent) stay on `redo generation`. `T-012-PLAN-SUPERSEDED.md`
records this; the dispatched tickets are the authority.

**Revised queue (all BETWEEN runs):** implement **T-012** first
(foundation), **T-013** any time (independent, tiny), **T-014** last and
only if wanted. Then ch8 restarts on the new machine and enters at the
revision rung for any surgical miss (T-012 existing-draft path), never a
blind fourth roll. Ch8 attempt-3 fixture preserved at `cf70a1b`.

## 12. ADDENDUM (2026-07-19) — T-012 redispatched twice-over (both blockers valid); T-014 preemptively fixed

Codex STOPPED on T-012 with two blockers, BOTH valid against the ticket as
written (receipts in T-012 §7):
- §3.5's STOP-condition grep was too broad — it flagged
  `structural_gate.py:105`'s redo-only option list, which is actually
  CORRECT (gate failures are structural/whole-scene → `redo generation`;
  revision applies only to prose-check/step-8 surgical misses). Fixed by
  EXEMPTING that line explicitly and narrowing the STOP-condition; write-set
  UNCHANGED.
- §4.5 required a pytest in a nonexistent invoke_writer test module. Rewrote
  to the repo's `python -c` import pattern (T-010 CLI-test precedent);
  verified the import path and the difflib ratio assertions dry-run green.
Same test-module defect class preemptively fixed in T-014 §4.3 (CLI
`--check-prose` guard, not a "unit"). Commits: `4b1e4b7` (T-012),
`d6f83ce` (T-014).

**T-012 is now clean to implement from `tickets/T-012-targeted-revision-rung.md`.**
Queue unchanged: T-012 (foundation) → T-013 (any time) → T-014 (optional).
Root-cause lesson (recurring, now 3×): acceptance commands AND STOP-condition
greps must be dry-run against HEAD before dispatch — including verifying that
any named test harness exists and that broad audit greps exempt
correct-as-is contracts. Extends handoff §2.7.

## 13. ADDENDUM (2026-07-19) — T-012/T-013/T-014 implemented; senior acceptance; T-014 regression → T-015 dispatched

All three implemented (T-012 `4834101`, T-013 `0b0f4af`, T-014 `ba7204b`);
write-sets matched. Senior re-ran acceptance independently against HEAD:

- **T-013 (LAW 16): ACCEPTED.** LAW 16 present with its case-law clause;
  LAWS 1–15 byte-unchanged; no stale "15 laws" counts under fiction_loop.
  Senior-owned HANDOFF.md count fix 15→16 done (`this session`).
- **T-012 (revision rung): mostly green** — `--check-labels` regression
  (ch7/att2/att3), diff-guard (`diff-guard ok`), arg-guards, `--revise
  --dry-run` (exit 0, revision_prompt.md holds draft+flagged lines, spend
  BYTE-UNCHANGED), test baseline `1 failed, 331 passed` all PASS. **BUT
  §4.1/§4.3 REGRESSED by T-014** (see below).
- **T-014 (anchor check): correct WHEN asked** — with
  `--anchor-requirement`, attempt3→`anchor_absent`, attempt2→labels-only
  (phrase present), `anchor_appears:false`→no-op. **Defect:** T-014 wired
  the anchor check into the SHARED `write_prose_deficiencies`
  UNCONDITIONALLY, and `load_anchor_requirement` RAISES on a missing
  `ANCHOR_REQUIREMENT_JSON` block. So `--check-prose` with NO
  `--anchor-requirement` (T-012's accepted label-only contract) now dies
  with a raw traceback whenever the assembled_prompt lacks the block —
  every historical draft, and it holds the label check hostage to the
  anchor contract. Live happy-path survives only because the Assembler
  always emits the block and the orchestrator relies on that unwritten
  coupling.

**T-015 dispatched** (`tickets/T-015-check-prose-anchor-coupling-regression.md`):
`--check-prose` runs labels ALWAYS, anchor check ONLY when
`--anchor-requirement` is supplied; orchestrator's live step-8 call passes
`--anchor-requirement …/assembled_prompt.md` so enforcement moves to the one
site that has the block; supplied-but-malformed block → clean handled error,
not a traceback. Write-set: invoke_writer.py + orchestrator.md (both already
T-014's). Fully offline acceptance. This is a classic integration
regression: T-014 changed shared code without re-running the prior ticket's
(T-012's) acceptance — the ticket-pipeline analogue of "gates before spend"
applied to redispatch.

**Queue: T-015 (small, between-runs) before ch8 restart.** After it lands,
the revision station is whole and ch8 re-enters at the revision rung for any
surgical miss. Fixtures preserved: attempt-2 `d91e558`, attempt-3 `cf70a1b`.

## 14. ADDENDUM (2026-07-19) — B operating model adopted; T-014 retired; LAW 17; CAST & FIT lens

Owner decisions this session, all executed:
- **Authoring discipline (committed):** the ticket template
  (`innovations/ticket-dispatch/kit/TICKET_TEMPLATE.md`) now has **Upstream**
  (preconditions the author dry-ran) and **Downstream** (consumers to
  re-verify, from field_registry) header fields + acceptance item 4. Kills the
  T-008/T-012/T-014 bounce class at authoring time.
- **T-014 RETIRED (decision "3c").** The prose anchor-check was optional (the
  gate catches anchor-absent authoritatively) and needed T-015 to babysit its
  coupling. CAST & FIT Q3 named it a bad hire → retire, don't babysit.
  **T-017** dispatched (revert T-014's surface; restore label-only
  `--check-prose`). **T-015 WITHDRAWN** (subsumed by T-017).
- **LAW 17 dispatched (T-018):** "know who eats your output" — a shared-surface
  change re-verifies its consumers. LAW-16-compliant by construction: its
  enforcement (the Downstream template field + the T-016 suite) ships with it.
- **T-016 (tool regression suite)** rewritten to depend on T-017 and freeze the
  POST-retirement label-only contract (anchor assertions removed). It is LAW
  17's mechanical enforcement — the factory's first immune cell.
- **CAST & FIT one-pager** committed at
  `innovations/situation-personification/cast-and-fit.md` — a reusable lens
  (five questions) for analysing a system as a household; the anchor-retirement
  is its worked example.

**Spec queue (all BETWEEN runs, offline, no paid calls):**
T-017 (retire anchor-check) → T-016 (regression suite; depends on T-017).
T-018 (LAW 17) independent, any time. All three implementable now.

**Deferred (not now):** full boundary-enforcement architecture (let the suite
reveal the seams first); a mechanical Upstream preflight (the template field +
author dry-run covers it for now — building the mechanism is deferred, priced-
guardrails discipline).

**PRODUCT — chapter 008:** still parked. Owner decision: ch8 restarts only
after ALL non-ch8-dependent specs are implemented (T-016/T-017/T-018). Then
paid, owner-started; re-enters at the revision rung for any surgical miss.
