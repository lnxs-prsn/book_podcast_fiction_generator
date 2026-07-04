#!/usr/bin/env python3
"""Generate output/scout.json from output/scout_listing.txt following 02_scout.md rules."""

import json
from datetime import datetime, timezone
from pathlib import Path, PurePath

ROOT = "/home/mr/Desktop/python/harness_design/harnessv8"
LISTING = Path("output/scout_listing.txt")
OUTPUT = Path("output/scout.json")

EXCLUDED_PREFIXES = (
    ".venv/",
    ".mypy_cache/",
    ".pytest_cache/",
    "src/.venv/",
    "src/build/",
    "src/.pytest_cache/",
    "src/harness.egg-info/",
    "src/__pycache__/",
)


def relative(path: str) -> str:
    if path == ROOT:
        return "."
    if path.startswith(ROOT + "/"):
        return path[len(ROOT) + 1 :]
    return path


def is_excluded(rel: str) -> bool:
    return any(rel == "." or rel.startswith(p) for p in EXCLUDED_PREFIXES)


def is_file_line(rel: str) -> bool:
    # find lists directories too; a line with an extension or no trailing slash is likely a file
    return "." in PurePath(rel).name or not rel.endswith("/")


def main() -> None:
    lines = LISTING.read_text().splitlines()
    rels = [relative(p) for p in lines]
    project_rels = [r for r in rels if not is_excluded(r)]
    file_rels = [r for r in project_rels if is_file_line(r) and r != "."]

    entry_points = []
    test_locations = []
    config_files = []
    dependency_manifests = []

    # Collect test directories separately to avoid duplicates from files inside them
    test_dirs_seen = set()

    for rel in project_rels:
        parts = PurePath(rel).parts
        name = parts[-1] if parts else ""
        lower_name = name.lower()

        # Entry points
        if (
            lower_name in ("main.py", "cli.py", "app.py", "__main__.py")
            or "cmd" in parts
            or "bin" in parts
        ):
            evidence = ""
            if lower_name == "main.py":
                evidence = "main.py filename pattern"
            elif lower_name == "__main__.py":
                evidence = "__main__.py executable module pattern"
            elif lower_name == "cli.py":
                evidence = "cli.py CLI entry pattern"
            elif lower_name == "app.py":
                evidence = "app.py application entry pattern"
            elif "cmd" in parts:
                evidence = "cmd/ directory convention"
            elif "bin" in parts:
                evidence = "bin/ directory convention"
            entry_points.append({"path": rel, "evidence": evidence})

        # Test locations
        if any(part.startswith("test_") or part.endswith("_test") or part.endswith("_spec") or part == "tests" for part in parts):
            # Prefer directory entries when present
            if rel.endswith("/"):
                if rel not in test_dirs_seen:
                    test_dirs_seen.add(rel)
                    test_locations.append({
                        "path": rel.rstrip("/"),
                        "framework": "pytest",
                        "evidence": "tests/ directory",
                    })
            else:
                # File: register the containing directory if it's a tests dir, else the file
                parent = str(PurePath(rel).parent)
                if parent.endswith("/tests") or parent == "tests":
                    if parent not in test_dirs_seen:
                        test_dirs_seen.add(parent)
                        test_locations.append({
                            "path": parent,
                            "framework": "pytest",
                            "evidence": "tests/ directory",
                        })
                elif name.startswith("test_") or "_test." in name or "_spec." in name:
                    test_locations.append({
                        "path": rel,
                        "framework": "pytest",
                        "evidence": "test_* filename pattern",
                    })

    # Special root-level entry points not caught above
    if "menu.py" in file_rels and not any(ep["path"] == "menu.py" for ep in entry_points):
        entry_points.append({"path": "menu.py", "evidence": "root-level menu launcher"})
    for run_file in ("src/run_book.py", "src/run_chapter.py"):
        if run_file in file_rels and not any(ep["path"] == run_file for ep in entry_points):
            entry_points.append({"path": run_file, "evidence": "run_* execution script"})

    # Config files (heuristic)
    config_patterns = {
        ".env": "environment variables",
        ".env.example": "environment variables template",
        ".gitignore": "git ignore rules",
        ".python-version": "Python version specification",
        "src/config.json": "application configuration JSON",
        "src/config.py": "application configuration module",
        "src/settings.py": "application settings module",
        "src/pyproject.toml": "Python project/tool configuration",
        "src/uv.lock": "uv dependency lock file",
        ".claude/settings.local.json": "Claude local settings",
    }
    for rel, purpose in config_patterns.items():
        if rel in file_rels:
            config_files.append({"path": rel, "purpose": purpose})

    # Dependency manifests
    dep_patterns = {
        "src/pyproject.toml": "pyproject.toml",
        "src/podcast_script_generator/llm/requirements.txt": "requirements.txt",
        "src/uv.lock": "uv.lock",
        "src/harness.egg-info/requires.txt": "other",
    }
    for rel, mtype in dep_patterns.items():
        if rel in file_rels:
            dependency_manifests.append({"path": rel, "type": mtype})

    # Source directories (top-level project dirs excluding obvious non-source)
    non_source = {
        ".", "books", "chapters", "data", "docs", "planning_agents",
        "polya_fiction", "scripts", "output", ".claude",
    }
    source_directories = []
    top_dirs = sorted({PurePath(r).parts[0] for r in project_rels if r != "." and "/" in r})
    for d in top_dirs:
        if d in non_source:
            continue
        note = "primary source" if d == "src" else "utilities"
        source_directories.append({"path": d, "note": note})

    # Important src subdirectories
    src_subdirs = [
        "src/cli", "src/endpoints", "src/engines", "src/fiction",
        "src/llm", "src/novel_pipeline", "src/phases", "src/podcast_script_generator",
        "src/slicer", "src/tts", "src/util", "src/tests",
    ]
    for d in src_subdirs:
        if any(r.startswith(d + "/") for r in project_rels):
            note = "tests" if d.endswith("/tests") or d == "src/tests" else "primary source"
            if d == "src/util":
                note = "utilities"
            if d == "src/phases":
                note = "other"
            source_directories.append({"path": d, "note": note})

    # Deduplicate source_directories
    seen = set()
    deduped_sd = []
    for sd in source_directories:
        if sd["path"] not in seen:
            seen.add(sd["path"])
            deduped_sd.append(sd)
    source_directories = deduped_sd

    # files_to_read: entry points first, then core source, then tests. Max 20.
    files_to_read = []
    # Prioritize root and obvious launchers
    priority_files = [
        "menu.py",
        "src/run_book.py",
        "src/run_chapter.py",
        "src/novel_pipeline/__main__.py",
        "src/novel_pipeline/cli.py",
        "src/cli/fiction.py",
        "src/cli/podcast.py",
        "src/fiction/seed_gen/__main__.py",
        "src/fiction/seed_gen/cli.py",
        "src/tts/cli.py",
        "src/podcast_script_generator/llm/main.py",
        "src/config.py",
        "src/settings.py",
        "src/endpoints/fiction.py",
        "src/endpoints/podcast.py",
        "src/engines/factory.py",
        "src/llm/factory.py",
        "src/novel_pipeline/api.py",
        "src/tests/test_cli_fiction.py",
        "src/tests/test_engines.py",
    ]
    for f in priority_files:
        if f in file_rels and f not in files_to_read:
            files_to_read.append(f)
    files_to_read = files_to_read[:20]

    gaps = [
        "Cannot determine exact dependency versions or build tool from directory listing alone; pyproject.toml/uv.lock need to be read.",
        "Cannot determine which entry point is the primary user-facing launcher without reading file contents or documentation.",
        "Cannot determine test runner invocation or custom fixtures without reading test files.",
        "Cannot determine runtime environment variables required without reading .env.example contents.",
    ]

    result = {
        "meta": {
            "produced_at": datetime.now(timezone.utc).isoformat(),
            "root": ROOT,
            "total_files": len(file_rels),
        },
        "entry_points": entry_points,
        "test_locations": test_locations,
        "config_files": config_files,
        "dependency_manifests": dependency_manifests,
        "source_directories": source_directories,
        "files_to_read": files_to_read,
        "gaps": gaps,
    }

    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
