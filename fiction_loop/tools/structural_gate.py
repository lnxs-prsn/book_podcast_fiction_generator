#!/usr/bin/env python3
"""Structural gate (orchestrator step 11.5) — deterministic, pre-state-mutation.

Verifies the chapter's STRUCTURE from update_brief.json + the pointer, BEFORE the
Updater applies anything. Word floors catch truncation; this catches under-population
(the failure mode word counts cannot see — chapter 004 passed the floor with a third
of its ordered cast). Exit 0 = pass, exit 1 = under-populated (report to user:
accept or redo; state untouched, redo costs only steps 7-11).
At FAIL time both state and the living document are untouched; no paid post-writer
refresh has run.
Stdlib only, zero tokens. Reads counts/booleans — never prose.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parent.parent
BRIEF_PATH = R / "prompts/update_brief.json"
RECEIPT_PATH = R / "prompts/.gate_pass.json"
QUOTA_BY_ARC = {1: 3, 2: 3, 3: 2, 4: 2}  # arc 5+ -> 1 (curriculum §9)


def brief_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def remove_receipt() -> None:
    RECEIPT_PATH.unlink(missing_ok=True)


def verify_receipt() -> int:
    if not RECEIPT_PATH.exists():
        print("no receipt")
        return 1

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        print("receipt verdict not PASS")
        return 1

    if receipt.get("verdict") != "PASS":
        print("receipt verdict not PASS")
        return 1

    try:
        current_hash = brief_sha256(BRIEF_PATH.read_bytes())
    except OSError:
        print("hash mismatch — brief changed since gate PASS")
        return 1

    if receipt.get("brief_sha256") != current_hash:
        print("hash mismatch — brief changed since gate PASS")
        return 1

    print("gate receipt verified: PASS")
    return 0


def run_gate() -> int:
    try:
        brief_bytes = BRIEF_PATH.read_bytes()
        brief = json.loads(brief_bytes)
        ms = json.loads((R / "state/master_state.json").read_text())
        arc = ms.get("arc_current", 1)
        quota = QUOTA_BY_ARC.get(arc, 1)
        problems: list[str] = []

        ctype = brief.get("chapter_type")
        if ctype in ("new_focal_character", "return_to_character"):
            pu = brief.get("process_updates") or {}
            shown = pu.get("failure_modes_shown_this_chapter") or []
            if len(shown) < quota:
                problems.append(
                    f"wrong-approach scenes: {len(shown)} of {quota} "
                    f"required for arc {arc} ({shown})"
                )

            au = brief.get("anchor_update") or {}
            if not au.get("appeared"):
                problems.append("anchor absent from a gate chapter (owner rule D3/F16)")

            if (pu.get("context_demonstrated") or "none") == "none":
                problems.append("no ordinary-life echo recorded (world rules: echo in same chapter)")

            fc = brief.get("focal_character") or {}
            if fc.get("is_new") is False and fc.get("life_progression_shown") is False:
                problems.append("returning focal shows no visible life progression (owner rule F14)")

            newcomers = (1 if fc.get("is_new") else 0) + sum(
                1 for e in (brief.get("other_entrants") or []) if e.get("is_new")
            )
            if newcomers < 1:
                problems.append("no improvised newcomer in the gate (owner rule F15)")

        if problems:
            remove_receipt()
            print("STRUCTURAL GATE: FAIL — chapter is under-populated; state NOT applied.")
            for problem in problems:
                print(f"  - {problem}")
            print("Options: redo generation (step 8) / redo from brief (step 7) / owner accepts explicitly.")
            return 1

        receipt = {
            "chapter": brief["chapter"],
            "brief_sha256": brief_sha256(brief_bytes),
            "verdict": "PASS",
            "at": datetime.now(timezone.utc).isoformat(),
        }
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n")
        print(f"STRUCTURAL GATE: PASS (arc {arc}, quota {quota}).")
        return 0
    except Exception as exc:
        remove_receipt()
        print(f"STRUCTURAL GATE: ERROR — {exc}")
        return 1


def main() -> int:
    if sys.argv[1:] == ["--verify"]:
        return verify_receipt()
    if sys.argv[1:]:
        print("usage: structural_gate.py [--verify]")
        return 1
    return run_gate()


if __name__ == "__main__":
    sys.exit(main())
