# Fix Spec v2: Unified LLM Transport Layer with Dependency Injection

## Goal

All **LLM HTTP transport** code lives in one place (`src/llm/`). Domain modules never import a concrete LLM client directly — they receive an abstraction as a parameter. Swapping providers means changing one factory file and one environment variable.

Domain-specific orchestration (token counting, cost gating, spend tracking, response validation) stays in the domain modules that own those concerns.

---

## What Was Wrong With v1

The original `fix_specs.md` correctly identified the problems but proposed an unimplementable merge:

1. **Protocol mismatch.** A single `LLMClient.call(prompt: str, context: str = "") -> str` cannot serve the novel pipeline, which needs messages, model, config, expected output tokens, cost-limit override, and task labels.
2. **Transport vs. domain confusion.** Token counting, cost gates, spend tracking, and truncation detection are **novel-pipeline domain concerns**, not generic LLM-client behavior. Moving them into `src/llm/` mixes domains.
3. **Package boundary violation.** `novel-pipeline` was a standalone installable package (`src/fiction/pipeline/pyproject.toml`). Moving its HTTP logic into an external `llm` package broke standalone installation and its test suite. **Resolved:** `novel_pipeline` has been converted to a regular module under `src/` — `pyproject.toml` deleted, package moved to `src/novel_pipeline/`. It now imports from `src/llm/` like any other module.
4. **Underspecified test migration.** `test_pipeline.py` patches `requests` and tests payload/cost/overflow/finish_reason logic. A literal merge requires restructuring around a new method, not a simple patch-target change.
5. **Missing call sites.** The v1 spec omitted `src/podcast_script_generator/llm/main.py`, `src/engines/llm_script.py`, `src/engines/factory.py`, `src/cli/podcast.py`, `src/cli/fiction.py`, and `src/endpoints/fiction.py`.
6. **Exception hierarchy collision.** `PodcastError`/`TTSSubmissionError` and `PipelineError`/`CostLimitError` are independent domain hierarchies and should not be forced into one file.

---

## Target Architecture

```
src/llm/
├── __init__.py
├── protocol.py            # LLMTransport + LLMClient protocols
├── factory.py             # create_client() / create_transport()
├── exceptions.py          # Transport-level exceptions only
├── env.py                 # resolve_from_env() — centralised env var names
└── providers/
    ├── __init__.py
    └── openrouter.py      # OpenRouter HTTP transport
```

`novel_pipeline` is a regular module under `src/` and imports `LLMTransport` directly from `llm.protocol`. No local protocol needed.

### `protocol.py`

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class LLMTransport(Protocol):
    """Raw transport. Caller builds the payload; transport executes HTTP.

    On success: returns the raw provider JSON response dict. The dict is
    unchanged — no transformation, no key renaming. Callers read
    finish_reason, usage, choices, etc. directly from the provider shape.
    Guaranteed: choices[0]["message"]["content"] is non-empty after
    strip() — the transport uses strip() to check for empty content and
    retries if the stripped result is empty; the returned dict is
    otherwise unchanged and the raw provider value is not modified.

    On failure: always raises LLMError (TransportError or RateLimitError).
    No raw exception of any kind escapes to the caller — network failures,
    HTTP status errors, JSON decode errors, and any exception raised while
    accessing the response dict (KeyError, IndexError, TypeError, etc.) are
    all caught and wrapped as TransportError.
    """

    def chat_completion(
        self,
        payload: dict,
        *,
        timeout: float | None = None,
    ) -> dict: ...


@runtime_checkable
class LLMClient(Protocol):
    """High-level simple client. Text in, text out.

    Use this protocol when the caller produces a single logical prompt and
    does not need to inspect the provider response envelope (finish_reason,
    usage, etc.). Callers that need raw response metadata or full message
    control use LLMTransport.chat_completion() directly.

    call(prompt) -> str
        Executes the prompt and returns the assistant text, stripped of
        leading and trailing whitespace. The underlying chat_completion
        guarantees content is non-empty after strip(); call() applies
        that strip() before returning so callers receive clean text.

    call(prompt, context=...) -> str
        For static prepend scenarios only: a shared system block, background
        instructions, or reference material where no custom separator or
        ordering is required. The combining is always f"{context}\\n\\n{prompt}".
        Use this when the split between "static prefix" and "variable prompt"
        is natural and the double-newline join is correct for the content.

        Do NOT use context when: a specific separator is required (e.g. the
        podcast "---" between prompt and PDF), when ordering is non-trivial,
        or when domain formatting rules govern the assembly. In those cases
        assemble the full string at the call site and pass it as prompt.
        Current callers (podcast, slicer, seed_gen) all assemble at the call
        site because they need the "---" separator or embed content via
        template substitution — context is intentionally unused by them, not
        dead code. A future caller with a plain system-prompt / user-query
        split (no separator, no template) is the intended consumer.

    On failure: raises LLMError. Callers that want a domain-specific
    exception catch LLMError and re-raise (see call_api in Step 2).
    """

    def call(self, prompt: str, *, context: str = "") -> str: ...
```

### `exceptions.py`

```python
class LLMError(Exception):
    """Base for all LLM transport errors."""

class TransportError(LLMError):
    """Any transport-level failure after retries exhausted: non-2xx HTTP,
    network error (Timeout/ConnectionError), empty content, or JSON decode
    failure."""

class RateLimitError(LLMError):
    """Rate limited even after retries."""

class LLMConfigError(LLMError):
    """Missing API key or invalid configuration."""
```

> **Note:** The name `APIResponseError` is intentionally avoided — `novel_pipeline/exceptions.py` already defines `APIResponseError(PipelineError)` as a domain-level exception. Using `TransportError` here prevents any ambiguity between transport-level and domain-level failures.

### `providers/openrouter.py`

A single class implementing both protocols:

```python
class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        api_url: str | None = None,
        max_tokens: int = 8192,
        retry_after_override: float | None = None,
        max_retries: int = 3,
        backoff_seconds: tuple[float, ...] = (2, 8, 32),
        jitter_max: float = 2.0,
    ) -> None: ...

    def chat_completion(self, payload: dict, *, timeout: float | None = None) -> dict: ...

    def call(self, prompt: str, *, context: str = "") -> str: ...
```

`call()` combines `context` and `prompt` as `f"{context}\n\n{prompt}"` when context is non-empty, then wraps in a single user message. The `---` separator is **not** used here — it is a podcast-domain convention assembled by the callers that need it: `call_api()` for the `main.py` → `call_api` path, and `LLMScriptEngine.generate()` for the direct engine path. `call()` receives an already-assembled prompt string and does not know or care about the separator. Callers with a natural prompt/context split (e.g. system instructions + user query) use `context` directly.

**Deployment-level parameters** — set once per deployment in `.env`; resolved by `resolve_from_env()` and passed as constructor args by the caller (constructor arg → hardcoded default). The "Env var" column documents the name `resolve_from_env()` uses to populate each constructor arg. `OpenRouterClient` has no internal env var fallbacks — all env var reading goes through `resolve_from_env()` at the call site:

| Parameter | Env var | Hardcoded default |
|-----------|---------|-------------------|
| `api_key` | `OPENROUTER_API_KEY` | raises `LLMConfigError` |
| `model` | `OPENROUTER_MODEL` | `z-ai/glm-4.5-air:free` |
| `api_url` | `OPENROUTER_URL` | `https://openrouter.ai/api/v1/chat/completions` |
| `max_tokens` | `OPENROUTER_MAX_TOKENS` | `8192` |
| `retry_after_override` | `OPENROUTER_RETRY_AFTER` | `None` (use header → body → backoff) |

`OpenRouterClient.__init__` is responsible for type-converting `max_tokens` and `retry_after_override` when they arrive as raw strings from `env.py`. Convert with `int()` / `float()` and raise `LLMConfigError` (not `ValueError`) on failure: `LLMConfigError(f"OPENROUTER_MAX_TOKENS must be an integer, got: {v!r}")`. Do not do this conversion in `env.py` — that module does not know the expected types.

**Pipeline-level parameters** — no env var; wiring origins read these from their own config files and pass as constructor args (constructor arg → hardcoded default):

| Parameter | Hardcoded default |
|-----------|-------------------|
| `max_retries` | `3` |
| `backoff_seconds` | `(2, 8, 32)` |
| `jitter_max` | `2.0` |

**Call-level parameter** — `timeout` on `chat_completion` is a per-call method arg, not a constructor param. `None` means no timeout. Wiring origins that need a timeout must pass it explicitly; the novel pipeline wiring origin reads `timeout_seconds` (TOML default: `120`) and passes it down through `run_session` → `requests_.py` → `api.call_api`. The podcast chain never set a timeout and continues not to.

> **Note:** `config_path` is intentionally removed. The podcast domain uses JSON (`src/config.py`) and the novel pipeline uses TOML (`novel_pipeline/config.py`) — two incompatible formats. Each entry point reads its own config and passes resolved values as constructor args. The transport layer never touches a config file.

**OpenRouter-specific retry delay:** On HTTP 429, `OpenRouterClient` resolves the retry delay in this order: (0) `retry_after_override` constructor arg — a fixed override in seconds, resolved by the wiring origin from `OPENROUTER_RETRY_AFTER` env var or `retry_after_seconds` in config, then passed in at construction time; (1) `Retry-After` header (seconds or HTTP date); (2) `error.metadata.retry_after_seconds` in the JSON response body — OpenRouter free-tier returns the delay here, not in the header; (3) `backoff_seconds` schedule. This body-parsing logic is specific to OpenRouter's error shape and lives in `OpenRouterClient`, not in the generic transport protocol.

> **Note — `retry_after_override` priority:** Priority (0) is intentional. `retry_after_override` is a hard override designed for test and staging environments where predictable, operator-controlled retry timing matters more than respecting the provider's signal. In production, leave `OPENROUTER_RETRY_AFTER` unset so the provider's `Retry-After` header and body field govern the delay. Setting `retry_after_override` in production means the client will ignore the provider's instruction — use it only when that behaviour is explicitly desired.

> **Note — non-OpenRouter endpoints (e.g. DashScope):** `OpenRouterClient` works with any OpenAI-compatible endpoint via the `api_url` constructor arg. The current `src/config.json` points to a DashScope endpoint — this is intentional and inherited: the project switched from OpenRouter to DashScope by overriding the URL and key without changing any code. Set `OPENROUTER_API_KEY` to the DashScope API key. The `error.metadata.retry_after_seconds` body field is OpenRouter-specific; when absent (as with DashScope), the transport falls through to the backoff schedule without error. If a future endpoint requires meaningfully different behaviour (non-OpenAI-compatible format, different auth scheme), add a new provider module under `src/llm/providers/` and a branch in `factory.py` — no domain code changes required.

### Transport contract

**On success:** Returns the raw provider JSON response dict unchanged. Callers read `choices[0]["message"]["content"]`, `usage`, `finish_reason`, etc. directly. One additional guarantee: if `chat_completion` returns, `choices[0]["message"]["content"]` is non-empty after `strip()` — the transport uses `strip()` to check for empty content and retries if the stripped result is empty, but the returned dict is otherwise unchanged; the raw provider value in `choices[0]["message"]["content"]` is not modified before being returned.

**On failure:** Always raises `LLMError`. No raw exception of any kind escapes to the caller. Network-level `requests.RequestException` subclasses — `Timeout`, `ConnectionError`, `SSLError`, `TooManyRedirects`, `ChunkedEncodingError`, and any other failure that is not an HTTP status code error — are caught and wrapped. `HTTPError` is not in this category — it is raised by `raise_for_status()` on a non-2xx response and is handled by the status-code logic (429 → retry, 5xx → retry, 4xx except 429 → fail-fast), not by the network-error catch. Any exception raised while accessing the response dict — `KeyError`, `IndexError`, `TypeError`, `AttributeError`, or any other built-in — is also caught and wrapped as `TransportError`; the transport's internal parsing operations never let raw exceptions reach callers.

| Exception raised | Condition |
|-----------------|-----------|
| `RateLimitError` | HTTP 429 exhausted retries |
| `TransportError` | Any other failure after retries exhausted |

**Absorbed with retry** (caller never sees these):

| Failure mode | Action |
|-------------|--------|
| HTTP 429 | Retry; honor `Retry-After` header (seconds or HTTP date), else backoff |
| HTTP 5xx | Retry with configurable exponential backoff + optional jitter |
| Network-level `requests.RequestException` (not `HTTPError`) | Retry with backoff — covers `Timeout`, `ConnectionError`, `SSLError`, `TooManyRedirects`, `ChunkedEncodingError`, and all other failures that are not HTTP status code errors |
| Empty or whitespace-only `choices[0].message.content` after `strip()` (HTTP 200) | Retry with backoff |

**Fail-fast, no retry** (raises `TransportError` immediately):

| Failure mode | Reason |
|-------------|--------|
| HTTP 4xx except 429 | Client error — retrying won't fix it. Applies to 400, 401, 403, 404, 405, 408, 422, and every other 4xx code. |
| `json.JSONDecodeError` | Severe infrastructure malfunction — no point retrying |
| Any exception from response parsing (`KeyError`, `IndexError`, `TypeError`, `AttributeError`, etc.) | Malformed provider response — structural issue, not retryable |

### `factory.py`

```python
import os
from llm.exceptions import LLMConfigError
from llm.protocol import LLMClient, LLMTransport

def _build(**kwargs):
    provider = os.getenv("LLM_PROVIDER", "openrouter")
    if provider == "openrouter":
        from llm.providers.openrouter import OpenRouterClient
        return OpenRouterClient(**kwargs)
    raise LLMConfigError(f"Unknown LLM_PROVIDER: {provider!r}")

def create_client(**kwargs) -> LLMClient:
    obj = _build(**kwargs)
    if not isinstance(obj, LLMClient):
        raise LLMConfigError(f"{type(obj).__name__} does not implement LLMClient")
    return obj

def create_transport(**kwargs) -> LLMTransport:
    obj = _build(**kwargs)
    if not isinstance(obj, LLMTransport):
        raise LLMConfigError(f"{type(obj).__name__} does not implement LLMTransport")
    return obj
```

`_build()` is private and works at the concrete type level — the one place in the codebase that is allowed to know about `OpenRouterClient` directly. `create_client()` and `create_transport()` each re-declare the return type the type checker needs to see; since `OpenRouterClient` implements both protocols, both declarations are satisfied without a cast.

Both protocols are `@runtime_checkable`, which is what makes the `isinstance` guards possible. The guards fail fast at construction time — if a provider class is registered in `factory.py` but does not implement the required protocol, the error surfaces immediately at wiring time rather than silently at the first call site.

`**kwargs` allows callers to pass `model`, `api_url`, `max_tokens`, etc. resolved from their own config files. Zero-arg calls still work and fall through to env vars / defaults.

### `env.py`

```python
import os

def resolve_from_env() -> dict:
    """Returns deployment-level LLM parameters that are set in the environment.

    Only keys with non-empty env vars are included in the result. Missing or
    empty vars are absent, so callers can use config-file values as fallback
    via dict merge:

        create_client(**{**cfg_kwargs, **resolve_from_env()})

    env always wins over config because resolve_from_env() is spread last.
    All provider-specific env var names for all currently registered providers
    are centralised here — if a var is renamed, change it in one place. When
    a new provider is added, add its env var block here alongside the existing
    OpenRouter block; do not hardcode provider-specific var names anywhere else.
    Factory-selection variables (e.g. LLM_PROVIDER) are not provider-specific
    constructor parameters and are read directly where they are used (factory.py).
    """
    result = {}
    if v := os.environ.get("OPENROUTER_API_KEY"):
        result["api_key"] = v
    if v := os.environ.get("OPENROUTER_MODEL"):
        result["model"] = v
    if v := os.environ.get("OPENROUTER_URL"):
        result["api_url"] = v
    if v := os.environ.get("OPENROUTER_MAX_TOKENS"):
        result["max_tokens"] = v
    if v := os.environ.get("OPENROUTER_RETRY_AFTER"):
        result["retry_after_override"] = v
    return result
```

`env.py` is a pure name mapper — it does not know or care what type each constructor argument expects. Raw strings are passed; `OpenRouterClient.__init__` converts `max_tokens` to `int` and `retry_after_override` to `float`, raising `LLMConfigError` with a clear message on invalid values (e.g. `OPENROUTER_MAX_TOKENS=abc`). Pipeline-level parameters (`max_retries`, `backoff_seconds`, `jitter_max`) have no env vars and are not included; wiring origins read those directly from their config files.

---

## Dependency Injection Pattern

Domain functions stop importing the concrete client. They accept an abstraction as a parameter:

```python
# Before (src/slicer/pdf_splitter.py)
def get_toc_from_llm(pdf_path: str) -> ...:
    sys.path.insert(0, llm_dir)
    from call_api import call_api
    response = call_api(pdf_text="", prompt_text=prompt)

# After
def get_toc_from_llm(pdf_path: str, llm: LLMClient) -> ...:
    response = llm.call(prompt=prompt)
```

> **Note:** This example shows the general DI pattern. For `src/slicer/pdf_splitter.py` specifically, the parameter is `llm: LLMClient | None` — see Step 3 for the exact signature and `None` guard. The `| None` is a slicer-specific graceful-degradation concern, not a general DI requirement.

Wiring happens at the engine factory, not inside domain functions. `src/engines/factory.py` is the origin for both podcast chains — it reads `src/config.json`, constructs the client once, and passes it into the engine:

```python
# src/engines/factory.py
from config import load_config
from llm.env import resolve_from_env
from llm.factory import create_client

def default_llm_script_engine(mode: str = "2person") -> ScriptEngine:
    cfg = load_config()
    client = create_client(**{
        "api_key": cfg.get("api_key"),
        "model": cfg.get("model"),
        "api_url": cfg.get("api_url"),
        "max_tokens": cfg.get("max_tokens"),
        "retry_after_override": cfg.get("retry_after_seconds"),
        **resolve_from_env(),  # env wins over config
    })
    return LLMScriptEngine(mode=mode, llm=client)

def default_splitter_engine() -> SplitterEngine:
    cfg = load_config()
    client = create_client(**{
        "api_key": cfg.get("api_key"),
        "model": cfg.get("model"),
        "api_url": cfg.get("api_url"),
        "max_tokens": cfg.get("max_tokens"),
        "retry_after_override": cfg.get("retry_after_seconds"),
        **resolve_from_env(),  # env wins over config
    })
    return PDFSplitterEngine(llm=client)
```

> **Note:** `resolve_from_env()` (from `llm.env`) is the single source of truth for all env var names. Do not hardcode `OPENROUTER_*` var names in wiring origins — import and call `resolve_from_env()` instead. Env always wins over config because `resolve_from_env()` is spread last in the dict merge. `resolve_from_env()` returns raw strings — type conversion (`int` for `max_tokens`, `float` for `retry_after_override`) happens inside `OpenRouterClient.__init__`, which is the only consumer that knows the expected types.
>
> **All callers use `resolve_from_env()`:** `engines/factory.py` (and the novel pipeline wiring origins) have a config file context — they build a cfg dict and spread `resolve_from_env()` last so env wins over config. Callers without a config file context (`slicer/pdf_splitter.py`, `fiction/seed_gen/cli.py`, `podcast_script_generator/llm/main.py`) call `create_client(**resolve_from_env())` directly — no cfg dict, just the env mapping. `OpenRouterClient` has no internal env var fallbacks; `resolve_from_env()` in `llm.env` is the single and only reader of env var names for all callers.

`src/cli/podcast.py` changes in one place: remove `default_splitter_engine` from the `engines.factory` import and remove the `splitter_engine=default_splitter_engine()` kwarg from the `generate_book_podcast` call. `endpoints/podcast.py` takes over lazy construction with `LLMConfigError` handling. All other behaviour is unchanged.

For the novel pipeline there are two entry paths with distinct wiring origins:

- **Harness path:** `src/cli/fiction.py` parses args (unchanged) → calls `src/endpoints/fiction.py:run_novel_session()`. `endpoints/fiction.py` is the wiring origin — it loads the TOML config, constructs the transport (when no `client` is injected), and passes it to `run_session`. Tests pass a `FakeLLMTransport` directly via the `client` parameter.
- **Direct path:** `src/novel_pipeline/cli.py` is still a valid direct entry point (`PYTHONPATH=src python src/novel_pipeline/cli.py --config ...`). It reads the TOML config, constructs the transport, and calls `run_session`. It is no longer a pip console script but is otherwise unchanged in purpose.

**Config loading is the wiring origin's responsibility.** `OpenRouterClient` never reads a config file — it accepts `api_key`, `model`, `api_url`, `max_tokens`, etc. directly or falls back to env vars. This keeps the transport layer free of format-specific config concerns.

---

## Migration Plan

### Step 1 — Create `src/llm/` package

Create the following files. The interface stubs in the **Target Architecture** section above are the authoritative contracts — implement them exactly as specified there.

| File | Content |
|------|---------|
| `src/llm/__init__.py` | Empty. Makes `llm` importable as a package. |
| `src/llm/protocol.py` | `LLMTransport` and `LLMClient` protocols. Full stub in Target Architecture → `protocol.py`. |
| `src/llm/exceptions.py` | `LLMError`, `TransportError`, `RateLimitError`, `LLMConfigError`. Full stub in Target Architecture → `exceptions.py`. |
| `src/llm/factory.py` | `create_client()` and `create_transport()`. Full stub in Target Architecture → `factory.py`. |
| `src/llm/env.py` | `resolve_from_env()`. Full stub in Target Architecture → `env.py`. All env var names live here — do not hardcode `OPENROUTER_*` var names anywhere else. |
| `src/llm/providers/__init__.py` | Empty. |
| `src/llm/providers/openrouter.py` | `OpenRouterClient` implementing both protocols. Full stub in Target Architecture → `providers/openrouter.py`. |

**What to extract from existing implementations into `OpenRouterClient`:**

From `src/novel_pipeline/api.py`: `_parse_retry_after` (header + HTTP-date parsing), `_backoff_seconds` (exponential schedule), `_jittered_sleep` (adds random jitter), the `requests` retry loop (429 / 5xx / network / empty-content retry logic).

From `src/podcast_script_generator/llm/call_api.py`: the `error.metadata.retry_after_seconds` body-fallback for OpenRouter free-tier 429 responses, auth header construction. **Do not** extract the `OPENROUTER_RETRY_AFTER` env var reading into `OpenRouterClient` — that is now handled by `resolve_from_env()` in `env.py`. What belongs in `OpenRouterClient` is the **handling** of the `retry_after_override` constructor arg: applying it as priority (0) in the 429 delay resolution logic.

**Do not copy** into `OpenRouterClient`: domain token accounting, cost gates, spend tracking, prompt assembly, or the `---` separator — those stay in their domain modules.

`adapters.py` and `SimpleLLMClient` are not needed — `call_api` is migrated to proper DI in Step 2.

### Step 2 — Update `call_api` to proper DI
Replace `src/podcast_script_generator/llm/call_api.py` with a DI function that accepts an `LLMClient`:

```python
from llm.exceptions import LLMError
from llm.protocol import LLMClient
from .exceptions import ScriptGenerationError

def call_api(pdf_text: str, prompt_text: str, llm: LLMClient) -> str:
    combined = f"{prompt_text}\n\n---\n\n{pdf_text}" if pdf_text else prompt_text
    try:
        return llm.call(prompt=combined)
    except LLMError as e:
        raise ScriptGenerationError(str(e)) from e
```

No module-level singleton. The `LLMClient` is created at the entry point (`main()`) and passed in. Transport errors are caught here and re-raised as `ScriptGenerationError` to preserve the podcast domain's exception contract.

### Step 3 — Update simple callers (DI with `LLMClient`)

**Migration order within this step:** `src/engines/factory.py` must be the first file migrated. It is the wiring origin that moves config reading out of the transport layer — until it is wired, domain code that previously read `src/config.json` inside the transport has no config path. Migrate the factory, verify it constructs and injects a client, then migrate the remaining files in any order.

| File | Change |
|------|--------|
| `src/engines/factory.py` | **Wiring origin.** Read `src/config.json`; call `create_client(api_key=..., model=..., api_url=..., max_tokens=..., retry_after_override=...)` with all deployment parameters resolved from env and config (env wins — see DI Pattern section above); pass the returned client into `LLMScriptEngine` and `PDFSplitterEngine`. The factory is the primary resolver for every deployment parameter including `api_key` — do not rely on `OpenRouterClient`'s internal env var fallback as the primary path. Do not instantiate `OpenRouterClient` directly — provider selection is the factory's responsibility. |
| `src/engines/llm_script.py` | Add `llm: LLMClient` to `__init__`. In `generate()`, remove the lazy `call_api` import. **Preserve the `fiction_meta` special case exactly as-is:** after the `{TECHNICAL_CONTENT}` substitution, call `self.llm.call(prompt)` with no separator — `pdf_text` is already embedded in the prompt and must not be appended again. **For all other modes**, assemble the combined prompt: `combined = f"{prompt_text}\n\n---\n\n{pdf_text}" if pdf_text else prompt_text`, then call `self.llm.call(combined)`. Applying the `---` separator in `fiction_meta` mode would duplicate the PDF content because `{TECHNICAL_CONTENT}` substitution already placed it inside the prompt string. |
| `src/engines/pdf_splitter.py` | Add `llm: LLMClient` to `__init__`; pass `llm` through to `run_splitter`. |
| `src/slicer/pdf_splitter.py` | Add `llm: LLMClient \| None` to `get_toc_from_llm`, `extract_toc`, and `run_splitter`; remove `sys.path.insert` block. **`get_toc_from_llm`:** add `if llm is None: return None` as the first line — when no client is available Stage 4 returns `None` immediately, allowing the pipeline to fall through to Stage 5 (`get_toc_from_content_scan`) without calling the LLM. Add `from llm.exceptions import LLMError` and replace the broad `except Exception` with `except LLMError` — `llm.call()` raises `LLMError` on transport failure; `ScriptGenerationError` is never raised here because slicer calls `llm.call()` directly, not through `call_api()`. Log the error and return `None`. **CLI `main()`:** add `from llm.exceptions import LLMConfigError` and `from llm.env import resolve_from_env` to imports. Call `create_client(**resolve_from_env())`. Wrap `create_client(**resolve_from_env())` in `try/except LLMConfigError` — log the error and set `client = None`. Pass `client` (possibly `None`) to `run_splitter`; it threads through `extract_toc` → `get_toc_from_llm` where the `None` guard fires. Do **not** return a failure dict on `LLMConfigError` — `run_splitter` must still be called so Stages 1–3 and Stage 5 can run; only Stage 4 is skipped. |
| `src/fiction/seed_gen/cli.py` | Remove `sys.path.insert`; import helpers via `podcast_script_generator.llm.*`. Add `from podcast_script_generator.llm.exceptions import ScriptGenerationError` and `from llm.exceptions import LLMConfigError` to imports — both are required before the handlers below compile. Replace `except (ValueError, RuntimeError)` with `except (ValueError, ScriptGenerationError)` — the new `call_api` raises `ScriptGenerationError`, not `RuntimeError`; leaving `RuntimeError` in the handler means LLM failures escape uncaught. In `main()`, add `from llm.env import resolve_from_env` to imports alongside the existing `from llm.exceptions import LLMConfigError`. Call `create_client(**resolve_from_env())`. Wrap `create_client(**resolve_from_env())` in `try/except LLMConfigError`: print a clean error message and call `sys.exit(1)` — without this, execution continues with `client` undefined, causing `AttributeError` at the `call_api` call site. `seed_gen` has no fallback path: if no API key is available there is nothing to do. Retain `import sys` — after removing `sys.path.insert` it would otherwise become a dead import, but `sys.exit(1)` requires it. |
| `src/podcast_script_generator/llm/main.py` | Add `from llm.exceptions import LLMConfigError` to imports — without this the `except LLMConfigError` block below raises `NameError` at runtime. Add `from llm.env import resolve_from_env` and `from llm.protocol import LLMClient` to imports. Add `llm: LLMClient | None = None` to `main()`. When `llm is None`, create the client via `create_client(**resolve_from_env())`; otherwise use the injected client. Pass the client to `call_api(pdf_text, prompt_text, llm=client)`. Catch `LLMConfigError` explicitly alongside `PodcastError` — `create_client()` raises `LLMConfigError` when the API key is missing or the provider is unknown; it is not a `PodcastError` and will escape uncaught without this explicit handler. Also add `print(f"Wrote {len(files)} files to {output_dir}")` after the `save_output(files, output_dir)` call — `main()` is the entry point and owns all user-facing output; `save_output` is a library function (Section 6 of the pipeline) and must not print to stdout. Also remove the "Prints `Wrote N files to {output_dir}` on success" clause from `save_output`'s docstring in `save_output.py` — it documents a stdout side effect that never belonged in a library function and was never implemented. |
| `src/tts/cli.py` | No change needed. Imports `TTSSubmissionError`, `TTSTimeoutError`, `PodcastError` from `podcast_script_generator.llm.exceptions` — those are TTS-domain exceptions kept in the podcast shim, not transport-level errors. |
| `src/endpoints/podcast.py` | Add `from llm.exceptions import LLMConfigError` to imports. In `generate_book_podcast`: **(1)** wrap the `default_splitter_engine()` call inside the existing `if splitter_engine is None:` branch in `try/except LLMConfigError` and `return [PodcastResult(error=e)]` on failure; **(2)** after the `if not resolve_dir or not resolve_dir.exists(): return []` check and before the `pdfs = sorted(...)` call, add an early script-engine construction block: if `script_engine is None`, construct via `default_llm_script_engine(mode=mode)` wrapped in `try/except LLMConfigError` and `return [PodcastResult(error=e)]` on failure. Wrap only the constructions — not the whole function. Placement after the `resolve_dir` check is required — construction must not fire when there are no chapter PDFs to process. This ensures a missing API key in book mode produces one structured error, not N identical per-chapter errors. **(3)** Also add `from llm.exceptions import LLMError` alongside `LLMConfigError`; add `from podcast_script_generator.llm.exceptions import ScriptGenerationError` if not already imported. In `generate_chapter_podcast`, wrap the `script_engine.generate(...)` call in `try/except LLMError as e: raise ScriptGenerationError(str(e)) from e`. The raised `ScriptGenerationError` is caught by `generate_chapter_podcast`'s existing outer `except Exception` and packaged as `PodcastResult(error=e)` — no additional catch site needed. This is the exception boundary for the engine path: `LLMError` (a transport exception) must not appear in `PodcastResult.error`; only domain exceptions should. Requires Step 1 (`src/llm/`) to be complete before this import resolves. |
| `src/cli/podcast.py` | Remove `default_splitter_engine` and `default_llm_script_engine` from the `engines.factory` import (line 77) — only `default_audio_engine` remains. Remove the `splitter_engine=default_splitter_engine()` kwarg from the `generate_book_podcast` call (line 97). Remove the eager `default_llm_script_engine(mode=args.mode)` construction (line 78) and replace with `script_engine = None` — the endpoint constructs it lazily. Both engine constructions move into `endpoints/podcast.py` with proper `LLMConfigError` handling. No other changes. |

### Step 4 — Update novel pipeline (DI with `LLMTransport`)

| File | Change |
|------|--------|
| `src/novel_pipeline/api.py` | Keep token/cost/overflow/finish_reason logic. Accept `client: LLMTransport` and `timeout: float | None`. Replace the HTTP request loop with `client.chat_completion(payload, timeout=timeout)` — pass `timeout` on every call so the per-call timeout from TOML config is honoured. **Remove** the embedded retry loop (429/5xx/network/empty-content) — the transport contract guarantees those are handled. **Do not fix the jitter inconsistency in the empty-content retry path before migrating** — that path calls `_backoff_seconds()` instead of `_jittered_sleep()`, but the entire retry loop is deleted here; fixing it first is wasted work. After this step the transport owns all retries and uses `_jittered_sleep()` consistently. **Remove** `_resolve_api_key`, header construction, URL resolution, `_parse_retry_after`, `_backoff_seconds`, `_jittered_sleep`, and the `requests` import — all owned by the transport now. Keep `finish_reason` checks (`length` → `ChapterValidationError`, `content_filter` → `APIResponseError`) — those are domain decisions. Continue calling `track_spend`. Translate transport exceptions into domain exceptions — **do not let transport exceptions escape into domain code**: `RateLimitError` → `APIRateLimitError`; `TransportError` → `APIResponseError`. Import both `RateLimitError` and `TransportError` from `llm.exceptions` and both `APIRateLimitError` and `APIResponseError` from `.exceptions`. |
| `src/novel_pipeline/requests_.py` | Add `client: LLMTransport` and `timeout: float | None` to `request_chapter` and `request_living_doc_update`. Receive `timeout` as a typed parameter — do not read from the config dict here. Forward it directly as the `timeout` argument to `api.call_api`. The wiring origin is the only place in the call chain that touches the string key `"timeout_seconds"`; every layer below receives a `float | None` value. |
| `src/novel_pipeline/session.py` | Add `client: LLMTransport` **and** `timeout: float | None` to `run_session`, `_run_one_chapter`, `_generate_chapter_text`, and `_resolve_starting_chapter`. Thread both through all four — they travel together. `_resolve_starting_chapter` calls `request_living_doc_update` on the resume-regeneration path; if either `client` or `timeout` is missing from that path, it raises `TypeError`. |
| `src/novel_pipeline/cli.py` | **Direct-run wiring origin.** Reads TOML config; constructs transport using `resolve_from_env()` (from `llm.env`) for env-priority resolution: `create_transport(**{"api_key": cfg.get("api_key"), "model": cfg["model"], "api_url": cfg.get("api_url"), "max_retries": cfg["max_retries"], "backoff_seconds": tuple(cfg["retry_backoff_seconds"]), "jitter_max": cfg["retry_jitter_seconds_max"], "max_tokens": cfg.get("max_tokens"), "retry_after_override": cfg.get("retry_after_seconds"), **resolve_from_env()})`. Pipeline-level parameters (`max_retries`, `backoff_seconds`, `jitter_max`) have no env vars and are not in `resolve_from_env()` — read them directly from TOML config. Read `cfg.get("timeout_seconds")` here and pass the resolved value as `timeout` to `run_session`. This is the only place in the direct-run call chain that touches the string key `"timeout_seconds"` — all layers below receive a typed `float | None` parameter, never a config dict or key name. `None` cannot occur in practice: `load_config()` applies `DEFAULTS` (`timeout_seconds: 120`) before returning, and then validates the value is > 0 — so `cfg["timeout_seconds"]` is always a positive integer after `load_config()`. Catch `LLMConfigError` at startup and map it to `ConfigError` / exit code 2 to preserve the documented exit-code contract. No longer a pip entry point but otherwise unchanged in purpose. |
| `src/endpoints/fiction.py` | **Harness wiring origin.** Apply wiring origin rules: construct transport before any domain call, wrap only the construction in try/except (not `run_session`), read `timeout` from config and pass as a typed arg before the domain call; when `client` is provided skip construction entirely. Add `client: LLMTransport \| None = None` to `run_novel_session`. When `client` is `None` (production path), load TOML config from `config_path` and construct the transport with the same `create_transport(**{...cfg_kwargs..., **resolve_from_env()})` call as `novel_pipeline/cli.py` above — pipeline-level parameters (`max_retries`, `backoff_seconds`, `jitter_max`) read directly from TOML config. When `client` is provided (test path), skip construction and use it directly. Read `cfg.get("timeout_seconds")` here and pass the resolved value as `timeout` to `run_session`. This is the only place in the harness call chain that touches the string key `"timeout_seconds"` — all layers below receive a typed `float | None` parameter, never a config dict or key name. `None` cannot occur in practice: `load_config()` applies `DEFAULTS` (`timeout_seconds: 120`) before returning, and then validates the value is > 0 — so `cfg["timeout_seconds"]` is always a positive integer after `load_config()`. Catch `LLMConfigError` during transport construction and map it to `ConfigError` / exit code 2. Add `from novel_pipeline.exceptions import ConfigError`, `from llm.protocol import LLMTransport`, and `from llm.env import resolve_from_env` to the imports. |
| `src/cli/fiction.py` | Add `except ConfigError` **before** the existing broad `except Exception` and return exit code 2. Import `ConfigError` from `novel_pipeline.exceptions`. Without this, `ConfigError` raised by `endpoints/fiction.py` is caught by the broad handler and silently returns exit 1, breaking the documented exit-code contract. All other behaviour is unchanged. **This is the only architecture-compliant fix.** Two alternatives exist but are ruled out by the architecture: (1) an `isinstance(e, ConfigError)` check inside the broad handler works mechanically but conflates semantically distinct cases and obscures intent; (2) raising `SystemExit(2)` inside `endpoints/fiction.py` pushes exit-code policy into the endpoint layer, which is reusable and must not own CLI concerns. Exit-code translation belongs at the CLI boundary — `cli/fiction.py` is already that boundary, as demonstrated by `KeyboardInterrupt → 1` and `Exception → 1` already present there, and by `novel_pipeline/cli.py` applying the same pattern at its own boundary (`except ConfigError: return 2` at lines 87 and 126). |
| `src/novel_pipeline/config.py` | Remove the env var override block that maps `OPENROUTER_API_KEY` → `config["api_key"]` and `OPENROUTER_MODEL` → `config["model"]`. After migration, `load_config()` is a pure TOML reader — it returns only values from the config file. Env var resolution is `resolve_from_env()`'s exclusive responsibility; the wiring origins (`novel_pipeline/cli.py` and `endpoints/fiction.py`) already spread `resolve_from_env()` last, so env always wins over TOML without any work inside `load_config()`. This block was a pre-migration holdover from when `novel_pipeline` was a standalone package with no wiring origin; it is now redundant and its presence means `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` appear in two places, violating the single-source-of-truth principle established by `env.py`. |

> **Note:** `src/cli/podcast.py` changes in two places: remove both `default_splitter_engine` and `default_llm_script_engine` from the import (line 77) and remove their eager constructions at lines 78 and 97. `src/endpoints/podcast.py` becomes the error boundary for both splitter-engine and script-engine construction in book mode. `src/engines/factory.py` is the wiring origin for engine construction and **does** change (see Step 3).

### Step 5 — Remove `sys.path.insert` blocks
- `src/slicer/pdf_splitter.py:214-216`
- `src/fiction/seed_gen/cli.py:7`
- Keep test-only hacks in `test_all.py` as test isolation mechanisms.

### Step 6 — Update tests

#### `src/podcast_script_generator/llm/test_all.py`

**Pre-existing bug 1 — `parse_args` arity (line 82):** `parse_args()` now returns 4 values `(pdf_path, prompt_path, output_dir, context)` but the test unpacks 3: `a, b, c = parse_args()`. This crashes the entire test run before any LLM-related code executes. Fix as part of the DI restructure below: change the unpacking to `a, b, c, ctx = parse_args()`. The `ctx` value will be `None` for the `2person` mode used in the test and can be ignored.

**Pre-existing bug 2 — `save_output` stdout assertion (line 320):** The test asserts `"Wrote 2 files" in r.stdout`, but `save_output` only calls `logger.debug(...)`, which never appears on stdout by default. **Do not** add a print to `save_output` — it is a library function (Section 6 of the pipeline) and must not own user-facing output. The fix belongs in `main()` (Step 3 above): add `print(f"Wrote {len(files)} files to {output_dir}")` after the `save_output(files, output_dir)` call, and remove the "Prints..." clause from `save_output`'s docstring. The test assertion at line 320 requires no change — it runs the full pipeline via `main.main()` as a subprocess and will pass once `main()` emits the message.

**DI migration:** The e2e test currently monkey-patches `call_api.call_api = lambda ...`. After migration that patch target no longer exists — `main()` constructs the client when no `llm` is injected (see Step 3). The test passes a fake `LLMClient` directly via `main(llm=fake)` — no patching required.

#### `src/novel_pipeline/tests/test_pipeline.py`

The test file is already at `src/novel_pipeline/tests/test_pipeline.py` — the move was completed when `novel_pipeline` was converted from a standalone package (see "What Was Wrong With v1", point 3). No move needed.

Remove the vestigial block at the top of the file (just above the `from novel_pipeline import` lines):

```python
# Ensure the freshly-installed package is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))
```

This block inserts the `tests/` directory itself — which contains no importable modules — and was a leftover from the old standalone-package era. After removing it, delete `import sys` if it is the only remaining consumer of that import. (`from pathlib import Path` and all other imports are still used and must stay.)

**Pre-migration fixes required (three tests fail today, before the transport refactor):**

**Pre-existing failure 1 — `WORLD_BIBLE` key renamed to `WORLD_LAWS`:** Three assertions search for `"=== WORLD_BIBLE ==="` but the production code renders the `world_laws` static doc key as `"=== WORLD_LAWS ==="`. Replace every occurrence of `"=== WORLD_BIBLE ==="` with `"=== WORLD_LAWS ==="` in `test_order_is_fixed`, `test_static_doc_order_overridable_via_config`, and `test_extra_static_docs_appended_alphabetised`. Three-line change.

**Pre-existing failure 2 — `test_runaway_rejections_eventually_raise` input mock consumed prematurely:** The test patches `builtins.input` with `iter(["y"] + ["n"] * 100)`. The `"y"` is intended for the living-doc validation prompt, but `run_session` also calls `builtins.input` for chapter approval, consuming the `"y"` before the living-doc prompt can see it. Fix: pass `approve_chapter=lambda n, t: False` to `run_session` so the chapter-approval path never calls `builtins.input`. The mock then has exactly one consumer and the `"y"` reaches the correct prompt.

**Gap 1 — `TestCallAPI`:** Rewrite around a `FakeLLMTransport` passed directly to `api.py` functions. Drop the `novel_pipeline.api.requests` patch entirely. `FakeLLMTransport` returns a valid provider dict with non-empty `choices[0]["message"]["content"]` on success and raises `TransportError` / `RateLimitError` on failure. All `api.py` functions now require both `client: LLMTransport` and `timeout: float | None` — pass `timeout=None` in standard tests; pass a concrete `float` only for any test that specifically asserts timeout-forwarding behaviour. Omitting `timeout` raises `TypeError`. Keep token/cost/overflow/finish_reason tests unchanged — they test domain logic, not transport.

**Gap 2 — Session-level tests** (`TestH2KeepOldStopsSession`, `TestM4RejectionLimitBounded`, etc.): `run_session` now requires `client: LLMTransport` **and** `timeout: float | None`. `_session_setup` must be extended to create a `FakeLLMTransport` and pass both `client` and `timeout=None` to every `run_session` call — there is no alternative. Without this every session test raises `TypeError`.

**Gap 3 — `TestRequestWrappers`:** Currently patches `novel_pipeline.requests_.call_api`. After migration `request_chapter` and `request_living_doc_update` accept `client` directly. Drop the `call_api` patch; pass a `FakeLLMTransport` directly to the wrapper functions instead. Both functions also require `timeout: float | None` — pass `timeout=None` for most tests, or a concrete `float` for any test that asserts timeout-forwarding behaviour. Omitting `timeout` raises `TypeError`.

**Move** retry tests (429 backoff, network error, `Retry-After` header, body-fallback `error.metadata.retry_after_seconds`, 4xx fail-fast raises `TransportError` immediately with no retry, malformed response missing `choices` structure raises `TransportError`) out of `test_pipeline.py` into a new `src/llm/providers/tests/test_openrouter.py` — they test transport behaviour, not domain behaviour. Preserve the assertion that `time.sleep` is called with the correct delay value.

**Dead test 1 — `test_env_overrides` (line 627):** Delete. This test asserts that `load_config()` merges `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` env vars into the returned dict. Step 4 deliberately removes that behaviour — `load_config()` becomes a pure TOML reader and env var merging moves to `resolve_from_env()` at the wiring origin. The test is a spec for a removed contract; there is no updated form worth keeping.

**Dead test 2 — `test_missing_api_key_raises` (line 1005):** Delete from `test_pipeline.py`. This test calls `call_api()` with the old pre-migration signature (messages, model, cfg dict) and asserts `ConfigError` when no API key is present. After Step 4, `call_api()` accepts `client: LLMTransport` — the old signature is gone and the API key check moves to `OpenRouterClient.__init__()`. Add equivalent coverage to `src/llm/providers/tests/test_openrouter.py`: assert that `OpenRouterClient(api_key=None)` raises `LLMConfigError`. This sits naturally alongside the other transport-layer tests already planned for that file.

### Step 7 — Delete old implementations (after verification)
- Remove the old `call_api` implementation from `src/podcast_script_generator/llm/call_api.py` — it is fully replaced by the DI version in Step 2.
- Do **not** delete `src/novel_pipeline/api.py`; it keeps domain orchestration.
- Do **not** touch `src/podcast_script_generator/llm/exceptions.py` — `PodcastError` stays as the domain base. `LLMError` is caught and re-raised as `ScriptGenerationError` before escaping the podcast domain — at `call_api` on the `main.py` path, and at `endpoints/podcast.py` on the engine path.

---

## Adding a New Provider Later

1. Add `src/llm/providers/new_provider.py` implementing **both** `LLMTransport` and `LLMClient`. Both are required — `create_transport()` and `create_client()` each assert the returned object satisfies the respective protocol via `isinstance` (enabled by `@runtime_checkable`). A class implementing only one will raise `LLMConfigError` at wiring time. There is no mechanism to register a provider for one protocol only.
2. Add a branch in `src/llm/factory.py`.
3. Set `LLM_PROVIDER=new_provider` in `.env`.
4. Zero changes to domain modules.

---

## Verification

```bash
# No production path hacks remain
grep -r "sys.path.insert" src/ | grep -v test | grep -v "__pycache__" | grep -v "ai_context.md"

# No domain module bypasses the factory (direct provider imports forbidden)
grep -r "from llm\.providers\|import OpenRouterClient" \
  src/slicer src/fiction src/engines src/tts src/novel_pipeline \
  src/cli src/endpoints src/podcast_script_generator

# Factory resolves correctly: provider instantiates and satisfies LLMClient protocol
PYTHONPATH=src python -c "
import os; os.environ['OPENROUTER_API_KEY'] = 'test-key'
from llm.env import resolve_from_env
from llm.factory import create_client
from llm.protocol import LLMClient
c = create_client(**resolve_from_env())
assert isinstance(c, LLMClient), type(c)
print('factory ok')
"

# Import smoke tests
PYTHONPATH=src python -c "from engines.llm_script import LLMScriptEngine; from slicer.pdf_splitter import get_toc_from_llm"

# env.py resolves correctly
PYTHONPATH=src python -c "
import os; os.environ['OPENROUTER_API_KEY'] = 'test-key'; os.environ['OPENROUTER_MAX_TOKENS'] = '4096'
from llm.env import resolve_from_env
r = resolve_from_env()
assert r['api_key'] == 'test-key', r
assert r['max_tokens'] == '4096', r
assert 'model' not in r
print('env.py ok')
"

# Podcast generator tests pass
PYTHONPATH=src python src/podcast_script_generator/llm/test_all.py

# Novel pipeline tests pass
PYTHONPATH=src python -m pytest src/novel_pipeline/tests/test_pipeline.py
```

---

## Scope Exclusions

- Do **not** move token counting, cost tracking, spend persistence, or living-doc validation out of `novel_pipeline`.
- Do **not** merge `PodcastError` and `PipelineError` hierarchies.
- Do **not** re-export `LLMError` as `PodcastError`. `PodcastError(Exception)` stays as the podcast domain base unchanged. Transport errors are always caught and re-raised as `ScriptGenerationError` before escaping the podcast domain: on the `call_api` path the boundary is `call_api`; on the engine path the boundary is `endpoints/podcast.py` (see Step 3).
- `client: LLMTransport` is a **required** parameter in `run_session`, `request_chapter`, and `request_living_doc_update` — no default. Wiring is the caller's responsibility. `novel_pipeline` is no longer standalone and has no reason to construct its own transport.
- Add `APIRateLimitError(APIResponseError)` to `novel_pipeline/exceptions.py` and re-export it in `novel_pipeline/__init__.py` alongside the existing exceptions. This is the only change to that file — the rest of the domain hierarchy (`CostLimitError`, `ContextOverflowError`, `APIResponseError`, etc.) stays exactly as-is. `APIRateLimitError` inherits from `APIResponseError` (not `PipelineError` directly) so that all existing `except APIResponseError` catch sites in `session.py` handle rate-limit exhaustion automatically — no catch-site additions required. Callers that need to distinguish rate-limit from other API errors catch `APIRateLimitError` first, before the broader `except APIResponseError`. **Exit codes:** the two CLI paths produce different codes by design — `novel_pipeline/cli.py` (direct path) maps `APIResponseError` to exit 3 and `APIRateLimitError` inherits that via the existing handler — no new handler needed there. `cli/fiction.py` (harness path) catches only `ConfigError` (exit 2) and everything else via the broad `except Exception` (exit 1) — rate-limit exhaustion exits 1 on this path, consistent with that CLI's intentional coarse exit-code contract. Do not add `except APIResponseError` to `cli/fiction.py`; that would impose `novel_pipeline/cli.py`'s granular scheme onto a boundary the spec designed differently.
- Do **not** add config file loading to `OpenRouterClient`. Entry points own config loading; the transport accepts explicit constructor args. `OpenRouterClient` has no internal env var fallbacks — all env var reading goes through `resolve_from_env()` at the call site for all callers. Do not add env var reads inside `OpenRouterClient`.
