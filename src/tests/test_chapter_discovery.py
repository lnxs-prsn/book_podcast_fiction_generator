"""Tests for chapter_glob-driven discovery in generate_book_podcast."""

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from settings import PodcastSettings


def test_pdf_splitter_engine_chapter_glob():
    from engines.pdf_splitter import PDFSplitterEngine
    engine = PDFSplitterEngine.__new__(PDFSplitterEngine)
    assert engine.chapter_glob == "*.pdf"


def test_epub_splitter_engine_chapter_glob():
    from format_adapters.epub_splitter import EPUBSplitterEngine
    engine = EPUBSplitterEngine.__new__(EPUBSplitterEngine)
    assert engine.chapter_glob == "chapter_*.txt"


def test_generate_book_podcast_pdf_discovers_pdf_files(tmp_path):
    from endpoints.podcast import generate_book_podcast

    chapters_dir = tmp_path / "chapters"
    chapters_dir.mkdir()
    (chapters_dir / "chapter_001.pdf").write_bytes(b"%PDF-1.4")
    (chapters_dir / "chapter_001.txt").write_text("ignored")

    pdf_splitter = MagicMock()
    pdf_splitter.chapter_glob = "*.pdf"

    script_engine = MagicMock()
    script_engine.generate.return_value = "HOST1: Hello\nHOST2: World"

    settings = PodcastSettings(root=tmp_path)
    results = generate_book_podcast(
        chapters_dir=chapters_dir,
        splitter_engine=pdf_splitter,
        script_engine=script_engine,
        settings=settings,
        skip_audio=True,
    )
    assert len(results) == 1


def test_generate_book_podcast_epub_discovers_txt_files(tmp_path):
    from endpoints.podcast import generate_book_podcast

    chapters_dir = tmp_path / "chapters"
    chapters_dir.mkdir()
    (chapters_dir / "chapter_001.txt").write_text("Chapter one content")
    (chapters_dir / "chapter_001.pdf").write_bytes(b"%PDF-1.4")

    epub_splitter = MagicMock()
    epub_splitter.chapter_glob = "chapter_*.txt"

    script_engine = MagicMock()
    script_engine.generate.return_value = "HOST1: Hello\nHOST2: World"

    settings = PodcastSettings(root=tmp_path)
    results = generate_book_podcast(
        chapters_dir=chapters_dir,
        splitter_engine=epub_splitter,
        script_engine=script_engine,
        settings=settings,
        skip_audio=True,
    )
    assert len(results) == 1


def test_no_extension_literal_in_generate_book_podcast_glob_args():
    """No .pdf or .epub string literal passed as argument to .glob() in generate_book_podcast."""
    import pathlib
    source = (pathlib.Path(__file__).parent.parent / "endpoints" / "podcast.py").read_text()
    tree = ast.parse(source)
    func = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "generate_book_podcast"
    )
    ext_literals = {".pdf", ".epub", ".PDF", ".EPUB"}
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "glob":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        for ext in ext_literals:
                            assert ext not in arg.value, (
                                f"Extension literal {ext!r} found in glob arg: {arg.value!r}"
                            )
