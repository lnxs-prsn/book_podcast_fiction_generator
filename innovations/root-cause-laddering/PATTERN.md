# Root-cause laddering — the defect usually lives one layer up

## What it is
A diagnostic habit for recurring or bounced failures: instead of fixing where
the failure *presents*, climb the layers that produce it. Two questions do the
climbing — **"instance or class?"** (am I fixing this one occurrence, or the
category that generates it?) and **"what layer does this defect actually live
in?"** — with a strong prior that the answer is *one layer up*, in the
machinery that changes the machine, not the machine that does the work.

## Problem it solves
Whack-a-mole. A team keeps fixing the visible symptom (the flaky output, the
crashing tool, the bounced work order) while the generator of those symptoms
sits untouched one level higher, so the failures keep re-appearing wearing new
faces. In self-modifying / agent-run systems this is acute: the bugs
concentrate in the *change-governance* layer (how work is authored, verified,
handed off), but attention stays on the production layer where they surface.

## How to use it
For any failure that bounced, recurred, or "shouldn't have happened":
1. **Ask "instance or class?"** If a class, the fix is a mechanism that makes
   the whole category impossible, not a patch to this case. Name both; ship
   the class fix, keep the instance fix as its test.
2. **Ask "what layer does this live in?"** Walk up: the output → the tool that
   made the output → the spec/order that drove the tool → the author of the
   spec → the process that governs authoring. Stop at the highest layer you
   can actually change.
3. **Expect one-layer-up.** The loud failure names a suspect; the root cause
   is often the character who *fed* that suspect (see situation-personification
   Q5). Check the feeder before blaming the actor.
4. **Confirm the fix is at the right altitude:** does it prevent the *next*,
   differently-masked instance? If it only stops this exact symptom, you
   stopped climbing too early.

## Fits projects like
Any system that debugs itself repeatedly — but especially **self-modifying or
agent-run** systems (codegen, agent pipelines, meta-tooling, CI-of-CI), where
the change-governance layer is both the highest-leverage and the least-watched
place for defects. Pairs naturally with situation-personification (that lens
finds *which character* is at fault; this one finds *which layer*).

## Proven in
Developed in book_podcast_fiction_generator, 2026-07 (AI-run fiction pipeline, one
human owner plus senior and junior AI agents).

**Worked.** Tickets T-008, T-012 and T-014 had bounced; laddering moved the fix from
each ticket to the authoring template (Upstream and Downstream fields, a
re-verify-consumers law; commit b615571). Separately, a regression was diagnosed as
**class over instance**: a one-off fix to decouple two checks (T-015) gave way to
retiring the component (T-017, f739452) and adding a tool regression suite (T-016,
12ed7b9). On 2026-07-20 laddering across a problem list named one root, truths kept
in two copies; that diagnosis is recorded but only partly carried out.

**Failed.** The 2026-07-19 authoring fix was judged high enough and was not: T-024 and
T-025 bounced on 2026-07-21 because acceptance results were predicted, not executed
(5cee375). The stopped-too-early check is judgment and missed this in advance.

**Correction to an earlier version of this section.** It said the ~40% generation pass
rate was an authoring defect and "not the model". The project's records treat that
rate as real and gave it its own tool-layer fix (T-012). Climbing found the authoring
defect too; it did not clear the lower layer. The same version's "drawing from memory"
was not found in the records and is removed.

Basis: commits and project documents listed in the context record, re-read 2026-11-05
by an agent working in this project. One project, no independent reuse, no measured rate.

## Kit (deployable files in `kit/`)
`kit/LADDER.md` — the two questions, the climb, and the "stopped too early?"
check, on one page. Run it at every bounce/recurrence.

## Context record

```json
{
  "schema_version": 1,
  "standard_version": "1.0",
  "id": "root-cause-laddering",
  "origin": {
    "project": "book_podcast_fiction_generator",
    "situation": "Repeated ticket bounces and a chapter that kept failing generation, during an AI-run fiction pipeline's between-run repair work.",
    "environment": "Raspberry Pi, single git repository, one human owner directing a senior AI agent and junior AI implementers through tickets; an AI-run fiction pipeline with deterministic gates and paid LLM calls.",
    "developed_on": "2026-07-19",
    "development_kind": "invented",
    "development_account": "Written up on 2026-07-19 (commit ef7ebf5) from a diagnosis session in this project; the repository records no received copy. 'Invented' means this specific form: the two questions, the named rungs, the one-layer-up prior and the stopped-too-early check. It claims no novelty over general root-cause analysis such as five whys, which it resembles; whether any such source influenced it is unknown."
  },
  "applicability": {
    "fits": [
      "A failure bounced, recurred or should not have happened, and the layers that produced it can be named and changed.",
      "Self-modifying or agent-run systems where work orders, specs or tooling generate failures seen elsewhere."
    ],
    "does_not_fit": [
      "A one-off failure with no recurrence, where the instance patch is sufficient.",
      "Cases where the higher rungs are outside your control; stop at the highest rung you can change."
    ],
    "prerequisites": [
      "A record of past failures and fixes detailed enough to walk the layers."
    ],
    "adaptations": [
      "Replace the rung names in LADDER.md with your own project's layers."
    ]
  },
  "evidence": [
    {
      "claim": "Laddering moved a repeated ticket-bounce problem from each ticket to the authoring template.",
      "outcome": "success",
      "project": "book_podcast_fiction_generator",
      "situation": "Tickets T-008, T-012 and T-014 had bounced; the fix was Upstream and Downstream template fields plus a re-verify-consumers law.",
      "occurred_on": "2026-07-19",
      "locators": [
        "commit b615571",
        "commit ef7ebf5",
        "progress/handoff-2026-07-18-all-tickets-landed-ch7-next.md section 14"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "Commits exist; the handoff section names the bounce class and the authoring fix.",
        "result": "Confirmed. The wording 'drawing from memory' in earlier write-ups was not found in these records and has been removed.",
        "reason": null
      }
    },
    {
      "claim": "Class-over-instance replaced a one-off decoupling fix with retiring the component and adding a tool regression suite.",
      "outcome": "success",
      "project": "book_podcast_fiction_generator",
      "situation": "T-015 would have decoupled two checks; T-017 retired the check and T-016 froze tool contracts.",
      "occurred_on": "2026-07-19",
      "locators": [
        "commit f739452",
        "commit 12ed7b9",
        "tickets/T-015-check-prose-anchor-coupling-regression.md",
        "tickets/T-017-retire-anchor-check.md"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "Commits and ticket files exist and say this.",
        "result": "Confirmed.",
        "reason": null
      }
    },
    {
      "claim": "An authoring-layer fix judged high enough on 2026-07-19 still let the next differently masked instance through.",
      "outcome": "failure",
      "project": "book_podcast_fiction_generator",
      "situation": "T-024 and T-025 bounced on 2026-07-21 because their acceptance results were predicted, not executed; the Upstream field only covered preconditions.",
      "occurred_on": "2026-07-21",
      "locators": [
        "commit 5cee375",
        "10-how-to-write-tickets.md rules T-6 to T-9",
        "innovations/ticket-dispatch/PATTERN.md Proven in"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "Commit and method file exist and cite both bounces.",
        "result": "Confirmed. The stopped-too-early check is applied by judgment and did not catch this in advance.",
        "reason": null
      }
    },
    {
      "claim": "Laddering across a problem list named one root: truths kept in two copies, synchronized by human memory.",
      "outcome": "mixed",
      "project": "book_podcast_fiction_generator",
      "situation": "A consolidated synthesis of pre-build factory problems; the resulting leak tickets are only partly carried out.",
      "occurred_on": "2026-07-20",
      "locators": [
        "progress/factory-open-problems-synthesis-2026-07-20.md section 0",
        "NEXT_ACTIONS.md sections 1 and 2"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "Synthesis text and queue entries read.",
        "result": "Diagnosis recorded; T-019 and T-020 remain undone in the queue, so the root is not yet validated by fixes.",
        "reason": null
      }
    }
  ],
  "limits": [
    "The 40% generation pass rate was not only an authoring defect: it was treated as real and got its own tool-layer fix (T-012). Climbing does not clear the lower layers.",
    "The one-layer-up prior is a heuristic from one project over a few weeks; no rate has been measured.",
    "All evidence is from one project and was assessed by an agent working in that project, with no independent reuse."
  ],
  "evolution": {
    "origin_state": "aligned",
    "assessed_on": "2026-11-05",
    "locators": [
      "progress/factory-open-problems-synthesis-2026-07-20.md",
      "NEXT_ACTIONS.md"
    ],
    "deltas": [],
    "reason": "The kit matches the practice as last recorded; last recorded project activity is 2026-08-10, so later practice is not observed."
  },
  "assets": [
    {
      "path": "kit/LADDER.md",
      "kind": "checklist",
      "purpose": "One-page statement of the two questions, the climb and the stopped-too-early check.",
      "adaptations": [
        "Rename the rungs for your project's layers."
      ],
      "dependencies": [],
      "context_ref": "PATTERN.md#kit-deployable-files-in-kit"
    }
  ]
}
```
