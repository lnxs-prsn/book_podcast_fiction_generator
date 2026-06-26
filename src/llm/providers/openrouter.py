"""OpenRouter HTTP transport implementing both LLMTransport and LLMClient."""

from __future__ import annotations

import json
import logging
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

from llm.exceptions import LLMConfigError, RateLimitError, TransportError
from llm.protocol import LLMClient, LLMTransport

logger = logging.getLogger(__name__)

_DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_MODEL = "z-ai/glm-4.5-air:free"
_DEFAULT_MAX_TOKENS = 8192
_DEFAULT_MAX_RETRIES = 3
_DEFAULT_BACKOFF_SECONDS = (2, 8, 32)
_DEFAULT_JITTER_MAX = 2.0

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_NETWORK_ERRORS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.SSLError,
    requests.exceptions.TooManyRedirects,
    requests.exceptions.ChunkedEncodingError,
)


class OpenRouterClient:
    """OpenRouter-compatible HTTP transport.

    Implements both the low-level LLMTransport protocol (raw payload in,
    raw provider dict out) and the high-level LLMClient protocol (prompt in,
    text out).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        api_url: str | None = None,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        retry_after_override: float | None = None,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        backoff_seconds: tuple[float, ...] = _DEFAULT_BACKOFF_SECONDS,
        jitter_max: float = _DEFAULT_JITTER_MAX,
        timeout: float | None = None,
    ) -> None:
        if api_key is None:
            raise LLMConfigError("api_key is required")

        if max_tokens is None:
            max_tokens = _DEFAULT_MAX_TOKENS
        try:
            max_tokens = int(max_tokens)
        except (TypeError, ValueError) as e:
            raise LLMConfigError(
                f"OPENROUTER_MAX_TOKENS must be an integer, got: {max_tokens!r}"
            ) from e

        if retry_after_override is not None:
            try:
                retry_after_override = float(retry_after_override)
            except (TypeError, ValueError) as e:
                raise LLMConfigError(
                    f"retry_after_override must be a float, got: {retry_after_override!r}"
                ) from e

        self.api_key = api_key
        self.model = model if model is not None else _DEFAULT_MODEL
        self.api_url = api_url if api_url is not None else _DEFAULT_API_URL
        self.max_tokens = max_tokens
        self.retry_after_override = retry_after_override
        self.max_retries = int(max_retries)
        self.backoff_seconds = tuple(float(x) for x in backoff_seconds)
        self.jitter_max = float(jitter_max)
        self.timeout = float(timeout) if timeout is not None else None

    # ------------------------------------------------------------------
    # LLMClient protocol
    # ------------------------------------------------------------------
    def call(
        self,
        prompt: str,
        *,
        context: str = "",
        timeout: float | None = None,
    ) -> str:
        """High-level text-in/text-out interface."""
        if context:
            user_content = f"{context}\n\n{prompt}"
        else:
            user_content = prompt

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": user_content}],
            "max_tokens": self.max_tokens,
        }
        response = self.chat_completion(payload, timeout=timeout if timeout is not None else self.timeout)
        content = response["choices"][0]["message"]["content"]
        # chat_completion guarantees content is non-empty after strip().
        return content.strip()

    # ------------------------------------------------------------------
    # LLMTransport protocol
    # ------------------------------------------------------------------
    def chat_completion(
        self,
        payload: dict,
        *,
        timeout: float | None = None,
    ) -> dict:
        """Execute a chat-completion payload against the configured endpoint."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=timeout,
                )
            except _NETWORK_ERRORS as e:
                last_error = e
                logger.debug(
                    "OpenRouter network error on attempt %d/%d: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    e,
                )
                if attempt >= self.max_retries:
                    raise TransportError(
                        f"Network error after {self.max_retries} retries: {e}"
                    ) from e
                self._sleep_backoff(attempt)
                continue

            # Fail-fast on non-retryable client errors.
            if response.status_code in (400, 401, 403):
                raise TransportError(
                    f"OpenRouter returned {response.status_code} "
                    f"(non-retryable): {response.text[:500]}"
                )

            if response.status_code in _RETRYABLE_STATUS:
                if response.status_code == 429:
                    wait = self._resolve_retry_after(response)
                else:
                    wait = self._backoff_seconds(attempt)

                logger.debug(
                    "OpenRouter retryable status %d on attempt %d/%d; sleeping %.2fs",
                    response.status_code,
                    attempt + 1,
                    self.max_retries + 1,
                    wait,
                )

                if attempt >= self.max_retries:
                    raise RateLimitError(
                        f"OpenRouter returned {response.status_code} after "
                        f"{self.max_retries} retries: {response.text[:500]}"
                    )
                time.sleep(wait)
                continue

            # Any other non-2xx not in our retry set.
            if not response.ok:
                raise TransportError(
                    f"OpenRouter returned {response.status_code}: "
                    f"{response.text[:500]}"
                )

            # Parse response.
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise TransportError(
                    f"non-JSON response: {e}: {response.text[:500]}"
                ) from e

            try:
                choice0 = data["choices"][0]
                content = choice0["message"]["content"]
            except (KeyError, IndexError, TypeError) as e:
                raise TransportError(
                    "malformed response (no choices[0].message.content): "
                    f"{json.dumps(data)[:500]}"
                ) from e

            if content is None:
                content = ""
            stripped = content.strip()
            if not stripped:
                if attempt >= self.max_retries:
                    raise TransportError(
                        "OpenRouter returned empty content after retries"
                    )
                logger.debug(
                    "OpenRouter empty content on attempt %d/%d; retrying",
                    attempt + 1,
                    self.max_retries + 1,
                )
                self._sleep_backoff(attempt)
                continue

            return data

        raise TransportError(
            f"exhausted retries with no specific error: {last_error}"
        )

    # ------------------------------------------------------------------
    # Retry helpers
    # ------------------------------------------------------------------
    def _resolve_retry_after(self, response: requests.Response) -> float:
        """Resolve the delay for a 429 response.

        Priority:
          0. retry_after_override constructor arg
          1. Retry-After header (seconds or HTTP date)
          2. error.metadata.retry_after_seconds in the JSON body
          3. backoff_seconds schedule
        """
        if self.retry_after_override is not None:
            return float(self.retry_after_override)

        header = response.headers.get("Retry-After", "")
        wait = self._parse_retry_after(header)
        if wait is not None:
            return wait

        try:
            body = response.json()
            body_wait = float(
                body.get("error", {})
                .get("metadata", {})
                .get("retry_after_seconds", -1)
            )
            if body_wait >= 0:
                return body_wait
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
            pass

        return self._backoff_seconds(0)

    def _parse_retry_after(self, value: str) -> float | None:
        """Parse a Retry-After header value (seconds or HTTP date)."""
        if not value:
            return None
        value = value.strip()
        try:
            return max(0.0, float(value))
        except ValueError:
            pass
        try:
            dt = parsedate_to_datetime(value)
            if dt is None:
                return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = (dt - datetime.now(timezone.utc)).total_seconds()
            return max(0.0, delta)
        except (TypeError, ValueError):
            return None

    def _backoff_seconds(self, attempt: int) -> float:
        schedule = self.backoff_seconds
        if not schedule:
            return 0.0
        idx = min(attempt, len(schedule) - 1)
        base = float(schedule[idx])
        jitter = (
            random.uniform(0.0, self.jitter_max) if self.jitter_max > 0 else 0.0
        )
        return base + jitter

    def _sleep_backoff(self, attempt: int) -> None:
        time.sleep(self._backoff_seconds(attempt))
