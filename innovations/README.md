# INNOVATIONS — a deployable toolbox of methods this project invented and proved

> Governance: `CONTRIBUTING.md` — admission bar (proven-with-evidence only),
> structure contract, add procedure, evolve-sync trigger. Read it BEFORE
> adding or changing anything here.

Each subdirectory is one **pattern** with two parts:

- `PATTERN.md` — what it is, the problem it kills, how to use it, what
  projects it fits, and dated proof from the origin project (an AI-built
  developer-training system: human owner + multiple AI agents on one repo,
  2026).
- `kit/` — **files you copy verbatim and act on**: templates, generic
  convention documents, a working commit hook, starter blocks. The kit is
  what makes a pattern deployable in a project with zero files written yet.

## Two ways in

**Brand-new empty project:** pick your patterns → copy each one's `kit/`
contents to the right place in the new repo (kits say where) → fill the
`<placeholders>` → start working under them from commit one. A sensible
minimal starter set: `spec-writing-method` + `ticket-dispatch` +
`trunk-review-queue`; add `multi-agent-coordination` the day a second agent
appears.

**Running project that hurts:** find your symptom in the index below → read
that `PATTERN.md` (it names the failure modes you're probably living) →
adopt its kit incrementally — every kit is additive (new files + one hook
config), none requires restructuring existing code.

## Index

| Pattern | One line | Problem it kills | Kit contents |
|---|---|---|---|
| [spec-writing-method/](spec-writing-method/PATTERN.md) | Numbered, auditable specs for AI implementers (M-1..M-17) | Scope drift; "done" as a vibe | the full method file, copy-ready |
| [ticket-dispatch/](ticket-dispatch/PATTERN.md) | Self-contained work orders, author-verified preconditions | Juniors burned by spec bugs | `TICKET_TEMPLATE.md` |
| [multi-agent-coordination/](multi-agent-coordination/PATTERN.md) | ALONE/GROUP modes, board, invariants, worktrees | Agents colliding in one tree | generic protocol + board + agent entry pointer |
| [trunk-review-queue/](trunk-review-queue/PATTERN.md) | Unpushed range = review queue; push = the gate | Branch ceremony; unreviewed publishing | generic `GIT_CONVENTIONS.md` |
| [handoff-discipline/](handoff-discipline/PATTERN.md) | Dated, stale-marked orientation doc + update triggers | Cold sessions repeating stale claims | generic rules + handoff skeleton |
| [machine-enforced-laws/](machine-enforced-laws/PATTERN.md) | Every rule gets a machine check | Rules-as-prose violated in hours | working `commit-msg` hook + preflight design |
| [file-state-machine/](file-state-machine/PATTERN.md) | Disposable sessions over durable file state | Agent context as load-bearing state | starter file set (RUN/registry/journal) |
| [verify-dont-trust/](verify-dont-trust/PATTERN.md) | A log is a claim, not proof | Confident wrong reports compounding | `REVIEW_CHECKLIST.md` |
| [trust-ladder-golden-sets/](trust-ladder-golden-sets/PATTERN.md) | Autonomy graduates from logged override rates | Autonomy by schedule or optimism | graduation-rule ledger template |
| [paid-call-governance/](paid-call-governance/PATTERN.md) | Caps before spend; receipts always | Silent API spend; lost provenance | caps file + wrapper contract |
| [decision-ledger/](decision-ledger/PATTERN.md) | Append-only owner decisions; propose-and-STOP | Agents deciding taste; relitigated decisions | `decisions_TEMPLATE.md` |

Natural pairings: spec-method + ticket-dispatch (design → dispatch);
multi-agent + trunk-queue + machine-laws (the working agreement);
file-state-machine + handoff (surviving session/machine death);
verify-dont-trust + trust-ladder (evidence before autonomy);
decision-ledger under all of them (the owner stays sovereign).

## Incubating (ideas without evidence yet — no directory rights; see CONTRIBUTING §1)

- (none)

## Origin evidence, in one paragraph

All eleven were exercised in one repo during 2026: a monorepo on a Raspberry
Pi, one human owner, three AI agents (one senior for specs/review, two junior
implementers). Highlights: 4 tickets dispatched-implemented-reviewed-merged in
one day including the protocol's first parallel worktree ticket; a machine
migration survived with zero lost work because all state was files; a commit
hook that machine-enforces the written conventions (and validated its own
installing commit); a 1252-test estate (1120 + 132) kept green through all of
it; and a golden-set evaluation spine where AI verdicts stay provisional until
a human (or logged override-rate evidence) says otherwise.
