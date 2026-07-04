import re
from pathlib import Path

from endpoints.podcast_types import PodcastResult
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from llm.exceptions import LLMConfigError, LLMError
from podcast_script_generator.llm.exceptions import ScriptGenerationError
from settings import PodcastSettings

def generate_chapter_podcast(
    source_path: Path | None = None,
    *,
    script_path: Path | None = None,
    script_engine: ScriptEngine | None = None,
    audio_engine: AudioEngine | None = None,
    settings: PodcastSettings | None = None,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    fiction_dir: Path | None = None,
) -> PodcastResult:
    if settings is None:
        raise TypeError("settings is required")

    try:
        if script_path is not None:
            script_path = Path(script_path).resolve()
            if not script_path.exists():
                return PodcastResult(error=FileNotFoundError(f"Script not found: {script_path}"))
            script_out = script_path
            naming_path = script_path
        else:
            if source_path is None:
                return PodcastResult(error=ValueError("source_path is required when not using --skip-script"))
            source_path = Path(source_path).resolve()
            if not source_path.exists():
                return PodcastResult(error=FileNotFoundError(f"Source file not found: {source_path}"))

            if mode == "realworld" and not context:
                return PodcastResult(error=ValueError("mode 'realworld' requires context"))

            if script_engine is None:
                from engines.factory import default_llm_script_engine
                script_engine = default_llm_script_engine(mode=mode)

            try:
                script_text = script_engine.generate(
                    source_path,
                    context=context,
                    fiction_dir=fiction_dir,
                )
            except LLMError as e:
                raise ScriptGenerationError(str(e)) from e

            script_out = settings.script_path_for(source_path)
            script_out.parent.mkdir(parents=True, exist_ok=True)
            script_out.write_text(script_text, encoding="utf-8")
            naming_path = source_path

        if skip_audio:
            return PodcastResult(script_path=script_out)

        if audio_engine is None:
            from engines.factory import default_audio_engine
            audio_engine = default_audio_engine()

        audio_dir = settings.audio_dir_for(naming_path)
        audio_path = audio_engine.generate(script_out, audio_dir, mode=mode)
        return PodcastResult(script_path=script_out, audio_path=audio_path)

    except Exception as e:
        return PodcastResult(error=e)


def generate_book_podcast(
    book_path: Path | None = None,
    chapters_dir: Path | None = None,
    toc_page: int | None = None,
    *,
    script_engine: ScriptEngine | None = None,
    audio_engine: AudioEngine | None = None,
    splitter_engine: SplitterEngine | None = None,
    settings: PodcastSettings | None = None,
    no_ocr: bool = False,
    force: bool = False,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    slice_only: bool = False,
) -> list[PodcastResult]:
    settings = settings or PodcastSettings()

    if toc_page is None:
        from config import load_config
        toc_page = load_config().get("toc_page")

    if book_path is not None:
        book_path = Path(book_path).resolve()
        if splitter_engine is None:
            from engines.factory import default_splitter_engine
            try:
                splitter_engine = default_splitter_engine(book_path)
            except LLMConfigError as e:
                return [PodcastResult(error=e)]
        chapters_out = settings.chapters_dir
        existing = list(chapters_out.glob(splitter_engine.chapter_glob)) if chapters_out.exists() else []
        if force or not existing:
            chapters_out.mkdir(parents=True, exist_ok=True)
            splitter_engine.split(
                book_path,
                toc_page=toc_page,
                output_dir=chapters_out,
                no_ocr=no_ocr,
            )

    if slice_only:
        return [PodcastResult()]

    resolve_dir = chapters_dir or settings.chapters_dir
    if not resolve_dir or not resolve_dir.exists():
        return []

    if script_engine is None:
        from engines.factory import default_llm_script_engine
        try:
            script_engine = default_llm_script_engine(mode=mode)
        except LLMConfigError as e:
            return [PodcastResult(error=e)]

    glob_pattern = splitter_engine.chapter_glob if splitter_engine is not None else "*"
    chapters = sorted(
        resolve_dir.glob(glob_pattern),
        key=lambda p: [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", p.stem)],
    )

    results = []
    for chapter in chapters:
        r = generate_chapter_podcast(
            chapter,
            script_engine=script_engine,
            audio_engine=audio_engine,
            settings=settings,
            skip_audio=skip_audio,
            mode=mode,
            context=context,
        )
        results.append(r)
    return results
