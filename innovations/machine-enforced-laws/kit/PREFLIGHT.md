# Session preflight — the start checklist every work session runs first

Implement as a small stdlib script (`tools/preflight.py` / `session.py`,
~100 lines) that every session — human or AI — runs before any work. Print
one status line, a CHECKS line, and on failure a REMEDY pointer, then exit
nonzero. The checks that earn their keep:

| Check | Gate or warn? | What it verifies |
|---|---|---|
| env | gate | required config files exist and parse |
| health | gate | core service/CLI answers (`<cli> health` style) |
| env/venv identity | gate | the interpreter/venv in use is THE project one (stale paths after moves/copies are a classic silent killer) |
| tree | gate | `git status --porcelain` empty — dirty tree means a dead session to investigate, not a surface to build on |
| hooks | **warn** | commit hooks installed — warn-only, because a fresh clone must boot far enough to tell you to install them |

Design rules proven the hard way:
- Every FAIL prints a REMEDY pointing at the doc section that fixes it —
  a refusal without a remedy just strands the next session.
- Gate vs warn is a deliberate per-check decision (see table).
- The preflight itself gets self-tests, and its expected values must be
  COMPUTED, not hardcoded (a hardcoded venv path broke the origin project's
  preflight after an environment restructure; a hardcoded hooksPath broke it
  after a monorepo merge — both now computed).
- Output is for a learner/operator, not a debugger: one status line, one
  checks line, a menu of next actions if green.
