#!/usr/bin/env python3
"""Offline regression checks for the public fiction_loop tool contracts."""

from __future__ import annotations

from copy import deepcopy
import json
import os
import shutil
import subprocess
import sys
import tempfile
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


def gate_fixture(
    brief: dict, master_state: dict, process_state: dict, *args: str
) -> CommandResult:
    """Run the real gate CLI against isolated copies of its three inputs."""
    with tempfile.TemporaryDirectory() as tmp:
        loop = Path(tmp) / "fiction_loop"
        (loop / "tools").mkdir(parents=True)
        (loop / "prompts").mkdir()
        (loop / "state").mkdir()
        shutil.copy2(GATE, loop / "tools/structural_gate.py")
        (loop / "prompts/update_brief.json").write_text(
            json.dumps(brief, indent=2) + "\n"
        )
        (loop / "state/master_state.json").write_text(
            json.dumps(master_state, indent=2) + "\n"
        )
        (loop / "state/process_state.json").write_text(
            json.dumps(process_state, indent=2) + "\n"
        )
        return run_command(str(loop / "tools/structural_gate.py"), *args)


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
        PROMPTS_DIR / "update_brief.json",
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

        from structural_gate import QUOTA_BY_ARC

        # Frozen against curriculum §9 Section 4 (the sole count owner: arc 1 -> 3,
        # arcs 2-8 -> 2). Guards the day-1 contradiction that false-failed ch8 arc-2
        # (field_registry.md "arc cast quota" row; human_decision.md DECISION 10).
        expected_quota = {1: 3, 2: 2, 3: 2, 4: 2}
        results.append(
            check(
                "structural gate QUOTA_BY_ARC matches curriculum §9 Section 4",
                QUOTA_BY_ARC == expected_quota,
                f"observed {QUOTA_BY_ARC}",
            )
        )

        brief_path = PROMPTS_DIR / "update_brief.json"
        live_ch8_brief = json.loads(brief_path.read_text())
        stale_result = run_command(str(GATE))
        results.append(
            check(
                "structural gate rejects stale live ch8 brief",
                stale_result.returncode == 1
                and "brief chapter 008 != scheduled 009" in stale_result.output,
            )
        )

        master_state = json.loads(
            (FICTION_LOOP_DIR / "state/master_state.json").read_text()
        )
        process_state = json.loads(
            (FICTION_LOOP_DIR / "state/process_state.json").read_text()
        )
        ch9_operation = "op_separate_condition"
        operation_state = process_state["operations"][ch9_operation]
        canonical_labels = (
            operation_state.get("failure_modes_shown", [])
            + operation_state.get("failure_modes_not_yet_shown", [])
        )
        ch9_brief = deepcopy(live_ch8_brief)
        ch9_brief["chapter"] = "009"
        ch9_brief["chapter_type"] = "return_to_character"
        ch9_brief["focal_character"]["id"] = "char_004"
        ch9_brief["focal_character"]["is_new"] = False
        ch9_brief["focal_character"]["life_progression_shown"] = True
        ch9_brief["process_updates"]["operation"] = ch9_operation
        ch9_brief["process_updates"]["failure_modes_shown_this_chapter"] = (
            canonical_labels[:2]
        )
        earned_item = "the hypothesis tester"

        none_pointer = deepcopy(master_state)
        none_pointer["next_chapter_pointer"]["failure_mode_to_show"] = "none"
        none_result = gate_fixture(ch9_brief, none_pointer, process_state)
        results.append(
            check(
                "structural gate rejects teaching pointer with no featured failure",
                none_result.returncode == 1
                and "earned-pool fallback missing, ADV-3" in none_result.output,
            )
        )

        earned_pointer = deepcopy(master_state)
        earned_pointer["next_chapter_pointer"]["failure_mode_to_show"] = earned_item
        gate_pass = gate_fixture(ch9_brief, earned_pointer, process_state)
        results.append(
            check(
                "structural gate accepts earned featured failure on ch9 return",
                gate_pass.returncode == 0
                and "STRUCTURAL GATE: PASS (arc 2, quota 2)" in gate_pass.output,
            )
        )

        invented_pointer = deepcopy(master_state)
        invented_pointer["next_chapter_pointer"]["failure_mode_to_show"] = (
            "not a pack item"
        )
        invented_result = gate_fixture(ch9_brief, invented_pointer, process_state)
        results.append(
            check(
                "structural gate rejects featured item outside earned pool",
                invented_result.returncode == 1
                and "featured failure 'not a pack item' not in earned pool"
                in invented_result.output,
            )
        )

        interlude_brief = deepcopy(ch9_brief)
        interlude_brief["chapter_type"] = "anchor_interlude"
        interlude_pointer = deepcopy(master_state)
        interlude_pointer["next_chapter_pointer"].update(
            {
                "type": "anchor_interlude",
                "char_id": None,
                "operation_due": None,
                "failure_mode_to_show": "none",
            }
        )
        interlude_result = gate_fixture(
            interlude_brief, interlude_pointer, process_state
        )
        results.append(
            check(
                "structural gate permits none on non-teaching interlude",
                interlude_result.returncode == 0
                and "earned-pool fallback missing" not in interlude_result.output,
            )
        )

        wrong_focal = deepcopy(ch9_brief)
        wrong_focal["focal_character"]["id"] = "char_005"
        wrong_focal_result = gate_fixture(
            wrong_focal, earned_pointer, process_state
        )
        results.append(
            check(
                "structural gate rejects wrong return focal id",
                wrong_focal_result.returncode == 1
                and "return focal id char_005 != scheduled char_004"
                in wrong_focal_result.output,
            )
        )

        duplicate_labels = deepcopy(ch9_brief)
        duplicate_labels["process_updates"]["failure_modes_shown_this_chapter"] = [
            canonical_labels[0],
            canonical_labels[0],
        ]
        duplicate_result = gate_fixture(
            duplicate_labels, earned_pointer, process_state
        )
        results.append(
            check(
                "structural gate counts distinct failure-mode labels",
                duplicate_result.returncode == 1
                and "1 distinct of 2" in duplicate_result.output,
            )
        )

        noncanonical_labels = deepcopy(ch9_brief)
        noncanonical_labels["process_updates"]["failure_modes_shown_this_chapter"] = [
            canonical_labels[0],
            "not a pack label",
        ]
        noncanonical_result = gate_fixture(
            noncanonical_labels, earned_pointer, process_state
        )
        results.append(
            check(
                "structural gate rejects non-canonical failure-mode labels",
                noncanonical_result.returncode == 1
                and "non-canonical failure-mode label(s): ['not a pack label']"
                in noncanonical_result.output,
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            loop = Path(tmp) / "fiction_loop"
            (loop / "tools").mkdir(parents=True)
            (loop / "prompts").mkdir()
            (loop / "state").mkdir()
            shutil.copy2(GATE, loop / "tools/structural_gate.py")
            (loop / "prompts/update_brief.json").write_text(
                json.dumps(ch9_brief, indent=2) + "\n"
            )
            (loop / "state/master_state.json").write_text(
                json.dumps(earned_pointer, indent=2) + "\n"
            )
            (loop / "state/process_state.json").write_text(
                json.dumps(process_state, indent=2) + "\n"
            )
            isolated_gate = loop / "tools/structural_gate.py"
            gate_pass = run_command(str(isolated_gate))
            isolated_receipt = loop / "prompts/.gate_pass.json"
            stale_receipt = json.loads(isolated_receipt.read_text())
            stale_receipt["chapter"] = "008"
            isolated_receipt.write_text(json.dumps(stale_receipt, indent=2) + "\n")
            stale_receipt_result = run_command(str(isolated_gate), "--verify")
            results.append(
                check(
                    "structural gate rejects receipt chapter mismatch",
                    gate_pass.returncode == 0
                    and stale_receipt_result.returncode == 1
                    and "receipt stale — chapter mismatch"
                    in stale_receipt_result.output,
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
