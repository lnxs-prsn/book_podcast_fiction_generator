"""Tests for format_adapters.epub_splitter — EPUBSplitterEngine."""

import re
from pathlib import Path

import pytest

import format_adapters.registry as _reg
from format_adapters.registry import UnsupportedFormatError


@pytest.fixture(autouse=True)
def _clean_and_register_epub_full():
    saved = dict(_reg._registry)
    _reg._registry.clear()
    from format_adapters.epub import extract_epub
    from format_adapters.epub_splitter import EPUBSplitterEngine
    _reg.register_adapters(".epub", extract_epub, EPUBSplitterEngine)
    yield
    _reg._registry.clear()
    _reg._registry.update(saved)


def test_split_raises_file_not_found(tmp_path):
    from format_adapters.epub_splitter import EPUBSplitterEngine
    engine = EPUBSplitterEngine()
    with pytest.raises(FileNotFoundError):
        engine.split(
            Path("/tmp/does_not_exist.epub"),
            toc_page=None,
            output_dir=tmp_path / "out",
            no_ocr=False,
        )


def test_split_writes_chapter_files(sample_epub, tmp_path):
    from format_adapters.epub_splitter import EPUBSplitterEngine
    engine = EPUBSplitterEngine()
    out = tmp_path / "chapters"
    result = engine.split(sample_epub, toc_page=None, output_dir=out, no_ocr=False)
    assert len(result) >= 1
    for p in result:
        assert p.exists()


def test_output_filenames_padded(sample_epub, tmp_path):
    from format_adapters.epub_splitter import EPUBSplitterEngine
    engine = EPUBSplitterEngine()
    out = tmp_path / "chapters"
    result = engine.split(sample_epub, toc_page=None, output_dir=out, no_ocr=False)
    for p in result:
        assert re.match(r"chapter_\d{3}\.txt$", p.name), f"Unexpected filename: {p.name}"


def test_toc_page_and_no_ocr_accepted(sample_epub, tmp_path):
    from format_adapters.epub_splitter import EPUBSplitterEngine
    engine = EPUBSplitterEngine()
    out = tmp_path / "chapters"
    # Should not raise
    engine.split(sample_epub, toc_page=5, output_dir=out, no_ocr=True)


def test_get_splitter_returns_epub_splitter_engine():
    from format_adapters import get_splitter
    from format_adapters.epub_splitter import EPUBSplitterEngine
    assert get_splitter(".epub") is EPUBSplitterEngine


def test_get_extractor_still_returns_extract_epub():
    from format_adapters import get_extractor
    from format_adapters.epub import extract_epub
    assert get_extractor(".epub") is extract_epub


def test_get_splitter_epub_does_not_raise():
    from format_adapters import get_splitter
    from format_adapters.epub_splitter import EPUBSplitterEngine
    result = get_splitter(".epub")
    assert result is EPUBSplitterEngine
