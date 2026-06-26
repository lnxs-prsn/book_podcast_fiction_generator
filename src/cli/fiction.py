import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from novel_pipeline.exceptions import ConfigError

if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/fiction.py ..."
    )

import logging

from path_utils import resolve_data_root

logger = logging.getLogger(__name__)


def _configure_logging(root: Path) -> None:
    """Configure console + rotating-file logging driven by LOG_LEVEL env var."""
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "cli-fiction.log"

    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    fh = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.NOTSET)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.getLogger().addHandler(fh)


def main() -> None:
    import argparse

    root: Path = resolve_data_root()
    _configure_logging(root)

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
        logger.error("Interrupted. State preserved.")
        sys.exit(1)
    except ConfigError as e:
        logger.error("Config error: %s", e)
        sys.exit(2)
    except Exception as e:
        logger.error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
