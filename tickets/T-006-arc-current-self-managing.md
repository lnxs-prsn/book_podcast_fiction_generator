# TICKET T-006: arc_current is self-managing — updater advances it, extractor uses the effective arc, analyst detects and repairs drift

```
Mode: alone
Depends-on: none (T-002/003/004/005 all merged and accepted)
Timing: BETWEEN runs only. BLOCKS chapter 008 kickoff — 008 must not start
        until this ticket lands AND the reconcile run (§2.4) has committed
        master_state.arc_current = 2.
Worktree: main working tree, run everything from the repo root
Write-set: fiction_loop/agents/updater.md,
           fiction_loop/agents/extractor.md,
           fiction_loop/tools/analyst.py,
           fiction_loop/core/field_registry.md,
           fiction_loop/core/chapter_type_contract.md,
           fiction_loop/state/master_state.json — ONLY via the §2.4
           reconcile path, in its OWN commit (never edited by hand or
           by any other mechanism in this ticket)
Hot-files: extractor.md (T-004 and T-005 both landed there recently)
State-access: EXCEPTION, owner-sanctioned 2026-07-18 ("no hand editing —
              the system must manage itself"): master_state.json may be
              written ONLY by the new deterministic repair path in §2.4,
              with before/after receipts logged in §6. No other state,
              prompts/, chapters/, living_document.md, or spend file is
              touched. LAW 8 compliance: deterministic tool + receipts +
              its own pathspec-limited commit.
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (verified 2026-07-18, senior review of chapter 007)

**A. Nothing in the pipeline ever advances `master_state.arc_current`.**
After chapter 007 (arc_transition, commit `0b3b362`) the field still reads
`1`. Updater STEP 7 and STEP 9 never touch it; no other agent or tool writes
it; it was seeded by `init_state.py` and has no producer since (LAW 4: a
field with no producer is a silent default — a bug). Consequences if 008 runs
at `arc_current = 1`:

- fetcher.md:32 fetches the curriculum section "matching
  master_state.arc_current" → chapter 008 would be assembled from ARC 1's
  narrative engine and gate-grade band instead of arc 2's;
- extractor deficit math (`deficit(X)` counts schedule entries with
  `arc <= arc_current`) sees every arc-2 touch as out of window → after 008,
  all deficits read 0 → STEP A.0 wrongly fires ANOTHER arc_transition
  for 009.

**B. The extractor's post-transition pointer is not derivable from the spec.**
Receipt: T-005 §6's own determinism walk shows that at `arc_current = 1`,
`op_check_result` has deficit 0 ("its schedule starts in arc 2"). Yet the
committed 008 pointer is `new_focal_character / op_check_result touch 1` —
correct for arc 2, but a literal walk of DECISION LOGIC at `arc_current = 1`
yields arc_transition again. The ch7 extraction run got the right answer by
judgment, not by contract — the same defect class T-005 §1A fixed (two
readings, one committed outcome; violates LAW 2/LAW 3).

**C. (minor, same producing document) A marker prefix leaked into state.**
`mystery_anchor.json` ch-007 `observation` begins with the literal string
`"UNDETERMINED — no verbatim notebook entry in chapter prose; "` followed by
an accurate observable description. The fetcher feeds the last 3
observable_log entries into the next chapters' assembled prompts, so the
meta-marker rides into ch 008–010 writer inputs.

## 2. Fix

**2.1 updater.md — STEP 9 advances the arc (prevention, LAW 6).**
In STEP 9 (arc_transition only), AFTER writing `/arcs/arc_[N]_summary.md`
(N = the `arc_current` value read at the start of the update sequence):

```
Re-open /state/master_state.json
Set arc_current = N + 1
Write master_state.json
```

Ordering is deliberate and must be stated in the spec text: summary first,
increment second, so the stored value can only ever LAG the derived truth
(§2.3 invariant) across a crash — never lead it. Do NOT fold this into
STEP 7: STEP 7 runs before the summary exists, and N would become ambiguous.
Add one historical line: "Added 2026-07 (T-006) — before this, arc_current
had no producer and stuck at its init value."

Mirror in `core/chapter_type_contract.md` table (matching the existing
"arc summary (Updater STEP 9)" row):

```
| arc_current advance (Updater STEP 9) | n/a | n/a | n/a | required |
```

**2.2 extractor.md — effective-arc rule (closes §1B).**
In DECISION LOGIC **Definitions**, add:

```
arc_effective = arc_current + 1  IF the chapter being extracted has
                chapter_type = arc_transition
                ELSE arc_current
```

and change `deficit(X)` (and any other Definitions/STEP text that reads
`arc_current`) to use `arc_effective`. Rationale line to include: the
extractor computes the pointer for the NEXT chapter at step 11, before the
Updater's STEP 9 advance at step 12; during an arc_transition extraction the
next chapter already belongs to the new arc. Historical note: "T-006 —
ratifies the ch7 run's committed 008 pointer, which a literal arc_current=1
walk could not produce."

**2.3 analyst.py — drift detection (detection, LAW 6; new signature, LAW 9).**
In `check_state()`, derive:

```
derived = 1 + count of files in fiction_loop/arcs/ matching
          ^arc_(\d+)_summary\.md$
```

Checks, in order:
1. Contiguity: the matched arc numbers must be exactly 1..K with no gaps or
   duplicates → else CRITICAL "arc summaries non-contiguous" with fix hint
   "inspect fiction_loop/arcs/ — no auto-repair possible", and SKIP the
   drift check.
2. Drift: if `master_state.arc_current != derived`:
   - mid-run (reuse the existing `mid_run` detection): INFO — the Updater
     may legitimately be between the summary write and the master write;
   - otherwise: CRITICAL
     `"arc_current drift (stored X, derived Y)"` with fix hint
     `"run: PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py --repair"`.
3. No drift → fold into the existing "state sync OK" line, e.g.
   `state sync OK (chapter_count=N, arc=X, next=...)`.

**2.4 analyst.py — `--repair` flag (correction, LAW 6; the sanctioned
mutation path).** Scope is EXACTLY arc_current reconciliation, nothing else:

- Refuse (non-zero exit, clear message) if `logs/STATUS.md` shows a run in
  progress (`state: RUNNING` or `state: BLOCKED`) or if the contiguity check
  fails.
- Otherwise: recompute `derived`, print a receipt line
  `REPAIR arc_current: stored X -> derived Y (basis: K arc summary files)`,
  write master_state.json with ONLY that field changed, exit 0. If stored
  already equals derived, print "no drift — nothing written" and exit 0
  (idempotent).
- Default invocation (no flag) stays strictly read-only — analyst remains a
  diagnostics tool; the flag is the explicit opt-in.

After the T-006 spec fix lands, this path should fire exactly once (the
current 1→2 reconcile) and thereafter only for the STEP 9 crash window.

**2.5 field_registry.md — register the field (LAW 2 + LAW 4).** New row for
`master_state.json.arc_current`:

- Owner/source of truth: the arc summary files (`arcs/arc_N_summary.md`,
  written once per arc_transition by Updater STEP 9); `arc_current` is the
  registered cached copy, invariant `arc_current = 1 + count(summaries)`.
- Producers: `tools/init_state.py` (seed 1), Updater STEP 9 (advance),
  `analyst.py --repair` (deterministic reconcile).
- Consumers: fetcher (curriculum arc section), assembler (closing/opening
  arc block), extractor (`arc_effective` deficit window), orchestrator
  (status read), analyst (invariant check).
- Case law note: stuck at 1 after ch7 because no producer existed (this
  ticket).

**2.6 LAW 4 audit, same sitting.** `grep -rn "arc_current" fiction_loop/agents/
fiction_loop/core/ fiction_loop/tools/ fiction_loop/RUN.md` — update or
explicitly exempt EVERY hit; list the disposition of each hit in §6.
(Known hits at ticket time: extractor.md, orchestrator.md, fetcher.md,
assembler.md, specs/pipeline_fixes.spec.md, prompts/fetched_fields.md —
prompts/ artifacts are exempt by definition; the spec file is a historical
design record, exempt with a note only if its text contradicts nothing.)

**2.7 extractor.md — anchor observation hygiene (closes §1C, prevention
only).** In the anchor_update section: `observation` contains ONLY
reader-observable prose facts, never marker/meta prefixes; the bare sentinel
`UNDETERMINED` is permitted only when the chapter contains NO observable
anchor material at all (and the Updater's existing report flag then applies).
The ch-007 entry is deliberately NOT edited (LAW 12 — fix the producing
document, not the artifact; the entry leaves the fetcher's 3-entry window
after chapter 010 and is otherwise accurate).

## 3. Acceptance (ALL must pass; dry-run status vs HEAD noted per the
ticket-authoring lesson)

1. `grep -n "arc_current" fiction_loop/agents/updater.md` → STEP 9 advance
   present with the summary-first ordering rationale. (HEAD today: 0 hits —
   passes only post-implementation, as intended.)
2. `grep -n "arc_effective" fiction_loop/agents/extractor.md` → defined in
   Definitions AND used by deficit(); no remaining bare `arc_current` read
   inside DECISION LOGIC except the arc_effective definition itself.
   (HEAD today: 0 hits.)
3. BEFORE the reconcile commit:
   `PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py` →
   CRITICAL `arc_current drift (stored 1, derived 2)`. Record the exact
   line in §6.
4. Reconcile: `PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py --repair`
   → receipt `stored 1 -> derived 2`; then
   `.venv/bin/python -c "import json;print(json.load(open('fiction_loop/state/master_state.json'))['arc_current'])"`
   → `2`; `git diff --name-only` for that commit → ONLY
   `fiction_loop/state/master_state.json` (+ this ticket's §6 append).
5. AFTER: analyst default run → all ok; state-sync line shows `arc=2`;
   re-run `--repair` → "no drift — nothing written" (idempotence).
6. Determinism walk (record in §6): at arc_current=2,
   `deficit(op_check_result)` = 1 (schedule `{1: 2, 2: 3}`, current_touch 0,
   prerequisite op_identify_unknown owned) → STEP A.0 does NOT fire →
   candidate selection yields the committed 008 pointer
   (new_focal_character / op_check_result / touch 1). Also walk the ch7 case
   under §2.2: extracting an arc_transition chapter uses arc_effective = 2 →
   same pointer — the spec now produces the committed outcome.
7. `chapter_type_contract.md` row present; `field_registry.md` row present;
   §2.6 grep audit disposition list recorded in §6.
8. Sanctioned test command
   (`PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q`,
   serial) → `1 failed, 331 passed` — the known pre-existing
   `test_factory.py` failure only; any OTHER failure blocks acceptance.
9. `git status --porcelain` clean after both commits; every change inside
   the write-set.

## 4. Commits (two, in this order, both pathspec-limited — never `git commit -a`)

1. `fix(specs+tools): arc_current self-managing — updater STEP 9 advance, extractor arc_effective, analyst drift check + --repair`
2. `fix(state): reconcile arc_current 1->2 via analyst --repair (T-006 §2.4; receipts in ticket §6)`

Trailers on both:
```
Ticket: T-006
Implemented-by: <Codex|Qwen — whoever implements>
```

## 5. Constraints

- Raspberry Pi; serial; zero paid calls.
- Never touch prompts/, chapters/, living_document.md, spend files, books/,
  .env; never cat/grep/print .env or `env | grep`.
- State is written by exactly one mechanism in this ticket: §2.4. If
  `--repair` refuses or errors, STOP, record in §6, leave the tree coherent —
  do not fall back to any other way of changing the file.
- On ANY failure: stop at that step, record it in §6 exactly as observed.

## 6. Implementer log (append below; never delete the ticket body)

### 2026-07-18 — Codex implementation, governance/tool phase

- Oriented from `HANDOFF.md`, current handoff §5, this ticket, and
  `fiction_loop/CONTRIBUTING.md`; working tree was clean and STATUS was
  `chapter: 007 | step: DONE | state: COMPLETE`.
- Implemented §2.1–§2.5 and §2.7 inside the declared write-set.
- Before reconcile, the default analyst run reported exactly:
  `[CRITICAL] arc_current drift (stored 1, derived 2)`.
- LAW 4 `arc_current` audit dispositions:
  - `agents/extractor.md`: updated — the input declaration remains valid;
    DECISION LOGIC now derives and exclusively uses `arc_effective`.
  - `agents/updater.md`: updated — STEP 9 is the advancing producer with
    summary-first crash ordering.
  - `agents/orchestrator.md`: exempt — status/display consumer, registered and
    compatible with the cached field.
  - `agents/fetcher.md`: exempt — curriculum/arc-summary consumer, registered
    and correct once STEP 9/repair maintains the cache.
  - `agents/assembler.md`: exempt — closing/opening arc consumer, registered
    and compatible.
  - `core/field_registry.md`: updated — source, invariant, producers,
    consumers, and T-006 case law registered.
  - `core/chapter_type_contract.md`: updated — required arc-transition advance
    row added.
  - `tools/analyst.py`: updated — invariant detection and explicit repair
    producer.
  - `tools/structural_gate.py`: exempt — read-only current-arc gate consumer;
    semantics remain correct and it does not compute a next-chapter pointer.
  - `specs/pipeline_fixes.spec.md`: historical design record, exempt; its seed
    value remains correct and its older scheduling/fallback prose is superseded
    by the live Extractor contract without contradicting the new invariant.
  - `prompts/fetched_fields.md`: generated pipeline artifact, exempt by ticket
    definition and untouched.
  - `RUN.md`: no hits.
- Determinism walk: stored/current effective arc 2 gives
  `deficit(op_check_result) = 1` from schedule `{1: 2, 2: 3}`, current touch 0,
  with prerequisite `op_identify_unknown` owned. STEP A.0 does not fire;
  candidate selection yields committed pointer 008
  `new_focal_character / op_check_result / touch 1`. While extracting ch7,
  `chapter_type = arc_transition` makes `arc_effective = 1 + 1 = 2`, producing
  the same pointer before Updater STEP 9 advances the stored cache.
- Sanctioned test command first hit the documented harness/cache restriction:
  `Could not create temporary file ... Read-only file system ... /home/mr/.cache/uv/...`.
  Re-run with approved uv-cache access completed with the sole expected failure:
  `src/engines/tests/test_factory.py::test_default_splitter_engine_passes_openrouter_timeout_seconds`;
  result `1 failed, 331 passed in 8.66s`.
- First pathspec-limited commit attempt hit the documented harness restriction
  exactly: `fatal: Unable to create '.../.git/index.lock': Read-only file system`.
  Retried through the approved external git-index path; no alternate design or
  file mutation was used.

### 2026-07-18 — Codex reconcile phase

- Governance/tool commit: `b128773`.
- The sanctioned path printed exactly:
  `REPAIR arc_current: stored 1 -> derived 2 (basis: 1 arc summary files)`.
- Immediate JSON readback printed `2`. The state diff contained exactly one
  line change: `master_state.json.arc_current` from 1 to 2.
- Post-reconcile default analyst run reported
  `state sync OK (chapter_count=7, arc=2, next=008 new_focal_character op_check_result)`
  with no CRITICAL findings (the expected thinking-tax WARN and git-worktree
  INFO remained).
- Idempotence re-run printed:
  `REPAIR arc_current: no drift — nothing written (stored 2, basis: 1 arc summary files)`.
- Before the state receipt commit, `git diff --name-only` showed only
  `fiction_loop/state/master_state.json`; this §6 receipt append is the other
  explicitly permitted path in the commit.
