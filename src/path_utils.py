"""Path resolution and validation helpers for the harness project.

All path validation logic lives here so other modules can resolve project
paths consistently without duplicating escape checks or root lookups.
"""

from __future__ import annotations

import os
from pathlib import Path


__all__ = [
    "resolve_data_root",
    "resolve_output_path",
    "resolve_input_path",
    "guard_path_escape",
]


def resolve_data_root(
    env_var: str = "HARNESS_ROOT",
    fallback: Path | str | None = None,
) -> Path:
    """Return the absolute project/data root directory.

    Resolution order:
        1. ``os.environ[env_var]`` if present.
        2. ``fallback`` if provided.
        3. The directory containing this module (``src/``).

    Args:
        env_var: Name of the environment variable that may override the root.
        fallback: Optional root to use when the environment variable is unset.

    Returns:
        Absolute, resolved :class:`pathlib.Path` pointing to the project root.
    """
    if env_var in os.environ:
        return Path(os.environ[env_var]).expanduser().resolve()
    if fallback is not None:
        return Path(fallback).expanduser().resolve()
    return Path(__file__).parent.resolve()


def guard_path_escape(
    path: Path | str,
    root: Path | str,
    *,
    message: str | None = None,
) -> None:
    """Raise ``ValueError`` if *path* resolves outside *root*.

    Both paths are fully resolved before comparison. Symbolic links that point
    outside *root* are therefore also rejected.

    Args:
        path: Path to validate.
        root: Root directory the path must stay inside.
        message: Optional override for the exception message.

    Raises:
        ValueError: If the resolved path is not contained within ``root``.
    """
    resolved_path = Path(path).expanduser().resolve()
    resolved_root = Path(root).expanduser().resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            message
            or f"Path escapes root: {resolved_path} is not under {resolved_root}"
        ) from exc


def _resolve_under_root(
    path: Path | str,
    root: Path | str | None,
    *,
    allow_escape: bool,
) -> Path:
    """Resolve *path* against *root* and optionally enforce containment."""
    if root is None:
        root = resolve_data_root()
    resolved_root = Path(root).expanduser().resolve()
    candidate = Path(path)
    if candidate.is_absolute():
        resolved = candidate.expanduser().resolve()
    else:
        resolved = (resolved_root / candidate).resolve()
    if not allow_escape:
        guard_path_escape(resolved, resolved_root)
    return resolved


def resolve_output_path(
    path: Path | str,
    root: Path | str | None = None,
    *,
    allow_escape: bool = False,
) -> Path:
    """Resolve an output path relative to the project root.

    Relative paths are anchored to ``root`` (default: ``resolve_data_root()``).
    Absolute paths are accepted as-is but still checked for containment unless
    ``allow_escape`` is ``True``.

    Args:
        path: Output path (relative or absolute).
        root: Optional root directory. Defaults to ``resolve_data_root()``.
        allow_escape: If ``True``, skip the containment check.

    Returns:
        Absolute, resolved :class:`pathlib.Path` for the output location.

    Raises:
        ValueError: If the resolved path escapes ``root`` (and ``allow_escape``
            is ``False``).
    """
    return _resolve_under_root(path, root, allow_escape=allow_escape)


def resolve_input_path(
    path: Path | str,
    root: Path | str | None = None,
    *,
    must_exist: bool = True,
    allow_escape: bool = False,
) -> Path:
    """Resolve an input path relative to the project root.

    Relative paths are anchored to ``root`` (default: ``resolve_data_root()``).
    Absolute paths are accepted as-is but still checked for containment unless
    ``allow_escape`` is ``True``.

    Args:
        path: Input path (relative or absolute).
        root: Optional root directory. Defaults to ``resolve_data_root()``.
        must_exist: If ``True`` (default), raise ``FileNotFoundError`` when the
            resolved path does not exist.
        allow_escape: If ``True``, skip the containment check.

    Returns:
        Absolute, resolved :class:`pathlib.Path` for the input location.

    Raises:
        FileNotFoundError: If ``must_exist`` is ``True`` and the path is missing.
        ValueError: If the resolved path escapes ``root`` (and ``allow_escape``
            is ``False``).
    """
    resolved = _resolve_under_root(path, root, allow_escape=allow_escape)
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Input path does not exist: {resolved}")
    return resolved
