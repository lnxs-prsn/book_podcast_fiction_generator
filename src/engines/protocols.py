from typing import Protocol, runtime_checkable
from pathlib import Path


@runtime_checkable
class ScriptEngine(Protocol):
    def generate(
        self,
        pdf_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str: ...


@runtime_checkable
class AudioEngine(Protocol):
    def generate(
        self,
        script_path: Path,
        audio_dir: Path,
        *,
        mode: str = "2person",
    ) -> Path: ...


@runtime_checkable
class SplitterEngine(Protocol):
    def split(
        self,
        book_pdf: Path,
        *,
        toc_page: int | None = None,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]: ...
