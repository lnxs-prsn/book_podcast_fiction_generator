# TICKET T-004: F15 detection contract — unnamed entrants must reach the structural gate

```
Mode: alone
Timing: BETWEEN runs only (specs change between runs — LAW: agents/ edits
        never mid-chapter). Dispatch after chapter 006's transaction commits.
Worktree: main working tree, run everything from the repo root
Write-set: fiction_loop/agents/extractor.md,
           fiction_loop/agents/updater.md,
           fiction_loop/tools/INTEGRATION_SPECS.md (update_brief schema section,
           if other_entrants is documented there)
Hot-files: none
State-access: none — do NOT touch fiction_loop/state/, fiction_loop/prompts/,
              fiction_loop/core/living_document.md, or any .pipeline_spend.json.
              structural_gate.py is deliberately NOT in the write-set.
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first.

## 1. Problem (verified live on chapter 006, 2026-07-18 — a LAW 4 contract failure)

Three documents compose into a guaranteed false FAIL:

- The assembled prompt (correctly) instructs: "Name the newcomer only if they
  matter" — unnamed newcomers are the recommended default (permanent-record
  hygiene).
- `extractor.md` line ~144: "Empty list if no other solver is named" —
  unnamed solvers never enter `other_entrants`.
- `structural_gate.py` counts F15 newcomers ONLY from `focal_character.is_new`
  + `other_entrants[].is_new`. It reads the brief, never prose — by design.

Chapter 006's prose contains an explicit improvised newcomer ("a newcomer
Yejide had never seen before", unnamed, the information-gatherer solver); the
Extractor emitted `other_entrants: []`; the gate failed the chapter with "no
improvised newcomer (F15)". Every component obeyed its own spec. The
composition is the bug: the gate consumes a signal its producer never emits
for the recommended case. Owner accepted chapter 006 explicitly (LAW 13
ledger entry in the chapter log); this ticket prevents recurrence from ch7 on.

## 2. Fix (producer emits, consumer filters; the gate stays untouched)

1. `extractor.md` — SECTION other_entrants: replace the "Empty list if no
   other solver is named" rule. New contract: EVERY solver present in the
   gate scene gets an entry — named solvers as today; unnamed solvers as
   `{"name": null, "is_new": true/false, "approach_taken": ...}`. `is_new`
   for an unnamed solver = the prose presents them as first-appearance (no
   continuity marker to any prior chapter). Add one WRONG/RIGHT example pair
   (chapter 006's unnamed information-gatherer is the ready-made example).
2. `updater.md` — the D6 card rule (line ~45) and `characters_entered`
   (line ~103): both explicitly SKIP entries with `name: null`. Cards and
   the permanent record remain named-only (D6 unchanged); unnamed entrants
   exist in the brief solely so deterministic gates can count them.
3. `INTEGRATION_SPECS.md` — if the update_brief schema is documented there,
   mirror the new other_entrants contract (LAW 2: schema stated once,
   accurately).
4. Register the change per LAW 4: producer = Extractor, consumers =
   structural_gate.py (counts is_new) and Updater (filters name null). State
   this producer/consumer line explicitly in extractor.md where the section
   is defined.

`structural_gate.py` needs NO change — once unnamed entrants carry `is_new`,
its existing count sees them. Do not "improve" it.

## 3. Acceptance (ALL must pass)

1. Contract test with a synthetic brief (scratchpad copy — never edit
   `prompts/update_brief.json`): a brief whose only newcomer is
   `{"name": null, "is_new": true, "approach_taken": "the information gatherer"}`
   → temporarily point a COPY of structural_gate.py's brief path at the
   scratchpad file in a throwaway run (or monkeypatch via
   `python -c` with json rewrite in scratchpad) → exits 0. The same brief
   with `is_new: false` on all entries → exits 1 with the F15 line.
2. `grep -n "Empty list if no other solver is named" fiction_loop/agents/extractor.md`
   → zero hits; the new unnamed-entry contract present instead.
3. `grep -n "name: null\|name == null\|name is null" fiction_loop/agents/updater.md`
   → the skip rule present at both card creation and characters_entered.
4. `git status --porcelain` → changes ONLY within the write-set.

## 4. Commit

`fix(specs): other_entrants records unnamed solvers so the F15 gate can count them`

Trailers:
```
Ticket: T-004
Implemented-by: <Codex|Qwen — whoever implements>
```

Pathspec-limit to the write-set (never `git commit -a`).

## 5. Constraints

- Raspberry Pi; zero paid calls; specs and docs only — no Python edits.
- Never touch state/, prompts/, logs/, living_document.md, spend files, books/.
- On ANY failure: stop, record in §6 exactly as observed, leave the tree
  coherent.

## 6. Implementer log (append below; never delete the ticket body)

- 2026-07-18 — Codex — BLOCKED before implementation. The read-only
  discovery command failed with:
  `rg: fiction_loop/INTEGRATION_SPECS.md: No such file or directory (os error 2)`.
  Cause: the command used `fiction_loop/INTEGRATION_SPECS.md`; the ticket's
  declared write-set places the file at
  `fiction_loop/tools/INTEGRATION_SPECS.md`. Per §5 ("On ANY failure: stop"),
  no contract files were edited and no acceptance commands were run.
