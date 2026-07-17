#!/usr/bin/env python3
"""fiction_loop progress — where are we, and how much is left.

Book-level, curriculum-level, and live chapter-step progress, computed from the
pipeline's own receipts (state files + STATUS.md). Zero tokens, stdlib only.
Usage:  .venv/bin/python fiction_loop/tools/progress.py        (or: watch -n 30 python3 ...)
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parent.parent

STEPS = [  # (key as it appears in STATUS.md, human label)
    ("01", "read state"), ("3.5", "log setup"), ("04", "Fetcher"),
    ("05", "Consistency (pre)"), ("06", "gate check"), ("07", "Assembler"),
    ("7.5", "Consistency (post)"), ("08", "Writer (LLM)"), ("09", "save chapter"),
    ("10", "Living doc (LLM)"), ("11", "Extractor"), ("12", "Updater"),
    ("13.5", "commit"), ("14", "report"),
]


def bar(frac: float, width: int = 24) -> str:
    n = int(round(frac * width))
    return "█" * n + "░" * (width - n)


def main() -> None:
    ms = json.loads((R / "state/master_state.json").read_text())
    ps = json.loads((R / "state/process_state.json").read_text())

    # --- curriculum: touch-events done vs scheduled --------------------------
    total = done = 0
    for op in ps["operations"].values():
        t = len(op.get("touch_schedule", {}))
        total += t
        done += min(op.get("current_touch", 0), t)
    remaining_events = total - done
    est_chapters_left = max(1, round(remaining_events / 3.0)), max(1, round(remaining_events / 2.0))

    n = ms["chapter_count"]
    title = ms.get("story_title", "?")
    print("=" * 64)
    print(f"{title} — PROGRESS")
    print("=" * 64)
    print(f"Chapters completed : {n}")
    print(f"Curriculum         : {bar(done / total)} {done}/{total} touch-events ({done / total:.0%})")
    print(f"Est. chapters left : ~{est_chapters_left[0]}–{est_chapters_left[1]} teaching chapters"
          f" (+ occasional structural)")
    ptr = ms.get("next_chapter_pointer", {})
    print(f"Next planned       : ch {ptr.get('chapter')} — {ptr.get('type')}"
          f" — {ptr.get('operation_due')} (touch {ptr.get('touch_due')})")

    # --- live chapter step ----------------------------------------------------
    sp = R / "logs/STATUS.md"
    if sp.exists():
        s = sp.read_text()
        m = {k: v.strip() for k, v in re.findall(r"(\w+): ([^|\n]+)", s)}
        state = m.get("state", "?")
        if state == "RUNNING":
            step = m.get("step", "?")
            idx = next((i for i, (k, _) in enumerate(STEPS) if k == step or k == step.zfill(2)), None)
            frac = (idx + 1) / len(STEPS) if idx is not None else 0
            label = STEPS[idx][1] if idx is not None else m.get("agent", "?")
            elapsed = ""
            try:
                since = datetime.fromisoformat(m.get("since", "").replace("Z", "+00:00"))
                mins = (datetime.now(timezone.utc) - since.astimezone(timezone.utc)).total_seconds() / 60
                elapsed = f" — {mins:.0f} min in this step"
            except Exception:
                pass
            print(f"\nRIGHT NOW          : chapter {m.get('chapter')} IN FLIGHT")
            print(f"Chapter progress   : {bar(frac)} step {step} of 14 ({label}){elapsed}")
            if idx is not None and idx + 1 < len(STEPS):
                nxt = " → ".join(l for _, l in STEPS[idx + 1:idx + 4])
                print(f"Coming up          : {nxt}")
        else:
            print(f"\nRIGHT NOW          : idle ({state}) — last: {m.get('chapter', '?')}")
            print("Start the next one : see fiction_loop/RUN.md kickoff prompt")
    print()


if __name__ == "__main__":
    main()
