"""Smoke tests for fiction/seed_gen/cli.py.

Covers:
- seed_gen cli can be imported from src/
- call_api is invoked with timeout=120.0 during Pass 1
- unexpected exceptions produce sanitized stderr output (no traceback) and exit 1
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path
from unittest import mock

import pytest

SRC_DIR = Path(__file__).parent.parent
PYTHON = sys.executable


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

def test_seed_gen_cli_importable():
    """fiction.seed_gen.cli must be importable from PYTHONPATH=src."""
    import fiction.seed_gen.cli  # noqa: F401


def test_call_api_importable_from_seed_gen():
    """call_api used by seed_gen cli must be importable."""
    from podcast_script_generator.llm.call_api import call_api
    assert callable(call_api)


# ---------------------------------------------------------------------------
# call_api timeout=120.0
# ---------------------------------------------------------------------------

class TestSeedGenCallApiTimeout:
    """call_api must be invoked with timeout=120.0 in the seed_gen flow."""

    def _make_client(self):
        """Return a mock LLMClient."""
        client = mock.MagicMock()
        client.call.return_value = (
            "### Genre 1: Action\n"
            "## Extracted Concepts\n"
            "- concept A\n- concept B\n- concept C\n- concept D\n- concept E"
        )
        return client

    def test_pass1_call_api_uses_timeout_120(self, tmp_path):
        """call_api for Pass 1 must receive timeout=120.0."""
        from podcast_script_generator.llm.call_api import call_api

        client = self._make_client()

        with mock.patch(
            "fiction.seed_gen.cli.call_api", wraps=call_api
        ) as mock_call_api, mock.patch(
            "fiction.seed_gen.cli.create_client", return_value=client
        ), mock.patch(
            "fiction.seed_gen.cli.extract_pdf", return_value="book text"
        ), mock.patch(
            "fiction.seed_gen.cli.load_templates",
            return_value={f: "" for f in [
                "world_laws.md", "curriculum.md", "style_contract.md",
                "full_map.md", "living_doc.md",
            ]},
        ), mock.patch(
            "fiction.seed_gen.cli.build_pass1_prompt", return_value="pass1 prompt"
        ), mock.patch(
            "fiction.seed_gen.cli.collect_user_plan",
            return_value={
                "genre_index": 1,
                "genre_text": "Action",
                "protagonist_name": "Alice",
                "protagonist_background": "Scientist",
                "concept_list": ["A", "B", "C", "D", "E"],
                "climax_concept": "A",
                "additions": "",
            },
        ), mock.patch(
            "fiction.seed_gen.cli.build_pass2_prompt", return_value="pass2 prompt"
        ), mock.patch(
            "fiction.seed_gen.cli.parse_output", return_value={}
        ), mock.patch(
            "fiction.seed_gen.cli.save_output"
        ), mock.patch(
            "fiction.seed_gen.cli.write_config_toml"
        ), mock.patch(
            "sys.argv",
            ["seed_gen", "fake.pdf", str(tmp_path)],
        ):
            import fiction.seed_gen.cli as sg
            # Reset create_client mock on the module
            sg.create_client = mock.MagicMock(return_value=client)
            sg.extract_pdf = mock.MagicMock(return_value="book text")
            sg.load_templates = mock.MagicMock(return_value={
                f: "" for f in [
                    "world_laws.md", "curriculum.md", "style_contract.md",
                    "full_map.md", "living_doc.md",
                ]
            })
            sg.build_pass1_prompt = mock.MagicMock(return_value="pass1 prompt")
            sg.collect_user_plan = mock.MagicMock(return_value={
                "genre_index": 1,
                "genre_text": "Action",
                "protagonist_name": "Alice",
                "protagonist_background": "Scientist",
                "concept_list": ["A", "B", "C", "D", "E"],
                "climax_concept": "A",
                "additions": "",
            })
            sg.build_pass2_prompt = mock.MagicMock(return_value="pass2 prompt")
            sg.parse_output = mock.MagicMock(return_value={})
            sg.save_output = mock.MagicMock()
            sg.write_config_toml = mock.MagicMock()

            with mock.patch.object(sg, "call_api", wraps=call_api) as patched_call_api:
                client.call.return_value = (
                    "### Genre 1: Action\n"
                    "## Extracted Concepts\n"
                    "- A\n- B\n- C\n- D\n- E"
                )
                try:
                    sg.main()
                except SystemExit:
                    pass

                # Verify at least one call_api invocation used timeout=120.0
                calls_with_timeout = [
                    c for c in patched_call_api.call_args_list
                    if c.kwargs.get("timeout") == 120.0
                    or (len(c.args) > 3 and c.args[3] == 120.0)
                ]
                assert calls_with_timeout, (
                    "call_api must be called with timeout=120.0 at least once"
                )


def test_call_api_signature_has_timeout():
    """call_api function signature must include a timeout parameter."""
    import inspect
    from podcast_script_generator.llm.call_api import call_api

    sig = inspect.signature(call_api)
    assert "timeout" in sig.parameters
    assert sig.parameters["timeout"].default == 120.0


def test_seed_gen_call_api_default_timeout():
    """The call_api calls in seed_gen/cli.py use timeout=120.0 explicitly."""
    import ast

    cli_path = SRC_DIR / "fiction" / "seed_gen" / "cli.py"
    source = cli_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    timeout_120_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # Check if this call is to call_api(...)
        func = node.func
        is_call_api = (
            (isinstance(func, ast.Name) and func.id == "call_api")
            or (isinstance(func, ast.Attribute) and func.attr == "call_api")
        )
        if not is_call_api:
            continue
        for kw in node.keywords:
            if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                if kw.value.value == 120.0:
                    timeout_120_calls.append(node)

    assert len(timeout_120_calls) >= 1, (
        "At least one call_api() call in seed_gen/cli.py must pass timeout=120.0"
    )


# ---------------------------------------------------------------------------
# Sanitized error on unexpected exception
# ---------------------------------------------------------------------------

def test_sanitized_error_no_traceback_on_exception(tmp_path):
    """When main() raises an unexpected exception, stderr has no traceback and
    the process exits with code 1.
    """
    out_dir = str(tmp_path)
    helper = tmp_path / "sg_error_helper.py"
    helper.write_text(
        textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(SRC_DIR)!r})

        import fiction.seed_gen.cli as sg

        # Patch load_templates to raise an unexpected error
        def _boom(*a, **kw):
            raise RuntimeError("synthetic boom for seed_gen test")

        sg.load_templates = _boom

        import unittest.mock as mock
        with mock.patch("sys.argv", ["seed_gen", "fake.pdf", {out_dir!r}]):
            try:
                sg.main()
            except SystemExit as e:
                sys.exit(e.code)
        """)
    )
    result = subprocess.run(
        [PYTHON, str(helper)],
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(SRC_DIR),
        },
    )
    assert result.returncode == 1, (
        f"Expected exit code 1, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Traceback" not in result.stderr, (
        f"Expected no traceback in stderr, got:\n{result.stderr}"
    )
    assert "Traceback" not in result.stdout, (
        f"Expected no traceback in stdout, got:\n{result.stdout}"
    )


def test_sanitized_error_message_present(tmp_path):
    """When an unexpected exception occurs, an error message is written to stderr."""
    out_dir = str(tmp_path)
    helper = tmp_path / "sg_error_msg_helper.py"
    helper.write_text(
        textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(SRC_DIR)!r})

        import fiction.seed_gen.cli as sg

        def _boom(*a, **kw):
            raise RuntimeError("synthetic boom for seed_gen test")

        sg.load_templates = _boom

        import unittest.mock as mock
        with mock.patch("sys.argv", ["seed_gen", "fake.pdf", {out_dir!r}]):
            try:
                sg.main()
            except SystemExit as e:
                sys.exit(e.code)
        """)
    )
    result = subprocess.run(
        [PYTHON, str(helper)],
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(SRC_DIR),
        },
    )
    # stderr should contain some error indication
    combined = result.stdout + result.stderr
    assert any(kw in combined.lower() for kw in ["error", "unexpected"]), (
        f"Expected error indication in output, got:\n{combined}"
    )
