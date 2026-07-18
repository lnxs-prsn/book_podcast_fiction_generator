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

import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
QUOTA_BY_ARC = {1: 3, 2: 3, 3: 2, 4: 2}  # arc 5+ -> 1 (curriculum §9)

brief = json.loads((R / "prompts/update_brief.json").read_text())
ms = json.loads((R / "state/master_state.json").read_text())
arc = ms.get("arc_current", 1)
quota = QUOTA_BY_ARC.get(arc, 1)
problems: list[str] = []

ctype = brief.get("chapter_type")
if ctype in ("new_focal_character", "return_to_character"):
    pu = brief.get("process_updates") or {}
    shown = pu.get("failure_modes_shown_this_chapter") or []
    if len(shown) < quota:
        problems.append(f"wrong-approach scenes: {len(shown)} of {quota} required for arc {arc} ({shown})")

    au = brief.get("anchor_update") or {}
    if not au.get("appeared"):
        problems.append("anchor absent from a gate chapter (owner rule D3/F16)")

    if (pu.get("context_demonstrated") or "none") == "none":
        problems.append("no ordinary-life echo recorded (world rules: echo in same chapter)")

    fc = brief.get("focal_character") or {}
    if fc.get("is_new") is False and fc.get("life_progression_shown") is False:
        problems.append("returning focal shows no visible life progression (owner rule F14)")

    newcomers = (1 if fc.get("is_new") else 0) + sum(
        1 for e in (brief.get("other_entrants") or []) if e.get("is_new"))
    if newcomers < 1:
        problems.append("no improvised newcomer in the gate (owner rule F15)")

if problems:
    print("STRUCTURAL GATE: FAIL — chapter is under-populated; state NOT applied.")
    for p in problems:
        print(f"  - {p}")
    print("Options: redo generation (step 8) / redo from brief (step 7) / owner accepts explicitly.")
    sys.exit(1)
print(f"STRUCTURAL GATE: PASS (arc {arc}, quota {quota}).")
