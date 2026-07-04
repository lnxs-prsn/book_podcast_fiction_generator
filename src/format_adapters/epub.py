from __future__ import annotations

import re
from pathlib import Path

from format_adapters.registry import register_adapters
from format_adapters.epub_splitter import EPUBSplitterEngine


def extract_epub(path: str | Path) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"EPUB file not found: {path}")

    import ebooklib
    from ebooklib import epub
    from html.parser import HTMLParser

    class _TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self._parts: list[str] = []
            self._skip = False

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self._skip = True

        def handle_endtag(self, tag):
            if tag in ("script", "style"):
                self._skip = False

        def handle_data(self, data):
            if not self._skip:
                self._parts.append(data)

        def get_text(self) -> str:
            return "".join(self._parts)

    def _strip_html(html_bytes: bytes) -> str:
        parser = _TextExtractor()
        try:
            parser.feed(html_bytes.decode("utf-8", errors="replace"))
        except Exception:
            pass
        return parser.get_text()

    book = epub.read_epub(str(path), options={"ignore_ncx": False})

    spine_ids = {item_id for item_id, _ in book.spine}
    paragraphs: list[str] = []

    for item in book.get_items():
        if item.get_id() not in spine_ids:
            continue
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        raw_text = _strip_html(item.get_content())
        for line in raw_text.splitlines():
            line = line.strip()
            if line:
                paragraphs.append(line)
            elif paragraphs and paragraphs[-1] != "":
                paragraphs.append("")

    # Collapse trailing blank lines
    while paragraphs and paragraphs[-1] == "":
        paragraphs.pop()

    return "\n".join(paragraphs)


register_adapters(".epub", extract_epub, EPUBSplitterEngine)
