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
- HARNESS FAILURES ARE ERRORS TOO. A failed subagent spawn, a file-tool refusal,
  a denied permission, a missing capability (e.g. no clock) — these fall under
  this rule even though they come from your harness, not the pipeline. Exactly
  ONE retry of the IDENTICAL operation is permitted for transient harness
  friction (e.g. a file tool that requires reading a file before overwriting
  it — read your own output file, ignore its stale content, retry the write).
  The failure AND the retry MUST be logged and MUST appear in your final report
  to the user. A recovery that requires changing approach is not friction — it
  is BLOCKED. Silently absorbing any failure is a conduct violation.
  (Case law 2026-07-17, ch-006 run: a failed Fetcher spawn and several file-tool
  refusals were absorbed silently; none reached the owner's report.)
- The Orchestrator, on receiving an undocumented Error: STOP THE RUN, then run the
  deterministic analyst (zero tokens, zero improvisation — it analyses, it never
  fixes):
    .venv/bin/python fiction_loop/tools/analyst.py
  and report to the user with the analyst's verdict + the log path. If the analyst
  says "unknown signature", say exactly that — never fill the gap with guesses.

## 2. SCOPE WALLS

- No agent reads or modifies ANYTHING outside `fiction_loop/` — not `src/`, not
  repo config, not the environment. Exactly THREE sanctioned exceptions:
  (1) the git transaction commands the orchestrator spec itself prescribes
  (steps 3.5, 13.5, `redo last chapter`) — always with pathspec `fiction_loop`;
  (2) the bridge scripts' documented read of the repo-root `.env`;
  (3) running `tools/analyst.py` / `tools/progress.py` and reading their output.
  Anything else outside fiction_loop/: report and stop.
- `.env` CONTENTS ARE SECRETS. No agent ever prints, cats, or greps `.env` —
  existence may be checked ONLY with `test -f .env` (exit code, no output).
  Only the bridge scripts read its contents, in-process. (Case law 2026-07-17:
  the orchestrator grepped `.env` for the API key while diagnosing; had the key
  existed, it would now sit in a transcript.)
- Within `fiction_loop/`, write only the files your spec names as your outputs.
- Never modify `fiction_loop/core/` (single exception: Updater STEP 8B appends to
  the character_naming.md ledger) or `fiction_loop/tools/`.
- The wall includes ALL repo-root orientation and planning documents —
  `HANDOFF.md`, `tickets/`, `progress/`, `innovations/`, `CLAUDE.md`,
  `AGENTS.md` — and `fiction_loop/CONTRIBUTING.md`. Those are maintainer
  orientation; RUN.md's kickoff prompt restates this as the ROLE FENCE.
  (Case law 2026-07-18: the ch8 driver read HANDOFF.md and tickets/ — both
  outside fiction_loop/ — then ran the Updater on a gate-FAILED brief in one
  incident and refused a documented resume in another.)

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
chapter: 001 | step: 08 | agent: writer | state: RUNNING | since: [YYYY-MM-DDTHH:MM]
last completed: 07.5 checker_post — POST-ASSEMBLY: NONE
```

**Per-agent log format** — append-only, plain lines, SHORT (bullet facts, never
transcripts, never file contents):
```
[HH:MM:SS] START — chapter 001, task: [one line]
[HH:MM:SS] [action taken] → [result in a few words]
[HH:MM:SS] DONE — [the exact return line sent to Orchestrator]
   or
[HH:MM:SS] BLOCKED — [verbatim error]. Stopping per agent_conduct.md §1.
```

Rules:
- TIMESTAMPS COME FROM THE SHELL, at write time: `date '+%H:%M:%S'` for log
  lines, `date -u '+%Y-%m-%dT%H:%M'` for STATUS.md `since:`. NEVER write a
  remembered, estimated, or example timestamp — you have no clock; an invented
  time is receipt forgery, and the analyst's stall/race detection consumes these
  fields. If you truly cannot run the shell, write `[no-clock]` instead.
  (Case law 2026-07-17: every agent in the ch-006 run copied `18:41:xx` from the
  examples formerly printed above; the real run was 23:05–23:17. File mtimes were
  the only honest record left.)
- DONE means success, and nothing else. On any failure the terminal line is
  `BLOCKED — ...` — never `DONE — Error: ...`. (Case law 2026-07-17: a
  `DONE — Error:` writer log line made analyst.py report a false TIMEOUT RACE
  and advise resuming from the NEXT step while a stale draft sat in
  chapter_draft.md.)
- Write the START line BEFORE doing anything (a stuck run must show where it stuck).
- Log every bash command you run and every file you write, one line each.
- Log deviations loudest: anything you did that your spec didn't literally say —
  including harness failures you retried past (§1).
- The Writer logs each bridge-script invocation and its exit code + stderr summary —
  an API call that happened but failed is exactly what the owner needs to see.

## 4. COST AWARENESS

Every call through the bridge scripts costs money and is rate/limit-tracked.
Calls exist only where the specs place them (steps 8 and 10, plus documented
retries). "Let me test if this fixes it" is not a documented call.
