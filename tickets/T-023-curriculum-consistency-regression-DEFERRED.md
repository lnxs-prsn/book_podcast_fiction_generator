# T-023 — curriculum-consistency regression (rule 5) — DEFERRED by owner

**This is a status marker, NOT a work order.** It holds the T-023 slot so there is no
gap in the ticket order. (Same role as the T-021/T-022 markers.)

## Status: deferred 2026-07-20 ("come back to this later")
Not struck — a valid future item, just not now.

## What it would be
A regression fixture enforcing **generation rule 5** (`specs/intake_factory.spec.md`
§1: *"One quantity, one owning table"*) — the guard against the DECISION 10 class (a
quantity stated in two curriculum places that silently diverged). The DECISION 10 fix
already added one such assertion (`QUOTA_BY_ARC matches curriculum §9 Section 4`, live in
`tools/regression/run.py`); T-023 generalizes that pattern.

## Open scope fork (decide before writing the ticket)
- **(a) Targeted** — assert each *known* single-source quantity appears only in its
  owning table (extend the existing QUOTA_BY_ARC assertion). Concrete, low-noise.
  *Senior lean.*
- **(b) General parser** — scan all curriculum tables for any numeric quantity
  duplicated across tables. Catches unknowns but noisy (numbers legitimately recur).

## When unblocked
Owner picks the scope fork → write the ticket → replace this marker. No hard
dependency on the other tickets. See current handoff §5.
