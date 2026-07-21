# PRE-WRITER GATE SPEC — the gate-check registry + prompt-parity validator

Status: DESIGN (2026-07-20). Ticket slot **T-022** (marker:
`tickets/T-022-prewriter-gate-SPECD-ticket-pending.md`; Phase-A ticket pending
T-024/T-026). Implements owner DECISION 14. The intake_factory
build list names this the "FIRST dissolver (Force 3)". Small by intent — this
defines the durable **contract** (a single registry of gate checks) and **Phase A**
precisely; Phase B is sketched only.

## 1. Purpose

Before the paid Writer runs, cheaply confirm the assembled prompt actually
*instructs* the Writer to satisfy every check the post-Writer structural gate
(step 11.5) will later *enforce*. Zero-token; prevents paid gate failures. It
would have caught **ch6-F15** (the gate had an F15 check; the prompt failed to
instruct the newcomer → post-paid FAIL).

## 2. Problem it dissolves (and the trap it must NOT create)

"The set of gate checks" is duplicated today: `structural_gate.py` *enforces* them;
`assembler.md` *instructs* them; nothing links the two, so they drift (ch6-F15).
The naive fix — a standalone pre-writer checklist — adds a THIRD hand-maintained
copy: add a gate check later, forget the checklist, and the pre-writer gate reports
a **green light that lies**. This spec forbids that: there is exactly **one** list,
and divergence from it is a **failing test** — "synced by the build," not by memory
(the consolidated root cause).

## 3. The single artifact — `gate_check_registry`

One machine-readable file (recommended `fiction_loop/core/gate_check_registry.json`),
the sole home for the gate's check-set. One entry per check:

```
{
  "id":               "quota",                       # stable key
  "applies_to":       ["new_focal_character", "return_to_character"],
  "post_writer_check":"len(distinct failure_modes_shown) >= arc quota",  # what the gate enforces (spec/ref)
  "prompt_rule":      "this chapter requires EXACTLY <N> wrong-approach solver scenes",  # what the prompt must carry; null if not Writer-facing
  "prompt_detector":  "<marker/regex the pre-writer validator greps in the assembled prompt>",
  "source":           "curriculum §9 / QUOTA_BY_ARC (pack)"             # where any VALUE comes from (LAW 14)
}
```

**Key distinction — not every check is Writer-facing.** Two kinds of entry:
- **prompt-facing** (`prompt_rule` non-null): the Writer must be instructed — the
  pre-writer validator checks the prompt carries the rule (quota, anchor-appears,
  echo, F14 life-progression, F15 newcomer, the failure beats).
- **brief-integrity** (`prompt_rule: null`): a check on the *extracted brief*
  matching the schedule, not a Writer instruction — no prompt counterpart, so the
  pre-writer validator skips it (focal-id ↔ pointer, is_new correctness, population
  membership, chapter-freshness, canonical-label membership). These still live in the
  registry so the **gate-parity guard** (§5) covers the whole check-set.

Values (quota numbers, canonical labels, earned pool) are read from pack data at
runtime — **never hardcoded** in the registry (LAW 14).

## 4. Consumers & phasing

- **Phase A (now-ready once deps land) — registry is DESCRIPTIVE.** A read-only
  pre-writer validator reads the registry and, for each prompt-facing entry whose
  `applies_to` matches the chapter type, confirms the assembled prompt contains the
  rule (via `prompt_detector`). The gate and assembler are unchanged. Low-regret: a
  new tool + a data file + a regression assertion; does not touch the
  `starting_factory` chassis logic beyond tagging (§5a).
- **Phase B (post-ch9) — registry becomes GENERATIVE, additively.** The Assembler
  generates its hard-rule blocks from `prompt_rule`; the structural gate generates
  its checks from `post_writer_check`. The parity guard then becomes tautological.
  **No rewrite** — Phase A's registry is promoted from "spec of what should be there"
  to "source of what is there." B is a later ticket; do not build it now.

## 5. The parity guard — what makes the trap impossible (ships WITH Phase A)

Two regression assertions (the regression suite is already the mandatory gate for
shared-surface changes, LAW 17), so any divergence goes red:

- **(a) Registry ⊇ gate.** Every check `structural_gate.py` can emit is tagged with
  a registry `id`; assert `{ids the gate emits} == {registry ids}`. *You cannot add a
  gate check without a registry entry.* (Requires a small Phase-A refactor: tag each
  `problems.append` with its id — the one bit of B-ish work pulled forward, and the
  only way to close the "stray unregistered gate check" hole.)
- **(b) Registry → prompt.** Every prompt-facing entry's `prompt_detector` matches
  the assembler template. *A registered Writer-facing check with no prompt rule* → red.

Lighter fallback (if (a)'s tagging is deferred): per-entry crafted-bad fixtures the
gate must reject. Catches "registry entry with no enforcement" but NOT a stray
unregistered gate check — so it is weaker than the tagged-id guarantee. Recommended:
do the tagging; it is small and it is what makes "never happens" true.

## 6. Seed entries (the check-set as of the T-024/T-026 additions)

prompt-facing: `quota` · `anchor_appears` · `echo` · `f14_life_progression`
(null≡false, DECISION 11 B5) · `f15_newcomer` · `featured_failure` (non-"none",
earned-pool, DECISION 13 / T-026).
brief-integrity (no prompt rule): `chapter_freshness` · `focal_id_matches` ·
`is_new_correct` · `population_membership` · `label_canonical` (all T-024).

## 7. Dependencies & sequencing

- **Seed completeness requires T-024 + T-026 to land first** (they ADD checks). Write
  the Phase-A ticket AFTER them, or the seed registry + parity guard get rebuilt
  twice. This spec can be written now; the ticket waits.
- **Orchestrator wiring:** the pre-writer validator runs between assembly and the paid
  Writer — that step lives in `RUN.md`, which is OUTSIDE the chassis write-set (same
  senior-TODO shape as T-025). The ticket leaves wiring as a senior task.
- **C3 "shown":** the `featured_failure` / quota entries count failure beats; when C3
  swaps the unit type→beat, the registry entry text updates in ONE place. Keep entries
  unit-neutral (DECISION 13 §4).

## 8. Relationship to B2 and the LAWs

This registry + its parity guard **is a concrete instance of the DECISION 11 B2
consumer-map organ** (one source; its consumers proven to match) — they should be
built as one, not two parallel single-sources. It structurally embodies **LAW 16**
(a rule ships its check — the check-set itself is now guarded) and **LAW 17** (the
registry is the machine-readable rule ↔ check ↔ consumers map).

## 9. Non-goals (do NOT do here)

- Do not build Phase B's generative machinery now (post-ch9).
- Do not hardcode any pack value (quota numbers, labels) in the registry (LAW 14).
- Do not make the pre-writer validator write state or spend tokens — read-only, stdlib.
