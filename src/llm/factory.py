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
        raise LLMConfigError(
            f"{type(obj).__name__} does not implement LLMClient"
        )
    return obj


def create_transport(**kwargs) -> LLMTransport:
    obj = _build(**kwargs)
    if not isinstance(obj, LLMTransport):
        raise LLMConfigError(
            f"{type(obj).__name__} does not implement LLMTransport"
        )
    return obj
