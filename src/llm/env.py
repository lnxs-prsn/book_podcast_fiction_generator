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
