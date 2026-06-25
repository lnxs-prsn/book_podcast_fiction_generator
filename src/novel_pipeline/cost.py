"""Cost estimation and spend tracking.

Spend state lives in ./.pipeline_spend.json with this schema:

    {
      "session_total": 0.00,
      "lifetime_total": 0.00,
      "session_started_at": "...",
      "entries": [{"ts": "...", "amount": 0.00, "note": "..."}, ...]
    }

Sessions are per-process: we initialise `session_total` to 0 in-memory on
first call within a run, while keeping `lifetime_total` cumulative across
runs.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .logging_ import log_event


_SPEND_FILE_DEFAULT = "./.pipeline_spend.json"

# Module-level session accumulator, reset per process.
_SESSION_SPEND = 0.0


def estimate_cost(
    prompt_tokens: int,
    expected_output_tokens: int,
    config: dict,
) -> float:
    """Return estimated USD cost for one call given configured per-1M prices."""
    p_in = float(config["price_per_1m_input_tokens"])
    p_out = float(config["price_per_1m_output_tokens"])
    return (prompt_tokens / 1_000_000.0) * p_in + (
        expected_output_tokens / 1_000_000.0
    ) * p_out


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


def _load_spend(path: Path) -> dict:
    if not path.exists():
        return {
            "session_total": 0.0,
            "lifetime_total": 0.0,
            "session_started_at": datetime.now(timezone.utc).isoformat(),
            "entries": [],
        }
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log_event("spend_file_corrupt_recreating", {"path": str(path), "error": str(e)})
        return {
            "session_total": 0.0,
            "lifetime_total": 0.0,
            "session_started_at": datetime.now(timezone.utc).isoformat(),
            "entries": [],
        }
    # Coerce in case of older files.
    data.setdefault("session_total", 0.0)
    data.setdefault("lifetime_total", 0.0)
    data.setdefault("entries", [])
    return data


def track_spend(amount: float, config: dict, *, note: str = "") -> dict:
    """Append a spend entry and return current totals.

    Returns: {"session_total": float, "lifetime_total": float}
    """
    global _SESSION_SPEND

    path = Path(config.get("spend_file_path", _SPEND_FILE_DEFAULT))
    data = _load_spend(path)

    _SESSION_SPEND += amount
    data["session_total"] = _SESSION_SPEND
    data["lifetime_total"] = float(data.get("lifetime_total", 0.0)) + amount
    data["entries"].append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "amount": round(amount, 6),
            "note": note,
        }
    )

    _atomic_write_json(path, data)
    log_event(
        "spend_tracked",
        {
            "amount": round(amount, 6),
            "session_total": round(_SESSION_SPEND, 6),
            "lifetime_total": round(data["lifetime_total"], 6),
            "note": note,
        },
    )
    return {
        "session_total": _SESSION_SPEND,
        "lifetime_total": data["lifetime_total"],
    }


def current_totals(config: dict) -> dict:
    """Read current totals without modifying anything."""
    path = Path(config.get("spend_file_path", _SPEND_FILE_DEFAULT))
    data = _load_spend(path)
    return {
        "session_total": _SESSION_SPEND,
        "lifetime_total": float(data.get("lifetime_total", 0.0)),
    }


def reset_session_spend() -> None:
    """Used by tests; resets the in-process session accumulator."""
    global _SESSION_SPEND
    _SESSION_SPEND = 0.0
