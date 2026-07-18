# TICKET T-009: gate pass-receipt — the Updater cannot run without a fresh gate PASS on the exact brief it consumes

```
Mode: alone
Depends-on: T-007 and T-008 MERGED FIRST (all three edit structural_gate.py
            and orchestrator.md; serialize T-007 → T-008 → T-009).
Timing: BETWEEN runs only — chapter 008 committed or formally abandoned
        first.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/structural_gate.py,
           fiction_loop/agents/orchestrator.md,
           fiction_loop/agents/updater.md (precondition line only),
           fiction_loop/core/field_registry.md
Hot-files: structural_gate.py, orchestrator.md (T-007/T-008 land there first)
State-access: none. The receipt artifact lives in fiction_loop/prompts/
              (pipeline artifact layer), never in state/.
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (fired live 2026-07-18, chapter 008 attempt 2)

After a gate FAIL and a `redo generation`, the driver session skipped steps
10/11/11.5 and spawned the Updater (step 12) directly. The Updater — the
one NON-IDEMPOTENT agent — began applying `update_brief.json` from the
REJECTED attempt (mtime 19:11, extracted from prose that no longer exists;
the gate's only verdict on that brief was FAIL). It created five card files
and modified a concept card before the owner killed it; recovery required
the staged-undo rung (cards restored, five files deleted — receipts in
handoff §7).

The invariant "state mutates only after a gate PASS" existed only as prose
in orchestrator step 11.5 ("Exit 1 → STOP before the Updater"). A driver
that skips a step skips the prose with it. LAW 6: make the violation
impossible, not forbidden. LAW 9 corollary (artifact freshness): a consumer
must be unable to consume a stale producer output silently.

## 2. Fix

**2.1 structural_gate.py — write a receipt on PASS, destroy it on FAIL.**
- On exit 0: write `fiction_loop/prompts/.gate_pass.json`:
  `{ "chapter": "NNN", "brief_sha256": <sha256 of update_brief.json bytes>,
     "verdict": "PASS", "at": <ISO timestamp> }`
  (chapter from the brief's own chapter field).
- On exit 1 (or any exception): DELETE the receipt file if present, before
  printing findings (LAW 9 freshness: a failed producer makes staleness
  impossible to miss).
- New mode `--verify`: recompute sha256 of the CURRENT update_brief.json;
  exit 0 iff the receipt exists, verdict PASS, and hashes match; else exit 1
  printing exactly why (`no receipt` / `hash mismatch — brief changed since
  gate PASS` / `receipt verdict not PASS`). Read-only in this mode. Stdlib
  only, zero tokens.
- Hash-by-bytes means ANY change to the brief (re-extraction, hand tamper)
  invalidates the receipt automatically — no TTL or step-counter needed.

**2.2 orchestrator.md — step 12 gains a deterministic preamble.** Before the
SPAWN Updater block:

```
12.0 Run bash — GATE RECEIPT CHECK (deterministic, zero tokens):
    .venv/bin/python fiction_loop/tools/structural_gate.py --verify
    Exit 0 → spawn the Updater (12.1).
    Exit 1 → STOP. Do not spawn the Updater under ANY instruction short of
    the owner's explicit written override. Report the verify output
    verbatim. The remedy is always to re-run the missing steps (10/11/11.5),
    never to skip this check.
```

Historical line: "Added 2026-07 (T-009) after the ch8 attempt-2 incident:
a driver skipped 10/11/11.5 post-redo and the Updater applied a
gate-FAILED brief; caught mid-mutation, undone via the staged ladder."

**2.3 updater.md — one precondition line at the top of UPDATE SEQUENCE:**
"Precondition: the orchestrator has just run `structural_gate.py --verify`
with exit 0 (step 12.0). If you cannot confirm this from the conversation,
STOP and return BLOCKED — you are the only non-idempotent agent."

**2.4 field_registry.md — register the artifact (LAW 4/LAW 15):**
`prompts/.gate_pass.json` — producer: structural_gate.py (written on PASS,
deleted on FAIL); consumers: orchestrator step 12.0 (`--verify`). Invariant
protected: state mutates only after a gate PASS on the byte-identical
brief. Evidence it can fire: T-009 acceptance runs below + the ch8 incident
it would have stopped.

**2.5 Housekeeping:** add `.gate_pass.json` to the chapter transaction's
commit pathspec treatment consistent with other prompts/ artifacts (it
rides along like update_brief.json; no .gitignore change).

## 3. Acceptance (ALL must pass)

1. FAIL path, runnable now against the parked ch8 tree (brief on disk is
   attempt-1's, gate-FAILing): run the gate → exit 1 AND no
   `.gate_pass.json` exists afterward; run `--verify` → exit 1 "no receipt".
   Record outputs in §5.
2. Tamper path: create a receipt by hand-crafting is NOT tested by editing
   state — instead: after any legitimate PASS receipt exists (see 3),
   append one byte to a COPY of the brief in the scratchpad and verify the
   hash logic via a scratch-tree run, OR verify by code inspection if a
   scratch tree is impractical on the Pi; record which.
3. PASS path: first live validation rides the next successful chapter run —
   after its gate PASS, `.gate_pass.json` exists, `--verify` exits 0, and
   the run's step 12.0 log line shows the check ran. Senior re-checks at
   next acceptance (same deferral precedent as T-006 mid-run guard /
   T-008 §4.7).
4. `grep -n "12.0" fiction_loop/agents/orchestrator.md` → preamble present
   before the SPAWN Updater block; updater.md precondition line present.
5. Test suite (sanctioned command) → `1 failed, 331 passed`.
6. `git status --porcelain` → write-set only; one pathspec-limited commit.

## 4. Commit

`fix(tools+specs): gate pass-receipt — Updater unreachable without fresh gate PASS (T-009)`

Trailers: `Ticket: T-009` / `Implemented-by: <Codex|Qwen>`.

## 5. Implementer log (append below; never delete the ticket body)

### 2026-07-18 — Codex — IMPLEMENTED

- Timing/dependency gates: PASS. T-007 (`b8f0b7c`) and T-008 (`3ab5f5a`)
  are merged; current handoff §9 records chapter 008 formally abandoned.
  Paid calls: none. Repository state and parked pipeline artifacts were not
  modified.
- `structural_gate.py` now hashes the exact brief bytes, writes
  `prompts/.gate_pass.json` only on PASS, and deletes any prior receipt
  before reporting gate FAIL or an exception. Read-only `--verify` checks
  receipt presence, PASS verdict, and the current brief hash.
- Orchestrator step 12.0 deterministically verifies the receipt before the
  Updater spawn; updater.md carries the matching non-idempotent-agent
  precondition. The registry records producer, consumer, protected invariant,
  and firing evidence. The chapter transaction text explicitly records that
  the receipt rides with the prompt artifacts.
- Live parked-brief FAIL acceptance:
  `STRUCTURAL GATE: FAIL` with
  `anchor absent from a gate chapter (owner rule D3/F16)`; exit 1;
  `.gate_pass.json` absent afterward. `--verify` printed exactly
  `no receipt` and exited 1.
- Scratch-tree PASS/tamper acceptance (`/tmp/t009-scratch`, no repo artifact
  edits): after changing only the copied brief's rejected anchor boolean so
  the complete deterministic gate legitimately passed, the gate wrote a
  receipt for chapter 008 and `--verify` printed
  `gate receipt verified: PASS` with exit 0. Adding one whitespace byte to
  the copied brief then made `--verify` print exactly
  `hash mismatch — brief changed since gate PASS` and exit 1.
- Static acceptance: orchestrator step 12.0 precedes the 12.1 Updater SPAWN;
  updater precondition is present; `py_compile` and `git diff --check` PASS.
  LAW 4 phrase audit found the new machinery only in the four ticket files;
  other gate/step-12 hits describe the existing pipeline order and need no
  receipt-contract change.
- Sanctioned serial suite:
  `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q` →
  expected `1 failed, 331 passed`; sole failure is the documented
  out-of-scope `test_default_splitter_engine_passes_openrouter_timeout_seconds`
  (`default_splitter_engine()` missing `source`).
- First live PASS receipt and step-12.0 log evidence remain intentionally
  deferred to the next successful owner-started chapter run, per §3.3.
