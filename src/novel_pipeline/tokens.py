"""Token counting with tiktoken + configurable fallback encoder.

If tiktoken cannot load its BPE tables (e.g. fully offline environment with
no cached encoder), a coarse character-based heuristic is used. This
maintains the spec's ±10% accuracy promise on typical English-language
prose; production deployments should ensure tiktoken can reach its CDN or
ship a pre-warmed cache.

I4: fallback encoding name and chars-per-token can be configured via
`tokenizer_encoding_fallback` and `tokenizer_chars_per_token`.
"""

from __future__ import annotations

from functools import lru_cache

from .logging_ import log_event


# Process-level default fallback encoding name. Overridable via the
# `model` form of count_tokens that takes config.
_DEFAULT_FALLBACK_ENCODING = "cl100k_base"
_DEFAULT_CHARS_PER_TOKEN = 4


@lru_cache(maxsize=16)
def _get_encoding(model: str, fallback_encoding: str):
    """Resolve a tiktoken encoder. Per-model first, fallback encoding next.

    Raises whatever tiktoken raises if neither is available; callers should
    handle the resulting exception via the heuristic path.
    """
    import tiktoken

    try:
        return tiktoken.encoding_for_model(model)
    except (KeyError, ValueError):
        return tiktoken.get_encoding(fallback_encoding)


def _heuristic_token_count(text: str, chars_per_token: int) -> int:
    """Coarse fallback when tiktoken is unavailable.

    Uses configurable chars-per-token (default 4) which is close to the
    long-run average for English prose with cl100k_base.
    """
    if not text:
        return 0
    chars = len(text)
    return max(1, chars // max(1, chars_per_token))


_FALLBACK_WARNED = False


def count_tokens(text: str, model: str, config: dict | None = None) -> int:
    """Count tokens in `text` for `model`.

    Uses tiktoken's model-specific encoding when available, otherwise the
    configured fallback encoding. If neither encoder can be loaded
    (offline + no cache), falls back to a chars-per-token heuristic and
    logs a one-time warning. The spec accepts ±10% variance.

    `config` is optional; when provided, `tokenizer_encoding_fallback` and
    `tokenizer_chars_per_token` are respected (I4).
    """
    global _FALLBACK_WARNED
    if not text:
        return 0

    cfg = config or {}
    fallback_encoding = cfg.get("tokenizer_encoding_fallback", _DEFAULT_FALLBACK_ENCODING)
    chars_per_token = int(cfg.get("tokenizer_chars_per_token", _DEFAULT_CHARS_PER_TOKEN))

    try:
        enc = _get_encoding(model, fallback_encoding)
        return len(enc.encode(text))
    except Exception as e:
        if not _FALLBACK_WARNED:
            _FALLBACK_WARNED = True
            log_event(
                "tiktoken_unavailable_using_heuristic",
                {"error": str(e), "model": model, "chars_per_token": chars_per_token},
            )
        return _heuristic_token_count(text, chars_per_token)
