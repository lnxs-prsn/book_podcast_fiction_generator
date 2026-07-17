# Review checklist — run this before reporting anyone's work as done

Copy into your repo; run top to bottom whenever you review an agent's (or
your own) completed work. The one rule behind every line: **a log is a claim,
not proof.**

1. **Re-run the acceptance checks yourself.** Same commands, your shell, from
   a clean starting state. Green in their log ≠ green.
2. **Diff vs the promise.** `git diff <base>` touches ONLY the declared
   write-set. Anything outside it: revert first, discuss second.
3. **Attribution present.** Commit message format + trailers
   (`Ticket:`, `Implemented-by:`) per conventions.
4. **Failure claims get re-diagnosed.** If work stopped on an error, verify
   the error is what they said it is — and whether it pre-existed their
   change (run the failing thing against the untouched baseline).
5. **Fail-first for new checks.** Anything claiming to detect X must be shown
   detecting a planted X before you trust its green.
6. **Claims you repeat, you verify.** Before carrying any statement into a
   handoff/report ("decision pending", "N tests"), check the authoritative
   source at that moment.
7. **LLM-derived data is verified before it becomes state.** Quotes
   substring-checked against sources; generated recipes/tests executed;
   unverifiable output rejected and logged, never stored.
8. **The suite after the merge.** Integration is serial; full affected suites
   green on the main branch after EACH merge before the next.
9. **Report faithfully.** What passed, what was skipped, what you did not
   check. An honest gap beats a confident summary.
