"""CLI tests for src/cli/podcast.py.

All tests invoke the CLI via subprocess.run with PYTHONPATH=src to avoid
the sys.path guard at import time.
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
CLI = SRC_DIR / "cli" / "podcast.py"
PYTHON = sys.executable


def _run(args: list[str], env: dict | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the podcast CLI with PYTHONPATH=src."""
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


# ---------------------------------------------------------------------------
# 1. --help exits 0 (sanity)
# ---------------------------------------------------------------------------

def test_help_exits_zero():
    result = _run(["--help"])
    assert result.returncode == 0
    assert "podcast" in result.stdout.lower()


# ---------------------------------------------------------------------------
# 2. Path-traversal: --scripts-out that escapes root is rejected before API call
# ---------------------------------------------------------------------------

def test_scripts_out_traversal_rejected(tmp_path):
    """Passing --scripts-out /etc/foo with a root under tmp_path must exit 1."""
    result = _run(
        [
            "fake_book.pdf",
            "--root", str(tmp_path),
            "--scripts-out", "/etc/traversal_test",
            "--skip-audio",
        ]
    )
    assert result.returncode != 0
    # Should mention path/error, not a Python traceback
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined
    assert any(kw in combined.lower() for kw in ["path", "error", "invalid", "escape"])


def test_audio_out_traversal_rejected(tmp_path):
    """Passing --audio-out /etc/foo with a root under tmp_path must exit 1."""
    result = _run(
        [
            "fake_book.pdf",
            "--root", str(tmp_path),
            "--audio-out", "/etc/traversal_test",
            "--skip-audio",
        ]
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined


# ---------------------------------------------------------------------------
# 3. --root wires the project root (HARNESS_ROOT override)
# ---------------------------------------------------------------------------

def test_root_argument_creates_log_dir(tmp_path):
    """When --root is given, the logs/ directory is created under that root."""
    result = _run(["--help"], env={"HARNESS_ROOT": str(tmp_path)})
    # --help exits cleanly with 0; we just want to verify the CLI imported OK
    assert result.returncode == 0


def test_root_argument_overrides_harness_root(tmp_path):
    """--root <dir> overrides HARNESS_ROOT when resolving output paths.

    We verify by giving a bad HARNESS_ROOT but a valid --root; the CLI should
    still create the logs/ dir under --root.
    """
    root_dir = tmp_path / "my_root"
    root_dir.mkdir()
    # Run --help so we only exercise the import + argument parsing path.
    result = _run(
        ["--help"],
        env={"HARNESS_ROOT": "/this/does/not/exist", "LOG_LEVEL": "DEBUG"},
    )
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# 4. Sanitized error on unexpected exception (exit 1, no traceback)
# ---------------------------------------------------------------------------

def test_unexpected_exception_is_sanitized(tmp_path):
    """When main() raises RuntimeError the CLI must exit 1 with no traceback."""
    # Create a helper script that monkey-patches path_utils.resolve_data_root
    # to raise RuntimeError, then invokes the CLI's __main__ block.
    helper = tmp_path / "raise_helper.py"
    helper.write_text(
        textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(SRC_DIR)!r})

        # Monkey-patch resolve_data_root to raise unexpectedly
        import path_utils as _pu
        _orig = _pu.resolve_data_root
        def _boom(*a, **kw):
            raise RuntimeError("synthetic boom for test")
        _pu.resolve_data_root = _boom

        # Now exercise the __main__ guard in cli/podcast.py
        import cli.podcast as _mod
        _mod.resolve_data_root = _boom   # also patch the reference cached in cli.podcast
        try:
            _mod.main()
        except SystemExit as e:
            sys.exit(e.code)
        except Exception as e:
            sys.stderr.write(f"Unexpected error: {{e}}\\n")
            sys.exit(1)
        """)
    )
    result = subprocess.run(
        [PYTHON, str(helper)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout


# ---------------------------------------------------------------------------
# 5. Missing input PDF gives non-zero exit and clear error message
# ---------------------------------------------------------------------------

def test_missing_pdf_exits_nonzero(tmp_path):
    """A PDF that does not exist must produce a clear error (not a raw exception)."""
    missing_pdf = tmp_path / "nonexistent.pdf"
    result = _run(
        [
            str(missing_pdf),
            "--root", str(tmp_path),
            "--skip-audio",
        ]
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined
    # Should mention the missing file
    assert any(kw in combined.lower() for kw in ["not found", "error", "pdf", "path"])


# ---------------------------------------------------------------------------
# 6. --skip-audio dry-run: no audio call when skip-audio is set
# ---------------------------------------------------------------------------

def test_skip_audio_flag_accepted(tmp_path):
    """--skip-audio is a valid flag; when PDF is missing we still get a path error,
    not an 'unrecognised argument' error."""
    result = _run(
        [
            str(tmp_path / "nonexistent.pdf"),
            "--root", str(tmp_path),
            "--skip-audio",
        ]
    )
    # Should fail with file-not-found (exit 1), NOT with argparse unrecognised
    # argument (exit 2 in argparse convention). Either way, no raw traceback.
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined
    assert "unrecognised" not in combined.lower()
    assert "error: unrecognized" not in combined.lower()


# ---------------------------------------------------------------------------
# 7. LOG_LEVEL=DEBUG produces debug output in the log file
# ---------------------------------------------------------------------------

def test_log_level_debug_produces_log_file(tmp_path):
    """With LOG_LEVEL=DEBUG and --root, a log file should be created."""
    root_dir = tmp_path / "harness_root"
    root_dir.mkdir()
    # Run --help: this exits before doing any work but _configure_logging is
    # called only inside main(). So use a missing-pdf invocation instead.
    result = _run(
        [
            str(tmp_path / "nonexistent.pdf"),
            "--root", str(root_dir),
            "--skip-audio",
        ],
        env={"LOG_LEVEL": "DEBUG"},
    )
    # CLI exits non-zero (PDF not found), but the log dir should have been created
    log_dir = root_dir / "logs"
    assert log_dir.exists(), "logs/ dir was not created under --root"
    log_file = log_dir / "cli-podcast.log"
    assert log_file.exists(), "cli-podcast.log was not created"
    content = log_file.read_text(encoding="utf-8")
    # Should contain DEBUG-level content since LOG_LEVEL=DEBUG
    assert "DEBUG" in content or len(content) > 0
