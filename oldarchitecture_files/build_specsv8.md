# Build Specs v8 — Engine Protocols + Dependency Injection Refactor

> Derived from `build_specsv7.md`.
> v8 addresses the feedback on v7:
> - `PodcastResult` / `ScriptMode` are extracted into `src/endpoints/podcast_types.py`
>   so the endpoint import is consistent.
> - Factory functions return protocol types (`ScriptEngine`, `AudioEngine`,
>   `SplitterEngine`) instead of `object`.
> - `PodcastSettings` is simplified (no `frozen=True`, no `object.__setattr__`).
> - `PDFSplitterEngine` uses the actual `run_splitter` return shape
>   (`files[*]["output_path"]`).
> - `WaveSpeedAudioEngine` accepts an optional `speakers` mapping so it is not
>   forced to read global config.
>
> Each pass names every file touched, the change type (add / modify / delete), and a
> done condition. Passes within a phase are ordered; complete each pass before the next.

---

## Gap Index (v7 → v8)

| Gap | Severity | Fixed In |
|-----|----------|----------|
| `endpoints/podcast_types.py` referenced but never created | High | Pass 0.3 |
| Factory functions return `object` | Medium | Pass 2.3 |
| `PodcastSettings.__post_init__` uses fragile `object.__setattr__` | Low | Pass 0.1 |
| `PDFSplitterEngine` assumes wrong file dict key (`"path"` vs `"output_path"`) | High | Pass 1.4 |
| `WaveSpeedAudioEngine` is forced to call `load_config()` for speakers | Low | Pass 1.3 |

---

## Design Summary

v8 keeps the three engine protocols from v7:

```python
# src/engines/protocols.py
from typing import Protocol
from pathlib import Path


class ScriptEngine(Protocol):
    def generate(
        self,
        pdf_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str:
        ...


class AudioEngine(Protocol):
    def generate(
        self,
        script_path: Path,
        audio_dir: Path,
        *,
        mode: str = "2person",
    ) -> Path:
        ...


class SplitterEngine(Protocol):
    def split(
        self,
        book_pdf: Path,
        *,
        toc_page: int,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]:
        ...
```

Endpoints receive engines and settings:

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

Default engines are assembled by a type-safe factory:

```python
from engines.factory import (
    default_local_script_engine,
    default_llm_script_engine,
    default_audio_engine,
    default_splitter_engine,
)

script_engine = default_llm_script_engine(mode="2person")
audio_engine = default_audio_engine()
splitter_engine = default_splitter_engine()
```

---

## Phase 0 — Foundation Objects

**Goal**: Create the protocols, settings object, shared types, and package structure
that all engine adapters will use. No behavioral change yet.

---

### Pass 0.0 — Engine Protocols

| File | Change |
|------|--------|
| `src/engines/__init__.py` | add — empty |
| `src/engines/protocols.py` | add — `ScriptEngine`, `AudioEngine`, `SplitterEngine` protocols |

**`src/engines/protocols.py` full content:**

```python
from typing import Protocol
from pathlib import Path


class ScriptEngine(Protocol):
    """Abstraction over local and LLM script generators."""

    def generate(
        self,
        pdf_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str:
        """Return a normalized speaker script as a string."""
        ...


class AudioEngine(Protocol):
    """Abstraction over TTS implementations."""

    def generate(
        self,
        script_path: Path,
        audio_dir: Path,
        *,
        mode: str = "2person",
    ) -> Path:
        """Generate audio from `script_path` and return the saved audio path."""
        ...


class SplitterEngine(Protocol):
    """Abstraction over the PDF book splitter."""

    def split(
        self,
        book_pdf: Path,
        *,
        toc_page: int,
        output_dir: Path,
        no_ocr: bool = False,
    ) -> list[Path]:
        """Split `book_pdf` into chapter PDFs and return their paths."""
        ...
```

**Done**:

```bash
PYTHONPATH=src python -c \
  "from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine; print('ok')"
# exits 0
```

---

### Pass 0.1 — PodcastSettings

| File | Change |
|------|--------|
| `src/settings.py` | add — `PodcastSettings` dataclass |

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

> No `frozen=True`. `PodcastSettings` is constructed once per CLI invocation, so
> mutability is not a practical risk, and `__post_init__` stays readable.

**Done**:

```bash
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

### Pass 0.2 — Package `__init__.py` Cleanup

**Goal**: Make every engine directory importable as a package so `sys.path.insert` can be
deleted in Phase 4.

| File | Change |
|------|--------|
| `src/podcast_script_generator/__init__.py` | add — empty |
| `src/podcast_script_generator/llm/__init__.py` | add — empty |
| `src/decide_later/__init__.py` | add — empty (if missing) |
| `src/decide_later/local/__init__.py` | add — empty (if missing) |

**Done**:

```bash
PYTHONPATH=src python -c \
  "import podcast_script_generator; import podcast_script_generator.llm; print('ok')"
# exits 0

PYTHONPATH=src python -c \
  "import decide_later.local; print('ok')"
# exits 0 (if the local generator package exists)
```

---

### Pass 0.3 — Shared Podcast Types

| File | Change |
|------|--------|
| `src/endpoints/__init__.py` | add — empty (if missing after v6) |
| `src/endpoints/podcast_types.py` | add — `ScriptMode` enum and `PodcastResult` dataclass |
| `src/endpoints/podcast.py` | modify — import from `podcast_types` instead of defining locally |

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

**`src/endpoints/podcast.py` change:**

Replace the local `ScriptMode` / `PodcastResult` definitions with:

```python
from endpoints.podcast_types import PodcastResult, ScriptMode
```

**Done**:

```bash
PYTHONPATH=src python -c "
from endpoints.podcast_types import ScriptMode, PodcastResult
from pathlib import Path
r1 = PodcastResult(error=ValueError('x'))
r2 = PodcastResult(script_path=Path('/tmp/x'))
assert not r1.ok
assert r2.ok
print('ok')
"
# exits 0

PYTHONPATH=src python -c \
  "from endpoints.podcast import PodcastResult, ScriptMode; print('re-export ok')"
# exits 0 (optional re-export for convenience)
```

---

## Phase 1 — Engine Adapters

**Goal**: Wrap every concrete engine behind the protocols. Each adapter owns its own imports
and stops reaching into sibling directories via `sys.path.insert`.

---

### Pass 1.1 — Local Script Engine

| File | Change |
|------|--------|
| `src/engines/local_script.py` | add — `LocalScriptEngine` adapter |

**`src/engines/local_script.py` full content:**

```python
import sys
from pathlib import Path

from engines.protocols import ScriptEngine


class LocalScriptEngine(ScriptEngine):
    """Adapter for the offline `decide_later.local.podcast_generator` engine."""

    def __init__(self, package_path: Path | None = None) -> None:
        # `decide_later.local` is only importable when its parent is on sys.path.
        # This adapter owns that one-time path setup; endpoints stay clean.
        if package_path is not None:
            path = str(package_path)
            if path not in sys.path:
                sys.path.insert(0, path)

    def generate(
        self,
        pdf_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str:
        from decide_later.local.podcast_generator import (
            extract_text,
            clean_text,
            generate_podcast_script,
        )
        from util.normalize import normalize_speakers

        raw = extract_text(str(pdf_path))
        if not raw:
            raise ValueError(f"No extractable text in {pdf_path.name}")
        return normalize_speakers(generate_podcast_script(str(pdf_path), clean_text(raw)))
```

**Done**:

```bash
PYTHONPATH=src python -c \
  "from engines.local_script import LocalScriptEngine; print('ok')"
# exits 0
```

---

### Pass 1.2 — LLM Script Engine

| File | Change |
|------|--------|
| `src/engines/llm_script.py` | add — `LLMScriptEngine` adapter |

**`src/engines/llm_script.py` full content:**

```python
import re
import sys
from pathlib import Path

from engines.protocols import ScriptEngine


class LLMScriptEngine(ScriptEngine):
    """Adapter for the OpenRouter LLM script generator."""

    def __init__(self, mode: str = "2person", package_path: Path | None = None) -> None:
        self.mode = mode
        if package_path is not None:
            path = str(package_path)
            if path not in sys.path:
                sys.path.insert(0, path)

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
            raise ValueError(f"cannot extract chapter number from PDF stem: {pdf_path.stem}")
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

```bash
PYTHONPATH=src python -c \
  "from engines.llm_script import LLMScriptEngine; print('ok')"
# exits 0
```

---

### Pass 1.3 — WaveSpeed Audio Engine

| File | Change |
|------|--------|
| `src/engines/wavespeed_audio.py` | add — `WaveSpeedAudioEngine` adapter |

**`src/engines/wavespeed_audio.py` full content:**

```python
import os
import sys
from pathlib import Path
from typing import Any

from config import load_config
from engines.protocols import AudioEngine


class WaveSpeedAudioEngine(AudioEngine):
    """Adapter for the WaveSpeed VibeVoice TTS engine."""

    def __init__(
        self,
        package_path: Path | None = None,
        speakers: dict[str, Any] | None = None,
    ) -> None:
        """
        Args:
            package_path: Path to add to sys.path so `tts.cli` is importable.
            speakers: Optional speaker mapping. If None, speakers are read from
                      `config.json` (or defaults). Pass a mapping to make the engine
                      fully self-describing and avoid global config.
        """
        if package_path is not None:
            path = str(package_path)
            if path not in sys.path:
                sys.path.insert(0, path)
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
            raise RuntimeError("WAVESPEED_API_KEY not set — run with skip_audio or set the env var")

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

```bash
PYTHONPATH=src python -c \
  "from engines.wavespeed_audio import WaveSpeedAudioEngine; print('ok')"
# exits 0
```

---

### Pass 1.4 — PDF Splitter Engine

| File | Change |
|------|--------|
| `src/engines/pdf_splitter.py` | add — `PDFSplitterEngine` adapter |
| `src/endpoints/slicer.py` | modify — re-export `PDFSplitterEngine` as a thin shim (optional) |

**`src/engines/pdf_splitter.py` full content:**

```python
from pathlib import Path

from engines.protocols import SplitterEngine


class PDFSplitterEngine(SplitterEngine):
    """Adapter for `slicer.pdf_splitter.run_splitter`.

    `run_splitter` returns a dict:
        {
            "success": bool,
            "source": str | None,
            "toc": list,
            "files": [
                {
                    "filename": str,
                    "title": str,
                    "start_page": int,
                    "end_page": int,
                    "page_count": int,
                    "output_path": str,   # <-- actual key
                    "created": bool,
                    "ocr_embedded": bool,
                },
                ...
            ],
            "output_dir": str,
            "dry_run": bool,
            ...
        }
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

```bash
PYTHONPATH=src python -c \
  "from engines.pdf_splitter import PDFSplitterEngine; print('ok')"
# exits 0
```

---

## Phase 2 — Refactor Endpoints to Use Injected Engines

**Goal**: `endpoints/podcast.py` no longer hard-codes engine choices or output paths.
It receives `ScriptEngine`, `AudioEngine`, and `PodcastSettings` as parameters.

---

### Pass 2.1 — Refactor `generate_chapter_podcast()`

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — rewrite `generate_chapter_podcast()` to accept injected engines and settings |

**Required imports after refactor:**

```python
from pathlib import Path

from config import load_config
from endpoints.podcast_types import PodcastResult, ScriptMode
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from settings import PodcastSettings
```

**New signature:**

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

**Implementation body:**

```python
settings = settings or PodcastSettings()

try:
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        return PodcastResult(error=FileNotFoundError(f"PDF not found: {pdf_path}"))

    if mode == "realworld" and not context:
        return PodcastResult(
            error=ValueError("mode 'realworld' requires context")
        )

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

**What is removed:**
- `run_local()`, `run_llm()`, `run_tts()` definitions (deleted in Pass 4.1)
- Module-level `_SCRIPTS_OUT` / `_AUDIO_OUT` constants
- `import re` at module level (moved into `LLMScriptEngine`)
- Fiction-content discovery (moved into `LLMScriptEngine`)

**Done**:

```bash
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

### Pass 2.2 — Refactor `generate_book_podcast()`

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — rewrite `generate_book_podcast()` to accept injected splitter, engines, and settings |

**New signature:**

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
3. If `book_pdf` is provided and `splitter_engine` is `None`, use the factory default.
4. Split if `force` or no chapters exist. Use `settings.chapters_dir` as output.
5. If `slice_only`, return `[PodcastResult()]` after splitting.
6. Resolve `chapters_dir = chapters_dir or settings.chapters_dir`.
7. Sort PDFs; for each, call `generate_chapter_podcast(...)` with the same engines and
   settings.
8. Continue on failure — do not stop the batch because one chapter failed.

**Done**:

```bash
PYTHONPATH=src python -c "
from endpoints.podcast import generate_book_podcast
from pathlib import Path
r = generate_book_podcast(chapters_dir=Path('/nonexistent'))
print(type(r), len(r))
"
# exits 0
```

---

### Pass 2.3 — Engine Factory

| File | Change |
|------|--------|
| `src/engines/factory.py` | add — type-safe default engine constructors |

**`src/engines/factory.py` full content:**

```python
from pathlib import Path

from engines.local_script import LocalScriptEngine
from engines.llm_script import LLMScriptEngine
from engines.wavespeed_audio import WaveSpeedAudioEngine
from engines.pdf_splitter import PDFSplitterEngine
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine

_SRC = Path(__file__).parent.parent  # src/


def default_local_script_engine(package_path: Path | None = None) -> ScriptEngine:
    if package_path is None:
        package_path = _SRC / "decide_later"
    return LocalScriptEngine(package_path=package_path)


def default_llm_script_engine(
    mode: str = "2person", package_path: Path | None = None
) -> ScriptEngine:
    if package_path is None:
        package_path = _SRC / "podcast_script_generator" / "llm"
    return LLMScriptEngine(mode=mode, package_path=package_path)


def default_audio_engine(
    package_path: Path | None = None,
    speakers: dict | None = None,
) -> AudioEngine:
    if package_path is None:
        package_path = _SRC / "tts"
    return WaveSpeedAudioEngine(package_path=package_path, speakers=speakers)


def default_splitter_engine() -> SplitterEngine:
    return PDFSplitterEngine()
```

**Done**:

```bash
PYTHONPATH=src python -c "
from engines.factory import (
    default_audio_engine,
    default_splitter_engine,
    default_local_script_engine,
    default_llm_script_engine,
)
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from pathlib import Path
assert isinstance(default_audio_engine(), AudioEngine)
assert isinstance(default_splitter_engine(), SplitterEngine)
assert isinstance(default_local_script_engine(), ScriptEngine)
assert isinstance(default_llm_script_engine(mode='2person'), ScriptEngine)
print('ok')
"
# exits 0
```

---

### Pass 2.4 — Update `endpoints/podcast.py` Imports

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — trim imports to only what the endpoint needs |

No `import re`, no `import sys`, no `sys.path.insert`, no module-level path constants.

**Done**:

```bash
grep "sys.path.insert" src/endpoints/podcast.py
# returns empty

grep "^SRC\|^ROOT\|_SCRIPTS_OUT\|_AUDIO_OUT" src/endpoints/podcast.py
# returns empty
```

---

## Phase 3 — Update the CLI

**Goal**: `cli/podcast.py` assembles engines and settings, then calls endpoints. It does not
contain business logic.

---

### Pass 3.1 — Rewrite `cli/podcast.py` Engine Assembly

| File | Change |
|------|--------|
| `src/cli/podcast.py` | modify — use factory + settings; pass engines to endpoints |

**Key assembly logic inside `main()`:**

```python
from engines.factory import (
    default_local_script_engine,
    default_llm_script_engine,
    default_audio_engine,
    default_splitter_engine,
)
from settings import PodcastSettings

settings = PodcastSettings()

# Override paths from CLI flags if provided (add flags in Pass 3.2).
script_engine = (
    default_llm_script_engine(mode=args.mode)
    if args.llm
    else default_local_script_engine()
)
audio_engine = None if args.skip_audio else default_audio_engine()

if args.book:
    splitter_engine = default_splitter_engine()
    results = generate_book_podcast(
        book_pdf=Path(args.book),
        toc_page=toc_page,
        script_engine=script_engine,
        audio_engine=audio_engine,
        splitter_engine=splitter_engine,
        settings=settings,
        no_ocr=args.no_ocr,
        force=args.force,
        skip_audio=args.skip_audio,
        mode=args.mode,
        context=context,
        slice_only=args.slice_only,
    )
    ...
else:
    result = generate_chapter_podcast(
        pdf_path=pdf_path,
        script_engine=script_engine,
        audio_engine=audio_engine,
        settings=settings,
        skip_audio=args.skip_audio,
        mode=args.mode,
        context=context,
        fiction_dir=fiction_dir,
    )
    ...
```

**Done**:

```bash
PYTHONPATH=src python src/cli/podcast.py --help
# exits 0

PYTHONPATH=src python src/cli/podcast.py <fixture_pdf>
# produces output identical to v6/v7
```

---

### Pass 3.2 — Add Path Override Flags (Optional)

| File | Change |
|------|--------|
| `src/cli/podcast.py` | modify — add `--scripts-out`, `--audio-out`, `--chapters-dir` flags |

Only add these if the project needs non-default paths. If not, skip this pass.

```python
parser.add_argument("--scripts-out", type=Path, default=None)
parser.add_argument("--audio-out", type=Path, default=None)
parser.add_argument("--chapters-dir", type=Path, default=None)
```

Construct:

```python
settings = PodcastSettings(
    scripts_out=args.scripts_out,
    audio_out=args.audio_out,
    chapters_dir=args.chapters_dir,
)
```

**Done**:

```bash
PYTHONPATH=src python src/cli/podcast.py --help | grep -E "scripts-out|audio-out|chapters-dir"
# shows the flags
```

---

## Phase 4 — Remove Legacy Coupling

**Goal**: Delete the old helper functions and remaining `sys.path.insert` calls.

---

### Pass 4.1 — Delete Legacy Helpers from `endpoints/podcast.py`

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — delete `run_local()`, `run_llm()`, `run_tts()` |

Verify nothing imports them from this module:

```bash
grep -rn "from endpoints.podcast import.*run_" src/
# must return empty except temporary imports that were already removed in v6
```

**Done**:

```bash
grep "def run_local\|def run_llm\|def run_tts" src/endpoints/podcast.py
# returns empty
```

---

### Pass 4.2 — Remove `sys.path.insert` from Engine Adapters

| File | Change |
|------|--------|
| `src/engines/local_script.py` | modify — remove constructor path hack if packages are importable without it |
| `src/engines/llm_script.py` | modify — same |
| `src/engines/wavespeed_audio.py` | modify — same |

**When to remove**: once Pass 0.2's `__init__.py` additions and `PYTHONPATH=src` make the
packages resolvable without extra path manipulation.

If `decide_later.local` still cannot be imported without the path insert, keep the
constructor parameter but document it as a transitional workaround.

**Done**:

```bash
grep -rn "sys.path.insert" src/engines/
# returns empty (or only documented transitional lines)
```

---

### Pass 4.3 — Update Shims and Tests

| File | Change |
|------|--------|
| `src/run_chapter.py` | no change — remains `from cli.podcast import main; main()` |
| `src/run_book.py` | no change — remains shim |
| `src/podcast_script_generator/llm/main.py` | modify — use `PodcastError` raises (already in v6) |
| `src/tts/cli.py` | modify — keep `main()` callable; no module-level argparse |

**Done**:

```bash
PYTHONPATH=src python src/run_chapter.py --help
PYTHONPATH=src python src/run_book.py --help
# both exit 0
```

---

## Phase 5 — Decoupled Smoke Tests

**Goal**: Prove that engines can be replaced without changing endpoint code.

---

### Pass 5.0 — Import Surface Verification

```bash
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast, generate_book_podcast
from endpoints.podcast_types import PodcastResult, ScriptMode
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from engines.local_script import LocalScriptEngine
from engines.llm_script import LLMScriptEngine
from engines.wavespeed_audio import WaveSpeedAudioEngine
from engines.pdf_splitter import PDFSplitterEngine
from engines.factory import (
    default_local_script_engine,
    default_llm_script_engine,
    default_audio_engine,
    default_splitter_engine,
)
from settings import PodcastSettings
print('all imports ok')
"
# exits 0
```

---

### Pass 5.1 — Fake Engine Test

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

**Done**:

```bash
# above script exits 0
```

---

### Pass 5.2 — Local vs LLM Mode Selection from CLI

```bash
# Without --llm, the CLI assembles LocalScriptEngine.
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf> --skip-audio
# exits 0 (local generator)

# With --llm, the CLI assembles LLMScriptEngine.
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf> --llm --skip-audio
# exits 0 (LLM generator)
```

---

### Pass 5.3 — Book Endpoint Uses Injected Splitter

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
| `engines.protocols` exists | All adapters + endpoints | Pass 0.0 |
| `PodcastSettings` exists | Endpoints, CLI, tests | Pass 0.1 |
| `endpoints/podcast_types.py` exists | `endpoints/podcast.py`, consumers | Pass 0.3 |
| `__init__.py` files make packages importable | Pass 4.2 | Pass 0.2 |
| `LocalScriptEngine` exists | Endpoints, factory, CLI | Pass 1.1 |
| `LLMScriptEngine` exists | Endpoints, factory, CLI | Pass 1.2 |
| `WaveSpeedAudioEngine` exists | Endpoints, factory, CLI | Pass 1.3 |
| `PDFSplitterEngine` exists | Endpoints, factory, CLI | Pass 1.4 |
| `generate_chapter_podcast()` accepts injected engines | Pass 3.1, 5.1 | Pass 2.1 |
| `generate_book_podcast()` accepts injected splitter | Pass 3.1, 5.3 | Pass 2.2 |
| `engines.factory` assembles defaults | CLI | Pass 2.3 |
| Old `run_local/run_llm/run_tts` removed from endpoint | Pass 5.1 | Pass 4.1 |
| `sys.path.insert` removed from adapters | Clean decoupling | Pass 4.2 |

---

## What v8 Does and Does Not Decouple

**Now decoupled:**
- Script generator implementation (local vs LLM) ↔ endpoint
- TTS engine implementation ↔ endpoint
- PDF splitter implementation ↔ endpoint
- Output paths ↔ endpoint (via `PodcastSettings`)
- Speaker config ↔ `WaveSpeedAudioEngine` (can be injected)
- Shared types (`PodcastResult`, `ScriptMode`) ↔ endpoint implementation

**Still coupled:**
- The CLI still knows which engine classes exist (through the factory). This is acceptable;
  the next decoupling step would be a plugin registry or configuration-driven engine
  selection.
- `generate_chapter_podcast()` still knows that "script → optional audio" is the pipeline
  shape. Changing the pipeline shape (e.g., adding a validation stage) would require
  editing the endpoint.

v8 is therefore a **practical, type-safe** decoupling: engines are swappable, settings are
injectable, tests can use fakes, and factory functions expose protocol types.
