# TICKET T-002: Normalize api_url in the LLM client + analyst signature for the empty-body 404

```
Mode: alone
Worktree: main working tree, run everything from the repo root
Write-set: src/llm/providers/openrouter.py,
           src/llm/providers/tests/test_openrouter.py,
           fiction_loop/tools/analyst.py,
           fiction_loop/agents/writer.md
Hot-files: none
State-access: none — do NOT touch fiction_loop/state/, fiction_loop/prompts/,
              fiction_loop/core/living_document.md, or any .pipeline_spend.json
Paid-calls: forbidden (tests are offline; analyst is a zero-token tool)
Env-conduct: NEVER cat/grep/print .env or `env | grep`. The only permitted
             env inspection is `echo $OPENROUTER_URL` / `echo $OPENROUTER_MODEL`.
```

Read `fiction_loop/CONTRIBUTING.md` before editing anything under
`fiction_loop/`. This ticket is the LAW 6 durable fix for the 2026-07-18
step-8 404 (see `progress/handoff-2026-07-18-deepseek-switch-404.md` §3).

## 1. Problem (root cause CONFIRMED 2026-07-18 by echo check in the companion session)

The chapter-006 Writer bridge failed at step 8 with `API error: OpenRouter
returned 404: ` (empty body), BRIDGE_EXIT:1. Confirmed cause:

- The companion harness's shell exported `OPENROUTER_URL=https://api.deepseek.com`
  — a BASE url (OpenAI-SDK `base_url` convention, no path).
- `.env` holds the correct full endpoint (`.../v1/chat/completions`), but shell
  env wins over `.env` by design (`invoke_writer.py` `_load_dotenv_fallback`,
  lines 19–32 at HEAD 86399e9; `src/llm/env.py` `resolve_from_env`, spread last).
- The client (`src/llm/providers/openrouter.py`, `requests.post(self.api_url, ...)`
  line 131–136) POSTs to the URL as-is → provider answers 404 with an EMPTY
  body. A model-not-found 404 would carry a JSON body; empty body = bad path.
- `analyst.py` had no signature for `returned 404` → verdict "UNKNOWN
  signature" instead of pointing at the env override.

Three failure modes to close (LAW 6, prevention > detection > correction):
prevention = normalize the URL in the client; detection = analyst signature
with a live env check; plus a second-offense conduct wording fix in writer.md.

## 2. Fix

### Step 1 — prevention: normalize `api_url` in the client (single source, LAW 2)

In `src/llm/providers/openrouter.py`, in `__init__`, replace the line

```python
self.api_url = api_url if api_url is not None else _DEFAULT_API_URL
```

with assignment through a new module-level helper (place it near
`_DEFAULT_API_URL`):

```python
def _normalize_api_url(api_url: str | None) -> str:
    """OpenAI-compatible providers serve chat at <base>/v1/chat/completions.
    Callers (and shell env, which wins over .env) sometimes supply a bare
    base_url; a raw POST to it returns an empty-body 404. Complete the path;
    leave any URL that already ends in /chat/completions untouched."""
    if api_url is None:
        return _DEFAULT_API_URL
    url = api_url.rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return url + "/chat/completions"
    return url + "/v1/chat/completions"
```

and `self.api_url = _normalize_api_url(api_url)`. Change nothing else in the
file. (Deliberate scope choice: every current caller — both bridges and
`src/endpoints` — targets OpenAI-convention endpoints; a provider with a
genuinely different path shape would get its own provider class per
`src/llm/env.py`'s comment, not this one.)

### Step 2 — tests for the helper

In `src/llm/providers/tests/test_openrouter.py`, add four cases (construct the
transport with a dummy `api_key` and assert `transport.api_url`; match the
file's existing style):

1. base url `https://api.deepseek.com` → `https://api.deepseek.com/v1/chat/completions`
2. `https://api.deepseek.com/v1` (and with trailing `/`) → same full path
3. full path passes through unchanged (also with trailing `/` stripped)
4. `api_url=None` → `_DEFAULT_API_URL` unchanged

Do NOT modify `src/endpoints/tests/test_fiction.py` — its env-precedence
tests use full-path URLs and must keep passing untouched.

### Step 3 — detection: analyst signature with live env check

In `fiction_loop/tools/analyst.py` `check_bridge_outs()` (SIGS loop, lines
143–155 at HEAD): add the needle `"returned 404"` to `SIGS` as
`("returned 404", "CRITICAL", "endpoint path wrong — a shell-exported
OPENROUTER_URL (base url, no /v1/chat/completions) overrides .env",
"run `echo $OPENROUTER_URL` in the run shell; unset it or export the full
/v1/chat/completions url")`.

Then give it the same stale-receipt aging the missing-key needle got in
b1ae048 (LAW 9 freshness — an old 404 .out must not trip the STEP 0 gate
after the env is fixed): in the loop's special-case branch, when
`needle == "returned 404"`, check `os.environ.get("OPENROUTER_URL", "")`
directly (this is NOT reading .env; conduct-safe):

- if it is set and its path does not end in `/chat/completions` → report the
  CRITICAL above, appending "override present NOW in THIS shell";
- otherwise → INFO: "previous bridge run failed on a bad endpoint path, but
  no bad override is present NOW — stale receipt; safe to re-run step 8".

Never print or log the URL's value beyond that suffix check — treat it as
sensitive plumbing; report only present/absent/malformed.

### Step 4 — conduct wording (second offense, cosmetic)

In `fiction_loop/agents/writer.md` CRITICAL RULES (after the STOP-DON'T-GUESS
bullet, line ~137): add one bullet stating that on ANY error the final
terminal status line MUST begin `BLOCKED` — never `DONE — Error:` or any
`DONE` variant (observed twice: ch5 post-mortem and 2026-07-18 run; the
analyst is immune, the log line is still wrong).

## 3. Acceptance (numbered; ALL must pass)

1. `PYTHONPATH=src .venv/bin/python -m pytest src/llm/providers/tests/ src/llm/tests/ src/endpoints/tests/test_fiction.py -q`
   → all green, including the 4 new cases; no test file other than
   `test_openrouter.py` modified.
2. `grep -n "returned 404" fiction_loop/tools/analyst.py` → hit inside SIGS
   and inside the freshness branch.
3. Simulated stale receipt: with the current shell holding NO
   `OPENROUTER_URL` override, and given the 2026-07-18 `08_writer_bridge.out`
   containing `returned 404` (if step 8 has since been re-run and overwrote
   it, reproduce by appending the literal lines `API error: OpenRouter
   returned 404: ` and `BRIDGE_EXIT:1` to a COPY under the scratchpad and
   point the check at it in a throwaway REPL — do NOT edit real logs),
   `PYTHONPATH=src .venv/bin/python fiction_loop/tools/analyst.py` reports it
   as INFO stale-receipt, NOT CRITICAL, and exits without tripping the gate.
4. `.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from llm.providers.openrouter import _normalize_api_url as n; print(n('https://api.deepseek.com'))"`
   → prints `https://api.deepseek.com/v1/chat/completions`.
5. `git status --porcelain` shows changes ONLY within the write-set (author's
   pre-existing modified/untracked files in `tickets/`, `progress/`,
   `fiction_loop/prompts/` may be present — leave them alone, do not stage).

## 4. Commit

`fix(llm): normalize api_url to full chat/completions path; analyst 404 signature`

Trailers:
```
Ticket: T-002
Implemented-by: <Codex|Qwen — whoever implements>
```

Pathspec-limit the commit to exactly the four write-set files (never
`git commit -a`).

## 5. Constraints

- This machine is a Raspberry Pi — run the test suite serially, nothing heavy
  in parallel, and NEVER during a pipeline run.
- Zero paid calls. Nothing in this ticket needs the network or an API key.
- NEVER cat/grep/print `.env` or `env | grep`. Step 3's env check reads
  `os.environ` in-process and reports only present/absent/malformed.
- Never touch `fiction_loop/state/`, `fiction_loop/prompts/`,
  `fiction_loop/core/living_document.md`, any `.pipeline_spend.json`, `books/`,
  or real files under `fiction_loop/logs/` (acceptance 3 uses a scratchpad copy).
- On ANY failure: stop at that step, record it in §6 exactly as observed,
  leave the tree coherent. Do not improvise alternative designs.

## 6. Implementer log (append below; never delete the ticket body)

- 2026-07-18 — Codex: implemented Steps 1–4 in the four-file write-set.
  Acceptance stopped at check 1 exactly as observed:
  `/home/mr/Desktop/python/github_clones_working_on/book_podcast_fiction_generator/.venv/bin/python: No module named pytest`
  (command exit 1). Per §5, did not install dependencies, improvise an
  alternative test command, run later acceptance checks, or commit.
- 2026-07-18 — senior acceptance: PASSED, all 5 checks. Check-1 blocker was a
  ticket-authoring gap, not an implementation fault: pytest has never been a
  declared dependency in `pyproject.toml` (no dev group exists). Ran the same
  suite via uv's ephemeral overlay — `PYTHONPATH=src uv run --frozen --with
  pytest python -m pytest src/llm/providers/tests/ src/llm/tests/
  src/endpoints/tests/test_fiction.py -q` → 27 passed (pyproject/uv.lock
  untouched). Checks 2–5: signature present in SIGS + freshness branch;
  analyst vs the real chapter_006 .out (no override in shell) → INFO stale
  receipt, gate not tripped; CRITICAL branch verified with a one-process
  simulated base-url override; `_normalize_api_url` prints the full path;
  status limited to write-set + pre-existing author files. Codex's `urlsplit`
  path check is an improvement over the ticket's naive suffix spec — accepted.
  Committed by the senior on Codex's behalf (Codex stopped pre-commit per §5).
  Follow-up for the owner: decide whether to add a `dev` dependency group with
  pytest via uv, or standardize on the `uv run --with pytest` form (T-003
  acceptance updated to the latter).
