# TICKET T-003: Project-owned env namespace — OPENROUTER_*/LLM_* → BOOKGEN_LLM_*

```
Mode: alone
Depends-on: T-002 MERGED FIRST (this ticket renames a line T-002 adds)
Timing: after chapter 006 lands — this deliberately breaks the current env
        contract; never implement mid-run
Worktree: main working tree, run everything from the repo root
Write-set: src/llm/env.py,
           src/llm/factory.py,
           src/llm/providers/openrouter.py       (error-message string only),
           src/llm/tests/test_factory.py,
           src/tests/test_llm_factory.py,
           src/endpoints/tests/test_fiction.py,
           src/podcast_script_generator/llm/test_all.py,
           src/podcast_script_generator/llm/tests/test_podcast.py,
           src/podcast_script_generator/llm/main.py       (docstring line only),
           fiction_loop/tools/analyst.py,
           fiction_loop/tools/invoke_writer.py    (error-message string only),
           fiction_loop/tools/refresh_living_doc.py (error-message string only),
           fiction_loop/tools/pipeline_config.toml  (comment only),
           fiction_loop/tools/INTEGRATION_SPECS.md,
           fiction_loop/agents/writer.md,
           fiction_loop/RUN.md,
           .env.example
Hot-files: none
State-access: none — do NOT touch fiction_loop/state/, fiction_loop/prompts/,
              fiction_loop/core/living_document.md, or any .pipeline_spend.json
Paid-calls: forbidden (tests are offline)
Env-conduct: NEVER cat/grep/print .env or `env | grep`. The implementer NEVER
             edits .env — the owner step in §4 covers it.
```

Read `fiction_loop/CONTRIBUTING.md` before editing anything under
`fiction_loop/`.

## 1. Problem (root cause of the 2026-07-18 step-8 404; see T-002 §1)

The LLM client is provider-agnostic, but its env vars carry a vendor's name
(`OPENROUTER_*`). Vendor-named and SDK-conventional variables are exactly the
names that OTHER tools sharing the shell also set: the Qwen companion harness
exported its own `OPENROUTER_URL` (base-url convention), which silently
overrode `.env`'s full endpoint (shell env wins by design) and 404'd the
Writer. T-002 made that *value* harmless via normalization; this ticket makes
the *collision* impossible: a project-owned prefix no external harness will
ever export (LAW 6 prevention at the root; LAW 2 — one naming convention).

## 2. The rename (mechanical; new name = BOOKGEN_ + role)

| Old | New |
|---|---|
| `OPENROUTER_API_KEY` | `BOOKGEN_LLM_API_KEY` |
| `OPENROUTER_MODEL` | `BOOKGEN_LLM_MODEL` |
| `OPENROUTER_URL` | `BOOKGEN_LLM_API_URL` |
| `OPENROUTER_MAX_TOKENS` | `BOOKGEN_LLM_MAX_TOKENS` |
| `OPENROUTER_RETRY_AFTER` | `BOOKGEN_LLM_RETRY_AFTER` |
| `LLM_PROVIDER` | `BOOKGEN_LLM_PROVIDER` |
| `LLM_DEFAULT_TIMEOUT_SECONDS` | `BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS` |

**Clean break — no aliases.** Do NOT keep reading any old name as fallback:
a compat shim would re-import the vulnerability (an external harness's
`OPENROUTER_URL` would again be honored whenever the new var is absent).

### Scope boundary (deliberate, do not "complete" it)

- IN: everything flowing through `src/llm/env.py` + `src/llm/factory.py` —
  the fiction pipeline AND `src/podcast_script_generator/llm/` (its tests set
  the old key name; they are in the write-set).
- OUT: `src/engines/` + `src/slicer/` and their `OPENROUTER_TIMEOUT_SECONDS`
  — a separate, older transport family for the podcast audio path that never
  runs under a companion shell. Renaming it is a future ticket if that
  subsystem is ever revived. Leave every hit there untouched.
- OUT: historical/dated records — `src/phases/`, `src/docs/`, `src/fiction/`,
  `src/README.md`, `src/initial_readme.md`, `fiction_loop/specs/
  pipeline_fixes.spec.md`, all `progress/` handoffs. Records keep old names.

## 3. Steps

1. `src/llm/env.py`: rename the five `os.environ.get(...)` keys per the
   table; update the docstring (it promises "renamed in one place" — this is
   that rename); update its `LLM_PROVIDER` mention.
2. `src/llm/factory.py`: rename `LLM_PROVIDER` and
   `LLM_DEFAULT_TIMEOUT_SECONDS` reads AND their error-message strings.
3. `src/llm/providers/openrouter.py`: the `OPENROUTER_MAX_TOKENS must be an
   integer` message → `BOOKGEN_LLM_MAX_TOKENS ...`. No other change (T-002's
   normalizer is name-agnostic — takes whatever URL wins; do not touch it).
4. `fiction_loop/tools/analyst.py`: rename ALL occurrences — the
   `os.environ.get` reads (~lines 50, 53), the `.env` key-name prefix checks
   (~lines 56, 58 — these compare key NAMES only, conduct-safe), the fix-text
   strings (~lines 64, 117), and T-002's freshness-branch
   `os.environ.get("OPENROUTER_URL")` → `BOOKGEN_LLM_API_URL`.
5. Error-hint strings in `invoke_writer.py` (~line 137) and
   `refresh_living_doc.py` (~line 115): `Check OPENROUTER_API_KEY` →
   `Check BOOKGEN_LLM_API_KEY`.
6. Live docs: `fiction_loop/RUN.md` (~line 14), `fiction_loop/agents/
   writer.md` (~lines 19, 74, 128), `fiction_loop/tools/INTEGRATION_SPECS.md`
   (~lines 252, 272, 432–435 — the 432 row's "variable name is legacy" note
   can now be replaced by "project-owned name, renamed 2026-07 (T-003)"),
   `fiction_loop/tools/pipeline_config.toml` header comment (~line 10).
7. `.env.example`: rename the three keys; keep values as-is.
8. `src/podcast_script_generator/llm/main.py`: the module docstring's
   `OPENROUTER_API_KEY  required for the API call` line →
   `BOOKGEN_LLM_API_KEY ...`. Docstring ONLY — the module resolves env via
   `llm.env.resolve_from_env`, so no code change is needed here. (Added
   2026-07-18 after the first dispatch correctly STOPPED on the
   write-set/acceptance-2 contradiction; senior re-swept the acceptance-2
   grep — this was the only file outside the write-set.)
9. Tests — rename env keys ONLY, never assertions' semantics:
   `src/llm/tests/test_factory.py`, `src/tests/test_llm_factory.py`,
   `src/endpoints/tests/test_fiction.py` (docstrings mentioning the old
   name may be updated), `src/podcast_script_generator/llm/test_all.py`
   (~line 284), `src/podcast_script_generator/llm/tests/test_podcast.py`
   (~line 325).

## 4. OWNER STEP (implementer: request this, never do it)

The owner renames the keys inside `.env` per the §2 table (same values, new
names) and removes/renames any `OPENROUTER_*` exports in their companion
harness config. Until this is done the pipeline will fail STEP 0 with the
analyst's missing-key CRITICAL — that failure is the correct signal, not a
bug. Do not proceed to acceptance 4–5 before the owner confirms.

**Delegation (owner → senior, 2026-07-18):** the owner delegated the `.env`
key rename to the senior instance. Senior performs it BLIND — in-place rename
of key NAMES only per the §2 table; never cat/grep/print the file or its
values — AFTER the implementation commit lands and BEFORE acceptance 4–5.
Verified 2026-07-18: repo and shell rc files carry no `OPENROUTER_*` exports;
the one residual check is the Qwen companion session's own live environment
(owner confirms nothing is exported there before the next chapter run). The
implementer contract is unchanged: never touch `.env`.

## 5. Acceptance (numbered; ALL must pass)

1. `PYTHONPATH=src uv run --frozen --with pytest python -m pytest src/ -q`
   → green, serially (Raspberry Pi — no `-n`, nothing heavy in parallel).
   pytest is NOT a declared dependency — the `uv run --with` overlay is the
   sanctioned way to get it (T-002 §6); do not add it to pyproject.toml.
2. `grep -rn "OPENROUTER_\|LLM_PROVIDER\|LLM_DEFAULT_TIMEOUT" src/llm src/endpoints src/podcast_script_generator fiction_loop --include="*.py" --include="*.md" --include="*.toml"`
   → zero hits outside `fiction_loop/specs/pipeline_fixes.spec.md` (record,
   untouched).
3. `grep -rn "OPENROUTER_TIMEOUT_SECONDS" src/engines src/slicer | wc -l`
   → unchanged vs HEAD (scope boundary respected).
4. (after owner step) `PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py`
   → key-present check passes; no CRITICAL from the rename.
5. (after owner step) `BOOKGEN_LLM_MODEL=probe PYTHONPATH=src .venv/bin/python -c "import sys; sys.path.insert(0,'src'); from llm.env import resolve_from_env; print(resolve_from_env()['model'])"`
   → prints `probe`.
6. `git status --porcelain` → changes ONLY within the write-set.

## 6. Commit

`refactor(env): project-owned BOOKGEN_LLM_* namespace, clean break from OPENROUTER_*/LLM_*`

Trailers:
```
Ticket: T-003
Implemented-by: <Codex|Qwen — whoever implements>
```

Pathspec-limit the commit to exactly the write-set files (never
`git commit -a`).

## 7. Constraints

- Raspberry Pi; zero paid calls; nothing here needs the network or a key.
- Clean break means clean: if any test seems to WANT a legacy fallback,
  that is a STOP-and-report, not a shim.
- Never touch `fiction_loop/state/`, `fiction_loop/prompts/`,
  `fiction_loop/core/living_document.md`, any `.pipeline_spend.json`,
  `books/`, `fiction_loop/logs/`, or `.env`.
- On ANY failure: stop at that step, record it in §8 exactly as observed,
  leave the tree coherent.

## 8. Implementer log (append below; never delete the ticket body)

### 2026-07-18 — Codex — STOPPED before implementation

- Read `AGENTS.md`, `HANDOFF.md`, the current handoff, and
  `fiction_loop/CONTRIBUTING.md` as required.
- Preflight command:
  `rg -n 'OPENROUTER_|LLM_PROVIDER|LLM_DEFAULT_TIMEOUT' src/llm src/endpoints src/podcast_script_generator fiction_loop/tools/analyst.py fiction_loop/tools/invoke_writer.py fiction_loop/tools/refresh_living_doc.py fiction_loop/tools/pipeline_config.toml fiction_loop/tools/INTEGRATION_SPECS.md fiction_loop/agents/writer.md fiction_loop/RUN.md .env.example`
- STOP reason: the command found
  `src/podcast_script_generator/llm/main.py:7:    OPENROUTER_API_KEY  required for the API call (via llm.env.resolve_from_env).`
  Acceptance 2 requires zero old-name hits under
  `src/podcast_script_generator`, but `src/podcast_script_generator/llm/main.py`
  is not in the ticket write-set. Strict write-set compliance and acceptance 2
  therefore cannot both be satisfied without a ticket correction.
- No implementation files were changed. Acceptance 1–3 and 6 were not run
  because the ticket requires STOP on any failure. `.env` was not inspected or
  modified.

### 2026-07-18 — senior — TICKET CORRECTED; REDISPATCH AUTHORIZED

- The STOP was correct and the finding verified: senior re-ran the
  acceptance-2 grep against HEAD — `src/podcast_script_generator/llm/main.py`
  (1 hit, docstring line 7) was the ONLY file with legacy-name hits outside
  the write-set. Every other hit maps to a write-set file.
- Resolution: file ADDED to the write-set (docstring line only) with new §3
  step 8; old step 8 renumbered to 9. Rationale: the module resolves env via
  `llm.env.resolve_from_env`, so after the rename the docstring would be
  actively wrong documentation (LAW 2) — exempting the hit was the worse fix.
- Ticket body is otherwise unchanged. Redispatch and implement as written.
