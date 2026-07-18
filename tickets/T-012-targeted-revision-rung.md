# TICKET T-012: targeted-revision rung — surgical fix replaces blind re-roll for checkable misses

```
Mode: alone
Depends-on: none of the un-landed tickets. T-007..T-011 already MERGED
            (queue clean at 1fa915b). Independent of T-013/T-014.
Timing: BETWEEN runs only — no chapter run in flight. Chapter 008 is
        ABANDONED (handoff §9), so this is dispatchable now.
Worktree: main working tree, repo root
Write-set: fiction_loop/tools/invoke_writer.py,
           fiction_loop/agents/orchestrator.md (ladder rung + step-8 error
           table line only),
           fiction_loop/RUN.md (undo/redo ladder text only),
           fiction_loop/core/field_registry.md (deficiency artifact row)
Hot-files: invoke_writer.py (T-010), orchestrator.md (T-007..T-011)
State-access: READ-ONLY read of state/process_state.json (label source,
              already used by validate_forbidden_labels). No writes to
              state/, no writes to chapters/. Writes ONLY to
              prompts/ (the deficiency report + the revised draft).
Paid-calls: ONE targeted-revision call per --revise invocation, and ONLY
            under the same cost-limit machinery as generation. This
            ticket's acceptance is ENTIRELY OFFLINE (--dry-run + fixtures);
            live proof that a revision actually converges rides the next
            owner-started chapter run, exactly like T-008's reorder.
```

Read `fiction_loop/CONTRIBUTING.md` first — LAW 3 (deterministic where it
can be), LAW 9 (never the non-idempotent agent), LAW 15 (no machinery that
cannot fire).

## 1. Problem (the arithmetic, confirmed live on chapter 008)

Each hard rule holds ~92–95% per pass; with ~12 simultaneous hard rules the
joint pass rate of a single generation roll is ~0.93¹² ≈ 40%. Chapter 008
rolled three times and missed a DIFFERENT rule each time (attempt 1: anchor
absent; attempt 2: HARD RULE 1 label leak; attempt 3: anchor absent again).
That is not malfunction — it is exactly what a 40%-per-roll process looks
like, and the misses land on different rules because each roll is an
independent sample.

The repair rung is the wrong shape. `redo generation` throws away the whole
draft and pours a fresh 40% roll. For a CHECKABLE, SURGICAL miss — a label
in narration, a coda one sentence too long, a single "the room was showing"
telling — holding the other 11 constraints while COPYING the good 95% of
the draft and correcting only the flagged span is a far easier task than
holding all 12 while INVENTING from scratch. The machine has no station for
that. This ticket adds it.

Scope boundary (honest): revision is for SURGICAL misses. A whole-scene
omission (the anchor torn-page scene absent entirely) is closer to
inventing than copying and stays on `redo generation` — the ladder routes
it there (§3.3). Do not try to make revision reconstruct a missing scene.

## 2. Design (single outcome, LAW 2/3)

Two new modes on `invoke_writer.py`, plus a ladder rung. No new tool; the
bridge already owns prose validation (T-010's label check) and the cost
machinery.

**2.1 `--check-prose PATH` — structured deficiency emission (no API call).**
Runs the prose-level deterministic checks the bridge owns and emits a
machine-readable report. Today that is exactly ONE check — the forbidden
narration labels (T-010's `validate_forbidden_labels`). Refactor that
validator to RETURN a list of deficiency records instead of only
printing/raising; `--check-prose` writes them to
`fiction_loop/prompts/prose_deficiencies.json` (empty list + exit 0 when
clean; the list + exit 1 when not) and mirrors human-readable lines to
stderr (keep the existing WARN/VIOLATION wording for continuity). The
existing `--check-labels` behaviour (raise `LabelLeakError`, exit 1) is
preserved as a thin wrapper so nothing that calls it today breaks.

Deficiency record shape (stable contract — T-014 and any future check emit
the SAME shape so the revision prompt is uniform):
```
{ "check": "forbidden_label", "rule": "HARD RULE 1",
  "line": 49, "detail": "narration label 'the executor'",
  "excerpt": "She sat on the stool ..." }
```

**2.2 `--revise DRAFT --deficiencies FILE [--dry-run]` — the rung.**
Assembles a targeted-revision prompt BY THE TOOL (no human composes it):
the full current draft, then the deficiency list rendered as an explicit
correction checklist, under a fixed instruction — "Return the chapter
unchanged EXCEPT for the flagged problems; correct ONLY those; do not
rewrite, re-order, or re-invent anything else." `--dry-run` writes the
assembled prompt to `fiction_loop/prompts/revision_prompt.md` and exits 0
WITHOUT calling the API (this is the offline acceptance hook). Without
`--dry-run` it makes ONE paid call through the SAME cost-limit /
CostLimitError path as generation, writes the revised draft to
`fiction_loop/prompts/chapter_draft.md`, then:
  - re-runs `--check-prose` on the result;
  - computes a diff-size guard: `difflib` changed-line ratio of revised
    vs. original. If ratio > `REVISION_MAX_DIFF_RATIO` (module constant,
    default 0.25 — the guard against the model "helpfully" rewriting),
    do NOT adopt the revision: restore the original draft, print
    `RevisionOverreachError` with the ratio, exit nonzero.
  - if checks still fail after adoption, exit nonzero (the ladder decides
    whether to revise again or fall to redo).

**2.3 Escalation lives in the LADDER, not the tool** (keeps the tool
stateless — LAW 9 spirit). The tool does at most one revision per call; the
orchestrator calls it at most TWICE, then falls to `redo generation`.

## 3. Fix

**3.1 invoke_writer.py:**
- Refactor `validate_forbidden_labels` to build and return a list of
  deficiency records (§2.1 shape); keep a wrapper that preserves the
  raise-on-violation `--check-labels` contract.
- Add `--check-prose PATH`: run the prose checks, write
  `prompts/prose_deficiencies.json`, exit 0/1 as above.
- Add `--revise DRAFT --deficiencies FILE [--dry-run]` per §2.2, including
  `RevisionOverreachError`, `REVISION_MAX_DIFF_RATIO = 0.25`, and the
  post-revision re-check. Revision uses the SAME model/config/cost path as
  generation (reuse `build_messages`/config loading; the only change is the
  message content is draft+deficiencies, not the assembled prompt).
- Arg validation: `--revise` requires `--deficiencies`; `--check-prose`
  and `--revise` are each mutually exclusive with the generation args (mirror
  the existing `--check-labels` guard).

**3.2 orchestrator.md — step-8 error table + new rung.** After a prose-check
FAIL (LabelLeakError today; any `--check-prose` deficiency after this
ticket): the rung is `revise` up to twice, each time re-running
`--check-prose`; if still failing after the second revision, OR if
`RevisionOverreachError` fires, fall to `redo generation`. Update the
LabelLeakError line (currently "retry step 8 once (redo generation)") to
route through the revision rung first. Add one case-law line naming T-012
and the ch8 arithmetic.

**3.3 RUN.md — undo/redo ladder text.** Add the revision rung to the
laddder description: cheapest-first is now
`revise` (checkable surgical miss) → `redo generation` (fresh roll / whole
scene missing) → `redo from brief` → `redo last chapter`. One line noting
revision is for surgical misses only; scene-shaped omissions skip straight
to `redo generation`.

**3.4 field_registry.md** — register `prompts/prose_deficiencies.json`
(producer: `invoke_writer.py --check-prose`; consumers: the orchestrator
ladder, `invoke_writer.py --revise`). Note it is a transient prompt-stage
artifact, not state.

**3.5 LAW 4 audit, same sitting:** grep `check-labels\|LabelLeakError\|
validate_forbidden_labels\|redo generation` across `fiction_loop/agents/
fiction_loop/core/ fiction_loop/tools/ fiction_loop/RUN.md
fiction_loop/specs/`; update or exempt EVERY hit; record dispositions in
§5. Known hits at ticket time: invoke_writer.py (refactor), orchestrator.md
(rung + error line), RUN.md (ladder), field_registry.md (row),
tickets are out of scope. If the grep surfaces a live contract OUTSIDE this
write-set that states the redo-only ladder, STOP and return BLOCKED (do not
widen the write-set yourself — the T-008 precedent: a write-set defect is
the senior's to fix on redispatch).

## 4. Acceptance (ALL must pass — entirely offline; three fixtures on disk)

Fixtures: committed `chapters/chapter_007.md` (clean); the abandoned-run
attempt-2 draft at `git show d91e558:fiction_loop/prompts/chapter_draft.md`
(label leak); the attempt-3 draft at
`git show cf70a1b:fiction_loop/prompts/chapter_draft.md` (labels clean).

1. `--check-prose` on chapter_007.md → `prose_deficiencies.json` is `[]`,
   exit 0. (ch7's artifact-quoted labels stay WARN, never deficiencies —
   the T-010 italic-exemption is preserved through the refactor.)
2. `--check-prose` on the attempt-2 fixture → deficiencies list contains
   the three narration-label records (lines ~49/55), exit 1. The italic
   torn-page label lines are WARN, not deficiencies.
3. `--check-prose` on the attempt-3 fixture → `[]`, exit 0 (attempt-3's
   only miss is the anchor scene, which is T-014's brief/prose-anchor
   concern, NOT a prose-label deficiency — proving this ticket does not
   over-claim).
4. `--revise <attempt-2 fixture> --deficiencies <the file from step 2>
   --dry-run` → writes `revision_prompt.md` containing the full draft AND
   an explicit correction checklist naming the three flagged lines; exit 0;
   NO spend entry appended (grep the spend file mtime/contents unchanged).
5. Diff-guard unit: with two static files differing by >25% of lines,
   `--revise ... --dry-run` is unaffected (dry-run never adopts), and the
   adoption path's guard is covered by a pytest that calls the ratio
   function directly (add to the existing invoke_writer test module; no
   API). Assert `RevisionOverreachError` above threshold, adoption below.
6. Arg-guard: `--revise` without `--deficiencies` errors; `--check-prose`
   combined with `--output` errors (mirror the `--check-labels` guard).
7. `--check-labels` still behaves exactly as today on all three fixtures
   (regression: T-010 acceptance §4.1/§4.2 re-run green).
8. Test suite (sanctioned command) → `1 failed, 331 passed` (the known
   pre-existing engines failure only).
9. `git status --porcelain` → changes only in the write-set; one
   pathspec-limited commit. NO paid call was made (spend file byte-identical
   to HEAD).

## 5. Commit

`fix(tools): targeted-revision rung — surgical fix replaces blind re-roll for checkable misses (T-012)`

Trailers: `Ticket: T-012` / `Implemented-by: <Codex|Qwen>`.

## 6. Constraints

- Raspberry Pi; the ONLY sanctioned paid call is a real `--revise` (no
  `--dry-run`), and this ticket must be implementable and acceptable with
  ZERO paid calls (all §4 steps are offline). Do not make a live revision
  call during implementation; its proof rides the next owner run.
- No writes to `state/`, `chapters/`, or `core/living_document.md`. The
  revised draft goes to `prompts/chapter_draft.md` only — the SAME artifact
  generation writes, so the existing step-9 copy-to-chapters is unchanged.
- If ANY §3 item cannot be completed, STOP and revert; leave the tree
  coherent; record in §5 exactly as observed (T-008 precedent).

## 7. Implementer log (append below; never delete the ticket body)
