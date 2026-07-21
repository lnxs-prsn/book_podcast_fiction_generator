# EXPLORATION_PREFERENCES.md — how the owner wants problems explored

**Audience: every AI agent in this repo.** This file exists so agents do not
have to be re-taught the owner's thinking style each session. Read it when a
task involves *understanding or deciding*, not just executing. Apply it
**situationally** (see §Scaling) — it is a toolkit, not a mandatory checklist.

## The one-line why

The owner runs a **systems-level differential diagnosis**: exhaust the
*problem space* before touching the *solution space*, interrogate each problem
along a fixed set of axes, and keep auditing the quality of the thinking
itself. Solutions are committed only after that — and even then: *list, don't
resolve* first, and record each decision.

Explain **to build the owner's own understanding**, not to close the ticket.
An answer that resolves the item but leaves the owner unable to reason about it
has failed. Show the diagnosis, not just the conclusion.

## The axes (the diagnostic toolkit)

Grouped by purpose. Not every axis fits every problem — pick the ones that
carry signal.

**1. Define & decompose**
- What exactly are we resolving? Pin the precise scope.
- What is each issue *in essence* about? Strip to the core.

**2. Map the system (how things relate)**
- Do any of these issues overlap / share structure?
- Does solving one *resolve or intensify* others? (second-order effects)
- Is there a chronological / sequencing order among them?
- Do they compete for the same resource, or depend on the same thing?

**3. Weigh & classify**
- Why should we care? (stakes / motivation)
- How big is the impact on the whole? (proportional / systemic weight)
- Is it binary or a spectrum (constant vs. gradient)?
- Classify by difficulty: *small design decision* vs. *needs a deep look* —
  and when asked to classify, **list, do not solve yet**.

**4. Leverage before invention**
- What do we already have that points to a solution? Reuse existing
  mechanisms/decisions before inventing new ones.

**5. Audit the thinking itself (meta)**
- Novelty check: are these fresh perspectives or old ones re-run? List
  problems that never got a *different* look.
- Quantify: what % of the problem set do we actually understand clearly?
- Reflect back: restate each issue in plain words and ask "did I understand
  this correctly?" — verify comprehension before proposing.
- Reject false binaries: ask "why not both A and B?" — seek synthesis.
- Sufficiency check: when one rule/answer can't cover it, say so and look
  deeper rather than paper over.
- Mechanism probe: ask "is there a structure *forcing* this / why is it this
  way?" — find the enforcing cause, not just the symptom.
- Reconcile models: when reality differs from the owner's stated mental
  model, surface the gap explicitly ("I thought X — here's why it's actually
  Y") instead of silently correcting.

**6. Trace origin & fit (archaeology)** *(added 2026-07-21, battle-tested on the
single-source smell — these questions did a lot of work, so they are kept)*
- **Origin — original or bolted on?** Is this baked into the founding design or added
  by a later patch? (git-blame the design intent, not just the line.) Original problems
  are load-bearing; add-ons are often removable.
- **Fractal or anomaly?** Is the problem's shape the *same as the system's* shape? If it
  recurs elsewhere, it is a **class** (there is a lot more of it), not a one-off — and
  the fix should be a principle, not a patch. If it appears once, it is an anomaly.
- **Where in the whole does it fit?** Which seam / boundary / layer does it sit on? A
  problem on a known architectural boundary is usually that boundary's central tension,
  not a defect — locate it before "fixing" it.
- **Who holds it — human or machine? Can that holder forget?** Name the actor a rule
  relies on. If the actor is memory ("maintainer remembers"), the rule is only as strong
  as vigilance — a smell.
- **Is it me, or could a machine verify it?** Separate the irreducible judgment (what
  only a human/agent can *recognize*) from what a machine could check fast — e.g. a
  stored number / content-hash fingerprint that fails a cheap test when the source
  changed but the derived copy didn't. Push everything downstream of the judgment onto
  the machine; keep only the recognition manual.

## Flow

Diverge on the problem (run lenses) → converge (group, quantify, classify) →
*then* diverge on options → converge (recorded decision). One item at a time
when walking a set; **propose-and-correct** — nothing gets applied to files
until the owner rules. Record outcomes where the repo expects them (e.g.
`fiction_loop/human_decision.md` for design forks, the handoff for state).

## Scaling — decide how much of this to run

Agents SHOULD right-size the diagnosis. Judge by **reversibility**, **blast
radius** (how many files/decisions/chapters downstream), and whether the
result **becomes canon**.

- **Full pass** (most axes + list-don't-solve + recorded decision):
  multi-issue design reviews, forks that become canon, cross-cutting or
  chassis (`fiction_loop/`) changes, pre-build passes, anything hard to
  reverse.
- **Light pass** (essence → stakes → reuse-first → reflect-back, then
  propose): a single scoped design decision, ticket scoping, a bounded
  trade-off.
- **Skip** (just answer): trivial / reversible / mechanical work, factual
  lookups, low-risk single-file edits, or when the owner has already supplied
  the frame. Do not perform the ritual for its own sake — that wastes tokens
  too.

The meta-audit axes (§5) are the first to drop on light tasks and the last to
drop on deep ones. When unsure which tier applies, state your read in one line
and proceed — do not stop to ask unless the choice changes the outcome.

## Named lineage (for agents who want the map)

Differential diagnosis (whole-flow match) · systems thinking / leverage points
(Meadows) · 5 Whys / root-cause (TPS) · Feynman technique (reflect-back) ·
Socratic / first-principles (essence, false-binary) · Double Diamond (diverge/
converge) · critical-path & dependency analysis · risk–impact–effort triage.
