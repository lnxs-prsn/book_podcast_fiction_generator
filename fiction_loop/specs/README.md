# CODEABLE PIPELINE SPECS

This directory is implementation-ready specs for the part of the fiction_loop pipeline
that involves no language understanding or creative generation — only arithmetic, JSON
manipulation, and lookups. It's a different kind of artifact than `fiction_loop/agents/`:

- **`agents/*.md`** — prompts an LLM subagent interprets loosely, every chapter.
- **`specs/*.md`** (this directory) — a specification precise enough that a programmer
  (or a code-generation tool) can implement it once as a plain function, with no
  interpretation left to make at call time. If a spec here still requires a judgment
  call, it isn't done — see the two fixes in `assembler_template.spec.md` for what
  "not done yet" looked like before being resolved.

## Boundary rule

If a step can be fully determined from already-structured data via arithmetic, table
lookup, or string templating with fixed boundaries — it belongs here. If it requires
reading or producing free-form natural language whose meaning isn't already extracted
as structured data, it stays an agent spec. See `core/field_registry.md` and
`core/chapter_type_contract.md` for the underlying data contracts both sides consume —
**specs here and prompts in `agents/` read the same core/ contract files**. There is one
source of truth for shape, variants, ordering, and field ownership regardless of which
side of the code/AI line consumes it.

## What's in scope here

| Spec | Supersedes (fully or in part) | Status |
|---|---|---|
| `deterministic_pipeline.spec.md` | `agents/orchestrator.md`, `agents/fetcher.md`, `agents/updater.md`, most of `agents/consistency_checker.md`, the DECISION LOGIC section of `agents/extractor.md` | Implementable — see the DRIFT NOTE at its top first: extractor DECISION LOGIC was rewritten (STEP A–E scheduler), CR3 is unblocked (prerequisite graph authored + live), C4 is exact enum equality post-assembly. Not yet implemented as code. |
| `assembler_template.spec.md` | The mechanical half of `agents/assembler.md` | **Unblocked** (see banner at its top): §5 lookup works (24 canonical-labelled rows), canonical_* fields authored on all 24 cards, assembler.md corrected. Implementable; must also append the HARD RULES block. Not yet implemented as code. |
| `intake_factory.spec.md` | The generalization: knowledge book in → templates + state derived → loop runs. Two-layer architecture (chassis vs pedagogy packs), 3 automated verifications (fidelity/logic/correspondence), propose-and-correct owner model (default-forward, taste flights, decisions ledger — never interview). | Design complete 2026-07-03; build list inside. Sequenced AFTER book-1 validation. |
| `pipeline_fixes.spec.md` | Cross-cutting: bridge scripts, state init, `extractor.md` DECISION LOGIC, pointer schema, checker staging, living-doc ownership | 2026-07 audit of everything currently broken, ordered by severity, plus F14–F17 (new design rules from owner decisions). **All owner calls resolved and F1–F17 APPLIED** (2026-07-02/03) — this row is now historical; see the STATUS banner in the file. |

## Sourcing rule for domain content

Any content added to `core/` reference docs that represents Pólya's actual method
(operation definitions, wrong-approach types, ordinary-life echoes, or anything else
attributed to *How to Solve It*) must be checked against the source text before being
written — not reconstructed from a model's internal knowledge of the book. A prior
attempt to author two missing Ordinary Life Echo rows from memory was reverted for
exactly this reason (see `core/field_registry.md`, Known orphans). This applies
regardless of who or what is doing the authoring — human or AI.

## What stays AI, and why (not covered by any spec here)

- **Writer** — all of it. Prose generation.
- **Extractor's prose-reading sections** (everything except DECISION LOGIC) — reading
  finished chapter prose and pulling structured meaning out of it. No code substitute.
- **Consistency Checker V3 and A2** — judging "is this framing explanatory" and "does
  this text show interiority." Genuine semantic/stylistic reads, kept as a small,
  narrowly-scoped LLM call rather than folded into the mechanical check function.
- **Assembler's new-character generation** (name/occupation/city/situation) — generative
  by nature, unless a curated name/city pool + random draw is an acceptable trade for
  less variety (a legitimate all-code alternative, not attempted here).
- **CR3 (prerequisite check)** — RESOLVED 2026-07-03: `prerequisite` exists on every
  concept card (owner-approved graph, D5) and the check is live in
  `consistency_checker.md`. Fully mechanical — implement per the DRIFT NOTE in
  `deterministic_pipeline.spec.md`.
