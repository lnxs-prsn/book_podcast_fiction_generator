"""Tests for podcast_script_generator.llm.call_api timeout handling."""

from unittest.mock import MagicMock

from podcast_script_generator.llm.call_api import call_api


def test_call_api_passes_timeout_to_llm():
    llm = MagicMock()
    llm.call.return_value = "response"
    result = call_api("pdf text", "prompt text", llm)
    llm.call.assert_called_once_with(
        prompt="prompt text\n\n---\n\npdf text", timeout=120.0
    )
    assert result == "response"


def test_call_api_passes_timeout_without_pdf_text():
    llm = MagicMock()
    llm.call.return_value = "response"
    result = call_api("", "prompt text", llm)
    llm.call.assert_called_once_with(prompt="prompt text", timeout=120.0)
    assert result == "response"
