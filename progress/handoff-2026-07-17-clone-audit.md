# HANDOFF — 2026-07-17 clone audit + role split — for the next AI

Self-contained. Written by the senior agent (Claude) after auditing a fresh
clone on a new OS. Where something may have changed since writing, this file
says CHECK instead of asserting.

## 0. New working model (owner ruling, 2026-07-17 — binding)

- **Claude = senior dev only**: verifies preconditions, writes tickets/specs,
  reviews, maintains handoffs. Does NOT implement.
- **Codex and the Qwen code companion (DeepSeek v4) = junior implementers.**
  They work from tickets in `tickets/` (format:
  `innovations/ticket-dispatch/kit/TICKET_TEMPLATE.md`). One ticket, one
  implementer, confined to the ticket's write-set. Cross-review: the other
  junior reviews; the senior runs the acceptance commands (verify-don't-trust
  — an implementer log is a claim, not proof).
- Owner interaction stays PROPOSE-AND-CORRECT (2026-07-10 handoff §5) —
  unchanged and still binding.

## 1. The machine/OS migration — what survived, what didn't

The repo was pushed to GitHub at a1a3dba (2026-07-11) and re-cloned on a new
OS 2026-07-17 ~09:56 (this machine is still a Raspberry Pi — Pi constraints
from the 2026-07-10 handoff §6 still apply).

Survived (in git): all prose (`fiction_loop/chapters/`, 6 files + rejected/),
all state (`fiction_loop/state/` incl. `.pipeline_spend.json`, lifetime spend
≈ $3.46), all core docs, agents, specs, tools, `src/uv.lock`. FI-1 did its
job — nothing load-bearing was lost.

Did NOT survive (gitignored):
- **`.env`** — recreate from `.env.example` (5 vars; only the OPENROUTER ones
  are needed for chapters). Tools read shell env first, `.env` fallback.
- **the venv** — being rebuilt at the repo ROOT via ticket T-001 (below).
- **`books/`** — the Pólya source epub is gone from this machine. Chapter
  generation does NOT read it at runtime (curriculum already extracted into
  core/), but the sourcing rule (specs/README.md) needs it for any new
  Pólya-derived core content. Restore from the old machine when possible.
- **`logs/`** — including `logs/chapter_006/`, which the 2026-07-10 handoff
  named as the test fixture for the pre-writer prompt gate. Partial
  substitute: `fiction_loop/prompts/assembled_prompt.md` (committed, ch6-era).

## 2. Story state — CHECK with tools once the venv exists

- `master_state.json`: 5 chapters complete, arc 1, pointer at chapter **006**
  (return_to_character, char_001, op_what_is_missing touch 2).
- `chapters/chapter_006.md` in git is still the REJECTED F15 draft. The ch6
  redo that was in flight on 2026-07-10 never landed (last paid writer calls
  2026-07-10 06:29, no living-doc update after, state never advanced).
  **First generation task is resolving ch6, not ch7** — the loop's own
  pointer will schedule it. Review checklist when it lands: F14 life
  progression nameable+visible; correct_approach continuity; anchor
  manifestation must differ from ch5's "seen".
- Before ANY paid call, run the free→cheap ladder:
  (1) `progress.py` (zero tokens) → (2) `analyst.py` (zero tokens, catches
  missing key/env faults) → (3) one tiny test call (~$0.0002, the spend log's
  existing `test model=...` practice) → only then generate.
- Owner intends chapter generation to be driven by the Qwen code companion.
  It must read `fiction_loop/RUN.md` + `core/agent_conduct.md` first; they
  are binding on any agent, human-driven or not.

## 3. Dispatched work

- **`tickets/T-001-move-python-project-root.md`** (implementer: Codex) —
  move pyproject/uv.lock/.python-version from `src/` to repo root, single
  root `.venv`, sweep the live `src/.venv` references. Rationale: every
  agent session kept finding an empty/missing root venv and hallucinating
  pip/venv repairs; one root project ends that class of failure. Owner
  explicitly chose this over keeping the src/-rooted layout.
  **LANDED f3ed1b5, 2026-07-17 21:19; all 5 acceptance checks re-run and
  verified by the senior (not from the implementer's log).** The interpreter
  is now **`.venv/bin/python` from the repo root** (PYTHONPATH=src
  unchanged). Ticket log note: 15 live references replaced, not the 12+1 the
  ticket estimated (author's grep was truncated; all extras were inside the
  listed write-set files). The 2026-07-10 handoff carries a staleness note
  pointing here.

## 4. Discovered this session (context for future decisions)

- Repo history: the project was an outer repo with `src` as a git SUBMODULE
  until 119fc63 (2026-06-25) consolidated it into one repo ("Phase 0", the
  submodule was broken). The GitHub push inherited the monorepo.
- **`innovations/` is present and UNTRACKED** — an 11-pattern toolbox (each
  PATTERN.md + deployable kit/) extracted from a DIFFERENT origin project
  (no references to this repo; verified by grep). One kit is already adopted
  here: root `09-how-to-write-specs.md` is byte-identical to
  `innovations/spec-writing-method/kit/`'s copy. Owner decided (2026-07-17,
  conversational): keep it, commit it, let it sit until build-list rows can
  cash in kits (nearest matches: decision-ledger kit ↔ the factory build
  list's "decisions ledger" row; machine-enforced-laws commit hook ↔ SG-14 /
  LAW 15). Committed 2026-07-17 as 23c7519.
- Adopting any kit here = the toolbox's first transplant evidence; record
  outcomes in the pattern's "Proven in".

## 4b. Orientation front door (added 2026-07-17, same session)

Cold-agent entry is now standardized: **`HANDOFF.md` at the repo root** is the
stable front-door pointer (per `innovations/handoff-discipline/kit/
HANDOFF_RULES.md`); `AGENTS.md` (read natively by Codex and other agents) and
`CLAUDE.md` (read natively by Claude Code) both route there. The three stale
orientation traps (`docs/project_state.md`, `docs/log.md`, `user_manual.md`)
carry STALE banners pointing to the front door. Keep HANDOFF.md's banner
aimed at the newest dated handoff whenever a new one is written.

## 4c. RUN-READY STATE (end of 2026-07-17 session — verified, not assumed)

Analyst run 2026-07-17 evening (post 526f08e): **all green except ONE
CRITICAL — no `OPENROUTER_API_KEY`** (`.env` gone with the clone; only the
owner has the key). Everything else verified: config OK (model=qwen3-max),
state sync OK (chapter_count=5, next=006 return_to_character
op_what_is_missing), git tree clean. Cleared this session: the stale
rejected-F15 `chapter_006.md` is archived as
`chapters/rejected/chapter_006_attempt1.md` (ch3 precedent) so the count
mismatch WARN is gone; RUN.md's stale ".env already contains the key" claim
and bare-python3 refs fixed in place.

**To resume generation (in order):**
1. OWNER: `cp .env.example .env`, set `OPENROUTER_API_KEY`.
2. Re-run `.venv/bin/python fiction_loop/tools/analyst.py` → expect zero
   CRITICALs (the "last commit is not a chapter transaction" INFO is normal).
3. Kickoff prompt for the generating agent (Qwen companion or any harness
   with subagents + shell): **the verbatim Kickoff prompt in
   `fiction_loop/RUN.md`** — no custom prompt. One session per chapter.
   Note: the harness MUST have a subagent/Task tool (context-budget rules
   depend on it) and a shell; 300 s shell timeout applies. An invalid key
   fails at the writer call with OpenRouter's misleading 401 ("Missing
   Authentication header" = key sent but INVALID) — no charge on auth
   failure; see RUN.md practical advice.
4. Chapter 006 lands first (the pointer schedules it automatically).
   **First-ever exercise of the return-chapter review** — senior (or owner)
   checks: F14 life progression nameable and visible; correct_approach
   continuity for char_001; anchor manifestation differs from ch5's "seen".
5. Continue one chapter per session toward the validation bar (§5).

## 5. Open queue (unchanged from 2026-07-10 except as noted)

1. ~~T-001 lands + acceptance verified by senior~~ DONE 2026-07-17 (f3ed1b5).
2. ~~Pre-run hygiene~~ DONE 2026-07-17 (526f08e) — only `.env` remains (§4c).
3. Generate chapters 006 → ~008/009 (the arc-1→2 boundary): the "validated"
   bar from `specs/intake_factory.spec.md` §3 — never-fired machinery must
   fire for real (arc_transition + anchor_interlude chapter types, failure
   pool growth at the arc boundary, F14 return-chapter continuity = ch6,
   compression at scale). Qwen companion drives; senior reviews each chapter.
4. FIRST BUILD after that: pre-writer prompt gate (fixture changed — old
   logs/ lost with the clone; use committed `prompts/assembled_prompt.md` or
   a freshly logged prompt from the ch6 run).
5. Then the standing order from 2026-07-10 §4: FI-2..FI-11, factory
   Stages 1–2 parallel track. All future implementation goes out as tickets
   (§0 role split).
6. Only open owner decision remains D10 (rights/licensing) — don't push it.
