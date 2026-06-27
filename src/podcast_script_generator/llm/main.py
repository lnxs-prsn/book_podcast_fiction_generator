"""Section 7: main.py — wire the pipeline.

Usage:
    python main.py <pdf_path> <output_dir>

Environment:
    OPENROUTER_API_KEY  required for the API call (via llm.env.resolve_from_env).
"""

import logging
import sys

from llm.env import resolve_from_env
from llm.exceptions import LLMConfigError
from llm.factory import create_client
from llm.protocol import LLMClient

try:
    from podcast_script_generator.llm.parse_args import parse_args
    from podcast_script_generator.llm.extract_pdf import extract_pdf
    from podcast_script_generator.llm.read_prompt import read_prompt
    from podcast_script_generator.llm.call_api import call_api
    from podcast_script_generator.llm.parse_output import parse_output
    from podcast_script_generator.llm.save_output import save_output
    from podcast_script_generator.llm.exceptions import PodcastError
except ImportError:
    from parse_args import parse_args
    from extract_pdf import extract_pdf
    from read_prompt import read_prompt
    from call_api import call_api
    from parse_output import parse_output
    from save_output import save_output
    from podcast_script_generator.llm.exceptions import PodcastError

logger = logging.getLogger(__name__)


def main(llm: LLMClient | None = None) -> None:
    pdf_path, prompt_path, output_dir, context = parse_args()
    pdf_text = extract_pdf(pdf_path)
    prompt_text = read_prompt(prompt_path, context)

    if llm is None:
        try:
            llm = create_client(**resolve_from_env())
        except LLMConfigError as e:
            sys.stderr.write(f"Error: {e}\n")
            raise SystemExit(1)

    response_text = call_api(pdf_text, prompt_text, llm)
    files = parse_output(response_text)
    save_output(files, output_dir)
    print(f"Wrote {len(files)} files to {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except PodcastError as e:
        sys.stderr.write(f"Error: {e}\n")
        raise SystemExit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        logger.exception("Unhandled exception in main")
        raise SystemExit(1)
