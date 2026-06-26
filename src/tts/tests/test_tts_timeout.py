"""Tests for TTS polling deadline (TTSTimeoutError) in cli.py and recover.py."""

import os
from unittest.mock import MagicMock, patch

import pytest

from podcast_script_generator.llm.exceptions import TTSTimeoutError
from tts.cli import send_to_api
from tts.recover import poll_and_download


class _FakeClock:
    """Deterministic monotonic clock for timeout tests."""

    def __init__(self, start: float = 1000.0):
        self._now = start

    def advance(self, seconds: float) -> None:
        self._now += seconds

    def __call__(self) -> float:
        return self._now


def _fake_client_factory() -> MagicMock:
    """Return a mock WaveSpeed client that never completes."""
    client = MagicMock()
    client._submit.return_value = ("req-123", None)
    client._get_result.return_value = {"data": {"status": "processing"}}
    return client


def _build_fake_sleep(fake_clock: _FakeClock):
    """Return a fake ``time.sleep`` that advances the deterministic clock."""

    def fake_sleep(seconds: float) -> None:
        fake_clock.advance(seconds)

    return fake_sleep


@patch("tts.cli.wavespeed.Client", return_value=_fake_client_factory())
@patch("tts.cli.time.sleep")
@patch("tts.cli.time.monotonic")
def test_send_to_api_raises_timeout_when_deadline_exceeded(
    mock_monotonic, mock_sleep, _mock_client
):
    """Advancing time.monotonic past the deadline raises TTSTimeoutError."""
    clock = _FakeClock()
    mock_monotonic.side_effect = clock
    mock_sleep.side_effect = _build_fake_sleep(clock)

    with pytest.raises(TTSTimeoutError) as exc_info:
        send_to_api(
            {"prompt": "hello"},
            api_key="test-key",
            output_folder=None,
            max_wait_seconds=15,
        )

    assert "max_wait_seconds=15" in str(exc_info.value)


@patch("tts.recover.wavespeed.Client", return_value=_fake_client_factory())
@patch("tts.recover.time.sleep")
@patch("tts.recover.time.monotonic")
def test_poll_and_download_raises_timeout_when_deadline_exceeded(
    mock_monotonic, mock_sleep, _mock_client
):
    """Recovery polling also raises TTSTimeoutError when the deadline is hit."""
    clock = _FakeClock()
    mock_monotonic.side_effect = clock
    mock_sleep.side_effect = _build_fake_sleep(clock)

    with pytest.raises(TTSTimeoutError) as exc_info:
        poll_and_download(
            "req-123",
            output_folder="/tmp/tts-recover-test",
            api_key="test-key",
            max_wait_seconds=15,
        )

    assert "max_wait_seconds=15" in str(exc_info.value)


@patch("tts.cli.wavespeed.Client", return_value=_fake_client_factory())
@patch("tts.cli.time.sleep")
@patch("tts.cli.time.monotonic")
def test_send_to_api_uses_wavespeed_max_wait_seconds_env_default(
    mock_monotonic, mock_sleep, _mock_client
):
    """When max_wait_seconds is omitted, WAVESPEED_MAX_WAIT_SECONDS is honored."""
    clock = _FakeClock()
    mock_monotonic.side_effect = clock
    mock_sleep.side_effect = _build_fake_sleep(clock)

    with patch.dict(os.environ, {"WAVESPEED_MAX_WAIT_SECONDS": "7"}):
        with pytest.raises(TTSTimeoutError) as exc_info:
            send_to_api(
                {"prompt": "hello"},
                api_key="test-key",
                output_folder=None,
            )

    assert "max_wait_seconds=7" in str(exc_info.value)
