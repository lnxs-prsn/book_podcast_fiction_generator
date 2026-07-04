# AGENT CONDUCT — READ BEFORE ACTING (every agent, every chapter)

Applies to the Orchestrator and every subagent. Referenced from every spawn prompt.
Exists because a chapter-001 subagent burned 500k+ tokens guessing at fixes and
modifying files outside its scope. The owner's rule: **problems are reported, not
improvised around. Stopping is cheap. Guessing costs real money per attempt.**

---

## 1. STOP — DON'T GUESS

- The ONLY permitted self-healing is what your spec's error table explicitly
  documents (e.g. Writer: retry once on ChapterValidationError-too-short). Nothing else.
- Any error, unexpected state, or ambiguity NOT covered by your spec:
  1. Write a BLOCKED entry to your log (see §3) with the verbatim error,
  2. Return one line to the Orchestrator: `Error: [type] — [one line]`,
  3. STOP. Do not retry with variations. Do not investigate src/. Do not test
     hypotheses — every LLM/API call costs money; a human answer costs nothing.
- The Orchestrator, on receiving an undocumented Error: STOP THE RUN and report to
  the user with the log path. Never debug on the user's behalf.

## 2. SCOPE WALLS

- No agent reads or modifies ANYTHING outside `fiction_loop/` — not `src/`, not
  repo config, not the environment. If you believe the problem is outside
  `fiction_loop/`, that is precisely what you report and precisely why you stop.
- Within `fiction_loop/`, write only the files your spec names as your outputs.
- Never modify `fiction_loop/core/` (single exception: Updater STEP 8B appends to
  the character_naming.md ledger) or `fiction_loop/tools/`.

## 3. LOGGING PROTOCOL

All logs live under `fiction_loop/logs/chapter_[NNN]/` — one directory per chapter,
so old runs never pollute new ones.

```
fiction_loop/logs/
  STATUS.md                      ← overwritten at every transition: what runs NOW
  chapter_001/
    00_orchestrator.log
    04_fetcher.log
    05_checker_pre.log
    07_assembler.log
    07.5_checker_post.log
    08_writer.log
    10_living_doc_refresh.log    ← orchestrator writes (bash step)
    11_extractor.log
    12_updater.log
```

**STATUS.md** (Orchestrator overwrites before and after every step):
```
chapter: 001 | step: 08 | agent: writer | state: RUNNING | since: 2026-07-02T18:41
last completed: 07.5 checker_post — POST-ASSEMBLY: NONE
```

**Per-agent log format** — append-only, plain lines, SHORT (bullet facts, never
transcripts, never file contents):
```
18:41:02 START — chapter 001, task: [one line]
18:41:30 [action taken] → [result in a few words]
18:44:10 DONE — [the exact return line sent to Orchestrator]
   or
18:44:10 BLOCKED — [verbatim error]. Stopping per agent_conduct.md §1.
```

Rules:
- Write the START line BEFORE doing anything (a stuck run must show where it stuck).
- Log every bash command you run and every file you write, one line each.
- Log deviations loudest: anything you did that your spec didn't literally say.
- The Writer logs each bridge-script invocation and its exit code + stderr summary —
  an API call that happened but failed is exactly what the owner needs to see.
```

## 4. COST AWARENESS

Every call through the bridge scripts costs money and is rate/limit-tracked.
Calls exist only where the specs place them (steps 8 and 10, plus documented
retries). "Let me test if this fixes it" is not a documented call.
