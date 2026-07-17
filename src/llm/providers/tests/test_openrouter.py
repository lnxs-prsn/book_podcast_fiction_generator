"""Transport-layer tests for llm.providers.openrouter."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from llm.exceptions import LLMConfigError, RateLimitError, TransportError
from llm.providers.openrouter import _DEFAULT_API_URL, OpenRouterClient


def _success_response(content: str = "hello") -> dict:
    return {
        "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }


def test_missing_api_key_raises():
    with pytest.raises(LLMConfigError):
        OpenRouterClient(api_key=None)


def test_invalid_max_tokens_raises():
    with pytest.raises(LLMConfigError):
        OpenRouterClient(api_key="k", max_tokens="abc")


def test_invalid_retry_after_override_raises():
    with pytest.raises(LLMConfigError):
        OpenRouterClient(api_key="k", retry_after_override="abc")


def test_api_url_base_gets_chat_completions_path():
    client = OpenRouterClient(api_key="k", api_url="https://api.deepseek.com")
    assert client.api_url == "https://api.deepseek.com/v1/chat/completions"


@pytest.mark.parametrize(
    "api_url",
    ["https://api.deepseek.com/v1", "https://api.deepseek.com/v1/"],
)
def test_api_url_v1_gets_chat_completions_path(api_url):
    client = OpenRouterClient(api_key="k", api_url=api_url)
    assert client.api_url == "https://api.deepseek.com/v1/chat/completions"


@pytest.mark.parametrize(
    "api_url",
    [
        "https://api.deepseek.com/v1/chat/completions",
        "https://api.deepseek.com/v1/chat/completions/",
    ],
)
def test_api_url_full_path_passes_through(api_url):
    client = OpenRouterClient(api_key="k", api_url=api_url)
    assert client.api_url == "https://api.deepseek.com/v1/chat/completions"


def test_api_url_none_uses_default():
    client = OpenRouterClient(api_key="k", api_url=None)
    assert client.api_url == _DEFAULT_API_URL


def test_429_retry_then_success():
    client = OpenRouterClient(
        api_key="k",
        max_retries=1,
        backoff_seconds=(2,),
        jitter_max=0.0,
    )
    success = _success_response()
    with patch("llm.providers.openrouter.requests.post") as mock_post, patch(
        "llm.providers.openrouter.time.sleep"
    ) as mock_sleep:
        resp429 = MagicMock()
        resp429.status_code = 429
        resp429.headers = {"Retry-After": "1"}
        resp429.text = "rate-limited"
        resp429.json.return_value = {"error": {"metadata": {}}}

        resp200 = MagicMock()
        resp200.status_code = 200
        resp200.ok = True
        resp200.json.return_value = success

        mock_post.side_effect = [resp429, resp200]
        result = client.chat_completion({"model": "m", "messages": []})
        assert result == success
        assert mock_post.call_count == 2
        mock_sleep.assert_called_with(1.0)


def test_429_body_fallback_retry_after():
    client = OpenRouterClient(
        api_key="k",
        max_retries=1,
        backoff_seconds=(2,),
        jitter_max=0.0,
    )
    success = _success_response()
    with patch("llm.providers.openrouter.requests.post") as mock_post, patch(
        "llm.providers.openrouter.time.sleep"
    ) as mock_sleep:
        resp429 = MagicMock()
        resp429.status_code = 429
        resp429.headers = {}
        resp429.text = "rate-limited"
        resp429.json.return_value = {
            "error": {"metadata": {"retry_after_seconds": 7.5}}
        }

        resp200 = MagicMock()
        resp200.status_code = 200
        resp200.ok = True
        resp200.json.return_value = success

        mock_post.side_effect = [resp429, resp200]
        result = client.chat_completion({"model": "m", "messages": []})
        assert result == success
        mock_sleep.assert_called_with(7.5)


def test_401_fail_fast_no_sleep():
    client = OpenRouterClient(
        api_key="k",
        max_retries=3,
        backoff_seconds=(2,),
        jitter_max=0.0,
    )
    with patch("llm.providers.openrouter.requests.post") as mock_post, patch(
        "llm.providers.openrouter.time.sleep"
    ) as mock_sleep:
        resp401 = MagicMock()
        resp401.status_code = 401
        resp401.text = "unauthorized"
        resp401.json.return_value = {"error": "unauthorized"}
        mock_post.return_value = resp401

        with pytest.raises(TransportError):
            client.chat_completion({"model": "m", "messages": []})

        assert mock_post.call_count == 1
        mock_sleep.assert_not_called()


def test_network_error_retries_with_backoff():
    client = OpenRouterClient(
        api_key="k",
        max_retries=2,
        backoff_seconds=(3, 9),
        jitter_max=0.0,
    )
    success = _success_response()
    with patch("llm.providers.openrouter.requests.post") as mock_post, patch(
        "llm.providers.openrouter.time.sleep"
    ) as mock_sleep:
        resp200 = MagicMock()
        resp200.status_code = 200
        resp200.ok = True
        resp200.json.return_value = success

        mock_post.side_effect = [
            requests.exceptions.ConnectionError("boom"),
            requests.exceptions.Timeout("timeout"),
            resp200,
        ]
        result = client.chat_completion({"model": "m", "messages": []})
        assert result == success
        assert mock_post.call_count == 3
        assert mock_sleep.call_count == 2


def test_malformed_response_raises_transport_error():
    client = OpenRouterClient(
        api_key="k",
        max_retries=0,
        backoff_seconds=(2,),
        jitter_max=0.0,
    )
    with patch("llm.providers.openrouter.requests.post") as mock_post, patch(
        "llm.providers.openrouter.time.sleep"
    ) as mock_sleep:
        resp200 = MagicMock()
        resp200.status_code = 200
        resp200.ok = True
        resp200.json.return_value = {"weird": "shape"}
        mock_post.return_value = resp200

        with pytest.raises(TransportError):
            client.chat_completion({"model": "m", "messages": []})

        mock_sleep.assert_not_called()


def test_empty_content_retries():
    client = OpenRouterClient(
        api_key="k",
        max_retries=1,
        backoff_seconds=(2,),
        jitter_max=0.0,
    )
    success = _success_response()
    with patch("llm.providers.openrouter.requests.post") as mock_post, patch(
        "llm.providers.openrouter.time.sleep"
    ) as mock_sleep:
        resp_empty = MagicMock()
        resp_empty.status_code = 200
        resp_empty.ok = True
        resp_empty.json.return_value = {
            "choices": [{"message": {"content": "   "}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

        resp200 = MagicMock()
        resp200.status_code = 200
        resp200.ok = True
        resp200.json.return_value = success

        mock_post.side_effect = [resp_empty, resp200]
        result = client.chat_completion({"model": "m", "messages": []})
        assert result == success
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1


def test_rate_limit_exhausted_raises_rate_limit_error():
    client = OpenRouterClient(
        api_key="k",
        max_retries=0,
        backoff_seconds=(2,),
        jitter_max=0.0,
    )
    with patch("llm.providers.openrouter.requests.post") as mock_post:
        resp429 = MagicMock()
        resp429.status_code = 429
        resp429.headers = {}
        resp429.text = "rate-limited"
        resp429.json.return_value = {"error": {"metadata": {}}}
        mock_post.return_value = resp429

        with pytest.raises(RateLimitError):
            client.chat_completion({"model": "m", "messages": []})
