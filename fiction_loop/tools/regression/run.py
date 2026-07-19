#!/usr/bin/env python3
"""Offline regression checks for the public fiction_loop tool contracts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REGRESSION_DIR = Path(__file__).resolve().parent
TOOLS_DIR = REGRESSION_DIR.parent
FICTION_LOOP_DIR = TOOLS_DIR.parent
REPO_ROOT = FICTION_LOOP_DIR.parent
FIXTURES_DIR = REGRESSION_DIR / "fixtures"
PROMPTS_DIR = FICTION_LOOP_DIR / "prompts"
WRITER = TOOLS_DIR / "invoke_writer.py"
GATE = TOOLS_DIR / "structural_gate.py"


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    output: str


class ArtifactSnapshot:
    """Restore transient prompt artifacts exactly as the runner found them."""

    def __init__(self, paths: tuple[Path, ...]) -> None:
        self._paths = paths
        self._before: dict[Path, tuple[bytes, int] | None] = {}

    def __enter__(self) -> "ArtifactSnapshot":
        for path in self._paths:
            if path.exists():
                self._before[path] = (path.read_bytes(), path.stat().st_mode)
            else:
                self._before[path] = None
        return self

    def __exit__(self, *_exc: object) -> None:
        for path, previous in self._before.items():
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                contents, mode = previous
                path.write_bytes(contents)
                path.chmod(mode)


def run_command(*args: str) -> CommandResult:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT / 'src'}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(REPO_ROOT / "src")
    )
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout)


def check(name: str, condition: bool, detail: str = "") -> bool:
    verdict = "PASS" if condition else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"{verdict}: {name}{suffix}")
    return condition


def prose_report() -> list[dict] | None:
    path = PROMPTS_DIR / "prose_deficiencies.json"
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return report if isinstance(report, list) else None


def main() -> int:
    results: list[bool] = []
    ch7 = FIXTURES_DIR / "ch7_clean.md"
    attempt2 = FIXTURES_DIR / "attempt2_labelleak.md"
    attempt3 = FIXTURES_DIR / "attempt3_clean.md"
    artifacts = (
        PROMPTS_DIR / "prose_deficiencies.json",
        PROMPTS_DIR / "revision_prompt.md",
        PROMPTS_DIR / ".gate_pass.json",
    )

    with ArtifactSnapshot(artifacts):
        for name, fixture, expected_exit in (
            ("check-labels ch7 clean", ch7, 0),
            ("check-labels attempt-2 label leak", attempt2, 1),
            ("check-labels attempt-3 clean", attempt3, 0),
        ):
            result = run_command(str(WRITER), "--check-labels", str(fixture))
            results.append(check(name, result.returncode == expected_exit))

        for name, fixture, expected_exit, expected_count in (
            ("check-prose ch7 returns []", ch7, 0, 0),
            ("check-prose attempt-3 returns []", attempt3, 0, 0),
            (
                "check-prose attempt-2 returns 4 forbidden_label records",
                attempt2,
                1,
                4,
            ),
        ):
            result = run_command(str(WRITER), "--check-prose", str(fixture))
            report = prose_report()
            valid_report = (
                report is not None
                and len(report) == expected_count
                and all(item.get("check") == "forbidden_label" for item in report)
            )
            no_traceback = "Traceback" not in result.output
            results.append(
                check(
                    name,
                    result.returncode == expected_exit
                    and valid_report
                    and no_traceback,
                )
            )

        sys.path.insert(0, str(TOOLS_DIR))
        from invoke_writer import REVISION_MAX_DIFF_RATIO, revision_diff_ratio

        identical_ratio = revision_diff_ratio("one\ntwo\n", "one\ntwo\n")
        results.append(
            check(
                "revision_diff_ratio identical is 0.0",
                identical_ratio == 0.0,
                f"observed {identical_ratio:.3f}",
            )
        )
        changed_ratio = revision_diff_ratio(
            "one\ntwo\nthree\nfour\n",
            "changed\nlines\nreplace\nmost\n",
        )
        results.append(
            check(
                "revision_diff_ratio detects over-25% change",
                changed_ratio > REVISION_MAX_DIFF_RATIO,
                f"observed {changed_ratio:.3f} > {REVISION_MAX_DIFF_RATIO:.2f}",
            )
        )

        revise_guard = run_command(str(WRITER), "--revise", str(ch7), "--dry-run")
        results.append(
            check(
                "--revise without --deficiencies errors",
                revise_guard.returncode != 0
                and "--revise requires --deficiencies" in revise_guard.output,
            )
        )
        prose_guard = run_command(
            str(WRITER),
            "--check-prose",
            str(ch7),
            "--output",
            str(PROMPTS_DIR / "chapter_draft.md"),
        )
        results.append(
            check(
                "--check-prose with --output errors",
                prose_guard.returncode != 0
                and "--check-prose cannot be combined" in prose_guard.output,
            )
        )

        gate_receipt = PROMPTS_DIR / ".gate_pass.json"
        gate_receipt.unlink(missing_ok=True)
        gate_result = run_command(str(GATE), "--verify")
        results.append(
            check(
                "structural gate verify without receipt fails",
                gate_result.returncode != 0
                and "no receipt" in gate_result.output.casefold(),
            )
        )

    failed = len(results) - sum(results)
    print(
        f"{'PASS' if failed == 0 else 'FAIL'}: "
        f"{len(results) - failed}/{len(results)} assertions passed"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
