"""Section 3: read_prompt — read a UTF-8 prompt text file."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
VALID_MODES = ("2person", "4person", "code", "realworld", "fiction_meta")


def resolve_prompt_path(mode: str) -> str:
    """Return the absolute path to the prompt file for the given mode.

    Raises ValueError for unknown modes, FileNotFoundError if the file is missing.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Valid modes: {', '.join(VALID_MODES)}")
    path = PROMPTS_DIR / f"mode_{mode}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return str(path)


def read_prompt(
    prompt_path: str,
    context: str | None = None,
    fiction_content: str | None = None,
) -> str:
    """Read the prompt file and return its contents with trailing whitespace stripped.

    If context is provided, substitutes {CURRENT_EVENT} (realworld mode).
    If fiction_content is provided, substitutes {FICTION_CONTENT} (fiction_meta mode).
    Raises ValueError (with the path) if the file cannot be opened or is empty.
    """
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise ValueError(f"Cannot open prompt file: {prompt_path}") from e

    content = content.rstrip()

    if not content:
        raise ValueError(f"Prompt file is empty: {prompt_path}")

    if context is not None:
        content = content.replace("{CURRENT_EVENT}", context)

    if fiction_content is not None:
        content = content.replace("{FICTION_CONTENT}", fiction_content)

    return content
