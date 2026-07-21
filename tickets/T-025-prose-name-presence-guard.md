# TICKET T-025: verify-from-source name-presence guard — every name the summary asserts must occur in the chapter prose

```
Mode: alone
Timing: BETWEEN runs only. High value BEFORE ch9 (a return — the highest-damage
        class for a mis-transcribed/lost name is a return, where a slipped name
        orphans or duplicates an existing character).
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/name_presence_check.py (NEW, standalone),
           fiction_loop/tools/regression/run.py (extend: assertions + fixtures ref),
           fiction_loop/core/field_registry.md (register the check),
           fiction_loop/CONTRIBUTING.md (ONE LAW 15 registration line)
Hot-files: none
Upstream (preconditions — author dry-ran EACH 2026-07-20, HEAD 9d0966c — chassis code identical to fe2e20d, intervening commit docs-only):
  - The Extractor is the ONLY stage that reads prose after the Writer; the
    Updater builds ~10 files from update_brief.json and is forbidden to re-read
    prose (updater.md CRITICAL RULES); the gate reads counts/booleans, never
    prose (structural_gate.py docstring). Verified — this is the "one-way door".
  - update_brief.json carries the name-bearing fields this guard reads:
    focal_character.name, other_entrants[].name (may be null),
    names_used_this_chapter (list). Verified against the live ch8 brief
    (names_used_this_chapter = ["Nantale Namakula","Dr. Akello","Moses"]).
  - **CORRECTION 2026-07-21 (implementer STOP — scope, not fixture):** the
    original draft also asserted `focal_character.city` ("Kampala") must appear in
    prose. It must NOT — a city is a setting attribute, not a name; a chapter need
    not speak its city (ch8 plays out indoors → `Kampala` occurs 0× in
    chapter_008.md, verified). That is a FALSE FAIL on a good chapter, which §5
    forbids. `city` is REMOVED from the asserted set; this guard is personal-names
    only (its stated invariant). City fidelity, if ever wanted, is the paid
    Stage-5 meaning inspector, not this free presence check.
  - The chapter prose is committed at fiction_loop/chapters/chapter_[NNN].md by
    step 9 before the Extractor runs at step 11. Verified (chapter_008.md exists).
  - structural_gate.py is the model for a standalone stdlib/zero-token
    orchestrator-invoked tool (exit 0 pass / 1 fail). Verified.
Downstream (consumers to re-verify): NONE — new LEAF machinery, like T-016 it
  BECOMES a check the Orchestrator runs; it regresses no existing consumer. The
  regression suite gains assertions over it (LAW 17). The Orchestrator gains one
  new step (~11.4, after Extractor, before/with the gate) — a RUN.md wiring note
  is out of this ticket's chassis write-set and is flagged for the senior.
State-access: READ-ONLY (reads the chapter file + update_brief.json). Writes
              nothing to state; may write a transient prompts/ report it cleans up.
Paid-calls: forbidden. This is the FREE deterministic slice of the (unbuilt,
            paid) Stage-5 Fidelity Inspector — text presence only, no meaning.
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 15 (registered machinery +
evidence it fires), LAW 16 (the guard ships with its own check). This is the
free depth of the "verify from the fresh source" direction; the paid meaning
re-read (Stage-5 proper) is explicitly NOT in scope.

## 1. Problem (verified 2026-07-20)

Once the Extractor writes a name into update_brief.json, nothing ever compares
it back to the story. A mis-transcribed name — the canonical example is a real
character: `char_008` is "Nantale Namakula"; a slip to "Nantare" — passes the
count-only gate and is fanned out by the Updater into ~10 files (character card,
population_index, event card, naming ledger, …) as canon, uncaught, because the
one stage that read the prose is behind us. The highest-damage class is a
wrong/lost name on a RETURN, where a slipped id/name duplicates or orphans an
existing character — and ch9 is a return (Wanjiku, char_004, name_due).

## 2. Fix

**2.1 New standalone tool `fiction_loop/tools/name_presence_check.py`** (stdlib
only, mirrors structural_gate.py's shape — `R = repo/fiction_loop`, exit 0/1):
- Read `prompts/update_brief.json`; read
  `chapters/chapter_[brief.chapter].md` (zero-pad from `brief["chapter"]`).
- Collect ASSERTED strings from the brief (PERSONAL NAMES only — NOT `city`; see
  the CORRECTION precondition):
  - `focal_character.name` (skip if focal is null — anchor_interlude/arc_transition),
  - every `other_entrants[].name` that is non-null,
  - every entry in `names_used_this_chapter`.
- For each asserted personal name, require that it OCCURS in the chapter text.
  Match rule (deterministic, forgiving of prose formatting):
  - case-insensitive; and for a multi-token name, PASS if the full string
    occurs OR every token occurs somewhere in the prose (handles "Dr. Akello"
    referred to later as "Akello", or "Nantale Namakula" then "Nantale"). A
    single-token name must occur as a whole word.
- Any asserted name with NO prose support → collect as a problem.
- Print one line per missing name (`MISSING FROM PROSE: "<name>" (field)`),
  print a PASS/FAIL summary, exit 1 if any missing else 0. Never read
  mystery_anchor.json / hidden_coherence. Clean any transient file written.

**2.2 Regression (tools/regression/run.py):** add assertions using the frozen
fixtures:
- the committed ch8 brief + chapters/chapter_008.md → exit 0 (personal names
  Nantale Namakula, Dr. Akello, Moses all present — verified 13/9/4 occurrences;
  `city` is NOT checked).
- a copy of the ch8 brief with `focal_character.name` mutated to "Nantare
  Namakula" → exit 1 naming the missing name (the Nantale case). Use an
  in-runner temp copy; do not mutate the committed brief.

**2.3 Register** in field_registry.md (producer: this tool reads
update_brief.json name fields + the chapter prose; consumer: Orchestrator
step 11.4 error handling) and ONE LAW 15 line in CONTRIBUTING naming the guard,
the invariant it protects (no name enters state that is absent from the story),
and its evidence-it-fires (the Nantare mutation goes red).

## 3. Acceptance (offline; author dry-ran each precondition)

1. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/name_presence_check.py`
   against the live ch8 brief + chapter_008.md → exit 0, all PERSONAL names
   present (city not checked — see the CORRECTION precondition).
2. Red proof: run it against a temp brief with "Nantale"→"Nantare" → exit 1,
   line `MISSING FROM PROSE: "Nantare Namakula" (focal_character.name)`.
   Record the observed red in §6 (LAW 15 evidence-it-fires).
3. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` →
   exit 0, all PASS (incl. the two new assertions), tree clean after.
4. Sanctioned pytest → `1 failed, 331 passed` (unchanged).
5. `git status --porcelain` → only the write-set; one commit; no paid call.
6. DOWNSTREAM RE-VERIFY: none (leaf); regression green (item 3).

## 4. Commit

`feat(tools): prose name-presence guard — no summary name enters state absent from the story (T-025)`

Trailers: `Ticket: T-025` / `Implemented-by: <implementer>`.

## 5. Constraints

- Raspberry Pi; zero paid calls; stdlib only; READ-ONLY on state and chapters.
- Text presence ONLY — do not attempt meaning/consistency (that is the paid
  Stage-5 inspector, deliberately out of scope). A false PASS on meaning is
  acceptable here; a false FAIL on a real name that is present is NOT — keep the
  token-match rule forgiving of prose formatting.
- Do NOT wire the Orchestrator step in this ticket (RUN.md is outside the
  chassis write-set); flag it for the senior in §6.
- On ANY failure: stop, revert, record in §6; do not improvise.

## 6. Implementer log (append below; never delete the ticket body)

- [ ] 2.1 name_presence_check.py
- [ ] 2.2 regression assertions (present + Nantare-red)
- [ ] 2.3 field_registry + LAW 15 registration
- [ ] acceptance 1–6
- [ ] commit
- [ ] NOTE for senior: RUN.md step-11.4 wiring (out of chassis write-set)

- **STOPPED 2026-07-21:** acceptance item 1 / precondition is false on HEAD.
  The live ch8 brief asserts `focal_character.city = "Kampala"`, but
  `chapters/chapter_008.md` contains no case-insensitive `Kampala` substring.
  Observed live check output:
  `MISSING FROM PROSE: "Kampala" (focal_character.city)` and exit 1; regression
  consequently reported 22/23 assertions passed. Reverted all implementation
  changes per §5; did not weaken the city rule or edit the committed artifact.

- **Senior resolution (2026-07-21): correct STOP — the bug was ticket SCOPE, not
  your work.** `focal_character.city` should never have been an asserted string:
  this guard's invariant is personal-name presence, and a city is a setting
  attribute a chapter need not speak (senior verified ch8 prose: Nantale 13×,
  Akello 9×, Moses 4×, Kampala 0×). Requiring the city verbatim is exactly the
  false-FAIL §5 forbids. Fixed in place — `city` REMOVED from §2.1 scope, the
  city match-rule bullet deleted, §2.2/§3 no longer expect "Kampala", CORRECTION
  precondition added. The Nantale→Nantare red proof is unaffected. **Cleared to
  resume from the top; nothing you did needs reverting beyond what you already
  reverted.** RUN.md step-11.4 wiring note (§6 last box) still stands for the senior.

- **IMPLEMENTED 2026-07-21:** 2.1–2.3 complete. Live ch8 proof observed
  `NAME PRESENCE CHECK: PASS`; isolated `Nantare Namakula` mutation observed exit
  1 with `MISSING FROM PROSE: "Nantare Namakula" (focal_character.name)`.
  Tool regression: 23/23 PASS. Sanctioned pytest: expected baseline unchanged at
  1 failed, 331 passed (`test_default_splitter_engine_passes_openrouter_timeout_seconds`).
  Downstream: none (leaf); no paid calls. **Senior follow-up remains:** wire the
  Orchestrator RUN.md step 11.4 outside this ticket's chassis write-set.
