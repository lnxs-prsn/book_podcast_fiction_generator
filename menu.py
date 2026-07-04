"""Interactive terminal launcher for the pipeline tools."""

import os
import sys
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a .env file at module import time.
# DOTENV_PATH can be used to point at a specific env file.
load_dotenv(os.environ.get("DOTENV_PATH", ".env"))

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from format_adapters import registered_extensions  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

PODCAST_MODES_FULL = ["2person", "4person", "code", "realworld", "fiction_meta"]
PODCAST_MODES_BOOK = ["2person", "4person", "code", "realworld"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    """Prompt the user and return stripped input."""
    try:
        value = input(prompt)
        return value.strip() if value.strip() else default
    except EOFError:
        return default


def yes_no(prompt: str, default: bool = True) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    raw = ask(f"{prompt} {hint}: ", "")
    if not raw:
        return default
    return raw.lower() in ("y", "yes")


def ask_pdf(label: str) -> Path:
    for attempt in range(1, 4):
        raw = ask(f"{label}: ")
        p = Path(raw).expanduser()
        if p.exists() and p.suffix.lower() in registered_extensions():
            return p.resolve()
        if not p.exists():
            print(f"  Error: file not found: {p}")
        else:
            print(f"  Error: not a supported source file: {p}")
        if attempt == 3:
            print("  Too many invalid attempts. Aborting.")
            return None
    return None


def ask_menu_choice(label: str, options: list[str], default: int = 1) -> str | None:
    print(f"\n{label}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = ask(f"Choice [{default}]: ", str(default))
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  Invalid choice — enter a number between 1 and {len(options)}.")


def multiline_input(prompt: str) -> str:
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines).strip()


def launch(cmd: list[str], cwd: str | None = None) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)
    env["HARNESS_ROOT"] = str(SRC_DIR)

    print("\n--- Launching ---")
    print("  " + " ".join(str(c) for c in cmd))
    print()

    result = subprocess.run(cmd, env=env, cwd=cwd)

    print()
    if result.returncode == 0:
        print("Done.")
    else:
        print(f"Exited with code {result.returncode}.")


def return_to_menu() -> bool:
    return yes_no("\nReturn to main menu?", default=True)


# ---------------------------------------------------------------------------
# Environment check
# ---------------------------------------------------------------------------

def preflight() -> None:
    warnings = []

    if sys.version_info < (3, 10):
        warnings.append(
            f"Warning: Python {sys.version_info.major}.{sys.version_info.minor} detected; 3.10+ recommended."
        )

    if not SRC_DIR.exists():
        print("Error: src/ directory not found. Cannot continue.")
        sys.exit(1)

    if not os.environ.get("OPENROUTER_API_KEY"):
        warnings.append("Warning: OPENROUTER_API_KEY is not set.")

    for w in warnings:
        print(w)


# ---------------------------------------------------------------------------
# Flow 1 — Podcast: Single Chapter
# ---------------------------------------------------------------------------

def flow_podcast_single() -> None:
    pdf = ask_pdf("PDF file path")
    if pdf is None:
        return

    mode_labels = [
        "2person       — two-host conversation",
        "4person       — four-host panel",
        "code          — code-focused discussion",
        "realworld     — real-world application",
        "fiction_meta  — fiction metadata episode",
    ]
    mode_choice = ask_menu_choice("Mode", mode_labels, default=1)
    mode = mode_choice.split()[0]

    audio = yes_no("Generate audio?", default=True)
    extra_context = yes_no("Add extra context?", default=False)
    context_text = ""
    if extra_context:
        context_text = multiline_input("Paste context (press Enter twice to finish):")

    print("\n--- Ready to run ---")
    print(f"  PDF:   {pdf}")
    print(f"  Mode:  {mode}")
    print(f"  Audio: {'yes' if audio else 'no'}")

    if not yes_no("Run?", default=True):
        return

    cmd = [sys.executable, str(SRC_DIR / "cli" / "podcast.py"), str(pdf), "--mode", mode]
    if not audio:
        cmd.append("--skip-audio")
    if context_text:
        cmd += ["--context", context_text]

    launch(cmd)
    return_to_menu()


# ---------------------------------------------------------------------------
# Flow 2 — Podcast: Full Book
# ---------------------------------------------------------------------------

def flow_podcast_book() -> None:
    pdf = ask_pdf("Book PDF path")
    if pdf is None:
        return

    mode_labels = ["2person", "4person", "code", "realworld"]
    mode = ask_menu_choice("Mode", mode_labels, default=1)

    toc_raw = ask("Table of contents page number (press Enter to auto-detect): ", "")
    toc_page = toc_raw if toc_raw.isdigit() else None

    audio = yes_no("Generate audio?", default=True)
    slice_only = yes_no("Slice chapters only, skip script and audio generation?", default=False)
    force = yes_no("Force regeneration of existing chapters?", default=False)

    print("\n--- Ready to run ---")
    print(f"  Book:        {pdf}")
    print(f"  Mode:        {mode}")
    print(f"  TOC page:    {toc_page if toc_page else 'auto-detect'}")
    print(f"  Audio:       {'yes' if audio else 'no'}")
    print(f"  Slice only:  {'yes' if slice_only else 'no'}")
    print(f"  Force:       {'yes' if force else 'no'}")

    if not yes_no("Run?", default=True):
        return

    cmd = [sys.executable, str(SRC_DIR / "cli" / "podcast.py"), "--book", str(pdf), "--mode", mode]
    if toc_page:
        cmd += ["--toc-page", toc_page]
    if not audio:
        cmd.append("--skip-audio")
    if slice_only:
        cmd.append("--slice-only")
    if force:
        cmd.append("--force")

    launch(cmd)
    return_to_menu()


# ---------------------------------------------------------------------------
# Flow 3 — Fiction: Generate Chapters
# ---------------------------------------------------------------------------

def flow_fiction_generate() -> None:
    configs = sorted(PROJECT_ROOT.rglob("config.toml"))

    config_path: Path | None = None

    if not configs:
        raw = ask("Config file path (none found automatically): ")
        p = Path(raw).expanduser()
        if not p.exists():
            print(f"  Error: file not found: {p}")
            return
        config_path = p.resolve()
    elif len(configs) == 1:
        print(f"\nFound config: {configs[0].relative_to(PROJECT_ROOT)}")
        if not yes_no("Use this config?", default=True):
            raw = ask("Config file path: ")
            p = Path(raw).expanduser()
            if not p.exists():
                print(f"  Error: file not found: {p}")
                return
            config_path = p.resolve()
        else:
            config_path = configs[0]
    else:
        options = [str(c.relative_to(PROJECT_ROOT)) for c in configs] + ["Enter path manually"]
        print("\nAvailable config files:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        while True:
            raw = ask(f"Choice [1]: ", "1")
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                idx = int(raw) - 1
                if idx == len(configs):
                    manual = ask("Config file path: ")
                    p = Path(manual).expanduser()
                    if not p.exists():
                        print(f"  Error: file not found: {p}")
                        return
                    config_path = p.resolve()
                else:
                    config_path = configs[idx]
                break
            print(f"  Invalid choice — enter 1–{len(options)}.")

    # Resume — only ask if state file exists
    resume = False
    state_file = config_path.parent / ".pipeline_state.json"
    if state_file.exists():
        resume = yes_no("Resume from last saved state?", default=False)

    chapter_start: str | None = None
    if yes_no("Start from a specific chapter number?", default=False):
        while True:
            raw = ask("Chapter number: ")
            if raw.isdigit() and int(raw) > 0:
                chapter_start = raw
                break
            print("  Error: enter a positive integer.")

    auto_approve = yes_no("Auto-approve each chapter without prompting?", default=False)
    dry_run = yes_no("Dry run (no real API calls, no cost)?", default=False)
    ignore_cost = yes_no("Ignore cost limit?", default=False)
    if ignore_cost:
        print("Warning: cost limit disabled.")

    print("\n--- Ready to run ---")
    print(f"  Config:        {config_path.relative_to(PROJECT_ROOT) if config_path.is_relative_to(PROJECT_ROOT) else config_path}")
    print(f"  Resume:        {'yes' if resume else 'no'}")
    print(f"  Chapter start: {chapter_start if chapter_start else '(none)'}")
    print(f"  Auto-approve:  {'yes' if auto_approve else 'no'}")
    print(f"  Dry run:       {'yes' if dry_run else 'no'}")
    print(f"  Cost limit:    {'disabled' if ignore_cost else 'enforced'}")

    if not yes_no("Run?", default=True):
        return

    cmd = [sys.executable, str(SRC_DIR / "cli" / "fiction.py"), "--config", str(config_path)]
    if resume:
        cmd.append("--resume")
    if chapter_start:
        cmd += ["--chapter-start", chapter_start]
    if auto_approve:
        cmd.append("--auto-approve")
    if dry_run:
        cmd.append("--dry-run")
    if ignore_cost:
        cmd.append("--ignore-cost-limit")

    launch(cmd)
    return_to_menu()


# ---------------------------------------------------------------------------
# Flow 4 — Fiction: New Project (Seed Gen)
# ---------------------------------------------------------------------------

def flow_fiction_seed() -> None:
    pdf = ask_pdf("Source book PDF (used to extract concepts and genre)")
    if pdf is None:
        return

    output_dir_raw = ask("Output directory for new project files: ")
    output_dir = Path(output_dir_raw).expanduser()

    if not output_dir.exists():
        if yes_no(f"  Directory does not exist. Create it?", default=True):
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            print("  Aborting.")
            return

    output_dir = output_dir.resolve()

    print("\n--- Ready to run ---")
    print(f"  Source PDF:  {pdf}")
    print(f"  Output dir:  {output_dir}/")
    print()
    print("  The seed generator will ask you further questions after launch")
    print("  (genre choice, protagonist, concepts).")

    if not yes_no("Run?", default=True):
        return

    cmd = [sys.executable, "-m", "fiction.seed_gen", str(pdf), str(output_dir)]
    launch(cmd)
    return_to_menu()


# ---------------------------------------------------------------------------
# Flow 5 — PDF Slicer
# ---------------------------------------------------------------------------

def flow_slicer() -> None:
    pdf = ask_pdf("Book PDF path")
    if pdf is None:
        return

    toc_raw = ask("TOC page number (press Enter for default 8): ", "")
    toc_page = toc_raw if toc_raw.isdigit() else None

    output_dir_raw = ask("Output directory (press Enter for default 'data/chapters'): ", "")
    output_dir = output_dir_raw if output_dir_raw else None

    chapters_only = yes_no("Skip front matter (keep only from Chapter 1 onward)?", default=False)
    dry_run = yes_no("Dry run (preview only, no files written)?", default=False)

    ocr_convert = False
    if not dry_run:
        print("\n  Warning: OCR conversion rewrites the whole scanned PDF to a searchable one.")
        print("  On a Raspberry Pi this can take 2–6 hours and will peg the CPU.")
        ocr_convert = yes_no("Enable full OCR conversion anyway?", default=False)

    print("\n--- Ready to run ---")
    print(f"  PDF:          {pdf}")
    print(f"  TOC page:     {toc_page if toc_page else 'auto (8)'}")
    print(f"  Output dir:   {output_dir if output_dir else 'data/chapters'}")
    print(f"  Chapters only:{' yes' if chapters_only else ' no'}")
    print(f"  Dry run:      {'yes' if dry_run else 'no'}")
    print(f"  OCR convert:  {'yes — this will be slow' if ocr_convert else 'no'}")

    if not yes_no("Run?", default=True):
        return

    cmd = [
        sys.executable, "-m", "slicer.pdf_splitter",
        "-i", str(pdf),
    ]
    if toc_page:
        cmd += ["-p", toc_page]
    if output_dir:
        cmd += ["-o", output_dir]
    else:
        cmd += ["-o", str(SRC_DIR / "data" / "chapters")]
    if chapters_only:
        cmd.append("--chapters-only")
    if dry_run:
        cmd.append("--dry-run")
    if ocr_convert:
        cmd.append("--ocr-convert")

    launch(cmd)
    return_to_menu()


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

MENU_OPTIONS = [
    ("Podcast  —  single chapter", flow_podcast_single),
    ("Podcast  —  full book", flow_podcast_book),
    ("Fiction  —  generate chapters", flow_fiction_generate),
    ("Fiction  —  new project (seed gen)", flow_fiction_seed),
    ("PDF Slicer  —  split book into chapters", flow_slicer),
    ("Quit", None),
]


def main_menu() -> None:
    while True:
        print("\n=== Pipeline Launcher ===\n")
        for i, (label, _) in enumerate(MENU_OPTIONS, 1):
            print(f"  {i}. {label}")
        print()
        raw = ask("Choice: ")
        if not raw.isdigit() or not (1 <= int(raw) <= len(MENU_OPTIONS)):
            print("  Invalid choice — enter a number from the menu.")
            continue
        idx = int(raw) - 1
        label, fn = MENU_OPTIONS[idx]
        if fn is None:
            print("Goodbye.")
            sys.exit(0)
        fn()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        preflight()
        main_menu()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
