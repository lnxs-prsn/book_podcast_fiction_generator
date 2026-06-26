import sys
from pathlib import Path

if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/podcast.py ..."
    )

import logging

CHAPTER_MODES = ["2person", "4person", "code", "realworld", "fiction_meta"]
BOOK_MODES    = ["2person", "4person", "code", "realworld"]


def main() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(message)s")

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

    # Path overrides (Pass 5.3)
    parser.add_argument("--scripts-out", type=Path, default=None)
    parser.add_argument("--audio-out", type=Path, default=None)
    parser.add_argument("--chapters-dir", type=Path, default=None)

    args = parser.parse_args()

    if args.book and args.pdf:
        parser.error("--book and pdf are mutually exclusive")

    if args.skip_script and not args.script_file:
        parser.error("--skip-script requires --script-file")

    if args.skip_script and args.book:
        parser.error("--skip-script cannot be used with --book")

    if args.book and args.mode == "fiction_meta":
        print("Error: --mode fiction_meta is not supported with --book", file=sys.stderr)
        sys.exit(1)

    # Resolve context
    context = args.context
    if args.context_file:
        context = Path(args.context_file).read_text(encoding="utf-8").strip()

    fiction_dir = Path(args.fiction_dir) if args.fiction_dir else None

    # Build settings with optional path overrides
    from settings import PodcastSettings
    settings = PodcastSettings(
        mode=args.mode,
        **({"scripts_out": args.scripts_out} if args.scripts_out else {}),
        **({"audio_out": args.audio_out} if args.audio_out else {}),
        **({"chapters_dir": args.chapters_dir} if args.chapters_dir else {}),
    )

    from engines.factory import default_audio_engine
    script_engine = None
    audio_engine = None if args.skip_audio else default_audio_engine()

    if args.book:
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
            book_pdf=Path(args.book),
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
                print(f"  error: {r.error}", file=sys.stderr)
        if fail_count:
            sys.exit(1)

    else:
        if not args.skip_script and not args.pdf:
            parser.error("pdf argument is required unless --book or --skip-script is given")
        from endpoints.podcast import generate_chapter_podcast
        r = generate_chapter_podcast(
            Path(args.pdf) if args.pdf else None,
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
            print(f"Error: {r.error}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        raise SystemExit(1)
