# Agent entry point (repo root) — copy to your repo root; agents auto-load it

Before doing ANYTHING in this repo:

1. Read `MULTI_AGENT_PROTOCOL.md` — you may not be the only agent here. Your
   dispatch prompt or ticket names your mode (ALONE / GROUP); no mode named =
   ALONE. Check `BOARD.md` for other active work.
2. Read `GIT_CONVENTIONS.md` before any git operation. Never `git add .` /
   `-A` / `commit -a`. Never push.
3. Your task is defined by a `TICKET_*.md` or spec — stay inside its
   write-set. Update its implementer log as you go; stop and log on failure
   instead of improvising.
4. Never create, print, or commit `.env` files or keys.
5. Changed project state, or found a doc telling lies? The handoff must learn
   it — rules in `HANDOFF_RULES.md` (tight write-set: record it in your
   ticket log and the reviewer carries it over).

<Adjust paths above to wherever you keep the convention files. Make one thin
pointer file per agent tool that auto-loads a different filename (CLAUDE.md,
QWEN.md, ...) — same content, pointing here.>
