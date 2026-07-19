# TICKET T-016: tool regression suite — freeze the fiction_loop tool contracts so a shared-surface change cannot silently regress a consumer

```
Mode: alone
Depends-on: T-017 MERGED FIRST (retires the anchor-check; the suite freezes
            the POST-retirement label-only --check-prose contract). Not
            dependent on the withdrawn T-015.
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/regression/  (new dir: runner + frozen fixtures),
           fiction_loop/core/field_registry.md (register suite + fixtures),
           fiction_loop/CONTRIBUTING.md (LAW 15 registration line ONLY)
Hot-files: none
Upstream (preconditions — author dry-ran EACH this session 2026-07-19):
  - POST-T-017, invoke_writer.py exposes: --check-labels, --check-prose
    (label-only), --revise --dry-run, revision_diff_ratio,
    REVISION_MAX_DIFF_RATIO (verified against current tree; --anchor-requirement
    is GONE after T-017).
  - structural_gate.py --verify → "no receipt"/exit 1 with no receipt (verified).
  - Fixtures retrievable: ch7 = committed chapters/chapter_007.md; attempt-2
    (label leak) = git show d91e558:.../chapter_draft.md; attempt-3 (clean
    labels) = git show cf70a1b:.../chapter_draft.md (all verified).
  - Sanctioned suite command works (verified: 1 failed, 331 passed).
Downstream (consumers to re-verify): none — new LEAF machinery. Its PURPOSE
  is to BECOME the downstream check future tool tickets must run; it regresses
  no existing consumer.
State-access: READ-ONLY. Writes only under tools/regression/ and the tools'
              normal prompts/ transient outputs (cleaned up). No state/chapter.
Paid-calls: forbidden. Every assertion offline (--dry-run for revision).
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 15 (registered machinery with
the invariant it protects + evidence it fires); LAW 17 (this suite IS the
enforcement of "re-verify consumers").

## 1. Problem (verified 2026-07-19)

The fiction_loop TOOLS have no regression net. The product pipeline has the
analyst (state) and the structural gate (chapters); `invoke_writer.py` /
`structural_gate.py` — the machinery that MAKES chapters — have none.
Consequence, live: T-014 changed shared code and silently regressed T-012's
`--check-prose` contract; caught only by hand. The acceptance fixtures we keep
hand-running (ch7 / attempt-2 / attempt-3) are a regression suite existing
only as muscle memory. Freeze it so the catch is structural. This is the CLASS
fix (T-017 was the instance fix for the anchor case); it is the mechanical
enforcement LAW 17 requires.

## 2. Fix

**2.1 Freeze the fixtures** under `fiction_loop/tools/regression/fixtures/`
as committed files (never git-show at runtime):
- `ch7_clean.md` ← copy of chapters/chapter_007.md
- `attempt2_labelleak.md` ← `git show d91e558:fiction_loop/prompts/chapter_draft.md`
- `attempt3_clean.md` ← `git show cf70a1b:fiction_loop/prompts/chapter_draft.md`

**2.2 A single offline runner** `fiction_loop/tools/regression/run.py` that
runs the frozen tool contracts, prints one PASS/FAIL line per assertion, and
exits 0 (all green) / nonzero (any red). Assertions (post-T-017 contract,
each verified this session):
- `--check-labels`: ch7 exit 0; attempt-2 exit 1; attempt-3 exit 0.
- `--check-prose` (label-only, no anchor after T-017): ch7 → [] exit 0, NO
  traceback; attempt-3 → [] exit 0; attempt-2 → 4 forbidden_label exit 1.
- `revision_diff_ratio`: identical → 0.0; a >25% change → > REVISION_MAX_DIFF_RATIO.
- arg-guards: `--revise` without `--deficiencies` errors; `--check-prose`
  with `--output` errors.
- `structural_gate.py --verify` with no receipt → nonzero + "no receipt".
Runner cleans any prompts/ artifacts it creates (prose_deficiencies.json,
revision_prompt.md) so it leaves the tree as it found it.

**2.3 Register** in `field_registry.md` (the suite consumes the tool CLIs +
frozen fixtures; consumed by the ticket process) and add ONE LAW 15 line in
CONTRIBUTING naming the suite, the invariant it protects (tool contracts do
not silently regress), and its evidence-it-fires (a red at the attempt-2
fixture). No pytest — standalone offline runner (T-010 CLI-test precedent).

## 3. Acceptance (offline)

1. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` →
   exit 0, every line PASS, tree left clean (`git status --porcelain` empty
   after).
2. **Red-on-regression proof:** temporarily point one assertion at a wrong
   expectation → runner exits nonzero naming the failing assertion; restore.
   Record the observed red in §6 (LAW 15 evidence-it-fires).
3. Sanctioned pytest suite → `1 failed, 331 passed` (unchanged).
4. LAW 15 line + field_registry rows present.
5. `git status --porcelain` → only the write-set; one commit; no paid call.
6. DOWNSTREAM RE-VERIFY: none (leaf).

## 4. Commit

`feat(tools): tool regression suite — freeze fiction_loop tool contracts against silent consumer regressions (T-016)`

Trailers: `Ticket: T-016` / `Implemented-by: <Codex|Qwen>`.

## 5. Constraints

- Raspberry Pi; zero paid calls; offline; no state/chapter writes.
- Fixtures are FROZEN — a fixture change is a deliberate, reviewed contract
  change, never a runtime regeneration.
- If ANY §2 item cannot be completed, STOP and revert; record in §6.

## 6. Implementer log (append below; never delete the ticket body)

- 2026-07-19 — Codex: implemented the standalone offline runner and three
  frozen fixtures; registered the suite in `field_registry.md` and under LAW
  15. Green acceptance: `run.py` exited 0 with 11/11 assertions PASS and
  restored transient prompt artifacts. Evidence-it-fires: temporarily changed
  the attempt-2 prose expectation from 4 deficiencies to 0; the runner exited
  1, named `FAIL: check-prose attempt-2 returns 4 forbidden_label records`,
  and summarized `FAIL: 10/11 assertions passed`; then restored and reran
  green. Fixture byte comparisons matched all three declared sources.
  Sanctioned pytest baseline: `1 failed, 331 passed` (only the documented
  pre-existing
  `test_default_splitter_engine_passes_openrouter_timeout_seconds` failure).
