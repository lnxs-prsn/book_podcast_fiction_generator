"""Tests for format-aware default_splitter_engine."""

from pathlib import Path
from unittest.mock import patch

import pytest

from engines import factory as engines_factory


@patch("engines.factory.create_client")
@patch("engines.factory.load_config")
def test_pdf_path_returns_pdf_splitter_engine(mock_load_config, mock_create_client):
    from engines.pdf_splitter import PDFSplitterEngine
    mock_load_config.return_value = {}
    result = engines_factory.default_splitter_engine(Path("book.pdf"))
    assert isinstance(result, PDFSplitterEngine)


@patch("engines.factory.create_client")
@patch("engines.factory.load_config")
def test_epub_path_returns_epub_splitter_engine(mock_load_config, mock_create_client):
    from format_adapters.epub_splitter import EPUBSplitterEngine
    mock_load_config.return_value = {}
    result = engines_factory.default_splitter_engine(Path("book.epub"))
    assert isinstance(result, EPUBSplitterEngine)


def test_unsupported_format_raises():
    from format_adapters.registry import UnsupportedFormatError
    with pytest.raises(UnsupportedFormatError):
        engines_factory.default_splitter_engine(Path("book.docx"))


@patch("engines.factory.create_client")
@patch("engines.factory.load_config")
def test_case_insensitive_pdf_extension(mock_load_config, mock_create_client):
    from engines.pdf_splitter import PDFSplitterEngine
    mock_load_config.return_value = {}
    result = engines_factory.default_splitter_engine(Path("book.PDF"))
    assert isinstance(result, PDFSplitterEngine)
