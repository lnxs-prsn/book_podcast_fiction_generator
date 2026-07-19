# ROOT-CAUSE LADDER — climb before you patch

Run this whenever a failure **bounced, recurred, or "shouldn't have
happened."** It stops whack-a-mole by moving the fix up to the layer that
*generates* the symptom.

## The two questions

**1. Instance or class?**
- *Instance:* this one occurrence.
- *Class:* the category that keeps producing occurrences.
- If it's a class, the real fix is a **mechanism that makes the whole
  category impossible** — not a patch to this case. Name both; ship the class
  fix; keep the instance fix as its test/fixture.

**2. What layer does this defect actually live in?**
Walk up until you reach the highest layer you can change:

```
the output / behaviour that failed
   ↑
the tool or component that produced it
   ↑
the spec / work-order / config that drove the tool
   ↑
the author of that spec (and how they verified it)
   ↑
the process that governs authoring & verification
```

Fix at the highest reachable rung — that's where the category dies.

## The prior: expect one layer up

The loud failure names a suspect. The root cause is usually the thing that
**fed** that suspect. Check the feeder before blaming the actor. In
self-modifying / agent-run systems, the bugs cluster in the
**change-governance** layer (how work is authored, verified, handed off) — the
highest-leverage and least-watched place — while attention stays on the
production layer where they merely surface.

## The "stopped too early?" check

Before you accept a fix, ask: **does it prevent the next, differently-masked
instance?**
- Yes → you climbed to the right rung.
- No (it only stops this exact symptom) → keep climbing; you patched an
  instance and left the class alive.

Pairs with **cast-and-fit**: personification finds *which character* is at
fault; this ladder finds *which layer*.
