"""Section 1: parse_args — read and validate CLI args."""

import argparse
import os

try:
    from podcast_script_generator.llm.read_prompt import resolve_prompt_path, VALID_MODES
except ImportError:
    from read_prompt import resolve_prompt_path, VALID_MODES


def parse_args() -> tuple[str, str, str, str | None]:
    """Parse CLI args: pdf_path, output_dir, --mode, --context / --context-file.

    Returns (pdf_path, prompt_path, output_dir, context) where context is the
    substitution string for {CURRENT_EVENT} (realworld mode only) or None.

    - pdf_path must exist as a file (raises FileNotFoundError if not).
    - output_dir is created if it does not exist.
    - --mode defaults to '2person'.
    - --mode realworld requires --context or --context-file; exits with error if absent.
    """
    parser = argparse.ArgumentParser(
        description="Generate a podcast script from a PDF chapter."
    )
    parser.add_argument("pdf_path", help="Path to input PDF file.")
    parser.add_argument("output_dir", help="Directory to write output files.")
    parser.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default="2person",
        help="Podcast format mode (default: 2person).",
    )
    parser.add_argument(
        "--context",
        default=None,
        help="Real-world event text for realworld mode (inline string).",
    )
    parser.add_argument(
        "--context-file",
        dest="context_file",
        default=None,
        help="Path to a file containing the real-world event text for realworld mode.",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_path):
        raise FileNotFoundError(args.pdf_path)

    os.makedirs(args.output_dir, exist_ok=True)

    prompt_path = resolve_prompt_path(args.mode)

    context: str | None = None
    if args.mode == "realworld":
        if args.context:
            context = args.context
        elif args.context_file:
            if not os.path.isfile(args.context_file):
                raise FileNotFoundError(args.context_file)
            with open(args.context_file, "r", encoding="utf-8") as f:
                context = f.read().strip()
        else:
            raise ValueError("--mode realworld requires --context or --context-file")

    return args.pdf_path, prompt_path, args.output_dir, context
