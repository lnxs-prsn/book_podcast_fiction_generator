# TICKET T-015: --check-prose must not crash when no anchor block is present (T-014 regression)

> **WITHDRAWN 2026-07-19 — SUPERSEDED BY T-017 (retire the anchor-check).**
> This ticket existed only to *babysit* T-014 (decouple its anchor check from
> the label check). The owner chose to RETIRE T-014 instead (decision "3c";
> CAST & FIT Q3 — a hire that needs a minder was a bad hire). T-017 removes
> the coupling by removing the component, which subsumes this fix — retiring
> the anchor check restores `--check-prose` to label-only. DO NOT IMPLEMENT.
> Kept for provenance.

```
Mode: alone
Depends-on: T-012 + T-014 MERGED (they are — 4834101, ba7204b). This
            repairs their interaction.
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/invoke_writer.py,
           fiction_loop/agents/orchestrator.md (the step-8 --check-prose
           invocation line + §ladder note only)
Hot-files: invoke_writer.py, orchestrator.md
State-access: READ-ONLY (process_state labels; the assembled_prompt for the
              anchor block). No writes to state/ or chapters/.
Paid-calls: forbidden. Fully offline acceptance (fixtures on disk).
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 1 (clean handled errors,
not raw tracebacks), LAW 15 (no machinery that cannot fire / no false
confidence).

## 1. Problem (regression found at T-012/T-014 acceptance, 2026-07-19)

T-014 wired the anchor check into the SHARED prose-check path
unconditionally: `write_prose_deficiencies` always calls
`validate_anchor_presence`, and `load_anchor_requirement` RAISES when the
assembled_prompt has no `ANCHOR_REQUIREMENT_JSON` block. Consequences,
verified against HEAD:

- **T-012 §4.1/§4.3 REGRESSED.** `--check-prose <draft>` with NO
  `--anchor-requirement` (its accepted label-only contract) now dies:
  `ValueError: assembled_prompt.md must contain exactly one
  ANCHOR_REQUIREMENT_JSON block`, surfaced as a raw "Unexpected error"
  traceback. At T-012's own commit these passed; T-014 broke them by
  changing shared code without re-running T-012's acceptance.
- **The label check is now hostage to the anchor contract.** A missing or
  stale block kills forbidden-label detection too — they are independent
  concerns and must fail independently.
- **Raw-traceback failure mode** (LAW 1): even the intended path, given a
  malformed/absent block, exits via the generic handler with a stack
  trace, not a one-line handled error.

Live happy-path is currently OK ONLY because the Assembler (assembler.md
step 8) always emits the block; the orchestrator's step-8 call passes NO
`--anchor-requirement` (orchestrator.md:201) and relies on that. That
coupling is exactly the brittle, unwritten dependency to remove.

## 2. Design (single outcome, LAW 2/3)

Split the two concerns cleanly and put anchor enforcement where the block
is guaranteed:

1. **`--check-prose` runs labels ALWAYS; runs the anchor check ONLY when an
   anchor requirement is explicitly supplied** (`--anchor-requirement
   FILE`). No flag → labels only, no anchor call, no crash. This restores
   T-012 §4.1/§4.3 verbatim.
2. **The Orchestrator's live step-8 call passes
   `--anchor-requirement fiction_loop/prompts/assembled_prompt.md`** so the
   anchor check IS enforced in the live path (where the Assembler
   guarantees the block). Enforcement does not silently vanish — it moves
   to the one call site that has the block, not the label-only standalone
   call.
3. **A supplied-but-missing/malformed block is a CLEAN handled error**
   (print a one-line message naming the problem, exit 1), NOT a raw
   traceback — same shape as the tool's other handled errors. When
   `--anchor-requirement` is given and the file lacks exactly one valid
   block, that is a real defect worth halting on (the Assembler should have
   emitted it), but it must halt legibly.

Do NOT make "absent block" a silent no-op inside the flagged path — that
would be the LAW 15 false-confidence trap (anchor check that never fires).
The no-op is only for the UN-flagged standalone call, which by contract is
label-only.

## 3. Fix

**3.1 invoke_writer.py:**
- `write_prose_deficiencies` (or its caller in `main`): only invoke
  `validate_anchor_presence` when an anchor-requirement path was explicitly
  provided. Signature suggestion: pass `prompt_path: Path | None`; when
  `None`, skip the anchor check entirely and return labels only.
- `main`'s `--check-prose` branch: pass the anchor path only when
  `args.anchor_requirement` is set; otherwise `None` (today it defaults to
  `DEFAULT_ASSEMBLED_PROMPT`, which is the bug).
- Wrap `load_anchor_requirement`'s validation failures so a supplied file
  with no/duplicate/malformed block prints a clean one-line error and exits
  1 (no traceback). Keep the strictness (exactly one valid block) for the
  flagged path.

**3.2 orchestrator.md:** the step-8 (`On Success, run --check-prose …`) line
and the step-8 ladder note (~lines 201, 372): add
`--anchor-requirement fiction_loop/prompts/assembled_prompt.md` to the
`--check-prose` invocation, so the live anchor check is enforced. One
sentence noting the standalone (no-flag) form is label-only by design.

**3.3 LAW 4 audit, same sitting:** grep `check-prose\|anchor_requirement\|
validate_anchor_presence\|load_anchor_requirement` across
`fiction_loop/agents/ fiction_loop/core/ fiction_loop/tools/
fiction_loop/RUN.md fiction_loop/specs/`; update or exempt EVERY hit,
record in §5. If a live contract OUTSIDE the write-set states the coupling,
STOP-not-widen (T-008 precedent).

## 4. Acceptance (ALL offline; fixtures regenerated from git)

Setup: `git show d91e558:fiction_loop/prompts/chapter_draft.md` → attempt2
(labels + anchor phrase present); `git show
cf70a1b:fiction_loop/prompts/chapter_draft.md` → attempt3 (labels clean,
anchor phrase ABSENT). Build `anchor_present.md` containing exactly one
block: `{"anchor_appears": true, "anchor_required_prose": ["The condition
itself provides the test. Solvers who skip the condition skip the gate."]}`.

1. **T-012 §4.1/§4.3 restored:** `--check-prose chapters/chapter_007.md`
   (NO flag) → exit 0, `prose_deficiencies.json` == `[]`, NO traceback.
   Same on the attempt3 fixture (NO flag) → exit 0, `[]`.
2. `--check-prose <attempt2>` (NO flag) → exit 1 with the 4 forbidden_label
   records only; no anchor record; no traceback.
3. `--check-prose <attempt3> --anchor-requirement anchor_present.md` →
   exit 1, one `anchor_absent` record. (Anchor enforced when asked.)
4. `--check-prose <attempt2> --anchor-requirement anchor_present.md` →
   exit 1, 4 forbidden_label records, NO anchor_absent (phrase present).
5. `--check-prose <attempt3> --anchor-requirement <file with a MALFORMED /
   absent block>` → clean one-line error, exit 1, NO Python traceback.
6. orchestrator.md step-8 line now contains
   `--anchor-requirement fiction_loop/prompts/assembled_prompt.md`.
7. Legacy `--check-labels` unchanged on all three fixtures (T-010 green).
8. Test suite → `1 failed, 331 passed`. `git status --porcelain` → only the
   write-set; one commit; no paid call (spend byte-identical).

## 5. Commit

`fix(tools): --check-prose runs labels standalone; anchor check enforced only when required (T-015, repairs T-014 regression)`

Trailers: `Ticket: T-015` / `Implemented-by: <Codex|Qwen>`.

## 6. Constraints

- Raspberry Pi; zero paid calls; no state/chapter writes.
- Do NOT make the flagged anchor path a silent no-op (LAW 15).
- If ANY §3 item cannot be completed, STOP and revert; record in §5.

## 7. Implementer log (append below; never delete the ticket body)
