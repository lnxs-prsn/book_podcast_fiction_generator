"""OpenRouter API call layer.

Owns:
- Token pre-flight (ContextOverflowError with per-document breakdown)
- Cost pre-flight (CostLimitError unless --ignore-cost-limit)
- Post-call actual-cost accounting via track_spend
- Truncation detection via finish_reason (C1)
- Configurable creativity controls (temperature/top_p/seed) (L1)
"""

from __future__ import annotations

import json

from llm.exceptions import RateLimitError, TransportError
from llm.protocol import LLMTransport

from .cost import current_totals, estimate_cost, track_spend
from .exceptions import (
    APIRateLimitError,
    APIResponseError,
    ChapterValidationError,
    ConfigError,
    ContextOverflowError,
    CostLimitError,
)
from .logging_ import log_event
from .tokens import count_tokens


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _messages_to_text(messages: list[dict]) -> str:
    """Concatenate message contents for token counting (system + user)."""
    return "\n".join(m.get("content", "") for m in messages)


def _count_prompt_tokens(messages: list[dict], model: str, config: dict) -> int:
    """H3: token counting that accounts for chat-template overhead.

    OpenAI's documented chat format adds ~4 tokens per message (role +
    separators) and ~3 tokens of priming for the completion. Both values
    are configurable via `token_count_per_message_overhead` and
    `token_count_completion_priming` (H3 / I4).
    """
    per_message = int(config.get("token_count_per_message_overhead", 4))
    priming = int(config.get("token_count_completion_priming", 3))

    total = 0
    for m in messages:
        content = m.get("content", "") or ""
        total += count_tokens(content, model, config)
        total += per_message
    total += priming
    return total


def _per_document_tokens(
    static_docs: dict[str, str] | None,
    living_doc: str | None,
    model: str,
    config: dict,
) -> dict[str, int]:
    """Token counts per document for the overflow error message."""
    out: dict[str, int] = {}
    if static_docs:
        for name, text in static_docs.items():
            out[name] = count_tokens(text, model, config)
    if living_doc is not None:
        out["living_doc"] = count_tokens(living_doc, model, config)
    return out


def _format_overflow_message(
    prompt_tokens: int,
    context_limit: int,
    safety_margin: int,
    doc_breakdown: dict[str, int],
    static_doc_order: list[str],
) -> str:
    lines = [
        f"Context overflow: prompt is {prompt_tokens} tokens, limit is "
        f"{context_limit}, safety margin {safety_margin}.",
        "Document sizes:",
    ]
    seen: set[str] = set()
    for key in static_doc_order:
        if key in doc_breakdown:
            lines.append(f"  {key + ':':<16} {doc_breakdown[key]} tokens")
            seen.add(key)
    for key in sorted(set(doc_breakdown) - seen - {"living_doc"}):
        lines.append(f"  {key + ':':<16} {doc_breakdown[key]} tokens")
    if "living_doc" in doc_breakdown:
        lines.append(
            f"  {'living_doc:':<16} {doc_breakdown['living_doc']} tokens  "
            f"<-- largest mutable document"
        )
    lines.extend(
        [
            "Suggestions:",
            "  1. Manually compress living_doc (remove resolved foreshadowing, "
            "collapse Touch 2+ entries).",
            "  2. Switch to a model with larger context window.",
            "No automatic truncation — that would corrupt pedagogical tracking.",
        ]
    )
    return "\n".join(lines)


def _enforce_cost_limits(
    estimated: float,
    config: dict,
    *,
    ignore_limit: bool,
) -> None:
    totals = current_totals(config)
    session_limit = float(config.get("cost_limit_usd_per_session", 5.00))
    lifetime_limit = float(config.get("cost_limit_usd_total", 50.00))

    if ignore_limit:
        return

    projected_session = totals["session_total"] + estimated
    projected_lifetime = totals["lifetime_total"] + estimated

    if projected_session > session_limit:
        raise CostLimitError(
            f"Session cost limit would be exceeded: "
            f"current ${totals['session_total']:.4f} + estimated "
            f"${estimated:.4f} = ${projected_session:.4f} > "
            f"${session_limit:.2f}. Re-run with --ignore-cost-limit to override."
        )
    if projected_lifetime > lifetime_limit:
        raise CostLimitError(
            f"Lifetime cost limit would be exceeded: "
            f"current ${totals['lifetime_total']:.4f} + estimated "
            f"${estimated:.4f} = ${projected_lifetime:.4f} > "
            f"${lifetime_limit:.2f}. Re-run with --ignore-cost-limit to override."
        )


def _build_payload(
    messages: list[dict],
    model: str,
    config: dict,
    *,
    max_tokens: int,
) -> dict:
    """C1 + L1: build the JSON payload with creativity controls and
    max_tokens. Optional fields are only included when set in config so
    legitimate API defaults still apply when unconfigured."""
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": int(max_tokens),
    }
    if config.get("temperature") is not None:
        payload["temperature"] = float(config["temperature"])
    if config.get("top_p") is not None:
        payload["top_p"] = float(config["top_p"])
    if config.get("seed") is not None:
        payload["seed"] = int(config["seed"])
    return payload


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def call_api(
    messages: list[dict],
    model: str,
    config: dict,
    *,
    client: LLMTransport,
    timeout: float | None = None,
    expected_output_tokens: int | None = None,
    ignore_cost_limit: bool = False,
    static_docs: dict[str, str] | None = None,
    living_doc: str | None = None,
    task_label: str = "",
) -> str:
    """Call the configured LLM transport and return the assistant text.

    Pre-flight:
      1. Token count vs context_limit - safety_margin.
      2. Estimated cost vs session/lifetime limits.
    Transport-level retries are handled by the injected client. Domain layer
    keeps finish_reason checks, cost accounting, and truncation detection.
    """
    context_limit = int(config["context_limit"])
    safety_margin = int(config.get("context_safety_margin", 8000))

    # --- Token pre-flight ---------------------------------------------------
    prompt_tokens = _count_prompt_tokens(messages, model, config)
    if prompt_tokens + safety_margin > context_limit:
        breakdown = _per_document_tokens(static_docs, living_doc, model, config)
        from .config import DEFAULT_STATIC_DOC_ORDER

        static_order = list(config.get("static_doc_order", DEFAULT_STATIC_DOC_ORDER))
        raise ContextOverflowError(
            _format_overflow_message(
                prompt_tokens, context_limit, safety_margin, breakdown, static_order
            )
        )

    # --- Cost pre-flight ----------------------------------------------------
    if expected_output_tokens is None:
        expected_output_tokens = int(
            config.get("expected_output_tokens_chapter", 4000)
        )

    explicit_max = None
    label_lc = (task_label or "").lower()
    if "update" in label_lc:
        explicit_max = config.get("api_default_max_tokens_update")
    else:
        explicit_max = config.get("api_default_max_tokens_chapter")
    max_tokens_for_payload = int(explicit_max) if explicit_max else int(expected_output_tokens)

    estimated = estimate_cost(prompt_tokens, expected_output_tokens, config)
    _enforce_cost_limits(estimated, config, ignore_limit=ignore_cost_limit)

    log_event(
        "api_call_preflight",
        {
            "task": task_label,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "expected_output_tokens": expected_output_tokens,
            "max_tokens_in_payload": max_tokens_for_payload,
            "estimated_cost_usd": round(estimated, 6),
            "temperature": config.get("temperature"),
            "top_p": config.get("top_p"),
            "seed": config.get("seed"),
        },
    )

    # --- Request via injected transport -------------------------------------
    payload = _build_payload(
        messages, model, config, max_tokens=max_tokens_for_payload
    )

    try:
        raw = client.chat_completion(payload, timeout=timeout)
    except RateLimitError as e:
        raise APIRateLimitError(str(e)) from e
    except TransportError as e:
        raise APIResponseError(str(e)) from e

    # --- Parse response -----------------------------------------------------
    choice0 = raw["choices"][0]
    content = choice0["message"]["content"]
    finish_reason = choice0.get("finish_reason")

    if finish_reason == "length":
        log_event(
            "api_call_truncated_by_length",
            {
                "task": task_label,
                "max_tokens_in_payload": max_tokens_for_payload,
                "content_chars": len(content or ""),
            },
        )
        raise ChapterValidationError(
            "Model hit max_tokens before completing the response "
            f"(finish_reason='length'; max_tokens={max_tokens_for_payload}). "
            "The output is truncated and unsafe to use. Either increase "
            "expected_output_tokens_chapter / "
            "api_default_max_tokens_chapter in config, or retry the "
            "request."
        )
    if finish_reason == "content_filter":
        log_event(
            "api_call_content_filtered",
            {"task": task_label},
        )
        raise APIResponseError(
            "Response was rejected by the model's content filter "
            "(finish_reason='content_filter'). Adjust the prompt or "
            "switch models."
        )

    content = content.strip()

    # --- Actual cost from usage --------------------------------------------
    usage = raw.get("usage") or {}
    actual_in = int(usage.get("prompt_tokens", prompt_tokens))
    actual_out = int(usage.get("completion_tokens", expected_output_tokens))
    actual_cost = estimate_cost(actual_in, actual_out, config)
    track_spend(
        actual_cost,
        config,
        note=f"{task_label} model={model} in={actual_in} out={actual_out}",
    )
    log_event(
        "api_call_success",
        {
            "task": task_label,
            "model": model,
            "actual_prompt_tokens": actual_in,
            "actual_completion_tokens": actual_out,
            "actual_cost_usd": round(actual_cost, 6),
            "content_chars": len(content),
            "finish_reason": finish_reason,
        },
    )
    return content
