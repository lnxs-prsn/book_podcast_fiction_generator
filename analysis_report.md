# Spec Review Report: `fix_specsv2.md`

**Review scope:** defects in the specification document itself. Code that has not been implemented yet is listed only as a codebase gap, not analyzed in depth.

---

## Section 1 — Summary Table

| Severity | Count | Issues |
|----------|-------|--------|
| CRITICAL | 0 | — |
| FALSE POSITIVE | 1 | C1: Slicer exception narrowing breaks non-LLM error handling |
| HIGH | 0 | — |
| RESOLVED | 9 | C2: Podcast CLI; H1: Factory verification command; H2: Stale `test_pipeline.py` move; H3: Verification grep omits podcast generator; H4: `main.py` `llm` parameter only in tests; H5: Dead tests for removed behaviors; M1: LLMError escapes engine path; M2: seed_gen exit unspecified; M5: boundary claim overclaimed |
| MEDIUM | 2 | `seed_gen` import path ambiguous; `run_splitter` default unspecified |
| LOW | 2 | CLI `sys.path` guards not covered by verification; Step 2 → Step 3 ordering implicit |

---

## Section 2 — Spec Defects

### CRITICAL

#### ~~C1~~ — FALSE POSITIVE: Slicer exception narrowing breaks non-LLM error handling

**Finding:** The analysis report misread the code structure of `get_toc_from_llm`. It assumed a single broad `except Exception` wrapping the entire function body. The actual code has three separate, already-compartmentalized try/except blocks:

- Lines 218–222: narrow except around the `call_api` import only
- Lines 228–234: narrow except around `fitz.open(pdf_path)` only
- Lines 285–289: narrow except around the LLM call only

The spec's instruction to "replace the broad `except Exception` with `except LLMError`" refers to the block at lines 285–289, which wraps only the LLM call. Replacing it with `except LLMError` is correct and safe — PDF and OCR failures are handled by their own blocks above and are unaffected. The spec instruction is sound; no fix needed in `fix_specsv2.md`.

<details>
<summary>Original finding (retained for reference)</summary>

- **What the spec says (Step 3, `src/slicer/pdf_splitter.py`):**  
  "Add `from llm.exceptions import LLMError` and replace the broad `except Exception` with `except LLMError` — `llm.call()` raises `LLMError` on transport failure... Log the error and return `None`."
- **Why it was claimed wrong:**  
  `get_toc_from_llm` was assumed to wrap the entire Stage 4 body, including `fitz.open(pdf_path)`, `_ocr_pages_text(...)`, and the LLM call, in a single broad `except Exception`. Code inspection showed this assumption was incorrect.
- **Dimensions:** B (exception flow), G (scope completeness).

</details>

#### ~~C2~~ — RESOLVED: Podcast CLI leaves `LLMConfigError` unhandled

**Resolution:** The root issue was that the CLI was doing wiring work (engine construction) that belongs in the endpoint. The fix follows the same pattern the spec applied to the splitter engine: remove eager construction from the CLI entirely, move responsibility to the endpoint. Two spec entries updated in Step 3 — `src/cli/podcast.py` and `src/endpoints/podcast.py`.

- `src/cli/podcast.py`: remove `default_llm_script_engine` from the import and replace the eager construction at line 78 with `script_engine = None`.
- `src/endpoints/podcast.py` (`generate_book_podcast`): add an early script-engine construction block after the `resolve_dir` existence check and before the `pdfs = sorted(...)` call, wrapped in `try/except LLMConfigError → return [PodcastResult(error=e)]`. Placement after the `resolve_dir` check prevents unnecessary construction when there are no chapter PDFs. One structured error for the whole book instead of N per-chapter errors.

<details>
<summary>Original finding (retained for reference)</summary>

- **What the spec said (Step 3, `src/cli/podcast.py`):**  
  "Remove `default_splitter_engine` from the `engines.factory` import... Remove the `splitter_engine=...` kwarg... No other changes."
- **Why it was wrong:**  
  `src/cli/podcast.py` still constructs the script engine at the CLI boundary via `default_llm_script_engine(mode=args.mode)` (line 78). That factory now builds an `LLMClient`, which raises `LLMConfigError` if `OPENROUTER_API_KEY` is missing. The spec's "No other changes" left this unhandled.
- **Dimensions:** B (exception flow), E (test/CLI alignment), G (call-site coverage).

</details>

---

### HIGH

#### ~~H1~~ — RESOLVED: Factory verification command fails

**Resolution:** The snippet set `OPENROUTER_API_KEY` as an env var then called `create_client()` with no arguments, implicitly expecting `OpenRouterClient` to read the env directly — the anti-pattern the spec eliminates. Fixed by adding `from llm.env import resolve_from_env` and changing `create_client()` to `create_client(**resolve_from_env())`, following the pattern the spec names for all callers without a config file context.

<details>
<summary>Original finding (retained for reference)</summary>

- **Why it was wrong:**  
  `create_client()` forwards its kwargs to `OpenRouterClient`. The spec states `OpenRouterClient` has no internal env var fallbacks and env reading must go through `resolve_from_env()`. The snippet set `OPENROUTER_API_KEY` but never called `resolve_from_env()`, so `create_client()` received `api_key=None` and raised `LLMConfigError`. The assertion never ran.
- **Dimensions:** F (verification command validity), A (internal contract consistency).

</details>

#### ~~H2~~ — RESOLVED: Stale source path for `test_pipeline.py` move

**Resolution:** Verified by direct file inspection: `src/novel_pipeline/tests/test_pipeline.py` exists; `src/fiction/pipeline/tests/test_pipeline.py` does not. The `git mv` block was removed from Step 6 and replaced with a one-line confirmation that the file is already at the correct path. The vestigial `sys.path.insert` removal instruction that followed is real (block confirmed present at lines 40–41 of the actual file) and was left unchanged.

<details>
<summary>Original finding (retained for reference)</summary>

- **Why it was wrong:**  
  The file was already at `src/novel_pipeline/tests/test_pipeline.py`. Executing the `git mv` command would fail immediately, blocking the implementer from reaching the valid instructions that follow.
- **Dimensions:** C (cross-reference integrity), D (migration step ordering — the move step was obsolete).

</details>

#### ~~H3~~ — RESOLVED: Verification grep omits the podcast generator domain directory

**Resolution:** Added `src/podcast_script_generator` to the grep command in the Verification section. All other `src/` subdirectories were inspected — `src/pdfslicer` is empty, `src/phases` and `src/docs` are not Python packages, `src/util` has no LLM imports. No other domain directory was missing.

<details>
<summary>Original finding (retained for reference)</summary>

- **Why it was wrong:**  
  The grep omitted `src/podcast_script_generator`, which contains `llm/call_api.py` and `llm/main.py` — explicitly migrated files. A direct provider import left there would pass verification silently.
- **Dimensions:** F (verification command validity), H (architecture layer compliance).

</details>

#### ~~H4~~ — RESOLVED: `main.py` `llm` injection parameter is only described in the test section

**Resolution:** The production code change (`llm: LLMClient | None = None` on `main()`, `None`-guard on `create_client()`) was moved from Step 6 into Step 3's `main.py` entry where it belongs. `from llm.protocol import LLMClient` import also added to Step 3 — it was missing and required for the type annotation. Step 6's DI migration paragraph trimmed to test-side description only, pointing back to Step 3. Pattern confirmed architecture-compliant: identical to `endpoints/fiction.py`'s `client: LLMTransport | None = None` injectable wiring origin pattern.

<details>
<summary>Original finding (retained for reference)</summary>

- **Why it was wrong:**  
  A production code change (adding the injectable `llm` parameter to `main()`) was described in Step 6 (test section) rather than Step 3 (production migration table). An implementer following steps in order would complete Step 3 without the parameter, then hit Step 6's test strategy which requires it.
- **Dimensions:** E (test instruction alignment).

</details>

#### ~~H5~~ — RESOLVED: `test_pipeline.py` env-override and missing-API-key tests are not addressed

**Resolution:** Both tests are dead specs — they describe behaviors Step 4 deliberately removes. Added two explicit "Dead test" instructions at the end of Step 6's `test_pipeline.py` section:

- `test_env_overrides` (line 627): delete. Tests `load_config()` merging env vars — a contract Step 4 removes entirely.
- `test_missing_api_key_raises` (line 1005): delete from `test_pipeline.py`; add replacement coverage in `src/llm/providers/tests/test_openrouter.py` asserting `OpenRouterClient(api_key=None)` raises `LLMConfigError` — the transport-layer equivalent, placed alongside the other transport tests already planned for that file.

<details>
<summary>Original finding (retained for reference)</summary>

- **Why it was wrong:**  
  Step 4 removes two behaviors (`load_config()` merging env vars; `call_api()` checking for missing API key) but Step 6 gave no instruction to retire the tests guarding those behaviors. Both tests would fail after migration, contradicting the verification claim "Novel pipeline tests pass."
- **Dimensions:** E (test instruction alignment), F (verification command validity).

</details>

---

### MEDIUM

#### ~~M1~~ — RESOLVED: `LLMError` escapes the direct engine path

**Resolution:** Adding the catch inside `llm_script.py` was ruled out — it would reintroduce the `engines/` → `podcast_script_generator/` dependency that Step 3 deliberately removes. The boundary belongs at `endpoints/podcast.py`: the wiring layer already imports from both `llm/` and `podcast_script_generator/` and is the natural owner of the engine-path exception boundary. Three locations updated in `fix_specsv2.md`:

- **Step 3 `src/endpoints/podcast.py`:** Added **(3)** — import `LLMError` alongside `LLMConfigError`; import `ScriptGenerationError` if not already present; wrap each per-chapter `script_engine.generate(...)` call in `try/except LLMError as e: raise ScriptGenerationError(str(e)) from e`.
- **Scope Exclusions:** Updated the blanket "caught at the `call_api` boundary" sentence to name both boundaries: `call_api` for the `main.py` path, `endpoints/podcast.py` for the engine path.
- **Step 7:** Same two-boundary update to the matching sentence.

<details>
<summary>Original finding (retained for reference)</summary>

- **What the spec said:**  
  Scope Exclusions: "Transport errors are caught at the `call_api` boundary and re-raised as `ScriptGenerationError`; it never escapes into domain code."  
  Step 3 `src/engines/llm_script.py`: "In `generate()`, remove the lazy `call_api` import... call `self.llm.call(prompt)`."
- **Why it was wrong:**  
  `src/engines/llm_script.py` calls `self.llm.call()` directly with no exception boundary. A transport failure raises `LLMError`, not `ScriptGenerationError`, so transport errors escaped into the podcast execution path — the Scope Exclusions claim that they "never escape into domain code" was unenforceable without a boundary on the engine path.
- **Conflicts with:**  
  The Scope Exclusions sentence quoted above.
- **Dimensions:** B (exception flow), H (architecture layer compliance).

</details>

#### ~~M2~~ — RESOLVED: `seed_gen` LLMConfigError handling lacks an exit decision

**Resolution:** `seed_gen` has no fallback path — the LLM call is the operation, not an optional stage. Added `sys.exit(1)` after the print, matching the pattern used by every other CLI entry point in the spec for fatal startup errors (`novel_pipeline/cli.py`, `cli/fiction.py`). Also added an explicit instruction to retain `import sys`: removing `sys.path.insert` would otherwise leave it as a dead import, but `sys.exit(1)` requires it.

<details>
<summary>Original finding (retained for reference)</summary>

- **What the spec said (Step 3, `src/fiction/seed_gen/cli.py`):**  
  "Wrap `create_client(**resolve_from_env())` in `try/except LLMConfigError` and print a clean error message — without this, a missing API key produces a traceback instead of a user-readable message."
- **Why it was wrong:**  
  The spec said to print a message but did not say whether to exit or continue. If the implementer printed and continued, `call_api` would be called with `client` undefined and raise `AttributeError`, not caught by the `(ValueError, ScriptGenerationError)` handler — producing the exact traceback the spec claimed to prevent.
- **Dimensions:** B (exception flow), E (test instruction alignment).

</details>

#### M3 — `seed_gen` import path is ambiguous
- **What the spec says (Step 3, `src/fiction/seed_gen/cli.py`):**  
  "Remove `sys.path.insert`; import helpers via `podcast_script_generator.llm.*`."
- **Why it is wrong:**  
  `src/podcast_script_generator/llm/__init__.py` is empty. `from podcast_script_generator.llm import extract_pdf` will fail because `extract_pdf` is a submodule, not a package attribute. The required imports are `from podcast_script_generator.llm.extract_pdf import extract_pdf`, etc. The wildcard phrasing is likely to be misread.
- **Dimensions:** C (cross-reference integrity), E (test instruction alignment).

#### M4 — `run_splitter` default parameter not specified
- **What the spec says (Step 3, `src/slicer/pdf_splitter.py`):**  
  "Add `llm: LLMClient | None` to `get_toc_from_llm`, `extract_toc`, and `run_splitter`."
- **Why it is wrong:**  
  `run_splitter` is a public API with a docstring example (`result = run_splitter("book.pdf", toc_page=10, chapters_only=True)` at line 724) and existing direct callers. If `llm` is added as a required parameter, those callers break. Because the intended behavior is graceful degradation when no client is supplied (Stage 4 skipped), the parameter should be `llm: LLMClient | None = None`. The spec does not state this.
- **Dimensions:** G (scope completeness / backward compatibility), C (cross-reference with the docstring example).

#### ~~M5~~ — RESOLVED: `LLMError`/`ScriptGenerationError` boundary claim is overclaimed

**Resolution:** Resolved as a consequence of ~~M1~~. The Scope Exclusions and Step 7 prose updates that fix M1 also correct this overclaimed invariant — both now name both exception boundaries (the `call_api` path and the engine path) instead of asserting a universal guarantee that the spec's own instructions did not enforce.

<details>
<summary>Original finding (retained for reference)</summary>

- **What the spec said:**  
  Scope Exclusions: "Transport errors are caught at the `call_api` boundary and re-raised as `ScriptGenerationError`; it never escapes into domain code."
- **Why it was wrong:**  
  As noted in M1, the direct engine path (`src/engines/llm_script.py`) allowed `LLMError` to escape. The statement was an overclaimed guarantee that the spec's own instructions did not enforce.
- **Dimensions:** A (internal contract consistency), H (architecture layer compliance).

</details>

---

### LOW

#### L1 — CLI `sys.path` guards are not covered by the "no path hacks" verification
- **What the spec says (Verification):**  
  `# No production path hacks remain` followed by a grep for `sys.path.insert`.
- **Why it is wrong:**  
  `src/cli/fiction.py` and `src/cli/podcast.py` contain `if str(Path(__file__).parent.parent) not in sys.path: raise RuntimeError(...)` guards. These are production path checks that the verification command does not detect, so the broad claim "No production path hacks remain" is only partially verified. (The spec does not say to remove them, so this is a verification precision issue, not a migration bug.)
- **Dimensions:** F (verification command validity), H (architecture layer compliance).

#### L2 — Ordering between Step 2 and Step 3 is implicit
- **What the spec says:**  
  Step 3 table assumes `src/podcast_script_generator/llm/call_api.py` already has the new DI signature (`call_api(pdf_text, prompt_text, llm)`). Step 2 defines that signature.
- **Why it is wrong:**  
  The spec explicitly orders migration within Step 3 (factory first) but never states that Step 2 must complete before Step 3. An implementer could migrate `main.py` before `call_api.py` and hit signature errors.
- **Dimensions:** D (migration step ordering).

---

## Section 3 — Codebase Gaps

These are places where the spec is correct but the code has not yet been updated. They require implementation, not spec fixes.

- `src/llm/` package does not exist; none of `protocol.py`, `exceptions.py`, `factory.py`, `env.py`, or `providers/openrouter.py` are present.
- `src/podcast_script_generator/llm/call_api.py` still contains the old `urllib`-based implementation.
- `src/podcast_script_generator/llm/main.py` does not accept an injectable `llm` parameter and does not catch `LLMConfigError`.
- `src/engines/factory.py` does not construct clients via `create_client` / `resolve_from_env`.
- `src/engines/llm_script.py` does not accept `llm: LLMClient` in `__init__`.
- `src/engines/pdf_splitter.py` does not accept or forward `llm`.
- `src/slicer/pdf_splitter.py` still has the `sys.path.insert` block and old signatures.
- `src/fiction/seed_gen/cli.py` still has the `sys.path.insert` block and old `except (ValueError, RuntimeError)` handler.
- `src/novel_pipeline/api.py` still owns the HTTP retry loop and `_resolve_api_key`.
- `src/novel_pipeline/requests_.py` and `src/novel_pipeline/session.py` do not accept `client` / `timeout`.
- `src/novel_pipeline/cli.py` and `src/endpoints/fiction.py` do not construct the transport.
- `src/cli/fiction.py` does not catch `ConfigError`.
- `src/endpoints/podcast.py` does not handle `LLMConfigError` for splitter-engine construction.
- `src/cli/podcast.py` still imports and passes `default_splitter_engine`.
- `src/novel_pipeline/config.py` still contains the `OPENROUTER_API_KEY` / `OPENROUTER_MODEL` env override block.
- `src/novel_pipeline/exceptions.py` and `src/novel_pipeline/__init__.py` do not define/export `APIRateLimitError`.
- `src/podcast_script_generator/llm/test_all.py` still uses the 3-tuple `parse_args` unpack and monkey-patches `call_api.call_api`.
- `src/novel_pipeline/tests/test_pipeline.py` still has the `sys.path.insert` vestigial block and tests for behavior that is being moved out of `load_config` / `call_api`.

---

## Section 4 — Already-Resolved Issues

These are items the spec flags but are already addressed in the current codebase.

- **`novel_pipeline` package move:** The spec notes under "What Was Wrong With v1" that the standalone package has been moved to `src/novel_pipeline/`; the codebase already reflects this.
- **`test_pipeline.py` location:** The file is already at `src/novel_pipeline/tests/test_pipeline.py`. The spec's `git mv` instruction is obsolete.
- **`save_output` stdout behavior:** `src/podcast_script_generator/llm/save_output.py` already only logs via `logger.debug(...)` and does not print to stdout. Only its docstring still claims it prints; the code behavior is already correct.
- **`parse_args` 4-tuple return:** `src/podcast_script_generator/llm/parse_args.py` already returns `(pdf_path, prompt_path, output_dir, context)`; the test bug at `test_all.py:82` is present in the test, not the production code.
