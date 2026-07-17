# TICKET T-001: One Python project at the repo root — move pyproject/uv.lock/venv out of src/

```
Mode: alone
Worktree: main working tree, run everything from the repo root
Write-set: pyproject.toml, uv.lock, .python-version (all: new at root, deleted from src/),
           .venv/ (created by uv, gitignored — never committed),
           README.md + main.py at root (delete — untracked uv-init litter),
           fiction_loop/tools/invoke_writer.py,
           fiction_loop/tools/refresh_living_doc.py,
           fiction_loop/tools/INTEGRATION_SPECS.md,
           fiction_loop/agents/orchestrator.md,
           fiction_loop/agents/writer.md,
           fiction_loop/specs/pipeline_fixes.spec.md,
           scripts/generate_scout_json.py
Hot-files: none
State-access: none — do NOT touch fiction_loop/state/, fiction_loop/prompts/,
              fiction_loop/core/living_document.md, or any .pipeline_spend.json
Paid-calls: forbidden (no API key needed anywhere in this ticket)
```

Read `fiction_loop/CONTRIBUTING.md` (the laws) before editing anything under
`fiction_loop/`. Repo root = the directory containing this `tickets/` folder.

## 1. Problem (preconditions verified 2026-07-17 by the ticket author)

The repo was re-cloned onto a new OS on 2026-07-17 (~09:56); virtualenvs are
gitignored, so no venv survived. The project's Python root has always been
`src/`, which causes a recurring failure: agents run bare `python` or `uv` from
the repo root, get (or create) a root venv with **zero dependencies**, then
hallucinate pip/venv repair steps. Verified tonight: a stub root venv failed
`import requests` while all real deps live in the src project.

Facts, each personally verified by the author on this clone:

- Tracked (git ls-files): `src/pyproject.toml` (project name `harness`,
  13 dependencies, `[tool.uv] package = true`, setuptools config),
  `src/uv.lock`, `src/.python-version` (contains `3.11`).
- Untracked litter at root from an abandoned `uv init` (2026-07-17 ~20:40):
  `.python-version` (contains `3.13`), `README.md` (empty, 0 lines),
  `main.py` (hello-world stub). A stub `pyproject.toml` and an empty `.venv/`
  also existed; the author already deleted those two.
- `git mv src/pyproject.toml src/uv.lock src/.python-version .` fails with
  `fatal: destination exists` while the litter `.python-version` is present
  (author hit exactly this). Delete the litter FIRST.
- Live files that hardcode the old interpreter path `src/.venv/bin/python`
  (grep-verified, line numbers as of HEAD a1a3dba):
  - `fiction_loop/tools/invoke_writer.py` lines 4, 58 (docstring + error hint)
  - `fiction_loop/tools/refresh_living_doc.py` lines 4, 57 (same)
  - `fiction_loop/tools/INTEGRATION_SPECS.md` lines 156, 290, 396, 413
  - `fiction_loop/agents/orchestrator.md` line 196
  - `fiction_loop/agents/writer.md` lines 29, 50
  - `fiction_loop/specs/pipeline_fixes.spec.md` lines 42, 100
  - `scripts/generate_scout_json.py` line 16 — NOTE: this one is a
    directory-skip entry `"src/.venv/"` in a list, not a command
- Historical/dated documents also mention `src/.venv`
  (`src/phases/phase_01/ai_context.md`, `src/phases/phase_04/passes.md`,
  `docs/fiction/initial_plan.md`, `progress/handoff-2026-07-10-factory-spec.md`).
  These are records of their date — DO NOT edit them. The author has placed a
  staleness note in the old handoff separately.
- `.env.example` uses `PYTHONPATH=src` — still correct after this ticket;
  leave it.

## 2. Fix

Execute in this order, from the repo root:

1. Delete the three untracked uv-init artifacts:
   `rm .python-version README.md main.py`
2. Move the real project files (preserves git history):
   `git mv src/pyproject.toml src/uv.lock src/.python-version .`
3. Edit the now-root `pyproject.toml` — ONLY the two setuptools path sections,
   because package paths are now relative to the repo root, not `src/`:

   ```toml
   [tool.setuptools]
   package-dir = {"" = "src"}
   py-modules = ["settings", "config"]

   [tool.setuptools.packages.find]
   where = ["src"]
   exclude = [".venv*", "*.tests*", "*.test*"]
   ```

   Change NOTHING else. Keep `name = "harness"` (renaming invalidates
   `uv.lock`), keep `requires-python = ">=3.11"`, keep the dependency list
   byte-identical, keep `[tool.uv] package = true` and the `[build-system]`
   block as they are.
4. `uv sync` from the repo root. Expectations: uv reads `.python-version`
   (3.11) and may download a standalone CPython 3.11 for aarch64 — that is
   normal and allowed; it then creates `.venv/` at the root and installs from
   the existing `uv.lock`. Do NOT run `uv lock`, `uv lock --upgrade`, or edit
   the lock. If `uv sync` wants to re-resolve (lock mismatch message), STOP
   and log — do not accept a new resolution.
5. In the seven live files listed in §1, replace the string
   `src/.venv/bin/python` → `.venv/bin/python` (12 occurrences), and in
   `scripts/generate_scout_json.py` replace the skip entry `"src/.venv/"` →
   `".venv/"`. Touch no other lines.

## 3. Acceptance (numbered; ALL must pass)

1. `ls src/pyproject.toml src/uv.lock src/.python-version` → all three "No
   such file or directory"; `cat .python-version` → `3.11`.
2. `.venv/bin/python -c "import requests, fitz, tiktoken, dotenv, ebooklib; print('deps ok')"`
   → prints `deps ok`.
3. `PYTHONPATH=src .venv/bin/python fiction_loop/tools/progress.py` → exit 0,
   output includes the 5 completed chapters / pointer at chapter 006.
   (Zero-token tool, no API key needed. Author note: could not dry-run — no
   venv exists on this clone at ticket-writing time; the same tool + state ran
   green pre-migration per `progress/handoff-2026-07-10-factory-spec.md` §2.)
4. `grep -rn "src/.venv" fiction_loop/ scripts/` → zero hits.
5. `git status --porcelain` shows changes ONLY within the write-set
   (`tickets/`, `innovations/`, `progress/` untracked/modified entries by the
   author may also be present — leave them alone, do not stage them).

## 4. Commit

`build: move python project root from src/ to repo root (single .venv)`

Trailers:
```
Ticket: T-001
Implemented-by: Codex
```

Pathspec-limit the commit to exactly the write-set files (the ch4 incident
rule: never `git commit -a`). `.venv/` is gitignored and must not appear.

## 5. Constraints

- This machine is a Raspberry Pi. `uv sync` may take several minutes —
  let it finish; run nothing heavy in parallel.
- **uv only.** Never `pip install`, never `python -m venv`, never conda —
  the whole point of this ticket is to end improvised environment repair.
- Zero paid calls; nothing here needs an API key or touches spend files.
- Never touch `fiction_loop/state/`, `fiction_loop/prompts/`,
  `fiction_loop/core/living_document.md`, any `.pipeline_spend.json`,
  or `books/`.
- On ANY failure: stop at that step, record it in §6 exactly as observed,
  leave the tree coherent. Do not improvise alternative designs (e.g. if a
  wheel fails to build on aarch64, that is a STOP-and-report, not a version
  bump).

## 6. Implementer log (append below; never delete the ticket body)

- [x] step 1 — litter removed
- [x] step 2 — git mv done
- [x] step 3 — pyproject paths edited
- [x] step 4 — `uv sync --locked` green; CPython 3.11.15, 63 packages installed
- [x] step 5 — reference sweep done; 15 observed live hits replaced (ticket estimate was 12)
- [x] acceptance 1–5 — missing old files; `3.11`; `deps ok`; progress reports 5 completed / ch 006; zero live `src/.venv` hits; status limited to write-set plus pre-existing author changes
- [x] commit — `build: move python project root from src/ to repo root (single .venv)`
