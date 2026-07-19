# CAST & FIT — a one-page lens for analysing a system as a household

A reusable diagnostic. When a system feels off and boxes-and-arrows aren't
showing why, re-cast it as **people with roles** and run the five questions.
It works because it swaps a technical problem for a social one, and human
intuition about "who belongs, who's overloaded, who doesn't fit" is fast and
sharp. It is a way to **find** problems and judge **fit** — never a proof.
Always check the story against the actual mechanics before acting on it.

## How to run it

1. **Cast every part as a role.** Each component, agent, tool, check, rule,
   and even yourself becomes a person with a job and a temperament (e.g. the
   Writer = a gifted but inconsistent improviser; the Gate = an incorruptible
   bouncer who reads only paperwork; the Senior = a clerk-of-works who draws
   plans but never builds).
2. **Walk any proposed change in as a new character** and ask whether they
   belong in the household.

## The five questions

1. **Does anyone duplicate another's job?** → redundancy / bloat.
2. **Is any chair empty?** → a missing component (a job nobody's doing).
3. **Does any new hire need a babysitter?** → bad fit / hidden coupling. A
   component that needs a second component to make it work was mis-onboarded;
   prefer re-onboarding or retiring it over institutionalising the minder.
4. **Is anyone overloaded?** → a station carrying too much (fix by offloading,
   not by blaming the worker).
5. **Who is actually malfunctioning vs. who is getting blamed?** → the loud
   failure and the root cause are often different characters.

## When to use it / when not

- **Use it for:** should this component exist? does it belong? is it
  redundant? what job is nobody doing? and for explaining a structural
  problem to someone who doesn't live in the code.
- **Don't use it for:** anything you *measure* rather than narrate —
  performance, numeric correctness, proofs. A convincing character story can
  be flatly wrong; the mechanics are the judge.

## Worked example — the anchor-check decision (2026-07)

The pipeline gained an **Anchor-Inspector** (T-014) to confirm a required
prop was on stage. Then a second ticket (T-015) appeared *solely to make the
Inspector behave* — separate his booth from the Proofreader's, stop him
pulling the fire alarm when a form was missing.

Running Q3 — *does the new hire need a babysitter?* — named it: the Inspector
plus his minder were **one hire done in two clumsy steps.** The
boxes-and-arrows view had us about to build the babysitter (T-015). The
character view said a hire that needs a minder was a bad hire, and the Gate
already caught the missing prop downstream anyway — so we **retired the
Inspector** instead of institutionalising the minder. Q1 also confirmed the
remaining watchers (Physician=state, Gate=product paperwork, Proofreader=prose
words, Night-Watchman=tool behaviour) don't overlap — the household wasn't
bloated, it had one bad hire. The lens changed the decision; the mechanics
(the verified regression) confirmed it was safe.

*One page, no upkeep. Pull it out; don't maintain a standing character-map.*
