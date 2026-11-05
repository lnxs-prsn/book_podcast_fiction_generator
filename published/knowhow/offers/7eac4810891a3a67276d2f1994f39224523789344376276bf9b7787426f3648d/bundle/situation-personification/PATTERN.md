# Situation personification — cast the system as a household to judge fit

## What it is
A diagnostic lens: re-cast a system's parts — components, agents, tools,
checks, rules, even yourself — as **people with roles and temperaments**,
then run five questions to expose redundancy, missing roles, and bad fits.
It works by swapping a *technical* problem for a *social* one, because human
intuition about "who belongs, who's overloaded, who needs supervision" is
far faster and sharper than the same reasoning over boxes-and-arrows. It
*finds* problems and judges fit; it never *proves* — the mechanics remain the
judge.

## Problem it solves
Structural problems that a data-flow diagram hides: a component that
technically works but shouldn't exist, two parts quietly doing one job, a job
nobody's doing, or a new addition that only functions because a second
addition babysits it. These are "fit" problems, and they're invisible when
you reason about data and control flow but obvious when you reason about
staff. It also makes architecture legible to non-implementers (owners,
reviewers) who think in stories.

## How to use it
1. **Cast every part as a role** with a job and a temperament (the flaky
   improviser; the incorruptible inspector who reads only paperwork; the
   clerk who draws plans but never builds).
2. **Walk any proposed change in as a new character** and ask whether they
   belong. Run the five questions:
   - Does anyone **duplicate another's job**? → redundancy / bloat.
   - Is any **chair empty**? → a job nobody is doing.
   - Does any **new hire need a babysitter**? → bad fit / hidden coupling;
     prefer re-onboarding or retiring it over institutionalising the minder.
   - Is anyone **overloaded**? → offload the station, don't blame the worker.
   - **Who is actually malfunctioning vs. who is getting blamed?** → the loud
     failure and the root cause are often different characters.
3. **Check the story against the mechanics before acting.** A convincing
   character narrative can be flatly wrong; use it to locate the problem,
   then confirm in the code/data.

Use it for: should this part exist? does it belong? is it redundant? what job
is nobody doing? and for explaining a structural problem to someone outside
the code. Don't use it for anything you *measure* rather than narrate —
performance, numeric correctness, proofs.

## Fits projects like
Any system with distinguishable parts and an evolving structure — software
architectures, agent pipelines, org/process design. Especially valuable at
component add/remove decisions and when "something feels off but I can't name
it," and wherever a non-engineer stakeholder needs the shape made legible.

## Proven in
Developed in book_podcast_fiction_generator, 2026-07 (AI-run fiction pipeline, one
human owner plus senior and junior AI agents).

**Worked.** A check was added early (T-014, ba7204b), then a *second* ticket appeared
solely to make it behave (T-015: decouple it, stop it crashing a sibling check).
Running Q3, *does the new hire need a babysitter?*, named them as one bad hire plus a
minder, while the data-flow view had the team about to build the babysitter. The
decision flipped to **retiring** the component (T-017, f739452), because a downstream
gate already did its job; the mechanics were checked first. Later castings of the
factory's spec, staff and work in progress produced further design findings, most not
yet proved by a build. An earlier story form, a spec narrating its own gaps, produced
fourteen findings closed in the spec on 2026-07-10 (1757b6c).

**Failed or limited.** The next day a structurally different adversarial and
reader-outcome pass found defects this family missed, including a free cross-check the
gate lacked and a rotation nothing enforced. The castings were descriptive and took
neither an attacker's nor a reader's seat. Casting three ways was still one method. A
follow-up found the company casting strong on roles and blind to pure flow problems.
**Use it alongside lenses of a different kind, not as the only review.**

**Correction to an earlier version of this section.** It said Q1 separately confirmed
the remaining checks did not overlap; no record of that was found, so it is removed.

Basis: commits and project documents listed in the context record, re-read 2026-11-05
by an agent working in this project. One project, no independent reuse.

## Kit (deployable files in `kit/`)
`kit/CAST-AND-FIT.md` — the one-page lens (five questions + how to run it +
when not to). Copy it in; it needs no upkeep — pull it out per-decision,
don't maintain a standing character-map.

## Context record

```json
{
  "schema_version": 1,
  "standard_version": "1.0",
  "id": "situation-personification",
  "origin": {
    "project": "book_podcast_fiction_generator",
    "situation": "A newly added pipeline check needed a second ticket just to make it behave, and the team was about to build that second ticket.",
    "environment": "Raspberry Pi, single git repository, one human owner directing a senior AI agent and junior AI implementers through tickets; an AI-run fiction pipeline with deterministic gates and paid LLM calls.",
    "developed_on": "2026-07-19",
    "development_kind": "invented",
    "development_account": "The five-question household form was first committed on 2026-07-19 (commit b615571) and reshaped into this bundle in ef7ebf5. An earlier story form, where a spec narrates its own gaps, was used here on 2026-07-10 (bbe56a1). The repository records no received copy. 'Invented' means this specific form; casting systems as people is a common idea in general and no novelty over it is claimed. Whether any outside source influenced it is unknown."
  },
  "applicability": {
    "fits": [
      "Deciding whether a component should exist, is redundant or is a bad fit, when a data-flow view is not showing why.",
      "Making a system's structure legible to an owner or reviewer who is not reading the code."
    ],
    "does_not_fit": [
      "Anything you measure rather than narrate: performance, numeric correctness, proofs.",
      "As the only review lens: it describes the system from inside and missed outcome and failure-injection problems."
    ],
    "prerequisites": [
      "The ability to check the story against the actual code or data before acting."
    ],
    "adaptations": [
      "Choose roles and temperaments for your own system's parts; the worked example in the kit is illustration."
    ]
  },
  "evidence": [
    {
      "claim": "Question 3 flipped a decision from building a babysitter ticket to retiring the component.",
      "outcome": "success",
      "project": "book_podcast_fiction_generator",
      "situation": "T-014 added an optional early check, T-015 existed only to fix its coupling; the structural gate already covered the job, so T-017 retired it.",
      "occurred_on": "2026-07-19",
      "locators": [
        "commit ba7204b",
        "commit f739452",
        "commit b615571",
        "tickets/T-017-retire-anchor-check.md",
        "progress/handoff-2026-07-18-all-tickets-landed-ch7-next.md section 14"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "Commits and ticket exist; the handoff records the Q3 reasoning and the retirement.",
        "result": "Confirmed. The earlier claim that Q1 separately confirmed no overlap among the remaining checks was not found in these records.",
        "reason": null
      }
    },
    {
      "claim": "Staff and work-in-progress castings produced further findings on the factory design.",
      "outcome": "success",
      "project": "book_podcast_fiction_generator",
      "situation": "Three castings of the factory spec, staff and work-in-progress item before build.",
      "occurred_on": "2026-07-19",
      "locators": [
        "progress/factory-spec-personification-2026-07-19.md",
        "progress/factory-cast-and-fit-2026-07-19.md",
        "progress/factory-wip-personification-2026-07-19.md"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "The three documents were read in part, including the Q3 finding and the fit discussion.",
        "result": "Findings are recorded; they are design findings, most of them not yet proved by a build.",
        "reason": null
      }
    },
    {
      "claim": "The story form produced fourteen findings that were folded into a spec.",
      "outcome": "success",
      "project": "book_podcast_fiction_generator",
      "situation": "A spec narrated its own gaps; findings SG-1 to SG-14 were closed in the spec the same day.",
      "occurred_on": "2026-07-10",
      "locators": [
        "commit bbe56a1",
        "commit 1757b6c",
        "progress/factory-user-stories.md"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "Commits and the status note exist.",
        "result": "Confirmed as closed in the spec; the document itself notes that closed in the spec does not mean built. This is the earlier story form, not the five questions.",
        "reason": null
      }
    },
    {
      "claim": "The lens family missed real defects that structurally different lenses found the next day.",
      "outcome": "failure",
      "project": "book_podcast_fiction_generator",
      "situation": "An adversarial and reader-outcome pass found a free cross-check the gate lacked, an unenforced rotation and an unverifiable mystery fairness gap, each recorded as missed by the personifications.",
      "occurred_on": "2026-07-20",
      "locators": [
        "progress/factory-adversarial-and-reader-pass-2026-07-20.md"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "The relevant findings and their 'why the personifications missed it' notes were read.",
        "result": "Confirmed. The same document's ADV-3 framing was later retired as wrong, so that pass was not error-free either.",
        "reason": null
      }
    },
    {
      "claim": "The company casting only partly fit the shape of a pipeline.",
      "outcome": "mixed",
      "project": "book_podcast_fiction_generator",
      "situation": "The owner asked whether the casting fit; a follow-up found it strong on roles and blind to pure flow problems.",
      "occurred_on": "2026-07-19",
      "locators": [
        "progress/factory-wip-personification-2026-07-19.md shape question section"
      ],
      "verification": {
        "status": "checked",
        "checked_on": "2026-11-05",
        "checked_by": "Claude Opus 5.5 agent session working in book_podcast_fiction_generator",
        "scope": "The section was read.",
        "result": "Confirmed as that document's own assessment.",
        "reason": null
      }
    }
  ],
  "limits": [
    "A convincing story can be wrong; it locates problems and does not prove them.",
    "Casting several ways is still one introspective method and does not add independent coverage.",
    "All evidence is from one project and was assessed by an agent working in that project, with no independent reuse."
  ],
  "evolution": {
    "origin_state": "aligned",
    "assessed_on": "2026-11-05",
    "locators": [
      "progress/factory-cast-and-fit-2026-07-19.md",
      "progress/factory-adversarial-and-reader-pass-2026-07-20.md"
    ],
    "deltas": [],
    "reason": "The kit matches the five-question lens as last recorded; its 'do not use as the only lens' limit is carried in this bundle's explanation and record. Last recorded project activity is 2026-08-10, so later practice is not observed."
  },
  "assets": [
    {
      "path": "kit/CAST-AND-FIT.md",
      "kind": "checklist",
      "purpose": "One-page lens: how to run it, the five questions, when not to use it and an illustration.",
      "adaptations": [
        "Cast your own system's parts; do not keep a standing character map."
      ],
      "dependencies": [],
      "context_ref": "PATTERN.md#kit-deployable-files-in-kit"
    }
  ]
}
```
