"""Tests for path_utils root resolution and path containment."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from path_utils import (
    guard_path_escape,
    resolve_data_root,
    resolve_input_path,
    resolve_output_path,
)


class TestResolveDataRoot:
    """Environment variable must win over fallback and default."""

    def test_env_var_wins(self, monkeypatch, tmp_path):
        env_dir = tmp_path / "env_root"
        env_dir.mkdir()
        monkeypatch.setenv("HARNESS_ROOT", str(env_dir))
        assert resolve_data_root() == env_dir.resolve()

    def test_env_var_override_name(self, monkeypatch, tmp_path):
        env_dir = tmp_path / "custom_env_root"
        env_dir.mkdir()
        monkeypatch.setenv("CUSTOM_ROOT", str(env_dir))
        assert resolve_data_root(env_var="CUSTOM_ROOT") == env_dir.resolve()

    def test_fallback_used_when_env_unset(self, monkeypatch, tmp_path):
        monkeypatch.delenv("HARNESS_ROOT", raising=False)
        fallback = tmp_path / "fallback_root"
        fallback.mkdir()
        assert resolve_data_root(fallback=fallback) == fallback.resolve()

    def test_env_wins_over_fallback(self, monkeypatch, tmp_path):
        env_dir = tmp_path / "env_root"
        env_dir.mkdir()
        fallback = tmp_path / "fallback_root"
        fallback.mkdir()
        monkeypatch.setenv("HARNESS_ROOT", str(env_dir))
        assert resolve_data_root(fallback=fallback) == env_dir.resolve()

    def test_default_is_src_directory(self, monkeypatch):
        monkeypatch.delenv("HARNESS_ROOT", raising=False)
        expected = Path(__file__).parent.parent.resolve()
        assert resolve_data_root() == expected


class TestResolveOutputPath:
    """Output paths are anchored to root and containment is enforced."""

    def test_relative_path_anchored_to_root(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        out = resolve_output_path("data/output/file.txt", root=root)
        assert out == (root / "data" / "output" / "file.txt").resolve()

    def test_absolute_path_accepted_when_inside_root(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        target = root / "inside.txt"
        target.write_text("x")
        out = resolve_output_path(target, root=root)
        assert out == target.resolve()

    def test_absolute_path_outside_root_raises(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "outside.txt"
        outside.write_text("x")
        with pytest.raises(ValueError, match="escapes root"):
            resolve_output_path(outside, root=root)

    def test_path_traversal_raises(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        with pytest.raises(ValueError, match="escapes root"):
            resolve_output_path("../outside.txt", root=root)

    def test_allow_escape_permits_absolute_outside_root(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "outside.txt"
        outside.write_text("x")
        out = resolve_output_path(outside, root=root, allow_escape=True)
        assert out == outside.resolve()

    def test_allow_escape_permits_traversal(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "outside.txt"
        outside.write_text("x")
        out = resolve_output_path("../outside.txt", root=root, allow_escape=True)
        assert out == outside.resolve()

    def test_default_root_used_when_none_provided(self, monkeypatch):
        monkeypatch.delenv("HARNESS_ROOT", raising=False)
        expected_root = Path(__file__).parent.parent.resolve()
        out = resolve_output_path("foo.txt")
        assert out == expected_root / "foo.txt"


class TestResolveInputPath:
    """Input paths require existence and stay inside root by default."""

    def test_existing_relative_input(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        target = root / "input.txt"
        target.write_text("hello")
        inp = resolve_input_path("input.txt", root=root)
        assert inp == target.resolve()

    def test_missing_input_raises_file_not_found(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        with pytest.raises(FileNotFoundError, match="does not exist"):
            resolve_input_path("missing.txt", root=root)

    def test_must_exist_false_does_not_require_existence(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        out = resolve_input_path("missing.txt", root=root, must_exist=False)
        assert out == (root / "missing.txt").resolve()

    def test_input_path_traversal_rejected(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "secret.txt"
        outside.write_text("secret")
        with pytest.raises(ValueError, match="escapes root"):
            resolve_input_path("../secret.txt", root=root)

    def test_existing_absolute_input_inside_root(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        target = root / "input.txt"
        target.write_text("hello")
        inp = resolve_input_path(target, root=root)
        assert inp == target.resolve()


class TestGuardPathEscape:
    """Direct tests for the containment guard."""

    def test_inside_root_passes(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        inside = root / "nested" / "file.txt"
        inside.parent.mkdir()
        inside.write_text("x")
        # Should not raise.
        guard_path_escape(inside, root)

    def test_outside_root_raises(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "outside.txt"
        outside.write_text("x")
        with pytest.raises(ValueError, match="escapes root"):
            guard_path_escape(outside, root)

    def test_custom_message(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        outside = tmp_path / "outside.txt"
        outside.write_text("x")
        with pytest.raises(ValueError, match="custom error text"):
            guard_path_escape(outside, root, message="custom error text")

    def test_resolves_dotdot_before_checking(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        # Construct a path that lexically contains ".." but resolves inside root.
        inside_via_dotdot = root / "a" / ".." / "file.txt"
        (root / "a").mkdir()
        inside_via_dotdot.write_text("x")
        # Should not raise because the resolved path is inside root.
        guard_path_escape(inside_via_dotdot, root)
