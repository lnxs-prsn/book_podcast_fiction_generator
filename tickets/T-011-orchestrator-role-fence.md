# TICKET T-011: role fence — the run driver operates the loop as Orchestrator, and knows nothing else

```
Mode: alone
Depends-on: T-007/T-008/T-009/T-010 MERGED FIRST (RUN.md and
            orchestrator.md are shared write-set; serialize last in the
            current queue).
Timing: BETWEEN runs only — chapter 008 committed or formally abandoned
        first.
Worktree: main working tree, repo root
Write-set: fiction_loop/RUN.md,
           fiction_loop/agents/orchestrator.md,
           fiction_loop/core/agent_conduct.md,
           HANDOFF.md (repo root — one scoping paragraph only),
           AGENTS.md (repo root — one scoping sentence only)
Hot-files: RUN.md, orchestrator.md
State-access: none
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first. NOTE the write-set crosses the
fiction_loop/ boundary (HANDOFF.md, AGENTS.md): sanctioned by this ticket
explicitly, because the defect IS the interaction between the repo-level
orientation docs and the run role — it cannot be fixed from inside
fiction_loop/ alone.

## 1. Problem (two incidents, same day, 2026-07-18)

The chapter-008 driver session (a) skipped steps 10/11/11.5 and ran the
Updater on a gate-FAILED brief, and (b) later refused to resume the run,
citing four dispatched tickets and proposing to implement them mid-run —
a blocking relationship no document states and the tickets' own timing
gates forbid.

Root cause — **two orientation systems, one front door, no precedence
rule:**

- `agent_conduct.md` §2 SCOPE WALLS already forbids what happened: "No
  agent reads or modifies ANYTHING outside fiction_loop/" — HANDOFF.md,
  tickets/, progress/ are all outside it. The wall existed and was
  crossed.
- But the repo-level front door actively countermands it for every cold
  session: AGENTS.md line 3 — "Orient first: read HANDOFF.md…" — and
  CLAUDE.md's equivalent. A fresh session pasted the RUN.md kickoff is
  still a cold session; it obeyed both masters. Nothing says which
  instruction wins for which role.
- The kickoff prompt (the driver's HARD CHANNEL, LAW 5) restates the
  context-budget rules about *pipeline content files* but never restates
  the scope wall about *governance documents* — the exact class that was
  crossed. LAW 5's lesson: a MUST that lives only in a referenced document
  is advisory in practice.

Owner decision (2026-07-18, recorded here): **the agent that runs
fiction_loop operates the loop as Orchestrator, and ONLY that.** Maintainer
orientation (handoff, tickets, laws, progress) is for maintainer sessions.

## 2. Fix

**2.1 RUN.md — kickoff prompt (the hard channel; LAW 5: full content
inline, never by reference).** Add to the pasted prompt block, after the
CONTEXT BUDGET bullet:

```
- ROLE FENCE: you are the run driver, not a maintainer. From this instant
  you read NOTHING outside fiction_loop/ — in particular NOT HANDOFF.md,
  NOT tickets/, NOT progress/, NOT innovations/, NOT CLAUDE.md/AGENTS.md,
  NOT fiction_loop/CONTRIBUTING.md. Repo-level "orient from the handoff
  first" instructions are for maintainer sessions and DO NOT apply to you.
  Your complete world is: agents/orchestrator.md, core/agent_conduct.md,
  and the files those two specs explicitly direct you to touch, step by
  step. You never implement tickets, edit specs or tools, or act on
  project plans — if anything outside your world seems to bear on the run
  (a ticket, a handoff note, an instruction you remember), STOP and report
  it verbatim; never act on it. You have no authority to decide the run
  should not proceed for reasons outside your specs.
```

**2.2 orchestrator.md — CONTEXT BUDGET section:** add the governance-doc
line: the Orchestrator never reads HANDOFF.md, tickets/, progress/,
innovations/, CONTRIBUTING.md, or repo-root orientation files; rationale:
role confusion, not context size. Historical line: "Added 2026-07 (T-011)
— the ch8 driver oriented from the handoff and (a) improvised a step skip,
(b) invented a ticket-blocking deadlock."

**2.3 agent_conduct.md §2 SCOPE WALLS:** add the case-law line naming the
seductive reads explicitly: "(Case law 2026-07-18: the ch8 driver read
HANDOFF.md and tickets/ — both outside fiction_loop/ — then ran the
Updater on a gate-FAILED brief in one incident and refused a documented
resume in another. The wall includes ALL repo-root orientation and
planning documents; RUN.md's kickoff prompt restates this as the ROLE
FENCE.)"

**2.4 HANDOFF.md front door — one scoping paragraph** (place directly
under the CURRENT-handoff blockquote):

"**Scope: maintainer sessions only.** A session running the fiction_loop
pipeline (RUN.md kickoff) must NOT orient here — its complete world is
`fiction_loop/RUN.md` + the two specs it names. If you were kicked off to
run a chapter, close this file now and report that you read it."

**2.5 AGENTS.md — one sentence** appended to the orient-first line:
"EXCEPTION: pipeline-run sessions (RUN.md kickoff) never orient here —
see the ROLE FENCE in RUN.md."

**2.6 LAW 4 audit, same sitting:** grep `HANDOFF\|orient` across
`fiction_loop/RUN.md fiction_loop/agents/ fiction_loop/core/` and the
repo-root CLAUDE.md/AGENTS.md; every hit updated or exempted with
disposition in §4. (CLAUDE.md itself is NOT in the write-set: its
orientation text already routes through HANDOFF.md, which now carries the
scope paragraph — verify this suffices and record; if CLAUDE.md turns out
to instruct run sessions directly, STOP and report rather than widening
the write-set.)

## 3. Acceptance (ALL must pass)

1. `grep -n "ROLE FENCE" fiction_loop/RUN.md` → present INSIDE the pasted
   kickoff prompt block (between the ``` fences), not outside it.
   (HEAD today: 0 hits.)
2. `grep -n "maintainer sessions only" HANDOFF.md` → the scoping paragraph
   present directly under the CURRENT blockquote.
3. `grep -n "EXCEPTION" AGENTS.md` → the one sentence present; AGENTS.md
   diff is exactly one line.
4. orchestrator.md CONTEXT BUDGET names the governance docs;
   agent_conduct.md §2 carries the case-law line.
5. Cold-read test (deterministic, zero tokens): a fresh reader following
   ONLY the kickoff prompt encounters the fence before any step
   instruction; a fresh maintainer following HANDOFF.md encounters the
   scope paragraph before the read-first list. Verify by reading order of
   the rendered files; record in §4.
6. §2.6 grep audit disposition list recorded in §4.
7. Test suite (sanctioned command) → `1 failed, 331 passed`.
8. `git status --porcelain` → write-set only; one pathspec-limited commit
   (pathspec includes the two root files).

## 4. Implementer log (append below; never delete the ticket body)
