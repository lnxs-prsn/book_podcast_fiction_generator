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
           note only),
           fiction_loop/tools/INTEGRATION_SPECS.md (§5 + §6 order text —
           ADDED on redispatch, §3.9),
           fiction_loop/core/pipeline_stage_manifest.md (order table +
           Extractor input list — ADDED on redispatch, §3.10)
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
tools/INTEGRATION_SPECS.md (WRITE — §3.9, it states the old order in two
places), core/pipeline_stage_manifest.md (WRITE — §3.10, order table +
Extractor input list).

**3.9 tools/INTEGRATION_SPECS.md** (added on redispatch — the original
ticket listed this as a conditional "check" and omitted it from the
write-set; the 2026-07-18 Codex audit correctly found it states the old
order and STOPPED per LAW 7. Two edits, text only, no code):
- §5 "refresh_living_doc.py — CONTRACT SPEC", **When called** (~line 283):
  change "AFTER step 9 (chapter saved) and BEFORE step 11 (Extractor
  generates update_brief). The updated living_document.md gives the
  Extractor richer context when writing the update_brief." to state the
  new order — refresh runs AFTER the structural gate passes (step 11.5)
  and BEFORE the Updater (step 12); DELETE the "richer context to the
  Extractor" rationale entirely (the Extractor no longer consumes
  living_document.md — §3.2). Keep the "optional but recommended / drift"
  note.
- §6 "HOW ORCHESTRATOR INTEGRATES THE TOOLS" (~lines 390–422): the step-10
  refresh block currently sits between step 9 (save) and step 11
  (Extractor) and its exit-0 line reads "Proceed to step 11 (Extractor)."
  Move/renumber the illustrative sequence so refresh follows the gate and
  precedes the Updater, matching orchestrator.md's new order (11 → 11.5 →
  10 → 12; step numbers kept per M-15). Exit-0 text becomes "Proceed to
  step 12 (Updater)." Mirror orchestrator.md exactly — this section is a
  worked example of it, so it must not diverge.

**3.10 core/pipeline_stage_manifest.md** (added on redispatch — same
audit, same STOP; this is a live data-availability contract):
- The order table (lines 9–19): the manifest is keyed by orchestrator
  step number and step numbers are KEPT, but the "Guaranteed available"
  semantics change. Row **11 Extractor**: REMOVE `living_document.md`
  from its input list (the Extractor no longer reads it — §3.2), and its
  note must no longer imply refresh ran before it. Row **10
  refresh_living_doc.py**: it now runs AFTER the gate and produces the
  refreshed doc for the Updater's downstream reference, NOT as Extractor
  context. Make the table unambiguous about execution order vs step
  number — annotate that execution order is 8→9→11→11.5→10→12 while step
  labels are retained (point at orchestrator.md as the authority).
- The step-11.5 structural gate is absent from this table today; adding a
  row for it is OPTIONAL and OUT OF SCOPE for T-008 (it produces no data
  field this manifest tracks until T-009's pass-receipt lands). Do not
  add it here — leave for T-009 if that ticket needs it. Note the
  omission in §5 so it is a recorded decision, not a miss.
- The "Why this exists" prose (lines 21–32): verify it makes no claim
  that depends on the old refresh-before-Extractor order; if clean,
  exempt with a note in §5. Do not rewrite it speculatively.

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
6a. **INTEGRATION_SPECS.md (§3.9):**
   `grep -n "richer context" fiction_loop/tools/INTEGRATION_SPECS.md` → 0
   hits (rationale deleted). `grep -n "Proceed to step 11 (Extractor)"
   fiction_loop/tools/INTEGRATION_SPECS.md` → 0 hits; the §6 refresh
   block's exit-0 line now names step 12 (Updater). The §5 "When called"
   line names the gate (11.5) and Updater (12), not "BEFORE step 11".
6b. **pipeline_stage_manifest.md (§3.10):**
   `grep -n "living_document" fiction_loop/core/pipeline_stage_manifest.md`
   → hits only in the refresh (step-10) row, NOT in the Extractor
   (step-11) input list. The table or its note states execution order
   8→9→11→11.5→10→12. §5 records the deliberate omission of a step-11.5
   row.
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

### 2026-07-18 — Codex — BLOCKED

- Timing/dependency gates: PASS. T-007 is merged at `b8f0b7c`; current handoff
  §9 records chapter 008 abandoned and the between-runs queue unlocked.
- Began the complete §3 reorder in the declared write-set, then ran the required
  §3.8 LAW 4 audit before validation.
- BLOCKER: the audit found live old-order contracts outside this ticket's
  write-set:
  - `fiction_loop/tools/INTEGRATION_SPECS.md:283` says refresh runs before
    Extractor and supplies it richer context; line 418 says refresh proceeds to
    step 11. Section 3.8 explicitly says to update this file if it states the
    order, but the ticket does not authorize writing it.
  - `fiction_loop/core/pipeline_stage_manifest.md:17-18` places refresh at 10
    before Extractor at 11 and lists `living_document.md` as an Extractor input.
    It is a live data-availability contract and is also absent from the
    write-set.
- Expanding the write-set or exempting contradictory live contracts would
  violate the ticket's write-set and LAW 4 respectively. Per §§6–7, STOPPED
  rather than improvising and reverted every partial implementation edit.
- Final tree is coherent: only this required implementer-log entry is changed.
  Paid calls: none. Acceptance suite not run because §3 could not be completed.

### 2026-07-18 — senior — REDISPATCH (blocker valid; ticket defect fixed)

The STOP was correct. Both flagged files are live old-order contracts and,
under LAW 7's all-or-nothing rule, a partial reorder that leaves them
stating the old order is the exact failure the ticket forbids — reverting
was the right call, not over-caution. The defect was mine: §3.8 named
`INTEGRATION_SPECS.md` only as a conditional "check" and left it out of
the write-set, and `pipeline_stage_manifest.md` was omitted entirely.
Fixed on redispatch:
- Write-set: both files ADDED (see header).
- §3.9: exact edits for INTEGRATION_SPECS.md (§5 "When called" + §6 worked
  sequence — text only, mirror orchestrator.md).
- §3.10: exact edits for pipeline_stage_manifest.md (Extractor input list
  loses living_document.md; refresh row + execution-order annotation;
  step-11.5 row explicitly OUT OF SCOPE, record in §5).
- §6a / §6b: grep-based acceptance proofs for both.
The reorder remains all-or-nothing and BETWEEN runs; T-007 already merged
(`b8f0b7c`). Re-run the FULL §3 (all items) from a clean tree — do not
resume the reverted partial. Nothing else in the ticket changed.

### 2026-07-18 — Codex — IMPLEMENTED

- Timing/dependency gates: PASS. T-007 is merged at `b8f0b7c`; current handoff
  §9 records chapter 008 abandoned and the between-runs queue unlocked. Paid
  calls: none; state, prompt artifacts, chapters, living document, backups, and
  spend receipts were not touched.
- Implemented the complete order `8→9→11→11.5→10→12` while retaining step
  labels. The Extractor no longer reads `living_document.md`;
  `reader_can_suspect_update` now derives from chapter prose +
  `mystery_anchor.json`. The paid refresh runs only after structural-gate PASS.
- LAW 4 audit (`refresh_living_doc|living_doc|step 10`) dispositions:
  - UPDATED: `agents/orchestrator.md`, `agents/extractor.md`, `RUN.md`,
    `tools/structural_gate.py`, `CONTRIBUTING.md` LAW 7,
    `core/field_registry.md`, `specs/intake_factory.spec.md`,
    `tools/INTEGRATION_SPECS.md`, and `core/pipeline_stage_manifest.md`.
  - EXEMPT — position-independent or unrelated step labels:
    `tools/analyst.py` parses the refresh failure event rather than pipeline
    position; `core/agent_conduct.md` only names the stable step-10 log;
    `agents/updater.md` uses its own internal STEP 10 report; `tools/pipeline_config.toml`,
    `tools/refresh_living_doc.py`, and the remaining `INTEGRATION_SPECS.md`
    hits define refresh mechanics/configuration, not call order;
    `agents/assembler.md`, `core/character_naming.md`, and
    `specs/pipeline_fixes.spec.md` use the living doc for other contracts or
    historical defects.
  - EXEMPT — immutable/out-of-write-set state receipts:
    `core/living_document.md` and its `.bak.*` files retain historical
    self-description saying the Extractor reads the document. They are L4 run
    artifacts, explicitly forbidden by this ticket's state-access fence, and
    are no longer operational inputs because both the Extractor spec and
    Orchestrator spawn list removed the path.
  - Deliberately did not add a step-11.5 manifest row, as §3.10 marks it
    optional and out of scope; the manifest's existing rationale is
    order-independent and was left unchanged.
- Static acceptance: order line numbers are 243 (11.5), 252 (10), 267 (12);
  Extractor `living_document` hits = 0; structural-gate `git restore` hits = 0;
  both stale INTEGRATION_SPECS phrases have 0 hits; manifest has one
  `living_document` hit (refresh row only) and records the new execution order.
  `git diff --check` PASS.
- Gate receipt against current HEAD: Exit 1, exactly as expected for the
  deliberately preserved abandoned chapter-008 brief — `anchor absent from a
  gate chapter`. Thus §4.4's older “committed passing brief” fixture assumption
  is stale after handoff §9/commit `cf70a1b`; no state or fixture was changed to
  manufacture a PASS. Gate decision logic is unchanged by T-008 (docstring and
  dead restore hint only).
- Sanctioned serial suite:
  `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q` →
  expected `1 failed, 331 passed`; sole failure is the documented out-of-scope
  `test_default_splitter_engine_passes_openrouter_timeout_seconds`
  (`default_splitter_engine()` missing `source`).
- §4.7 live validation is intentionally deferred to the next owner-started
  paid chapter run, per ticket. The step-11.5 manifest-row omission above is
  deliberate, pending T-009 if needed.
