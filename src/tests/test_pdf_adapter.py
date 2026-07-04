"""Tests for format_adapters.pdf — PDF adapter registration."""

from pathlib import Path

import pytest

import format_adapters.registry as _reg


@pytest.fixture(autouse=True)
def _clean_and_register():
    saved = dict(_reg._registry)
    _reg._registry.clear()
    from podcast_script_generator.llm.extract_pdf import extract_pdf
    from engines.pdf_splitter import PDFSplitterEngine
    _reg.register_adapters(".pdf", extract_pdf, PDFSplitterEngine)
    yield
    _reg._registry.clear()
    _reg._registry.update(saved)


def test_get_extractor_returns_extract_pdf():
    from format_adapters import get_extractor
    from podcast_script_generator.llm.extract_pdf import extract_pdf
    assert get_extractor(".pdf") is extract_pdf


def test_get_splitter_returns_pdf_splitter_engine():
    from format_adapters import get_splitter
    from engines.pdf_splitter import PDFSplitterEngine
    assert get_splitter(".pdf") is PDFSplitterEngine


def test_registered_extensions_includes_pdf():
    from format_adapters import registered_extensions
    assert ".pdf" in registered_extensions()


def test_case_insensitive_extractor_lookup():
    from format_adapters import get_extractor
    from podcast_script_generator.llm.extract_pdf import extract_pdf
    assert get_extractor(Path("some/book.PDF")) is extract_pdf


def test_case_insensitive_splitter_lookup():
    from format_adapters import get_splitter
    from engines.pdf_splitter import PDFSplitterEngine
    assert get_splitter(Path("some/book.PDF")) is PDFSplitterEngine


def test_extract_pdf_not_relocated():
    from podcast_script_generator.llm.extract_pdf import extract_pdf  # noqa: F401
    assert True


def test_pdf_splitter_engine_not_relocated():
    from engines.pdf_splitter import PDFSplitterEngine  # noqa: F401
    assert True
