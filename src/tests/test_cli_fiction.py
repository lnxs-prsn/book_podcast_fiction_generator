"""CLI tests for src/cli/fiction.py.

All tests invoke the CLI via subprocess.run with PYTHONPATH=src to avoid
the sys.path guard at import time.

Key behaviours tested:
- JSONL log_event output is NOT swallowed (reaches stderr when log path not configured)
- LOG_LEVEL=DEBUG emits debug output into the log file
- ConfigError produces exit code 2 with no traceback
- Generic Exception produces exit code 1 with no traceback
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).parent.parent
CLI = SRC_DIR / "cli" / "fiction.py"
PYTHON = sys.executable


def _run(
    args: list[str],
    env: dict | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess:
    """Run the fiction CLI with PYTHONPATH=src."""
    base_env = {**os.environ, "PYTHONPATH": str(SRC_DIR)}
    if env:
        base_env.update(env)
    return subprocess.run(
        [PYTHON, str(CLI)] + args,
        capture_output=True,
        text=True,
        cwd=str(cwd or SRC_DIR),
        env=base_env,
    )


def _write_helper(tmp_path: Path, body: str) -> Path:
    """Write a helper script body into tmp_path/helper.py and return its path."""
    helper = tmp_path / "helper.py"
    helper.write_text(textwrap.dedent(body))
    return helper


# ---------------------------------------------------------------------------
# 1. --help exits 0 (sanity)
# ---------------------------------------------------------------------------

def test_help_exits_zero():
    result = _run(["--help"])
    assert result.returncode == 0
    assert "fiction" in result.stdout.lower() or "novel" in result.stdout.lower()


# ---------------------------------------------------------------------------
# 2. Missing --config exits non-zero (argparse requires it)
# ---------------------------------------------------------------------------

def test_missing_config_flag_exits_nonzero():
    result = _run([])
    # argparse exits 2 for missing required argument
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# 3. ConfigError produces exit code 2 with no traceback
# ---------------------------------------------------------------------------

def test_config_error_exits_two(tmp_path):
    """When run_novel_session raises ConfigError, the CLI must exit 2."""
    # Write a minimal TOML config so argparse is satisfied
    config_file = tmp_path / "bad.toml"
    config_file.write_text("[config]\n# intentionally empty\n")

    # We use a helper script that patches run_novel_session to raise ConfigError
    helper_body = f"""
import sys
sys.path.insert(0, {str(SRC_DIR)!r})

# Patch run_novel_session before fiction.py is imported
import endpoints.fiction as _ef
from novel_pipeline.exceptions import ConfigError

def _raise_config_error(*a, **kw):
    raise ConfigError("bad config for test")

_ef.run_novel_session = _raise_config_error

# Also patch resolve_data_root so logging can initialize without a real root
import path_utils as _pu
import pathlib
_pu.resolve_data_root = lambda *a, **kw: pathlib.Path({str(tmp_path)!r})

# Now import and run main
import cli.fiction as _mod
_mod.main()
"""
    helper = _write_helper(tmp_path, helper_body)
    result = subprocess.run(
        [PYTHON, str(helper), "--config", str(config_file)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
    )
    assert result.returncode == 2, (
        f"Expected exit 2 for ConfigError, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined


# ---------------------------------------------------------------------------
# 4. Generic Exception produces exit code 1 with no traceback
# ---------------------------------------------------------------------------

def test_generic_exception_exits_one(tmp_path):
    """When run_novel_session raises a generic Exception, the CLI must exit 1."""
    config_file = tmp_path / "cfg.toml"
    config_file.write_text("[config]\n")

    helper_body = f"""
import sys
sys.path.insert(0, {str(SRC_DIR)!r})

import endpoints.fiction as _ef
import path_utils as _pu
import pathlib

_ef.run_novel_session = lambda *a, **kw: (_ for _ in ()).throw(
    RuntimeError("synthetic runtime error")
)
_pu.resolve_data_root = lambda *a, **kw: pathlib.Path({str(tmp_path)!r})

import cli.fiction as _mod
_mod.main()
"""
    helper = _write_helper(tmp_path, helper_body)
    result = subprocess.run(
        [PYTHON, str(helper), "--config", str(config_file)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
    )
    assert result.returncode == 1, (
        f"Expected exit 1 for generic Exception, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined


# ---------------------------------------------------------------------------
# 5. JSONL log_event is preserved (not swallowed)
#
# When _LOG_PATH is None, log_event() writes to stderr.
# We mock run_novel_session to trigger a log_event call and verify the
# resulting JSONL line appears in the process output.
# ---------------------------------------------------------------------------

def test_jsonl_log_event_not_swallowed(tmp_path):
    """JSONL log_event output from run_novel_session must reach stderr."""
    config_file = tmp_path / "cfg.toml"
    config_file.write_text("[config]\n")

    # Helper: patch run_novel_session to emit a known log_event line, then
    # return a valid SessionResult so the CLI exits 0.
    helper_body = f"""
import sys
import json
sys.path.insert(0, {str(SRC_DIR)!r})

import endpoints.fiction as _ef
import path_utils as _pu
import pathlib
from novel_pipeline.session import SessionResult
from novel_pipeline.logging_ import log_event

def _mock_session(*a, **kw):
    # Emit a JSONL event; since _LOG_PATH is None it goes to stderr
    log_event("test_jsonl_marker", {{"payload": "hello_jsonl"}})
    return SessionResult(
        chapters_written=0,
        final_chapter_number=0,
        cost_usd=0.0,
        completed=True,
        state_path=pathlib.Path({str(tmp_path)!r}) / ".pipeline_state.json",
    )

_ef.run_novel_session = _mock_session
_pu.resolve_data_root = lambda *a, **kw: pathlib.Path({str(tmp_path)!r})

import cli.fiction as _mod
_mod.main()
"""
    helper = _write_helper(tmp_path, helper_body)
    result = subprocess.run(
        [PYTHON, str(helper), "--config", str(config_file)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
    )
    # The CLI prints "Session complete." on stdout — exit 0 is expected
    combined = result.stdout + result.stderr
    # The JSONL line must appear somewhere in the output
    assert "test_jsonl_marker" in combined, (
        "Expected JSONL event 'test_jsonl_marker' in output but got:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    # Verify it is valid JSONL
    jsonl_lines = [
        line for line in result.stderr.splitlines()
        if line.startswith("{") and "test_jsonl_marker" in line
    ]
    assert jsonl_lines, "No valid JSONL line found in stderr"
    parsed = json.loads(jsonl_lines[0])
    assert parsed["event"] == "test_jsonl_marker"
    assert parsed["payload"] == "hello_jsonl"


# ---------------------------------------------------------------------------
# 6. LOG_LEVEL=DEBUG emits debug output in the log file under root/logs/
# ---------------------------------------------------------------------------

def test_log_level_debug_emits_debug_in_log_file(tmp_path):
    """With LOG_LEVEL=DEBUG, debug messages must appear in root/logs/cli-fiction.log."""
    config_file = tmp_path / "cfg.toml"
    config_file.write_text("[config]\n")

    helper_body = f"""
import sys
sys.path.insert(0, {str(SRC_DIR)!r})

import endpoints.fiction as _ef
import path_utils as _pu
import pathlib
from novel_pipeline.session import SessionResult
import logging

def _mock_session(*a, **kw):
    # Emit a debug message via the cli.fiction logger
    import cli.fiction as _mod
    _mod.logger.debug("debug_marker_for_test")
    return SessionResult(
        chapters_written=0,
        final_chapter_number=0,
        cost_usd=0.0,
        completed=True,
        state_path=pathlib.Path({str(tmp_path)!r}) / ".pipeline_state.json",
    )

_ef.run_novel_session = _mock_session
_pu.resolve_data_root = lambda *a, **kw: pathlib.Path({str(tmp_path)!r})

import cli.fiction as _mod
_mod.main()
"""
    helper = _write_helper(tmp_path, helper_body)
    result = subprocess.run(
        [PYTHON, str(helper), "--config", str(config_file)],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PYTHONPATH": str(SRC_DIR),
            "LOG_LEVEL": "DEBUG",
        },
    )
    log_file = tmp_path / "logs" / "cli-fiction.log"
    assert log_file.exists(), (
        f"Expected cli-fiction.log at {log_file}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    content = log_file.read_text(encoding="utf-8")
    assert "debug_marker_for_test" in content, (
        f"Expected debug marker in log file. Contents:\n{content}"
    )
    assert "DEBUG" in content, (
        f"Expected DEBUG level in log file. Contents:\n{content}"
    )
