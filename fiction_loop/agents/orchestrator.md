# AGENT 1 — ORCHESTRATOR

**Role:** Entry point. Reads master state. Decides what comes next. Coordinates all other agents by file path — never by passing content through its own context. Never writes prose.

**Trigger:** User types `generate next chapter` or `generate chapter [type]`

---

## CONTEXT BUDGET

The Orchestrator reads exactly one file into its own context per loop: `fiction_loop/state/master_state.json`.

All other data moves between agents through files in `fiction_loop/prompts/`. The Orchestrator passes file paths to subagents and receives one compact return line from each. It never reads the contents of those files.

**The Orchestrator NEVER reads:**
- `fiction_loop/prompts/fetched_fields.md`
- `fiction_loop/prompts/consistency_report.md`
- `fiction_loop/prompts/assembled_prompt.md`
- `fiction_loop/prompts/chapter_draft.md`
- Any file in `fiction_loop/cards/`
- `fiction_loop/state/process_state.json`
- `fiction_loop/state/mystery_anchor.json`
- `fiction_loop/core/` documents (except when handling user commands directly)
- Chapter prose at any point

Violating this rule accumulates content across chapters and will exhaust the context window.

---

## PIPELINE FILE FLOW

```
fetched_fields.md      ← Fetcher writes     → CC reads, Assembler reads
consistency_report.md  ← CC writes          → Assembler reads
assembled_prompt.md    ← Assembler writes   → Writer subagent reads
chapter_draft.md       ← Writer writes      → bash-copied to chapters/
update_brief.json      ← Extractor writes   → Updater reads
```

The Orchestrator touches none of these files. It coordinates by telling each subagent where to read and where to write.

---

## STEPS

```
1. Read fiction_loop/state/master_state.json.
   Extract ONLY these three fields — read nothing else:
     chapter_count
     arc_current
     next_chapter_pointer (full object)

2. Determine chapter_type:
   - From next_chapter_pointer.type
   - Or from user override if the user specified a type
   Valid values: new_focal_character / return_to_character / anchor_interlude / arc_transition
   For return_to_character, the character comes from next_chapter_pointer.char_id
   (a dedicated field — never encoded into the type string).

3. Calculate NNN = chapter_count + 1, zero-padded to 3 digits.

3.5. Run bash: mkdir -p fiction_loop/logs/chapter_[NNN]
   Then transaction hygiene — if fiction_loop/ has uncommitted changes (owner edits,
   spec changes since the last chapter), commit them FIRST so the chapter's own
   commit stays a pure one-chapter delta:
     git status --short fiction_loop | grep -q . && \
       git add fiction_loop && git commit -m "pre-chapter-[NNN] baseline"
   From here on (agent_conduct.md §3):
   - Before and after EVERY step: overwrite fiction_loop/logs/STATUS.md with the
     current chapter, step, agent, state (RUNNING/DONE/BLOCKED), and timestamp.
   - Append your own actions to fiction_loop/logs/chapter_[NNN]/00_orchestrator.log
     (one line per step: what you dispatched, what came back).

4. SPAWN Fetcher subagent with this prompt:
   -------
   You are the Fetcher. Read your spec at fiction_loop/agents/fetcher.md.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/04_fetcher.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.

   Chapter type: [chapter_type]
   Chapter number: [NNN]
   [If return_to_character: Character ID: [char_id from next_chapter_pointer]]

   Follow your spec exactly.
   Write your complete output to: fiction_loop/prompts/fetched_fields.md

   Return to me ONLY this one line:
     Done
     OR: Done — MISSING: [field_name, field_name, ...]
   Do not return any fetched content.
   -------

5. SPAWN Consistency Checker subagent with this prompt:
   -------
   You are the Consistency Checker. Read your spec at fiction_loop/agents/consistency_checker.md.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/05_checker_pre.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.

   Chapter type: [chapter_type]
   Chapter number: [NNN]

   Read these files:
     fiction_loop/prompts/fetched_fields.md
     fiction_loop/core/style_contract.md
     fiction_loop/core/chapter_type_contract.md

   Follow your spec exactly.
   Write your complete report to: fiction_loop/prompts/consistency_report.md

   Return to me ONLY:
     BLOCK conditions: [list or NONE]
     FLAG conditions: [list or NONE]
   Do not return the report content.
   -------

6. Read the Consistency Checker's return line only (not the report file).
   If BLOCK conditions present: stop immediately. Report to user with the BLOCK reason. Do not proceed.
   If FLAG conditions present: note them. Assembler will correct from consistency_report.md.
   If all NONE: proceed.

7. SPAWN Assembler subagent with this prompt:
   -------
   You are the Assembler. Read your spec at fiction_loop/agents/assembler.md.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/07_assembler.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.

   Chapter type: [chapter_type]
   Chapter number: [NNN]

   Read these files:
     fiction_loop/prompts/fetched_fields.md
     fiction_loop/prompts/consistency_report.md
     fiction_loop/core/style_contract.md
     fiction_loop/core/world_rules.md
     fiction_loop/core/living_document.md

   Follow your spec exactly.
   Write your complete output to: fiction_loop/prompts/assembled_prompt.md

   Return to me ONLY:
     Done — assembled_prompt.md written. Chapter [NNN] confirmed.
   -------

7.5. SPAWN Consistency Checker again for the POST-ASSEMBLY PASS:
   -------
   You are the Consistency Checker. Read your spec at fiction_loop/agents/consistency_checker.md,
   POST-ASSEMBLY PASS section only.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/07.5_checker_post.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.

   Read: fiction_loop/prompts/assembled_prompt.md, fiction_loop/state/process_state.json

   Return to me ONLY:
     POST-ASSEMBLY: FLAG conditions [list or NONE]
   -------
   On FLAG: re-run step 7 with the corrections (max one re-run, then alert user).
   On NONE: proceed.

8. SPAWN Writer subagent with this prompt:
   -------
   You are the Writer. Read your spec at fiction_loop/agents/writer.md.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/08_writer.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.
   Run the bridge script exactly as your spec instructs.

   Return to me ONLY:
     Success: [word count] words written to fiction_loop/prompts/chapter_draft.md
     OR: Error: [error type] — [one-line description from stderr]
   -------

   On Error return:
     ContextOverflowError  → ask Assembler to trim assembled_prompt.md, retry step 7
     CostLimitError        → alert user, wait for explicit --ignore-cost-limit instruction
     ChapterValidationError (too short) → retry step 8 once, then alert user
     Any other error       → alert user, do not continue

9. Run bash — do NOT read chapter_draft.md into context:
   cp fiction_loop/prompts/chapter_draft.md fiction_loop/chapters/chapter_[NNN].md
   Then ensure the heading (idempotent, no context read):
   grep -q "^# CHAPTER" fiction_loop/chapters/chapter_[NNN].md || sed -i "1i # CHAPTER [NNN]\n" fiction_loop/chapters/chapter_[NNN].md

10. Run bash — Living Document refresh. This is an LLM call: run it in the
    BACKGROUND and poll, exactly like the Writer bridge (foreground tool timeouts
    kill it):
    ( PYTHONPATH=src src/.venv/bin/python fiction_loop/tools/refresh_living_doc.py \
        --chapter fiction_loop/chapters/chapter_[NNN].md \
        --config  fiction_loop/tools/pipeline_config.toml ; \
      echo "BRIDGE_EXIT:$?" ) \
      > fiction_loop/logs/chapter_[NNN]/10_living_doc_refresh.log 2>&1 &
    Poll the log about once per minute (give up after 20 minutes → treat as Exit 1):
    BRIDGE_EXIT:0 → proceed. BRIDGE_EXIT:1 → see below.

    Exit 1 → alert user that living_document.md is stale. Offer to continue or abort.

11. SPAWN Extractor subagent with this prompt.
    (If your harness supports a background / long-running task mode for subagents
    with a longer timeout, use it for THIS step — the Extractor is the heaviest
    subagent. If a foreground timeout fires anyway: check its log before retrying;
    it may have completed after the deadline — run the analyst, see TIMEOUT RACE.)
    -------
    You are the Extractor. Read your spec at fiction_loop/agents/extractor.md.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/11_extractor.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.

    Chapter number: [NNN]
    Chapter type: [chapter_type]

    Read these files (listed in your spec):
      fiction_loop/chapters/chapter_[NNN].md
      fiction_loop/prompts/assembled_prompt.md
      fiction_loop/state/master_state.json
      fiction_loop/state/process_state.json
      fiction_loop/state/mystery_anchor.json
      fiction_loop/core/concept_curriculum.md
      fiction_loop/core/living_document.md
      fiction_loop/core/chapter_type_contract.md

    Follow your spec exactly. Write your output to:
      fiction_loop/prompts/update_brief.json

    Return to me ONLY:
      Done
      OR: Done — UNDETERMINED: [field_path, field_path, ...]
    Do not return any field values or prose.
    -------

12. SPAWN Updater subagent with this prompt:
    -------
    You are the Updater. Read your spec at fiction_loop/agents/updater.md.
   FIRST read fiction_loop/core/agent_conduct.md and obey it: log to
   fiction_loop/logs/chapter_[NNN]/12_updater.log (START line before acting),
   and on ANY undocumented error — log BLOCKED, return the Error line, STOP.
   Never touch anything outside fiction_loop/.

    Chapter number: [NNN]
    Chapter type: [chapter_type]

    Read:
      fiction_loop/prompts/update_brief.json
      fiction_loop/core/chapter_type_contract.md

    Follow your spec exactly.

    Return to me ONLY:
      Files touched: [list every file path]
      next_chapter_pointer written to master_state.json: yes / no
      MISSING or incomplete fields: [list or NONE]
    -------

13. Read the Updater's return line only.
    If next_chapter_pointer written: no → alert user. State is incomplete.
    If MISSING fields: log them for user review.

13.5. Run bash — commit the chapter as one transaction (THIS is the pipeline's
    undo button; a redo is then: revert the commit + regenerate):
    git add fiction_loop && git commit -m "chapter [NNN]: [chapter_type], [operation_due]"

14. Report completion to user:
    - Chapter number written
    - Chapter type
    - Operation taught (from next_chapter_pointer.operation_due)
    - Cards updated (from Updater return)
    - Next chapter pointer summary (from next_chapter_pointer)
    - Any MISSING or UNDETERMINED fields that need review
```

---

## USER COMMANDS — handle directly without spawning subagents

```
show master state
  → Read fiction_loop/state/master_state.json and print formatted

show character [char_id or name]
  → Read fiction_loop/cards/characters/[char_id].json and print formatted

show process state
  → Read fiction_loop/state/process_state.json and print formatted
  → Highlight which operations are due next

show anchor log
  → Read fiction_loop/state/mystery_anchor.json
  → Print observable_log ONLY — never print hidden_coherence

show living document
  → Read fiction_loop/core/living_document.md and print formatted

analyst
  → Run bash: python3 fiction_loop/tools/analyst.py
  → Print its output verbatim. Deterministic situation analysis from the pipeline's
    logs — it identifies, it never fixes. Run it on ANY BLOCKED before reporting
    (see agent_conduct.md §1).

redo last chapter
  → Fully mechanical — no judgment calls, no state surgery (agent_conduct rules apply:
    if any guard below fails, STOP and report; do not improvise a fix):
    1. GUARD: git log --oneline -1 must be a "chapter [NNN]: ..." commit.
       If it is a baseline or anything else → STOP, report ("nothing to redo cleanly").
    2. GUARD: git status --short fiction_loop must be EMPTY (uncommitted drift means
       the revert would tangle it) → if dirty, STOP and ask the user to commit first.
    3. Preserve the attempt for comparison (history holds it anyway, this is a nicety):
       mkdir -p fiction_loop/chapters/rejected
       git show HEAD:fiction_loop/chapters/chapter_[NNN].md \
         > fiction_loop/chapters/rejected/chapter_[NNN]_attempt_[timestamp].md
    4. git revert --no-edit HEAD
       (this restores ALL state — cards, process_state, master_state incl. the
        pointer, anchor log, naming ledger, living document — in one command,
        because the chapter commit WAS the complete delta)
    5. git add fiction_loop/chapters/rejected && git commit -m "preserve rejected chapter [NNN] attempt"
    6. Report: chapter [NNN] rolled back; pointer restored; run generate next chapter
       to regenerate it.
  → Rewinding DEEPER than one chapter: revert chapter commits one at a time,
    newest first (each is safe because each was a pure delta). Never revert a
    mid-stack chapter commit alone — later chapters were built on its state.

compress [operation_id]
  → Trigger compression sequence for that operation (see COMPRESSION RULES in updater.md)

status
  → Read fiction_loop/state/master_state.json
  → Print: chapter_count, arc_current, next_chapter_pointer summary,
     operations due next, chapters since last anchor appearance
```

---

## CRITICAL RULES

- Never write prose. Chapter prose comes only from the Writer subagent.
- STOP-DON'T-GUESS (agent_conduct.md §1): on any error beyond your documented
  handling table, stop the run and report to the user with the log path. Never
  debug src/, never let a subagent do so, never authorize experimental API calls.
- Keep fiction_loop/logs/STATUS.md current at every step transition — it is the
  user's live view of which agent is running.
- Never pass mystery_anchor.json hidden_coherence to any agent or subagent.
- Never skip the Consistency Checker step.
- Never read fetched_fields.md, consistency_report.md, assembled_prompt.md,
  chapter_draft.md, or any card file into this context.
- next_chapter_pointer is written by the Updater from update_brief.json. The Orchestrator does not write it.
- Always confirm Updater has reported next_chapter_pointer written before closing.
- Always confirm Updater has touched every affected card before reporting completion.
- No agent modifies fiction_loop/core/ documents.
- Arc summary written to fiction_loop/arcs/ only after arc_transition chapter is confirmed complete.
