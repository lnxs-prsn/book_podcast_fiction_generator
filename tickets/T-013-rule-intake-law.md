# TICKET T-013: rule-intake law — a new hard rule must ship its own check or its excuse

```
Mode: alone
Depends-on: none. Independent of T-012/T-014 (touches only CONTRIBUTING.md).
            May land in any order relative to them.
Timing: BETWEEN runs only (constitution edit). No chapter run in flight.
Worktree: main working tree, repo root
Write-set: fiction_loop/CONTRIBUTING.md (one new law + its case law)
Hot-files: none
State-access: none
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first — this ticket adds LAW 16 and
must not disturb LAWS 1–15 or the "lower number wins" preamble.

## 1. Problem (the ratchet that strangled the writer)

Every incident since chapter 1 promoted its violation to a hard rule (rule
12 was added in July after ch6; the cast quota grew with arc 2). Each added
rule multiplies the writer's joint single-roll pass rate (~0.93ⁿ). The
machine's own immune response — "promote every violation to a hard rule" —
has been slowly strangling its own writer, because nothing ever takes load
off the prompt and most promoted rules were left to the LLM's own
self-check (the most expensive, least reliable enforcer) instead of a grep
(the cheapest, perfect one). T-010 (labels) and T-012 (revision) fix the
COST of a miss for CHECKABLE rules. This law stops the ratchet at the
SOURCE so the fix does not decay: after today, a new hard rule must arrive
WITH its deterministic check, or with a written admission that it cannot
have one.

## 2. Design (single outcome)

Add **LAW 16 — A NEW HARD RULE SHIPS ITS OWN CHECK OR ITS EXCUSE.** No
violation may be promoted to a hard rule unless the SAME change either
(a) ships a deterministic check that emits a structured deficiency (the
T-012 §2.1 record shape) and registers it under LAW 15, OR (b) records, in
the rule's own text, a one-line NON-CHECKABILITY note explaining why no
deterministic check is possible (e.g. it is a matter of voice or pacing
that only the gate/owner can judge). A hard rule with neither is
incomplete and must not be added.

Rationale line to include: a rule's ongoing cost is (rule count) ×
(cost-per-miss); T-010 + T-012 drive cost-per-miss toward one cheap call
for checkable rules, so the immune response must pay its own enforcement
cost or declare it cannot — otherwise the prompt silently re-accumulates
the load this quarter's work just removed.

Case law to cite: HARD RULE 1 (planning labels) rode the Writer's
self-check for weeks until it leaked into ch8 attempt-2 narration and cost
a roll before T-010 made it a grep; the ch8 three-roll incident is the
arithmetic proof (§ handoff 2026-07-18 §§6–9).

## 3. Fix

**3.1 CONTRIBUTING.md** — append `**LAW 16 — ...**` after LAW 15, in the
established voice (bold lead, the rule, then *(case law: …)*). Keep it to
one paragraph. Do NOT renumber or edit any existing law.

**3.2** Update the ONE in-scope "15 laws" reference so the count stays true
(LAW 2 single-source): `fiction_loop/specs/intake_factory.spec.md:29`
("15 laws with case law") → 16. The other stale count lives in the
maintainer-owned `HANDOFF.md:39`, OUTSIDE fiction_loop/ and off-limits to
the implementer (agent_conduct §2 scope wall); the SENIOR updates that one
at acceptance. Do not touch HANDOFF.md.

## 4. Acceptance

1. `grep -n "LAW 16" fiction_loop/CONTRIBUTING.md` → the new law present,
   with a `(case law:` clause; LAWS 1–15 byte-unchanged
   (`git diff` shows only an addition after LAW 15 + the two count fixes).
2. `grep -rn "15 laws\|fifteen laws" fiction_loop/` → zero stale counts
   inside fiction_loop/ (intake_factory.spec.md updated to 16). HANDOFF.md
   is the senior's to fix at acceptance (out of implementer scope).
3. Test suite (sanctioned command) → `1 failed, 331 passed` (unaffected).
4. `git status --porcelain` → only the write-set; one pathspec-limited
   commit.

## 5. Commit

`docs(laws): LAW 16 — a new hard rule ships its own check or its excuse (T-013)`

Trailers: `Ticket: T-013` / `Implemented-by: <Codex|Qwen>`.

## 6. Constraints

- No code, no state, no paid calls. Pure constitution edit.
- Lower-number-wins ordering is preserved; LAW 16 is the highest number and
  yields to all others in conflict.

## 7. Implementer log (append below; never delete the ticket body)
