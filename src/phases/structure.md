# Phases Directory

Each phase gets its own directory: `phase_01/`, `phase_02/`, etc.

## Directory layout

```
phases/
  phase_01/
    passes.md       — pass log: what each commit changed and what it may have broken
    ai_context.md   — full picture for the AI: everything done this phase, for fast diagnosis if something breaks
  phase_02/
    passes.md
    ai_context.md
```

## passes.md format

```
## Pass N — <one-line description>
Commit: <hash>
Changed: ...
May have broken: ...
```

## ai_context.md purpose

Written for the AI, not for humans. Contains:

- What the phase goal was
- Every file touched and why
- Key decisions made
- Known risks or fragile spots left behind
- What to check first if something breaks
