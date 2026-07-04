"""Tests for registry-based extractor selection in engines and seed_gen CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import format_adapters.registry as _reg


@pytest.fixture(autouse=True)
def _reset_registry():
    saved = dict(_reg._registry)
    yield
    _reg._registry.clear()
    _reg._registry.update(saved)


def test_llm_script_engine_calls_get_extractor_with_source_path():
    from engines.llm_script import LLMScriptEngine
    engine = LLMScriptEngine(mode="2person", llm=MagicMock())
    with patch("engines.llm_script.get_extractor") as mock_get:
        mock_get.return_value = MagicMock(return_value="fake chapter text")
        try:
            engine.generate(Path("book.epub"), context=None, fiction_dir=None)
        except Exception:
            pass
        mock_get.assert_called_once_with(Path("book.epub"))


def test_get_extractor_pdf_returns_extract_pdf():
    from format_adapters import get_extractor
    from podcast_script_generator.llm.extract_pdf import extract_pdf
    assert get_extractor(".pdf") is extract_pdf


def test_get_extractor_epub_returns_extract_epub():
    from format_adapters import get_extractor
    from format_adapters.epub import extract_epub
    assert get_extractor(".epub") is extract_epub


def test_llm_script_engine_unsupported_format_propagates():
    from format_adapters.registry import UnsupportedFormatError
    from engines.llm_script import LLMScriptEngine
    engine = LLMScriptEngine(mode="2person", llm=MagicMock())
    with pytest.raises(UnsupportedFormatError):
        engine.generate(Path("book.docx"), context=None, fiction_dir=None)


def test_seed_gen_cli_uses_get_extractor():
    import ast
    import pathlib
    source = pathlib.Path(__file__).parent.parent / "fiction" / "seed_gen" / "cli.py"
    tree = ast.parse(source.read_text())
    imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert any(
        n.module == "format_adapters" and any(a.name == "get_extractor" for a in n.names)
        for n in imports
    )
    assert not any("extract_pdf" in [a.name for a in n.names] for n in imports)
