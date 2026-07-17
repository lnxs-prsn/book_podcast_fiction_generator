# Paid-call governance — starter (copy blocks; implement the wrapper in ~100 lines)

## 1. `spend_caps.json` — one cap key per paid purpose

```json
{
  "ask": 5,
  "evaluate": 2,
  "<new_purpose>": 0
}
```
A purpose with no key (or 0) is REFUSED — honest refusal beats silent spend.
Raising a cap is an owner decision (ledger entry), not an agent edit.

## 2. The wrapper contract (implement as `tools/paid.py` or equivalent)

Single entry point for EVERY paid call in the project:

```
paid --cap-key <purpose> --unit-id <cycle/ticket id> -- <the actual call>
```

Behavior, in order:
1. Load caps + current counts for (<purpose>, <unit-id>).
2. Over cap → print a refusal naming key/count/cap, exit nonzero, make NO
   call. (Refusal is free — test this by asserting the ledger did not grow.)
3. Make the call; APPEND a receipt row to `state/spend.json`:
   `{ts, purpose, unit_id, ok|degraded|failed, note}` — receipt EVERY
   attempt, including $0 and failed ones. The receipt, not the price, is
   what makes provenance reconstructable.
4. Degraded output (backend down, refusal-shaped answer): receipt it, WITHHOLD
   the result from the caller, log why.

## 3. The rules around the wrapper

- A paid path that bypasses the wrapper is a review-blocking defect.
- The spend ledger has ONE writer: the wrapper. Agents' tickets default to
  `Paid-calls: forbidden`; a budgeted ticket names the cap key.
- New paid features add their cap key + wrapper routing IN THE SAME SPEC as
  the feature.
- Backends without owner authorization return None/refuse cleanly — never
  stub a fake success.

## 4. Self-tests worth having

Cap-block makes no call and no receipt growth beyond the refusal note; a
successful call adds exactly one receipt; a degraded response is receipted
and withheld.
