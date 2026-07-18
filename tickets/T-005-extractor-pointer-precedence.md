# TICKET T-005: Extractor pointer logic — arc-transition precedence + required lead_failure_mode

```
Mode: alone
Depends-on: T-004 MERGED FIRST (same write-set file — extractor.md; serialize)
Timing: BETWEEN runs only (agents/ edits never mid-chapter). Chapter 007 must
        not have started.
Worktree: main working tree, run everything from the repo root
Write-set: fiction_loop/agents/extractor.md,
           fiction_loop/tools/INTEGRATION_SPECS.md (ONLY if the pointer fields
           or lead_failure_mode are documented there; otherwise untouched)
Hot-files: none
State-access: none — do NOT touch fiction_loop/state/, fiction_loop/prompts/,
              fiction_loop/core/, or any .pipeline_spend.json. The known
              missing 006 lead-history entry (§1) is documented, deliberately
              NOT backfilled here (LAW 8 — hand surgery on state is owner-only).
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (verified 2026-07-18, senior review of chapter 006)

**A. Two spec-compliant readings of the same state produced different
pointers.** With every eligible operation at deficit 0:

- the ch5 extraction run took STEP A's FALLBACK and scheduled
  `op_what_is_missing` touch 2 for ch6 — an arc-2 `touch_schedule` entry
  taught during arc 1 (early; harmless; committed state, not to be
  retro-corrected);
- the ch6 extraction run (`logs/chapter_006/11_extractor.log`) skipped the
  FALLBACK and applied STEP D → ch7 `arc_transition`.

Root cause: STEP A's FALLBACK ("pick the eligible arc_current operation with
the lowest current_touch") and STEP D ("every eligible operation has deficit
0 → arc_transition") fire on the SAME condition, and no precedence is stated.
The FALLBACK set is non-empty whenever any eligible op exists, so a literal
reader never reaches STEP D. A deterministic decision with two valid outcomes
violates LAW 2/LAW 3.

**B. `lead_failure_mode` is not contractually required.** The Updater appends
to `failure_mode_lead_history` only when
`update_brief.process_updates.lead_failure_mode` exists and != "none"
(updater.md STEP 7), but extractor.md never obliges setting it. Ch6's brief
left it unset: `master_state.failure_mode_lead_history` has NO 006 entry
(the actual lead was "the executor"). The LAW 11 rotation record silently
skipped a chapter. (Impact currently nil — arc 2 rotates a fresh failure-mode
pool — but the contract hole will bite again.)

## 2. Fix (extractor.md DECISION LOGIC section; gate and updater untouched)

1. **Precedence:** add STEP A.0 before candidate selection: "IF every
   ELIGIBLE operation has deficit = 0 → go directly to STEP D (arc
   transition). Gate-blocked operations do not hold the arc open (their
   deficit carries, per STEP D's existing note)." DELETE the FALLBACK
   paragraph — dead code under this precedence. Add a one-line historical
   note: "Precedence fixed 2026-07 (T-005) after the ch5/ch6 divergence."
2. **STEP D selection, explicit:** secondary_touches for an arc_transition
   pointer = cleared ops with deficit > 0, by largest deficit, max 2; if none
   exist, an EMPTY list is valid — ambient reinforcement is carried by the
   Assembler's cumulative "use naturally" list (owner D1 hybrid + D9 lever 4),
   not by the pointer. (This ratifies the ch6 run's behavior.)
3. **lead_failure_mode contract (LAW 4, registered in place):** for gate
   chapters, `process_updates.lead_failure_mode` = the FIRST wrong approach
   dramatized in the prose — REQUIRED, never omitted; `"none"` only for
   anchor_interlude / arc_transition. State the producer/consumer line where
   the field is defined: producer = Extractor; consumers = Updater STEP 7
   (appends to `failure_mode_lead_history`) and the Extractor's own
   `failure_mode_to_show` selection (least-recently-led rotation).
4. `INTEGRATION_SPECS.md`: mirror ONLY if these fields are documented there
   (LAW 2 — stated once, accurately).

## 3. Acceptance (ALL must pass)

1. `grep -n "FALLBACK" fiction_loop/agents/extractor.md` → zero hits inside
   DECISION LOGIC (the historical note may mention the word once).
2. `grep -n "STEP A.0" fiction_loop/agents/extractor.md` → present, before
   candidate selection.
3. `grep -n "lead_failure_mode" fiction_loop/agents/extractor.md` → REQUIRED
   contract present, with the producer/consumer line.
4. Determinism dry-run (read-only): walk the new logic by hand against the
   committed state files → the result for ch7 must equal the committed
   pointer (arc_transition, operation_due null, secondary_touches []).
   Record the walk in §6.
5. `git status --porcelain` → changes ONLY within the write-set.

## 4. Commit

`fix(specs): extractor pointer logic — arc-transition precedence, required lead_failure_mode`

Trailers:
```
Ticket: T-005
Implemented-by: <Codex|Qwen — whoever implements>
```

Pathspec-limit to the write-set (never `git commit -a`).

## 5. Constraints

- Raspberry Pi; zero paid calls; specs and docs only — no Python edits.
- Never touch state/, prompts/, core/, logs/, living_document.md, spend
  files, books/, .env.
- On ANY failure: stop at that step, record it in §6 exactly as observed,
  leave the tree coherent.

## 6. Implementer log (append below; never delete the ticket body)

- 2026-07-18 — Codex: prerequisite/timing checks passed (T-004 accepted at
  `58e4dbd`; analyst reported chapter 006 COMPLETE and next pointer 007, so no
  chapter 007 run was in flight). Updated `extractor.md` only; no matching
  pointer or `lead_failure_mode` fields were documented in
  `tools/INTEGRATION_SPECS.md`, so that file remained untouched.
- Determinism dry-run against committed state: `arc_current = 1`. The eligible
  operations are `op_identify_unknown` (current touch 2),
  `op_what_is_missing` (current touch 2), `op_separate_condition` (current
  touch 1), `op_check_result` (current touch 0; its schedule starts in arc 2),
  and `op_look_at_unknown` (current touch 1). Each has deficit 0 at arc 1.
  STEP A.0 therefore goes directly to STEP D: `type = arc_transition`,
  `operation_due = null`, and `touch_due = null`. No cleared operation has
  deficit > 0 at arc 1, so `secondary_touches = []`. This equals the committed
  chapter-007 pointer.
- Commit attempt failed exactly as observed:
  `fatal: Unable to create '/home/mr/Desktop/python/github_clones_working_on/book_podcast_fiction_generator/.git/index.lock': Read-only file system`.
  This was the harness filesystem boundary, not a spec/test failure; the tree
  remained coherent and the same path-limited commit was retried with repository
  write approval.
