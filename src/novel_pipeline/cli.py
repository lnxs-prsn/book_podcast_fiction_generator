"""CLI entry point.

Exit codes:
  0  success
  1  user abort / KeyboardInterrupt / cost limit / rejection-limit reached
  2  config error (incl. ResumeStateError, PromotionCollisionError)
  3  API error after retries / context overflow / unexpected error
"""

from __future__ import annotations

import argparse
import sys
import traceback

from llm.env import resolve_from_env
from llm.exceptions import LLMConfigError
from llm.factory import create_transport

from .config import load_config
from .exceptions import (
    APIResponseError,
    ConfigError,
    ContextOverflowError,
    CostLimitError,
    DocumentLoadError,
    PromotionCollisionError,
    RejectionLimitReachedError,
    ResumeStateError,
)
from .logging_ import configure as configure_log
from .logging_ import log_event
from .session import run_session, ApproveChapterFn
from .prompt import prompt_user


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="novel-pipeline",
        description=(
            "Pedagogical-novel writing pipeline. Generates chapters via "
            "OpenRouter, gates on human approval, maintains a living doc."
        ),
    )
    p.add_argument(
        "--config",
        required=True,
        help="Path to TOML config file.",
    )
    p.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip all interactive prompts (use with care).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the loop without writing files or calling the API.",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing chapters; detect interrupt-mid-cycle.",
    )
    p.add_argument(
        "--chapter-start",
        type=int,
        default=None,
        metavar="N",
        help="Force the starting chapter number (overrides gap-scan).",
    )
    p.add_argument(
        "--ignore-cost-limit",
        action="store_true",
        help="Bypass the session/lifetime cost gate.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    approve_fn: ApproveChapterFn = (lambda n, t: True) if args.auto_approve else prompt_user

    # --- Config + logging ---
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2

    configure_log(config["log_path"])
    log_event(
        "cli_start",
        {
            "config_path": args.config,
            "auto_approve": args.auto_approve,
            "dry_run": args.dry_run,
            "resume": args.resume,
            "chapter_start": args.chapter_start,
            "ignore_cost_limit": args.ignore_cost_limit,
        },
    )

    # --- Build transport (wiring origin) ---
    cfg_kwargs = {
        "api_key": config.get("api_key"),
        "model": config["model"],
        "api_url": config.get("api_url"),
        "max_retries": config["max_retries"],
        "backoff_seconds": tuple(config["retry_backoff_seconds"]),
        "jitter_max": config["retry_jitter_seconds_max"],
        "max_tokens": config.get("max_tokens"),
        "retry_after_override": config.get("retry_after_seconds"),
    }
    try:
        client = create_transport(**{**cfg_kwargs, **resolve_from_env()})
    except LLMConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2
    timeout = config.get("timeout_seconds")

    # --- Run ---
    try:
        run_session(
            config,
            client,
            timeout,
            auto_approve=args.auto_approve,
            dry_run=args.dry_run,
            resume=args.resume,
            chapter_start=args.chapter_start,
            ignore_cost_limit=args.ignore_cost_limit,
            approve_chapter=approve_fn,
        )
    except KeyboardInterrupt:
        print("\nInterrupted. State preserved. Exit code 1.", file=sys.stderr)
        return 1
    except ResumeStateError as e:
        print(f"Resume state error: {e}", file=sys.stderr)
        log_event("cli_resume_state_error", {"error": str(e)})
        return 2
    except PromotionCollisionError as e:
        print(f"Promotion collision (state drift): {e}", file=sys.stderr)
        log_event("cli_promotion_collision", {"error": str(e)})
        return 2
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2
    except DocumentLoadError as e:
        print(f"Document load error: {e}", file=sys.stderr)
        log_event("cli_document_load_error", {"error": str(e)})
        return 2
    except CostLimitError as e:
        print(f"Cost limit hit: {e}", file=sys.stderr)
        log_event("cli_cost_limit", {"error": str(e)})
        return 1
    except RejectionLimitReachedError as e:
        print(f"Rejection limit reached: {e}", file=sys.stderr)
        log_event("cli_rejection_limit_reached", {"error": str(e)})
        return 1
    except ContextOverflowError as e:
        print(str(e), file=sys.stderr)
        log_event("cli_context_overflow", {})
        return 3
    except APIResponseError as e:
        print(f"API error after retries: {e}", file=sys.stderr)
        log_event("cli_api_error", {"error": str(e)})
        return 3
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        log_event(
            "cli_unexpected_error",
            {"error": str(e), "traceback": traceback.format_exc()},
        )
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
