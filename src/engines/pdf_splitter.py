from __future__ import annotations

from pathlib import Path

from engines.protocols import SplitterEngine
from llm.protocol import LLMClient


class PDFSplitterEngine(SplitterEngine):
    """Adapter for `slicer.pdf_splitter.run_splitter`.

    `run_splitter` result dict shape:
        {"success": bool, "files": [{"output_path": str, ...}], ...}
    """

    chapter_glob: str = "*.pdf"

    def __init__(self, *, llm: LLMClient) -> None:
        self.llm = llm

    def split(
        self,
        book_path: Path,
        *,
        toc_page: int | None = None,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]:
        from slicer.pdf_splitter import run_splitter

        output_dir.mkdir(parents=True, exist_ok=True)
        kwargs = {}
        if toc_page is not None:
            kwargs["toc_page"] = toc_page
        result = run_splitter(
            input_path=str(book_path),
            output_dir=str(output_dir),
            prefix="chapter",
            chapters_only=True,
            no_ocr=no_ocr,
            llm=self.llm,
            **kwargs,
        )
        if not result.get("success"):
            raise RuntimeError(f"slicer failed: {result.get('error', 'unknown')}")
        return [Path(f["output_path"]) for f in result.get("files", [])]
