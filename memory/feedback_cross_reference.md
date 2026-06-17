---
name: feedback-cross-reference
description: When multiple files are read in the same session, actively cross-reference them rather than accepting one file's summary of another
metadata:
  type: feedback
---

When two related files are in context (e.g. a spec and an analysis report of that spec), do not answer questions by relying solely on one file's characterization of the other. Cross-reference both directly.

**Why:** User asked how many issues were unresolved after reading both fix_specsv2.md and specs_analysis_report.md. The report claimed 2 issues were resolved in the spec. Instead of verifying this against fix_specsv2.md (which was already in context), the answer was accepted at face value — producing an unverified count.

**How to apply:** When a question requires a factual claim that spans multiple files already in context, check all relevant files before answering. Do not treat a summary document as ground truth when the primary source is available.
