"""Tests for generate_book_podcast — format-agnostic splitter selection."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from endpoints.podcast import generate_book_podcast
from settings import PodcastSettings


@pytest.fixture
def settings(tmp_path):
    return PodcastSettings(root=tmp_path)


def _fake_splitter(chapter_glob: str = "*.pdf"):
    engine = MagicMock()
    engine.chapter_glob = chapter_glob
    engine.split.return_value = []
    return engine


def _fake_script_engine():
    engine = MagicMock()
    engine.generate.return_value = "HOST1: Hello\nHOST2: World"
    return engine


def test_pdf_path_calls_default_splitter_engine_with_path(tmp_path, settings):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = Path(f.name)
    try:
        splitter = _fake_splitter("*.pdf")
        with patch("engines.factory.default_splitter_engine", return_value=splitter) as mock_factory:
            generate_book_podcast(
                book_path=pdf_path,
                splitter_engine=None,
                settings=settings,
                skip_audio=True,
                slice_only=True,
            )
            mock_factory.assert_called_once_with(pdf_path.resolve())
    finally:
        pdf_path.unlink(missing_ok=True)


def test_epub_path_calls_default_splitter_engine_with_path(tmp_path, settings):
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        epub_path = Path(f.name)
    try:
        splitter = _fake_splitter("chapter_*.txt")
        with patch("engines.factory.default_splitter_engine", return_value=splitter) as mock_factory:
            generate_book_podcast(
                book_path=epub_path,
                splitter_engine=None,
                settings=settings,
                skip_audio=True,
                slice_only=True,
            )
            mock_factory.assert_called_once_with(epub_path.resolve())
    finally:
        epub_path.unlink(missing_ok=True)


def test_chapter_output_written_for_injected_splitter(tmp_path, settings):
    chapters_dir = tmp_path / "chapters"
    chapters_dir.mkdir()
    ch1 = chapters_dir / "chapter_001.txt"
    ch1.write_text("content")

    splitter = _fake_splitter("chapter_*.txt")
    script_engine = _fake_script_engine()

    results = generate_book_podcast(
        chapters_dir=chapters_dir,
        splitter_engine=splitter,
        script_engine=script_engine,
        settings=settings,
        skip_audio=True,
    )
    assert len(results) >= 1


def test_unsupported_format_propagates(tmp_path, settings):
    from format_adapters.registry import UnsupportedFormatError
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        docx_path = Path(f.name)
    try:
        with pytest.raises(UnsupportedFormatError):
            generate_book_podcast(
                book_path=docx_path,
                settings=settings,
                skip_audio=True,
            )
    finally:
        docx_path.unlink(missing_ok=True)
