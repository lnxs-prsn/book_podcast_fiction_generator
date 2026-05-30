# Planning Directory

This directory tracks all design and implementation planning for harnessv3, organized by phases and passes.

## Structure

```
planning_dir/
  phase_01/
    pass_01.md
    pass_02.md
    ...
  phase_02/
    pass_01.md
    ...
```

## Rules

- **One phase at a time.** Do not start a new phase until the current phase is resolved.
- **Every phase is self-contained.** A phase covers one focused area of work. It should not depend on work planned in a future phase.
- **Passes fix problems within a phase.** If a phase has an issue, add a new pass to address it. Keep iterating with passes until the phase is clean.
- **Do not mix phases.** Problems found in phase N are fixed by passes in phase N, not by starting phase N+1 early.

## Phase folder naming

`phase_NN` — zero-padded two-digit number, e.g. `phase_01`, `phase_02`.

## Pass file naming

`pass_NN.md` — zero-padded two-digit number inside the phase folder, e.g. `pass_01.md`, `pass_02.md`.

## Pass file format

```
# Pass N — <one-line description>

## Goal
What this pass is trying to accomplish.

## Changes
What was done.

## Problems found
Any issues discovered during this pass.

## Status
[ ] In progress  /  [x] Resolved
```
