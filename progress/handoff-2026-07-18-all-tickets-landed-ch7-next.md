# HANDOFF — 2026-07-18 (session end) — T-002/004/005/003 ALL LANDED; next: ch7 kickoff

Written by the senior instance at session end; supersedes
`handoff-2026-07-18-ch6-landed-open-queue.md` (whose §§5–8 addenda remain the
detailed record of today's review/ticket cycle — read them for the *why*
behind any claim here). Every claim below verified against git/files at
commit `03a5d32`, working tree clean.

## 0. Roles (unchanged; precedent extended)

Owner assigns; senior writes tickets, re-runs acceptance independently,
updates the handoff, never implements — EXCEPT owner-delegated small tasks
(precedent today: the T-003 `.env` blind key rename, delegated explicitly).
Codex/Qwen implement. New precedent (T-003 §8): when the implementer's
harness blocks a step (read-only `~/.cache/uv`, git index writes), the
senior runs that step externally, commits on the implementer's behalf with
the `Implemented-by:` trailer, and logs it in the ticket — the
implementation credit stays with the implementer.

## 1. State

- **Chapter 006** committed `a77eec8`; prose review PASSED and owner
  ACCEPTED 2026-07-18 (record: prior handoff §5). 6 chapters exist;
  `arc_current` = 1.
- **Next pointer: 007 — arc_transition.** No gate, no anchor, no operation
  due; `secondary_touches: []` is valid (ambient reinforcement rides the
  Assembler's "use naturally" list). Pointer clean — RUN.md prompt as
  written, no resume note.
- **All four tickets merged AND senior-accepted:** T-002 (`aebc2ca`, URL
  normalization + 404 signature), T-004 (`58e4dbd`, unnamed newcomers reach
  the F15 gate), T-005 (`1063ff0`, extractor STEP A.0 arc-transition
  precedence + required lead_failure_mode), T-003 (`9abbd11`,
  `BOOKGEN_LLM_*` env namespace, clean break).
- **Env contract is now `BOOKGEN_LLM_*` everywhere, including `.env`**
  (3 keys renamed blind by senior per delegation). Analyst ran green
  end-to-end on the new names 2026-07-18 night (key present, state sync ok,
  tree clean). The Qwen-shell 404 collision class is closed at the root.
- `tickets/` files carry complete implementer + acceptance logs for each.

## 2. Binding facts (cold session must know)

1. **pytest is NOT a project dependency.** Sanctioned command:
   `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q`
   (serial — Raspberry Pi). Never add pytest to pyproject.
2. **Implementer-harness blocks are a known class:** safety-classifier
   false-positives (analyst.py), service outages, read-only uv cache, git
   index writes. Remedy: §0 precedent. Verify with receipts, not STATUS
   claims.
3. **F15 false-fail is RESOLVED** (T-004): the structural gate now counts
   unnamed newcomers via `other_entrants` `name: null` entries. The old
   grep-the-prose workaround is obsolete. Updater skips `name: null` for
   cards (permanent record stays named-only, D6).
4. **Extractor pointer logic is single-outcome** (T-005): STEP A.0 sends
   all-deficits-zero straight to arc transition; the FALLBACK is deleted;
   `lead_failure_mode` is REQUIRED for gate chapters ("none" only for
   structural types).
5. **Curriculum §7 map columns beyond an op's card `touch_target` are the
   AMBIENT layer, not scheduled chapters** (owner D9 lever 2; D1 hybrid).
   The D9-amendment note now sits above the map in
   `core/concept_curriculum.md`. Cards' `touch_schedule` is the machine
   truth. Do not re-open; ch6's "owned" compression was verified correct.
6. **Thinking tax (deepseek-v4-pro): ~2.5× billed vs visible tokens is
   EXPECTED**; analyst WARNs at that ratio by design. Keep the model — full
   ch6 cycle cost $0.028, cheapest to date. Keep `max_tokens` ≥ ~2.5×
   expected prose or reasoning eats the budget (empty-output smoke receipt
   2026-07-17).
7. **Ticket-authoring lesson (3 corrections on T-003 alone):** dry-run every
   acceptance command against HEAD when writing a ticket — check the grep's
   scope covers the write-set AND that its pattern still passes after a
   correct implementation (substring collisions with new names).
8. **Known pre-existing test failure, NOT a regression:**
   `src/engines/tests/test_factory.py::test_default_splitter_engine_passes_openrouter_timeout_seconds`
   (TypeError: missing `source`) — fails identically at pre-T-003 HEAD;
   engines/slicer are the out-of-scope legacy subsystem. Future ticket only
   if revived. Expect `1 failed, 331 passed` until then.

## 3. Open queue (in order)

1. **OWNER, before the next run:** confirm the Qwen companion session's live
   environment exports no `OPENROUTER_*` (repo and shell rc files verified
   clean; that session is the one place the senior cannot see). This is the
   last residual of the 404 saga.
2. **Chapter 007 kickoff** (arc_transition) — PAID RUN, owner starts it.
   RUN.md prompt as written. First run under the new env names and the
   T-004/T-005 contracts: watch step 0 (analyst must pass key-present on
   `BOOKGEN_LLM_API_KEY`) and expect the arc summary step (updater STEP 9)
   to fire for the first time.
3. Optional, owner-only (LAW 8 hand surgery, own commit): backfill
   `{"chapter": "006", "lead": "the executor"}` into
   `master_state.failure_mode_lead_history`. Documented, harmless if left —
   arc 2 rotates a fresh failure-mode pool.
4. Older queue: `handoff-2026-07-17-clone-audit.md` §5, unchanged.

## 4. How to continue (cold-start)

Read-first: this file → `handoff-2026-07-18-ch6-landed-open-queue.md`
(§§5–8) → `fiction_loop/CONTRIBUTING.md` → `tickets/` (all four have full
logs) → `fiction_loop/core/agent_conduct.md` before any chapter run.
Diagnostics (zero tokens): `PYTHONPATH=src .venv/bin/python
fiction_loop/tools/analyst.py` and `.../progress.py`. Conduct: never
cat/grep/print `.env` or `env | grep`; env inspection is `echo $VAR` for
non-secret vars only; interpreter is `.venv/bin/python` from repo root, uv
only, never pip; Raspberry Pi — nothing heavy in parallel.
