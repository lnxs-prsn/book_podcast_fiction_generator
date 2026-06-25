# Initial Build Plan

**Scope:** Fix every blocker identified in the technical audit, harden input/output path boundaries, and leave the project shippable with all tests green.

**Constraint:** All changes must be backward-compatible. Existing CLI invocations, config files, state files, generated chapters, and the test suite must continue to work after the fixes — with two documented exceptions: (1) Phase 0 discards the separate `src/` git history (only the current state is preserved); (2) `.env` removal from git history (Phase 1) requires all contributors to re-clone.

**How to read this document:**
- A **phase** is a sequential gate. The next phase does not start until the current phase's gate passes.
- A **pass** is a parallel work unit inside a phase. Each pass owns its listed files exclusively — no other pass in the same phase touches those files. Passes within a phase run simultaneously.
- Each phase ends with a **gate** — the minimum state the repo must be in before the next phase begins.

---

## Already Done — Do Not Re-Implement

| Item | File | Evidence |
|---|---|---|
| `HARNESS_ROOT` env var; data paths under `src/data/` | `src/settings.py:12` | `os.environ.get("HARNESS_ROOT", Path(__file__).parent)` |
| `launch()` sets `HARNESS_ROOT=SRC_DIR`; all 5 menu flows use `launch()` | `menu.py:77-80` | `env["HARNESS_ROOT"] = str(SRC_DIR)` |
| Fiction config output paths changed from `../../../data/` to `../../data/` | `src/fiction/pipeline/config.toml` | Lines 31, 52-54 use `../../data/fiction/…` |
| `TTSTimeoutError` exception class | `src/podcast_script_generator/llm/exceptions.py:13` | Class exists — do not re-create |

---

## Pre-Implementation Audit — Verified 2026-06-25

This section records the **actual repo state** confirmed by inspection before any implementation work began. Use it to avoid re-deriving facts already established.

### Phase 0 status: NOT started

Every Phase 0 gate fails. Nothing in Phase 0 has been done:

| Gate condition | Status | Detail |
|---|---|---|
| `src/.git` removed | **FAIL** | `src/.git/` is a full nested git repo (branches, index, HEAD all present) |
| `src/` tracked as files (not gitlink) | **FAIL** | `git ls-tree HEAD src` → mode `160000` — still a broken submodule entry |
| Root `.gitignore` exists | **FAIL** | No `.gitignore` at project root |
| `.env` untracked/ignored | **FAIL** | `git ls-files .env` returns `.env` — `.env` IS tracked in the root git |
| Phase 0 consolidation commit | **FAIL** | Latest commit is `e1bd1f7 Clean up old architecture files…` |
| `python3 -m pytest src/ -q` → 113 passed | **PASS** | 113 passed in 1.52 s — baseline confirmed |

### Python version mismatch (affects Pass 2.1)

- `src/.python-version` currently contains `3.14`
- `src/pyproject.toml` currently declares `requires-python = ">=3.14"`
- System Python is `3.11.2`
- Pass 2.1 must change **both** files from `3.14` → `3.11`
- **Do not run `uv sync` before Pass 2.1** — it will fail against system Python 3.11.2

### `.env` is git-tracked (security)

- `git ls-files .env` returns `.env` — the file has been committed to root git history
- `git status` shows `M .env` (modified in working tree since last commit)
- Phase 0 Pass 0.3 must NOT stage `.env` (it is already excluded from the explicit `git add` list); it will remain tracked but unmodified in the new commit
- Phase 1 Pass 1.1 (key rotation) must happen before Phase 1.2 runs `git filter-repo`, so the rotated (already-invalidated) key is what ends up being rewritten out of history
- Adding `.gitignore` with `.env` in Phase 0 Pass 0.2 will **not** stop git tracking the already-committed file; `git rm --cached .env` is not in the plan because Phase 1.2 filter-repo rewrites the entire history anyway — that is intentional

### `src/config.json` current values

- `api_url`: `https://openrouter.ai/api/v1/chat/completions` — **already correct, no change needed**
- `model`: `"openrouter/free"` — Pass 2.6 must change this to `"openrouter/auto"`
- All other fields (`max_tokens`, `speakers`, `wavespeed_model`, `tts_scale`) are correct

### `src/settings.py` current values (affects Pass 2.2)

- `load_dotenv()` is **not called** anywhere in the file — confirmed absent, Pass 2.2 adds it
- `run_id` uses `strftime("%Y%m%d_%H%M%S")` — no microseconds, confirmed, Pass 2.2 adds `_%f`

### `src/novel_pipeline/config.py` current value (affects Pass 2.2)

- `min_chapter_words` default is `100` (line 112) — Pass 2.2 changes it to `1500`
- `src/fiction/pipeline/config.toml` also sets `min_chapter_words = 100` (line 35) — that file must **not** be changed (it is intentional short-chapter config)

---

## Architecture Principles (must hold across every pass)

1. **Env wins over file, defaults are safe.** Precedence: env vars > config file > defaults. Defaults must point to OpenRouter and a sane model.
2. **Fail fast, fail sanitized.** Tracebacks must never reach users. Internal diagnostics go to logs; user-facing messages go to stderr.
3. **Timeouts everywhere there is network I/O.** Every `requests` call and every polling loop must have a bounded lifetime.
4. **No secrets in git.** `.env` and `api_keys.txt` are never tracked.
5. **Python baseline is 3.11.** Packaging files must match the running interpreter.
6. **One place for path validation.** `src/path_utils.py` is the single module for path resolution and escape checks. No other file duplicates this logic.
7. **Tests are the contract.** A failing test means the code must adapt; only update a test if the test itself is stale.
8. **No restructuring.** `src/` is the Python package root. `novel_pipeline/` is the production fiction engine. `engines/` + `endpoints/` + `cli/` form the podcast layer. `llm/` is the shared transport. Do not move or rename these.

---

## Phase 0 — Git Consolidation

**Goal:** Collapse the two nested git repositories into one single repo rooted at the project root (`harnessv7_migrated/`, to be renamed `app/`). This is a structural prerequisite — Phase 1's `git filter-repo` and Phase 2's worktrees assume one repo. Running them against the current dual-git structure produces undefined results.

**Who runs this:** One agent (or the operator manually). Sequential — no parallelism.

**Background:** `src/` currently has its own `.git/` directory and is recorded in the root git as a broken gitlink (mode `160000`, no `.gitmodules`). The `.env` file lives in the root git. `menu.py` and the spec files are untracked in the root git. All Python code and tests live in `src/`.

**Tradeoff:** Deleting `src/.git/` discards the separate commit history inside `src/`. The current state of `src/` is preserved — only the history is lost. This is acceptable given the migration context.

---

### Pass 0.1 — Snapshot and Discard src git

**Work:**

1. Verify tests pass before touching anything:
   ```bash
   python3 -m pytest src/ -q
   ```
   Must report `113 passed`. If not, stop and fix before continuing.

2. Remove the broken submodule reference from the root git index:
   ```bash
   git rm --cached src
   ```

3. Delete the nested git database:
   ```bash
   rm -rf src/.git
   ```
   `src/` is now a plain directory.

---

### Pass 0.2 — Root .gitignore (early, before staging)

**Work:**

Create root `.gitignore` now — before `git add src/` — so build artifacts, data outputs, and secrets are never staged:

```gitignore
# Secrets
.env
api_keys.txt

# Python
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info
.venv/

# Outputs / data artifacts — scoped to src/data/ to avoid blocking src/config.json
src/data/output/
src/data/fiction/
src/data/chapters/
src/data/**/*.json
src/data/**/*.jsonl
*.pdf
*.mp3

# IDE
.vscode/
.idea/
```

**Note:** Phase 1 Pass 1.2 also creates this file. Since Phase 0 runs first, Phase 1 Pass 1.2 must skip the `.gitignore` creation step — it is already done here. Phase 1 Pass 1.2 still creates `.env.example` and updates `user_manual.md`.

---

### Pass 0.3 — Stage and Commit Unified Tree

**Work:**

1. Stage `src/` as a normal directory and the tracked root files. Stage only these — do not use `git add .`:
   ```bash
   git add src/ menu.py migration_agents/ tobe_edited_prompts/ initial_build.md initial_specs_shipping.md custom_init_specs.md .gitignore
   ```
   Do not stage `data/` (runtime outputs), `.env`, `.venv/`, or any file the `.gitignore` blocks. If unsure whether a file belongs, check `git check-ignore -v <file>` first.

2. Verify nothing sensitive is staged:
   ```bash
   git status
   ```
   `.env` must appear under "Changes not staged" or "Untracked files" — never under "Changes to be committed".

3. Commit:
   ```bash
   git commit -m "Phase 0: consolidate src/ into root repo, drop broken submodule"
   ```

---

### Pass 0.4 — Rename Root Directory (optional but recommended)

**Work:**

Rename the project root directory from `harnessv7_migrated/` to `app/`. This is a filesystem operation outside git — git does not track directory renames at the parent level.

```bash
# From the parent directory:
mv harnessv7_migrated app
```

Update any absolute paths in `.env`, shell scripts, or IDE workspace files that reference `harnessv7_migrated/` by name.

**This step is optional.** If skipping, treat `harnessv7_migrated/` as the project root for all subsequent phases. The name does not affect any code path.

---

### Phase 0 Gate

- [ ] `ls src/.git` returns "No such file or directory"
- [ ] `git ls-files src/ | head -5` returns Python source files (not a gitlink)
- [ ] Root `.gitignore` exists and `git check-ignore -v .env` reports it
- [ ] `git status` shows `.env` as untracked or ignored — never staged
- [ ] `python3 -m pytest src/ -q` still reports `113 passed, 0 failed`
- [ ] `git log --oneline -1` shows the Phase 0 consolidation commit

**Do not start Phase 1 until this gate passes.**

---

## Phase 1 — Security Gate

**Goal:** Remove the secret from git history and prevent re-introduction before any code is changed.
**Passes:** Sequential — 1.1 must complete before 1.2 can start.
**Who runs this:** One agent (or the operator manually).

---

### Pass 1.1 — Key Rotation (manual operator action)

**Owns:** No files — external action only.

**Work:**
- Log in to OpenRouter dashboard and rotate `OPENROUTER_API_KEY`.
- Log in to WaveSpeed dashboard and rotate `WAVESPEED_API_KEY`.
- Update your local `.env` file with the new values (do not commit it).

**Verify:** New keys work — run any LLM call and confirm it returns a response.

---

### Pass 1.2 — Git Cleanup and Baseline Secrets Hygiene

**Owns:** `.env.example` (new file), `user_manual.md`, git history.

**Note:** Root `.gitignore` was created in Phase 0 Pass 0.2 — do not recreate it here. This pass only handles history rewrite, `.env.example`, and `user_manual.md`.

**Work:**

1. Remove `.env` from git history:
   ```bash
   git filter-repo --path .env --invert-paths
   ```
   This rewrites history. All contributors must re-clone after this is pushed.

2. Create `.env.example` at project root:
   ```
   # Copy this file to .env and fill in real values. Never commit .env.
   # To keep .env outside the project tree entirely, set DOTENV_PATH before launching:
   #   DOTENV_PATH=~/.secrets/app.env python menu.py
   OPENROUTER_API_KEY=your-key-here
   WAVESPEED_API_KEY=your-key-here
   ```

3. Update `user_manual.md`: add a setup step telling users to copy `.env.example → .env` and fill in keys, with a note on the `DOTENV_PATH` option for keeping secrets outside the project tree.

**Verify:**
- `git ls-files .env` returns nothing.
- `git check-ignore -v .env api_keys.txt` reports the root `.gitignore` rule.
- `.env.example` exists and contains no real key values.

---

### Phase 1 Gate

- [ ] `git ls-files .env` returns nothing
- [ ] Root `.gitignore` exists and ignores `.env`, `api_keys.txt`, and output dirs
- [ ] `.env.example` exists with placeholder values only

**Do not start Phase 2 until this gate passes.**

---

## Phase 2 — Independent Fixes

**Goal:** Fix packaging, reliability, and config issues that have no dependencies on each other.
**Passes:** All 6 run in parallel. Each pass owns its files exclusively.
**Isolation:** Each pass runs in its own git worktree on its own branch. Merge all 6 branches sequentially after all passes complete and verify gate.

---

### Pass 2.1 — Python Version Fix

**Owns:** `src/pyproject.toml`, `src/.python-version`, `src/uv.lock`, `src/README.md`

**Current values (confirmed 2026-06-25):** `src/.python-version` = `3.14`; `src/pyproject.toml` = `requires-python = ">=3.14"`. System Python is `3.11.2`. Both files must change from `3.14` → `3.11`. Do not run `uv sync` in any earlier pass — it will fail against the system interpreter.

**Work:**
- Change `src/pyproject.toml` line 6: `requires-python = ">=3.11"` (currently `">=3.14"`).
- Change `src/.python-version` to contain `3.11` (currently `3.14`).
- Run `uv lock` from `src/` to regenerate `uv.lock` for the 3.11 baseline.
- Update the prerequisites table in `src/README.md` if it still mentions a version other than 3.11.

**Verify:** `uv sync` succeeds; `python3 -m pytest` from `src/` passes (113/113).

---

### Pass 2.2 — Config Defaults and Secrets Loading

**Owns:** `src/novel_pipeline/config.py`, `src/settings.py`, `menu.py`

**Current values (confirmed 2026-06-25):** `min_chapter_words` default is `100` at `config.py:112`; `load_dotenv()` is absent from `settings.py`; `run_id` uses `%Y%m%d_%H%M%S` (no microseconds).

**Work:**

`src/novel_pipeline/config.py` — change line 112:
- `"min_chapter_words": 100` → `"min_chapter_words": 1500`
- Do not touch `src/fiction/pipeline/config.toml` — it explicitly sets `min_chapter_words = 100` and that behavior must be preserved.
- Confirm standalone tests at lines 987 and 1105 still pass (they use explicit overrides, not the default).

`src/settings.py` — change `run_id` precision:
- Current: `datetime.now().strftime("%Y%m%d_%H%M%S")`
- Change to: `datetime.now().strftime("%Y%m%d_%H%M%S_%f")` (microsecond precision)

`src/settings.py` — add `.env` loading at module level (currently `python-dotenv` is a listed dependency but `load_dotenv()` is never called anywhere):
```python
from dotenv import load_dotenv
load_dotenv(os.environ.get("DOTENV_PATH") or Path(__file__).resolve().parent.parent / ".env")
```
Place this after the existing imports, before any `os.environ.get(...)` calls. This covers all CLI entry points that import from `src/`.

`menu.py` — add the same `.env` loading near the top of the file, after the existing imports:
```python
from dotenv import load_dotenv
load_dotenv(os.environ.get("DOTENV_PATH") or PROJECT_ROOT / ".env")
```
`PROJECT_ROOT` is already defined at line 8. This covers interactive use via the menu.

**Why both files:** `menu.py` launches subprocesses — each subprocess starts fresh and imports `src/settings.py` independently. Both locations are needed so secrets load regardless of whether the user enters via the menu or calls a CLI script directly.

**Usage after this change:**
```bash
# Default: looks for .env next to menu.py (same as before, but now actually loaded)
python menu.py

# Safe: .env lives outside the project tree — physically cannot be committed
DOTENV_PATH=~/.secrets/app.env python menu.py

# CI/production: skip .env entirely, inject secrets directly as env vars
OPENROUTER_API_KEY=xxx WAVESPEED_API_KEY=yyy python menu.py
```

**Verify:**
- `python3 -m pytest src/novel_pipeline/tests/test_pipeline.py::TestConfig::test_minimal_config_applies_defaults -v` passes.
- Two runs started in the same second produce distinct `run_id` directories.
- `DOTENV_PATH=/tmp/test.env python menu.py` loads keys from `/tmp/test.env` instead of the project root.
- Running `python src/cli/podcast.py --help` with `DOTENV_PATH` set loads the correct `.env`.

---

### Pass 2.3 — LLM Layer Timeouts

**Owns:** `src/llm/protocol.py`, `src/llm/factory.py`, `src/engines/factory.py`, `src/podcast_script_generator/llm/call_api.py`

**Note:** `src/fiction/seed_gen/cli.py` and `src/slicer/pdf_splitter.py` also need timeouts but are owned by Phase 3 passes to avoid file conflicts.

**Work:**

`src/llm/protocol.py` — verify `LLMClient.chat_completion` accepts `timeout: float | None = None`. Add it if absent.

`src/llm/factory.py`:
- Read `LLM_DEFAULT_TIMEOUT_SECONDS` env var; default `120.0`.
- Pass `timeout` into the provider constructor as the default for every `chat_completion` call.

`src/engines/factory.py`:
- `default_llm_script_engine()` and `default_splitter_engine()` must pass `timeout=...` when calling `create_client(...)`.
- Use env var `OPENROUTER_TIMEOUT_SECONDS` if set, else `120.0`.

`src/podcast_script_generator/llm/call_api.py`:
- Change the internal call to `llm.chat_completion(..., timeout=120.0)`.

**Verify:** Unit tests mock `requests.post` and assert `timeout` keyword is present in the call args.

---

### Pass 2.4 — TTS Polling Caps

**Owns:** `src/tts/cli.py`, `src/tts/recover.py`

**Note:** `TTSTimeoutError` already exists in `src/podcast_script_generator/llm/exceptions.py:13`. Import it — do not re-create it.

**Work:**

In both `src/tts/cli.py` (polling function around line 117) and `src/tts/recover.py` (polling function around line 39):

1. Add `max_wait_seconds: float` parameter; default `3600.0`.
2. Before the loop: `deadline = time.monotonic() + max_wait_seconds`.
3. At the top of each loop iteration:
   ```python
   if time.monotonic() > deadline:
       raise TTSTimeoutError(
           f"TTS job did not complete within {max_wait_seconds}s. "
           f"Run src/tts/recover.py <path> to resume."
       )
   ```
4. Read `WAVESPEED_MAX_WAIT_SECONDS` env var in each file; use it as the default if set.

**Verify:** A mocked test advances `time.monotonic` past the deadline and asserts `TTSTimeoutError` is raised with the expected message.

---

### Pass 2.5 — path_utils Module

**Owns:** `src/path_utils.py` (new file), `src/tests/test_path_utils.py` (new file)

**Work:**

Create `src/path_utils.py` — this module must not import any project-specific code:

```python
"""Reusable path helpers. No project-specific imports."""
from __future__ import annotations
import os
from pathlib import Path


def resolve_data_root(preferred: Path | str | None = None) -> Path:
    """Return an absolute Path for the data root.
    Priority: preferred argument > HARNESS_ROOT env var > src/ directory.
    """
    if preferred is not None:
        return Path(preferred).resolve()
    env = os.environ.get("HARNESS_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).parent.resolve()


def resolve_output_path(
    path: Path | str | None,
    root: Path,
    *default_segments: str,
) -> Path:
    """Resolve an output path against root; create parent dirs; check writability."""
    if path is None:
        resolved = root.joinpath(*default_segments)
    elif Path(path).is_absolute():
        resolved = Path(path)
    else:
        resolved = (root / path).resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    if not os.access(resolved.parent, os.W_OK):
        raise PermissionError(f"Output directory not writable: {resolved.parent}")
    return resolved


def resolve_input_path(path: Path | str, root: Path) -> Path:
    """Resolve a relative input path against root; verify it exists and is readable."""
    p = Path(path)
    resolved = p if p.is_absolute() else (root / p).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Input file not found: {resolved}")
    if not os.access(resolved, os.R_OK):
        raise PermissionError(f"Input file not readable: {resolved}")
    return resolved


def guard_path_escape(path: Path, root: Path) -> Path:
    """Raise ValueError if path resolves outside root."""
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        raise ValueError(f"Path {path!r} escapes the project root {root!r}")
    return resolved
```

Create `src/tests/test_path_utils.py` covering:
- `HARNESS_ROOT` env var wins over fallback in `resolve_data_root()`.
- `resolve_data_root(preferred=...)` wins over env var.
- Relative paths resolve against root in `resolve_output_path()`.
- Absolute paths pass through unchanged in `resolve_output_path()`.
- `resolve_input_path()` raises `FileNotFoundError` for missing files.
- `guard_path_escape()` rejects `../../../etc/passwd` and absolute paths outside root.
- `guard_path_escape()` accepts valid paths inside root.

**Verify:** `python3 -m pytest src/tests/test_path_utils.py -v` passes.

---

### Pass 2.6 — Stale Config Update

**Owns:** `src/config.json`

**Current values (confirmed 2026-06-25):** `api_url` is already `https://openrouter.ai/api/v1/chat/completions` — correct, no change needed. `model` is currently `"openrouter/free"` — must be changed to `"openrouter/auto"`. All other fields (`max_tokens`, `speakers`, `wavespeed_model`, `tts_scale`) are correct.

**Work:**
- `api_url` is already correct — do not touch it.
- Replace `model` value with `"openrouter/auto"` (currently `"openrouter/free"`).
- Leave all other fields unchanged.

**Verify:** Running without env vars routes calls to OpenRouter by default.

---

### Phase 2 Gate

- [ ] All 6 branches merged to main with no conflicts
- [ ] `uv sync` succeeds on Python 3.11
- [ ] `python3 -m pytest` from `src/` reports **113 passed, 0 failed**
- [ ] `src/path_utils.py` exists and its tests pass
- [ ] `TTSTimeoutError` is raised when the TTS deadline is exceeded
- [ ] `DOTENV_PATH=/tmp/test.env python menu.py` loads from `/tmp/test.env`; omitting `DOTENV_PATH` falls back to project root `.env`

**Do not start Phase 3 until this gate passes.**

---

## Phase 3 — Cross-File Consolidations

**Goal:** Handle the three file-conflict groups that could not run in parallel in Phase 2. Each pass now owns one group completely.
**Passes:** All 3 run in parallel.
**Isolation:** Each pass runs in its own git worktree on its own branch. Merge all 3 branches after all passes complete and verify gate.

---

### Pass 3.1 — Traceback Sanitization + seed_gen Timeout

**Owns:** `src/podcast_script_generator/llm/main.py`, `src/cli/podcast.py`, `src/fiction/seed_gen/cli.py`

**Work:**

`src/podcast_script_generator/llm/main.py` — extend the `if __name__ == "__main__"` block:
```python
if __name__ == "__main__":
    try:
        main()
    except PodcastError as e:
        sys.stderr.write(f"Error: {e}\n")
        raise SystemExit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        logger.exception("Unhandled exception in main")
        raise SystemExit(1)
```
Add `logger = logging.getLogger(__name__)` at module level if not already present.

`src/cli/podcast.py` — wrap the body of `main()` in a `try/except Exception` block:
```python
def main():
    # ... argument parsing stays unchanged above ...
    try:
        # existing main body
        ...
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        logger.exception("Unhandled exception")
        raise SystemExit(1)
```
Do not change argument parsing or any happy-path output.

`src/fiction/seed_gen/cli.py` — two changes in one pass to avoid re-opening the file:
1. Extend the existing `try/except` in `main()` (around line 262) to catch `Exception`:
   ```python
   except Exception as e:
       sys.stderr.write(f"Unexpected error: {e}\n")
       logger.exception("Unhandled exception in seed_gen")
       raise SystemExit(1)
   ```
2. At line 279, pass `timeout=120.0` to `call_api(...)` (deferred from Pass 2.3 to avoid file conflict).

**Verify:**
- A test triggers `RuntimeError` in each entry point; asserts stderr contains no traceback and contains `Error:` or `Unexpected error:`; exit code is 1.

---

### Pass 3.2 — Slicer: Timeout + Path Hardening

**Owns:** `src/slicer/pdf_splitter.py`

**Depends on:** `src/path_utils.py` (created in Pass 2.5 — must exist before this pass).

**Work:**

`src/slicer/pdf_splitter.py` — two changes in one pass:

1. **Timeout** (deferred from Pass 2.3): In `main()` around line 799–803, add `timeout` to the kwargs passed to `create_client(...)`. Read `OPENROUTER_TIMEOUT_SECONDS` env var, default `120.0`.

2. **Path hardening**: Change `DEFAULT_OUTPUT_DIR = "split_chapters"` — anchor it:
   - CLI `main()` accepts `--root` argument (default from `HARNESS_ROOT` env var via `path_utils.resolve_data_root()`).
   - When `-o/--output-dir` is omitted, resolve to `root / "data" / "chapters"` instead of CWD-relative.
   - When `run_splitter()` is called programmatically, `output_dir` must be explicit — remove any hidden CWD default.
   - The standalone CLI still accepts `-o/--output-dir`; document the new default behaviour in `user_manual.md`.

**Verify:**
- Invoking `pdf_splitter.py` from an arbitrary working directory writes chapters under the project root, not CWD.
- Unit test asserts `timeout` keyword is passed to `requests.post`.

---

### Pass 3.3 — Endpoints Cleanup

**Owns:** `src/endpoints/podcast.py`

**Depends on:** `src/path_utils.py` (created in Pass 2.5 — must exist before this pass).

**Work:**
- Remove unused `_SRC` and `_ROOT` constants (both derived from `__file__`).
- Make `settings` a required argument to `generate_chapter_podcast()`. If backward compatibility with no-arg calls is needed, raise `TypeError` with the message: `"settings is required; construct PodcastSettings(root=...) and pass it explicitly."`.
- Keep `script_out.parent.mkdir(parents=True, exist_ok=True)`.
- `src/cli/podcast.py` always passes `settings`, so the CLI path is unchanged.

**Verify:** Calling `generate_chapter_podcast()` without `settings` raises `TypeError` with a clear message.

---

### Phase 3 Gate

- [ ] All 3 branches merged to main with no conflicts
- [ ] `python3 -m pytest` from `src/` reports **113 passed, 0 failed**
- [ ] Triggering a `RuntimeError` in any CLI entry point prints a sanitized error and exits 1 without a traceback
- [ ] `generate_chapter_podcast()` without `settings` raises `TypeError`
- [ ] `pdf_splitter.py` output resolves under project root when `-o` is omitted

**Do not start Phase 4 until this gate passes.**

---

## Phase 4 — CLI Podcast Hardening

**Goal:** Fully harden `src/cli/podcast.py` with path validation and observability. This file was already modified in Phase 3 (Pass 3.1 added traceback handling), so it can only be worked on now.
**Passes:** 1 pass (single agent).

---

### Pass 4.1 — CLI Path Validation and Observability

**Owns:** `src/cli/podcast.py`, `src/cli/fiction.py`

**Depends on:** `src/path_utils.py` (Phase 2), traceback wrap in `src/cli/podcast.py` (Phase 3 Pass 3.1).

**Work:**

`src/cli/podcast.py`:

1. **Path validation** — add `--root` argument and resolve all I/O paths:
   ```bash
   # These must all still work
   python src/cli/podcast.py ../books/foo.pdf --skip-audio
   HARNESS_ROOT=/app/data python src/cli/podcast.py /app/input/foo.pdf --skip-audio
   python src/cli/podcast.py ../books/foo.pdf --root ./my-data --scripts-out ./my-data/scripts
   ```
   - Add `--root` argument; default from `HARNESS_ROOT` env var via `path_utils.resolve_data_root()`.
   - Resolve `--scripts-out`, `--audio-out`, `--chapters-dir` via `path_utils.resolve_output_path()`.
   - Validate input PDFs (`pdf` positional, `--book`) via `path_utils.resolve_input_path()`.
   - Build `PodcastSettings(root=root, scripts_out=..., audio_out=..., chapters_dir=...)` with absolute paths.
   - When `--root` is absent and `HARNESS_ROOT` is unset, behavior is identical to today.

2. **Observability**:
   - Read `LOG_LEVEL` env var; apply via `logging.basicConfig(level=...)`.
   - Add `RotatingFileHandler` (max 10 MB) for the module logger.
   - Convert any remaining `print()` error messages to `logger.error()` calls.

`src/cli/fiction.py`:
   - Read `LOG_LEVEL` env var; apply via `logging.basicConfig(level=...)`.
   - Add `RotatingFileHandler` (max 10 MB).
   - Convert `print()` error messages to `logger.error()` calls.
   - Keep existing JSONL `log_event` for `novel_pipeline`; do not remove it.

**Verify:**
- `python src/cli/podcast.py ../books/foo.pdf --scripts-out /etc/foo` raises a clear path error before any API call.
- `python src/cli/podcast.py ../books/George_Polya_How_To_Solve_It_.pdf --skip-audio` still works from repo root.
- `HARNESS_ROOT=/tmp/harness_test python src/cli/podcast.py /some/input.pdf --skip-audio` writes outputs under `/tmp/harness_test`.
- `LOG_LEVEL=DEBUG` produces debug output in the log file.

---

### Phase 4 Gate

- [ ] `python3 -m pytest` from `src/` reports **113 passed, 0 failed**
- [ ] Path validation rejects `../../../etc/passwd` and unwritable output dirs before any API call
- [ ] All README CLI invocations work unchanged
- [ ] `HARNESS_ROOT` override routes output to the specified directory
- [ ] `LOG_LEVEL=DEBUG` produces debug output; log files cap at 10 MB

**Do not start Phase 5 until this gate passes.**

---

## Phase 5 — Validation and Coverage

**Goal:** Expand the test suite to cover all new and previously untested modules; confirm the full project is shippable.
**Passes:** 1 pass (single agent with full repo access).

---

### Pass 5.1 — Test Expansion and Final Validation

**Owns:** All test files (new and modified). No production code changes.

**Work:**

Convert `src/podcast_script_generator/llm/test_all.py` into a real pytest module under `src/podcast_script_generator/llm/tests/test_podcast.py`. Keep coverage identical; just make it runnable via `pytest`.

Add new test files:
- `src/tests/test_engines.py` — `fiction_meta` content resolution and speaker mapping in `src/engines/llm_script.py`.
- `src/tests/test_normalize.py` — speaker label normalization in `src/util/normalize.py`.
- `src/tests/test_llm_factory.py` — env-var resolution and provider dispatch in `src/llm/factory.py` and `src/llm/env.py`.
- `src/tests/test_cli_podcast.py` — argument parsing with `monkeypatch`; assert `--skip-audio` does not call the audio engine; assert bad path raises before any API call.
- `src/tests/test_cli_fiction.py` — env injection and error sanitization.

Add smoke tests (mock network and filesystem):
- `src/tests/test_slicer_smoke.py` — `run_splitter()` with a mock PDF and mocked LLM client.
- `src/tests/test_tts_smoke.py` — polling function raises `TTSTimeoutError` when deadline is exceeded.
- `src/tests/test_seed_gen_smoke.py` — `main()` with mocked `call_api`; assert sanitized stderr on error.

Update existing tests that call `PodcastSettings()` with no args: pass `root=tmp_path` to all such calls.

Run the full test suite as the final step:
```bash
python3 -m pytest src/ -v
PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py
```

**Verify:**
- `pytest` from `src/` reports **>120 passed, 0 failed**.
- `PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py` still reports **37 passed**.

---

### Phase 5 Gate — Shipping Criteria

- [ ] `git ls-files .env` returns nothing
- [ ] Root `.gitignore` ignores `.env`, `api_keys.txt`, build artifacts, and output files
- [ ] `uv sync` succeeds on Python 3.11
- [ ] `python3 -m pytest` from `src/` reports **>120 passed, 0 failed**
- [ ] `PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py` reports **37 passed**
- [ ] Every `requests.post` / `requests.get` call has a non-`None` timeout
- [ ] TTS polling loop has a deadline; `TTSTimeoutError` is raised when exceeded
- [ ] Any CLI entry point with a mocked failing dependency prints a sanitized error to stderr and exits 1 without a traceback
- [ ] Two podcast CLI runs in the same second produce distinct `run_id` directories
- [ ] `src/config.json` points to OpenRouter by default
- [ ] `python src/cli/podcast.py ../books/foo.pdf --scripts-out /etc/foo` raises a path error before any API call
- [ ] `python src/cli/podcast.py ../books/George_Polya_How_To_Solve_It_.pdf --skip-audio` still works from repo root
- [ ] `HARNESS_ROOT=/tmp/harness_test python src/cli/podcast.py /some/input.pdf --skip-audio` writes under `/tmp/harness_test`
- [ ] `src/fiction/pipeline/config.toml` still produces short-chapter output when run
- [ ] `DOTENV_PATH=~/.secrets/app.env python menu.py` loads secrets from outside the project tree
- [ ] `git ls-files '*.env'` and `git ls-files '*.json' -- src/config.json` confirm `src/config.json` is tracked and no `.env` file is tracked

---

## What Not to Do

- Do not change the `novel_pipeline` architecture, state file format, or JSONL event schema unless a bug demands it.
- Do not remove or rename existing CLI flags.
- Do not add features, animation storyboards, or new pipelines.
- Do not migrate existing generated fiction chapters or state files.
- Prefer adding optional parameters with defaults over changing required signatures.
- Do not re-create `TTSTimeoutError` — it already exists in `exceptions.py:13`.
- Do not change `src/podcast_script_generator/llm/save_output.py` path-traversal guard — it is already correct.
- Do not put path validation logic anywhere other than `src/path_utils.py`.
- `run_chapter.py` and `run_book.py` appear only in `src/README.md` docs — no code action needed.
