"""Smoke tests for the TTS polling modules."""

import inspect

from tts.cli import send_to_api
from tts.recover import poll_and_download


def test_send_to_api_accepts_max_wait_seconds():
    """The cli.send_to_api polling loop accepts a deadline parameter."""
    sig = inspect.signature(send_to_api)
    assert "max_wait_seconds" in sig.parameters


def test_poll_and_download_accepts_max_wait_seconds():
    """The recover.poll_and_download polling loop accepts a deadline parameter."""
    sig = inspect.signature(poll_and_download)
    assert "max_wait_seconds" in sig.parameters
