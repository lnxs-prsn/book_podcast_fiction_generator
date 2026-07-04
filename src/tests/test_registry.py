"""Tests for format_adapters.registry public API."""

from pathlib import Path

import pytest

import format_adapters.registry as _reg
from format_adapters.registry import (
    UnsupportedFormatError,
    get_extractor,
    get_splitter,
    register_adapters,
    registered_extensions,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Reset registry state before each test and restore after."""
    saved = dict(_reg._registry)
    _reg._registry.clear()
    yield
    _reg._registry.clear()
    _reg._registry.update(saved)


def _make_extractor():
    def extractor(path):
        return "text"
    return extractor


class FakeSplitter:
    pass


def test_register_pair_retrievable():
    ext = _make_extractor()
    register_adapters(".pdf", ext, FakeSplitter)
    assert get_extractor(".pdf") is ext
    assert get_splitter(".pdf") is FakeSplitter


def test_extractor_only_registration():
    ext = _make_extractor()
    register_adapters(".epub", ext, None)
    assert get_extractor(".epub") is ext
    with pytest.raises(UnsupportedFormatError):
        get_splitter(".epub")


def test_get_extractor_accepts_full_path():
    ext = _make_extractor()
    register_adapters(".pdf", ext, FakeSplitter)
    assert get_extractor(Path("/some/book.pdf")) is ext


def test_get_splitter_accepts_full_path():
    ext = _make_extractor()
    register_adapters(".pdf", ext, FakeSplitter)
    assert get_splitter(Path("/some/book.pdf")) is FakeSplitter


def test_get_extractor_raises_for_unregistered():
    with pytest.raises(UnsupportedFormatError):
        get_extractor(".docx")


def test_get_splitter_raises_for_unregistered():
    with pytest.raises(UnsupportedFormatError):
        get_splitter(".docx")


def test_registered_extensions_sorted():
    register_adapters(".pdf", _make_extractor(), None)
    register_adapters(".epub", _make_extractor(), None)
    exts = registered_extensions()
    assert exts == sorted(exts)


def test_registered_extensions_includes_extractor_only():
    ext = _make_extractor()
    register_adapters(".epub", ext, None)
    assert ".epub" in registered_extensions()


def test_register_twice_overwrites():
    ext1 = _make_extractor()
    ext2 = _make_extractor()
    register_adapters(".pdf", ext1, None)
    register_adapters(".pdf", ext2, None)
    assert get_extractor(".pdf") is ext2


def test_case_insensitive_registration_and_lookup():
    ext = _make_extractor()
    register_adapters(".PDF", ext, FakeSplitter)
    assert get_extractor(".pdf") is ext
    assert get_splitter(".pdf") is FakeSplitter


def test_case_insensitive_path_lookup():
    ext = _make_extractor()
    register_adapters(".pdf", ext, FakeSplitter)
    assert get_extractor(Path("/some/book.PDF")) is ext
    assert get_splitter(Path("/some/book.PDF")) is FakeSplitter
