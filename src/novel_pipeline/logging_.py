"""Append-only JSONL event log.

Logging failures never crash the pipeline; they fall back to stderr.
"""

from __future__ import annotations

import json
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

_LOG_PATH: Path | None = None
_LOG_LOCK = threading.Lock()


def configure(log_path: str) -> None:
    """Set the log file path. Called once at startup from load_config consumers."""
    global _LOG_PATH
    _LOG_PATH = Path(log_path)


def log_event(event: str, data: dict | None = None) -> None:
    """Write one JSONL line. Never raises."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }
    if data:
        record.update(data)
    line = json.dumps(record, ensure_ascii=False, default=str)
    try:
        if _LOG_PATH is None:
            # Not configured yet — write to stderr so we don't lose early events.
            print(line, file=sys.stderr)
            return
        with _LOG_LOCK:
            _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with _LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception as e:  # pragma: no cover - logging must never crash
        try:
            print(f"[log_event failed: {e}] {line}", file=sys.stderr)
        except Exception:
            pass
