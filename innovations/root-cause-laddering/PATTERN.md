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
Origin project, 2026-07 (AI-run pipeline, human owner + senior/junior agents):
an investigation that opened on "the generative model only succeeds ~40% of
the time" laddered up through the repair mechanism, to the work-orders that
kept bouncing, to the *author* of those work-orders drawing from memory
instead of verifying — the actual defect was in the authoring process, not the
model. Separately, a regression was diagnosed as **class over instance**: the
one-off fix (decouple two coupled checks) was superseded by removing the badly
coupled component entirely, and the durable fix was named as a missing
regression net for the tooling layer — each a rung above where the bug first
showed. The recurring finding across the session: the defect sat one layer up,
in the machinery that changes the machine.

## Kit (deployable files in `kit/`)
`kit/LADDER.md` — the two questions, the climb, and the "stopped too early?"
check, on one page. Run it at every bounce/recurrence.
