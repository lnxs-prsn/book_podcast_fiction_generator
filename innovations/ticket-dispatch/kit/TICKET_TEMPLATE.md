# TICKET: <imperative title — what will be true when this is done>

```
Mode: alone | group
Worktree: <path + branch — group only; created by the coordinator, not you>
Write-set: <exact files/globs the implementer may create or modify>
Hot-files: <shared files this ticket is allowed to touch, or "none">
Upstream (preconditions — author dry-ran that EACH exists/holds): <the
  paths, tools, test harnesses, fixtures, and source fields this ticket
  ASSUMES are already present before building — e.g. "the `<module>` test
  suite exists", "`<config file>` carries the `<field>` block". A
  precondition you did not personally run is a STOP waiting to happen.>
Downstream (consumers to re-verify — looked up in the producer/consumer
  registry): <for EVERY file/surface in the write-set, who depends on it and
  must be re-checked AFTER the change — e.g. "`<shared module>` → re-run
  `<consumer ticket>`'s acceptance + the regression suite over that surface".
  "none" only if the surface is a genuine leaf. A shared surface with an empty
  Downstream is an authoring error.>
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

## 3. Acceptance (numbered; ALL must pass. The author has EXECUTED every item
##    that can run at authoring time and pasted its OBSERVED output — not a
##    predicted "expected result". Tag each item [RUN@HEAD] or [POST-BUILD].
##    See `10-how-to-write-tickets.md` T-6/T-7/T-8.)

1. [RUN@HEAD] <command reading EXISTING artifacts/state → the OBSERVED output,
   pasted here, run against HEAD before dispatch. If it does not already produce
   the PASS result, the ticket is NOT ready: fix the premise, or supply a correct
   fixture the PASS-case needs (T-8) — never predict a PASS you did not observe.
   Both T-024 and T-025 bounced because this item was predicted, not run.>
2. [POST-BUILD] <exercises code THIS ticket creates (cannot exist yet) →
   predicted result + WHY it can't be pre-run. This is the implementer's first
   checkpoint. A [POST-BUILD] tag must never hide a check that was actually
   runnable at HEAD.>
3. [RUN@HEAD] <existing test suite → green, with the OBSERVED count.>
4. <git status shows ONLY the write-set changed — the ticket's own
   implementer-log section is exempt (standing rule) and need not be listed>
5. <DOWNSTREAM RE-VERIFY — mandatory whenever the write-set touches a shared
   surface: the tool regression suite is green, AND each consumer named in
   the Downstream header has its acceptance re-run green. A downstream
   regression must fail HERE, in this ticket, not be discovered by the next
   one. Omit this line only if Downstream is a true "none".>

## 4. Commit

`<area>: <exact message>` + trailers per conventions
(`Ticket:`, `Implemented-by:`).

## 5. Constraints

<Environment limits (machine, no installs, etc.). Never touch <secrets/state
paths>. Zero paid calls unless §header budgets them. On ANY failure: stop at
that step, log it in §6, leave the tree coherent — do not improvise
alternative designs.>

## 6. Implementer log (append below; never delete the ticket body)

Appending here is always allowed and is exempt from the write-set / "only the
write-set changed" acceptance (standing rule) — this section is the one
implicit write target every ticket has.

- [ ] <step>
- [ ] acceptance 1–N
- [ ] commit
