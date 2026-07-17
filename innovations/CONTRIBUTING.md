# CONTRIBUTING — how this toolbox is governed

This folder preaches machine-enforced laws and evidence-before-trust; it is
governed by the same standards. Four rules; a checker (`check.py`, once built)
enforces the mechanical ones.

## 1. Admission bar — what may enter

A pattern enters ONLY when all three hold:
- **Invented or materially refined** in a real project (not imported theory).
- **Used successfully** — it survived contact with real work at least once.
- **Evidence citable** — the "Proven in" section names dated, checkable facts
  (commits, incidents, test counts), including the failures that forged it.

Speculative ideas, untested improvements, and "this should work" designs are
NOT patterns — but they need a home, not a wall: keep them in the origin
project's own docs/tickets until they earn evidence, or add a one-line entry
to the README's "Incubating" list (an idea there has no directory rights —
it graduates to a pattern only by passing this bar).

## 2. Structure contract — the only allowed shapes

- `innovations/README.md`, `innovations/CONTRIBUTING.md`, optional
  `innovations/check.py` — the ONLY files at folder root.
- One directory per pattern: `<kebab-name>/PATTERN.md` + `<kebab-name>/kit/`
  with at least one deployable file.
- Every `PATTERN.md` has AT LEAST these six sections, in this order:
  `## What it is` · `## Problem it solves` · `## How to use it` ·
  `## Fits projects like` · `## Proven in` · `## Kit (deployable files in
  `kit/`)`. Additional sections are allowed after them — the six are a
  minimum contract for checkability, not a ceiling on growth.
- Kits are GENERIC: no origin-project names/paths outside explicitly labeled
  "origin project" evidence notes; project specifics become `<placeholders>`.
- Every pattern directory has a row in README's index; no index row without a
  directory.

## 3. Add procedure

1. Check the admission bar (§1) honestly — evidence first.
2. Create the directory per §2; write PATTERN.md; extract/genericize the kit.
3. Verify kit genericness: grep kits for origin-project identifiers; zero
   hits outside labeled evidence notes.
4. Add the README index row (+ pairings line if it composes with others).
5. Run `check.py` if present. One commit, `docs:` area.

## 4. Evolve-sync trigger (the drift killer)

When a LIVE method in the origin project changes in a way that alters the
pattern's advice — a conventions rule rewritten, a protocol invariant added,
the hook's contract changed — the SAME sitting updates the corresponding
kit/PATTERN here, or records the divergence in the pattern's "Proven in" as a
known delta. A kit that silently disagrees with the living original is the
staleness failure this whole toolbox exists to prevent. (Same rule mirrored
in the origin repo's handoff discipline: found staleness gets recorded where
the next reader will look.)

Removal follows the same bar in reverse: a pattern that real use DISPROVED is
not deleted — its "Proven in" gains the counter-evidence and, if fully dead,
the pattern moves to a `retired/` subfolder with the reason. Failed patterns
are evidence too.
