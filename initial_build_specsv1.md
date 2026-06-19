# initial_build_specsv1.md — LLM Transport DI Migration

> Source of truth: `fix_specsv2.md` (requirements) and `code_facts_report_transport.md` (structural facts).
> All AST citations are line numbers in `code_facts_report_transport.md`.

---

## Phase 1: Create `src/llm/` Package

**REQUIRES:** `src/llm/` directory does not exist. Running `PYTHONPATH=src python -c "import llm"` raises `ModuleNotFoundError`.

**PRODUCES:** Seven new files exist under `src/llm/`. `PYTHONPATH=src python -c "from llm.protocol import LLMTransport, LLMClient; from llm.exceptions import LLMError; from llm.factory import create_client; from llm.providers.openrouter import OpenRouterClient"` exits 0.

**ROLLBACK:** `rm -rf src/llm/`

---

### Pass 1.1: Core Protocol and Exception Modules

**SCOPE:** Create `src/llm/__init__.py` (empty), `src/llm/protocol.py` (two `@runtime_checkable` Protocol classes), and `src/llm/exceptions.py` (four exception classes). No other files touched.

**RISK:** Incorrect Protocol method signatures break the `isinstance` guards in Phase 1 Pass 1.2 and every DI injection site downstream.

**DONE WHEN:**
1. `src/llm/__init__.py` exists and is empty (zero bytes or a single blank line).
2. `src/llm/protocol.py` defines `LLMTransport` and `LLMClient` both decorated with `@runtime_checkable`, each with exactly the method signatures specified in `fix_specsv2.md` § Target Architecture → `protocol.py`.
3. `src/llm/exceptions.py` defines `LLMError(Exception)`, `TransportError(LLMError)`, `RateLimitError(LLMError)`, and `LLMConfigError(LLMError)` — four classes, no more.
4. All four exception classes are importable and satisfy the expected inheritance chain.

**PROOF TESTS:**
1. **Condition:** `__init__.py` exists.
   **Verify:**
   ```bash
   test -f src/llm/__init__.py
   ```
2. **Condition:** Protocol signatures correct.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from llm.protocol import LLMTransport, LLMClient
   import inspect
   assert hasattr(LLMTransport, 'chat_completion'), 'LLMTransport missing chat_completion'
   sig = inspect.signature(LLMTransport.chat_completion)
   params = list(sig.parameters.keys())
   assert 'self' in params and 'payload' in params and 'timeout' in params, f'Wrong params: {params}'
   assert hasattr(LLMClient, 'call'), 'LLMClient missing call'
   sig2 = inspect.signature(LLMClient.call)
   params2 = list(sig2.parameters.keys())
   assert 'prompt' in params2 and 'context' in params2, f'Wrong params: {params2}'
   print('protocol ok')
   "
   ```
3. **Condition:** `@runtime_checkable` applied to both.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from llm.protocol import LLMTransport, LLMClient
   from typing import runtime_checkable, Protocol
   # runtime_checkable means isinstance() works on Protocol
   assert issubclass(LLMTransport, Protocol), 'LLMTransport not a Protocol'
   assert issubclass(LLMClient, Protocol), 'LLMClient not a Protocol'
   print('runtime_checkable ok')
   "
   ```
4. **Condition:** Exception hierarchy correct.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from llm.exceptions import LLMError, TransportError, RateLimitError, LLMConfigError
   assert issubclass(TransportError, LLMError)
   assert issubclass(RateLimitError, LLMError)
   assert issubclass(LLMConfigError, LLMError)
   assert not issubclass(TransportError, RateLimitError)
   print('exceptions ok')
   "
   ```

---

### Pass 1.2: Environment Resolver and Factory

**SCOPE:** Create `src/llm/env.py` (`resolve_from_env()`) and `src/llm/factory.py` (`_build`, `create_client`, `create_transport`). No existing files touched.

**RISK:** If `factory.py` imports `OpenRouterClient` at module scope (not inside `_build`), a missing provider file causes an `ImportError` on any `import llm.factory` call. If `env.py` does type conversion, `OpenRouterClient.__init__` cannot detect invalid values.

**DONE WHEN:**
1. `src/llm/env.py` defines `resolve_from_env() -> dict` that returns only keys whose env vars are non-empty; values are raw strings (no type conversion).
2. `src/llm/factory.py` defines `create_client(**kwargs) -> LLMClient` and `create_transport(**kwargs) -> LLMTransport` that both internally call the private `_build(**kwargs)`.
3. `factory.py` reads `LLM_PROVIDER` via `os.getenv("LLM_PROVIDER", "openrouter")` and imports `OpenRouterClient` inside `_build` only (lazy import — not at module scope).
4. Both `create_client` and `create_transport` perform `isinstance` checks against their respective Protocol and raise `LLMConfigError` on mismatch.

**PROOF TESTS:**
1. **Condition:** `resolve_from_env` returns raw strings only for present env vars.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import os
   os.environ['OPENROUTER_API_KEY'] = 'test-key'
   os.environ['OPENROUTER_MAX_TOKENS'] = '4096'
   # Deliberately do NOT set OPENROUTER_MODEL
   from llm.env import resolve_from_env
   r = resolve_from_env()
   assert r.get('api_key') == 'test-key', r
   assert r.get('max_tokens') == '4096', r  # raw string, not int
   assert 'model' not in r, r
   print('env ok')
   "
   ```
2. **Condition:** `factory.py` importable; functions defined.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "from llm.factory import create_client, create_transport; print('factory imports ok')"
   ```
3. **Condition:** `OpenRouterClient` is NOT imported at module scope in `factory.py`.
   **Verify:**
   ```bash
   ! grep -E "^from llm.providers.openrouter import|^import llm.providers.openrouter" src/llm/factory.py
   ```
4. **Condition:** `create_client` with a known provider (openrouter) and valid key succeeds; `isinstance(result, LLMClient)` is True.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import os; os.environ['OPENROUTER_API_KEY'] = 'test-key'
   from llm.factory import create_client
   from llm.protocol import LLMClient
   c = create_client(**{'api_key': 'test-key'})
   assert isinstance(c, LLMClient), type(c)
   print('create_client ok')
   "
   ```

---

### Pass 1.3: OpenRouter Provider Implementation

**SCOPE:** Create `src/llm/providers/__init__.py` (empty) and `src/llm/providers/openrouter.py` (`OpenRouterClient` class implementing both protocols). No existing files touched.

**RISK:** If retry logic copies the jitter inconsistency from `novel_pipeline/api.py` (empty-content retry uses `_backoff_seconds` instead of `_jittered_sleep`), the spec's contract — "transport uses `_jittered_sleep()` consistently" — is violated. If `OpenRouterClient` reads env vars internally, the single-source-of-truth invariant of `env.py` is broken.

**DONE WHEN:**
1. `src/llm/providers/__init__.py` exists (empty).
2. `src/llm/providers/openrouter.py` defines `OpenRouterClient` with `__init__` accepting exactly the parameters listed in `fix_specsv2.md` § Target Architecture → `providers/openrouter.py`.
3. `OpenRouterClient` implements both `LLMTransport` and `LLMClient` — `isinstance(obj, LLMTransport)` and `isinstance(obj, LLMClient)` both return `True`.
4. `OpenRouterClient.__init__` raises `LLMConfigError` (not `ValueError`) when `api_key=None`, when `max_tokens` is a non-integer string, or when `retry_after_override` is a non-float string.
5. `OpenRouterClient` contains NO `os.environ.get` or `os.environ["..."]` calls — all env var reading is externalized to `env.py`.
6. `OpenRouterClient.chat_completion` retry delay for HTTP 429 resolves in priority order: `retry_after_override` constructor arg → `Retry-After` header → `error.metadata.retry_after_seconds` body field → `backoff_seconds` schedule. Evidence: grep for the body field string.

**PROOF TESTS:**
1. **Condition:** `providers/__init__.py` exists.
   **Verify:**
   ```bash
   test -f src/llm/providers/__init__.py
   ```
2. **Condition:** `OpenRouterClient` constructor accepts all spec parameters.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from llm.providers.openrouter import OpenRouterClient
   sig = inspect.signature(OpenRouterClient.__init__)
   params = list(sig.parameters.keys())
   for expected in ['api_key','model','api_url','max_tokens','retry_after_override','max_retries','backoff_seconds','jitter_max']:
       assert expected in params, f'{expected!r} missing from __init__; got {params}'
   print('constructor params ok')
   "
   ```
3. **Condition:** Both Protocol isinstance checks pass.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from llm.providers.openrouter import OpenRouterClient
   from llm.protocol import LLMTransport, LLMClient
   c = OpenRouterClient(api_key='test-key')
   assert isinstance(c, LLMTransport), f'Not LLMTransport: {type(c)}'
   assert isinstance(c, LLMClient), f'Not LLMClient: {type(c)}'
   print('protocols ok')
   "
   ```
4. **Condition:** `LLMConfigError` raised on missing/invalid args (not `ValueError`).
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from llm.providers.openrouter import OpenRouterClient
   from llm.exceptions import LLMConfigError
   # Test 1: missing api_key
   try:
       OpenRouterClient(api_key=None)
       assert False, 'expected LLMConfigError for api_key=None'
   except LLMConfigError:
       pass
   # Test 2: invalid max_tokens string
   try:
       OpenRouterClient(api_key='k', max_tokens='abc')
       assert False, 'expected LLMConfigError for max_tokens=abc'
   except LLMConfigError:
       pass
   print('LLMConfigError raises ok')
   "
   ```
5. **Condition:** No internal env var reads.
   **Verify:**
   ```bash
   ! grep -E "os\.environ|os\.getenv" src/llm/providers/openrouter.py
   ```
6. **Condition:** Body-fallback retry-after parsing present.
   **Verify:**
   ```bash
   grep -q "retry_after_seconds" src/llm/providers/openrouter.py
   ```

---

## Phase 2: Wire Podcast Engine DI Chain

**REQUIRES:** Phase 1 complete (`PYTHONPATH=src python -c "from llm.factory import create_client"` exits 0). `src/engines/llm_script.py::LLMScriptEngine.__init__` has signature `(self, mode: str)` with no `llm` parameter — confirmed at AST report line 311. `src/engines/factory.py::default_llm_script_engine` body is `return LLMScriptEngine(mode=mode)` — confirmed at AST report line 1161. `src/slicer/pdf_splitter.py::get_toc_from_llm` has signature `(pdf_path: str)` with no `llm` parameter — confirmed at AST report line 753.

**PRODUCES:** `LLMScriptEngine.__init__` accepts `llm: LLMClient`. `PDFSplitterEngine.__init__` accepts `llm: LLMClient`. `get_toc_from_llm`, `extract_toc`, and `run_splitter` in `slicer/pdf_splitter.py` accept `llm: LLMClient | None`. `engines/factory.py` constructs a client from config + env and injects it into both engine constructors. `slicer/pdf_splitter.py` no longer contains `sys.path.insert`.

**ROLLBACK:** `git checkout -- src/engines/factory.py src/engines/llm_script.py src/engines/pdf_splitter.py src/slicer/pdf_splitter.py`

---

### Pass 2.1: Script Engine DI Wiring

**SCOPE:** Modify `src/engines/llm_script.py` (add `llm: LLMClient` to `__init__`; replace lazy `call_api` import in `generate()` with `self.llm.call()`). Simultaneously update `src/engines/factory.py::default_llm_script_engine` to construct an `LLMClient` from config+env and inject it. These two files must change atomically — updating the engine without updating the factory leaves `default_llm_script_engine()` calling `LLMScriptEngine(mode=mode)` without the required `llm` arg.

**RISK:** The `fiction_meta` special case in `generate()` must NOT apply the `---` separator (the `{TECHNICAL_CONTENT}` substitution already embeds pdf_text in the prompt). All other modes must apply `combined = f"{prompt_text}\n\n---\n\n{pdf_text}" if pdf_text else prompt_text`. Swapping these is a silent logic error.

**DONE WHEN:**
1. `LLMScriptEngine.__init__` accepts `llm: LLMClient` as a required parameter (no default value).
2. `LLMScriptEngine.generate()` calls `self.llm.call(...)` directly — no `from podcast_script_generator.llm.call_api import call_api` inside the method body.
3. For `fiction_meta` mode: `generate()` calls `self.llm.call(prompt)` where `prompt` already contains the substituted `{TECHNICAL_CONTENT}` — no pdf_text appended separately.
4. `engines/factory.py::default_llm_script_engine` imports `load_config` from `config`, `create_client` from `llm.factory`, and `resolve_from_env` from `llm.env`; it reads config keys and spreads `resolve_from_env()` last; it constructs and injects the client.

**PROOF TESTS:**
1. **Condition:** `llm` parameter in `LLMScriptEngine.__init__`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from engines.llm_script import LLMScriptEngine
   sig = inspect.signature(LLMScriptEngine.__init__)
   params = list(sig.parameters.keys())
   assert 'llm' in params, f\"'llm' not in {params}\"
   assert sig.parameters['llm'].default is inspect.Parameter.empty, 'llm should have no default'
   print('LLMScriptEngine init ok')
   "
   ```
2. **Condition:** No `call_api` import inside `generate()`.
   **Verify:**
   ```bash
   ! grep -q "from podcast_script_generator.llm.call_api import\|from call_api import" src/engines/llm_script.py
   ```
3. **Condition:** `generate()` calls `self.llm.call`.
   **Verify:**
   ```bash
   grep -q "self\.llm\.call" src/engines/llm_script.py
   ```
4. **Condition:** `default_llm_script_engine` reads config, creates client, and injects it.
   **Verify:**
   ```bash
   grep -q "create_client" src/engines/factory.py && grep -q "resolve_from_env" src/engines/factory.py && grep -q "load_config" src/engines/factory.py
   ```

---

### Pass 2.2: Splitter Engine DI Wiring

**SCOPE:** Modify `src/engines/pdf_splitter.py` (add `llm: LLMClient` to `PDFSplitterEngine.__init__`; pass `llm` through to `run_splitter`). Modify `src/slicer/pdf_splitter.py` (add `llm: LLMClient | None` parameter to `get_toc_from_llm`, `extract_toc`, and `run_splitter`; add `if llm is None: return None` guard at top of `get_toc_from_llm`; replace broad `except Exception` with `except LLMError`; remove `sys.path.insert` block at lines 214-216). Update `src/engines/factory.py::default_splitter_engine` to construct client and inject into `PDFSplitterEngine`. All three files must change atomically — updating `PDFSplitterEngine` without updating the factory leaves `default_splitter_engine()` calling `PDFSplitterEngine()` without the required `llm` arg.

**RISK:** The `sys.path.insert` block in `get_toc_from_llm` at lines 214-216 (AST report line 753 notes: "sys.path: Runtime path manipulation detected") is removed. After removal the old `from call_api import call_api` line that follows it will fail to import unless it is also removed/replaced by `llm.call()` usage. Ensure the entire legacy import block is replaced.

**DONE WHEN:**
1. `PDFSplitterEngine.__init__` accepts `llm: LLMClient` as a required parameter.
2. `slicer/pdf_splitter.py::get_toc_from_llm` signature includes `llm: LLMClient | None`; first executable line is `if llm is None: return None`.
3. `slicer/pdf_splitter.py` contains no `sys.path.insert` call.
4. `slicer/pdf_splitter.py` imports `LLMError` from `llm.exceptions` and uses `except LLMError` (not `except Exception`) in `get_toc_from_llm`.
5. `engines/factory.py::default_splitter_engine` constructs a client and injects it.

**PROOF TESTS:**
1. **Condition:** `PDFSplitterEngine.__init__` has `llm` param.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from engines.pdf_splitter import PDFSplitterEngine
   sig = inspect.signature(PDFSplitterEngine.__init__)
   assert 'llm' in sig.parameters, f\"'llm' not in {list(sig.parameters.keys())}\"
   print('PDFSplitterEngine init ok')
   "
   ```
2. **Condition:** `get_toc_from_llm` signature includes `llm` and has None guard.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from slicer.pdf_splitter import get_toc_from_llm
   sig = inspect.signature(get_toc_from_llm)
   assert 'llm' in sig.parameters, f\"'llm' not in {list(sig.parameters.keys())}\"
   print('get_toc_from_llm signature ok')
   "
   ```
   ```bash
   # Verify None guard: calling with llm=None returns None immediately without file I/O
   PYTHONPATH=src python -c "
   from slicer.pdf_splitter import get_toc_from_llm
   result = get_toc_from_llm('nonexistent_path.pdf', llm=None)
   assert result is None, f'Expected None, got {result!r}'
   print('None guard ok')
   "
   ```
3. **Condition:** `sys.path.insert` removed from `slicer/pdf_splitter.py`.
   **Verify:**
   ```bash
   ! grep -q "sys\.path\.insert" src/slicer/pdf_splitter.py
   ```
4. **Condition:** `LLMError` imported and used in except clause.
   **Verify:**
   ```bash
   grep -q "from llm.exceptions import LLMError" src/slicer/pdf_splitter.py && grep -q "except LLMError" src/slicer/pdf_splitter.py
   ```
5. **Condition:** `default_splitter_engine` injects client.
   **Verify:**
   ```bash
   grep -q "PDFSplitterEngine(llm=" src/engines/factory.py
   ```

---

## Phase 3: Migrate Podcast Domain Callers

**REQUIRES:** Phase 2 complete. `src/engines/llm_script.py::LLMScriptEngine.generate()` calls `self.llm.call()` — confirmed via `grep -q "self.llm.call" src/engines/llm_script.py`. `src/podcast_script_generator/llm/call_api.py::call_api` has signature `(pdf_text: str, prompt_text: str)` with no `llm` parameter — confirmed at AST report line 659. `src/cli/podcast.py` imports `default_llm_script_engine, default_audio_engine, default_splitter_engine` from `engines.factory` at line 77 (AST report line 70) and constructs `script_engine = default_llm_script_engine(mode=args.mode)` eagerly (AST report body line ~2056).

**PRODUCES:** `call_api.py` signature is `(pdf_text: str, prompt_text: str, llm: LLMClient) -> str`. `main.py` and `seed_gen/cli.py` construct and inject a client. `endpoints/podcast.py` wraps splitter-engine and script-engine construction in `try/except LLMConfigError`. `cli/podcast.py` passes `script_engine=None` and does not pass `splitter_engine` kwarg.

**ROLLBACK:** `git checkout -- src/podcast_script_generator/llm/call_api.py src/podcast_script_generator/llm/main.py src/podcast_script_generator/llm/save_output.py src/fiction/seed_gen/cli.py src/endpoints/podcast.py src/cli/podcast.py`

---

### Pass 3.1: Podcast `call_api` DI Migration

**SCOPE:** Replace `src/podcast_script_generator/llm/call_api.py` with the DI version (spec Step 2). Update `src/podcast_script_generator/llm/main.py` to accept `llm: LLMClient | None = None`, construct client when `None`, and pass it to `call_api`; add `print(f"Wrote {len(files)} files to {output_dir}")` after `save_output` call. Remove the "Prints `Wrote N files`" clause from `src/podcast_script_generator/llm/save_output.py` docstring. Three files, one cohesive concept: `call_api` DI migration with its callers updated atomically.

**RISK:** After this pass `src/fiction/seed_gen/cli.py` still imports `call_api` via the `sys.path.insert` hack and calls it with the old two-arg signature. This is a broken call site (would `TypeError` at runtime) but is NOT an import error — Python will parse and import without failure. Pass 3.2 repairs this.

**DONE WHEN:**
1. `call_api.py` defines `call_api(pdf_text: str, prompt_text: str, llm: LLMClient) -> str` — three parameters, no more, no less.
2. `call_api.py` imports `LLMClient` from `llm.protocol` and `LLMError` from `llm.exceptions`; it raises `ScriptGenerationError` (not `LLMError`) to the caller.
3. `main.py::main()` accepts an `llm: LLMClient | None = None` parameter; when `llm is None` it constructs a client via `create_client(**resolve_from_env())`.
4. `main.py::main()` prints `Wrote {n} files to {output_dir}` after the `save_output` call (this is the user-facing output line that `test_all.py` line 320 asserts on).
5. `save_output.py` docstring does NOT contain the phrase "Prints" referring to stdout output.

**PROOF TESTS:**
1. **Condition:** `call_api` three-parameter signature.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from podcast_script_generator.llm.call_api import call_api
   sig = inspect.signature(call_api)
   params = list(sig.parameters.keys())
   assert params == ['pdf_text', 'prompt_text', 'llm'], f'Wrong params: {params}'
   print('call_api signature ok')
   "
   ```
2. **Condition:** `call_api` imports from `llm.*` and re-raises as `ScriptGenerationError`.
   **Verify:**
   ```bash
   grep -q "from llm.protocol import LLMClient" src/podcast_script_generator/llm/call_api.py && grep -q "from llm.exceptions import LLMError" src/podcast_script_generator/llm/call_api.py && grep -q "ScriptGenerationError" src/podcast_script_generator/llm/call_api.py
   ```
3. **Condition:** `main.py::main` accepts `llm` parameter.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from podcast_script_generator.llm.main import main
   sig = inspect.signature(main)
   assert 'llm' in sig.parameters, f\"'llm' not in {list(sig.parameters.keys())}\"
   p = sig.parameters['llm']
   assert p.default is None, f'default should be None, got {p.default!r}'
   print('main llm param ok')
   "
   ```
4. **Condition:** `main.py` prints `Wrote ... files to ...` after `save_output`.
   **Verify:**
   ```bash
   grep -q "Wrote.*files.*to" src/podcast_script_generator/llm/main.py
   ```
5. **Condition:** `save_output.py` docstring no longer claims to print to stdout.
   **Verify:**
   ```bash
   ! grep -q "Prints.*Wrote\|stdout" src/podcast_script_generator/llm/save_output.py
   ```

---

### Pass 3.2: Seed Generator DI Migration

**SCOPE:** Modify `src/fiction/seed_gen/cli.py` only: remove `sys.path.insert(0, ...)` at line 7; rewrite bare-name imports (`from extract_pdf import`, etc.) to fully-qualified forms (`from podcast_script_generator.llm.extract_pdf import`); add `from llm.factory import create_client`, `from llm.env import resolve_from_env`, `from llm.exceptions import LLMConfigError`, `from podcast_script_generator.llm.exceptions import ScriptGenerationError`; in `main()` construct client via `create_client(**resolve_from_env())` wrapped in `try/except LLMConfigError: print(...); sys.exit(1)`; replace `except (ValueError, RuntimeError)` at line 286 with `except (ValueError, ScriptGenerationError)`.

**RISK:** Removing `sys.path.insert` without updating the bare-name imports causes `ModuleNotFoundError` at import time. The `import sys` statement must be retained — `sys.exit(1)` requires it after the `sys.path.insert` removal.

**DONE WHEN:**
1. `seed_gen/cli.py` does not contain `sys.path.insert`.
2. `seed_gen/cli.py` imports all four helpers with fully-qualified paths (`podcast_script_generator.llm.*`).
3. `seed_gen/cli.py` imports `ScriptGenerationError` from `podcast_script_generator.llm.exceptions` and `LLMConfigError` from `llm.exceptions`.
4. `seed_gen/cli.py::main()` creates a client via `create_client(**resolve_from_env())` and wraps it in `try/except LLMConfigError` that calls `sys.exit(1)`.
5. The `except (ValueError, RuntimeError)` handler at old line 286 is replaced by `except (ValueError, ScriptGenerationError)`.

**PROOF TESTS:**
1. **Condition:** `sys.path.insert` removed.
   **Verify:**
   ```bash
   ! grep -q "sys\.path\.insert" src/fiction/seed_gen/cli.py
   ```
2. **Condition:** Fully-qualified imports present.
   **Verify:**
   ```bash
   grep -q "from podcast_script_generator.llm.extract_pdf import" src/fiction/seed_gen/cli.py && grep -q "from podcast_script_generator.llm.call_api import" src/fiction/seed_gen/cli.py
   ```
3. **Condition:** Exception imports present.
   **Verify:**
   ```bash
   grep -q "from podcast_script_generator.llm.exceptions import ScriptGenerationError" src/fiction/seed_gen/cli.py && grep -q "from llm.exceptions import LLMConfigError" src/fiction/seed_gen/cli.py
   ```
4. **Condition:** `except (ValueError, ScriptGenerationError)` handler present; `RuntimeError` removed.
   **Verify:**
   ```bash
   grep -q "except (ValueError, ScriptGenerationError)" src/fiction/seed_gen/cli.py && ! grep -q "except.*RuntimeError" src/fiction/seed_gen/cli.py
   ```
5. **Condition:** Module importable without errors.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "import fiction.seed_gen.cli; print('seed_gen.cli importable')"
   ```

---

### Pass 3.3: Podcast Endpoint Error Boundary and CLI Lazy Construction

**SCOPE:** Modify `src/endpoints/podcast.py` and `src/cli/podcast.py`. In `endpoints/podcast.py`: add `from llm.exceptions import LLMConfigError, LLMError`; add `from podcast_script_generator.llm.exceptions import ScriptGenerationError`; in `generate_book_podcast` wrap `default_splitter_engine()` call in `try/except LLMConfigError → return [PodcastResult(error=e)]`; add early script-engine construction block after the `resolve_dir` check (if `script_engine is None` → construct → wrap in `try/except LLMConfigError → return [PodcastResult(error=e)]`); in `generate_chapter_podcast` wrap `script_engine.generate(...)` call in `try/except LLMError as e: raise ScriptGenerationError(str(e)) from e`. In `cli/podcast.py`: remove `default_splitter_engine` and `default_llm_script_engine` from the `engines.factory` import (line 77 of source, AST report line 70); remove eager `script_engine = ... default_llm_script_engine(mode=args.mode)` construction; replace with `script_engine = None`; remove `splitter_engine=default_splitter_engine()` kwarg from `generate_book_podcast` call.

**RISK:** The early script-engine construction block in `generate_book_podcast` must be placed AFTER the `if not resolve_dir or not resolve_dir.exists(): return []` check — constructing the client when there are no PDFs to process wastes a construction and fires an error even when there is nothing to do. Placement before that check is a logic error.

**DONE WHEN:**
1. `endpoints/podcast.py` imports `LLMConfigError` and `LLMError` from `llm.exceptions`.
2. `endpoints/podcast.py::generate_book_podcast` contains a `try/except LLMConfigError` block wrapping the splitter-engine construction.
3. `endpoints/podcast.py::generate_chapter_podcast` contains a `try/except LLMError` block wrapping `script_engine.generate(...)` that re-raises as `ScriptGenerationError`.
4. `cli/podcast.py` does NOT import `default_llm_script_engine` or `default_splitter_engine` from `engines.factory`.
5. `cli/podcast.py` does NOT call `default_llm_script_engine(...)` eagerly; contains `script_engine = None` instead.
6. `cli/podcast.py` does NOT pass `splitter_engine=default_splitter_engine()` to `generate_book_podcast`.

**PROOF TESTS:**
1. **Condition:** `endpoints/podcast.py` imports `LLMConfigError`.
   **Verify:**
   ```bash
   grep -q "from llm.exceptions import.*LLMConfigError" src/endpoints/podcast.py
   ```
2. **Condition:** Splitter-engine construction wrapped in `LLMConfigError` guard.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import ast, pathlib
   src = pathlib.Path('src/endpoints/podcast.py').read_text()
   # Check both except clauses exist
   assert 'LLMConfigError' in src, 'LLMConfigError not found in endpoints/podcast.py'
   assert 'PodcastResult(error=e)' in src, 'PodcastResult(error=e) not found'
   print('error boundary ok')
   "
   ```
3. **Condition:** `generate_chapter_podcast` wraps `script_engine.generate` in LLMError catch.
   **Verify:**
   ```bash
   grep -q "except LLMError" src/endpoints/podcast.py && grep -q "raise ScriptGenerationError" src/endpoints/podcast.py
   ```
4. **Condition:** `cli/podcast.py` no longer imports or calls the two removed factory functions.
   **Verify:**
   ```bash
   ! grep -q "default_llm_script_engine\|default_splitter_engine" src/cli/podcast.py
   ```
5. **Condition:** `cli/podcast.py` has `script_engine = None` (lazy construction handed to endpoint).
   **Verify:**
   ```bash
   grep -q "script_engine = None" src/cli/podcast.py
   ```

---

## Phase 4: Migrate Novel Pipeline DI

**REQUIRES:** Phase 1 complete. `src/novel_pipeline/exceptions.py` does NOT contain `APIRateLimitError` (verified: `! grep -q "APIRateLimitError" src/novel_pipeline/exceptions.py`). `src/novel_pipeline/api.py` defines `_resolve_api_key`, `_parse_retry_after`, `_backoff_seconds`, `_jittered_sleep` — confirmed at AST report lines 347, 389, 397, 405. `src/novel_pipeline/session.py::run_session` signature is `(config: dict, auto_approve: bool, dry_run: bool, resume: bool, chapter_start: int | None, ignore_cost_limit: bool, approve_chapter: ApproveChapterFn)` with no `client` or `timeout` parameter — confirmed at AST report line 590. `src/endpoints/fiction.py::run_novel_session` has no `client` parameter — confirmed at AST report line 1969.

**PRODUCES:** `APIRateLimitError(APIResponseError)` defined and exported. `api.py::call_api` accepts `client: LLMTransport` and `timeout: float | None` and delegates HTTP to `client.chat_completion`. `requests_.py` passes `client` and `timeout` through. `session.py` threads `client` and `timeout` through all four affected functions. `novel_pipeline/cli.py` and `endpoints/fiction.py` are wiring origins that construct transport and supply it. `cli/fiction.py` catches `ConfigError` before `except Exception`. `config.py::load_config` reads only TOML — no env overrides.

**ROLLBACK:** `git checkout -- src/novel_pipeline/exceptions.py src/novel_pipeline/__init__.py src/novel_pipeline/api.py src/novel_pipeline/requests_.py src/novel_pipeline/session.py src/novel_pipeline/cli.py src/endpoints/fiction.py src/cli/fiction.py src/novel_pipeline/config.py`

---

### Pass 4.1: Add `APIRateLimitError` to Exception Hierarchy

**SCOPE:** Modify `src/novel_pipeline/exceptions.py` (add `APIRateLimitError(APIResponseError)`) and `src/novel_pipeline/__init__.py` (add `APIRateLimitError` to both the `from .exceptions import` block and the `__all__` list). No other files touched. This pass is a prerequisite for Pass 4.2 where `api.py` imports and raises `APIRateLimitError`.

**RISK:** If `APIRateLimitError` inherits from `PipelineError` directly instead of `APIResponseError`, existing `except APIResponseError` catch sites in `session.py` will NOT catch rate-limit exhaustion automatically, breaking the documented catch-site invariant.

**DONE WHEN:**
1. `exceptions.py` defines `APIRateLimitError` that inherits from `APIResponseError` (not `PipelineError` directly).
2. `__init__.py` imports `APIRateLimitError` from `.exceptions` and includes it in `__all__`.
3. `issubclass(APIRateLimitError, APIResponseError)` is True; `issubclass(APIRateLimitError, PipelineError)` is also True (by transitivity).

**PROOF TESTS:**
1. **Condition:** `APIRateLimitError` defined with correct base.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from novel_pipeline.exceptions import APIRateLimitError, APIResponseError, PipelineError
   assert issubclass(APIRateLimitError, APIResponseError), 'Must inherit from APIResponseError'
   assert issubclass(APIRateLimitError, PipelineError), 'Must transitively inherit from PipelineError'
   print('APIRateLimitError hierarchy ok')
   "
   ```
2. **Condition:** Re-exported from `__init__.py`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   from novel_pipeline import APIRateLimitError
   print('APIRateLimitError exported ok')
   "
   ```
3. **Condition:** Exists in `__all__`.
   **Verify:**
   ```bash
   grep -q "APIRateLimitError" src/novel_pipeline/__init__.py
   ```

---

### Pass 4.2: API and Requests Layer DI Migration

**SCOPE:** Modify `src/novel_pipeline/api.py` and `src/novel_pipeline/requests_.py`. In `api.py`: add `client: LLMTransport` and `timeout: float | None` to `call_api`; replace the HTTP request loop with `raw = client.chat_completion(payload, timeout=timeout)`; remove `_resolve_api_key`, `_parse_retry_after`, `_backoff_seconds`, `_jittered_sleep` functions and the `requests` import; translate transport exceptions: `RateLimitError → APIRateLimitError`, `TransportError → APIResponseError`. In `requests_.py`: add `client: LLMTransport` and `timeout: float | None` to `request_chapter` and `request_living_doc_update`; forward both to `api.call_api`.

> **Note:** After this pass, `session.py` still calls `requests_.request_chapter(...)` without `client` or `timeout`. This is a broken call path (would `TypeError` at runtime) but NOT an import error — `session.py` imports successfully. Pass 4.3 repairs it.

**RISK:** `api.py` must keep token/cost/overflow/finish_reason logic (owned by domain, not transport). Removing `track_spend`, `_enforce_cost_limits`, or `finish_reason` checks is a scope violation. The `OPENROUTER_URL` env var read inside the old `call_api` must NOT be replaced by a new env var read — URL resolution moves to the wiring origins via `resolve_from_env()`.

**DONE WHEN:**
1. `api.py::call_api` signature includes `client: LLMTransport` and `timeout: float | None` parameters.
2. `api.py` does NOT define `_resolve_api_key`, `_parse_retry_after`, `_backoff_seconds`, or `_jittered_sleep`.
3. `api.py` does NOT import `requests` at the top level.
4. `api.py` imports `RateLimitError` and `TransportError` from `llm.exceptions`; imports `APIRateLimitError` and `APIResponseError` from `.exceptions`.
5. `requests_.py::request_chapter` signature includes `client: LLMTransport` and `timeout: float | None`.
6. `requests_.py::request_living_doc_update` signature includes `client: LLMTransport` and `timeout: float | None`.

**PROOF TESTS:**
1. **Condition:** `call_api` signature has `client` and `timeout`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from novel_pipeline.api import call_api
   sig = inspect.signature(call_api)
   params = list(sig.parameters.keys())
   assert 'client' in params, f\"'client' not in {params}\"
   assert 'timeout' in params, f\"'timeout' not in {params}\"
   print('call_api DI signature ok')
   "
   ```
2. **Condition:** Removed transport functions gone.
   **Verify:**
   ```bash
   ! grep -q "def _resolve_api_key\|def _parse_retry_after\|def _backoff_seconds\|def _jittered_sleep" src/novel_pipeline/api.py
   ```
3. **Condition:** `requests` not imported.
   **Verify:**
   ```bash
   ! grep -q "^import requests\|^from requests" src/novel_pipeline/api.py
   ```
4. **Condition:** Transport exception imports present.
   **Verify:**
   ```bash
   grep -q "from llm.exceptions import" src/novel_pipeline/api.py && grep -q "RateLimitError" src/novel_pipeline/api.py && grep -q "TransportError" src/novel_pipeline/api.py
   ```
5. **Condition:** `request_chapter` signature has `client` and `timeout`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from novel_pipeline.requests_ import request_chapter, request_living_doc_update
   for fn in (request_chapter, request_living_doc_update):
       sig = inspect.signature(fn)
       params = list(sig.parameters.keys())
       assert 'client' in params, f\"'client' missing from {fn.__name__}: {params}\"
       assert 'timeout' in params, f\"'timeout' missing from {fn.__name__}: {params}\"
   print('requests_ DI signatures ok')
   "
   ```

---

### Pass 4.3: Thread DI Through Session and Wire Entry Points

**SCOPE:** Modify `src/novel_pipeline/session.py`, `src/novel_pipeline/cli.py`, and `src/endpoints/fiction.py`. In `session.py`: add `client: LLMTransport` and `timeout: float | None` to `run_session`, `_run_one_chapter`, `_generate_chapter_text`, and `_resolve_starting_chapter`; thread both through all call chains (all four functions travel together — `_resolve_starting_chapter` calls `request_living_doc_update` on the resume path, so omitting `client` or `timeout` from that function causes `TypeError`). In `novel_pipeline/cli.py`: construct transport via `create_transport(**{...cfg_kwargs..., **resolve_from_env()})` wrapping `LLMConfigError` → exit 2; read `cfg.get("timeout_seconds")` → pass as `timeout` to `run_session`. In `endpoints/fiction.py`: add `client: LLMTransport | None = None` parameter; when `None`, load TOML config and construct transport with the same pattern; when provided, use it directly; read `cfg.get("timeout_seconds")` and pass as `timeout`. These three files must change atomically — updating `session.py` without updating the entry points leaves `run_session` with required `client` that no caller provides.

**RISK:** `novel_pipeline/cli.py` must catch `LLMConfigError` and map it to exit code 2, consistent with the existing `except ConfigError: return 2` pattern (see body at AST report line 1934). Pipeline-level parameters (`max_retries`, `backoff_seconds`, `jitter_max`) have no env vars and must be read directly from TOML config dict, not from `resolve_from_env()`.

**DONE WHEN:**
1. `session.py::run_session` signature includes `client: LLMTransport` and `timeout: float | None` as required parameters.
2. `session.py::_resolve_starting_chapter` signature includes `client: LLMTransport` and `timeout: float | None`.
3. `novel_pipeline/cli.py::main` calls `create_transport(...)` and passes `client=client, timeout=timeout` to `run_session`.
4. `novel_pipeline/cli.py::main` imports `LLMConfigError` from `llm.exceptions` and handles it with `return 2`.
5. `endpoints/fiction.py::run_novel_session` signature includes `client: LLMTransport | None = None`.
6. `endpoints/fiction.py` imports `LLMTransport` from `llm.protocol` and `resolve_from_env` from `llm.env`.

**PROOF TESTS:**
1. **Condition:** `run_session` has `client` and `timeout` params.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from novel_pipeline.session import run_session
   sig = inspect.signature(run_session)
   params = list(sig.parameters.keys())
   assert 'client' in params, f\"'client' not in {params}\"
   assert 'timeout' in params, f\"'timeout' not in {params}\"
   assert sig.parameters['client'].default is inspect.Parameter.empty, 'client must be required'
   print('run_session signature ok')
   "
   ```
2. **Condition:** `_resolve_starting_chapter` has `client` and `timeout`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from novel_pipeline.session import _resolve_starting_chapter
   sig = inspect.signature(_resolve_starting_chapter)
   params = list(sig.parameters.keys())
   assert 'client' in params and 'timeout' in params, f'Missing DI params: {params}'
   print('_resolve_starting_chapter signature ok')
   "
   ```
3. **Condition:** `novel_pipeline/cli.py` calls `create_transport` and handles `LLMConfigError`.
   **Verify:**
   ```bash
   grep -q "create_transport" src/novel_pipeline/cli.py && grep -q "LLMConfigError" src/novel_pipeline/cli.py
   ```
4. **Condition:** `run_novel_session` has `client: LLMTransport | None = None`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   import inspect
   from endpoints.fiction import run_novel_session
   sig = inspect.signature(run_novel_session)
   assert 'client' in sig.parameters, f\"'client' not in {list(sig.parameters.keys())}\"
   assert sig.parameters['client'].default is None, 'client default must be None'
   print('run_novel_session signature ok')
   "
   ```
5. **Condition:** `endpoints/fiction.py` imports transport protocol and env resolver.
   **Verify:**
   ```bash
   grep -q "from llm.protocol import.*LLMTransport" src/endpoints/fiction.py && grep -q "from llm.env import resolve_from_env" src/endpoints/fiction.py
   ```

---

### Pass 4.4: CLI Exit Code Boundary and Config Cleanup

**SCOPE:** Modify `src/cli/fiction.py` (add `except ConfigError` before `except Exception`, import `ConfigError` from `novel_pipeline.exceptions`) and `src/novel_pipeline/config.py` (remove the env override block that sets `cfg["api_key"]` from `OPENROUTER_API_KEY` and `cfg["model"]` from `OPENROUTER_MODEL` — lines 1338-1341 in AST report body section). The `config.py` change is safe only after Pass 4.3 has made the wiring origins responsible for env var resolution via `resolve_from_env()`.

**RISK:** The `except ConfigError` in `cli/fiction.py` must be placed BEFORE the broad `except Exception` — Python catches exceptions in order. If placed after, it is dead code. The `config.py` change must not remove the `api_key` key from the list of `known` keys at the bottom of `load_config` (the key is still valid; only the env-override assignment is removed).

**DONE WHEN:**
1. `cli/fiction.py` imports `ConfigError` from `novel_pipeline.exceptions`.
2. `cli/fiction.py` has `except ConfigError` handler that returns exit code 2; this clause appears before `except Exception` in the source text.
3. `config.py::load_config` does NOT contain `os.environ.get("OPENROUTER_API_KEY")` or `os.environ.get("OPENROUTER_MODEL")`.
4. `config.py` still imports `os` (used elsewhere for env var checks like `OPENROUTER_API_KEY` validation — **VERIFY VIA AST**: confirm `os` is still used for something other than the removed override lines before removing the import).

**PROOF TESTS:**
1. **Condition:** `ConfigError` imported in `cli/fiction.py`.
   **Verify:**
   ```bash
   grep -q "from novel_pipeline.exceptions import.*ConfigError\|from novel_pipeline import.*ConfigError" src/cli/fiction.py
   ```
2. **Condition:** `except ConfigError` present and precedes `except Exception`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   src = open('src/cli/fiction.py').read()
   config_pos = src.find('except ConfigError')
   exception_pos = src.find('except Exception')
   assert config_pos != -1, 'except ConfigError not found in cli/fiction.py'
   assert config_pos < exception_pos, f'except ConfigError ({config_pos}) must come before except Exception ({exception_pos})'
   print('except order ok')
   "
   ```
3. **Condition:** Env override block removed from `config.py`.
   **Verify:**
   ```bash
   ! grep -q "OPENROUTER_API_KEY\|OPENROUTER_MODEL" src/novel_pipeline/config.py
   ```
4. **Condition:** `load_config` still importable after change (no broken reference).
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "from novel_pipeline.config import load_config; print('load_config importable')"
   ```

---

## Phase 5: Update Tests

**REQUIRES:** Phase 4 complete. `src/novel_pipeline/session.py::run_session` requires `client: LLMTransport` and `timeout: float | None`. `src/novel_pipeline/api.py::call_api` requires `client: LLMTransport`. `src/novel_pipeline/tests/test_pipeline.py` still patches `novel_pipeline.api.requests` (old transport approach). `WORLD_BIBLE` appears at lines 360, 385, 416 in `test_pipeline.py`. `sys.path.insert` block exists at line 41 of `test_pipeline.py`. `src/podcast_script_generator/llm/test_all.py` unpacks `parse_args()` into 3 values (line 82) and monkey-patches `call_api.call_api` (around line 309).

**PRODUCES:** `test_pipeline.py` pre-existing failures fixed; `TestCallAPI`, `TestRequestWrappers`, and session-level tests rewritten around `FakeLLMTransport`; dead tests deleted; `sys.path.insert` block removed. `src/llm/providers/tests/test_openrouter.py` contains transport-layer tests. `test_all.py` uses `main(llm=fake)` DI pattern; `parse_args` arity fixed.

**ROLLBACK:** `git checkout -- src/novel_pipeline/tests/test_pipeline.py src/podcast_script_generator/llm/test_all.py` and `rm -rf src/llm/providers/tests/`

---

### Pass 5.1: Fix Pre-Existing Test Failures in `test_pipeline.py`

**SCOPE:** Modify `src/novel_pipeline/tests/test_pipeline.py` only. Three targeted fixes that are independent of the transport migration and fail TODAY before any DI changes: (1) replace every occurrence of `"=== WORLD_BIBLE ==="` with `"=== WORLD_LAWS ==="` — three occurrences at lines 360, 385, 416; (2) in `TestM4RejectionLimitBounded::test_runaway_rejections_eventually_raise` (line 1290), add `approve_chapter=lambda n, t: False` to the `run_session` call so the chapter-approval path never consumes the `builtins.input` mock.

> **Note:** Pass 5.1 fixes pre-existing failures that are NOT caused by the transport migration. Do NOT rewrite `TestCallAPI` or session tests here — that is Pass 5.2's responsibility. After Pass 5.1, these two specific tests pass; the rest of `TestCallAPI` still patches `requests` and fails.

**DONE WHEN:**
1. The string `"=== WORLD_BIBLE ==="` does NOT appear anywhere in `test_pipeline.py`.
2. The string `"=== WORLD_LAWS ==="` appears in `test_pipeline.py` at the three assertion sites that previously used `WORLD_BIBLE`.
3. `test_runaway_rejections_eventually_raise` passes `approve_chapter=lambda n, t: False` to `run_session`.

**PROOF TESTS:**
1. **Condition:** `WORLD_BIBLE` removed.
   **Verify:**
   ```bash
   ! grep -q "WORLD_BIBLE" src/novel_pipeline/tests/test_pipeline.py
   ```
2. **Condition:** `WORLD_LAWS` present (at least 3 occurrences replacing the old string).
   **Verify:**
   ```bash
   count=$(grep -c "WORLD_LAWS" src/novel_pipeline/tests/test_pipeline.py); test "$count" -ge 3
   ```
3. **Condition:** `approve_chapter` lambda added in `test_runaway_rejections_eventually_raise`.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "
   src = open('src/novel_pipeline/tests/test_pipeline.py').read()
   # Find the test method and check approve_chapter lambda appears near run_session call
   idx = src.find('test_runaway_rejections_eventually_raise')
   assert idx != -1, 'test not found'
   snippet = src[idx:idx+800]
   assert 'approve_chapter=lambda' in snippet, f'approve_chapter lambda missing in snippet: {snippet[:400]}'
   print('approve_chapter lambda ok')
   "
   ```

---

### Pass 5.2: Migrate `test_pipeline.py` to `FakeLLMTransport` DI

**SCOPE:** Modify `src/novel_pipeline/tests/test_pipeline.py` only. Four changes in one file: (a) remove the `sys.path.insert` block at line 41 (insert into `tests/` dir, not importable modules — leftover from standalone-package era); remove `import sys` if no longer used elsewhere in the file; (b) delete `test_env_overrides` method (line 627) — tests a removed contract; (c) delete `test_missing_api_key_raises` method (line 1005) — tests the old `call_api` signature; (d) rewrite `TestCallAPI` around a `FakeLLMTransport` passed directly to `api.call_api` (drop `novel_pipeline.api.requests` patch); fix `TestRequestWrappers` to pass `FakeLLMTransport` and `timeout=None` directly; fix `_session_setup` (and all session-level tests: `TestH2KeepOldStopsSession`, `TestM4RejectionLimitBounded`, `TestC2FirstRunGuard`, `TestC3AutoApproveResumeRefuses`, `TestC4AutoApproveSkipGap`) to create `FakeLLMTransport` and pass `client=fake_transport, timeout=None` to every `run_session` call.

**RISK:** `FakeLLMTransport` must implement `LLMTransport` protocol (define `chat_completion(self, payload, *, timeout=None) -> dict` returning a valid provider dict with non-empty `choices[0]["message"]["content"]`). A `FakeLLMTransport` that returns a dict missing `choices` will cause `api.call_api` to raise `TransportError` instead of returning text, breaking happy-path tests. A `FakeLLMTransport` that raises `TransportError` must be a separate variant used only in failure-path tests.

**DONE WHEN:**
1. `test_pipeline.py` does NOT contain the `sys.path.insert(0, str(Path(__file__).resolve().parent))` block.
2. `test_pipeline.py` does NOT contain the method `test_env_overrides`.
3. `test_pipeline.py` does NOT contain the method `test_missing_api_key_raises`.
4. `test_pipeline.py` defines a `FakeLLMTransport` class (or equivalent) that implements `chat_completion` and does NOT patch `novel_pipeline.api.requests` anywhere in `TestCallAPI`.
5. All `run_session` calls in the test file pass `client=` and `timeout=` keyword arguments.
6. All `request_chapter` and `request_living_doc_update` calls in `TestRequestWrappers` pass a `client=` argument.

**PROOF TESTS:**
1. **Condition:** `sys.path.insert` block removed.
   **Verify:**
   ```bash
   ! grep -q "sys.path.insert(0, str(Path(__file__)" src/novel_pipeline/tests/test_pipeline.py
   ```
2. **Condition:** Dead tests deleted.
   **Verify:**
   ```bash
   ! grep -q "def test_env_overrides\|def test_missing_api_key_raises" src/novel_pipeline/tests/test_pipeline.py
   ```
3. **Condition:** `FakeLLMTransport` (or equivalent fake) defined.
   **Verify:**
   ```bash
   grep -q "FakeLLMTransport\|class Fake.*Transport\|def chat_completion" src/novel_pipeline/tests/test_pipeline.py
   ```
4. **Condition:** No `requests` patch in `TestCallAPI`.
   **Verify:**
   ```bash
   ! grep -q "novel_pipeline.api.requests\|patch.*requests" src/novel_pipeline/tests/test_pipeline.py
   ```
5. **Condition:** `run_session` calls in test file include `client=` kwarg.
   **Verify:**
   ```bash
   # All run_session calls must pass client= — check that at least one appears
   grep -q "run_session.*client=" src/novel_pipeline/tests/test_pipeline.py
   ```
6. **Condition:** Test suite importable with PYTHONPATH=src.
   **Verify:**
   ```bash
   PYTHONPATH=src python -c "import novel_pipeline.tests.test_pipeline; print('test_pipeline importable')" 2>&1 | grep -v "^$"
   ```

---

### Pass 5.3: Create Transport-Layer Test File

**SCOPE:** Create `src/llm/providers/tests/` directory, create `src/llm/providers/tests/test_openrouter.py` containing transport-layer tests moved/adapted from `test_pipeline.py` (429 backoff, network error, `Retry-After` header, `error.metadata.retry_after_seconds` body fallback, 4xx fail-fast, malformed response raises `TransportError`) plus coverage of `OpenRouterClient(api_key=None)` raising `LLMConfigError` (migrated from deleted `test_missing_api_key_raises`). Do NOT create `src/llm/providers/tests/__init__.py` — follow the no-`__init__` convention used by `src/novel_pipeline/tests/`.

**RISK:** Tests that assert `time.sleep` is called with the correct delay value require patching the `sleep` call inside `openrouter.py`. The patch target must be `llm.providers.openrouter.time.sleep` (not `time.sleep`), otherwise the patch does not intercept the call.

**DONE WHEN:**
1. `src/llm/providers/tests/test_openrouter.py` exists.
2. The test file asserts `OpenRouterClient(api_key=None)` raises `LLMConfigError`.
3. The test file contains at least one test for 429 retry behaviour (asserts `time.sleep` is called).
4. The test file contains at least one test for 4xx non-429 fail-fast (`TransportError` raised immediately, `time.sleep` NOT called).
5. The test file is collectible by pytest with `PYTHONPATH=src`.

**PROOF TESTS:**
1. **Condition:** Test file exists.
   **Verify:**
   ```bash
   test -f src/llm/providers/tests/test_openrouter.py
   ```
2. **Condition:** No `__init__.py` in tests dir (follows project convention).
   **Verify:**
   ```bash
   ! test -f src/llm/providers/tests/__init__.py
   ```
3. **Condition:** `LLMConfigError` for missing api_key tested.
   **Verify:**
   ```bash
   grep -q "api_key.*None\|LLMConfigError" src/llm/providers/tests/test_openrouter.py
   ```
4. **Condition:** 429 retry test present.
   **Verify:**
   ```bash
   grep -q "429\|retry\|time.sleep" src/llm/providers/tests/test_openrouter.py
   ```
5. **Condition:** pytest can collect the file.
   **Verify:**
   ```bash
   PYTHONPATH=src python -m pytest src/llm/providers/tests/test_openrouter.py --collect-only -q 2>&1 | grep -v "^$" | tail -5
   ```

---

### Pass 5.4: Fix `test_all.py` DI Migration

**SCOPE:** Modify `src/podcast_script_generator/llm/test_all.py` only. Two changes: (1) fix `parse_args` arity bug at line 82: change `a, b, c = parse_args()` to `a, b, c, ctx = parse_args()` — `parse_args()` now returns 4 values but the test unpacks 3, crashing the entire test run; (2) replace the monkey-patch approach (line 309: `call_api.call_api = lambda ...`) with a `FakeLLMClient` passed via `main(llm=fake)` — `main()` now accepts `llm: LLMClient | None = None` (added in Pass 3.1).

**RISK:** The `FakeLLMClient` must implement `call(self, prompt: str, *, context: str = "") -> str` (the `LLMClient` protocol method). It must return a string in the exact format that `parse_output.py` expects (with `### FILE:` delimiters) to exercise the full pipeline including `save_output`. If the fake returns a plain string not matching the expected format, `parse_output` raises `ValueError` and the test fails.

**DONE WHEN:**
1. `test_all.py` unpacks `parse_args()` into 4 values (line ~82 region: `a, b, c, ctx = parse_args()`).
2. `test_all.py` does NOT contain `call_api.call_api = lambda` monkey-patch.
3. The e2e pipeline test passes `main(llm=fake_client)` where `fake_client` is a `FakeLLMClient` that returns a response string matching `parse_output`'s expected format.
4. `test_all.py` is runnable with `PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py` (exits 0).

**PROOF TESTS:**
1. **Condition:** `parse_args` unpacked to 4 values.
   **Verify:**
   ```bash
   grep -q "a, b, c, ctx = parse_args()\|_, _, _, _ = parse_args()" src/podcast_script_generator/llm/test_all.py
   ```
2. **Condition:** Monkey-patch removed.
   **Verify:**
   ```bash
   ! grep -q "call_api.call_api = lambda\|call_api\.call_api\s*=" src/podcast_script_generator/llm/test_all.py
   ```
3. **Condition:** `main(llm=...)` call present.
   **Verify:**
   ```bash
   grep -q "main(llm=" src/podcast_script_generator/llm/test_all.py
   ```
4. **Condition:** `test_all.py` exits 0.
   **Verify:**
   ```bash
   PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py
   ```

---

## Final Verification Checklist

Run all of the following after Phase 5 completes. All must exit 0.

```bash
# 1. No production sys.path.insert hacks remain
grep -r "sys.path.insert" src/ | grep -v test | grep -v "__pycache__" | grep -v "ai_context.md" | grep -v "initial_readme" && echo "FAIL: sys.path.insert found in production code" || echo "PASS: no sys.path.insert in production"

# 2. No domain module imports OpenRouterClient directly
grep -r "from llm\.providers\|import OpenRouterClient" \
  src/slicer src/fiction src/engines src/tts src/novel_pipeline \
  src/cli src/endpoints src/podcast_script_generator && echo "FAIL: direct provider import" || echo "PASS: no direct provider imports"

# 3. Factory instantiates correctly
PYTHONPATH=src python -c "
import os; os.environ['OPENROUTER_API_KEY'] = 'test-key'
from llm.env import resolve_from_env
from llm.factory import create_client
from llm.protocol import LLMClient
c = create_client(**resolve_from_env())
assert isinstance(c, LLMClient), type(c)
print('factory ok')
"

# 4. Import smoke tests
PYTHONPATH=src python -c "
from engines.llm_script import LLMScriptEngine
from slicer.pdf_splitter import get_toc_from_llm
from novel_pipeline.session import run_session
from endpoints.fiction import run_novel_session
from cli.fiction import main
print('all imports ok')
"

# 5. env.py resolves correctly (raw strings only)
PYTHONPATH=src python -c "
import os; os.environ['OPENROUTER_API_KEY'] = 'test-key'; os.environ['OPENROUTER_MAX_TOKENS'] = '4096'
from llm.env import resolve_from_env
r = resolve_from_env()
assert r['api_key'] == 'test-key', r
assert r['max_tokens'] == '4096', r   # raw string, not int
assert 'model' not in r
print('env.py ok')
"

# 6. Novel pipeline test suite
PYTHONPATH=src python -m pytest src/novel_pipeline/tests/test_pipeline.py -v

# 7. Transport layer tests
PYTHONPATH=src python -m pytest src/llm/providers/tests/test_openrouter.py -v

# 8. Podcast generator tests
PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py
```

---

## AST Gaps and Ambiguities

**AST GAP — `src/config.py` key names:** The podcast-domain `src/config.py::load_config()` return dict key names are not analyzed in `code_facts_report_transport.md`. The spec for `engines/factory.py` uses `cfg.get("api_key")`, `cfg.get("model")`, `cfg.get("api_url")`, `cfg.get("max_tokens")`, `cfg.get("retry_after_seconds")`. **Builder must verify** these exact key names exist in the dict returned by `from config import load_config` before writing `engines/factory.py`. If key names differ, adjust the `cfg.get("...")` calls accordingly. The `endpoints/podcast.py` file (AST report line 86) already imports `from config import load_config` at line 92 — examine that usage to confirm the key names.

**AST GAP — `src/novel_pipeline/cli.py` `resolve_from_env` import:** The current `novel_pipeline/cli.py` import block (AST report lines 124-133) does not include `llm.env` or `llm.factory`. Pass 4.3 adds these. **Builder must verify** there is no circular import when `novel_pipeline/cli.py` imports from `llm.*` — both are under `src/` with `PYTHONPATH=src`, so there should be none.

**AMBIGUITY — `test_pipeline.py` session-level `_session_setup`:** The spec says "`_session_setup` must be extended to create a `FakeLLMTransport` and pass both `client` and `timeout=None` to every `run_session` call." The report lists session-level test classes (`TestH2KeepOldStopsSession` at line 1253, `TestM4RejectionLimitBounded` at line 1289, etc.) but does NOT show a shared `_session_setup` fixture. **Builder must verify** whether `_session_setup` is a pytest fixture, a shared helper function, or embedded per-class setup, then apply the DI extension accordingly. If no shared setup exists, add `client` and `timeout=None` to every individual `run_session` call site.

**AMBIGUITY — `src/fiction/seed_gen/cli.py` bare-name imports:** After removing `sys.path.insert`, imports like `from call_api import call_api` become `from podcast_script_generator.llm.call_api import call_api`. The spec states "import helpers via `podcast_script_generator.llm.*`". **Done Condition:** All four bare-name imports (`extract_pdf`, `call_api`, `parse_output`, `save_output`) are replaced with fully-qualified forms. If any additional bare-name imports exist in `seed_gen/cli.py` beyond the four listed, apply the same fully-qualified substitution.

**RESOLVED AMBIGUITY — `save_output` stdout:** The spec states `save_output` must NOT print, and `main()` must add the print. This was split: Pass 3.1 removes the docstring "Prints" clause from `save_output.py` AND adds the `print(...)` to `main.py`. Done Conditions for both are specified in Pass 3.1.
