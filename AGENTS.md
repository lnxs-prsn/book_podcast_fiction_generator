# AGENTS.md — entry point for any AI agent in this repo

**Orient first: read `HANDOFF.md` (repo root), then the current handoff it
points to. Do not orient from `docs/` or root-level manuals — several are
stale and say so in their banners.** EXCEPTION: pipeline-run sessions
(RUN.md kickoff) never orient here — see the ROLE FENCE in `fiction_loop/RUN.md`.

Binding rules, in force for every agent regardless of harness:

1. **Roles:** work is dispatched as tickets in `tickets/` (template:
   `innovations/ticket-dispatch/kit/TICKET_TEMPLATE.md`). If you are
   implementing a ticket: stay inside its write-set, follow §5 constraints,
   append to its implementer log, STOP on failure — never improvise
   alternative designs. Current role assignments: see the current handoff §0.
   **Standing exemption:** appending to the ticket's OWN implementer-log
   section is always permitted and does NOT count against its write-set or
   any "only the write-set changed" acceptance check — a ticket need not list
   itself. (This is the ONLY implicit write target; everything else is the
   literal write-set.)
2. **Environment:** `.venv/bin/python` from the repo root (uv-managed).
   uv only — never pip install, never create venvs by hand.
3. **fiction_loop/:** read `fiction_loop/CONTRIBUTING.md` before changing
   anything under it; `fiction_loop/core/agent_conduct.md` binds during
   chapter runs. Never touch `fiction_loop/state/`, `fiction_loop/prompts/`,
   or `core/living_document.md` while a chapter is in flight; never edit or
   revert `.pipeline_spend.json` (real money receipts).
4. **Git:** pathspec-limited commits only (never `git commit -a`); commit
   message conventions and trailers per the active ticket.
5. **Paid calls:** forbidden unless the ticket/run explicitly budgets them;
   gates-before-spend always.
6. **Hardware:** Raspberry Pi — no heavy parallel processes.
7. **Explaining / deciding:** when a task involves understanding or deciding
   (not just executing), follow the owner's exploration style in
   `EXPLORATION_PREFERENCES.md` — problem-space-first, axis-by-axis, applied
   *situationally* (it says when to scale down or skip). Not binding for pure
   execution.
8. **Owner decisions — file, don't page.** (Maintainer sessions only; a run
   session stops and reports per `fiction_loop/RUN.md`.) When you hit a
   blocker only the owner can decide: do not guess, do not stop to ask —
   append it to `fiction_loop/human_decision.md` in that file's §0 schema,
   marked `[PROPOSED]`, then continue with other tasks. If nothing else is
   unblocked, stop and tell the owner a decision is waiting there. When unsure
   whether a task depends on the ruling, treat it as blocked; never spend paid
   calls on work the ruling could invalidate. (LAW 13 governs what qualifies.)
9. **Your own judgment calls are auditable.** Decisions you make WITHOUT the
   owner — what to do next, what to defer, a scope you narrowed, a ticket you
   struck, a handoff claim you doubted — go in `NEXT_ACTIONS.md` §3 with the
   reasoning, in the same sitting. The owner cannot object to reasoning they
   cannot see, and an objection now is cheaper than discovering a bad call
   three chapters later. `NEXT_ACTIONS.md` also carries the ordered queue and
   why each item is next or deferred. It keeps only the newest 5 per section;
   when a 6th arrives, MOVE (never copy) the oldest to the append-only ledger
   `progress/agent-decisions.jsonl`, one JSON object per line.
