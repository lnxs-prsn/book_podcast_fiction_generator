# TICKET T-020: retire the anchor-description leak — move the fixed observable presentation into mystery_anchor.json (pack data); Assembler reads it

```
Mode: alone
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/agents/assembler.md (remove hardcode; read from pack),
           fiction_loop/state/mystery_anchor.json (add observable_presentation),
           fiction_loop/core/field_registry.md (register the field),
           fiction_loop/tools/regression/run.py (extend: assertion)
Hot-files: none
Upstream (preconditions — author dry-ran EACH 2026-07-20, HEAD d7e1f99 — chassis code identical to fe2e20d/starting_factory, intervening commits docs/tickets only):
  - The description is hardcoded verbatim at assembler.md:229 and that is the
    ONLY agent-prompt leak (verified: `grep -rn "grey coat" fiction_loop/` →
    assembler.md:229 is the sole agent-prompt hit; chapter prose, living_document,
    and assembled_prompt.md are legitimate renderings/derivations, not the leak).
  - mystery_anchor.json has keys {observable_log, reader_can_suspect,
    hidden_coherence}; the description belongs in the OBSERVABLE region, away from
    hidden_coherence (DECISION 11 B4). Verified.
  - mystery_anchor.json is AUTHORED content, NOT seeded by init_state.py (verified:
    `grep "mystery_anchor" fiction_loop/tools/init_state.py` → none) → adding an
    authored field is initialization, not a producer-state mutation.
  - The value is FIXED CANON since ch1: "an unremarkable man in a grey coat,
    carrying a small black notebook. Never described in more detail, never named,
    never aged."
  - Sanctioned pytest baseline: `1 failed, 331 passed` (documented pre-existing).
Downstream (consumers to re-verify):
  - The Assembler anchor section (assembler.md:227-229) is the sole consumer — it
    copies the line verbatim into the brief. After the fix it reads the value from
    mystery_anchor.json.observable_presentation instead. No structural_gate /
    Extractor / Updater consumer (grep confirms the value is copied, not parsed).
  - field_registry.md gains a producer/consumer row. Regression asserts the
    hardcode is gone + the field present.
State-access: writes mystery_anchor.json (adds ONE authored field; between runs
              only — NOT a producer-managed counter; do not touch observable_log /
              reader_can_suspect / hidden_coherence).
Paid-calls: forbidden. NOTE: the assembler.md change is a PROMPT edit — validated by
            review + regression, not by an offline run.
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 14 (book-specific content lives in
the pack, never in an agent prompt). This ticket implements owner DECISION 11 B4
(which explicitly authorized the senior to draft it once safe placement was
verified — placement verified 2026-07-20).

## 1. Problem (verified 2026-07-20)

The anchor's observable presentation ("an unremarkable man in a grey coat, carrying
a small black notebook…") is hardcoded in `assembler.md:229` — book-specific content
baked into a multi-book chassis (the QUOTA_BY_ARC LAW-14 leak class). Verified
SINGULAR: only the agent prompt leaks it.

## 2. Fix

**2.1 mystery_anchor.json — add the authored field.** Add a top-level
`"observable_presentation"` in the reader-observable region (sibling to
`observable_log` / `reader_can_suspect`; NOT under `hidden_coherence`), value =
the canon line verbatim:
`"an unremarkable man in a grey coat, carrying a small black notebook. Never described in more detail, never named, never aged."`

**2.2 assembler.md — read from the pack.** Replace the hardcoded line at
assembler.md:229 with an instruction to read `observable_presentation` from
mystery_anchor.json and copy it into the brief verbatim (same "FIXED CANON, copy
verbatim" semantics — now sourced from pack data, not the prompt). The
never-named/never-aged constraint travels with the field value.

**2.3 field_registry.md — register.** Add a row: producer = authored pack content
(`mystery_anchor.json.observable_presentation`); consumer = Assembler anchor
section. One-line B4 case law.

**2.4 regression (tools/regression/run.py).** Assert:
- `fiction_loop/agents/assembler.md` contains no "grey coat" / hardcoded
  description string → the leak is gone.
- `mystery_anchor.json.observable_presentation` is present and non-empty.

## 3. Acceptance (offline; author dry-ran each precondition)

1. `grep -n "grey coat\|black notebook" fiction_loop/agents/assembler.md` → no hits.
2. `observable_presentation` present in mystery_anchor.json, equals the canon line,
   and is NOT inside `hidden_coherence`.
3. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py` → exit 0,
   all PASS (old + new).
4. Sanctioned pytest → `1 failed, 331 passed` (unchanged).
5. `git status --porcelain` → only the write-set; one commit; no paid call.
6. DOWNSTREAM RE-VERIFY: Assembler anchor section now reads the pack value (review —
   prompt); field_registry row present.

## 4. Commit

`feat(anchor): move fixed observable presentation to mystery_anchor.json pack data; assembler reads it (T-020, DECISION 11 B4)`

Trailers: `Ticket: T-020` / `Implemented-by: <implementer>`.

## 5. Constraints

- Raspberry Pi; zero paid calls.
- **LAW 14:** no book-specific content in agent prompts.
- Place the field in the OBSERVABLE region — never under/near `hidden_coherence`
  (agents are walled from it; leaking the description there would couple it to the
  secret).
- Between-runs only; the added field is authored canon, not a producer counter — do
  not touch `observable_log` / `reader_can_suspect` / `hidden_coherence`.
- On ANY failure: stop at that step, revert, record in §6; do not improvise.

## 6. Implementer log (append below; never delete the ticket body)

- [ ] 2.1 mystery_anchor.json observable_presentation
- [ ] 2.2 assembler.md reads from pack
- [ ] 2.3 field_registry registration
- [ ] 2.4 regression assertion
- [ ] acceptance 1–6
- [ ] commit
