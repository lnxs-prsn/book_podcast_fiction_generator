# TICKET T-019: retire the QUOTA_BY_ARC chassis/pack leak — the gate READS the per-arc quota from a pack-owned manifest, never a hardcoded copy

```
Mode: alone
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/structural_gate.py,
           fiction_loop/tools/init_state.py (emit the manifest),
           fiction_loop/state/arc_quota.json (NEW pack manifest — created here
             for the live instance, deterministically from the curriculum),
           fiction_loop/tools/regression/run.py (repoint the freeze assertion),
           fiction_loop/core/field_registry.md (update the arc-cast-quota row)
Hot-files: none
Upstream (preconditions — author dry-ran EACH 2026-07-20, HEAD 9d0966c — chassis code identical to fe2e20d, intervening commit docs-only):
  - `QUOTA_BY_ARC = {1:3, 2:2, 3:2, 4:2}` is hardcoded at
    structural_gate.py:24 and consumed at :70 (`quota = QUOTA_BY_ARC.get(arc,1)`)
    — verified by grep.
  - field_registry.md:15 names the SOLE count owner: concept_curriculum.md §9
    **Section 4** (arc 1 → 3, arcs 2–8 → 2), and lists the three copies that
    must change together (assembler BEAT QUOTA table, assembler HARD RULE 7,
    structural_gate.py QUOTA_BY_ARC). DECISION 10 corrected the VALUE; the leak
    (a copy living in chassis code) remains. Verified.
  - tools/regression/run.py carries a `QUOTA_BY_ARC` freeze assertion (added at
    6d15c30, DECISION 10). Verified it must be repointed, not deleted.
  - init_state.py generates per-instance state from the curriculum — verified it
    is the correct producer for a pack-derived manifest (Stage-4 down payment).
  - Sanctioned pytest baseline: `1 failed, 331 passed`.
Downstream (consumers to re-verify — field_registry.md:15):
  - structural_gate.py (this ticket repoints it to the manifest).
  - tools/regression/run.py freeze assertion → repoint to arc_quota.json.
  - assembler.md BEAT QUOTA table + HARD RULE 7 STILL hold hardcoded copies
    AFTER this ticket — they are the Assembler's guidance to the Writer, NOT the
    enforcement (the GATE is). This ticket does NOT touch them (assembler is an
    agent reading markdown; migrating it is a separate ticket). Flag them as
    remaining-leak in field_registry so the next sweep finishes the job.
State-access: reads state/master_state.json (arc_current) + the new
              state/arc_quota.json; writes state/arc_quota.json ONCE (creation,
              deterministic from curriculum) + prompts/.gate_pass.json as today.
Paid-calls: forbidden. Stdlib only.
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 14 (this IS the chassis/pack
leak the law is insurance against; DECISION 10 was its live proof), LAW 15/16
(the freeze assertion is the machinery that keeps the count from re-drifting),
LAW 17 (re-verify the regression consumer).

## 1. Problem (verified 2026-07-20)

The per-arc wrong-approach quota is pedagogy — it belongs to the pack
(curriculum §9 Section 4), which owns the count. But the enforcement gate keeps
its own hardcoded copy, `QUOTA_BY_ARC` (structural_gate.py:24). On the first
arc-2 chapter (ch8) that copy disagreed with the curriculum and false-failed a
correct draft, blocking the run (DECISION 10). The value was fixed; the leak —
chassis code owning a pack quantity — remains, so a different book run through
this same chassis would inherit *Sankofa's* arc quotas. LAW 14 says: find the
chassis/pack leak. This retires the demonstrated-costly one: the gate must READ
the count from a pack-owned source, not own a copy.

## 2. Fix

**2.1 Introduce a pack-owned manifest `fiction_loop/state/arc_quota.json`** —
the first slice of the Stage-4 pack manifest the factory will generate per book:
```json
{ "by_arc": { "1": 3, "2": 2, "3": 2, "4": 2 }, "default": 1 }
```
Values are the curriculum §9 Section 4 table (arc 1 → 3, arcs 2+ → 2, arc 5+ →
1). Create it in this ticket for the live instance — this is a deterministic
transcription of the count OWNER (Section 4), not hand-authored policy.

**2.2 init_state.py emits it (producer, LAW 14 correct home):** when generating
state, derive `arc_quota.json` from the curriculum §9 Section 4 table so a new
book's instance gets ITS quotas, never Sankofa's. (If a full parse of §9 is out
of scope for this ticket, at minimum init_state must WRITE arc_quota.json with
the Section-4-derived map and a comment pointing at the owner — never leave the
gate to a hardcoded fallback.)

**2.3 structural_gate.py reads the manifest:** replace the module-level
`QUOTA_BY_ARC` dict with a load from `state/arc_quota.json`:
```python
def load_arc_quota():
    data = json.loads((R / "state/arc_quota.json").read_text())
    by_arc = {int(k): v for k, v in data.get("by_arc", {}).items()}
    return by_arc, data.get("default", 1)
```
In `run_gate()`: `by_arc, default = load_arc_quota(); quota = by_arc.get(arc, default)`.
If the manifest is missing/unreadable → gate ERROR (exit 1) with a clear
message; do NOT silently fall back to a hardcoded map (a silent fallback would
re-introduce the leak).

**2.4 Repoint the regression freeze assertion (tools/regression/run.py):** the
existing `QUOTA_BY_ARC` freeze now asserts arc_quota.json's `by_arc` equals the
frozen {1:3,2:2,3:2,4:2} + default 1, AND that structural_gate.py no longer
defines a `QUOTA_BY_ARC` literal (grep-style assertion: the string is gone from
the tool). This keeps the "count can't silently drift" invariant on the NEW
source and proves the leak stays closed.

**2.5 field_registry.md:15** — update the arc-cast-quota row: source of truth
unchanged (Section 4); the gate copy is now `state/arc_quota.json` (read, not
owned); assembler BEAT QUOTA table + HARD RULE 7 flagged as the two REMAINING
hardcoded copies (a follow-on ticket migrates them). Add DECISION-10-closes case
law: "gate leak retired (T-019) → arc_quota.json; assembler copies pending."

## 3. Acceptance (offline; author dry-ran each precondition)

1. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/structural_gate.py` on
   the live ch8 brief → PASS (arc 2, quota 2) — identical verdict to today, now
   sourced from arc_quota.json (implementer confirms by temporarily setting
   arc_quota.json arc "2" to 3 → the same brief FAILs "1... of 3"; restore).
   Record both in §6.
2. Manifest-missing proof: rename arc_quota.json → gate exits 1 with the clear
   error (no silent fallback); restore.
3. `grep -n QUOTA_BY_ARC fiction_loop/tools/structural_gate.py` → no literal
   dict remains (only, at most, a comment/ref).
4. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` →
   exit 0, all PASS incl. the repointed freeze; tree clean after.
5. Sanctioned pytest → `1 failed, 331 passed` (unchanged).
6. `git status --porcelain` → only the write-set; one commit; no paid call.
7. DOWNSTREAM RE-VERIFY: regression green (item 4); assembler copies flagged in
   field_registry (item 2.5), not silently left undocumented.

## 4. Commit

`refactor(gate): read per-arc quota from pack manifest state/arc_quota.json — retire QUOTA_BY_ARC leak (LAW 14, T-019)`

Trailers: `Ticket: T-019` / `Implemented-by: <Codex|Qwen>`.

## 5. Constraints

- Raspberry Pi; zero paid calls; stdlib only.
- The manifest values are a transcription of curriculum §9 Section 4 — if they
  disagree with Section 4 at author time, STOP (that is a fresh curriculum
  contradiction, not this ticket's call).
- Do NOT migrate the assembler copies here (separate ticket) — only DOCUMENT
  them as remaining. Do NOT add a silent hardcoded fallback in the gate.
- On ANY failure: stop, revert, record in §6; do not improvise.

## 6. Implementer log (append below; never delete the ticket body)

- [ ] 2.1 arc_quota.json created (from Section 4)
- [ ] 2.2 init_state.py emits it
- [ ] 2.3 gate reads it (no hardcoded fallback)
- [ ] 2.4 regression freeze repointed + leak-gone assertion
- [ ] 2.5 field_registry updated (assembler copies flagged)
- [ ] acceptance 1–7
- [ ] commit
