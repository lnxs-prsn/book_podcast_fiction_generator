import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/podcast.py ..."
    )

import logging

from path_utils import resolve_data_root, resolve_input_path, resolve_output_path

CHAPTER_MODES = ["2person", "4person", "code", "realworld", "fiction_meta"]
BOOK_MODES    = ["2person", "4person", "code", "realworld"]

logger = logging.getLogger(__name__)


def _configure_logging(root: Path) -> None:
    """Configure console + rotating-file logging driven by LOG_LEVEL env var."""
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "cli-podcast.log"

    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    fh = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.NOTSET)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.getLogger().addHandler(fh)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="podcast generation pipeline")

    # Chapter flags
    parser.add_argument("pdf", nargs="?", default=None, help="PDF file for single chapter")
    parser.add_argument("--skip-audio", action="store_true")
    parser.add_argument("--skip-script", action="store_true")
    parser.add_argument("--script-file", type=Path, default=None,
                        help="Existing script to use instead of generating one (requires --skip-script)")
    parser.add_argument("--mode", choices=CHAPTER_MODES, default="2person")
    parser.add_argument("--context", default=None)
    parser.add_argument("--context-file", default=None)
    parser.add_argument("--fiction-dir", default=None)

    # Book flags
    parser.add_argument("--book", default=None, metavar="PDF")
    parser.add_argument("--toc-page", type=int, default=None)
    parser.add_argument("--no-ocr", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--slice-only", action="store_true")

    # Path overrides
    parser.add_argument("--root", type=Path, default=None,
                        help="Project root directory (default: HARNESS_ROOT env var or src/)")
    parser.add_argument("--scripts-out", type=Path, default=None)
    parser.add_argument("--audio-out", type=Path, default=None)
    parser.add_argument("--chapters-dir", type=Path, default=None)

    args = parser.parse_args()

    # Resolve project root first so logging can use it
    root: Path = args.root.resolve() if args.root else resolve_data_root()

    _configure_logging(root)

    logger.debug("Project root resolved to %s", root)

    if args.book and args.pdf:
        parser.error("--book and pdf are mutually exclusive")

    if args.skip_script and not args.script_file:
        parser.error("--skip-script requires --script-file")

    if args.skip_script and args.book:
        parser.error("--skip-script cannot be used with --book")

    if args.book and args.mode == "fiction_meta":
        logger.error("--mode fiction_meta is not supported with --book")
        sys.exit(1)

    # Validate and resolve output path overrides BEFORE any API call
    scripts_out: Path | None = None
    audio_out: Path | None = None
    chapters_dir: Path | None = None

    if args.scripts_out is not None:
        try:
            scripts_out = resolve_output_path(args.scripts_out, root, allow_escape=False)
        except ValueError as e:
            logger.error("Invalid --scripts-out path: %s", e)
            sys.exit(1)

    if args.audio_out is not None:
        try:
            audio_out = resolve_output_path(args.audio_out, root, allow_escape=False)
        except ValueError as e:
            logger.error("Invalid --audio-out path: %s", e)
            sys.exit(1)

    if args.chapters_dir is not None:
        try:
            chapters_dir = resolve_output_path(args.chapters_dir, root, allow_escape=False)
        except ValueError as e:
            logger.error("Invalid --chapters-dir path: %s", e)
            sys.exit(1)

    # Validate input PDF (allow_escape=True — PDF may come from outside HARNESS_ROOT)
    if args.pdf is not None:
        try:
            pdf_path = resolve_input_path(args.pdf, root, allow_escape=True, must_exist=True)
        except FileNotFoundError as e:
            logger.error("Input PDF not found: %s", e)
            sys.exit(1)
    else:
        pdf_path = None

    if args.book is not None:
        try:
            book_path = resolve_input_path(args.book, root, allow_escape=True, must_exist=True)
        except FileNotFoundError as e:
            logger.error("Input book PDF not found: %s", e)
            sys.exit(1)
    else:
        book_path = None

    # Resolve context
    context = args.context
    if args.context_file:
        context = Path(args.context_file).read_text(encoding="utf-8").strip()

    fiction_dir = Path(args.fiction_dir) if args.fiction_dir else None

    # Build settings with resolved root and optional path overrides
    from settings import PodcastSettings
    settings = PodcastSettings(
        root=root,
        mode=args.mode,
        **({"scripts_out": scripts_out} if scripts_out is not None else {}),
        **({"audio_out": audio_out} if audio_out is not None else {}),
        **({"chapters_dir": chapters_dir} if chapters_dir is not None else {}),
    )

    from engines.factory import default_audio_engine
    script_engine = None
    audio_engine = None if args.skip_audio else default_audio_engine()

    if book_path:
        # Interactive toc_page prompt if not provided
        if args.toc_page is None:
            try:
                toc_page = int(input("TOC page number: "))
            except (ValueError, EOFError):
                toc_page = None
        else:
            toc_page = args.toc_page

        from endpoints.podcast import generate_book_podcast
        results = generate_book_podcast(
            book_pdf=book_path,
            toc_page=toc_page,
            script_engine=script_engine,
            audio_engine=audio_engine,
            settings=settings,
            no_ocr=args.no_ocr,
            force=args.force,
            skip_audio=args.skip_audio,
            mode=args.mode,
            context=context,
            slice_only=args.slice_only,
        )
        ok_count = sum(1 for r in results if r.ok)
        fail_count = len(results) - ok_count
        print(f"Book complete: {ok_count} ok, {fail_count} failed")
        for r in results:
            if r.ok and r.script_path:
                print(f"  script: {r.script_path}")
            elif not r.ok:
                logger.error("chapter error: %s", r.error)
        if fail_count:
            sys.exit(1)

    else:
        if not args.skip_script and pdf_path is None:
            parser.error("pdf argument is required unless --book or --skip-script is given")
        from endpoints.podcast import generate_chapter_podcast
        r = generate_chapter_podcast(
            pdf_path,
            script_path=args.script_file,
            script_engine=script_engine,
            audio_engine=audio_engine,
            settings=settings,
            skip_audio=args.skip_audio,
            mode=args.mode,
            context=context,
            fiction_dir=fiction_dir,
        )
        if r.ok:
            if r.script_path:
                print(f"script: {r.script_path}")
            if r.audio_path:
                print(f"audio:  {r.audio_path}")
        else:
            logger.error("Error: %s", r.error)
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        logger.exception("Unhandled exception")
        raise SystemExit(1)
