# HANDOFF — 2026-07-18 (evening) — chapter 006 LANDED; queue: review → T-004 → T-003

Written by the senior instance at session end; supersedes
`handoff-2026-07-18-deepseek-switch-404.md` (that file's §3b–3d addenda
remain the detailed record of today's 404/harness/F15 events; its §4 is
historical). Roles unchanged: `handoff-2026-07-17-clone-audit.md` §0 —
owner assigns; senior writes tickets and re-runs acceptance, never
implements; Codex/Qwen implement.

## 1. State (every claim verified against git/files at commit c3d5329)

- **Chapter 006 is committed as transaction `a77eec8`** — first full
  chapter transaction and first deepseek-v4-pro chapter. 1,909 words,
  return_to_character (Yejide/char_001), gate G-006 closed and archived,
  anchor via torn notebook page, op_what_is_missing touch 2, comprehension
  compressed to "owned" (review item — see §3.1). Working tree clean.
- **Next pointer: 007 — arc_transition.** No gate, no anchor, no operation
  due (per master_state at a77eec8). Structurally immune to the F15 trap
  (§2.3).
- **T-002 merged** (`aebc2ca`, accepted): client normalizes any api_url to
  the full `/v1/chat/completions` path; analyst has a `returned 404`
  signature with freshness aging; writer.md BLOCKED-wording rule.
- **The step-8 404 saga is CLOSED.** Root cause: Qwen companion session
  carried a base-URL `OPENROUTER_URL` overriding `.env` (shell wins by
  design). Codex ran with a clean env and the chapter landed — Qwen-layer
  localization confirmed; the exact in-Qwen mechanism was never proven and
  is moot once T-003 lands. Full proven-vs-open ledger:
  `handoff-2026-07-18-deepseek-switch-404.md` §3c.

## 2. Binding facts learned today (cold session must know)

1. **pytest is NOT a project dependency** and must not be added. The
   sanctioned test command is
   `PYTHONPATH=src uv run --frozen --with pytest python -m pytest ... -q`
   (ephemeral overlay; pyproject/uv.lock untouched). See T-002 §6.
2. **Codex harness quirks:** its safety classifier (a) false-positives on
   `analyst.py` (the .env key-presence read looks like secret access) and
   (b) had a full service outage blocking even `date`. Remedies: run the
   analyst gate externally (senior shell) and say so in the log, take Codex
   out of Auto mode, or pre-approve analyst.py. Aircraft-vs-scanner rule:
   these blocks are harness-side; the pipeline state stays clean — verify
   with receipts (pgrep + .out mtimes), not with STATUS.md claims.
3. **F15 FALSE-FAIL WARNING (until T-004 lands):** the structural gate
   cannot see unnamed newcomers — extractor.md emits `other_entrants` only
   for NAMED solvers while the prompt correctly says "name the newcomer
   only if they matter". Any chapter whose only newcomer is unnamed will
   FAIL F15 falsely. Before believing that gate verdict: grep the chapter
   prose for the newcomer; if present → owner accepts explicitly (LAW 13,
   log it), never redo generation (infinite paid-retry loop). Ch6 set the
   precedent (ledger entry in its chapter log).
4. **Env naming decision (owner, final): `BOOKGEN_LLM_*`** project-owned
   namespace replaces `OPENROUTER_*`/`LLM_*` — clean break, no aliases.
   That is T-003; do not partially rename outside it.

## 3. Open queue (in order)

1. **Chapter 006 prose review** (owner or senior): F14 life progression
   nameable+visible; char_001 continuity; anchor manifestation differs from
   ch5's "seen". PLUS two items added today: (a) verify touch-2 →
   "owned" compression against the curriculum's comprehension ladder
   (possible Updater over-compression — check the concept card + curriculum
   §ladder); (b) THINKING TAX ratio from `.pipeline_spend.json` receipts —
   first real deepseek-v4-pro data point; if reasoning dwarfs prose,
   revisit model/budgets (analyst WARN was deliberately downgraded, see
   d1c381b).
2. **T-004 redispatch** (`tickets/T-004-f15-unnamed-newcomer-contract.md`):
   first attempt aborted on its own path typo (ticket §6); ticket is
   correct — redispatch verbatim with a note to use the write-set's exact
   paths. Between-runs timing is satisfied (ch6 committed). Senior re-runs
   acceptance after.
3. **T-003** (`tickets/T-003-bookgen-env-namespace.md`): env-namespace
   rename. Preconditions all met (T-002 merged, ch6 landed, between runs).
   Includes an OWNER STEP: rename `.env` keys + remove companion-harness
   OPENROUTER_* exports; implementer must never touch `.env`.
4. Older queue: `handoff-2026-07-17-clone-audit.md` §5, unchanged.

## 4. How to continue (cold-start)

Read-first: this file → `handoff-2026-07-18-deepseek-switch-404.md`
(§3b–3d) → the two 2026-07-17 handoffs → `fiction_loop/CONTRIBUTING.md` →
`tickets/`. Diagnostics: `PYTHONPATH=src .venv/bin/python
fiction_loop/tools/analyst.py` (zero tokens) and `.../progress.py`
(mid-run position). Chapter 007 kickoff: RUN.md prompt as written — no
resume note needed; the pointer is clean. Conduct: never cat/grep/print
`.env` or `env | grep`; env inspection is `echo $VAR` for non-secret vars
only.
