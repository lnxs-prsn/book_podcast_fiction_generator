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
Origin project, 2026-07 (an AI-run content pipeline): a component was added
as an early check, then a *second* ticket appeared solely to make the first
behave (decouple it, stop it crashing a sibling check). Running Q3 — *does
the new hire need a babysitter?* — named them as one bad hire plus a minder;
the data-flow view had the team about to build the babysitter. The lens
flipped the decision to **retiring** the component (a downstream check already
covered its job), which the verified mechanics then confirmed was safe. Q1
independently confirmed the remaining checks didn't overlap — the system
wasn't bloated, it had one mis-onboarded part. The lens changed the action;
the mechanics validated it.

## Kit (deployable files in `kit/`)
`kit/CAST-AND-FIT.md` — the one-page lens (five questions + how to run it +
when not to). Copy it in; it needs no upkeep — pull it out per-decision,
don't maintain a standing character-map.
