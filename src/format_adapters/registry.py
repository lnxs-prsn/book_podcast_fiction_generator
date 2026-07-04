from __future__ import annotations

from pathlib import Path
from typing import Callable


class UnsupportedFormatError(Exception):
    pass


_registry: dict[str, dict] = {}


def register_adapters(
    extension: str,
    extractor: Callable,
    splitter: type | None,
) -> None:
    _registry[extension.lower()] = {"extractor": extractor, "splitter": splitter}


def _normalize_ext(path_or_ext: str | Path) -> str:
    s = str(path_or_ext)
    if "." in Path(s).name:
        return Path(s).suffix.lower()
    return s.lower() if s.startswith(".") else s.lower()


def get_extractor(path_or_ext: str | Path) -> Callable:
    ext = Path(str(path_or_ext)).suffix.lower() if Path(str(path_or_ext)).suffix else str(path_or_ext).lower()
    entry = _registry.get(ext)
    if entry is None:
        raise UnsupportedFormatError(f"No adapter registered for extension: {ext!r}")
    return entry["extractor"]


def get_splitter(path_or_ext: str | Path) -> type:
    ext = Path(str(path_or_ext)).suffix.lower() if Path(str(path_or_ext)).suffix else str(path_or_ext).lower()
    entry = _registry.get(ext)
    if entry is None:
        raise UnsupportedFormatError(f"No adapter registered for extension: {ext!r}")
    splitter = entry["splitter"]
    if splitter is None:
        raise UnsupportedFormatError(f"No splitter registered for extension: {ext!r} (extractor-only)")
    return splitter


def registered_extensions() -> list[str]:
    return sorted(_registry.keys())
