"""Bridge: assembled_prompt.md → call_api() → chapter_draft.md.

Usage (from project root):
  PYTHONPATH=src src/.venv/bin/python fiction_loop/tools/invoke_writer.py \\
    --prompt fiction_loop/prompts/assembled_prompt.md \\
    --config fiction_loop/tools/pipeline_config.toml \\
    --output fiction_loop/prompts/chapter_draft.md
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path


def _load_dotenv_fallback() -> None:
    """Minimal .env fallback: if repo-root .env exists, set any KEY=VALUE lines
    not already present in the environment (shell env always wins)."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v


_load_dotenv_fallback()

# ---------------------------------------------------------------------------
# src/ imports (PYTHONPATH=src required)
# ---------------------------------------------------------------------------
try:
    from novel_pipeline.config import load_config
    from novel_pipeline.api import call_api
    from novel_pipeline.exceptions import (
        ContextOverflowError,
        CostLimitError,
        ChapterValidationError,
        APIResponseError,
        APIRateLimitError,
        ConfigError,
    )
    from llm.factory import create_transport
    from llm.env import resolve_from_env
    from llm.exceptions import LLMConfigError
except ImportError as e:
    print(
        f"Import error: {e}\n"
        "Run with PYTHONPATH=src, e.g.:\n"
        "  PYTHONPATH=src src/.venv/bin/python fiction_loop/tools/invoke_writer.py ...",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def build_messages(assembled_prompt: str, config: dict) -> list[dict]:
    return [
        {"role": "system", "content": config["system_prompt_generate_chapter"]},
        {"role": "user",   "content": assembled_prompt},
    ]


def validate_word_count(text: str, min_words: int) -> None:
    wc = len(text.split())
    if wc < min_words:
        raise ChapterValidationError(
            f"Chapter too short: {wc} words, minimum {min_words}. "
            f"First 200 chars: {text[:200]!r}"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="fiction_loop Writer bridge")
    p.add_argument("--prompt", required=True, help="Path to assembled_prompt.md")
    p.add_argument("--config", required=True, help="Path to pipeline_config.toml")
    p.add_argument("--output", required=True, help="Where to write chapter_draft.md")
    p.add_argument(
        "--ignore-cost-limit",
        action="store_true",
        default=False,
        help="Skip cost-limit enforcement",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    try:
        # 1. Load config
        try:
            config = load_config(args.config)
        except FileNotFoundError:
            print(f"Config not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        except ConfigError as e:
            print(f"Config error: {e}", file=sys.stderr)
            sys.exit(1)

        from novel_pipeline.logging_ import configure as _configure_log
        _configure_log(config["log_path"])

        # 2. Env overrides — env always wins (resolve_from_env only returns
        # non-empty values; filtering on `k in config` would drop api_key,
        # which the TOML never defines).
        env = resolve_from_env()
        config = {**config, **env}

        # 3. Build transport
        try:
            transport = create_transport(
                api_key=config.get("api_key"),
                model=config["model"],
                api_url=config.get("api_url"),
                max_retries=config["max_retries"],
                backoff_seconds=tuple(config["retry_backoff_seconds"]),
                jitter_max=config["retry_jitter_seconds_max"],
            )
        except LLMConfigError as e:
            print(
                f"LLM config error: {e}. Check OPENROUTER_API_KEY.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 4. Read assembled prompt
        prompt_path = Path(args.prompt)
        if not prompt_path.exists():
            print(
                f"assembled_prompt.md not found at {args.prompt}. "
                "Run Assembler first.",
                file=sys.stderr,
            )
            sys.exit(1)
        assembled = prompt_path.read_text(encoding="utf-8")

        # 5. Build messages and call API
        messages = build_messages(assembled, config)
        chapter = call_api(
            messages,
            config["model"],
            config,
            client=transport,
            timeout=config.get("timeout_seconds"),
            expected_output_tokens=config.get("expected_output_tokens_chapter"),
            ignore_cost_limit=args.ignore_cost_limit,
            task_label="generate_chapter",
        )

        # 6. Validate word count. A failed draft is a paid artifact — salvage it
        # to <output>.rejected.md instead of discarding, so it can be inspected
        # (and so --output never silently retains a PREVIOUS chapter's draft as
        # if it were this one).
        try:
            validate_word_count(chapter, int(config.get("min_chapter_words", 2000)))
        except ChapterValidationError:
            rejected = Path(str(args.output) + ".rejected.md")
            rejected.write_text(chapter, encoding="utf-8")
            print(f"Rejected draft salvaged to {rejected}", file=sys.stderr)
            raise

        # 7. Write output
        Path(args.output).write_text(chapter, encoding="utf-8")
        print(
            f"OK: {len(chapter.split())} words → {args.output}",
            file=sys.stderr,
        )
        sys.exit(0)

    except ContextOverflowError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except CostLimitError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except APIRateLimitError as e:
        print(f"Rate limit: {e}. All retries exhausted.", file=sys.stderr)
        sys.exit(1)
    except APIResponseError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except ChapterValidationError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception:
        print(f"Unexpected error:\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
