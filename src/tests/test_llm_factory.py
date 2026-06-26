"""Tests for llm.factory — LLM_DEFAULT_TIMEOUT_SECONDS env var read and forwarded."""

from unittest.mock import patch

import pytest

from llm.exceptions import LLMConfigError
from llm.factory import create_client, create_transport


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_client_uses_llm_default_timeout_seconds(mock_client):
    with patch.dict("os.environ", {"LLM_DEFAULT_TIMEOUT_SECONDS": "90.5"}, clear=True):
        create_client(api_key="k")
    mock_client.assert_called_once()
    assert mock_client.call_args.kwargs["timeout"] == 90.5


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_client_explicit_timeout_overrides_env(mock_client):
    with patch.dict("os.environ", {"LLM_DEFAULT_TIMEOUT_SECONDS": "90.5"}, clear=True):
        create_client(api_key="k", timeout=30.0)
    assert mock_client.call_args.kwargs["timeout"] == 30.0


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_client_no_timeout_when_env_unset(mock_client):
    with patch.dict("os.environ", {}, clear=True):
        create_client(api_key="k")
    mock_client.assert_called_once()
    assert "timeout" not in mock_client.call_args.kwargs


def test_create_client_rejects_invalid_llm_default_timeout():
    with patch.dict(
        "os.environ", {"LLM_DEFAULT_TIMEOUT_SECONDS": "not-a-number"}, clear=True
    ):
        with pytest.raises(LLMConfigError):
            create_client(api_key="k")


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_transport_uses_llm_default_timeout_seconds(mock_client):
    with patch.dict("os.environ", {"LLM_DEFAULT_TIMEOUT_SECONDS": "45"}, clear=True):
        create_transport(api_key="k")
    assert mock_client.call_args.kwargs["timeout"] == 45.0


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_transport_explicit_timeout_overrides_env(mock_client):
    with patch.dict("os.environ", {"LLM_DEFAULT_TIMEOUT_SECONDS": "45"}, clear=True):
        create_transport(api_key="k", timeout=10.0)
    assert mock_client.call_args.kwargs["timeout"] == 10.0


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_client_forwards_api_key(mock_client):
    with patch.dict("os.environ", {}, clear=True):
        create_client(api_key="my-secret-key")
    assert mock_client.call_args.kwargs["api_key"] == "my-secret-key"


def test_create_transport_rejects_invalid_llm_default_timeout():
    with patch.dict(
        "os.environ", {"LLM_DEFAULT_TIMEOUT_SECONDS": "bad-value"}, clear=True
    ):
        with pytest.raises(LLMConfigError):
            create_transport(api_key="k")
