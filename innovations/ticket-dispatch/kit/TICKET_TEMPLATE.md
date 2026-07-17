# TICKET: <imperative title — what will be true when this is done>

```
Mode: alone | group
Worktree: <path + branch — group only; created by the coordinator, not you>
Write-set: <exact files/globs the implementer may create or modify>
Hot-files: <shared files this ticket is allowed to touch, or "none">
State-access: none | reads <what> | writes <what>
Paid-calls: forbidden | budgeted via <wrapper + cap key>
```

Read <your protocol file> and <your git conventions file> first.
Repo root = the directory containing this file.

## 1. Problem (preconditions verified <date> by the ticket author)

<What is broken/missing, with FACTS the author personally verified: exact
file:line locations, the exact failing command + its output signature, proof
the proposed mechanism works (author ran it). A precondition you did not
dry-run does not belong here.>

## 2. Fix

<Exact changes: which files, what logic, what to preserve, what NOT to do.
Include code snippets for anything you'd rather not have improvised.>

## 3. Acceptance (numbered; ALL must pass; author has dry-run each one's
##    preconditions)

1. <machine-checkable command → expected result>
2. <existing test suite → green, with expected count>
3. <git status shows ONLY the write-set changed>

## 4. Commit

`<area>: <exact message>` + trailers per conventions
(`Ticket:`, `Implemented-by:`).

## 5. Constraints

<Environment limits (machine, no installs, etc.). Never touch <secrets/state
paths>. Zero paid calls unless §header budgets them. On ANY failure: stop at
that step, log it in §6, leave the tree coherent — do not improvise
alternative designs.>

## 6. Implementer log (append below; never delete the ticket body)

- [ ] <step>
- [ ] acceptance 1–N
- [ ] commit
