# TICKET T-007: redo-generation rung tells the truth — conditional living-doc restore after a post-refresh rejection

```
Mode: alone
Depends-on: none. MUST land before T-008 (shared write-set:
            orchestrator.md, RUN.md, structural_gate.py; serialize).
Timing: BETWEEN runs only — chapter 008 must be COMMITTED (or the run
        formally abandoned) first. The ch8 mid-run recovery itself is NOT
        this ticket: the driver applies the restore manually per the
        orchestrator's documented receipt mechanism.
Worktree: main working tree, repo root
Write-set: fiction_loop/agents/orchestrator.md,
           fiction_loop/RUN.md,
           fiction_loop/tools/structural_gate.py
Hot-files: orchestrator.md (T-008 lands here next)
State-access: none — do NOT touch state/, prompts/, core/, chapters/,
              spend files.
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (fired live 2026-07-18, chapter 008 attempt 1)

The structural gate (step 11.5) FAILed the ch8 draft (anchor absent — HARD
RULE 8 under-delivery by the Writer). By then step 10 had already run the
PAID living-doc refresh against that rejected draft — the documented LAW 7
standing violation ("every rejection wastes one call and pollutes the living
doc"). Two documents then actively misled the driver:

- orchestrator.md `redo generation` rung: "No git involved — **nothing was
  mutated**." False after step 10: `core/living_document.md` now contained
  canon from prose that will never exist. A driver following the ladder
  faithfully retries on top of the polluted doc, and the rejected canon
  leaks into every later consumer (the near-miss CONTRIBUTING already
  records as LAW 4 case law).
- structural_gate.py FAIL output offers the redo options with no mention of
  the restore.

The undo ladder's premise ("state mutates only at step 12", LAW 8) is broken
by the step-10 refresh; the ladder inherited the broken premise. Root cause
(the ordering itself) is T-008; THIS ticket makes the ladder truthful and
the recovery mechanical in the meantime (LAW 6: detection/correction while
prevention is pending). It deliberately does NOT touch the step order —
LAW 7's mapped reorder must be done whole (T-008), never partially.

## 2. Fix

**2.1 orchestrator.md — `redo generation` rung (USER COMMANDS, ~line 325).**
Replace the rung body with:

```
redo generation
  → Use when: the draft is bad but the brief is fine, and step 12 has NOT run.
  → IF step 10 (living-doc refresh) already ran for the rejected attempt
    (its log fiction_loop/logs/chapter_[NNN]/10_living_doc_refresh.log shows
    BRIDGE_EXIT:0): FIRST run bash:
      git restore --source=HEAD -- fiction_loop/core/living_document.md
    (HEAD predates the run — one chapter = one commit, nothing is committed
    mid-run — so this is the exact pre-run document; the refresh re-runs
    legitimately on the new draft. Receipt: the tool's pre-refresh
    core/living_document.md.bak.* remains on disk.)
  → Then re-run step 8 only (assembled_prompt.md is intact on disk). Fresh
    retry budget.
  → Cost: one API call (+ the refresh call re-run at step 10 — the rejected
    attempt's refresh call is sunk cost, LAW 7 known debt until T-008).
```

Add one historical line: "Restore condition added 2026-07 (T-007) after the
ch8 rejection polluted the living doc for real; becomes vestigial when
T-008 moves the refresh behind the gate — keep it as defense-in-depth (it
self-neutralizes: the condition can no longer be true)."

**2.2 orchestrator.md — step 11.5 FAIL text.** After "State has not been
touched", add: "…but core/living_document.md HAS been if step 10 ran — the
redo rungs begin with its restore (see USER COMMANDS)."

**2.3 RUN.md — staged-undo summary (~lines 86–91).** Amend the
`redo generation` parenthetical from "(draft bad, one API call)" to
"(draft bad; restore living doc if step 10 ran, then one API call)". No
other RUN.md text change (LAW 2: the rung's full definition lives in
orchestrator.md; RUN.md is the pointer copy and must stay consistent).

**2.4 structural_gate.py — FAIL output fix hint.** After the existing
"Options: …" line, print one static line:

```
If step 10 (living-doc refresh) already ran: first
  git restore --source=HEAD -- fiction_loop/core/living_document.md
```

(House style: receipts + fix hints, like analyst.py. Stdlib-only, zero
tokens, no new inputs — the gate does not itself check the log; the hint is
conditional in wording, deterministic in emission.)

## 3. Acceptance (ALL must pass; dry-run vs HEAD noted)

1. `grep -n "git restore" fiction_loop/agents/orchestrator.md` → present in
   BOTH the `undo state application` rung (pre-existing) and the
   `redo generation` rung (new). (HEAD today: only the former.)
2. `grep -n "nothing was mutated" fiction_loop/agents/orchestrator.md` →
   zero hits. (HEAD today: 1 hit.)
3. `grep -n "living doc" fiction_loop/RUN.md` (case-insensitive) → the
   amended ladder line present.
4. `.venv/bin/python fiction_loop/tools/structural_gate.py` run against the
   CURRENT committed state (post-ch8, passing brief on disk) → exit 0 and
   NO hint line (hint prints only on FAIL). Then verify the FAIL path
   deterministically without touching state: run it with a scratch
   under-populated brief via a copied tree or by reading the code path —
   the hint line must be emitted in the FAIL branch only. Record method
   used in §5.
5. Test suite (sanctioned command) → `1 failed, 331 passed` (documented
   legacy failure only).
6. `git status --porcelain` → changes only in the write-set; one
   pathspec-limited commit.

## 4. Commit

`fix(specs+tools): redo-generation rung restores living doc after post-refresh rejection (T-007)`

Trailers: `Ticket: T-007` / `Implemented-by: <Codex|Qwen>`.

## 5. Implementer log (append below; never delete the ticket body)
