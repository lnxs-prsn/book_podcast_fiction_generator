# Build Specs v10 — LLM-Only Podcast + Fiction Pipeline

> Derived from `build_specsv9.md`.
> v10 removes the local/template-based script generator entirely — LLM (OpenRouter)
> is the single script generation path. Also fixes three verified errors from v9.
> Nothing from any prior spec is assumed to be built; this is the single definitive spec.
>
> Each pass names every file touched, the change type (add / modify / delete), and a
> done condition. Passes within a phase are ordered; complete each pass before the next.

---

## Gap Index (v9 → v10)

| Gap | Severity | Fixed In |
|-----|----------|----------|
| Local/template-based generator removed; no quality benefit | High | Phase 3 (Pass 3.3 dropped) |
| `decide_later/` lives at project root, not `src/` — caused wrong `__init__.py` paths in v9 | High | Eliminated (local engine removed) |
| `slicer/` and `tts/` `__init__.py` missing from v9 Pass 3.0 | High | Pass 1.0 (new) |
| Phase 1.2 imported `podcast_script_generator.llm.exceptions` before its `__init__.py` existed | Medium | Pass 1.0 runs first; resolves ordering |
| Engine adapters carried unnecessary `package_path` / `sys.path` params | Low | Adapters simplified |
| v9 Pass 7.4 ("remove sys.path from adapters") was moot — adapters never had it | Low | Pass dropped; passes renumbered |
| v9 shimmed `run_chapter.py` / `run_book.py` after deleting their helpers — ordering risk | Low | Shim and helper removal merged into Pass 7.3 |

---

## Phase 0 — Invocation Model

**Goal**: Establish a single, consistent import model before any code is written.

---

### Pass 0.0 — PYTHONPATH Convention

**Root cause of the `sys.path.insert` proliferation**: `python src/cli/podcast.py` adds
`src/cli/` to `sys.path[0]`, not `src/`. Sibling-package imports fail. Earlier specs patched
this per-file. This spec fixes it once at the invocation level.

**Canonical invocation**:

```bash
PYTHONPATH=src python src/cli/podcast.py <args>
PYTHONPATH=src python src/cli/fiction.py <args>
```

**Persistent option** — add `.env` at `harnessv3/`:

```
PYTHONPATH=src
```

`uv run` reads this automatically. Plain `python` still requires the prefix or shell export.

**What this eliminates**: module-level `sys.path.insert` in all new files. Engine adapters
in v10 have no `sys.path` code at all — Pass 1.0's `__init__.py` files make every package
importable with `PYTHONPATH=src`.

**What this does NOT change**: `sys.path.insert` calls inside the function bodies of
`run_local()`, `run_llm()`, and `run_tts()` in the existing `run_chapter.py`, and inside
`run_book.py`. Both files are replaced by shims in Pass 7.3.

**`_SRC` / `_ROOT` constants** in `endpoints/podcast.py` — retained for output path
computation, not for `sys.path`:

```python
from pathlib import Path

_SRC  = Path(__file__).parent.parent        # src/
_ROOT = Path(__file__).parent.parent.parent  # harnessv3/
```

**Done**:
```
PYTHONPATH=src python -c "from config import load_config; print(load_config())"
# exits 0 after Pass 1.1 creates config.py
```

---

## Phase 1 — Foundation

**Goal**: Package structure, config loading, and exception hierarchy in place before any
endpoints are written. No behavior change to existing entry points.

---

### Pass 1.0 — Package Structure

**Goal**: Create all `__init__.py` files needed before Pass 1.2 imports from
`podcast_script_generator.llm.exceptions`.

| File | Change |
|------|--------|
| `src/podcast_script_generator/__init__.py` | add — empty |
| `src/podcast_script_generator/llm/__init__.py` | add — empty |
| `src/slicer/__init__.py` | add — empty |
| `src/tts/__init__.py` | add — empty |
| `src/util/__init__.py` | add — empty |
| `src/engines/__init__.py` | add — empty |
| `src/cli/__init__.py` | add — empty |
| `src/endpoints/__init__.py` | add — empty |

All files are empty. This pass must complete before Pass 1.2.

**Done**:
```
PYTHONPATH=src python -c "
import podcast_script_generator
import podcast_script_generator.llm
import slicer
import tts
print('ok')
"
# exits 0
```

---

### Pass 1.1 — Shared Config Loader

| File | Change |
|------|--------|
| `src/config.py` | add |
| `src/run_chapter.py` | modify — remove `_load_config()` definition; add `from config import load_config`; rename 1 call site |
| `src/run_book.py` | modify — same; rename 1 call site |
| `src/tts/cli.py` | modify — same; rename 3 call sites |
| `src/podcast_script_generator/llm/call_api.py` | modify — same; rename 4 call sites |

**`src/config.py` full implementation:**

```python
import json
from pathlib import Path

_DEFAULT_PATH = Path(__file__).parent / "config.json"

def load_config(path=None) -> dict:
    p = Path(path) if path else _DEFAULT_PATH
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
```

**Import pattern** — add guard comment immediately above the import in all four files:

```python
# If this import fails, do NOT add sys.path.insert here.
# The fix is: export PYTHONPATH=src (or prefix: PYTHONPATH=src python ...).
from config import load_config
```

**Call-site renames** (use `grep -n "_load_config"` to locate):
- `src/tts/cli.py`: 3 call sites in `build_api_payload()`, `send_to_api()`, `cli_entrypoint()`
- `src/podcast_script_generator/llm/call_api.py`: 4 call sites in the `_resolve_*()` helpers
- `src/run_chapter.py`: 1 call site in `run_tts()`
- `src/run_book.py`: 1 call site in `main()`

**Done**:
```
PYTHONPATH=src python -c "from config import load_config; print(load_config())"
# exits 0

PYTHONPATH=src python src/run_chapter.py --help
# still works

grep -rn "_load_config" src/run_chapter.py src/run_book.py src/tts/cli.py \
  src/podcast_script_generator/llm/call_api.py
# returns empty
```

---

### Pass 1.2 — Podcast Exception Hierarchy

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/exceptions.py` | add |
| `src/podcast_script_generator/llm/main.py` | modify — `sys.exit()` calls → typed raises; add `__main__` guard |
| `src/tts/cli.py` | modify — remap exceptions; broaden `cli_entrypoint()` catch |
| `src/run_chapter.py` | modify — catch `PodcastError` at CLI boundary |

**`src/podcast_script_generator/llm/exceptions.py` full content:**

```python
class PodcastError(Exception):
    pass

class PDFExtractionError(PodcastError):
    pass

class ScriptGenerationError(PodcastError):
    pass

class TTSSubmissionError(PodcastError):
    pass

class TTSTimeoutError(PodcastError):
    pass
```

**`tts/cli.py` remapping** — Pass 1.0 ensures `podcast_script_generator.llm` is a package:

```python
from podcast_script_generator.llm.exceptions import (
    PodcastError, TTSSubmissionError, TTSTimeoutError
)
```

- Delete local `AuthError` class definition.
- `raise AuthError(...)` → `raise TTSSubmissionError(...)`
- `raise RuntimeError(f"WaveSpeed job failed...")` → `raise TTSSubmissionError(...)`
- `raise ConnectionError(...)` → `raise TTSTimeoutError(...)`
- `cli_entrypoint()` catch: `(ValueError, AuthError, ConnectionError, RuntimeError, OSError)`
  → `(PodcastError, ValueError, OSError)`

**`main.py` `__main__` guard:**

```python
if __name__ == "__main__":
    try:
        main()
    except PodcastError as e:
        import sys
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

**Done**:
```
grep -rn "sys.exit" src/podcast_script_generator/ | grep -v "__main__"
# returns empty

grep "sys.exit" src/tts/cli.py
# hits only inside cli_entrypoint()

grep "sys.exit" src/run_chapter.py
# exactly one hit (CLI boundary catch)
```

---

### Pass 1.3 — Structured Logging Migration

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/call_api.py` | modify — `print(f"OpenRouter 429...")` → `logger.debug(...)` |
| `src/podcast_script_generator/llm/save_output.py` | modify — `print(f"Wrote N files...")` → `logger.debug(...)` |
| `src/tts/cli.py` | modify — convert 5 prints in `send_to_api()` to logger calls |
| `src/run_chapter.py` | modify — add `logging.basicConfig(level=logging.INFO, format="%(message)s")` |
| `src/run_book.py` | modify — same |

**Logger setup pattern** (add to each library file):

```python
import logging
logger = logging.getLogger(__name__)
```

**`tts/cli.py` print mapping** inside `send_to_api()`:
- Submission confirmation → `logger.info(...)`
- Recovery-file notice → `logger.info(...)` (conditional on `job_file`)
- Polling start → `logger.info(...)`
- Per-poll status → `logger.debug(...)`
- Completion confirmation → `logger.info(...)`

**Done**:
```
grep -rn "^\s*print(" src/podcast_script_generator/ src/tts/cli.py
# returns empty

PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# produces INFO-level output without crashing
```

---

## Phase 2 — Utilities + Types

---

### Pass 2.1 — Speaker Normalization Extract

| File | Change |
|------|--------|
| `src/util/normalize.py` | add — `normalize_speakers(text: str) -> str` |
| `src/run_chapter.py` | modify — delete `_to_speaker_format()` definition; update 3 call sites; add import |

Locate with: `grep -n "def _to_speaker_format" src/run_chapter.py`.
This pass extracts AND renames to `normalize_speakers`.

`src/util/__init__.py` already exists from Pass 1.0.

**Three call sites in `run_chapter.py`**:
- 1 inside `run_local()`
- 2 inside `run_llm()` (fiction_meta branch + all-other-modes branch)

**Import to add:**
```python
from util.normalize import normalize_speakers
```

**Done**:
```
PYTHONPATH=src python -c \
  "from util.normalize import normalize_speakers; print(normalize_speakers('ALEX: hi'))"
# exits 0

PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# behavior unchanged
```

---

### Pass 2.2 — Shared Podcast Types

| File | Change |
|------|--------|
| `src/endpoints/podcast_types.py` | add |

`src/endpoints/__init__.py` already exists from Pass 1.0.

**Pre-flight check:**
```
grep -rn "PodcastResult(ok=" src/
# must return empty before proceeding
```

**`src/endpoints/podcast_types.py` full content:**

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ScriptMode(str, Enum):
    TWO_PERSON = "2person"
    FOUR_PERSON = "4person"
    CODE = "code"
    REALWORLD = "realworld"
    FICTION_META = "fiction_meta"


@dataclass
class PodcastResult:
    script_path: Path | None = None
    audio_path: Path | None = None
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
```

`ok` is a read-only property. Constructor usage:
- Success with audio: `PodcastResult(script_path=script_out, audio_path=audio_path)`
- Success without audio: `PodcastResult(script_path=script_out)`
- Failure: `PodcastResult(error=some_exception)`
- `slice_only` success: `PodcastResult()`

**Done**:
```
PYTHONPATH=src python -c "
from endpoints.podcast_types import ScriptMode, PodcastResult
r = PodcastResult(error=ValueError('x'))
assert r.ok == False
r2 = PodcastResult(script_path=__import__('pathlib').Path('/tmp/x'))
assert r2.ok == True
print('ok')"
# exits 0
```

---

### Pass 2.3 — Shared Prompt Helper

| File | Change |
|------|--------|
| `src/util/prompt.py` | add |

```python
def prompt_user(chapter_num: int, draft_text: str) -> bool:
    print(f"Chapter {chapter_num} draft (first 500 chars):\n{draft_text[:500]}\n")
    choice = input("[y/n/q]: ").strip().lower()
    if choice == "q":
        raise KeyboardInterrupt
    return choice == "y"
```

`q` raises `KeyboardInterrupt`, propagating to `run_session()`'s existing handler.

**Done**:
```
PYTHONPATH=src python -c "from util.prompt import prompt_user; print('ok')"
# exits 0
```

---

## Phase 3 — Engine Protocols + Adapters

**Goal**: Wrap every concrete engine behind a protocol, inject them into endpoints.

Pass 3.0 (v9's "Package __init__.py Cleanup") is dropped — all `__init__.py` files are
created in Pass 1.0. Pass 3.3 (v9's `LocalScriptEngine`) is dropped — LLM is the only
generator. Remaining passes are renumbered.

---

### Pass 3.1 — Engine Protocols

| File | Change |
|------|--------|
| `src/engines/protocols.py` | add |

`src/engines/__init__.py` already exists from Pass 1.0.

**`src/engines/protocols.py` full content:**

```python
from typing import Protocol
from pathlib import Path


class ScriptEngine(Protocol):
    def generate(
        self,
        pdf_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str: ...


class AudioEngine(Protocol):
    def generate(
        self,
        script_path: Path,
        audio_dir: Path,
        *,
        mode: str = "2person",
    ) -> Path: ...


class SplitterEngine(Protocol):
    def split(
        self,
        book_pdf: Path,
        *,
        toc_page: int,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]: ...
```

**Done**:
```
PYTHONPATH=src python -c \
  "from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine; print('ok')"
# exits 0
```

---

### Pass 3.2 — PodcastSettings

| File | Change |
|------|--------|
| `src/settings.py` | add |

**`src/settings.py` full content:**

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PodcastSettings:
    """Path + behavior settings for the podcast pipeline."""

    root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    scripts_out: Path | None = None
    audio_out: Path | None = None
    chapters_dir: Path | None = None
    summary_out: Path | None = None

    def __post_init__(self) -> None:
        if self.scripts_out is None:
            self.scripts_out = self.root / "data" / "output" / "scripts"
        if self.audio_out is None:
            self.audio_out = self.root / "data" / "output" / "audio"
        if self.chapters_dir is None:
            self.chapters_dir = self.root / "data" / "chapters"
        if self.summary_out is None:
            self.summary_out = self.root / "data" / "output" / "run_summary.txt"

    def script_path_for(self, pdf_path: Path) -> Path:
        return self.scripts_out / f"{pdf_path.stem}_podcast.txt"

    def audio_dir_for(self, pdf_path: Path) -> Path:
        return self.audio_out / pdf_path.stem
```

**Done**:
```
PYTHONPATH=src python -c "
from settings import PodcastSettings
from pathlib import Path
s = PodcastSettings()
assert s.scripts_out.name == 'scripts'
assert s.script_path_for(Path('/tmp/01_chapter.pdf')).name == '01_chapter_podcast.txt'
print('ok')
"
# exits 0
```

---

### Pass 3.3 — LLM Script Engine

| File | Change |
|------|--------|
| `src/engines/llm_script.py` | add |

LLM is the only script engine. No `package_path` parameter — `PYTHONPATH=src` and the
`__init__.py` files from Pass 1.0 make all imports resolve without path surgery.

**`src/engines/llm_script.py` full content:**

```python
import re
from pathlib import Path

from engines.protocols import ScriptEngine


class LLMScriptEngine(ScriptEngine):
    """Adapter for the OpenRouter LLM script generator."""

    def __init__(self, mode: str = "2person") -> None:
        self.mode = mode

    def generate(
        self,
        pdf_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str:
        from podcast_script_generator.llm.extract_pdf import extract_pdf
        from podcast_script_generator.llm.read_prompt import read_prompt, resolve_prompt_path
        from podcast_script_generator.llm.call_api import call_api
        from util.normalize import normalize_speakers

        pdf_text = extract_pdf(str(pdf_path))
        fiction_content = self._resolve_fiction_content(pdf_path, fiction_dir)
        prompt = read_prompt(resolve_prompt_path(self.mode), context, fiction_content)

        if self.mode == "fiction_meta":
            prompt = prompt.replace("{TECHNICAL_CONTENT}", pdf_text)
            return normalize_speakers(call_api("", prompt))
        return normalize_speakers(call_api(pdf_text, prompt))

    def _resolve_fiction_content(
        self, pdf_path: Path, fiction_dir: Path | None
    ) -> str | None:
        if self.mode != "fiction_meta":
            return None
        if fiction_dir is None:
            raise ValueError("mode 'fiction_meta' requires fiction_dir")
        if not fiction_dir.is_dir():
            raise ValueError(f"fiction directory not found: {fiction_dir}")
        match = re.match(r"^(\d+)", pdf_path.stem)
        if not match:
            raise ValueError(
                f"cannot extract chapter number from PDF stem: {pdf_path.stem}"
            )
        chapter_num = int(match.group(1))
        fiction_file = fiction_dir / f"chapter_{chapter_num:02d}.md"
        if not fiction_file.exists():
            candidates = sorted(fiction_dir.glob(f"*{match.group(1)}*.md"))
            if not candidates:
                raise ValueError(
                    f"no fiction chapter found for chapter {chapter_num:02d} in {fiction_dir}"
                )
            fiction_file = candidates[0]
        return fiction_file.read_text(encoding="utf-8").strip()
```

**Done**:
```
PYTHONPATH=src python -c \
  "from engines.llm_script import LLMScriptEngine; print('ok')"
# exits 0
```

---

### Pass 3.4 — WaveSpeed Audio Engine

| File | Change |
|------|--------|
| `src/engines/wavespeed_audio.py` | add |

No `package_path` parameter — `src/tts/__init__.py` from Pass 1.0 makes `tts.cli`
importable with `PYTHONPATH=src`.

**`src/engines/wavespeed_audio.py` full content:**

```python
import os
from pathlib import Path
from typing import Any

from config import load_config
from engines.protocols import AudioEngine


class WaveSpeedAudioEngine(AudioEngine):
    """Adapter for the WaveSpeed VibeVoice TTS engine."""

    def __init__(self, speakers: dict[str, Any] | None = None) -> None:
        self._speakers = speakers

    def generate(
        self,
        script_path: Path,
        audio_dir: Path,
        *,
        mode: str = "2person",
    ) -> Path:
        from tts.cli import main as tts_main

        api_key = os.environ.get("WAVESPEED_API_KEY")
        if not api_key:
            raise RuntimeError(
                "WAVESPEED_API_KEY not set — run with skip_audio or set the env var"
            )
        audio_dir.mkdir(parents=True, exist_ok=True)
        speakers = self._resolve_speakers(mode)
        saved = tts_main(str(script_path), str(audio_dir), api_key, speakers)
        return Path(saved)

    def _resolve_speakers(self, mode: str) -> dict[str, Any]:
        if self._speakers is not None:
            return self._speakers
        cfg_speakers = load_config().get("speakers", {})
        return {
            "speaker_1": cfg_speakers.get("speaker_1", "en-Alice_woman"),
            "speaker_2": cfg_speakers.get("speaker_2", "en-Carter_man"),
            "speaker_3": cfg_speakers.get("speaker_3", "en-Maya_woman") if mode == "4person" else None,
            "speaker_4": cfg_speakers.get("speaker_4", "en-Frank_man") if mode == "4person" else None,
        }
```

**Done**:
```
PYTHONPATH=src python -c \
  "from engines.wavespeed_audio import WaveSpeedAudioEngine; print('ok')"
# exits 0
```

---

### Pass 3.5 — PDF Splitter Engine

| File | Change |
|------|--------|
| `src/engines/pdf_splitter.py` | add |

No `sys.path.insert` — `src/slicer/__init__.py` from Pass 1.0 makes `slicer.pdf_splitter`
importable with `PYTHONPATH=src`.

**`src/engines/pdf_splitter.py` full content:**

```python
from pathlib import Path

from engines.protocols import SplitterEngine


class PDFSplitterEngine(SplitterEngine):
    """Adapter for `slicer.pdf_splitter.run_splitter`.

    `run_splitter` result dict shape:
        {"success": bool, "files": [{"output_path": str, ...}], ...}
    """

    def split(
        self,
        book_pdf: Path,
        *,
        toc_page: int,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]:
        from slicer.pdf_splitter import run_splitter

        output_dir.mkdir(parents=True, exist_ok=True)
        result = run_splitter(
            input_path=str(book_pdf),
            toc_page=toc_page,
            output_dir=str(output_dir),
            prefix="chapter",
            chapters_only=True,
            no_ocr=no_ocr,
        )
        if not result.get("success"):
            raise RuntimeError(f"slicer failed: {result.get('error', 'unknown')}")
        return [Path(f["output_path"]) for f in result.get("files", [])]
```

**Done**:
```
PYTHONPATH=src python -c \
  "from engines.pdf_splitter import PDFSplitterEngine; print('ok')"
# exits 0
```

---

### Pass 3.6 — Engine Factory

| File | Change |
|------|--------|
| `src/engines/factory.py` | add |

**`src/engines/factory.py` full content:**

```python
from engines.llm_script import LLMScriptEngine
from engines.wavespeed_audio import WaveSpeedAudioEngine
from engines.pdf_splitter import PDFSplitterEngine
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine


def default_llm_script_engine(mode: str = "2person") -> ScriptEngine:
    return LLMScriptEngine(mode=mode)


def default_audio_engine(speakers: dict | None = None) -> AudioEngine:
    return WaveSpeedAudioEngine(speakers=speakers)


def default_splitter_engine() -> SplitterEngine:
    return PDFSplitterEngine()
```

**Done**:
```
PYTHONPATH=src python -c "
from engines.factory import (
    default_audio_engine,
    default_splitter_engine,
    default_llm_script_engine,
)
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
assert isinstance(default_audio_engine(), AudioEngine)
assert isinstance(default_splitter_engine(), SplitterEngine)
assert isinstance(default_llm_script_engine(mode='2person'), ScriptEngine)
print('ok')
"
# exits 0
```

---

## Phase 4 — Podcast Endpoints

**Goal**: `generate_chapter_podcast()` and `generate_book_podcast()` are directly callable
with no argparse, no print, no sys.exit.

---

### Pass 4.1 — `generate_chapter_podcast()`

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | add (or modify if partially built) |

**Required imports:**

```python
from pathlib import Path

from endpoints.podcast_types import PodcastResult
from engines.protocols import ScriptEngine, AudioEngine
from settings import PodcastSettings
```

**Signature:**

```python
def generate_chapter_podcast(
    pdf_path: Path,
    *,
    script_engine: ScriptEngine | None = None,
    audio_engine: AudioEngine | None = None,
    settings: PodcastSettings | None = None,
    skip_audio: bool = False,
    mode: str = "2person",
    context: str | None = None,
    fiction_dir: Path | None = None,
) -> PodcastResult:
```

**Body:**

```python
    settings = settings or PodcastSettings()

    try:
        pdf_path = Path(pdf_path).resolve()
        if not pdf_path.exists():
            return PodcastResult(error=FileNotFoundError(f"PDF not found: {pdf_path}"))

        if mode == "realworld" and not context:
            return PodcastResult(error=ValueError("mode 'realworld' requires context"))

        if script_engine is None:
            from engines.factory import default_llm_script_engine
            script_engine = default_llm_script_engine(mode=mode)

        script_text = script_engine.generate(
            pdf_path,
            context=context,
            fiction_dir=fiction_dir,
        )

        settings.scripts_out.mkdir(parents=True, exist_ok=True)
        script_out = settings.script_path_for(pdf_path)
        script_out.write_text(script_text, encoding="utf-8")

        if skip_audio:
            return PodcastResult(script_path=script_out)

        if audio_engine is None:
            from engines.factory import default_audio_engine
            audio_engine = default_audio_engine()

        audio_dir = settings.audio_dir_for(pdf_path)
        audio_path = audio_engine.generate(script_out, audio_dir, mode=mode)
        return PodcastResult(script_path=script_out, audio_path=audio_path)

    except Exception as e:
        return PodcastResult(error=e)
```

**Done**:
```
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
r = generate_chapter_podcast(Path('/nonexistent.pdf'))
assert not r.ok and r.error is not None
print('ok')
"
# exits 0
```

---

### Pass 4.2 — `generate_book_podcast()`

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — add `generate_book_podcast()` |

**Signature:**

```python
def generate_book_podcast(
    book_pdf: Path | None = None,
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
```

**Implementation rules:**

1. `settings = settings or PodcastSettings()`.
2. If `toc_page is None`: load from `config.json`; if still `None`, raise `ValueError`.
3. If `book_pdf` provided and `splitter_engine is None`, use `default_splitter_engine()`.
4. Split if `force` or no chapters exist in `settings.chapters_dir`.
5. If `slice_only`, return `[PodcastResult()]` after splitting.
6. Resolve `chapters_dir = chapters_dir or settings.chapters_dir`.
7. Sort PDFs numerically; for each, call `generate_chapter_podcast(...)` with the same
   engines and settings.
8. Continue on failure — do not stop the batch for one failed chapter.

**Done**:
```
PYTHONPATH=src python -c "
from endpoints.podcast import generate_book_podcast
from pathlib import Path
r = generate_book_podcast(chapters_dir=Path('/nonexistent'))
print(type(r), len(r))
"
# exits 0
```

---

### Pass 4.3 — Slicer Endpoint

| File | Change |
|------|--------|
| `src/endpoints/slicer.py` | add — thin re-export shim |

```python
from engines.pdf_splitter import PDFSplitterEngine  # noqa: F401
from slicer.pdf_splitter import run_splitter  # noqa: F401

__all__ = ["run_splitter", "PDFSplitterEngine"]
```

**Done**:
```
PYTHONPATH=src python -c "from endpoints.slicer import run_splitter; print('ok')"
# exits 0
```

---

## Phase 5 — Podcast CLI + TTS Boundary

**Goal**: `cli/podcast.py` assembles engines and settings, then calls endpoints. LLM is
always the script engine — there is no `--llm` flag.

---

### Pass 5.1 — TTS Engine Boundary

| File | Change |
|------|--------|
| `src/tts/cli.py` | modify — move `import argparse` from module level into `cli_entrypoint()` body |

Locate with: `grep -n "^import argparse" src/tts/cli.py`

**Done**:
```
grep "argparse" src/tts/cli.py
# hits only inside cli_entrypoint()
```

---

### Pass 5.2 — Podcast CLI Wrapper

| File | Change |
|------|--------|
| `src/cli/podcast.py` | add |

`src/cli/__init__.py` already exists from Pass 1.0.

**PYTHONPATH guard** — add at the top, before any local imports:

```python
import sys
from pathlib import Path
if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/podcast.py ..."
    )
```

**Logging** — configure at the start of `main()`:

```python
import logging

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
```

**Engine assembly** — LLM is always the script engine:

```python
from engines.factory import default_llm_script_engine, default_audio_engine, default_splitter_engine
from settings import PodcastSettings

settings = PodcastSettings()
script_engine = default_llm_script_engine(mode=args.mode)
audio_engine = None if args.skip_audio else default_audio_engine()
```

**Routing**: `--book PDF` routes to `generate_book_podcast()`. Absent → routes to
`generate_chapter_podcast()` using positional `pdf`.

**Full argument surface:**

Chapter flags:
- `pdf` (positional)
- `--skip-audio`
- `--mode` (choices: `CHAPTER_MODES`)
- `--context`
- `--context-file`
- `--fiction-dir`

Book flags:
- `--book`
- `--toc-page`
- `--no-ocr`
- `--force`
- `--slice-only`

**Mode sets:**

```python
CHAPTER_MODES = ["2person", "4person", "code", "realworld", "fiction_meta"]
BOOK_MODES    = ["2person", "4person", "code", "realworld"]
# fiction_meta requires per-chapter fiction files; not supported in batch
```

After parsing: if `args.book` and `args.mode == "fiction_meta"`, print error and
`sys.exit(1)`.

**`--context-file` handling:**
```python
if args.context_file:
    context = Path(args.context_file).read_text(encoding="utf-8").strip()
```

**`--fiction-dir` handling:**
```python
fiction_dir = Path(args.fiction_dir) if args.fiction_dir else None
```

**Interactive `toc_page` prompt:**
```python
if args.book and args.toc_page is None:
    try:
        toc_page = int(input("TOC page number: "))
    except (ValueError, EOFError):
        toc_page = None
else:
    toc_page = args.toc_page
```

Print result paths to stdout. Print errors to stderr. `sys.exit(1)` on failure.

**Done**:
```
PYTHONPATH=src python src/cli/podcast.py --help
# exits 0; shows `pdf` positional and `--book` flag; no `--llm` flag present

PYTHONPATH=src python src/cli/podcast.py <fixture_pdf> --skip-audio
# exits 0
```

---

### Pass 5.3 — Path Override Flags (Optional)

| File | Change |
|------|--------|
| `src/cli/podcast.py` | modify — add `--scripts-out`, `--audio-out`, `--chapters-dir` |

```python
parser.add_argument("--scripts-out", type=Path, default=None)
parser.add_argument("--audio-out", type=Path, default=None)
parser.add_argument("--chapters-dir", type=Path, default=None)
```

Construct `PodcastSettings` with those overrides if provided.

---

## Phase 6 — Novel Pipeline Callback Refactor

**Goal**: `session.py` has no `input()` in the chapter-approval path, no `sys.exit()`.
Approval injected via callable.

---

### Pass 6.1 — SessionResult + Callback Type

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — add `ApproveChapterFn` type alias and `SessionResult` dataclass |

```python
from typing import Callable
from dataclasses import dataclass

ApproveChapterFn = Callable[[int, str], bool]
# (chapter_number, full_chapter_text) → True = approve, False = reject

@dataclass
class SessionResult:
    chapters_written: int
    final_chapter_number: int
    cost_usd: float
    completed: bool
    state_path: Path
```

`cost_usd` from `current_totals(config)["session_total"]`.
`state_path` from `Path(config["state_file_path"])`.

**Done**:
```
PYTHONPATH=src python -c \
  "from fiction.pipeline.novel_pipeline.session import SessionResult, ApproveChapterFn; print('ok')"
# exits 0
```

---

### Pass 6.2 — session.py Callback Injection

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — inject callback; replace `sys.exit(1)` with `raise`; return `SessionResult` |

**Changes in detail:**

1. Add `approve_chapter: ApproveChapterFn = lambda n, text: True` to `run_session()`.

2. Add `approve_chapter: ApproveChapterFn` to `_run_one_chapter()`. Thread it from
   `run_session()` to `_run_one_chapter()` at the call site.

3. Inside `_run_one_chapter()`, replace the entire approval block (both the `auto_approve`
   fast-path and the `input("Approve and update living doc? [y/n/q]: ")` branch) with:

   ```python
   approved = approve_chapter(chapter_num, chapter_text)
   if not approved:
       log_event("chapter_rejected", {"chapter": chapter_num, "attempt": attempt})
       print(f"Rejected. Draft remains at {draft_path}. Attempt {attempt}/{max_rejections}.")
       chapter_text = None
       continue
   break
   ```

4. Convert the draft-preview print block to `logger.info(...)`. Locate with:
   `grep -n "Draft saved\|draft_path" src/fiction/pipeline/novel_pipeline/session.py`

5. Replace `sys.exit(1)` in `except KeyboardInterrupt:` with `raise KeyboardInterrupt`.
   Locate with:
   `grep -n "KeyboardInterrupt" src/fiction/pipeline/novel_pipeline/session.py`

6. Return `SessionResult` at the 2 early-exit points and the post-loop fall-through.
   Locate early exits with:
   `grep -n "should_continue\|Proceed" src/fiction/pipeline/novel_pipeline/session.py`

   - Early exit when `should_continue` is False:
     `return SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False, state_path=Path(config["state_file_path"]))`
   - Early exit when "Proceed?" is declined: same pattern.
   - Normal completion (post-loop fall-through):
     `return SessionResult(chapters_written=completed, final_chapter_number=current_chapter, cost_usd=current_totals(config)["session_total"], completed=True, state_path=Path(config["state_file_path"]))`

**`input()` scope note**: `session.py` also contains `_prompt_yes_no()` and
`_prompt_choice()`, both of which call `input()`. These are gated by `auto=True` paths
and are intentionally preserved for interactive use.

**Done**:
```
grep "input()" src/fiction/pipeline/novel_pipeline/session.py | \
  grep -v "_prompt_yes_no\|_prompt_choice"
# returns empty

grep "sys.exit" src/fiction/pipeline/novel_pipeline/session.py
# returns empty
```

---

### Pass 6.3 — Novel Pipeline CLI Update

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/cli.py` | modify — construct `approve_fn`; pass to `run_session()` |

> The `--auto-approve` flag already exists. Do NOT add it again.

```python
from util.prompt import prompt_user

approve_fn = (lambda n, t: True) if args.auto_approve else prompt_user
```

Pass `approve_chapter=approve_fn` to `run_session()`.

**Done**:
```
PYTHONPATH=src python src/fiction/pipeline/novel_pipeline/cli.py \
  --auto-approve <config>
# runs without stdin prompts
```

---

### Pass 6.4 — Fiction Endpoint Wrapper

| File | Change |
|------|--------|
| `src/endpoints/fiction.py` | add |

**Pre-condition** — `novel_pipeline` must be importable:
```
PYTHONPATH=src python -c "import novel_pipeline; print('ok')"
# Must exit 0. If this fails:
#   cd src/fiction/pipeline && pip install -e . && cd -
```

```python
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult


def run_novel_session(
    config_path: str | Path,
    resume: bool = False,
    auto_approve: bool = False,
    dry_run: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: ApproveChapterFn | None = None,
) -> SessionResult:
    config = load_config(str(config_path))
    if approve_chapter is None:
        approve_chapter = lambda n, t: True
    return run_session(
        config,
        resume=resume,
        auto_approve=auto_approve,
        dry_run=dry_run,
        chapter_start=chapter_start,
        ignore_cost_limit=ignore_cost_limit,
        approve_chapter=approve_chapter,
    )
```

**Done**:
```
PYTHONPATH=src python -c \
  "from endpoints.fiction import run_novel_session; print('ok')"
# exits 0
```

---

### Pass 6.5 — Fiction CLI

| File | Change |
|------|--------|
| `src/cli/fiction.py` | add |

**PYTHONPATH guard** (same as Pass 5.2):
```python
import sys
from pathlib import Path
if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/fiction.py ..."
    )
```

Mirror exact flags from `novel_pipeline/cli.py`:
`--config` (required), `--auto-approve`, `--dry-run`, `--resume`,
`--chapter-start`, `--ignore-cost-limit`.

```python
from util.prompt import prompt_user

approve_fn = (lambda n, t: True) if args.auto_approve else prompt_user
```

Call `run_novel_session()` from `endpoints.fiction`.

**Done**:
```
PYTHONPATH=src python src/cli/fiction.py --help
# same flags as novel_pipeline/cli.py

PYTHONPATH=src python src/cli/fiction.py --auto-approve <config>
# no stdin prompts
```

---

## Phase 7 — Cleanup

**Goal**: Dead code removed. Root-level entry points shimmed. README updated.

v9's Pass 7.4 ("Remove sys.path.insert from Engine Adapters") is dropped — v10 adapters
never had `sys.path.insert`. The shim pass and legacy-helper removal are merged into
Pass 7.3 to eliminate an ordering hazard (the helpers must be gone before shimming would
leave run_book.py in a broken state).

---

### Pass 7.1 — Remove Private Config Loaders

**Pre-condition**: Pass 1.1 complete. Verify 4 hits:
```
grep -rn "from config import load_config" src/run_chapter.py src/run_book.py \
  src/tts/cli.py src/podcast_script_generator/llm/call_api.py
```

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — delete `_load_config()` definition |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — same |
| `src/podcast_script_generator/llm/call_api.py` | modify — same |

**Done**:
```
grep -rn "_load_config" src/
# returns empty
```

---

### Pass 7.2 — Delete run_simple.py

| File | Change |
|------|--------|
| `src/fiction/run_simple.py` | delete |

```
grep -rn "run_simple" src/
# must return empty before deletion
```

**Done**:
```
ls src/fiction/run_simple.py
# "No such file"
```

---

### Pass 7.3 — Shim Entry Points + Remove Legacy Helpers

**Pre-conditions** — verify ALL before proceeding:

1. Passes 4.1, 4.2, and 5.2 are complete.
2. `src/cli/podcast.py` has `--book`:
   `PYTHONPATH=src python src/cli/podcast.py --help | grep -- "--book"` returns a hit.
3. Nothing outside `run_book.py` imports from `run_chapter`:
   `grep -rn "from run_chapter import\|import run_chapter" src/ | grep -v run_book` returns empty.

> **Critical**: Apply BOTH shims in the same commit. The shim replaces the entire
> file body — this is what removes `run_local()`, `run_llm()`, `run_tts()` from
> `run_chapter.py` and the `rc.*` calls from `run_book.py`.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — replace entire body |
| `src/run_book.py` | modify — replace entire body |

**Shim body for both files:**

```python
from cli.podcast import main

if __name__ == "__main__":
    main()
```

The `if __name__ == "__main__"` guard ensures `main()` does not execute on import.

**Done**:
```
PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# identical output to:
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf>

PYTHONPATH=src python src/run_book.py --help
# exits 0; exposes --book flag

grep "def run_local\|def run_llm\|def run_tts" src/run_chapter.py
# returns empty (body replaced by shim)
```

---

### Pass 7.4 — Update initial_readme.md

| File | Change |
|------|--------|
| `src/initial_readme.md` | modify — update Entry Points section |

- List `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs.
- Document `run_chapter.py` and `run_book.py` as backward-compat shims.
- Document `PYTHONPATH=src` invocation convention.
- Note that LLM (OpenRouter) is the only script generation path; no local/offline mode.

**Done**:
```
grep "src/cli/podcast.py" src/initial_readme.md  # returns a hit
grep "PYTHONPATH" src/initial_readme.md           # returns a hit
```

---

## Phase 8 — Behavioral Verification

---

### Pass 8.0 — Import Surface Verification

Run before any behavioral pass. Failure here means a package is missing or `PYTHONPATH`
is wrong — not a logic error.

```bash
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast, generate_book_podcast
from endpoints.podcast_types import PodcastResult, ScriptMode
from endpoints.slicer import run_splitter
from endpoints.fiction import run_novel_session
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from engines.llm_script import LLMScriptEngine
from engines.wavespeed_audio import WaveSpeedAudioEngine
from engines.pdf_splitter import PDFSplitterEngine
from engines.factory import (
    default_llm_script_engine,
    default_audio_engine,
    default_splitter_engine,
)
from settings import PodcastSettings
from util.normalize import normalize_speakers
from util.prompt import prompt_user
print('all imports ok')
"
# Must exit 0 before running passes 8.1–8.6.
```

---

### Pass 8.1 — Podcast Endpoint Smoke Tests

```bash
PYTHONPATH=src python -c "
from endpoints.podcast_types import PodcastResult
from pathlib import Path
r1 = PodcastResult(error=ValueError('x'))
r2 = PodcastResult(script_path=Path('/tmp/x'))
r3 = PodcastResult()
assert not r1.ok
assert r2.ok
assert r3.ok
print('PodcastResult invariants ok')
"

PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
r = generate_chapter_podcast(Path('/nonexistent/file.pdf'))
assert not r.ok and r.error is not None
print('missing PDF handled gracefully ok')
"

PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
r = generate_chapter_podcast(Path('/nonexistent/file.pdf'), mode='fiction_meta')
assert not r.ok
assert 'fiction_dir' in str(r.error)
print('fiction_meta validation ok')
"
```

---

### Pass 8.2 — Fiction Endpoint Smoke Tests

```bash
PYTHONPATH=src python -c "
from util.prompt import prompt_user
import inspect
sig = inspect.signature(prompt_user)
params = list(sig.parameters)
assert params == ['chapter_num', 'draft_text'], f'unexpected: {params}'
print('prompt_user signature ok')
"
```

---

### Pass 8.3 — Shim Equivalence Check

```bash
PYTHONPATH=src python src/run_chapter.py --help | grep -q "\-\-help" \
  && echo "run_chapter shim ok"
PYTHONPATH=src python src/run_book.py --help | grep -q "\-\-book" \
  && echo "run_book shim ok"

python -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('rc', 'src/run_chapter.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
leaked = [x for x in dir(mod) if not x.startswith('_') and x not in ('main',)]
assert leaked == [], f'unexpected symbols in shim: {leaked}'
print('no symbol leakage ok')
"
```

---

### Pass 8.4 — Fake Engine Test

```bash
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
import tempfile

class FakeScriptEngine:
    def generate(self, pdf_path, *, context=None, fiction_dir=None):
        return 'Speaker 0: hello\nSpeaker 1: world'

class FakeAudioEngine:
    def generate(self, script_path, audio_dir, *, mode='2person'):
        audio_dir.mkdir(parents=True, exist_ok=True)
        p = audio_dir / 'fake.mp3'
        p.write_text('fake audio')
        return p

with tempfile.TemporaryDirectory() as td:
    pdf = Path(td) / '01_chapter.pdf'
    pdf.write_bytes(b'%PDF-fake')
    settings = __import__('settings').PodcastSettings(root=Path(td))
    r = generate_chapter_podcast(
        pdf,
        script_engine=FakeScriptEngine(),
        audio_engine=FakeAudioEngine(),
        settings=settings,
    )
    assert r.ok, r.error
    assert r.script_path.exists()
    assert r.audio_path.exists()
    print('fake engine test ok')
"
# exits 0
```

---

### Pass 8.5 — CLI Smoke Test

```bash
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf> --skip-audio
# exits 0

PYTHONPATH=src python src/cli/podcast.py --help | grep "\-\-llm" | wc -l
# must print 0 — --llm flag must not appear
```

---

### Pass 8.6 — Book Endpoint Uses Injected Splitter

```bash
PYTHONPATH=src python -c "
from endpoints.podcast import generate_book_podcast
from pathlib import Path
import tempfile

class FakeSplitter:
    def split(self, book_pdf, *, toc_page, output_dir, no_ocr=False):
        p = output_dir / '01_chapter.pdf'
        p.write_bytes(b'%PDF-fake')
        return [p]

class FakeScriptEngine:
    def generate(self, pdf_path, *, context=None, fiction_dir=None):
        return 'Speaker 0: hello'

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    book = root / 'book.pdf'
    book.write_bytes(b'%PDF-fake')
    settings = __import__('settings').PodcastSettings(root=root)
    results = generate_book_podcast(
        book_pdf=book,
        toc_page=1,
        splitter_engine=FakeSplitter(),
        script_engine=FakeScriptEngine(),
        audio_engine=None,
        settings=settings,
        skip_audio=True,
    )
    assert len(results) == 1
    assert results[0].ok
    print('injected splitter test ok')
"
# exits 0
```

---

## Appendix — Cross-Phase Dependencies

| Dependency | Consumer | Provider |
|------------|----------|----------|
| `PYTHONPATH=src` invocation model | All passes | Pass 0.0 |
| `__init__.py` for all 8 packages | All subsequent passes | Pass 1.0 |
| `src/config.py` exists | Passes 1.2–7.1 | Pass 1.1 |
| `_load_config()` renamed (9 call sites across 4 files) | Pass 7.1 done condition | Pass 1.1 |
| `PodcastError` hierarchy exists | Passes 4.1, 5.2 | Pass 1.2 |
| `src/util/normalize.py` exists | Pass 3.3 | Pass 2.1 |
| `src/util/prompt.py` exists | Passes 6.3, 6.5 | Pass 2.3 |
| `PodcastResult`, `ScriptMode` defined (`ok` as property) | Pass 4.1 | Pass 2.2 |
| `engines.protocols` exists | All adapters + endpoints | Pass 3.1 |
| `PodcastSettings` exists | Endpoints, CLI, tests | Pass 3.2 |
| `LLMScriptEngine` exists | Endpoints, factory, CLI | Pass 3.3 |
| `WaveSpeedAudioEngine` exists | Endpoints, factory, CLI | Pass 3.4 |
| `PDFSplitterEngine` exists | Endpoints, factory | Pass 3.5 |
| `engines.factory` assembles defaults | CLI | Pass 3.6 |
| `generate_chapter_podcast()` accepts injected engines | Passes 5.2, 8.4 | Pass 4.1 |
| `generate_book_podcast()` accepts injected splitter | Passes 5.2, 8.6 | Pass 4.2 |
| `src/endpoints/slicer.py` exists | Import surface | Pass 4.3 |
| `logging.basicConfig` in `cli/podcast.py main()` | Pass 7.3 (shim removes it from run_chapter) | Pass 5.2 |
| `src/cli/podcast.py` has full book flags incl. `--slice-only` | Pass 7.3 pre-condition | Pass 5.2 |
| `SessionResult` + `ApproveChapterFn` defined | Pass 6.2 | Pass 6.1 |
| `approve_chapter` wired in `run_session()` + `_run_one_chapter()` | Passes 6.3, 6.4 | Pass 6.2 |
| `novel_pipeline` importable (egg installed) | Pass 6.4 | Pre-condition: `pip install -e .` |
| `run_novel_session()` exists | Pass 6.5 | Pass 6.4 |
| All four files use shared `load_config` | Pass 7.1 | Pass 1.1 |
| `src/endpoints/podcast.py` has full book logic | Pass 7.3 pre-condition | Pass 4.2 |
| Pass 8.0 import surface verified | Passes 8.1–8.6 | Pass 8.0 |

---

## What v10 Does and Does Not Decouple

**Now decoupled:**
- Script generator (single LLM path) ↔ endpoint
- TTS engine ↔ endpoint
- PDF splitter ↔ endpoint
- Output paths ↔ endpoint (via `PodcastSettings`)
- Speaker config ↔ `WaveSpeedAudioEngine` (injectable)
- Shared types (`PodcastResult`, `ScriptMode`) ↔ endpoint implementation
- Approval logic ↔ fiction pipeline (via `ApproveChapterFn` callback)

**Still coupled:**
- The CLI knows which engine classes exist (through the factory). Acceptable; the next
  step would be a plugin registry or config-driven selection.
- `generate_chapter_podcast()` encodes the "script → optional audio" pipeline shape.

v10 is **simpler than v9**: one fewer engine adapter, no `package_path` plumbing in any
adapter, no runtime `sys.path` manipulation, the `--llm` flag eliminated from the CLI
surface, and the shim/cleanup ordering hazard resolved by merging Passes 7.3 and 7.4.
