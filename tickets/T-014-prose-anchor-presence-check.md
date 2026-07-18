# TICKET T-014: prose anchor-presence check — catch the missing anchor scene BEFORE the extractor spend

```
Mode: alone
Depends-on: T-012 SHOULD land first (this check emits the SAME deficiency
            record shape, §2.1 of T-012, so --revise can consume it).
            Not strictly blocking. Independent of T-013.
Timing: BETWEEN runs only. No chapter run in flight.
Worktree: main working tree, repo root
Write-set: (design (b), recommended) fiction_loop/agents/assembler.md,
           fiction_loop/tools/invoke_writer.py,
           fiction_loop/agents/orchestrator.md (step-8 error/ladder line),
           fiction_loop/core/field_registry.md
           — final write-set depends on the §2 design fork; CONFIRM the
           Assembler-contract question in §2 BEFORE editing, and if design
           (b) is not viable STOP and return BLOCKED (do not fall back to
           the brittle option without owner sign-off).
Hot-files: invoke_writer.py, orchestrator.md
State-access: READ-ONLY (assembled_prompt.md and/or a structured anchor
              field). No writes to state/ or chapters/.
Paid-calls: forbidden (pure deterministic check).
```

PRIORITY: OPTIONAL / DEFERRABLE. The structural gate (step 11.5) ALREADY
catches anchor-absent authoritatively — it reads `anchor_update.appeared`
from the brief and fails the chapter (this is what caught ch8 attempt 1).
This ticket does NOT close a correctness gap; it moves the catch EARLIER
(prose-time, before the paid Extractor call) and mechanizes the driver's
manual pre-gate grep, removing an improvisation surface (T-011 spirit). Ship
it when the cheaper wins (T-012/T-013) are in and the Assembler-contract
question below is resolved. It is safe to leave undone.

Read `fiction_loop/CONTRIBUTING.md` first — LAW 2 (single source), LAW 3
(determinism boundary), LAW 14 (chassis/pack: no book-specific literals in
code).

## 1. Problem (ch8 attempts 1 and 3)

Both anchor failures were caught only after the Extractor had already run
and encoded `anchor_update.appeared = false` into the brief — one wasted
paid Extractor call each time. On attempt 3 the driver caught it EARLIER by
hand-grepping the prose for the anchor's concluding line, before running the
Extractor. That manual grep is exactly the kind of undocumented, in-the-
driver's-head step T-011 exists to eliminate. Mechanize it.

The naive version is a trap: a coarse noun grep FALSE-PASSES. Attempt 3
contains the words "notebook" (Emmanuel's) and "page" (the chart's second
page) in unrelated contexts while the actual anchor torn-page scene is
absent. The only reliable prose signal is the SPECIFIC required anchor
content for THIS chapter — for ch8, the concluding line "The condition
itself provides the test. Solvers who skip the condition skip the gate."
(verified: present in attempt-2, ABSENT in attempt-3). That literal is
book/chapter-specific and MUST NOT be hardcoded (LAW 14).

## 2. Design fork — RESOLVE BEFORE CODING

The required anchor phrase for the current chapter lives, today, only in the
free prose of `prompts/assembled_prompt.md` (it appears there 3×, e.g. under
"Macro mystery evidence to plant:", double-quoted). Two options:

**(a) parse the assembled_prompt prose** for the quoted required phrase.
REJECTED as the primary design: it depends on the Assembler's free-text
section headers and quoting staying stable — an unwritten contract (LAW 2
violation waiting to happen; LAW 15 shadow machinery).

**(b) structured field (RECOMMENDED).** The Assembler already KNOWS the
required anchor prose (it writes it into the prompt). Have it ALSO emit a
machine-readable field — e.g. `anchor_required_prose: [ "<phrase>", ... ]`
— into a structured artifact the check reads (either a small
`prompts/anchor_requirement.json`, or a fenced machine block appended to
assembled_prompt.md). The check greps the draft for each required phrase
(normalized for whitespace/curly quotes) ONLY when the pointer says
`anchor_appears: true`. This is a clean producer→consumer contract (LAW 4)
with no prose parsing.

**BLOCK CONDITION:** if design (b) cannot be done cleanly (e.g. the
Assembler does not have the phrase as a discrete value and would have to
invent one), STOP and return BLOCKED with a note — that means the anchor
requirement itself is not yet a single-sourced value, which is a prior
defect for the owner/senior to ticket, not something to paper over with
brittle prose parsing.

## 3. Fix (assuming design (b))

**3.1 assembler.md** — spec the new `anchor_required_prose` output: when the
pointer's `anchor_appears` is true, the Assembler emits the required
anchor-scene literal(s) as a discrete machine-readable field alongside the
prompt. Register producer/consumer in field_registry (§3.4).

**3.2 invoke_writer.py** — add the anchor-presence check to the
`--check-prose` suite (T-012): read the required phrases; for each, if
absent from the draft (normalized match), emit a deficiency record
(`"check": "anchor_absent"`, the missing phrase, `"rule": "HARD RULE 8"`).
When `anchor_appears` is false, the check is a no-op. Reuse T-012's report
path and record shape so `--revise` sees it uniformly. NOTE: per T-012 §2's
scope boundary, an `anchor_absent` deficiency is a WHOLE-SCENE omission —
the ladder routes it to `redo generation`, NOT revision (adding a missing
scene is inventing, not surgical copying). The check's JOB is the early
cheap catch; the REPAIR is still redo.

**3.3 orchestrator.md** — the prose-check FAIL rung already exists (T-012);
add the anchor case to its routing note: `anchor_absent` → `redo
generation` directly (skip revision). One case-law line: ch8 attempts 1/3.

**3.4 field_registry.md** — register `anchor_required_prose` (producer:
Assembler; consumer: `invoke_writer.py --check-prose`) and, if used, the
`anchor_requirement.json` artifact.

**3.5 LAW 4 audit** as in T-012 §3.5; STOP-not-widen if a live contract
outside the write-set states the anchor-check boundary.

## 4. Acceptance (offline; fixtures on disk)

The current `prompts/assembled_prompt.md` (ch8's) names the required phrase
"The condition itself provides the test. Solvers who skip the condition skip
the gate." Use it to seed the design-(b) field for the fixture run.

1. `--check-prose` on the attempt-3 draft
   (`git show cf70a1b:fiction_loop/prompts/chapter_draft.md`) with
   `anchor_appears=true` and the required phrase present in the structured
   field → an `anchor_absent` deficiency, exit 1.
2. `--check-prose` on the attempt-2 draft
   (`git show d91e558:...`) with the same field → NO anchor deficiency
   (the phrase is present), exit governed only by the label check
   (which is why attempt-2 still fails on labels — proving the two checks
   are independent).
3. Coarse-grep guard: a unit asserting that a draft containing "notebook"
   and "page" but NOT the required phrase (i.e. attempt 3) is reported
   ABSENT — the check must not false-pass on incidental nouns.
4. `anchor_appears=false` → the anchor check emits nothing regardless of
   draft content (no-op path covered).
5. Test suite → `1 failed, 331 passed`. `git status --porcelain` → only the
   write-set; one commit. No paid calls.

## 5. Commit

`fix(tools+specs): prose anchor-presence check — early catch before the extractor spend (T-014)`

Trailers: `Ticket: T-014` / `Implemented-by: <Codex|Qwen>`.

## 6. Constraints

- Raspberry Pi; zero paid calls; no state/chapter writes.
- NO book-specific literal in code (LAW 14) — the phrase comes from the
  Assembler field at runtime, never from a constant.
- STOP-not-improvise if design (b) is not cleanly available (§2 block).

## 7. Implementer log (append below; never delete the ticket body)
