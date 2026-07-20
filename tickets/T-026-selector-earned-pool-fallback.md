# TICKET T-026: featured-failure selector — earned-pool fallback + retire the "none"-on-teaching-chapter escape (ADV-3)

```
Mode: alone
Timing: BETWEEN runs only. No chapter run in flight. (Must land BEFORE the ch9
        run — ch9 is the first return_to_character whose taught operation's own
        failure pool is exhausted, the exact case this fixes.)
Worktree: main working tree, repo root
Write-set: fiction_loop/agents/extractor.md (selector rule + "none" contract),
           fiction_loop/tools/structural_gate.py (deterministic guard),
           fiction_loop/tools/regression/run.py (extend: new assertions),
           fiction_loop/core/field_registry.md (register fallback + guard case law)
Hot-files: none
Upstream (preconditions — author dry-ran EACH 2026-07-20, HEAD b5e9ff4 — chassis code identical to fe2e20d/starting_factory, intervening commits docs-only):
  - The featured-failure selector is PURELY agent-driven: `failure_mode_to_show`
    is computed by the Extractor LLM per extractor.md:369-388; NO .py tool
    computes it (verified: `grep -rnE 'failure_mode_to_show' fiction_loop/tools/`
    → no hits). extractor.md:388 emits `"none" if operation_due is null or list
    is empty` — the exact bug line.
  - extractor.md:369-372 primary rule = op's own failure_modes_not_yet_shown,
    least-recently-LED, tiebreak least-recently-SHOWN; extractor.md:376 records
    the 2026-07-04 WHY-LED-NOT-SHOWN owner ruling (do NOT invert it).
  - init_state.py:497 seeds each op's `failure_modes_not_yet_shown` =
    FAILURE_POOLS[arc_introduced] → an op's pool is its introduction-arc pool,
    fully spent at touch 1 (arc quota == pool size). Verified.
  - LIVE: process_state.json op_separate_condition
    `failure_modes_not_yet_shown == []`, `failure_modes_shown ==
    ["the executor","the system builder","the information gatherer"]`; the ch9
    pointer is {type return_to_character, operation op_separate_condition,
    failure_mode_to_show "none"}. Verified against the live files.
  - The earned-types union is derivable pack-side: ∪ over process_state
    operations of (failure_modes_shown ∪ failure_modes_not_yet_shown). At ch9
    that union contains "the hypothesis tester" (arc-2 type, never in
    failure_mode_lead_history, never in any op's failure_modes_shown). Verified.
  - At gate time for chapter N, master_state.next_chapter_pointer still describes
    chapter N (Updater overwrites it only at step 12, AFTER the gate) — same
    upstream fact T-024 relies on (updater.md STEP 7 ordering).
  - Sanctioned pytest baseline: `1 failed, 331 passed` (documented pre-existing
    failure only).
Downstream (consumers to re-verify):
  - structural_gate.py is consumed by Orchestrator step 11.5 (run) + 12.0
    (--verify) and frozen by tools/regression/run.py → regression MUST gain
    assertions for the new guard and stay green (LAW 17).
  - The Assembler reads pointer.failure_mode_to_show as the lead wrong approach
    (assembler.md:179). After this fix it will NEVER receive "none" on a teaching
    chapter → re-confirm the Assembler still consumes a real type correctly (it
    already does; the fix removes an off-contract input, adds none).
  - **C3 (DECISION 12) is a FUTURE consumer of this exact rotation machinery** —
    the fallback/guard select "least-recently-X ITEM"; C3 will swap the item from
    failure TYPE to led BEAT. Keep unit-agnostic (see §5). LAW 17 note.
  - field_registry gate-consumed row + selector row updated. No state SCHEMA
    change → no Updater re-verify beyond the Assembler note above.
  - COORDINATION: T-024 also adds next_chapter_pointer reads to structural_gate.py
    → serialize. If T-024 landed first, reuse its `ptr`/`pop_ids` bindings; do not
    duplicate.
State-access: READ-ONLY (gate reads master_state.json + process_state.json;
              writes only prompts/.gate_pass.json as today).
Paid-calls: forbidden. NOTE: the extractor.md change is a PROMPT edit — it takes
            effect only on the next paid Extractor run, so it is validated by
            review + the deterministic guard/regression, NOT by an offline
            execution. The guard (structural_gate.py) IS offline-testable.
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 14 (the earned-types set is
derived from the pack, NEVER a hardcoded list of the 14 canonical names — that
would be a fresh QUOTA_BY_ARC-class leak), LAW 15 (registered machinery + evidence
it fires), LAW 16 (a new rule ships its deterministic check), LAW 17 (the
regression suite is the consumer re-verification; C3 is a declared future consumer).
This ticket implements owner DECISION 13 — read it before changing anything.

## 1. Problem (verified 2026-07-20; full analysis in human_decision.md DECISION 13)

The featured-failure selector reads only the taught operation's OWN
`failure_modes_not_yet_shown`. Because each op spends its whole (introduction-arc)
failure pool at touch 1, every touch-2 RETURN finds it empty and the selector
emits `"none"` (extractor.md:388). `"none"` is overloaded — the contract reserves
it for non-teaching interludes (extractor.md:248) — so a teaching return carrying
it is an off-contract instruction that can make the Assembler under-populate the
gate (post-paid FAIL) or make a strict implementer STOP. **ch9 is the first hit;
it is a recurring class for every return.** (The return-master + newcomer-failers
shape itself is CORRECT and intended — do NOT "fix" it by relaxing the quota.)

## 2. Fix

**2.1 extractor.md — earned-pool fallback (replace the empty-list clause).**
In the `failure_mode_to_show` block (extractor.md:369-388), keep the primary rule
unchanged, then replace the line `"none" if operation_due is null or list is empty`
with two distinct cases:
- **operation_due is null** (anchor_interlude / arc_transition) → `"none"`.
- **operation_due non-null but the op's `failure_modes_not_yet_shown` is empty**
  (a teaching chapter on a returning/depleted op) → **FALL BACK to the earned
  pool**: the union across ALL operations in process_state of
  (`failure_modes_shown ∪ failure_modes_not_yet_shown`); from that set pick by the
  SAME key as the primary path — least-recently-LED (oldest entry in
  `failure_mode_lead_history`; a type that has never led ranks first), tiebreak
  least-recently-SHOWN. NEVER emit `"none"` for a teaching chapter.
Phrase the fallback unit-neutrally ("the least-recently-led ITEM from the earned
pool", item = failure type today) — see §5. Add a one-line pointer to DECISION 13.

**2.2 extractor.md — tighten the `"none"` contract.** Update extractor.md:248 so
`"none"` is documented as `operation_due is null` ONLY, and note the earned-pool
fallback is what a teaching chapter uses instead.

**2.3 structural_gate.py — deterministic guard (LAW 16).** In `run_gate()`, in the
teaching-chapter branch (`ctype in ("new_focal_character","return_to_character")`),
read the pointer's featured failure and require it is a real earned type:
```python
ptr = ms.get("next_chapter_pointer") or {}          # reuse T-024's binding if present
fms = ptr.get("failure_mode_to_show")
ps = json.loads((R / "state/process_state.json").read_text())
earned = set()
for opv in (ps.get("operations") or {}).values():
    earned |= set(opv.get("failure_modes_shown", []))
    earned |= set(opv.get("failure_modes_not_yet_shown", []))
if fms in (None, "none"):
    problems.append("teaching chapter has no featured failure (selector emitted 'none' — earned-pool fallback missing, ADV-3)")
elif earned and fms not in earned:
    problems.append(f"featured failure {fms!r} not in earned pool")
```
(If `earned` is empty — schema drift — skip the membership check but keep the
"none" check; never hard-fail on a missing pool.)

**2.4 field_registry.md — register.** Add case law: (a) the selector earned-pool
fallback + the retired `"none"`-on-teaching escape (DECISION 13); (b) the new gate
guard as a LAW 15 registered check with LAW 16 evidence.

**2.5 regression (tools/regression/run.py).** Add assertions:
- a teaching (return) pointer with `failure_mode_to_show == "none"` → gate FAIL
  naming the ADV-3 problem.
- a teaching pointer with a real earned type (e.g. "the hypothesis tester") →
  guard passes (chapter otherwise well-formed → PASS).
- an interlude pointer (`operation_due` null) with `"none"` → guard does NOT fire
  (still valid).
- a teaching pointer with a non-canonical featured type → FAIL "not in earned pool".

## 3. Acceptance (offline; author dry-ran each precondition)

1. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/structural_gate.py` on the
   live ch8 brief → still PASS (ch8's featured failure "the confident specialist"
   is in the earned pool); receipt written.
2. Each crafted input in §2.5 → gate exit 0/1 as specified; implementer records
   observed lines in §6 (LAW 15 evidence).
3. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` → exit 0,
   all PASS (old + new), tree clean after.
4. extractor.md review check (no offline exec possible — prompt): the fallback rule
   is present, unit-neutral, preserves LEAD-primary/SHOWN-tiebreak, and `"none"` is
   documented as operation_due-null only. Record the diff in §6.
5. Sanctioned pytest → `1 failed, 331 passed` (unchanged).
6. `git status --porcelain` → only the write-set; one commit; no paid call.
7. DOWNSTREAM RE-VERIFY: regression green (item 3); Assembler contract note
   (§Downstream) confirmed — a real featured type is consumed as before.

## 4. Commit

`feat(selector+gate): earned-pool fallback for featured failure; retire 'none' on teaching chapters (ADV-3, T-026)`

Trailers: `Ticket: T-026` / `Implemented-by: <Codex|Qwen>`.

## 5. Constraints

- Raspberry Pi; zero paid calls; stdlib only in gate code; no state/chapter writes
  (only prompts/.gate_pass.json as today).
- **LAW 14:** the earned-types set is derived from process_state pools at runtime —
  do NOT hardcode the 14 canonical failure names anywhere.
- **Do NOT invert the 2026-07-04 LED-not-SHOWN ruling** (extractor.md:376). The
  fallback uses the SAME key: LED primary, SHOWN tiebreak.
- **Do NOT relax the quota for returns.** The return-master + newcomer-failers
  shape is intended (DECISION 13). This ticket fixes the selector SOURCE only.
- **C3 unit-agnostic:** phrase the fallback + guard as selecting "the
  least-recently-led ITEM from the earned pool" — the item is a failure type today,
  but DECISION 12 C3 will swap it to a led beat. Do not bake "type" into names,
  comments, or structure such that C3 must rip it out.
- Serialize with T-024 (shared structural_gate.py + pointer reads). On ANY failure:
  stop at that step, revert, record in §6; do not improvise.

## 6. Implementer log (append below; never delete the ticket body)

- [ ] 2.1 extractor.md earned-pool fallback
- [ ] 2.2 extractor.md "none" contract tightened
- [ ] 2.3 structural_gate.py deterministic guard
- [ ] 2.4 field_registry registration
- [ ] 2.5 regression assertions
- [ ] acceptance 1–7
- [ ] commit
