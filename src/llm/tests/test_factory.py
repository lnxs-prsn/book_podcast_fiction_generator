"""Tests for llm.factory timeout handling."""

from unittest.mock import patch

import pytest

from llm.exceptions import LLMConfigError
from llm.factory import create_client, create_transport


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_client_uses_llm_default_timeout_seconds(mock_client):
    with patch.dict(
        "os.environ", {"BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS": "90.5"}, clear=True
    ):
        create_client(api_key="k")
    mock_client.assert_called_once()
    assert mock_client.call_args.kwargs["timeout"] == 90.5


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_client_explicit_timeout_overrides_env(mock_client):
    with patch.dict(
        "os.environ", {"BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS": "90.5"}, clear=True
    ):
        create_client(api_key="k", timeout=30.0)
    assert mock_client.call_args.kwargs["timeout"] == 30.0


@patch("llm.providers.openrouter.OpenRouterClient")
def test_create_transport_uses_llm_default_timeout_seconds(mock_client):
    with patch.dict(
        "os.environ", {"BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS": "45"}, clear=True
    ):
        create_transport(api_key="k")
    assert mock_client.call_args.kwargs["timeout"] == 45.0


def test_create_client_rejects_invalid_llm_default_timeout():
    with patch.dict(
        "os.environ", {"BOOKGEN_LLM_DEFAULT_TIMEOUT_SECONDS": "not-a-number"}, clear=True
    ):
        with pytest.raises(LLMConfigError):
            create_client(api_key="k")
