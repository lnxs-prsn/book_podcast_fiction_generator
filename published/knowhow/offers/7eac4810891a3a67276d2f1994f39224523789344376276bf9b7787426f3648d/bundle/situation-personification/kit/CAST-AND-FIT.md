# CAST & FIT — a one-page lens for analysing a system as a household

A reusable diagnostic. When a system feels off and boxes-and-arrows aren't
showing why, re-cast it as **people with roles** and run the five questions.
It works because it swaps a technical problem for a social one, and human
intuition about "who belongs, who's overloaded, who doesn't fit" is fast and
sharp. It is a way to **find** problems and judge **fit** — never a proof.
Always check the story against the actual mechanics before acting on it.

## How to run it

1. **Cast every part as a role.** Each component, agent, tool, check, rule —
   and yourself — becomes a person with a job and a temperament (e.g. a
   gifted-but-inconsistent improviser; an incorruptible inspector who reads
   only the paperwork, never the work itself; a clerk who draws plans but
   never builds).
2. **Walk any proposed change in as a new character** and ask whether they
   belong in the household.

## The five questions

1. **Does anyone duplicate another's job?** → redundancy / bloat.
2. **Is any chair empty?** → a job nobody is doing (a missing component).
3. **Does any new hire need a babysitter?** → bad fit / hidden coupling. A
   part that needs a second part to make it work was mis-onboarded; prefer
   re-onboarding or retiring it over institutionalising the minder.
4. **Is anyone overloaded?** → a station carrying too much; fix by offloading,
   not by blaming the worker.
5. **Who is actually malfunctioning vs. who is getting blamed?** → the loud
   failure and the root cause are often different characters.

## When to use it / when not

- **Use for:** should this component exist? does it belong? is it redundant?
  what job is nobody doing? and explaining a structural problem to someone who
  doesn't live in the code.
- **Don't use for:** anything you *measure* rather than narrate — performance,
  numeric correctness, proofs. A convincing character story can be flatly
  wrong; the mechanics are the judge.

## Worked example (illustration)

A pipeline gained an early "inspector" check. Then a second change appeared
*only to make the inspector behave* — separate it from a sibling check, stop
it crashing the whole stage when an input was missing. Question 3 — *does the
new hire need a babysitter?* — named it: the inspector plus its minder were
**one hire done in two clumsy steps.** The flow diagram had the team about to
build the babysitter. The character view said a hire that needs a minder was a
bad hire — and a later-stage check already caught the same thing — so they
**retired the inspector** instead. Question 1 confirmed the remaining checks
didn't overlap: the system wasn't bloated, it had one bad hire. The lens
changed the decision; the verified mechanics confirmed it was safe.

*One page, no upkeep. Pull it out per decision; don't maintain a standing
character-map of the whole system.*
