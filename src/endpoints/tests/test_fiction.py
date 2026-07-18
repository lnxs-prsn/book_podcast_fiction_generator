"""Tests for the fiction endpoint env-override config merge.

Regression tests for Error 3: BOOKGEN_LLM_MODEL env var not reaching the
config dict passed to run_session. The fix is in endpoints/fiction.py —
env overrides are merged into config before the session is started, so
the config dict is the single resolved source of truth for the whole session.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_pipeline.session import SessionResult


_FILE_MODEL = "file/model"
_FILE_URL = "https://file-url/v1/chat/completions"

_MINIMAL_RAW_CONFIG = {
    "model": _FILE_MODEL,
    "api_url": _FILE_URL,
    "max_retries": 2,
    "retry_backoff_seconds": [2, 8],
    "retry_jitter_seconds_max": 0.0,
}


def _fake_result() -> SessionResult:
    return SessionResult(
        chapters_written=0,
        final_chapter_number=1,
        cost_usd=0.0,
        completed=False,
        state_path=Path(".pipeline_state.json"),
    )


@pytest.fixture
def call_endpoint():
    """Factory fixture: invoke run_novel_session with all external I/O mocked.

    Returns a callable that accepts an optional ``client`` kwarg and returns
    ``(config_seen_by_run_session, create_transport_mock)``.
    """
    from endpoints.fiction import run_novel_session

    def _call(*, client=None):
        captured = {}

        def fake_run_session(config, transport, timeout, **kwargs):
            captured["config"] = config
            return _fake_result()

        with (
            patch("endpoints.fiction.load_config", return_value=dict(_MINIMAL_RAW_CONFIG)),
            patch("endpoints.fiction.create_transport", return_value=MagicMock()) as mock_create,
            patch("endpoints.fiction.run_session", side_effect=fake_run_session),
        ):
            run_novel_session("fake.toml", client=client, auto_approve=True)

        return captured["config"], mock_create

    return _call


class TestEnvModelOverride:
    """BOOKGEN_LLM_MODEL must override config.toml's model everywhere the
    session reads it — both the config dict passed to run_session and the
    kwargs used to construct the transport."""

    def test_model_env_wins_over_file(self, call_endpoint, monkeypatch):
        monkeypatch.setenv("BOOKGEN_LLM_MODEL", "env/model")
        config, _ = call_endpoint()
        assert config["model"] == "env/model"

    def test_no_env_var_keeps_file_model(self, call_endpoint, monkeypatch):
        monkeypatch.delenv("BOOKGEN_LLM_MODEL", raising=False)
        config, _ = call_endpoint()
        assert config["model"] == _FILE_MODEL

    def test_api_url_env_wins_over_file(self, call_endpoint, monkeypatch):
        monkeypatch.setenv("BOOKGEN_LLM_API_URL", "https://env-url/v1/chat/completions")
        config, _ = call_endpoint()
        assert config["api_url"] == "https://env-url/v1/chat/completions"

    def test_no_api_url_env_keeps_file_url(self, call_endpoint, monkeypatch):
        monkeypatch.delenv("BOOKGEN_LLM_API_URL", raising=False)
        config, _ = call_endpoint()
        assert config["api_url"] == _FILE_URL

    def test_env_key_absent_from_raw_config_not_injected(self, call_endpoint, monkeypatch):
        # BOOKGEN_LLM_API_KEY has no corresponding key in the raw config dict,
        # so it must not appear in the config that run_session receives.
        monkeypatch.setenv("BOOKGEN_LLM_API_KEY", "sk-env-key")
        config, _ = call_endpoint()
        assert "api_key" not in config

    def test_transport_receives_env_model(self, call_endpoint, monkeypatch):
        monkeypatch.setenv("BOOKGEN_LLM_MODEL", "env/model")
        _, mock_create = call_endpoint()
        assert mock_create.call_args.kwargs["model"] == "env/model"

    def test_injected_client_skips_transport_but_env_still_reaches_config(
        self, call_endpoint, monkeypatch
    ):
        # When a client is provided externally, create_transport is not called,
        # but the env override must still land in the config dict that
        # run_session receives (session reads model from config, not client).
        monkeypatch.setenv("BOOKGEN_LLM_MODEL", "env/model")
        config, mock_create = call_endpoint(client=MagicMock())
        assert config["model"] == "env/model"
        mock_create.assert_not_called()
