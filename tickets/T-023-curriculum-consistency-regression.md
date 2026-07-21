# TICKET T-023: freeze the DECISION 10 within-curriculum duplication — §9's reader-progression table defers to Section 4 for the wrong-approach count and never restates the numerals; a regression proves it

```
Mode: alone
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/core/concept_curriculum.md (§9 READER EXPERTISE
             PROGRESSION only — remove the attributed count numerals, keep the
             deferral-to-Section-4 wording),
           fiction_loop/tools/regression/run.py (add the guard assertion),
           fiction_loop/core/field_registry.md (note the §9 de-dup + guard on the
             arc-cast-quota row)
Hot-files: none
Upstream (preconditions — author dry-ran EACH 2026-07-21, HEAD 2abd2a9 — chassis code identical to fe2e20d, intervening commits docs-only):
  - DECISION 10 made §9's reader-progression table "defer" to Section 4 on the
    per-arc wrong-approach COUNT, but left ATTRIBUTED numeral copies in place:
      · concept_curriculum.md:196 (the deferral note) restates "(arc 1 → three,
        arcs 2–8 → two)";
      · :200 restates "(Section 4: arc 1 → three, arc 2 → two)";
      · :201 "Both wrong approaches the arc defines shown fully" (count-bearing).
    Verified by read. These AGREE with Section 4 today — the exact dormant-but-
    consistent precondition DECISION 10 fired from (a copy that matches now and
    can silently diverge on a future edit).
  - Section 4 is the SOLE count owner (field_registry.md:15; concept_curriculum.md:196
    "owned by Section 4 above"). Section 4 sits ABOVE line 192, i.e. OUTSIDE the
    "## 9. READER EXPERTISE PROGRESSION" section — so a guard scoped to that
    section cannot touch the owner. Verified.
  - tools/regression/run.py is the guard home; baseline 12/12 PASS (handoff §3).
    Verified the new assertion STACKS (does not replace an existing one).
  - This is distinct from T-019: T-019 retires the CHASSIS copy (gate's
    QUOTA_BY_ARC → arc_quota.json); T-023 retires the WITHIN-CURRICULUM copies
    (rule 5, one owning table). No hard dependency; both edit run.py, so if both
    are in flight, rebase the later one. Verified non-overlapping edits otherwise.
  - Sanctioned pytest baseline: `1 failed, 331 passed`.
Downstream (consumers to re-verify — field_registry.md:15):
  - No runtime consumer reads these numerals (they are prose guidance to the
    Assembler agent). Removing the numerals while keeping "per Section 4" changes
    no enforced behavior — the GATE reads the count elsewhere. Verified.
State-access: none. Reads two core/ docs; writes run.py + two core/ docs. No
              state/ mutation, no prompts/ artifacts.
Paid-calls: forbidden. Stdlib only.
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 2 (single source; this is rule 5,
"one quantity, one owning table", applied WITHIN the pack), LAW 3 (the guard is
the deterministic half), LAW 17 (re-verify the regression consumer). This ticket
is the first concrete instance of `human_decision.md` DECISION 15's
**eliminate → guard** ladder; read D15 before starting.

## 1. Problem (verified 2026-07-21)

DECISION 10's root was a quantity stated in two of the curriculum's own tables
(Section 4 = 2; the reader-progression table = "three minimum") that agreed
through all of arc 1 and diverged on the first arc-2 chapter, false-failing a
correct draft. The fix corrected the VALUE and added a "this table defers" note —
but the reader-progression table (§9) STILL restates the count as attributed
numerals (`concept_curriculum.md:196/200/201`). Attributed copies are lower-risk
than DECISION 10's unattributed one, but they are still copies: edit Section 4's
count without editing these and they silently diverge again. Rule 5 says the
count lives in exactly ONE table; every other table DEFERS, it does not restate.
Per DECISION 15 the copy is eliminable (the table can say "per Section 4" with no
numeral), so we ELIMINATE then GUARD — not guard a copy we could have removed.

## 2. Fix

**2.1 Eliminate the numeral copies in §9 (concept_curriculum.md, READER
EXPERTISE PROGRESSION section only).** Replace each attributed count restatement
with a pure deferral that carries NO per-arc numeral:
  - :196 deferral note → keep "the COUNT of wrong-approach types per arc is owned
    by Section 4 above — this table never restates or overrides it." (drop the
    parenthetical "(arc 1 → three, arcs 2–8 → two)").
  - :200 → "every wrong approach the arc defines (per Section 4), each fully
    dramatized." (drop "arc 1 → three, arc 2 → two").
  - :201 → phrase without a count numeral, e.g. "The wrong approaches the arc
    defines (per Section 4) are shown fully; the second may be shortened as
    recognition grows."
  Meaning is preserved exactly — the reader-progression table keeps governing
  dramatization intensity; only the duplicated numerals leave.
  **STOP condition:** if any restatement's number DISAGREES with Section 4 at
  author time, STOP and surface it — that is a fresh live contradiction, not this
  ticket's call (mirrors T-019). (Author confirmed AGREEMENT at HEAD; a disagreement
  would mean the source drifted since.)

**2.2 Add the guard (tools/regression/run.py).** New assertion:
  - Read `fiction_loop/core/concept_curriculum.md`.
  - Slice the "## 9. READER EXPERTISE PROGRESSION" section (from that heading to
    the next `## ` heading or EOF).
  - Assert the slice contains NO per-arc count restatement — regex on the
    restatement SHAPE, e.g. `re.search(r"arc\s*\d\s*[→-]+\s*(one|two|three|\d)",
    slice, re.I)` is None, and the bare count-words tied to the pattern are gone.
    "per Section 4" (no numeral) passes; "arc 2 → two" fails.
  - Message on failure: name the offending line so a maintainer sees the
    re-introduced copy immediately.
  Keep it a scoped, single-source-aware assertion (NOT a general "any number
  duplicated anywhere" scan — that path was ruled out; DECISION 15 / audit).

**2.3 field_registry.md:15** — extend the arc-cast-quota row: record that §9's
reader-progression table now defers to Section 4 with NO numeral (rule 5 within
the pack), frozen by the T-023 assertion in run.py. Add case-law line:
"within-curriculum duplication (DECISION 10 root) retired + frozen (T-023)."

## 3. Acceptance (offline; author dry-ran each precondition)

1. After 2.1: `grep -nEi "arc *[0-9] *[→-]+ *(one|two|three|[0-9])"` over the §9
   READER EXPERTISE PROGRESSION section → no match; the deferral wording still
   names Section 4 as owner (meaning preserved).
2. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` → exit 0,
   all PASS including the new assertion; tree clean after.
3. Guard-bites proof: temporarily re-insert "arc 2 → two" into the reader-
   progression table → run.py FAILs on the new assertion naming that line;
   restore. Record both verdicts in §6.
4. Section-4 untouched: `git diff` shows changes ONLY within the §9 READER
   EXPERTISE PROGRESSION section of concept_curriculum.md (the count owner keeps
   its numerals).
5. Sanctioned pytest → `1 failed, 331 passed` (unchanged).
6. `git status --porcelain` → only the write-set; one commit; no paid call.
7. DOWNSTREAM RE-VERIFY: regression green (item 2); no runtime consumer reads the
   removed numerals (they were agent prose guidance); field_registry updated (2.3).

## 4. Commit

`test(curriculum): freeze §9 count-deferral to Section 4 — retire the DECISION 10 within-pack duplication (rule 5, LAW 2, T-023)`

Trailers: `Ticket: T-023` / `Implemented-by: <implementer>`.

## 5. Constraints

- Raspberry Pi; zero paid calls; stdlib only.
- Edit ONLY the §9 READER EXPERTISE PROGRESSION section of concept_curriculum.md.
  Do NOT touch Section 4 (the owner) or any other section.
- Meaning-preserving de-duplication ONLY — do not change what the reader-
  progression table teaches about dramatization intensity.
- The guard is a SCOPED single-source assertion, not a general duplicate-number
  scanner (ruled out: DECISION 15 / the registry audit).
- On ANY failure or an author-time Section-4 disagreement: stop, revert, record
  in §6; do not improvise.

## 6. Implementer log (append below; never delete the ticket body)

- [ ] 2.1 §9 numerals eliminated (deferral wording kept; Section-4 agreement confirmed)
- [ ] 2.2 guard assertion added to run.py (scoped regex)
- [ ] 2.3 field_registry updated
- [ ] acceptance 1–7 (incl. guard-bites proof)
- [ ] commit
