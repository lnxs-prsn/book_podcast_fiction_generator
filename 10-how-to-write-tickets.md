# 10 — How to Write Tickets for AI Implementers

Status: settled · **Portable: this file is self-contained — lift it into any
repo unchanged.** Companion to `09-how-to-write-specs.md`: specs design the
system; tickets dispatch bounded changes to it. Where the spec method has
M-numbers, this has T-numbers (append-only). The deployable skeleton is
`innovations/ticket-dispatch/kit/TICKET_TEMPLATE.md`; this file is the *method*
behind it.

> **Cue:** you are about to hand a scoped change to an AI implementer that will
> execute it cold — possibly a cheaper model, possibly a different agent each
> time — while you (senior/human) gate quality but don't write the code. A bad
> ticket costs a wasted run, an amend, and a re-dispatch.

The method has four parts: shape of the **ticket**, of the **preconditions**, of
the **acceptance**, of the **collaboration**. The acceptance part (T-6…T-9) is
the spine — it is where tickets fail in practice.

## A. Shape of the ticket

- **T-1 — One ticket, one atomic change, clean tree at the end.** Independently
  completable in one sitting, independently verifiable. The **Write-set** is an
  exact promise; a commit outside it is reverted without discussion. (Mirrors
  spec M-7.)
- **T-2 — Hard scope + STOP-not-improvise.** Name what NOT to do. On ANY
  ambiguity or red check, the implementer stops and logs — never improvises a
  redesign. A junior stopping at a red check is the system working, not failing
  (see T-11). AI implementers fail by initiative, not disobedience (spec M-4).
- **T-3 — Every claim carries its evidence.** A fact in the ticket is a
  `file:line`, or the exact command *and its output*. "Verified" without the
  observed result is a wish. A precondition or premise you did not personally run
  does not belong in the ticket.

## B. Shape of the preconditions (Upstream)

- **T-4 — Dry-run every precondition against HEAD before dispatch.** Does the
  binary exist, is the dependency declared, does the path resolve, does the field
  hold the value you assumed? Grep first, dispatch second.
- **T-5 — Verify against the ARTIFACT, not your model of it.** The dominant
  failure mode: the author *pictures* the state instead of *opening* it. State
  moves — the pointer advances, the arc advances, the cast grows, a schema gets
  renamed. Read the current file at HEAD, not the state you remember.
  *(Case law: T-024 assumed `brief.chapter == pointer` — the Updater had already
  advanced the pointer, one `read master_state.json` would have shown it. T-025
  assumed a city name appears in prose — the chapter was indoors, one `grep`
  would have shown 0. Both were one-command checks against a live artifact,
  skipped in favor of a mental model.)*

## C. Shape of the acceptance (the spine)

- **T-6 — Acceptance is EXECUTED, not predicted.** Every acceptance item that can
  run at authoring time (it reads existing artifacts/state) MUST be run against
  HEAD, and the ticket carries its **observed output** — never an "expected
  result". An acceptance block with no observed output is not dispatch-ready.
  This is spec M-5 ("done is a verdict, never an impression") *and* the project's
  own LAW-15 "evidence it fires" — the standard the ticket imposes on the code —
  turned back on the ticket's own claims.
- **T-7 — Split runnable-now from not-yet-buildable; tag every item.**
  `[RUN@HEAD]` items read existing state and MUST show observed output now.
  `[POST-BUILD]` items exercise the code this ticket will create; they carry a
  predicted result *and the reason they can't pre-run*, and are the implementer's
  first checkpoint. A `[POST-BUILD]` tag must never hide a check that was
  actually runnable at HEAD — that mislabel is exactly how a false premise ships.
- **T-8 — A PASS-case needs a valid input state; construct it, don't assert the
  live artifact is what it isn't.** If the live artifact isn't in the state the
  PASS-case requires (post-run, arc advanced, tool not yet wired), build a
  correct fixture and test against that. Asserting "the live X passes" when live
  X has moved on is the T-024 bounce.
- **T-9 — Scope each assertion to the ticket's stated invariant, nothing
  adjacent.** Assert only what the invariant requires. A check on a neighbouring
  field manufactures false FAILs on good inputs. *(Case law: T-025's invariant is
  personal-name presence; asserting the focal's *city* also appears in prose is
  out of invariant and false-fails an indoor chapter.)*

## D. Shape of the collaboration

- **T-10 — Declare the blast radius and re-verify it HERE.** For every shared
  surface in the write-set, name its consumers (from the producer/consumer
  registry) and re-run their acceptance in *this* ticket's §3. A shared surface
  with an empty Downstream is an authoring error; a downstream regression must
  fail in the ticket that caused it, never be discovered by the next one.
- **T-11 — A red STOP is a correct outcome.** When an implementer stops at a red
  check, the senior diagnoses, AMENDS the ticket in place (dated correction +
  recorded resolution), and clears it to resume. The ticket accumulates the true
  history of the work; nothing the implementer did to earn the stop is "wasted".
- **T-12 — The coherence test.** The ticket must obey the standard it imposes on
  the code (spec M-14, applied to tickets). If it demands "evidence it fires" of
  every check, its own acceptance must be *executed with evidence*. When the way
  you dispatch a change violates the way the change must work, one of the two is
  wrong — this document itself is numbered, scoped, cued, and names its non-goals.

## Operational checklist (before dispatching any ticket)

1. Write-set is exact; scope + STOP rule stated (T-1, T-2).
2. Every precondition dry-run against HEAD, output in hand — read the artifact,
   not your memory of it (T-4, T-5).
3. Acceptance items tagged `[RUN@HEAD]` / `[POST-BUILD]`; every `[RUN@HEAD]` item
   executed and its observed output pasted; PASS-cases given valid fixtures where
   live state has moved (T-6, T-7, T-8).
4. Every assertion scoped to the stated invariant (T-9).
5. Downstream consumers named and re-verified in §3 (T-10).
6. Only then flip drafted → dispatch-ready.

## Do NOT

- Do not predict a PASS you did not run. Do not verify a premise against a mental
  model of state instead of the file at HEAD. Do not assert the live artifact is
  a state it has moved past. Do not check a field the ticket's invariant doesn't
  own. Do not dispatch with an empty observed-output block.
