# TICKET T-018: LAW 17 — a change to a shared surface re-verifies its consumers ("know who eats your output")

```
Mode: alone
Depends-on: none (constitution edit). Independent of T-016/T-017.
Timing: BETWEEN runs only.
Worktree: main working tree, repo root
Write-set: fiction_loop/CONTRIBUTING.md (one new law + case law),
           fiction_loop/specs/intake_factory.spec.md (law-count bump
           "16 laws" → "17 laws" ONLY — added on redispatch, §3.2)
Hot-files: none
Upstream (preconditions — author verified 2026-07-19):
  - CONTRIBUTING.md currently ends at LAW 16 (verified); the new law is 17.
  - This law's enforcement already exists / is in flight: the ticket
    template's Downstream field + acceptance item 4 (committed), and the
    tool regression suite (T-016). So LAW 17 ships WITH its check — it is
    LAW-16-compliant by construction.
Downstream (consumers to re-verify — CORRECTED on redispatch): the law COUNT
  ("the N laws") is a shared value with consumers. Verified hits of "16 laws":
  (a) fiction_loop/specs/intake_factory.spec.md:29 — IN write-set, bump here;
  (b) HANDOFF.md:29 — OUTSIDE fiction_loop, senior updates at acceptance
  (T-013 precedent). CONTRIBUTING.md itself gains only the LAW 17 paragraph.
  [Original Downstream said "none — no code consumes it." That was WRONG and
  caused the STOP below — a live demonstration that even LAW 17's own ticket
  under-enumerated its consumers, which is exactly why the mechanical check,
  not the principle alone, is the point.]
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

**3.2** Bump the law-count copies from "16" to "17". Verified hits
(`grep -rn "16 laws\|sixteen laws" fiction_loop/ HANDOFF.md`):
- `fiction_loop/specs/intake_factory.spec.md:29` ("16 laws with case law")
  → "17 laws with case law" — IN write-set, you update it.
- `HANDOFF.md:29` ("the 16 laws") — OUTSIDE fiction_loop, off-limits to the
  implementer (agent_conduct scope wall); the SENIOR updates it at
  acceptance (T-013 precedent). Do not touch HANDOFF.md.
Change only the digit; touch nothing else in the spec.

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
- 2026-07-19 — Codex — **BLOCKED.** The required §3.2 count scan found a real
  stale count at `fiction_loop/specs/intake_factory.spec.md:29` ("16 laws"),
  and §3.2 requires updating real hits under `fiction_loop/`, but the literal
  write-set permits only `fiction_loop/CONTRIBUTING.md`. Per AGENTS.md §1 and
  LAW 1, stopped without editing LAW 17 or the out-of-write-set spec. Expand
  the write-set to include `fiction_loop/specs/intake_factory.spec.md`, or
  explicitly exempt that hit for a separate ticket.
- 2026-07-19 — senior — **RESOLVED (write-set expanded; STOP was correct;
  authoring defect owned).** `intake_factory.spec.md` added to the write-set
  (law-count bump only); the Downstream field is corrected (it wrongly said
  "none"). The irony is instructive and now recorded in the ticket: the LAW 17
  ticket itself under-enumerated its consumers — the count is a shared value.
  HANDOFF.md's count stays the senior's at acceptance. **Proceed:** LAW 17
  into CONTRIBUTING §3.1; bump the ONE digit in intake_factory.spec.md §3.2;
  append your log here.
- 2026-07-19 — Codex — **IMPLEMENTED.** Appended LAW 17 with its LAW-16
  enforcement and T-014 case law; bumped the factory spec's sole law-count copy
  from 16 to 17. Acceptance verification completed with no paid calls.
