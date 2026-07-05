# CONTRIBUTING — THE LAWS OF fiction_loop

Read this BEFORE fixing any bug or extending anything. This is the maintainer-facing
constitution: how changes are made without turning the system into glue. The
runtime rules for agents DURING a chapter run live in `core/agent_conduct.md`;
this file governs changes TO the system between runs.

There are always ten valid-looking ways to fix a bug here. Nine of them contradict
an existing contract. This file exists so any maintainer — human or AI, of any
capability — picks the tenth. Every law below was paid for by a real incident,
cited as case law. When in doubt, the law with the lower number wins.

---

## 1. WHAT THIS SYSTEM IS (read this or misunderstand everything)

fiction_loop is a **file-state machine operated by disposable LLM sessions**.

- ALL state lives in files. No session, context window, or conversation holds
  anything that matters. A session can be killed at any step and a fresh one
  resumes from files alone. This is why "one session per chapter costs nothing."
- Agents are **interpreters of contracts, not owners of logic**. An agent prompt
  (`agents/*.md`) may interpret prose; it must never be the only place a number,
  threshold, or schema lives.
- Modularity here is real, just not class-shaped. The equivalents:

| Code concept | fiction_loop equivalent |
|---|---|
| Interface / API | The pipeline files (`prompts/*.md`, `update_brief.json`) + one-line agent returns |
| Encapsulation | CONTEXT BUDGET — the Orchestrator never reads content files; subagents see only their spec'd inputs |
| Type system | The determinism boundary (LAW 3) — countable things are code, not judgment |
| Dependency graph | `core/field_registry.md` — every field/rule has registered producers and consumers |
| Unit tests | Deterministic zero-token tools: `structural_gate.py`, `analyst.py` |
| Transactions | One chapter = one git commit; state mutates only at step 12 (Updater) |
| Architecture decision records | `human_decision.md` (taste) + registry case law (mechanics) |

## 2. THE LAYER MODEL (where does this change belong?)

```
L0  CANON      core/ reference docs (world_rules, style_contract, concept_curriculum,
               correspondence_map, character_naming) — hand-authored content.
               Pólya-derived content MUST be verified against the source epub
               (sourcing rule, specs/README.md). Owner-approved changes only.
L1  CONTRACTS  field_registry.md, chapter_type_contract.md, the pipeline file flow,
               one-line return formats, update_brief schema. Change = registry
               audit in the same sitting (LAW 4).
L2  AGENTS     agents/*.md — prompts interpreting L0/L1. May be edited freely
               BETWEEN runs, but every MUST they impose obeys LAW 5 (hard channel)
               and every number they use is a registered copy of an L0/L1 source.
L3  TOOLS      tools/*.py — deterministic, stdlib-only, zero tokens. They analyze,
               count, and report; they never write state and never call LLMs
               (bridge scripts invoke_writer / refresh_living_doc are the two
               sanctioned exceptions — the ONLY code that spends money).
L4  STATE      state/ + cards/ + chapters/ — written ONLY by the Updater (step 12)
               inside a chapter transaction, or by the documented undo ladder,
               or by owner-approved seeded surgery WITH receipts committed.
```

Dependencies point downward only: agents read contracts and canon; tools read
receipts and state; state depends on nothing. A change that makes an upper layer
depend on a lower layer's internals (e.g. an agent prompt hardcoding a tool's
threshold) is wrong even if it works.

## 3. THE LAWS

**LAW 1 — STOP, DON'T GUESS.** Any error or ambiguity not covered by a documented
handling table: stop, run `tools/analyst.py`, report. Never experiment with paid
calls; never debug `src/`. *(Case law: chapter-001 subagent burned 500k+ tokens
guessing; `core/agent_conduct.md` was written in response and governs runtime.)*

**LAW 2 — SINGLE SOURCE OF TRUTH.** Every number, threshold, name, and rule has
exactly ONE owning document. Every other appearance is a copy and MUST be listed
in `field_registry.md` next to its source. Changing the source without updating
listed copies is the change; forgetting a copy is the bug. *(Case law: the arc
cast quota lives in curriculum §9 and is copied in assembler.md and
structural_gate.py QUOTA_BY_ARC — tuning one without the others makes the gate
reject correct chapters.)*

**LAW 3 — THE DETERMINISM BOUNDARY.** If a step can be decided by arithmetic,
counting, table lookup, or string templating over already-structured data, it is
code (L3 or `specs/`), never an LLM judgment. If a check CAN be deterministic it
MUST be. *(Case law: word-count floors could not see an under-populated cast;
`structural_gate.py` counts the brief and caught it on its first live run.)*

**LAW 4 — REGISTER PRODUCERS AND CONSUMERS, THEN AUDIT.** No new field without a
registry row naming both producer and consumer (a field with only one is dead
work or a silent default — both bugs). After ANY rule change, grep the rule's key
phrases across `agents/ core/ tools/ RUN.md` and update or exempt every hit IN
THE SAME SITTING. *(Case law: four incidents in the registry's RULE-CHANGE AUDIT
section, all born in the gap between "rule changed" and "consumers audited
later"; also: the living document's consumer list was stale, which nearly hid
that a rejected chapter's canon leaks into the next prompt.)*

**LAW 5 — HARD REQUIREMENTS GO IN THE HARD CHANNEL, FULLY SPELLED OUT.** The
Writer model obeys the HARD RULES block (final section, explicit, self-check
instruction) near-100% and treats mid-brief text as advisory. Any MUST goes in
the block with its full content inline — never by reference to elsewhere in the
prompt, never as an ambiguous placeholder. *(Case law: rule 7 said "fill in the
arc's number here"; the Assembler wrote "Arc 1." instead of "THREE" and two
chapter attempts shipped under-populated before the placeholder was fixed.)*

**LAW 6 — PREVENTION > DETECTION > CORRECTION.** Prefer making the violation
impossible to produce (template quarantine, enums, drawn-not-invented identity)
over checking for it afterward, and prefer deterministic detection over redo
loops. *(Owner rule, 2026-07-02; the prevention layer eliminated all three
chapter-1 violation classes in one move.)*

**LAW 7 — GATES BEFORE SPEND.** Deterministic verification runs before the next
paid call and before any state mutation, wherever the data allows. *(Known
standing violation, documented and accepted for now: the living-doc refresh
(paid) runs at step 10, before the structural gate at 11.5 — every rejection
wastes one call and pollutes the living doc. The mapped fix is a 6-consumer
reorder; do not "quick-fix" it partially.)*

**LAW 8 — STATE MUTATES ONCE, TRANSACTIONALLY.** Only the Updater (step 12)
writes L4, and one chapter is one commit. Anything else uses the staged undo
ladder (RUN.md), cheapest rung first: redo generation → redo from brief → undo
state application → redo last chapter. Hand surgery on state requires owner
approval, receipts (`update_brief.json`, `.bak` files), and its own commit.
Governance/spec commits are pathspec-limited and NEVER ride inside a chapter
transaction. *(Case law: chapter 004 v1's commit swept mid-flight spec edits and
had to be surgically reverted; note the standing defect — `.gitignore:28` still
keeps prose out of commits, so "commit = complete delta" is not yet true.)*

**LAW 9 — RECEIPTS EVERYWHERE, ANALYST FIRST.** Every run leaves deterministic
evidence: STATUS.md, per-agent logs (START before acting), the brief, spend file,
`.bak` files. `analyst.py` must be able to diagnose from receipts alone; every
new failure signature gets added to its table. The spend file records real money
and is NEVER reverted. Debugging starts with `python3 fiction_loop/tools/analyst.py`,
not with reading prose.

**LAW 10 — CONTEXT BUDGET IS CORRECTNESS, NOT OPTIMIZATION.** The Orchestrator
never reads content files; subagents return one line; data moves by file path.
Violations don't fail fast — they compound until a long-book session dies. Any
new agent or step must state its inputs, its output file, and its one-line
return before it exists.

**LAW 11 — ANTI-FORMULA IS ENFORCED BY TRACKED STATE, NEVER ASSUMED.** Reader-
visible variety (anchor manifestation, featured failure mode, echo context,
name-delivery vehicle) must be driven by a recorded rotation the pipeline can
read — an enum, a history array, a least-recently ledger — never left to LLM
creativity or to a metric that can saturate. *(Case law: "least recently shown"
permanently ties when the arc quota equals the pool size; the executor was
featured three chapters running before `failure_mode_lead_history` existed.
Free-text echo labels defeated dedupe until the context enum, owner D4.)*

**LAW 12 — FIX THE PRODUCING DOCUMENT, NOT THE ARTIFACT.** Never hand-edit
`assembled_prompt.md`, a chapter, or a brief to pass a check. Find the document
that produced the defect (usually L2 or L1), fix it there, and re-run the
cheapest ladder rung so the artifact is regenerated legitimately.

**LAW 13 — TASTE BELONGS TO THE OWNER, AS A LEDGER ENTRY.** Anything that changes
what the finished book feels like (pedagogy, pacing, cast, mystery, naming) is a
DECISION, recorded in `human_decision.md` with options and a marked default —
presented propose-and-correct style (a visible proposal to react to), never as an
open interview question. Mechanical consequences of a recorded decision are
ordinary work and need no new ask.

**LAW 14 — CHASSIS AND PACK STAY SEPARATE (the generic-tool law).** The machinery
(agents' procedures, tools, contracts, these laws) is the chassis; everything
about Pólya, gates, Africa, the grey-coat observer is the pedagogy pack and
belongs in `core/` docs, cards, and state — never hardcoded into an agent
procedure or a tool. Before adding ANY literal content string to `agents/*.md`
or `tools/*.py`, ask: "would this survive swapping the book?" If no, it goes in
a `core/` doc the agent is told to read. Known accepted debts (do not add more):
the anchor's physical description in assembler.md; wrong-approach mirror content
quoted into assembler.md rather than fetched from world_rules §5.
*(This law is what makes `specs/intake_factory.spec.md` — book in, loop out —
buildable without rewriting the machinery.)*

## 4. BUG-FIX PROCEDURE (the algorithm)

1. `python3 fiction_loop/tools/analyst.py`. Trust it. "Unknown signature" means
   say exactly that — then investigate receipts, not hypotheses.
2. Classify the defect by layer (§2). Symptom guide:
   - prose violates a rule → L2 (usually the brief induced it — check the
     assembled prompt before blaming the Writer model)
   - two documents disagree → L1 (registry: who owns it? fix copies from source)
   - a check missed something countable → L3 (extend the gate/analyst)
   - state is wrong → L4 (undo ladder rung, never hand-edit mid-run)
   - the book feels wrong → L0/LAW 13 (owner decision, not a code fix)
3. Before editing: look up every touched field/rule in `field_registry.md`.
   If it has no row, add the row FIRST — you are the person discovering this
   dependency; the next AI shouldn't have to.
4. Fix at the owning document; update every registered copy in the same sitting;
   append case law to the registry if you found a new bug class.
5. Verify with zero-token tools (gate, analyst, JSON parse, grep the artifact).
   Paid verification happens only via the normal pipeline, cheapest rung.
6. Commit pathspec-limited, governance separate from chapter transactions,
   message stating the law/incident that motivated it.
7. Hitting taste, ambiguity, or an undocumented fork → stop, write the DECISION
   proposal with a marked default (LAW 13). Do not pick silently.

## 5. EXTENSION PROCEDURE

- **New field**: registry row first (producer AND consumer, or don't add it) →
  schema → producer spec → consumer spec → seed/migrate existing state with a
  receipt commit. *(Precedent: `lead_failure_mode` → `failure_mode_lead_history`,
  commit e60f541.)*
- **New check**: if countable → `structural_gate.py` (or a new L3 tool), placed
  before spend/mutation per LAW 7; if judgment → Consistency Checker spec, with
  its stage (pre / post-assembly) stated. Register what it reads.
- **New hard requirement on the Writer**: HARD RULES block, content inline
  (LAW 5), plus — if countable — its deterministic twin in the gate. A hard rule
  without a gate check is a wish.
- **New agent or step**: conduct header + log path + one-line return + declared
  file inputs/outputs (LAW 10) BEFORE writing its procedure; then update
  orchestrator steps, `progress.py` STEPS table, `analyst.py` expectations,
  agent_conduct §3 log layout, and RUN.md — the step order has six consumers.
- **New chapter type**: column in `chapter_type_contract.md` first, then branch
  guards in every consumer the contract row lists.
- **New book (the real goal)**: nothing in this file changes. If generalizing
  forces a law change here, the design has a chassis/pack leak — find it first.

## 6. DOCUMENT MAP (who owns what)

| Document | Owns |
|---|---|
| `RUN.md` | Operating the loop: kickoff, redo/rollback ladder, practical advice |
| `core/agent_conduct.md` | Agent behavior DURING a run (stop-don't-guess, scope, logging) |
| `core/field_registry.md` | Data + rule dependency graph, case law, open items |
| `core/chapter_type_contract.md` | Which brief sections exist per chapter type |
| `human_decision.md` | Owner taste decisions ledger (resolved; append new forks) |
| `specs/README.md` + `specs/*` | The code/AI boundary; implementation-ready specs; sourcing rule |
| `logs/`, `state/.pipeline_spend.json` | Receipts (never reverted) |
| **this file** | How to change any of the above without contradiction |
