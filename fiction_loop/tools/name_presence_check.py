#!/usr/bin/env python3
"""Verify that every personal name asserted by the brief occurs in its prose.

Orchestrator step 11.4: deterministic, stdlib-only, zero tokens, and read-only.
Exit 0 means every asserted name has prose support; exit 1 means one or more
names are missing or the inputs could not be checked.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


R = Path(__file__).resolve().parent.parent
BRIEF_PATH = R / "prompts/update_brief.json"


def asserted_names(brief: dict) -> list[tuple[str, str]]:
    """Return non-null personal names paired with their brief field."""
    asserted: list[tuple[str, str]] = []
    focal = brief.get("focal_character")
    if isinstance(focal, dict) and focal.get("name"):
        asserted.append((str(focal["name"]), "focal_character.name"))

    for index, entrant in enumerate(brief.get("other_entrants") or []):
        if isinstance(entrant, dict) and entrant.get("name"):
            asserted.append(
                (str(entrant["name"]), f"other_entrants[{index}].name")
            )

    for index, name in enumerate(brief.get("names_used_this_chapter") or []):
        if name:
            asserted.append((str(name), f"names_used_this_chapter[{index}]"))
    return asserted


def has_prose_support(name: str, prose: str) -> bool:
    """Apply the ticket's forgiving, case-insensitive name matching rule."""
    if name.casefold() in prose.casefold():
        return True
    tokens = re.findall(r"\w+", name, flags=re.UNICODE)
    return bool(tokens) and all(
        re.search(rf"(?<!\w){re.escape(token)}(?!\w)", prose, re.IGNORECASE)
        for token in tokens
    )


def run_check() -> int:
    try:
        brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
        chapter = str(brief["chapter"])
        chapter_path = R / "chapters" / f"chapter_{int(chapter):03d}.md"
        prose = chapter_path.read_text(encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"NAME PRESENCE CHECK: ERROR — {exc}")
        return 1

    missing = [
        (name, field)
        for name, field in asserted_names(brief)
        if not has_prose_support(name, prose)
    ]
    for name, field in missing:
        print(f'MISSING FROM PROSE: "{name}" ({field})')

    if missing:
        print(f"NAME PRESENCE CHECK: FAIL — {len(missing)} missing name(s).")
        return 1
    print("NAME PRESENCE CHECK: PASS — all asserted personal names occur in prose.")
    return 0


def main() -> int:
    if sys.argv[1:]:
        print("usage: name_presence_check.py")
        return 1
    return run_check()


if __name__ == "__main__":
    raise SystemExit(main())
