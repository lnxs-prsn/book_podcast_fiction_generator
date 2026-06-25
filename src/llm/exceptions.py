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
