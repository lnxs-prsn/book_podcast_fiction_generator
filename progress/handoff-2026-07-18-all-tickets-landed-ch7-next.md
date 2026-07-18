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
