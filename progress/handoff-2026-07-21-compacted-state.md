# HANDOFF — 2026-07-21 (COMPACTED current-state)

**This is a COMPACTION.** It snapshots current truth and replaces the running
`handoff-2026-07-19-compacted-state.md` (§§1–17) as the front door. That file is
ARCHIVED — still the detailed *why* behind any claim here, read this first.
Compaction method: `innovations/handoff-discipline/kit/HANDOFF_RULES.md` §Compaction.
All claims below re-verified against git/state/code at **HEAD `2abd2a9`, tree clean**.

## 1. State (verified against master_state.json + git, 2026-07-21)

- **8 chapters committed, `arc_current` = 2.** Next pointer = **ch9 `009`**:
  `return_to_character`, `char_004` (Wanjiku Mwangi), `op_separate_condition`,
  `touch_due 2`, **`name_due true`**, `failure_mode_to_show "none"`, `anchor_appears true`.
- ch8 committed + accepted (`8935458`). No chapter run since. **ch9 is the next
  product step — PAID, owner-started** (see §5 for what must land first).
- Restore point: annotated tag **`starting_factory` → `fe2e20d`** (local, unpushed)
  marks the working 1-book flow before factory work. All commits since are docs/
  tickets/spec only — **no chassis code has changed since `fe2e20d`.**

## 2. Roles (unchanged)

Owner assigns. Senior (this instance) writes tickets in `tickets/`, re-runs
acceptance independently, records design rulings in `human_decision.md`, updates this
handoff, **never implements** — except owner-delegated small tasks. Implementers
(Codex/Qwen; tickets are now **implementer-agnostic**) stay in the write-set,
STOP-not-improvise on any ambiguity. Harness-block precedent: when an implementer's
harness blocks a step, the senior runs it externally and commits `Implemented-by:`.

## 3. Binding facts a cold session must know

1. **pytest is NOT a project dependency.** Sanctioned command:
   `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q`. Baseline:
   **`1 failed, 331 passed`** — the one failure
   (`test_default_splitter_engine_passes_openrouter_timeout_seconds`) is a known
   pre-existing legacy failure, NOT a regression.
2. **Tool regression suite:** `PYTHONPATH=src .venv/bin/python fiction_loop/tools/regression/run.py`
   → baseline **12/12 PASS** (verified 2026-07-20). This is the mandatory gate for any
   shared tool-surface change (LAW 17).
3. **Interpreter:** `.venv/bin/python` from repo root, usually `PYTHONPATH=src`. **uv
   only — never pip.** Raspberry Pi: nothing heavy in parallel. **No paid calls unless
   a ticket/run budgets them.** Env namespace is `BOOKGEN_LLM_*` (T-003).
4. **Pipeline order (post-T-008):** 8 Writer → 9 save → 11 Extractor → 11.5 structural
   gate → 10 living-doc refresh → 12 Updater. The **structural gate (11.5)** is the
   anchor authority, receipt-guarded (T-009); the Updater is unreachable without a
   fresh PASS. `arc_current` self-manages (T-006). The run driver is Orchestrator ONLY
   (T-011).
5. **The teaching model (crucial — it dissolved the "ADV-3 crisis"):** the **focal is
   the RESOLVER** (reaches the right question; `assembler.md:118`), NOT a failer. Wrong
   approaches are carried by a separate cast of **wrong-approach solvers** (≥1 improvised
   newcomer, F15). A **returning master applying correctly while newcomers fail** is the
   *intended engine of the whole back half of the book* (operation difficulty is a fixed
   rating; mastery grows with touches; late-arc gates pair a master with failing
   newcomers). `failure_mode_to_show` = the chapter's *featured* failure (a solver's),
   not the focal's mistake.
6. **Earned-failure-pool fact (drove DECISION 13):** `init_state.py:497` pre-seeds
   EVERY operation's failure pool at init, INCLUDING future arcs. So "union of all
   process_state pools" = all 14 book-wide failure types. Any earned-pool derivation
   MUST filter by `arc_introduced ≤ arc_current` or it leaks future-arc failures into
   early chapters.

## 4. Decision ledger (rulings live in `fiction_loop/human_decision.md`)

DECISIONS 1–14 recorded there. The ones a cold session most needs:
- **D10** — arc-2 cast quota 3→2 (Section 4 is sole count owner); `QUOTA_BY_ARC`
  freeze in regression.
- **D11 (B1–B5)** — Updater idempotency stamp; collapse 4 re-verify layers into ONE
  consumer-map organ (audit-first); anti-formula = multi-axis budget (specifics open);
  anchor-desc → `mystery_anchor.json` (=T-020); F14 null≡false.
- **D12 (C1–C4)** — mystery-fairness = clue schedule + auditor (process-pack); code
  substrate deliberately LAST (D8 stands); **"shown" needs a dedicated arc-aware design
  pass before arc 3** (beats-not-solvers); world-thinning minor.
- **D13** — **ADV-3 resolved**: featured-failure selector earned-pool fallback
  (arc-filtered; LED-primary/SHOWN-tiebreak) + `"none"` reserved for interludes + gate
  guard. = ticket **T-026**.
- **D14** — **pre-writer gate** = single-source `gate_check_registry` + bidirectional
  parity guard; Phase A (validator) then Phase B (generative, post-ch9); IS the D11-B2
  consumer-map organ. Spec: `fiction_loop/specs/prewriter_gate.spec.md`.

## 5. Open queue

**Dispatch-ready tickets (all zero-paid, offline, implementer-agnostic, drafted — NOT
dispatched; senior dry-run status noted):**
1. **T-024** gate cross-field integrity (ADV-1/2/4) — *first* (T-026 reuses its
   gate/pointer binding). Full acceptance dry-run NOT yet done.
2. **T-026** selector earned-pool fallback + `"none"` guard (ADV-3/D13) —
   **dispatch-verified** (senior dry-run 2026-07-20, arc-filter correction applied).
3. **T-025** prose name-presence guard (the free verify-from-source slice).
4. **T-019** retire `QUOTA_BY_ARC` leak (Stage-4 down payment).
5. **T-020** anchor-description leak → `mystery_anchor.json` (D11-B4). **Independent** of
   the chain — dispatch anytime.

Order: **T-024 → T-026 → T-025 → T-019**; T-020 anytime.
**ch9 (paid) should not run until T-026 lands** (removes the `"none"` ambiguity
deterministically), ideally with T-024 + T-025 (they guard the exact return-chapter
failure classes).

**Reserved-backlog outcomes:** T-021 (mirror leak) **STRUCK — not a leak** (Assembler
fetches from `world_rules §5`; `field_registry` not-a-leak note left). T-022 **spec'd**
(D14) — its Phase-A ticket waits on T-024/T-026 (they extend the seed check-set).
T-023 (curriculum rule-5 regression) **deferred by owner**.

**Open design work (not tickets yet):** the **"shown"/C3 design pass** (before arc 3;
prerequisite for ADV-2/RDR-2 correctness in later arcs); **B3** anti-formula specifics
(budget formula, thresholds, enforcement home); **RDR-3** mystery-fairness plan-schema +
auditor isolation; **B2** consumer-map organ (now partly absorbed — the D14 gate-check
registry IS this organ for the gate-check duty). Un-ticketed hardening: **ADV-5** Updater
idempotency (D11-B1), **P2** calibration organ, **P3** fire `anchor_interlude`, the
**paid** one-way-door Stage-5 read.

## 6. Factory-build sequencing (asked + answered this session)

The factory (multi-book, `specs/intake_factory.spec.md` §2 build list) is design-
complete, unbuilt. Per **D8/D12-C2**, the code/factory layer is deliberately LAST:
**ch9 validates the chassis on its riskiest path (a return) → then build.** So ch9 is
the go-signal to *start*, but:
- Build **design-settled parts first** (T-022 pre-writer gate = the spec's designated
  first build; Stage-4 manifest down-payments like T-019's `arc_quota`).
- **Defer** stages depending on open design. The thing gating the *bulk* of the factory
  is NOT ch9 — it's the **C3 "shown" design pass**.

## 7. Read-first order (cold session)

1. **This file** — current state + queue.
2. Archived *why*: `handoff-2026-07-19-compacted-state.md` (§§1–17), then older
   2026-07-18/17 handoffs.
3. `fiction_loop/CONTRIBUTING.md` — the 17 laws; binding before any change under
   `fiction_loop/`.
4. `fiction_loop/human_decision.md` — design rulings (DECISIONS 1–14).
5. `fiction_loop/core/agent_conduct.md` — binding during a chapter run.
6. `tickets/` — drafted work orders (T-019/020/024/025/026); `fiction_loop/specs/` for
   factory + pre-writer-gate design.

Diagnostics (zero tokens): `PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py`
and `.../progress.py`; regression `.../tools/regression/run.py`.
