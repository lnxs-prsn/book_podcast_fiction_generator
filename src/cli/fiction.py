import sys
from pathlib import Path

from novel_pipeline.exceptions import ConfigError

if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/fiction.py ..."
    )

import logging


def main() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Novel fiction pipeline")
    parser.add_argument("--config", required=True, help="Path to TOML config file")
    parser.add_argument("--auto-approve", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--chapter-start", type=int, default=None)
    parser.add_argument("--ignore-cost-limit", action="store_true")

    args = parser.parse_args()

    from novel_pipeline.prompt import prompt_user
    from endpoints.fiction import run_novel_session

    approve_fn = (lambda n, t: True) if args.auto_approve else prompt_user

    try:
        result = run_novel_session(
            config_path=args.config,
            resume=args.resume,
            auto_approve=args.auto_approve,
            dry_run=args.dry_run,
            chapter_start=args.chapter_start,
            ignore_cost_limit=args.ignore_cost_limit,
            approve_chapter=approve_fn,
        )
        print(f"Session complete. Chapters written: {result.chapters_written}")
    except KeyboardInterrupt:
        print("\nInterrupted. State preserved.", file=sys.stderr)
        sys.exit(1)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
