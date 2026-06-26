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
    if "timeout" not in kwargs:
        if timeout_env := os.getenv("LLM_DEFAULT_TIMEOUT_SECONDS"):
            try:
                kwargs["timeout"] = float(timeout_env)
            except (TypeError, ValueError) as e:
                raise LLMConfigError(
                    f"LLM_DEFAULT_TIMEOUT_SECONDS must be a float, got: {timeout_env!r}"
                ) from e
    obj = _build(**kwargs)
    if not isinstance(obj, LLMClient):
        raise LLMConfigError(
            f"{type(obj).__name__} does not implement LLMClient"
        )
    return obj


def create_transport(**kwargs) -> LLMTransport:
    if "timeout" not in kwargs:
        if timeout_env := os.getenv("LLM_DEFAULT_TIMEOUT_SECONDS"):
            try:
                kwargs["timeout"] = float(timeout_env)
            except (TypeError, ValueError) as e:
                raise LLMConfigError(
                    f"LLM_DEFAULT_TIMEOUT_SECONDS must be a float, got: {timeout_env!r}"
                ) from e
    obj = _build(**kwargs)
    if not isinstance(obj, LLMTransport):
        raise LLMConfigError(
            f"{type(obj).__name__} does not implement LLMTransport"
        )
    return obj
