"""Tests for generate_chapter_podcast — format-agnostic behavior."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from endpoints.podcast import generate_chapter_podcast
from settings import PodcastSettings


@pytest.fixture
def settings(tmp_path):
    return PodcastSettings(root=tmp_path)


def _fake_script_engine(script_text: str = "HOST1: Hello\nHOST2: World"):
    engine = MagicMock()
    engine.generate.return_value = script_text
    return engine


def test_pdf_source_writes_script(tmp_path, settings):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = Path(f.name)
    try:
        engine = _fake_script_engine()
        result = generate_chapter_podcast(
            source_path=pdf_path,
            script_engine=engine,
            settings=settings,
            skip_audio=True,
        )
        assert result.ok
        assert result.script_path is not None
        assert result.script_path.exists()
    finally:
        pdf_path.unlink(missing_ok=True)


def test_epub_source_writes_script(tmp_path, settings):
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        epub_path = Path(f.name)
    try:
        engine = _fake_script_engine()
        result = generate_chapter_podcast(
            source_path=epub_path,
            script_engine=engine,
            settings=settings,
            skip_audio=True,
        )
        assert result.ok
        assert result.script_path is not None
        assert result.script_path.exists()
    finally:
        epub_path.unlink(missing_ok=True)


def test_missing_source_returns_file_not_found_error(settings):
    result = generate_chapter_podcast(
        source_path=Path("/tmp/does_not_exist_xyz.epub"),
        settings=settings,
        skip_audio=True,
    )
    assert not result.ok
    assert isinstance(result.error, FileNotFoundError)
    assert "Source file not found" in str(result.error)


def test_script_engine_receives_source_path(tmp_path, settings):
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        epub_path = Path(f.name)
    try:
        engine = _fake_script_engine()
        generate_chapter_podcast(
            source_path=epub_path,
            script_engine=engine,
            settings=settings,
            skip_audio=True,
        )
        call_args = engine.generate.call_args
        passed_path = call_args.args[0] if call_args.args else call_args.kwargs.get("source_path")
        assert passed_path == epub_path.resolve()
    finally:
        epub_path.unlink(missing_ok=True)
