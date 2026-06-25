"""Pipeline state file + resume detection (v2 patch).

`.pipeline_state.json` schema:
  {
    "last_chapter_promoted": int,
    "last_chapter_living_doc_updated": int,
    "last_chapter_drafted": int,        # H7: optional, present when known
    "updated_at": "ISO-8601"
  }

H7: `last_chapter_drafted` is optional in the read schema; older files
without it are accepted. write_state accepts it as an optional kwarg and
omits it from the file if not provided.

I9: canonical chapter regex is configurable via
`canonical_chapter_regex` in config; default kept for backward compat
when callers don't pass a config.

It is the cross-file consistency oracle on resume. We compare it against
filesystem reality (canonical chapters present in output_dir) to detect
interrupts in the middle of the promote/update cycle.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .exceptions import ResumeStateError
from .logging_ import log_event


_DEFAULT_CHAPTER_RE_STR = r"^chapter_(\d{2,})\.md$"


def _chapter_re(config: dict | None) -> "re.Pattern[str]":
    cfg = config or {}
    pattern = cfg.get("canonical_chapter_regex", _DEFAULT_CHAPTER_RE_STR)
    return re.compile(pattern)


# ---------------------------------------------------------------------------
# Filesystem scan
# ---------------------------------------------------------------------------

def list_canonical_chapters(output_dir: str, config: dict | None = None) -> list[int]:
    """Return sorted list of canonical chapter numbers present in output_dir.

    I9: regex is config-driven, default `chapter_(\\d{2,})\\.md`.
    """
    p = Path(output_dir)
    if not p.exists():
        return []
    chap_re = _chapter_re(config)
    nums: list[int] = []
    for entry in p.iterdir():
        if not entry.is_file():
            continue
        m = chap_re.match(entry.name)
        if m:
            nums.append(int(m.group(1)))
    return sorted(nums)


def find_next_chapter_number(output_dir: str, config: dict | None = None) -> int:
    """Return the first missing positive integer in the canonical chapter
    sequence starting at 1.
    """
    nums = set(list_canonical_chapters(output_dir, config))
    i = 1
    while i in nums:
        i += 1
    return i


def compute_gaps(output_dir: str, config: dict | None = None) -> list[int]:
    """Return integers missing below the maximum present chapter number."""
    nums = list_canonical_chapters(output_dir, config)
    if not nums:
        return []
    present = set(nums)
    return [i for i in range(1, max(nums)) if i not in present]


# ---------------------------------------------------------------------------
# State file I/O
# ---------------------------------------------------------------------------

def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_state(state_file_path: str) -> dict | None:
    """Read state file. None if missing. ResumeStateError on malformed JSON.

    H7: `last_chapter_drafted` is treated as optional — older files
    without that key are still valid.
    """
    p = Path(state_file_path)
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ResumeStateError(
            f"malformed JSON in {p}: {e}. Either repair manually or delete "
            f"the file (and any canonical chapters) to start fresh."
        ) from e
    except OSError as e:
        raise ResumeStateError(f"cannot read {p}: {e}") from e

    # Minimal schema check; only the original two keys are required.
    required = {"last_chapter_promoted", "last_chapter_living_doc_updated"}
    if not required.issubset(data):
        raise ResumeStateError(
            f"{p} missing required keys; expected {sorted(required)}, "
            f"got {sorted(data.keys())}"
        )
    # H7: backfill the optional key if absent.
    data.setdefault("last_chapter_drafted", None)
    return data


def write_state(
    state_file_path: str,
    *,
    last_chapter_promoted: int,
    last_chapter_living_doc_updated: int,
    last_chapter_drafted: int | None = None,
) -> None:
    """Atomically write the state file.

    H7: `last_chapter_drafted` is optional. When provided, it's persisted;
    when None, it is omitted from the JSON file.
    """
    data: dict = {
        "last_chapter_promoted": last_chapter_promoted,
        "last_chapter_living_doc_updated": last_chapter_living_doc_updated,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if last_chapter_drafted is not None:
        data["last_chapter_drafted"] = int(last_chapter_drafted)
    _atomic_write_json(Path(state_file_path), data)
    log_event("state_file_written", data)


# ---------------------------------------------------------------------------
# Resume detection
# ---------------------------------------------------------------------------

def detect_resume_state(
    output_dir: str,
    state_file_path: str,
    config: dict | None = None,
) -> dict:
    """Cross-check filesystem against the state file.

    Returns:
      {
        "next_chapter": int,
        "last_promoted": int,
        "last_doc_updated": int,
        "last_drafted": int | None,    # H7: from state file, else None
        "consistent": bool,
        "gaps_present": list[int],
        "state_file_exists": bool,
        "chapters_on_disk": list[int],
      }
    """
    chapters_on_disk = list_canonical_chapters(output_dir, config)
    state = read_state(state_file_path)

    if state is None and chapters_on_disk:
        raise ResumeStateError(
            f".pipeline_state.json missing but canonical chapters exist in "
            f"{output_dir}: {chapters_on_disk}. Either delete the chapters "
            f"to start fresh, or manually create {state_file_path} reflecting "
            f"the true last-promoted and last-doc-updated values."
        )

    if state is None:
        last_promoted = 0
        last_doc_updated = 0
        last_drafted: int | None = None
        state_file_exists = False
    else:
        last_promoted = int(state["last_chapter_promoted"])
        last_doc_updated = int(state["last_chapter_living_doc_updated"])
        drafted_raw = state.get("last_chapter_drafted")
        last_drafted = int(drafted_raw) if drafted_raw is not None else None
        state_file_exists = True

    return {
        "next_chapter": find_next_chapter_number(output_dir, config),
        "last_promoted": last_promoted,
        "last_doc_updated": last_doc_updated,
        "last_drafted": last_drafted,
        "consistent": last_promoted == last_doc_updated,
        "gaps_present": compute_gaps(output_dir, config),
        "state_file_exists": state_file_exists,
        "chapters_on_disk": chapters_on_disk,
    }
