# TICKET T-008: gate-before-refresh reorder — the LAW 7 standing violation, fixed whole

```
Mode: alone
Depends-on: T-007 MERGED FIRST (shared write-set: orchestrator.md, RUN.md,
            structural_gate.py; serialize).
Timing: BETWEEN runs only — no chapter run in flight. First live validation
        rides the next chapter run (paid, owner starts) — see §4.7.
Worktree: main working tree, repo root
Write-set: fiction_loop/agents/orchestrator.md,
           fiction_loop/RUN.md,
           fiction_loop/agents/extractor.md,
           fiction_loop/tools/structural_gate.py (docstring/text only),
           fiction_loop/CONTRIBUTING.md (LAW 7 standing-violation note only),
           fiction_loop/core/field_registry.md,
           fiction_loop/specs/intake_factory.spec.md (auto-redo precondition
           note only)
Hot-files: orchestrator.md, extractor.md (heavily edited this month:
           T-004/005/006/007)
State-access: none — no state/, prompts/, chapters/, core/living_document.md,
              spend files. This is a pure contract/order change.
Paid-calls: forbidden. The reorder's live proof is the NEXT owner-started
            chapter run, not this ticket.
```

Read `fiction_loop/CONTRIBUTING.md` first — especially LAW 7's text about
this exact fix: "The mapped fix is a 6-consumer reorder; **do not
'quick-fix' it partially**." This ticket IS that fix, whole.

## 1. Problem

Pipeline order today: 8 Writer → 9 copy → **10 living-doc refresh (PAID)** →
11 Extractor → 11.5 structural gate → 12 Updater. Every gate rejection
therefore (a) wastes one paid refresh call and (b) pollutes
`core/living_document.md` with canon from a draft that will never exist.
Documented as the LAW 7 standing violation; fired live on 2026-07-18
(chapter 008 attempt 1, anchor-absent rejection; recovery via T-007's
restore rung).

**Why the order exists (the one real coupling):** the gate consumes
`update_brief.json`, so the Extractor must run before the gate — and
extractor.md declares it runs "after refresh_living_doc.py" because exactly
ONE of its output fields, `reader_can_suspect_update`, is computed by
diffing the REFRESHED living doc's "MYSTERY PERSON THREAD" line against
`mystery_anchor.json.reader_can_suspect`. One field forces the paid call in
front of the gate. Sever that, and the refresh moves behind the gate freely.

## 2. Design decision (single outcome, LAW 2/3)

`reader_can_suspect_update` changes source: the Extractor derives it from
the CHAPTER PROSE it already reads, diffed against
`mystery_anchor.json.reader_can_suspect` (which it also already reads).
The living-doc hop is deleted from the Extractor entirely.

Why this beats the alternatives considered: (a) it removes a second LLM's
paraphrase from the provenance of a state field (the extractor currently
records the refresh model's wording, not the prose's); (b) it shrinks the
Extractor's input list — LAW 10 context budget; (c) extractor.md:21 shows
the living doc was read for this ONE section only, so nothing else is lost.
Alternatives rejected: deferring the field to a post-refresh second
extractor pass (new step, new failure surface); having the Updater read the
living doc at step 12 (moves an extraction judgment into the wrong agent).

**Step numbers are KEPT, position moves** (precedent: M-15 first-use rule —
never renumber). New order: 8 → 9 → 11 → 11.5 → **10** → 12. Log filename
`10_living_doc_refresh.log` and all step-10 references stay valid.

## 3. Fix

**3.1 orchestrator.md — move the step-10 block** (the background
refresh + poll + Exit-1 handling, verbatim) from its current position to
AFTER step 11.5's "Exit 0 → proceed", BEFORE step 12. Adjust the two
adjacent transition lines ("Exit 0 → proceed to step 12" becomes "Exit 0 →
proceed to step 10 (refresh), then step 12"). Step 11.5's Exit-1 text: now
truthfully states NO paid refresh has run and NOTHING was mutated — align
its wording (and drop the T-007 "…but living_document.md HAS been" clause,
which becomes false). Add one historical line at the moved block:
"Moved behind the gate 2026-07 (T-008); before that, every rejection cost
one refresh call and polluted the living doc (LAW 7 case law)."

**3.2 extractor.md:**
- Line 5 "Called by": now "Orchestrator (step 11), after the chapter has
  been saved to fiction_loop/chapters/" — delete the refresh clause.
- Input list (~line 21): DELETE the living_document.md line.
- SECTION reader_can_suspect_update (~line 330): new contract — "Compare
  what THIS chapter's prose lets an attentive reader newly suspect about
  the anchor against mystery_anchor.json's current reader_can_suspect
  array. If the prose supports a suspicion not already recorded: one
  sentence capturing it, written observationally. If nothing new: 'none'."
  Add the T-008 provenance note (field now derives from prose, not the
  refresh model's paraphrase).
- orchestrator.md step-11 spawn prompt: remove living_document.md from the
  Read list (it mirrors the spec's input list — LAW 2 copy).

**3.3 RUN.md:48** — step list order text updated to match (refresh
described after the gate).

**3.4 structural_gate.py** — docstring only: "redo costs only steps 7-11"
stays true and gets stronger; amend to note state AND living doc are
untouched at FAIL time. The T-007 hint line (restore command) is now
unreachable-by-construction: DELETE it (LAW 15 — machinery that cannot
fire buys false confidence). The T-007 rung condition in orchestrator.md
stays (it self-neutralizes and covers any future regression).

**3.5 CONTRIBUTING.md LAW 7** — rewrite the standing-violation parenthetical
as resolved case law: keep the incident (what the violation was, that it
fired live on ch8), state it was fixed by T-008's reorder, and that the
gate now runs before every paid post-writer call. Do not delete the case
law — laws keep their scars.

**3.6 field_registry.md** — update the living_document.md consumer row(s):
the Extractor is REMOVED as a consumer; `reader_can_suspect_update`'s
producer note now cites chapter prose + mystery_anchor.json as sources.
Case-law note: T-008.

**3.7 intake_factory.spec.md:215** — the auto-redo precondition
("REQUIRES the gate-before-refresh reorder first") is now satisfied; amend
to "(satisfied by T-008, 2026-07)" — one line, nothing else in that spec.

**3.8 LAW 4 audit, same sitting:** grep `refresh_living_doc\|living_doc\|
step 10` across `fiction_loop/agents/ fiction_loop/core/ fiction_loop/tools/
fiction_loop/RUN.md fiction_loop/specs/` — update or exempt EVERY hit;
record each disposition in §5. Known hits at ticket time: orchestrator.md
(move), RUN.md (text), extractor.md (sever), structural_gate.py (docstring
+ dead hint), CONTRIBUTING.md LAW 7 (resolve), intake_factory.spec.md:215
(satisfy), field_registry.md (rows), analyst.py (log-signature tables — its
step-10 log parsing is position-independent; verify and exempt with a note),
tools/INTEGRATION_SPECS.md (check; update only if it states the order).

## 4. Acceptance (ALL must pass)

1. Order proof: in orchestrator.md, the step-10 block's line number is
   GREATER than step 11.5's and LESS than step 12's
   (`grep -n "10\. Run bash — Living Document refresh\|11\.5\. Run bash\|12\. SPAWN Updater" fiction_loop/agents/orchestrator.md`
   — three hits, strictly increasing in that order: 11.5, 10, 12).
2. `grep -n "living_document" fiction_loop/agents/extractor.md` → zero hits.
   (HEAD today: 3.)
3. `grep -n "living_document" fiction_loop/agents/orchestrator.md` → hits
   only in: the moved step-10 block, the undo-ladder rungs, and the status
   command — NOT in the step-11 spawn prompt.
4. structural_gate.py: hint line gone
   (`grep -c "git restore" fiction_loop/tools/structural_gate.py` → 0);
   gate still exits 0 against the committed passing brief.
5. CONTRIBUTING LAW 7: `grep -n "standing violation" fiction_loop/CONTRIBUTING.md`
   → the LAW 7 instance now reads as resolved (T-008 named); no other law
   touched.
6. Registry + spec notes present (§3.6, §3.7); §3.8 disposition list in §5.
7. **Live validation (next owner-started chapter run, not this ticket):**
   watch two receipts and append them to §5 after the run: (a) the run's
   log sequence shows 11 → 11.5 → 10 → 12; (b) on any future gate FAIL,
   `core/living_document.md` is untouched (no new .bak, no diff) and the
   only cost is the writer call. Senior re-checks both at next acceptance.
8. Test suite (sanctioned command) → `1 failed, 331 passed`.
9. `git status --porcelain` → changes only in the write-set; one
   pathspec-limited commit.

## 5. Commit

`fix(specs): gate-before-refresh reorder — LAW 7 standing violation resolved whole (T-008)`

Trailers: `Ticket: T-008` / `Implemented-by: <Codex|Qwen>`.

## 6. Constraints

- Raspberry Pi; zero paid calls; no state or prompt-artifact edits.
- The reorder is all-or-nothing: if ANY §3 item cannot be completed,
  STOP and revert the working tree — a partial reorder is the exact
  failure LAW 7 forbids.
- On ANY failure: record in §5 exactly as observed, leave the tree
  coherent.

## 7. Implementer log (append below; never delete the ticket body)
