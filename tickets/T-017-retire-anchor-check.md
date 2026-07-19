# TICKET T-017: retire the prose anchor-check (T-014) — remove the hire that needed a babysitter

```
Mode: alone
Depends-on: none. Lands first; T-016 depends on THIS.
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/invoke_writer.py,
           fiction_loop/agents/assembler.md,
           fiction_loop/agents/orchestrator.md,
           fiction_loop/core/field_registry.md
Hot-files: invoke_writer.py, orchestrator.md
Upstream (preconditions — author verified this session 2026-07-19):
  - T-014 landed at ba7204b; the anchor machinery exists in invoke_writer.py:
    ANCHOR_REQUIREMENT_RE, load_anchor_requirement, validate_anchor_presence,
    _normalize_required_prose, --anchor-requirement, and the unconditional
    call inside write_prose_deficiencies (all verified by grep + live run).
  - The structural gate ALREADY catches anchor-absent authoritatively on the
    brief (structural_gate.py: "anchor absent from a gate chapter" — verified);
    retiring the prose pre-check loses only an early catch, not the catch.
Downstream (consumers to re-verify — from field_registry + this session):
  - invoke_writer.py `--check-prose` consumers: T-012's label-only contract
    (§4.1/§4.3) — retiring the anchor call RESTORES it; must re-verify green.
  - orchestrator step-8 `--check-prose` invocation — must still run (labels).
  - field_registry rows for the anchor artifact/field — removed here.
State-access: READ-ONLY (labels from process_state as today). No state/chapter
              writes.
Paid-calls: forbidden. Fully offline.
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (decision 2026-07-19, owner-approved "3c: retire")

T-014 added a prose anchor-check as an *early* catch before the Extractor
spend. It was OPTIONAL from the start (the structural gate already catches
anchor-absent authoritatively), and it was wired into the shared
`write_prose_deficiencies` such that a missing `ANCHOR_REQUIREMENT_JSON`
block crashed the whole prose check — regressing T-012's label-only
contract (see the withdrawn T-015, which existed only to babysit it).
Applying the CAST & FIT lens (Q3): a hire that needs a minder was a bad
hire; the fix is to retire it, not institutionalise the minder. This ticket
removes T-014 wholesale and restores the pre-T-014 `--check-prose`
(label-only) behaviour.

## 2. Fix (revert T-014's surface, keep everything else)

**2.1 invoke_writer.py:** delete `ANCHOR_REQUIREMENT_RE`,
`load_anchor_requirement`, `validate_anchor_presence`,
`_normalize_required_prose`, the `--anchor-requirement` arg and its
guards, and the `validate_anchor_presence` call inside
`write_prose_deficiencies` — so `write_prose_deficiencies` runs ONLY the
label check and never reads an assembled_prompt. Keep `--check-prose`,
`--revise`, `revision_diff_ratio`, the deficiency-record shape, and the
label check exactly as T-012 left them. `--check-prose` with no flag =
label-only, exit 0/1, no traceback.

**2.2 assembler.md:** remove the step-8 `ANCHOR_REQUIREMENT_JSON` emission
instruction and the fenced-block contract added by T-014. Leave the rest of
the anchor SECTION (the human-facing anchor scene guidance) untouched — that
predates T-014 and stays.

**2.3 orchestrator.md:** remove the `anchor_absent` routing note in the
step-8 ladder (T-014's addition). The `--check-prose` call stays (labels);
its FAIL still routes to the revision rung (T-012). Structural anchor
enforcement remains where it always was — the gate at 11.5.

**2.4 field_registry.md:** remove the `anchor_required_prose` /
`anchor_requirement.json` rows added by T-014.

**2.5 LAW 4 audit, same sitting:** grep `anchor_requirement\|
ANCHOR_REQUIREMENT\|validate_anchor_presence\|load_anchor_requirement\|
anchor_absent` across `fiction_loop/`; every hit is removed or is
pre-T-014 human-facing anchor prose (exempt, record in §6). If a live
contract outside the write-set references the retired machinery, STOP-not-widen.

## 3. Acceptance (offline; fixtures from git)

1. `--check-prose fiction_loop/chapters/chapter_007.md` (no flags) → exit 0,
   `prose_deficiencies.json` == `[]`, NO traceback. (T-012 §4.1 restored.)
2. `--check-prose` on the attempt-3 draft
   (`git show cf70a1b:fiction_loop/prompts/chapter_draft.md`) → exit 0, `[]`.
   (T-012 §4.3 restored.)
3. `--check-prose` on the attempt-2 draft
   (`git show d91e558:...`) → exit 1, the 4 forbidden_label records only.
4. `grep -rn "anchor_requirement\|ANCHOR_REQUIREMENT\|validate_anchor_presence" fiction_loop/`
   → zero hits (machinery fully gone).
5. `--check-labels` unchanged on all three fixtures (T-010 green).
6. Test suite → `1 failed, 331 passed`. `git status --porcelain` → only the
   write-set; one commit; no paid call.
7. DOWNSTREAM RE-VERIFY: T-012's `--check-prose` label-only acceptance
   (§4.1/§4.3) is green (that's items 1–3 above — the regression is gone).

## 4. Commit

`revert(tools): retire prose anchor-check (T-014) — restore label-only --check-prose; gate remains the anchor authority (T-017)`

Trailers: `Ticket: T-017` / `Implemented-by: <Codex|Qwen>`.

## 5. Constraints

- Zero paid calls; offline; no state/chapter writes; Raspberry Pi.
- Do NOT touch the structural gate's anchor check — it is the authority and
  stays.
- On ANY failure: STOP, revert, record in §6, leave the tree coherent.

## 6. Implementer log (append below; never delete the ticket body)

- 2026-07-19 — Codex — **IMPLEMENTED.** Removed T-014's
  `ANCHOR_REQUIREMENT_JSON` producer/consumer contract, CLI flag, parsing and
  phrase-matching code, field-registry row, and `anchor_absent` routing notes.
  The pre-existing human-facing anchor guidance and the structural gate were
  untouched; Orchestrator step 8 still invokes `--check-prose` for label
  enforcement.
- Offline acceptance: chapter 007 and ch8 attempt 3 each exited 0 with `[]`;
  ch8 attempt 2 exited 1 with exactly four `forbidden_label` records and no
  traceback. Legacy `--check-labels` passed the two clean fixtures and rejected
  attempt 2 with the same four narration hits. The LAW 4 audit found zero
  retired-machinery hits across `fiction_loop/`; `git diff --check` passed.
  The sanctioned serial suite produced the documented baseline:
  `1 failed, 331 passed` (only
  `test_default_splitter_engine_passes_openrouter_timeout_seconds`). The first
  suite invocation hit the known read-only uv-cache harness restriction; the
  exact command completed after approved cache access. No paid call or
  state/chapter write was made.

- 2026-07-19 — senior — **ACCEPTED.** Independently re-ran acceptance against
  `f739452`: `--check-prose` label-only restored (ch7 → `[]` exit 0; attempt-3
  → `[]` exit 0; attempt-2 → 4 `forbidden_label` exit 1 — T-012 §4.1/§4.3
  regression gone); `grep -rn` for anchor machinery across `fiction_loop/` →
  ZERO hits; `--anchor-requirement` flag removed (unrecognized); suite
  `1 failed, 331 passed` (baseline). Downstream (T-012 label-only) green.
  T-016 is now unblocked.
