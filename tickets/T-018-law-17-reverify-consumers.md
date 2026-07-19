# TICKET T-018: LAW 17 — a change to a shared surface re-verifies its consumers ("know who eats your output")

```
Mode: alone
Depends-on: none (constitution edit). Independent of T-016/T-017.
Timing: BETWEEN runs only.
Worktree: main working tree, repo root
Write-set: fiction_loop/CONTRIBUTING.md (one new law + case law)
Hot-files: none
Upstream (preconditions — author verified 2026-07-19):
  - CONTRIBUTING.md currently ends at LAW 16 (verified); the new law is 17.
  - This law's enforcement already exists / is in flight: the ticket
    template's Downstream field + acceptance item 4 (committed), and the
    tool regression suite (T-016). So LAW 17 ships WITH its check — it is
    LAW-16-compliant by construction.
Downstream (consumers to re-verify): none — CONTRIBUTING is read by humans/
  agents; no code consumes it. (The "16 laws" count references were fixed at
  T-013; confirm none now say "16 laws" needs bumping — see §3.2.)
State-access: none
Paid-calls: forbidden
```

Read `fiction_loop/CONTRIBUTING.md` first — do not disturb LAWS 1–16 or the
"lower number wins" preamble.

## 1. Problem (owner decision 2026-07-19; the T-014 regression)

Tickets verify their own delta but not what their delta *touches*. T-014
changed the shared `write_prose_deficiencies` and silently regressed T-012's
label-only contract; nothing caught it until the senior re-ran T-012's
acceptance by hand. The owner's principle: **anyone who changes a shared
surface must know who eats its output, and re-verify them.** Obvious enough
to be constitution.

## 2. Design

Add **LAW 17 — KNOW WHO EATS YOUR OUTPUT.** A change to any surface with
registered consumers (LAW 4) must, in the SAME change: (a) enumerate those
consumers — the ticket's Downstream field — and (b) re-verify them (their
acceptance, and/or the tool regression suite) as part of its own acceptance.
A downstream regression must fail in the ticket that caused it, never be
discovered by the next one. Enforcement (LAW 16 self-compliance): the ticket
template's Downstream field + acceptance item 4, and the tool regression
suite (T-016).

Case law: T-014 rewired `write_prose_deficiencies` and regressed T-012's
`--check-prose` label-only contract; caught only by hand re-verification
(handoff 2026-07-19 §13).

## 3. Fix

**3.1 CONTRIBUTING.md** — append `**LAW 17 — ...**` after LAW 16, in the
house voice (bold lead, the rule, then *(case law: …)*). One paragraph. Do
NOT renumber or edit any existing law.

**3.2** Check for any "16 laws" count copy that must become "17":
`grep -rn "16 laws\|sixteen laws" fiction_loop/ HANDOFF.md`. Update the
in-scope ones under `fiction_loop/`; note any `HANDOFF.md` hit for the
senior (out of implementer scope, per T-013 precedent). At ticket time the
known counts still read "15/16" fixed by T-013; verify and update only real
hits.

## 4. Acceptance

1. `grep -n "LAW 17" fiction_loop/CONTRIBUTING.md` → present with a
   `(case law:` clause; LAWS 1–16 byte-unchanged (`git diff` shows only an
   addition after LAW 16 + any count fix).
2. `grep -rn "16 laws\|sixteen laws" fiction_loop/` → zero stale counts
   under fiction_loop.
3. Test suite → `1 failed, 331 passed`. `git status --porcelain` → only the
   write-set PLUS this ticket's own implementer-log section (standing
   exemption, AGENTS.md §1 — the ticket file is not counted against the
   write-set); one commit.
4. DOWNSTREAM RE-VERIFY: none (leaf doc).

## 5. Commit

`docs(laws): LAW 17 — a shared-surface change re-verifies its consumers (T-018)`

Trailers: `Ticket: T-018` / `Implemented-by: <Codex|Qwen>`.

## 6. Constraints

- No code, no state, no paid calls. Pure constitution edit.
- LAW 17 is the highest number and yields to all others in conflict.

## 7. Implementer log (append below; never delete the ticket body)

- 2026-07-19 — implementer — **BLOCKED (valid).** Ticket write-set is only
  `CONTRIBUTING.md`, but AGENTS.md + §7 require appending here, and §4 said
  "only the write-set changed" — a contradiction (the ticket file is not in
  its own write-set).
- 2026-07-19 — senior — **RESOLVED (class fix; STOP was correct).** This was
  a template-inherited contradiction affecting EVERY ticket, not a T-018 bug.
  Added a standing exemption: appending to a ticket's own implementer-log
  section is always allowed and is excluded from the write-set / "only the
  write-set changed" check — AGENTS.md §1, TICKET_TEMPLATE §3/§6, and §4 above
  now say so. No ticket lists itself. **Proceed:** implement LAW 17 into
  CONTRIBUTING.md per §3; append your log here freely.
