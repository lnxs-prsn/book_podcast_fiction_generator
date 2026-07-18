# T-012 PLAN — SUPERSEDED (expanded into dispatched T-012/T-013/T-014)

STATUS: SUPERSEDED 2026-07-18. This plan has been expanded into three
DISPATCHED tickets by the senior (the implementer correctly refused to
build from a PLAN):
- `T-012-targeted-revision-rung.md` — the core station (revise-not-reroll
  for SURGICAL checkable misses; zero-paid acceptance, live proof rides a
  run).
- `T-013-rule-intake-law.md` — LAW 16 (a new hard rule ships its check or
  its excuse); stops the ratchet at the source.
- `T-014-prose-anchor-presence-check.md` — OPTIONAL/deferrable early catch
  of a missing anchor scene before the Extractor spend (gate already
  catches it authoritatively).

Key design correction made during expansion (recorded so it is not lost):
all three ch8 failure modes are ALREADY caught deterministically today (the
structural gate catches anchor-absent on the brief; T-010's label check
catches label leaks on prose). The station's real win is therefore
REVISE-NOT-REROLL for surgical misses, NOT new correctness. A whole-scene
omission (anchor absent) is closer to inventing than copying, so it stays
on `redo generation` — revision targets surgical spans only. A coarse prose
anchor grep FALSE-PASSES (attempt 3 contains "notebook"/"page" incidentally
while the anchor scene is absent), so T-014 derives the required phrase from
a structured Assembler field, never a hardcoded literal.

Original plan text retained below for provenance; the dispatched tickets are
the authority.
Queue position (revised): T-012 → (T-013 any time) → T-014 optional.
All BETWEEN runs.

## 0. Diagnosis being fixed (agreed with owner)

Writer holds each hard rule ~92–95%/pass; 12 simultaneous rules ⇒ ~0.93¹²
≈ 40% joint pass per roll. Three ch8 rolls missed a DIFFERENT rule each
(1: anchor absent; 2: HARD RULE 1 label leak; 3: labels clean but
torn-page anchor absent again — receipts: spend entry 19:10, greps in
session log). Blind redo is memoryless re-sampling. Fix: drive
cost-per-miss to ~one cheap call for every mechanically checkable rule.
Steady state: generate → deterministic checks → targeted revision → gate
→ state (~2 paid calls/chapter regardless of rule count). Do NOT strip
checkable rules from the writer prompt (compliance still saves a call).

## 1. Immediate zero-token actions (senior, before any ticket lands)

1. Preserve ch8 attempt 3 as a fixture next to the existing T-010
   fixtures (ch7 + attempt-2 convention): copy current working-tree
   `fiction_loop/prompts/chapter_draft.md` to the fixtures location as
   `ch8_attempt3.md`. It is the T-012 acceptance fixture: passes label
   check, warm-stool + wiped-panel traces present, FAILS anchor check
   (no torn page / no "condition itself provides" line).
2. Commit fixture + this plan (pathspec-limited). Spend file rides along
   (LAW 9: never reverted).
3. Update HANDOFF current-handoff addendum: ch8 abandoned, queue order
   above, attempt-3 fixture location.

## 2. T-012 — targeted-revision rung

Write-set: `fiction_loop/tools/invoke_writer.py`, structural-check tool(s)
(whatever T-010 lands as), `fiction_loop/specs/orchestrator.md` (ladder),
`RUN.md` ladder line, chapter_type_contract if check patterns are
per-type. Design decisions (owner-agreed, do not re-litigate):

1. **Checks emit structured deficiencies**, not bare FAIL: list of
   {rule_id, description, evidence_expected, where}. Patterns derived at
   RUNTIME from brief/process_state (LAW 14 — the T-010 pattern; anchor
   check reads the brief's macro-evidence list, never hardcodes "torn
   page").
2. **Revision mode in invoke_writer.py**: input = existing draft + the
   deficiency list; prompt assembled BY THE TOOL (no human composes
   prompts — no-hand-surgery doctrine, one layer up). Instruction shape:
   "correct ONLY the flagged spots; change nothing else."
3. **Post-revision: re-run ALL deterministic checks**, plus a mechanical
   diff-size guard (revision touching more than N% of the draft ⇒
   escalate; pick N from ch7/ch8 fixture measurements, ~15–20% likely).
4. **Escalation**: two failed revisions ⇒ redo generation. Redo prompt
   gains the deficiency report appended (conditioned redo — may instead
   land inside T-007's ladder rewrite if cheaper there; coordinate).
5. **Existing-draft intake**: if a draft exists on resume and fails only
   checkable rules, the ladder enters at the revision rung (this is how
   an abandoned attempt is machined instead of discarded).
6. **Ladder position**: deterministic-check FAIL → revision (×2) → redo
   generation → owner. Gate (step 11) remains the backstop for
   non-checkable qualities; checks gate only the cheap loop.
7. Acceptance sketch: revision run on the attempt-3 fixture inserts the
   torn-page beat (content derivable from the brief), all checks then
   pass, diff-size under guard; label check still passes; ch7 fixture
   untouched by check false-positives. Zero-token except one budgeted
   revision call (owner authorizes).

## 3. T-013 — rule-intake law (stops the ratchet)

Write-set: `fiction_loop/CONTRIBUTING.md` (new law or amendment).
Rule: no violation may be promoted to a hard rule unless the promotion
ships EITHER a deterministic check emitting a structured deficiency
(§2.1 shape) OR a written non-checkability note in the rule's entry.
Rationale line: a rule's cost is rule-count × cost-per-miss; checks +
revision make checkable rules ~free, so the immune response pays its own
enforcement cost. Audit item: sweep the CURRENT 12 hard rules into
checkable/non-checkable columns (this audit is also T-012's check
build-list).

## 4. Rejected alternatives (recorded so they are not re-proposed)

- Manual finishing pass on attempt 3 (hand surgery, one layer up).
- Best-of-N sampling (3× spend for ~78% vs revision's one call; no help
  for near-misses).
- Removing checkable rules from the writer prompt (no dilution evidence
  at n=8; compliance still saves calls).
- Fourth blind roll (the indicted behavior).
