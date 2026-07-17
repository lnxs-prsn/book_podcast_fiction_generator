# AGENTS.md — entry point for any AI agent in this repo

**Orient first: read `HANDOFF.md` (repo root), then the current handoff it
points to. Do not orient from `docs/` or root-level manuals — several are
stale and say so in their banners.**

Binding rules, in force for every agent regardless of harness:

1. **Roles:** work is dispatched as tickets in `tickets/` (template:
   `innovations/ticket-dispatch/kit/TICKET_TEMPLATE.md`). If you are
   implementing a ticket: stay inside its write-set, follow §5 constraints,
   append to its implementer log, STOP on failure — never improvise
   alternative designs. Current role assignments: see the current handoff §0.
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
