# Decision ledger — append-only owner decisions, four frames, propose-and-STOP

## What it is
One append-only file (`decisions.md`) holding every owner-level decision. Any
change touching the owner's taste, money, autonomy, or an expensive-to-reverse
property is written there as a PROPOSAL with lettered options and a marked
default — and the agent **STOPS**. Only an explicit owner answer (recorded in
place as ACCEPTED/REJECTED, dated) unblocks the work. Entries use four frames:
**Essence** (what is being decided, once) / **Analogy** (a human-world
parallel) / **Impact + reversibility** (how far it reaches; can it be undone)
/ **What the architecture points at** (which option the system's own design
favors).

## Problem it solves
Two opposite failures: agents quietly making taste/money/autonomy decisions
the owner never saw; and decisions being relitigated every session because
nobody wrote down what was decided, why, or that it was CLOSED. Append-only
matters: editing closed history destroys the ledger's evidentiary value.

## How to use it
1. Trigger test — before acting, ask: does this change what the owner
   experiences, spends, or can't easily undo? If yes → ledger proposal +
   STOP. A session may SURFACE a pending proposal but must not act on it.
2. Write options (A/B/C) with a default; the four frames force honest
   framing — especially "impact + reversibility," which separates one-way
   doors from trivia.
3. The owner answers in place; the entry is stamped and never edited again.
   Corrections are NEW entries superseding old ones by reference.
4. Historical entries are never retrofitted to new formats (append-only
   applies to form, not just content).
5. Cross-link: STATUS files and handoffs cite ledger timestamps as evidence —
   and readers verify against the ledger before repeating a claim about it.

## Fits projects like
Any owner + AI-agent project (the STOP is what keeps the human sovereign);
also human teams wanting decision archaeology. Pairs with trust-ladder
(graduation rules are ledger decisions) and handoff-discipline (the ledger is
the authority handoffs cite).

## Proven in
Origin project, 2026: dozens of entries governing VCS adoption, live-backend
authorization, an AI-provisional adjudicator (a CON-rule exception argued in
four frames and accepted), spend budgets, and the autonomy graduation rule —
each unblocking work only after an explicit owner answer. The four-frame
format was itself an owner request recorded as a ledger decision. Failure
case that validates the STOP: an agent once proposed AND executed in the same
turn — the owner reverted it, and the rule "a question is not a dispatch" is
now protocol.

## Kit (deployable files in `kit/`)
`kit/decisions_TEMPLATE.md` — the ledger header rules + a four-frame entry template.
