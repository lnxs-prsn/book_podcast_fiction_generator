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
3. **RESOLVED by `58e4dbd` (T-004 accepted — see §6):** ~~F15 FALSE-FAIL
   WARNING (until T-004 lands)~~ — the structural gate now counts unnamed
   newcomers via the new other_entrants contract. Historical text follows:
   the structural gate
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

> **SUPERSEDED IN PART by §5 (same day, later):** queue item 1 (ch6 review) is
> DONE and ACCEPTED; the open queue is now T-004 → T-005 → T-003.

Read-first: this file → `handoff-2026-07-18-deepseek-switch-404.md`
(§3b–3d) → the two 2026-07-17 handoffs → `fiction_loop/CONTRIBUTING.md` →
`tickets/`. Diagnostics: `PYTHONPATH=src .venv/bin/python
fiction_loop/tools/analyst.py` (zero tokens) and `.../progress.py`
(mid-run position). Chapter 007 kickoff: RUN.md prompt as written — no
resume note needed; the pointer is clean. Conduct: never cat/grep/print
`.env` or `env | grep`; env inspection is `echo $VAR` for non-secret vars
only.

## 5. ADDENDUM (2026-07-18, late) — ch6 review ACCEPTED; queue: T-004 → T-005 → T-003

Senior review of queue item 1 ran in full; owner ACCEPTED chapter 006 (no
redo). Every claim below verified against files this sitting.

1. **F14 / continuity / anchor — PASS.** Progression nameable+visible
   (supervisory cubicle, name on the glass; never gate-attributed); char_001
   continuity verified against the pre-ch6 card (`git show a77eec8~1`);
   anchor manifestation `notebook_page` differs from ch5's `seen` (repeating
   ch2's vehicle is legal — the rotation constraint is vs the previous
   chapter). LAW 13 F15-override ledger entry confirmed at
   `logs/chapter_006/00_orchestrator.log:38`.
2. **"Owned" compression is CORRECT — not Updater over-compression.**
   Verified against updater.md COMPRESSION RULES + owner D9 lever 2 (easy
   ops target 2 touches): master_state's `"owned"` is summary-only; full
   schedule/history retained in the concept card and `process_state.json`
   (which is what the Extractor plans from). The confusion source was
   curriculum §7's stale 3/4 columns — D9 said the columns would be edited
   down when the registry was authored; they never were. FIXED this sitting:
   D9-amendment note added under §7's legend (cards' `touch_schedule` =
   machine truth; beyond-target columns = ambient layer per D1 hybrid + D9
   lever 4). Owner ruled "follow the existing structure" — no card
   re-encoding, no new scheduling machinery.
3. **THINKING TAX (first deepseek-v4-pro receipts, `.pipeline_spend.json`):**
   generation out=5,901 tokens vs ~2,600-token chapter → reasoning ≈ 55% of
   output; living-doc update ≈ 63% (out=6,088 vs qwen3-max's ~2,200 for the
   same task). BUT the full ch6 cycle cost $0.028 vs $0.067 (qwen3-max) and
   ~$0.40 (qwen3.7-plus) — cheapest chapter to date. Verdict: keep model and
   budgets. Operational rule: `max_tokens` ≥ ~2.5× expected prose (the
   2026-07-17 smoke receipt shows reasoning eating the whole budget at 16).
4. **NEW FINDING → T-005** (`tickets/T-005-extractor-pointer-precedence.md`):
   extractor STEP A FALLBACK and STEP D fire on the same all-deficits-zero
   condition with no precedence — ch5's run took the FALLBACK (taught ch6 an
   arc-2 touch early; harmless, committed state), ch6's run took STEP D
   (arc_transition; the correct reading, ratified by the ticket). Also
   `lead_failure_mode` is not contractually required: NO 006 entry in
   `failure_mode_lead_history` (actual lead: the executor). Deliberately NOT
   backfilled — LAW 8 hand surgery, and harmless since arc 2 rotates a fresh
   failure-mode pool. Dispatch T-005 only AFTER T-004 (same write-set file).
5. **T-004 redispatch authorized** (owner); senior note in its §6 —
   exact-paths warning (`fiction_loop/tools/INTEGRATION_SPECS.md`).
6. **T-003 owner step DELEGATED to senior** (owner, this session): senior
   renames the `.env` keys blind after the implementation lands (ticket §4).
   Repo + shell rc verified clean of `OPENROUTER_*`; residual check is the
   Qwen companion session's live env.

**Open queue now:** dispatch T-004 → senior acceptance → dispatch T-005 →
senior acceptance → dispatch T-003 → senior .env step + acceptance → chapter
007 kickoff (RUN.md prompt as written; pointer clean). Older queue:
`handoff-2026-07-17-clone-audit.md` §5, unchanged.

## 6. ADDENDUM (2026-07-18, later) — T-004 ACCEPTED (58e4dbd); queue: T-005 → T-003

- **T-004 implemented by Codex (`58e4dbd`) and ACCEPTED by senior** — all §3
  criteria re-run independently (synthetic-brief gate test both directions,
  contract greps, write-set check); full record in the ticket's §6. The F15
  false-fail warning (§2.3) is RESOLVED — unnamed newcomers now reach the
  structural gate. structural_gate.py and state untouched, as designed.
- Process note: the implementer omitted the §6 log append (reported via owner
  instead); senior backfilled it. Next dispatch prompt should restate that
  the log append is part of the ticket.
- **Open queue now:** dispatch T-005 (extractor precedence — unblocked, T-004
  landed) → senior acceptance → dispatch T-003 → senior .env step +
  acceptance → chapter 007 kickoff. T-003 is NOT yet implemented or
  dispatched. Older queue: `handoff-2026-07-17-clone-audit.md` §5, unchanged.

## 7. ADDENDUM (2026-07-18, later still) — T-005 ACCEPTED (1063ff0); queue: T-003 only

- **T-005 implemented by Codex (`1063ff0`) and ACCEPTED by senior** — all §3
  criteria re-run independently, including the determinism dry-run (result
  equals the committed ch7 pointer). Extractor pointer logic is now
  single-outcome: STEP A.0 arc-transition precedence, FALLBACK deleted,
  STEP D selection explicit, lead_failure_mode REQUIRED with LAW 4
  producer/consumer registration. Full record in the ticket's §6.
- **Open queue now: T-003 only** (then ch7 kickoff). Sequence: dispatch
  T-003 → implementation commit lands → senior performs the delegated .env
  key rename (blind, per T-003 §4) → senior runs acceptance 1–6 (4–5 are
  post-rename) → done. Older queue: `handoff-2026-07-17-clone-audit.md` §5,
  unchanged.
