# Autonomy graduation rule — decision-ledger entry template

Decide the RULE once, in advance, while nothing is eligible — never at the
moment of temptation. Paste into your decision ledger and have the owner
answer it.

```markdown
## <ISO ts> — <system> autonomy graduation: how per-capability auto-approve is granted  [PROPOSED]
Essence: today every automated <verdict/action> is a proposal a human
  confirms or overturns. This decides — once, as policy — what happens the
  day a capability first proves reliable: may scoped autonomy be PROPOSED,
  or is manual confirmation kept forever?
Analogy: autopilot certification — the recorder logs how often the captain
  overrode a maneuver; below an override threshold across N real flights,
  the manufacturer may FILE for certification of that one maneuver. Filing
  is not granting; a human signs, and certification is revocable.
Impact + reversibility: A is reversible per-capability (auto-suspend on
  threshold breach + owner revoke); B permanently forecloses the autonomy
  ladder and caps what the system can become.
Architecture points at: A — trust earned from logged evidence, granted
  through a human airlock, revoked automatically when evidence turns.
Context: eligibility arithmetic exists (<stats command>) and REPORTS
  eligibility without granting. Threshold: override rate < <10%> over the
  last <50> real human rulings, per capability. Nothing is eligible today.
Options:
  A) When a capability first reports eligible, a session drafts a scoped
     per-capability proposal HERE (naming the capability, its rule, its
     last-N override rate, the ruling ids behind it) and STOPS for explicit
     owner acceptance. Auto-approved actions stay logged, still count toward
     the running rate, and autonomy AUTO-SUSPENDS if the rate crosses back
     over the threshold.                                          ← DEFAULT
  B) Manual confirmation forever; the ladder is closed.
Decision: <owner answers>
```

Non-negotiables that ride along with option A:
- NEVER fabricate rulings/cases to reach a threshold — poisoned ground truth
  is unrecoverable.
- Confirmed-good cases freeze (with consent) into a read-only golden set;
  a green re-run against it becomes the change gate for the judging code.
- No human expert available? A second, independent model may rule
  PROVISIONALLY — flagged everywhere as provisional, stamped into any frozen
  case, superseded by a human path the moment one exists.
