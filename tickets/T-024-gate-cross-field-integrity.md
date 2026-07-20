# TICKET T-024: structural gate cross-field integrity — bind the brief's focal id / chapter / failure-list to the schedule so a mis-id or padded count cannot pass

```
Mode: alone
Timing: BETWEEN runs only. No chapter run in flight. (Highest value applied
        BEFORE the ch9 run — ch9 is a return_to_character, the exact case ADV-1
        breaks.)
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/structural_gate.py,
           fiction_loop/tools/regression/run.py (extend: new assertions),
           fiction_loop/core/field_registry.md (register the new gate checks)
Hot-files: none
Upstream (preconditions — author dry-ran EACH 2026-07-20, HEAD 9d0966c — chassis code identical to fe2e20d, intervening commit docs-only):
  - structural_gate.py run_gate() reads prompts/update_brief.json +
    state/master_state.json; today it checks quota/anchor/echo/F14/F15 ONLY —
    grep confirms NO population_index / char_id / pointer cross-check exists
    (verified: `grep -nE 'population_index|char_id' tools/structural_gate.py`
    → no code hits, docstring only).
  - master_state.json carries `next_chapter_pointer` (chapter, type, char_id)
    and `population_index` (list of {id,name,...}) — verified against the live
    file; the ch9 pointer is {chapter "009", type return_to_character, char_id
    char_004}, and char_004 is present in population_index.
  - At gate time for chapter N, master_state.next_chapter_pointer still
    describes chapter N (the Updater overwrites it only at step 12, AFTER the
    gate) — verified from updater.md STEP 7 ordering.
  - update_brief carries focal_character.{id,is_new,name},
    process_updates.failure_modes_shown_this_chapter, chapter — verified
    against the live ch8 brief.
  - process_state.json holds each operation's failure pool
    (failure_modes_shown + failure_modes_not_yet_shown) — the SAME source
    invoke_writer.py derives its label set from (field_registry row for the
    forbidden-label check). Verified present.
  - Sanctioned pytest baseline: `1 failed, 331 passed` (documented pre-existing
    failure only).
Downstream (consumers to re-verify): structural_gate.py is consumed by
  Orchestrator step 11.5 (run) + step 12.0 (--verify) and frozen by
  tools/regression/run.py → the regression suite MUST gain assertions for the
  new checks and stay green (LAW 17). field_registry gate-consumed-booleans row
  updated. No state schema changes → no Updater/Extractor re-verify.
State-access: READ-ONLY (reads master_state.json, process_state.json,
              update_brief.json; writes only prompts/.gate_pass.json as today).
Paid-calls: forbidden. Stdlib only, zero tokens (gate invariant).
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 15 (registered machinery +
evidence it fires), LAW 16 (a new check ships with its check), LAW 17 (the
regression suite is the consumer re-verification). LAW 14: the failure-mode
membership set is derived from the pack (process_state), never hardcoded — do
NOT copy the 14 canonical names into gate code (that would be a NEW leak of the
QUOTA_BY_ARC class).

## 1. Problem (verified 2026-07-20)

The structural gate weighs the brief but never checks it is the RIGHT brief for
the scheduled chapter. Three concrete escapes, all reachable, one imminent:

- **ADV-1 (imminent, ch9):** the gate never binds `focal_character.id` to the
  schedule. ch9 is a `return_to_character` for `char_004`. If the Extractor
  writes the wrong existing id, or sets `is_new: true` with a fresh id for a
  character who is actually a return, the gate passes; the Updater (STEP 1) then
  updates the WRONG character's card, or CREATES A DUPLICATE card +
  population_index row. Nothing catches it — and the damage lands on Wanjiku's
  `name_due` return payoff (five chapters after her ch4 setup).
- **ADV-2:** the anti-under-population check (its whole reason for existing —
  ch4 "a third of its ordered cast") counts `len(failure_modes_shown_this_chapter)`.
  A duplicate or non-canonical entry (`["the executor","the executor"]`)
  satisfies `len >= quota` while the prose shows one wrong approach. Under-
  population passes.
- **ADV-4:** `verify_receipt()` confirms the brief's bytes are unchanged but
  never checks the brief is for the chapter being applied. VERIFIED LIVE THIS
  SESSION: the leftover ch8 brief + receipt still return `--verify` exit 0
  (`gate receipt verified: PASS`) — a stale PASS. If an N+1 run reached step
  12.0 without regenerating, it would re-apply chapter N.

## 2. Fix

All additions are deterministic, stdlib-only, and read data already present.

**2.1 In `run_gate()`, after loading `brief` and `ms`, before the ctype block —
schedule/identity binding (ADV-1, ADV-4):**
```python
ptr = ms.get("next_chapter_pointer") or {}
pop_ids = {c.get("id") for c in (ms.get("population_index") or [])}

# (a) the gated chapter is the scheduled one
if brief.get("chapter") != ptr.get("chapter"):
    problems.append(
        f"brief chapter {brief.get('chapter')} != scheduled "
        f"{ptr.get('chapter')} (stale or mismatched brief)"
    )

# (b) focal identity matches the schedule / population
fc = brief.get("focal_character") or {}
if ctype in ("new_focal_character", "return_to_character"):
    if ctype == "return_to_character":
        if fc.get("id") != ptr.get("char_id"):
            problems.append(
                f"return focal id {fc.get('id')} != scheduled "
                f"{ptr.get('char_id')}"
            )
        if fc.get("is_new") is not False:
            problems.append("return focal must have is_new=false")
        if fc.get("id") not in pop_ids:
            problems.append(f"return focal id {fc.get('id')} not in population_index")
    else:  # new_focal_character
        if fc.get("is_new") is not True:
            problems.append("new_focal_character focal must have is_new=true")
        if fc.get("id") in pop_ids:
            problems.append(
                f"new focal id {fc.get('id')} already in population_index "
                f"(duplicate)"
            )
```
(`fc` may already be assigned later in the function — reuse one binding; do not
shadow.)

**2.2 In the quota block, replace the bare length check with distinct +
canonical-membership (ADV-2).** Derive the valid set from the taught operation's
pool in process_state.json — NOT a hardcoded list:
```python
ps = json.loads((R / "state/process_state.json").read_text())
op = (brief.get("process_updates") or {}).get("operation")
op_pool = (ps.get("operations") or {}).get(op, {})
valid = set(op_pool.get("failure_modes_shown", [])) | set(
    op_pool.get("failure_modes_not_yet_shown", [])
)
distinct = list(dict.fromkeys(shown))            # order-preserving dedupe
if len(distinct) < quota:
    problems.append(
        f"wrong-approach scenes: {len(distinct)} distinct of {quota} "
        f"required for arc {arc} ({shown})"
    )
if valid:
    bad = [s for s in shown if s not in valid]
    if bad:
        problems.append(f"non-canonical failure-mode label(s): {bad}")
```
(If the pool lookup yields an empty `valid` set — e.g. schema drift — skip the
membership check but keep distinctness; never hard-fail on a missing pool.)

**2.3 In `verify_receipt()`, add a chapter-freshness bind (ADV-4):** after the
hash match succeeds, also require `receipt.get("chapter") == brief.get("chapter")`
(the receipt already stores `chapter`; read the brief JSON, not just bytes) and
that `brief["chapter"]` equals `master_state.next_chapter_pointer.chapter`. Any
mismatch → print "receipt stale — chapter mismatch" and return 1.

**2.4 Register** in field_registry.md: extend the gate-consumed row to include
`focal_character.id` / `next_chapter_pointer` / `population_index` /
process_state failure pools as gate inputs, with the ADV-1/2/4 case law
(one-line each). Add the assertions to the LAW 15 evidence.

**2.5 Regression (tools/regression/run.py):** add assertions that FAIL on a
crafted-bad brief and PASS on the live ch8 brief:
- ch8 brief (fixture) → gate PASS (all new checks satisfied: chapter 008 ==
  pointer, new focal char_008 ∉ prior population, 2 distinct canonical labels).
- a return brief whose focal id ≠ pointer.char_id → FAIL naming the mismatch.
- a brief with `["the executor","the executor"]` at quota 2 → FAIL
  "1 distinct of 2".
- a receipt whose chapter ≠ brief chapter → `--verify` exit 1.

## 3. Acceptance (offline; author dry-ran each precondition)

1. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/structural_gate.py` on
   the live ch8 brief → still PASS (arc 2, quota 2); receipt written.
2. Each ADV crafted-bad input above → gate/verify exit 1 naming the specific
   problem (implementer records the observed lines in §6 — LAW 15 evidence).
3. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` →
   exit 0, all PASS (old + new assertions), tree clean after.
4. Sanctioned pytest → `1 failed, 331 passed` (unchanged).
5. `git status --porcelain` → only the write-set; one commit; no paid call.
6. DOWNSTREAM RE-VERIFY: regression suite green (item 3); Orchestrator gate
   steps unchanged in interface (still exit 0/1 + receipt).

## 4. Commit

`feat(gate): cross-field integrity — bind brief focal-id/chapter/failure-list to schedule (ADV-1/2/4, T-024)`

Trailers: `Ticket: T-024` / `Implemented-by: <Codex|Qwen>`.

## 5. Constraints

- Raspberry Pi; zero paid calls; stdlib only; no state/chapter writes (only
  prompts/.gate_pass.json as today).
- Do NOT hardcode the canonical failure-mode names in gate code — derive from
  process_state pools (LAW 14). Do NOT resolve ADV-3 here (whether the quota
  should apply to returns at all is an OPEN OWNER DECISION — this ticket keeps
  the existing quota semantics and only adds orthogonal checks).
- On ANY failure: stop at that step, revert, record in §6; do not improvise.

## 6. Implementer log (append below; never delete the ticket body)

- [ ] 2.1 schedule/identity binding
- [ ] 2.2 distinct + canonical membership
- [ ] 2.3 receipt freshness bind
- [ ] 2.4 field_registry + LAW 15 registration
- [ ] 2.5 regression assertions
- [ ] acceptance 1–6
- [ ] commit
