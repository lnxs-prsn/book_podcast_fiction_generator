# HANDOFF — 2026-08-10 (decision protocol + agent-judgment visibility)

**Scope of this session: governance/process only.** No chassis code changed, no state
mutated, no paid calls, no chapter run. Project state is exactly as the 2026-07-21
compaction describes it — **8 chapters, `arc_current` 2, ch9 run and BLOCKED at the
structural gate, HOLD standing.** Read `handoff-2026-07-21-compacted-state.md` for state;
read this for what changed about *how decisions get made and recorded*.

Verified at HEAD `b07a736` (working tree dirty — changes below are UNCOMMITTED).

## 1. What changed, and why

The owner identified two gaps that no document covered:

1. **Decisions needing the owner were being thrown mid-task with thin context**, and the
   session then stalled waiting for a ruling. LAW 13 already required
   propose-and-correct with a marked default, but `CONTRIBUTING.md` §4 step 7 said
   **"stop"** — so one unruled fork idled a whole session while the owner was away.
2. **Decisions the agent makes alone were invisible.** Ordering, deferrals, scope
   narrowings, struck tickets — none of the reasoning was written anywhere the owner
   could object to it.

### The protocol now (binding)

- **`AGENTS.md` rule 8 — owner decisions: file, don't page.** Hit a fork only the owner
  can settle → do not guess, do not stop to ask → append it to
  `fiction_loop/human_decision.md` in the §0 schema marked `[PROPOSED]` → **continue with
  other tasks that do not depend on the ruling.** Stop and tell the owner only if nothing
  else is unblocked. When unsure whether a task depends on the ruling, treat it as
  blocked; never spend paid calls on work a ruling could invalidate. **Maintainer
  sessions only** — a pipeline-run session is fenced out of `AGENTS.md` and still STOPS
  and reports per `RUN.md` STOP-DON'T-GUESS.
- **`AGENTS.md` rule 9 — agent judgment calls are auditable.** Calls made WITHOUT the
  owner go in `NEXT_ACTIONS.md` §3 with the reasoning, in the same sitting.
- **`CONTRIBUTING.md` §4 step 7 amended** — "stop" became "write the proposal, then
  continue; stop only if nothing else is unblocked", with the owner rule recorded as case
  law. **This is the only line of the constitution that had to change.**
- **`CONTRIBUTING.md` LAW 13 extended** — open forks are APPENDED to `human_decision.md`
  marked `[PROPOSED]`; status flips in place when ruled. Also: never file a half-proposal
  (uncosted options = design work owed first, not a question).

### Where things live now

| Need | File | How to find it |
|---|---|---|
| Forks awaiting the OWNER | `fiction_loop/human_decision.md` | `grep -n "^## .*\[PROPOSED\]" fiction_loop/human_decision.md` |
| What's next + why; agent's own calls | `NEXT_ACTIONS.md` (root) | §1 next, §2 deferred + why, §3 judgment calls |
| Archived agent judgment calls | `progress/agent-decisions.jsonl` | append-only JSONL, stdlib-parseable |

**Decision entry schema** (`human_decision.md` §0 defines it): `## <ISO8601> — <title>
[PROPOSED|ACCEPTED|REJECTED]` · Essence · Analogy (optional) · Impact & reversibility ·
Architecture points at · Context · Options with a marked default · Decision.
DECISIONS 1–15 predate it and keep their prose form — already ruled, nothing to migrate.

**`NEXT_ACTIONS.md` keeps only the newest 5 per section**; older entries MOVE (never
copy) to `progress/agent-decisions.jsonl`. Three earlier calls were seeded there at
creation (T-024 acceptance correction, T-025 scope narrowing, T-021 strike).

## 2. Effect on the ch9 block

The 2026-07-21 handoff §1 listed two PENDING SENIOR ACTIONS. Status now:

- **(B) — DONE.** The arc-vs-operation wrong-approach fork is **filed and ready to rule**:
  `human_decision.md`, entry `2026-08-10 — Featured wrong approach on a return:
  operation-tied or arc-tied? [PROPOSED]`. Where 07-21 §1 says "(B) … NOT yet drafted",
  that is STALE.
- **(A) — still NOT started.** Pinning the deterministic re-derivation mechanism for
  ch9's stale `failure_mode_to_show="none"`.

**Two findings from writing (B), both from reading live state — they change the fork:**

1. **`failure_modes_not_yet_shown` is `[]` book-wide AND for `op_separate_condition`.**
   Every one of the 14 failure types has been shown. "Pick an unshown one" is not an
   available answer, so this needs a general rule, not a ch9 patch.
2. **The arc-2 cast is already live** — `failure_mode_lead_history` shows ch8 led with
   "the confident specialist". The question is only which authority governs a *return*.

Consequently the fork was filed with **three** options, not the two 07-21 framed: a union
(operation-pool-first, arc-cast fallback, arc-filtered) is the marked DEFAULT because it
is DECISION 13's already-ruled selector shape generalised. Also recorded: **T-024's
canonicity check already encodes the operation-tied option implicitly** — an unruled
position that was built in, not a neutral detector.

**Correction to a 07-21 claim.** That handoff states causes (1) and (2) are independent.
Treat as **provisional**: the pointer is produced by the T-026 selector, so if the fork is
ruled operation-tied the selector's source may change and a re-derived pointer would need
redoing. Cheap-to-redo is not the same as independent. Logged in `NEXT_ACTIONS.md` §3.

**HOLD still stands** — no gate override, no blind redo, no paid ch9 re-run until (A)
lands and the fork is ruled.

## 3. Files changed this session (all UNCOMMITTED)

```
M  AGENTS.md                        rules 8 (owner decisions) + 9 (judgment calls);
                                    old rule 7 (exploration) kept its number
M  fiction_loop/CONTRIBUTING.md     §4 step 7 amended; LAW 13 extended
M  fiction_loop/human_decision.md   §0 (how to find open forks + schema); ch9 fork
                                    appended as [PROPOSED]; stale 2026-07-02 banner marked
?? NEXT_ACTIONS.md                  queue + reasoning + agent judgment log
?? progress/agent-decisions.jsonl   append-only ledger, 3 seeded entries
```

Verified: 15 `## DECISION` headers and 14 ruling lines intact in the ledger; the ledger
JSONL parses; the `[PROPOSED]` grep returns exactly one entry.

**Suggested commits** (pathspec-limited, per AGENTS.md rule 4): governance
(`AGENTS.md` + `CONTRIBUTING.md` + `human_decision.md`) separate from the new
visibility files (`NEXT_ACTIONS.md` + `progress/agent-decisions.jsonl`).

## 4. What a cold session should do next

Unchanged in substance from 07-21, now with reasoning recorded in `NEXT_ACTIONS.md` §1–2:

1. **(A)** pin the ch9 pointer re-derivation mechanism — output is provisional until the
   fork is ruled.
2. **C3 "shown" design pass** — the long pole; gates later-arc ADV-2/RDR-2 correctness and
   the bulk of the factory, and is startable *because* ch9 is held.
3. **T-020 / T-023** — drafted, dry-run-verified, independent, dispatchable now.
4. **T-022 Phase-A ticket** — writable today (T-024 + T-026 both landed).

Deliberately NOT started: widening T-024's canonicity check — its shape differs under
each option of the open fork, so starting it is guessing.
