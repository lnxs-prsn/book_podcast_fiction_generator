# HANDOFF — 2026-07-10 factory-spec session — for the next AI

Self-contained: assumes no access to the previous session's memory. Everything
verifiable is in git; where something might have changed since writing, this
file says CHECK instead of asserting.

## 0. Read-first order (before touching anything)

1. `fiction_loop/CONTRIBUTING.md` — the constitution, 15 laws + case law. The
   project's declared FIRST READ for any maintenance session.
2. `fiction_loop/specs/intake_factory.spec.md` — THE factory spec (heavily
   updated today; stages 0–7, build list, sequencing).
3. `progress/factory-user-stories.md` + `progress/factory-user-manual.md` — the
   issue-finding instruments and their findings (SG-1..14 all closed in spec;
   six trial-and-error forces; post-fix confessions and their same-day
   resolutions).
4. `progress/addional_good_to_know.md` — the generalization map (pointers).
5. `fiction_loop/core/agent_conduct.md` — STOP-DON'T-GUESS, scope walls, cost
   rules. Binding on every agent.

## 1. What this session did (all committed; verify with `git log --oneline -10`)

| Commit | What |
|---|---|
| 1c8b51c | spec absorbed ch1–ch6 lessons (chassis list, 3 leaks as debt, 4 generation rules, concrete validation gate, parallel tracks) |
| 1757b6c | SG-1..14 closed: Stage 0 (intake/instancing/budget/delivery), accept-queue-refuse, derived sizing, repair loop, deadness reviewer, correction economics, redo policy, calibration pack, spec-sync rule, D10 |
| bbe56a1 | progress/ docs committed (were untracked) |
| bd488d9 | OWNER corrections: front door = MENU (continue existing / start new; precedent menu.py); refuse → DEFER (no unclassifiable books, taxonomy extensible) |
| 7372ed8 | stories: status epilogues + SIX TRIAL-AND-ERROR FORCES section |
| d3fe315 | stories: "the spec speaks again" — post-fix personification, 6 new confessions |
| d56d01e | confession defaults applied: ONE calibration organ (accepted + deferred/), redo policy amendments (redos budget-counted; auto-redo requires gate/refresh reorder), 4 dissolver build rows, §3 spec-readiness rule, clean-rewrite debt |
| 5309f0c | FI-1 EXECUTED: .gitignore `!fiction_loop/chapters/`, ALL prose in git for the first time (6 chapters + rejected/) |

## 2. LIVE state — CHECK before assuming

- **Chapter 6 (first return chapter, op_what_is_missing touch 2) was IN FLIGHT
  all session** — redo-from-brief after an F15 gate failure, assembler restarted
  09:16. It may be done, failed, or stalled by the time you read this.
  **Run `src/.venv/bin/python fiction_loop/tools/progress.py` (from repo root)
  and, if anything looks wrong, `fiction_loop/tools/analyst.py` — never guess.**
  Beware: logs/STATUS.md can be stale; trust file mtimes + analyst.
- `fiction_loop/chapters/chapter_006.md` at commit 5309f0c is the REJECTED F15
  draft, not a result. The pipeline's step 13.5 commits the real one when it
  lands.
- **When ch6 lands, review** (first-ever exercise of both): F14 life progression
  must be nameable and visible; correct_approach continuity; anchor
  manifestation must differ from ch5's "seen".
- Interpreter: use `src/.venv/bin/python`, never bare python (root venv lacks
  requests).

## 3. The method that emerged today (now binding)

- **Story treatment** is a §3 spec-readiness rule: a new/heavily-revised spec is
  not READY until it has a from-text-only user manual, a first-person
  personification, and a foreseen-issues register. Worked example = the two
  progress/ files (14 issues found pre-build, zero tokens).
- **Six forces** explain why improvements historically cost a paid chapter:
  (1) writer obedience measured never promised, (2) production-only test bench,
  (3) paid feedback loop, (4) rules as prose in copies, (5) deterministic steps
  run by LLMs, (6) no own failure catalog. Dissolvers for 1–4 are build-list
  rows in the spec.

## 4. Open work, in order

1. **BUILD, don't write** (standing warning from confession 2: build list grew
   10→14 rows, rows built = 0). First build = **pre-writer prompt gate**:
   deterministic script, runs after step 7.5 / before step 8, verifies the
   assembled prompt carries a HARD RULE matching every structural_gate check
   (quota / anchor / echo / F14 / F15 ↔ rules 7/8/9/10/12). Zero tokens,
   prevents paid gate failures. First test fixture: ch6's own logged prompt
   (logs/chapter_006/) which historically lacked the newcomer rule.
2. Remaining foreseen issues (FI-2..FI-11, from this session's forecast — full
   list in the session summary inside memory; key ones): gate-before-refresh
   reorder (6 consumers mapped — REQUIRED before auto-redo policy is
   implemented); null-blind check sweep (F14 pattern siblings); define "shown"
   before arc 3; the 3 chassis/pack leak fixes (anchor description + mirror
   content in assembler.md, QUOTA_BY_ARC in structural_gate.py); arc-1→2
   boundary fixtures; extractor content formulas; living-doc scale probe; quote
   anchoring format for the fidelity checker; per-model obedience card;
   transaction trio remainder (step 13.5 pathspec-limiting, redo-guard
   hardening — FI-1 gitignore part is DONE).
3. Factory Stages 1–2 are chapter-independent (calibratable against
   `fiction_loop/specs/genre_derivation.md`'s 5 worked books) — parallel track.

## 5. Owner interaction model (empirical, binding)

- **PROPOSE-AND-CORRECT, never interview.** Present a marked default and
  artifacts he can react to. He makes creative calls by correcting visible
  proposals, not by answering questions.
- **Findings ARE resolutions** (his ruling today): when an analysis names its
  own fix, apply the marked default — don't ask "what should I decide?".
  Reserve questions for true taste/ownership calls.
- The ONLY open owner decision: **D10** (rights/licensing of inputs/outputs) —
  matters only before third-party shipping. Don't push it.
- He never reads long docs; he reads stories and corrects specifics. Keep
  deliverables skimmable and reactable.

## 6. Operational rules that saved this session

- **Commit your spec/doc edits EARLY and pathspec-limited** — step 13.5's
  chapter commit is NOT yet pathspec-limited and will sweep uncommitted edits
  into a chapter transaction (ch4 incident).
- Never touch `fiction_loop/state/`, `prompts/`, `core/living_document.md`
  while a chapter is in flight; spend file `.pipeline_spend.json` is real money,
  never revert it.
- The pipeline runner is NOT Claude Code — different harness (subagents +
  shell, 300 s shell timeout). Specs/RUN.md stay harness-agnostic.
- This machine is a Raspberry Pi: no heavy greps over big files, no parallel
  heavy processes, especially while a pipeline is running.
- Verify before fixing (read the file, run the tool, check the actual error);
  on BLOCKED: analyst first, report verdict, never improvise (conduct §1).
