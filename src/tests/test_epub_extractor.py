"""Tests for format_adapters.epub — extract_epub and extractor-only registration."""

from pathlib import Path

import pytest

import format_adapters.registry as _reg
from format_adapters.registry import UnsupportedFormatError


@pytest.fixture(autouse=True)
def _clean_and_register_epub():
    saved = dict(_reg._registry)
    _reg._registry.clear()
    from format_adapters.epub import extract_epub
    _reg.register_adapters(".epub", extract_epub, None)
    yield
    _reg._registry.clear()
    _reg._registry.update(saved)


def test_extract_epub_raises_file_not_found():
    from format_adapters.epub import extract_epub
    with pytest.raises(FileNotFoundError):
        extract_epub(Path("/tmp/does_not_exist.epub"))


def test_extract_epub_returns_nonempty_string(sample_epub):
    from format_adapters.epub import extract_epub
    result = extract_epub(sample_epub)
    assert isinstance(result, str)
    assert len(result) > 0


def test_extract_epub_no_html_tags(sample_epub):
    from format_adapters.epub import extract_epub
    result = extract_epub(sample_epub)
    assert "<html" not in result
    assert "<body" not in result
    assert "<p" not in result


def test_get_extractor_returns_extract_epub():
    from format_adapters import get_extractor
    from format_adapters.epub import extract_epub
    assert get_extractor(".epub") is extract_epub


def test_epub_in_registered_extensions():
    from format_adapters import registered_extensions
    assert ".epub" in registered_extensions()


def test_get_splitter_epub_raises_unsupported():
    from format_adapters import get_splitter
    with pytest.raises(UnsupportedFormatError):
        get_splitter(".epub")


def test_case_insensitive_epub_path_lookup():
    from format_adapters import get_extractor
    from format_adapters.epub import extract_epub
    assert get_extractor(Path("book.EPUB")) is extract_epub
