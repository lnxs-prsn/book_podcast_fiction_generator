# Spec-writing method for AI-implemented projects (M-1..M-17)

## What it is
A method for writing specifications that AI agents implement without further
design input. Seventeen numbered rules in four groups: shape of the spec,
shape of the work, shape of the data, shape of the collaboration. The origin
project keeps the full method as a standalone file (`09-how-to-write-specs.md`)
— copy that file alongside this summary when adopting.

## Problem it solves
AI implementers fail by *initiative*, not disobedience: they add databases,
caches, and "improvements" nobody asked for, skim monolithic specs, and call
things done on an impression. Prose specs can only be agreed with; they can't
be audited.

## How to use it
The load-bearing rules, in practice order:
- **M-1** Number every requirement with normative force (MUST/SHOULD/MAY +
  stable IDs like `INV-3`). Tests and commits reference IDs — coverage becomes
  a query.
- **M-2** One concern per file, sized for a context window, declared reading
  order. An implementer loads 2–3 files, never a monolith.
- **M-3** A tiny constitution of expensive-to-reverse invariants; everything
  defers to it; change it explicitly before violating it.
- **M-4** Name what NOT to build, in every file. Scope creep is the AI failure
  mode; "Do NOT build" lists are the fence.
- **M-5** Acceptance criteria everywhere — "done" is a checklist verdict,
  never an impression.
- **M-6/M-7** Phases are a trust ladder with data-answerable graduation
  signals (autonomy earned, never scheduled); work decomposes into atomic
  passes — one sitting, independently verifiable, clean tree, claimed by
  committing the STATUS change.
- **M-8/M-9** Externalize ALL build state (STATUS keyed to IDs where done =
  commit hash; write-ahead journal; session start/end rituals) and keep one
  flight recorder OUTSIDE the repo — the record of failures must not live
  inside the thing that fails.
- **M-15/M-16/M-17** Write the user manual BEFORE the implementation and
  derive numbered stories from it; on existing systems the manual diff
  classifies the change (a "refactor" needing manual edits is a behavior
  change under a false name); write stories for every role the project will
  meet — the maintainer's stories are never optional.
The method is append-only: new rules get new numbers; old numbers never change
meaning.

## Fits projects like
Anything AI-implemented from specs, solo-owner projects where sessions die and
restart, multi-agent builds — and, honestly, human teams with high turnover.
Overkill for throwaway scripts.

## Proven in
Origin project, 2026: two full spec packages (feature1/feature2, ~20 component
specs with TICK/RUB/GOLD/FAIL-style IDs) implemented across many disposable AI
sessions with a 1252-test estate; a 28-issue spec audit fixed by mapping
issue→ID→file; phase gating (Q4+ blocked on graduation signals) successfully
prevented premature autonomy builds. The method survived contact with three
different AI implementers.

## Kit (deployable files in `kit/`)
`kit/09-how-to-write-specs.md` — the FULL method, copy-ready; this PATTERN file is only the summary.
