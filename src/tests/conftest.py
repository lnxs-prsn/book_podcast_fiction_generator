"""Shared test fixtures."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def sample_epub(tmp_path_factory) -> Path:
    """Create a minimal valid EPUB file for use in tests."""
    import ebooklib
    from ebooklib import epub

    book = epub.EpubBook()
    book.set_title("Test Book")
    book.set_language("en")
    book.add_author("Test Author")

    ch1 = epub.EpubHtml(title="Chapter 1", file_name="chap1.xhtml", lang="en")
    ch1.content = b"<html><body><h1>Chapter 1</h1><p>This is chapter one content.</p></body></html>"

    ch2 = epub.EpubHtml(title="Chapter 2", file_name="chap2.xhtml", lang="en")
    ch2.content = b"<html><body><h1>Chapter 2</h1><p>This is chapter two content.</p></body></html>"

    book.add_item(ch1)
    book.add_item(ch2)
    book.toc = (epub.Link("chap1.xhtml", "Chapter 1", "chap1"), epub.Link("chap2.xhtml", "Chapter 2", "chap2"))
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", ch1, ch2]

    epub_path = tmp_path_factory.mktemp("epub") / "test.epub"
    epub.write_epub(str(epub_path), book)
    return epub_path
