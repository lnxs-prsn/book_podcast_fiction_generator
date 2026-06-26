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
        ordering is required. The combining is always f"{context}\n\n{prompt}".
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

    def call(
        self,
        prompt: str,
        *,
        context: str = "",
        timeout: float | None = None,
    ) -> str: ...
