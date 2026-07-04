from format_adapters.registry import (
    register_adapters,
    get_extractor,
    get_splitter,
    registered_extensions,
    UnsupportedFormatError,
)

import format_adapters.pdf   # noqa: F401  — registers .pdf adapter
import format_adapters.epub  # noqa: F401  — registers .epub extractor

__all__ = [
    "register_adapters",
    "get_extractor",
    "get_splitter",
    "registered_extensions",
    "UnsupportedFormatError",
]
