from __future__ import annotations

from pathlib import Path

from engines.protocols import SplitterEngine


class EPUBSplitterEngine(SplitterEngine):
    """Splits an EPUB into per-chapter .txt files."""

    chapter_glob: str = "chapter_*.txt"

    def __init__(self, *, llm=None) -> None:
        pass

    def split(
        self,
        book_path: Path,
        *,
        toc_page: int | None = None,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]:
        if not book_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {book_path}")

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
            raw = parser.get_text()
            lines = []
            for line in raw.splitlines():
                line = line.strip()
                if line:
                    lines.append(line)
                elif lines and lines[-1] != "":
                    lines.append("")
            while lines and lines[-1] == "":
                lines.pop()
            return "\n".join(lines)

        book = epub.read_epub(str(book_path), options={"ignore_ncx": False})
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build ordered list of spine items (documents only)
        spine_ids = [item_id for item_id, _ in book.spine]
        id_to_item = {item.get_id(): item for item in book.get_items()}

        spine_docs = []
        for sid in spine_ids:
            item = id_to_item.get(sid)
            if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                spine_docs.append(item)

        # Try to get chapter boundaries from TOC
        toc_hrefs: list[str] = []
        for entry in book.toc:
            if hasattr(entry, "href"):
                toc_hrefs.append(entry.href.split("#")[0])
            elif isinstance(entry, tuple) and hasattr(entry[0], "href"):
                toc_hrefs.append(entry[0].href.split("#")[0])

        if toc_hrefs:
            # Group spine docs by chapter using TOC boundaries
            toc_file_names = []
            for href in toc_hrefs:
                base = href.split("/")[-1]
                toc_file_names.append(base)

            chapters: list[list] = []
            current: list = []
            for item in spine_docs:
                fname = item.file_name.split("/")[-1]
                if fname in toc_file_names and current:
                    chapters.append(current)
                    current = [item]
                else:
                    current.append(item)
            if current:
                chapters.append(current)
        else:
            # Each spine item is its own chapter
            chapters = [[item] for item in spine_docs]

        written: list[Path] = []
        for idx, chapter_items in enumerate(chapters, start=1):
            text_parts = []
            for item in chapter_items:
                text = _strip_html(item.get_content())
                if text:
                    text_parts.append(text)
            text = "\n\n".join(text_parts)
            if not text.strip():
                continue
            out_file = output_dir / f"chapter_{idx:03d}.txt"
            out_file.write_text(text, encoding="utf-8")
            written.append(out_file)

        return written
