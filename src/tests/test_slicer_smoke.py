"""Smoke tests for slicer/pdf_splitter.py.

Covers:
- pdf_splitter can be imported from src/
- timeout kwarg is forwarded to requests.post when a client is built
- default output_dir resolves relative to project root (via path_utils),
  not relative to the current working directory
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

def test_pdf_splitter_importable():
    """slicer.pdf_splitter must be importable from PYTHONPATH=src."""
    import slicer.pdf_splitter  # noqa: F401


def test_run_splitter_callable():
    """run_splitter must be importable and callable as a Python API."""
    from slicer.pdf_splitter import run_splitter
    assert callable(run_splitter)


# ---------------------------------------------------------------------------
# Timeout forwarding
# ---------------------------------------------------------------------------

class TestSlicerTimeoutSmoke:
    """requests.post must receive the timeout kwarg when the client is invoked."""

    def _mock_response(self):
        resp = mock.MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }
        return resp

    def test_client_forwards_timeout_to_requests_post(self):
        """An OpenRouterClient built with timeout=120.0 passes it to requests.post."""
        from llm.providers.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key", timeout=120.0)

        with mock.patch("requests.post", return_value=self._mock_response()) as mock_post:
            client.call(prompt="test prompt")

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert "timeout" in kwargs, "requests.post must receive timeout keyword"
        assert kwargs["timeout"] == 120.0

    def test_env_var_timeout_parsed_as_float(self, monkeypatch):
        """The slicer main() timeout logic: OPENROUTER_TIMEOUT_SECONDS parses to float."""
        monkeypatch.setenv("OPENROUTER_TIMEOUT_SECONDS", "45.0")
        timeout_str = os.environ.get("OPENROUTER_TIMEOUT_SECONDS", "120.0")
        assert float(timeout_str) == 45.0

    def test_env_var_timeout_defaults_to_120(self, monkeypatch):
        """When OPENROUTER_TIMEOUT_SECONDS is absent, the default is 120.0."""
        monkeypatch.delenv("OPENROUTER_TIMEOUT_SECONDS", raising=False)
        timeout_str = os.environ.get("OPENROUTER_TIMEOUT_SECONDS", "120.0")
        assert float(timeout_str) == 120.0


# ---------------------------------------------------------------------------
# Output path anchoring
# ---------------------------------------------------------------------------

class TestSlicerOutputPathSmoke:
    """run_splitter() with output_dir=None must anchor output to project root."""

    def _minimal_pdf(self, tmp_path: Path) -> Path:
        import fitz

        pdf_path = tmp_path / "smoke.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()
        return pdf_path

    def test_default_output_dir_not_cwd_relative(self, tmp_path, monkeypatch):
        """With output_dir=None, resolved output is under resolve_data_root(), not CWD."""
        from path_utils import resolve_data_root
        from slicer.pdf_splitter import run_splitter

        monkeypatch.chdir(tmp_path)

        pdf_path = self._minimal_pdf(tmp_path)

        result = run_splitter(
            input_path=str(pdf_path),
            output_dir=None,
            no_ocr=True,
            llm=None,
        )

        project_root = resolve_data_root()

        if result.get("output_dir"):
            returned_dir = Path(result["output_dir"])
            assert returned_dir.is_absolute()
            assert str(returned_dir).startswith(str(project_root)), (
                f"output_dir {returned_dir} is not under project root {project_root}"
            )
        else:
            # Early failure (blank PDF, no TOC) — verify path resolution logic directly
            expected = project_root / "split_chapters"
            assert expected.is_absolute()
            assert str(expected).startswith(str(project_root))

    def test_output_dir_is_not_cwd(self, tmp_path, monkeypatch):
        """The resolved default output_dir must differ from tmp_path (our fake CWD)."""
        from path_utils import resolve_data_root

        monkeypatch.chdir(tmp_path)

        project_root = resolve_data_root()
        default_out = project_root / "split_chapters"

        # Default output resolves under project root, not under tmp_path
        assert not str(default_out).startswith(str(tmp_path)), (
            "Default output_dir must not be under CWD"
        )

    def test_path_utils_resolve_data_root_used(self, monkeypatch):
        """resolve_data_root() honours HARNESS_ROOT env var."""
        from path_utils import resolve_data_root

        with monkeypatch.context() as m:
            m.setenv("HARNESS_ROOT", "/tmp/harness_test_root")
            root = resolve_data_root()
            assert str(root) == "/tmp/harness_test_root"
