# TICKET T-010: deterministic forbidden-label check at the writer bridge — HARD RULE 1 becomes code

```
Mode: alone
Depends-on: T-007/T-008/T-009 MERGED FIRST (orchestrator.md is shared;
            serialize last). Independent of T-009 logically, but the
            write-sets overlap in orchestrator.md.
Timing: BETWEEN runs only — chapter 008 committed or formally abandoned
        first.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/invoke_writer.py,
           fiction_loop/agents/orchestrator.md (step-8 error table line),
           fiction_loop/core/field_registry.md
Hot-files: orchestrator.md
State-access: READ-ONLY read of fiction_loop/state/process_state.json by
              the tool at runtime (label source). No writes to state/.
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (fired live 2026-07-18, chapter 008 attempt 2)

The attempt-2 draft violated HARD RULE 1: its narration used all three
internal planning labels verbatim ("The confident specialist had stayed
inside her pharmacological groups. The hypothesis tester… The executor…" —
chapter_draft.md line 49 at incident time). Nothing in the pipeline could
catch it: the structural gate reads the brief, never prose; the only
enforcement was the Writer's own self-check — the exact agent that
violated it. A literal string search is the most deterministic check the
system could possibly have (LAW 3: if it CAN be deterministic it MUST be
code), and it was missing. Attempt 1 had already burned one roll on a
different hard rule; a free check would have rejected attempt 2 at 19:42
before any human review.

## 2. Design (calibrated to BOTH observed cases — tripwire, not aspiration)

**Label source (LAW 14 — chassis/pack separation, LAW 2 — single source):**
the tool derives the forbidden set at runtime from
`state/process_state.json`: the union of every operation's
`failure_modes_shown` + `failure_modes_not_yet_shown` strings. No label is
ever hardcoded in the tool; swapping the book swaps the labels for free.

**Narration vs artifact (the ch7 precedent):** committed chapter 007 prose
legitimately contains anchor-notebook terms as QUOTED ARTIFACT text
(italic lines). A blanket grep would retro-fail an accepted chapter — a
tripwire miscalibrated (LAW 3 corollary b). Deterministic split:

- A line whose entire content is italic (starts and ends with `*` after
  stripping whitespace/blockquote markers) is ARTIFACT QUOTATION → a label
  hit there is reported as WARN (visible, never blocking).
- A label hit in any other line is NARRATION → violation.
- Matching: case-insensitive, on the label with or without its leading
  "the " (the incident text used "The confident specialist").

**Placement — cheapest detection point (LAW 7):** inside
`invoke_writer.py`'s existing post-generation validation (it already
enforces the word floor and owns the salvage machinery). On narration
violation: salvage the draft to `.rejected.md` (existing LAW 9 pattern),
print the offending line numbers + matched labels, raise/exit as a new
`LabelLeakError` signature.

**Orchestrator step-8 error table gains one line:**
`LabelLeakError → retry step 8 once (redo generation; fresh roll), then
alert user with the offending lines — owner may accept explicitly or order
redo from brief.` (Same accept-or-redo semantics as the structural gate;
the tripwire detects, the human decides.)

## 3. Fix checklist

1. `invoke_writer.py`: label-set loader (process_state read-only), the
   narration/artifact line classifier, the check wired into existing
   validation order (AFTER word floor — a truncated draft fails for
   truncation first), salvage + `LabelLeakError` + stderr report
   (line number, matched label, first 60 chars of the line).
2. orchestrator.md step-8 error table: the new line above. Historical note:
   "Added 2026-07 (T-010); ch8 attempt 2 narrated all three labels and no
   check could see it."
3. field_registry.md row: check name, producer (invoke_writer.py), label
   source (process_state failure-mode arrays), consumers (orchestrator
   step-8 error handling), invariant protected (HARD RULE 1), evidence it
   fires (§4.1 fixtures). LAW 15 registration.
4. LAW 5 corollary check (inverse direction): rule 1 already exists in the
   HARD RULES block — no prompt change needed; note this explicitly in the
   registry row so the gate↔hard-rule pairing is recorded complete.

## 4. Acceptance (ALL must pass — both fixtures exist on disk today)

1. **Fixture A (must FAIL):** run the check standalone against the parked
   attempt-2 draft (`prompts/chapter_draft.md` at incident state, or its
   preserved copy — if the run has moved on, use the `.rejected.md`
   salvage or `chapters/chapter_008.md` from the incident tree; record
   which). Expect: narration violations reported for the three labels on
   the "confident specialist / hypothesis tester / executor" narration
   line; nonzero exit. The italic torn-page lines (entries 23–27 at
   incident time) must appear as WARN, not violations.
2. **Fixture B (must PASS):** run against committed
   `chapters/chapter_007.md` → exit 0; the artifact-quoted anchor terms
   (*executor*, *system builder*, *information gatherer*) produce at most
   WARNs. A blanket-grep implementation fails this fixture — that is the
   point of it.
3. Standalone invocation documented (e.g. `invoke_writer.py --check-labels
   PATH`) so the driver and senior can run it zero-token any time.
4. Test suite (sanctioned command) → `1 failed, 331 passed`.
5. `git status --porcelain` → write-set only; one pathspec-limited commit.

## 5. Commit

`fix(tools): deterministic forbidden-label check at the writer bridge (T-010)`

Trailers: `Ticket: T-010` / `Implemented-by: <Codex|Qwen>`.

## 6. Implementer log (append below; never delete the ticket body)

### 2026-07-18 — Codex

- Implemented the runtime-derived forbidden-label check, `LabelLeakError`,
  rejected-draft salvage, and zero-token `--check-labels PATH` mode in
  `invoke_writer.py`; added the Orchestrator error handling and LAW 15 registry
  row.
- Calibrated artifact classification at the matched italic span. This is needed
  because accepted chapter 007 line 181 contains the three artifact labels as
  inline italic spans rather than as a whole-line italic block.
- Fixture A:
  `PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py
  --check-labels fiction_loop/chapters/chapter_008.md` → exit 1; lines 23/25/27
  WARN as artifact labels, line 49 reports the required three narration labels
  (and line 55 reports one additional executor narration hit).
- Fixture B:
  `PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py
  --check-labels fiction_loop/chapters/chapter_007.md` → exit 0; its three
  inline-italic artifact labels WARN.
- Sanctioned serial suite:
  `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q` →
  expected baseline `1 failed, 331 passed`
  (`test_default_splitter_engine_passes_openrouter_timeout_seconds`, missing
  required `source`).
