"""Tests for engines.factory timeout handling."""

from unittest.mock import patch

import pytest

from engines import factory as engines_factory


@patch("engines.factory.create_client")
@patch("engines.factory.load_config")
def test_default_llm_script_engine_passes_openrouter_timeout_seconds(
    mock_load_config, mock_create_client
):
    mock_load_config.return_value = {}
    with patch.dict(
        "os.environ", {"OPENROUTER_TIMEOUT_SECONDS": "120"}, clear=True
    ):
        engines_factory.default_llm_script_engine()
    mock_create_client.assert_called_once()
    assert mock_create_client.call_args.kwargs["timeout"] == 120.0


@patch("engines.factory.create_client")
@patch("engines.factory.load_config")
def test_default_splitter_engine_passes_openrouter_timeout_seconds(
    mock_load_config, mock_create_client
):
    mock_load_config.return_value = {}
    with patch.dict(
        "os.environ", {"OPENROUTER_TIMEOUT_SECONDS": "120"}, clear=True
    ):
        engines_factory.default_splitter_engine()
    assert mock_create_client.call_args.kwargs["timeout"] == 120.0


@patch("engines.factory.load_config")
def test_default_engine_rejects_invalid_openrouter_timeout_seconds(
    mock_load_config,
):
    mock_load_config.return_value = {}
    with patch.dict(
        "os.environ", {"OPENROUTER_TIMEOUT_SECONDS": "bad"}, clear=True
    ):
        with pytest.raises(ValueError):
            engines_factory.default_llm_script_engine()
