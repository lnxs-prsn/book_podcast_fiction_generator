# Build Specs v9 — Complete Podcast + Fiction Pipeline Refactor

> Derived from `build_specsv8.md`.
> v9 is a consolidation: it keeps all v8 engine-protocol / DI / type-safety improvements
> and re-integrates the fiction-pipeline callback refactor, cleanup passes, and
> behavioral verification that were present in v6 but dropped in v7/v8.
> Nothing from any prior spec is assumed to be built; this is the single definitive spec.
>
> Each pass names every file touched, the change type (add / modify / delete), and a
> done condition. Passes within a phase are ordered; complete each pass before the next.

---

## Gap Index (v8 → v9)

| Gap | Severity | Fixed In |
|-----|----------|----------|
| v7/v8 dropped the fiction-pipeline callback refactor entirely | High | Phase 6 |
| v7/v8 dropped cleanup passes (remove private loaders, shim entry points, update README) | High | Phase 7 |
| v7/v8 dropped behavioral verification passes | High | Phase 8 |
| v6 moved `run_local`/`run_llm`/`run_tts` into `endpoints/podcast.py` as an intermediate step; v9 skips that step and goes straight to engine adapters | Medium | Phase 3 |
| `endpoints/podcast_types.py` referenced but created late in v8; v9 creates it earlier (Phase 2) | Low | Pass 2.2 |

---

## Phase 0 — Invocation Model

**Goal**: Establish a single, consistent import model for all scripts before any code is
written. All subsequent passes assume this model is in place.

---

### Pass 0.0 — PYTHONPATH Convention

**Root cause of the sys.path.insert proliferation**: When a script is invoked as
`python src/cli/podcast.py`, Python adds `src/cli/` to `sys.path[0]` — not `src/`. Any
import of a sibling package (`from config import load_config`, `from endpoints.podcast import
...`) fails unless `src/` is added to the path. Earlier specs patched this per-file with
`sys.path.insert`. This spec fixes it once at the invocation level.

**The invocation model**: all scripts are run from `harnessv3/` with `src/` on PYTHONPATH:

```bash
# Canonical form — prefix every invocation:
PYTHONPATH=src python src/cli/podcast.py <args>
PYTHONPATH=src python src/cli/fiction.py <args>

# Or set once in the shell for a session:
export PYTHONPATH=src
```

**Persistent option** — add a `.env` at `harnessv3/` (uv reads this automatically):

```
# harnessv3/.env
PYTHONPATH=src
```

With the `.env` in place, `uv run python src/cli/podcast.py` picks up `PYTHONPATH=src`
without any prefix. Plain `python src/cli/podcast.py` still requires the explicit prefix
or shell export.

**What this eliminates in subsequent passes**:
- The module-level `sys.path.insert(0, str(_SRC))` block that earlier specs add to
  `endpoints/podcast.py`, `endpoints/slicer.py`, `endpoints/fiction.py`,
  `cli/podcast.py`, and `cli/fiction.py` — all removed.
- The module-level `sys.path.insert(0, str(Path(__file__).parent.parent))` blocks that
  earlier specs add to `tts/cli.py` and `call_api.py` in Pass 1.1 — also removed.

**What this does NOT change**:
- The `sys.path.insert` calls inside function bodies of `run_local()`, `run_llm()`, and
  `run_tts()` in `run_chapter.py` — those insert subdirectory paths for modules that
  have no `__init__.py` (`src/podcast_script_generator/llm/`, `src/tts/`). They are
  pre-existing, function-scoped, and are removed in Phase 7 when the old helpers are deleted.

**`_SRC` / `_ROOT` constants**: `endpoints/podcast.py` still needs `_SRC` and `_ROOT`
for computing output paths (`data/output/scripts/`, `data/output/audio/`). These constants
remain but are no longer needed for `sys.path` manipulation:

```python
from pathlib import Path

_SRC  = Path(__file__).parent.parent        # src/
_ROOT = Path(__file__).parent.parent.parent  # harnessv3/
_SCRIPTS_OUT = _ROOT / "data" / "output" / "scripts"
_AUDIO_OUT   = _ROOT / "data" / "output" / "audio"
```

No `import sys` and no `sys.path.insert` at module level in this file.

**Done**:
```
PYTHONPATH=src python -c "from config import load_config; print(load_config())"
# exits 0

PYTHONPATH=src python -c "from endpoints.podcast import generate_chapter_podcast; print('ok')"
# exits 0 after Pass 4.1 is complete; checking import path works before that point
```

---

## Phase 1 — Foundation

**Goal**: Config loading and exception hierarchy in place before any endpoints are written.
No behavior change to existing entry points.

---

### Pass 1.1 — Shared Config Loader

| File | Change |
|------|--------|
| `src/config.py` | add |
| `src/run_chapter.py` | modify — remove `_load_config()` definition; add `from config import load_config`; rename 1 call site |
| `src/run_book.py` | modify — same; rename 1 call site |
| `src/tts/cli.py` | modify — remove `_load_config()` definition; add `from config import load_config`; rename 3 call sites |
| `src/podcast_script_generator/llm/call_api.py` | modify — remove `_load_config()` definition; add `from config import load_config`; rename 4 call sites |

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

**Import pattern for `tts/cli.py` and `call_api.py`** — Pass 0.0 establishes
`PYTHONPATH=src`, so `src/` is already on the path at import time. No `sys.path.insert`
is needed:

```python
from config import load_config
```

Do NOT add `sys.path.insert` to these files.

**Add a guard comment near the import in each of the four modified files** —
this prevents an agent from silently re-adding a `sys.path.insert` when it encounters
an import failure during development:

```python
# If this import fails, do NOT add sys.path.insert here.
# The fix is: export PYTHONPATH=src in your shell (or prefix: PYTHONPATH=src python ...).
from config import load_config
```

Add this comment block in `tts/cli.py`, `call_api.py`, `run_chapter.py`, and
`run_book.py` — immediately above the `from config import load_config` line in each file.

`src/run_chapter.py` and `src/run_book.py` compute `SRC = Path(__file__).parent` (IS
`src/`). They need no path-insert — `from config import load_config` works as-is.

**Call-site renames for `tts/cli.py` and `call_api.py`**:

- `src/tts/cli.py`: rename `_load_config()` → `load_config()` at 3 call sites inside
  `build_api_payload()`, `send_to_api()`, and `cli_entrypoint()`.
- `src/podcast_script_generator/llm/call_api.py`: rename `_load_config()` → `load_config()`
  at all call sites inside the resolver functions. Locate them with:
  `grep -n "_load_config" src/podcast_script_generator/llm/call_api.py`

**Call-site renames for `run_chapter.py` and `run_book.py`**:

- `src/run_chapter.py`: rename `_load_config()` → `load_config()` at the call site inside
  `run_tts()` — `cfg_speakers = _load_config().get("speakers", {})`.
  Locate it with: `grep -n "_load_config" src/run_chapter.py`
- `src/run_book.py`: rename `_load_config()` → `load_config()` at the call site inside
  `main()` — `toc_page = args.toc_page or _load_config().get("toc_page")`.
  Locate it with: `grep -n "_load_config" src/run_book.py`

> Note: the novel_pipeline has a completely separate TOML-based `load_config()` in
> `src/fiction/pipeline/novel_pipeline/config.py`. That loader is NOT related to
> `src/config.py` and must not be modified.

**Done**:
```
PYTHONPATH=src python -c "from config import load_config; print(load_config())"
# exits 0

PYTHONPATH=src python src/run_chapter.py --help
# still works

grep -rn "_load_config" src/run_chapter.py src/run_book.py src/tts/cli.py \
  src/podcast_script_generator/llm/call_api.py
# returns empty

grep -rn "sys.path.insert" src/tts/cli.py src/podcast_script_generator/llm/call_api.py
# returns empty (module-level inserts must not be present)
```

---

### Pass 1.2 — Podcast Exception Hierarchy

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/exceptions.py` | add |
| `src/podcast_script_generator/llm/main.py` | modify — `sys.exit()` calls → typed raises; add `__main__` guard |
| `src/tts/cli.py` | modify — remap `AuthError` → `TTSSubmissionError`; remap `RuntimeError` (WaveSpeed) → `TTSSubmissionError`; remap timeout/network errors → `TTSTimeoutError`; broaden `cli_entrypoint()` catch |
| `src/run_chapter.py` | modify — catch `PodcastError` at CLI boundary; print to stderr; `sys.exit(1)` |

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

**`tts/cli.py` remapping** — type-remap only (no new raises, just replace types):
- Delete local `AuthError` class definition.
- `raise AuthError(...)` → `raise TTSSubmissionError(...)`
- `raise RuntimeError(f"WaveSpeed job failed...")` → `raise TTSSubmissionError(...)`
- `raise ConnectionError(...)` → `raise TTSTimeoutError(...)`
- `cli_entrypoint()` catch: `(ValueError, AuthError, ConnectionError, RuntimeError, OSError)`
  → `(PodcastError, ValueError, OSError)`

**Exception import path for `tts/cli.py`** — `PYTHONPATH=src` is set (Pass 0.0),
so the full dotted import path works as-is:

```python
from podcast_script_generator.llm.exceptions import (
    PodcastError, TTSSubmissionError, TTSTimeoutError
)
```

**`main.py` update** — replace `sys.exit()` inside `main()` and update `__main__` guard:

```python
# Inside main():
#   FileNotFoundError path → raise PDFExtractionError(...)
#   ValueError / KeyError path → raise ScriptGenerationError(...)
#   catch-all → raise PodcastError(...)

if __name__ == "__main__":
    try:
        main()
    except PodcastError as e:
        import sys
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

**Done condition — corrected grep for `main.py`**:

```
grep -rn "sys.exit" src/podcast_script_generator/ | grep -v "__main__"
# returns empty (the sys.exit(1) in the __main__ guard is the allowed exception)

grep "sys.exit" src/tts/cli.py
# returns hits only inside cli_entrypoint()

grep "sys.exit" src/run_chapter.py
# returns exactly one hit (the CLI boundary catch)
```

---

### Pass 1.3 — Structured Logging Migration

| File | Change |
|------|--------|
| `src/podcast_script_generator/llm/call_api.py` | modify — add `import logging` + `logger`; `print(f"OpenRouter 429...")` → `logger.debug(...)` |
| `src/podcast_script_generator/llm/save_output.py` | modify — add `import logging` + `logger`; `print(f"Wrote N files...")` → `logger.debug(...)` |
| `src/tts/cli.py` | modify — add `import logging` + `logger`; convert 5 prints in `send_to_api()` to logger calls |
| `src/run_chapter.py` | modify — add `logging.basicConfig(level=logging.INFO, format="%(message)s")` at entry |
| `src/run_book.py` | modify — same |

**Logger setup pattern** (add to each of the three library files):

```python
import logging
logger = logging.getLogger(__name__)
```

**`tts/cli.py` print mapping** — all 5 prints inside `send_to_api()`:
- Submission confirmation (`TTS submitted  request_id=...`) → `logger.info(...)`
- Recovery-file notice (`Recovery file  {job_file}`) → `logger.info(...)` (conditional on `job_file`)
- Polling start (`Polling for completion...`) → `logger.info(...)`
- Per-poll status (`[{elapsed}s] status=...`) → `logger.debug(...)`
- Completion confirmation (`[done] {elapsed}s`) → `logger.info(...)`

> The prints in `run_chapter.py`'s `main()` are intentionally left as-is here — they are
> CLI output that will be stripped entirely in Phase 7 when the body migrates to
> `generate_chapter_podcast()`. Premature conversion would complicate that pass.

**Done**:

```
grep -rn "^\s*print(" src/podcast_script_generator/ src/tts/cli.py
# returns empty

PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# produces INFO-level output without crashing
```

---

## Phase 2 — Utilities + Types

**Goal**: Extract shared utilities and canonical types before endpoints or engines are written.

---

### Pass 2.1 — Speaker Normalization Extract

| File | Change |
|------|--------|
| `src/util/__init__.py` | add — empty |
| `src/util/normalize.py` | add — `normalize_speakers(text: str) -> str` |
| `src/run_chapter.py` | modify — delete `_to_speaker_format()` definition; update 3 call sites; add import |

**What to extract**: the function is currently named `_to_speaker_format` in `run_chapter.py`.
Locate it with: `grep -n "def _to_speaker_format" src/run_chapter.py`.
This pass is an extraction AND a rename to `normalize_speakers`.

**Three call sites to update in `run_chapter.py`**:
- Inside `run_local()` — `grep -n "_to_speaker_format" src/run_chapter.py` will show all three
- Inside `run_llm()` — two calls (one for `fiction_meta` branch, one for all other modes)

**Import to add**:
```python
from util.normalize import normalize_speakers
```

(`PYTHONPATH=src` is set, so this resolves correctly from any invocation.)

**Done**:

```
PYTHONPATH=src python -c \
  "from util.normalize import normalize_speakers; print(normalize_speakers('ALEX: hi'))"
# exits 0; returns a Speaker 0:-prefixed line

PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# behavior unchanged

ls src/util/__init__.py src/util/normalize.py
# both files exist
```

---

### Pass 2.2 — Shared Podcast Types

| File | Change |
|------|--------|
| `src/endpoints/__init__.py` | add — empty (if missing) |
| `src/endpoints/podcast_types.py` | add — `ScriptMode` enum and `PodcastResult` dataclass |

**Pre-flight check** — `ok` becomes a `@property` in this pass. If any existing code
constructs `PodcastResult(ok=True, ...)` or `PodcastResult(ok=False, ...)`, it will break
at runtime with `TypeError: __init__() got an unexpected keyword argument 'ok'`. Verify
the codebase is clean before creating the class:

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

`ok` is a read-only property computed from `error`. This eliminates the impossible
`PodcastResult(ok=True, error=ValueError(...))` state.

**Constructor usage throughout the spec**:
- Success with audio: `PodcastResult(script_path=script_out, audio_path=audio_path)`
- Success without audio: `PodcastResult(script_path=script_out)`
- Failure: `PodcastResult(error=some_exception)`
- `slice_only` success: `PodcastResult()`

**Done**:

```
ls src/endpoints/__init__.py
# file exists

PYTHONPATH=src python -c \
  "from endpoints.podcast_types import ScriptMode, PodcastResult
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
| `src/util/prompt.py` | add — `prompt_user()` function |

**Extract to `src/util/prompt.py`** — both `cli/fiction.py` (Pass 6.4) and
`novel_pipeline/cli.py` need this function. Extract it once here rather than duplicating:

```python
# src/util/prompt.py

def prompt_user(chapter_num: int, draft_text: str) -> bool:
    print(f"Chapter {chapter_num} draft (first 500 chars):\n{draft_text[:500]}\n")
    choice = input("[y/n/q]: ").strip().lower()
    if choice == "q":
        raise KeyboardInterrupt
    return choice == "y"
```

**`q` quit semantics**: `q` raises `KeyboardInterrupt`, which propagates to
`run_session()`'s existing `except KeyboardInterrupt` handler — the correct quit path.
Do not return `False` for `q` — that would loop for regeneration.

**Done**:

```
PYTHONPATH=src python -c "from util.prompt import prompt_user; print('ok')"
# exits 0
```

---

## Phase 3 — Engine Protocols + Adapters

**Goal**: Wrap every concrete engine behind a protocol, inject them into endpoints, and make
them replaceable without editing endpoint code.

---

### Pass 3.0 — Package `__init__.py` Cleanup

**Goal**: Make every engine directory importable as a package so `sys.path.insert` can be
deleted in Phase 7.

| File | Change |
|------|--------|
| `src/podcast_script_generator/__init__.py` | add — empty |
| `src/podcast_script_generator/llm/__init__.py` | add — empty |
| `src/decide_later/__init__.py` | add — empty (if missing) |
| `src/decide_later/local/__init__.py` | add — empty (if missing) |

**Done**:

```
PYTHONPATH=src python -c \
  "import podcast_script_generator; import podcast_script_generator.llm; print('ok')"
# exits 0

PYTHONPATH=src python -c \
  "import decide_later.local; print('ok')"
# exits 0 (if the local generator package exists)
```

---

### Pass 3.1 — Engine Protocols

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

```
PYTHONPATH=src python -c \
  "from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine; print('ok')"
# exits 0
```

---

### Pass 3.2 — PodcastSettings

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

### Pass 3.3 — Local Script Engine

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

```
PYTHONPATH=src python -c \
  "from engines.local_script import LocalScriptEngine; print('ok')"
# exits 0
```

---

### Pass 3.4 — LLM Script Engine

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

```
PYTHONPATH=src python -c \
  "from engines.llm_script import LLMScriptEngine; print('ok')"
# exits 0
```

---

### Pass 3.5 — WaveSpeed Audio Engine

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

```
PYTHONPATH=src python -c \
  "from engines.wavespeed_audio import WaveSpeedAudioEngine; print('ok')"
# exits 0
```

---

### Pass 3.6 — PDF Splitter Engine

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

```
PYTHONPATH=src python -c \
  "from engines.pdf_splitter import PDFSplitterEngine; print('ok')"
# exits 0
```

---

### Pass 3.7 — Engine Factory

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

```
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

## Phase 4 — Podcast Endpoints

**Goal**: `generate_chapter_podcast()` and `generate_book_podcast()` are directly callable
with no argparse, no print, no sys.exit. They receive engines and a settings object instead
of hard-coding behavior.

---

### Pass 4.1 — `generate_chapter_podcast()`

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
- `run_local()`, `run_llm()`, `run_tts()` definitions (deleted in Phase 7)
- Module-level `_SCRIPTS_OUT` / `_AUDIO_OUT` constants
- `import re` at module level (moved into `LLMScriptEngine`)
- Fiction-content discovery (moved into `LLMScriptEngine`)
- `import sys` and `sys.path.insert` at module level

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
| `src/endpoints/slicer.py` | add — thin shim re-exporting the splitter adapter |

**Full content of `src/endpoints/slicer.py`** — no `sys.path.insert` (PYTHONPATH
from Pass 0.0 makes `slicer.pdf_splitter` resolvable):

```python
from engines.pdf_splitter import PDFSplitterEngine  # noqa: F401
from slicer.pdf_splitter import run_splitter  # noqa: F401

__all__ = ["run_splitter", "PDFSplitterEngine"]
```

After this pass, `src/endpoints/podcast.py` imports the splitter from `engines.factory`
(via `default_splitter_engine()`) rather than from `slicer.pdf_splitter` directly.

**Done**:

```
PYTHONPATH=src python -c "from endpoints.slicer import run_splitter; print('ok')"
# exits 0
```

---

## Phase 5 — Podcast CLI + TTS Boundary

**Goal**: `cli/podcast.py` assembles engines and settings, then calls endpoints. It does not
contain business logic. `tts/cli.py` `main()` is a clean engine function with no argparse.

---

### Pass 5.1 — TTS Engine Boundary

| File | Change |
|------|--------|
| `src/tts/cli.py` | modify — move `import argparse` from module level into `cli_entrypoint()` body |

The only change required is moving that one import line. `main()` already has the correct
signature. `cli_entrypoint()` already exists. Locate the module-level argparse import with:
`grep -n "^import argparse" src/tts/cli.py`

**Done**:

```
grep "argparse" src/tts/cli.py
# returns hits only inside cli_entrypoint()

grep "sys.exit" src/tts/cli.py
# returns hits only inside cli_entrypoint()
```

---

### Pass 5.2 — Podcast CLI Wrapper

| File | Change |
|------|--------|
| `src/cli/__init__.py` | add — empty |
| `src/cli/podcast.py` | add — argparse wrapper; assembles engines via factory |

**No `sys.path.insert` in this file** — `PYTHONPATH=src` (Pass 0.0) makes all
imports resolve correctly without path surgery.

**PYTHONPATH guard** — add at the top of `src/cli/podcast.py`, before any local
imports. Turns a silent `ModuleNotFoundError` into an actionable message:

```python
import sys
from pathlib import Path
if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/podcast.py ..."
    )
```

This is detection, not a patch — it does not add anything to `sys.path`.

**Logging configuration** — `run_chapter.py` currently configures `logging.basicConfig`
(added in Pass 1.3), but `run_chapter.py` is shimmed away in Phase 7. Add the same
configuration to `src/cli/podcast.py`'s `main()` so TTS polling output and INFO-level
messages remain visible after shimming:

```python
import logging

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # ... rest of main body
```

**Engine assembly inside `main()`:**

```python
from engines.factory import (
    default_local_script_engine,
    default_llm_script_engine,
    default_audio_engine,
    default_splitter_engine,
)
from settings import PodcastSettings

settings = PodcastSettings()

script_engine = (
    default_llm_script_engine(mode=args.mode)
    if args.llm
    else default_local_script_engine()
)
audio_engine = None if args.skip_audio else default_audio_engine()
```

**Routing logic**: `--book PDF` is the router flag. Absent → routes to
`generate_chapter_podcast()` using positional `pdf`. Present → routes to
`generate_book_podcast()`.

**Full argument surface**:

Chapter flags:
- `pdf` (positional)
- `--llm`
- `--skip-audio`
- `--mode`
- `--context`
- `--context-file`
- `--fiction-dir`

Book flags:
- `--book`
- `--toc-page`
- `--no-ocr`
- `--force`
- `--slice-only`

**`--mode` choices** — use the full set for chapter routing, the restricted set for
book routing:

```python
CHAPTER_MODES = ["2person", "4person", "code", "realworld", "fiction_meta"]
BOOK_MODES    = ["2person", "4person", "code", "realworld"]
# fiction_meta requires per-chapter fiction files; not supported in batch
```

After parsing, if `args.book` is set and `args.mode == "fiction_meta"`, print an error and
`sys.exit(1)` — `fiction_meta` is not supported in book mode.

**`--fiction-dir` handling** — the endpoint owns discovery; the CLI just passes the path:

```python
fiction_dir = Path(args.fiction_dir) if args.fiction_dir else None
# Pass to generate_chapter_podcast(fiction_dir=fiction_dir)
```

**`--context-file` handling** — read the file content and pass as `context`:
```python
if args.context_file:
    context = Path(args.context_file).read_text(encoding="utf-8").strip()
```

**`--slice-only` routing**: pass `slice_only=True` to `generate_book_podcast()`.

**Interactive `toc_page` prompt** (the only place it may appear):
```python
if args.book and args.toc_page is None:
    try:
        toc_page = int(input("TOC page number: "))
    except (ValueError, EOFError):
        toc_page = None
else:
    toc_page = args.toc_page
```

Print result paths to stdout. Print errors to stderr. `sys.exit(1)` on any failure.

**Done**:

```
PYTHONPATH=src python src/cli/podcast.py --help
# exits 0; shows both `pdf` positional and `--book` flag

PYTHONPATH=src python src/cli/podcast.py <fixture_pdf>
# produces identical output to PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
```

---

### Pass 5.3 — Path Override Flags (Optional)

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

```
PYTHONPATH=src python src/cli/podcast.py --help | grep -E "scripts-out|audio-out|chapters-dir"
# shows the flags
```

---

## Phase 6 — Novel Pipeline Callback Refactor

**Goal**: `session.py` has no `input()` in the chapter-approval path, no `sys.exit()`.
Approval injected via callable. Tests drive the session without touching stdin.

---

### Pass 6.1 — SessionResult Dataclass + Callback Type

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — add `ApproveChapterFn` type alias; add `SessionResult` dataclass |

**Definitions to add** (no behavior change in this pass):
```python
from typing import Callable
from dataclasses import dataclass

ApproveChapterFn = Callable[[int, str], bool]
# args: (chapter_number, full_chapter_text) → True = approve, False = reject

@dataclass
class SessionResult:
    chapters_written: int
    final_chapter_number: int
    cost_usd: float
    completed: bool
    state_path: Path
```

`cost_usd` is populated from `current_totals(config)["session_total"]` (already imported).
`state_path` is populated from `Path(config["state_file_path"])`.

`Callable` and `dataclass` imports need to be added; `Path` is already imported.

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
| `src/fiction/pipeline/novel_pipeline/session.py` | modify — inject callback; replace `sys.exit(1)` with `raise`; convert draft-preview prints to logger; return `SessionResult`; thread callback to `_run_one_chapter()` |

**Changes in detail:**

1. Add `approve_chapter: ApproveChapterFn = lambda n, text: True` parameter to
   `run_session()`.

2. Add `approve_chapter: ApproveChapterFn` parameter to `_run_one_chapter()`. Pass it
   through from `run_session()` at the `_run_one_chapter(...)` call site.

3. Inside `_run_one_chapter()`: replace the entire approval block — both the
   `auto_approve` fast-path and the `input("Approve and update living doc? [y/n/q]: ")`
   branch — with:
   ```python
   approved = approve_chapter(chapter_num, chapter_text)
   if not approved:
       # rejected: log and continue for regeneration
       log_event("chapter_rejected", {"chapter": chapter_num, "attempt": attempt})
       print(f"Rejected. Draft remains at {draft_path}. Attempt {attempt}/{max_rejections}.")
       chapter_text = None
       continue
   break  # approved
   ```
   `True` → proceeds to promotion; `False` → rejected (loops for regeneration);
   `KeyboardInterrupt` (raised by the callback on `q`) → propagates to caller.

   The `[auto-approve] approving draft` print that was in the old `auto_approve`
   fast-path is removed with the block. It is not converted to a logger call — it simply
   does not appear under callback-based approval.

4. Convert the draft-preview print block to `logger.info(...)`. Locate it with:
   `grep -n "Draft saved\|draft_path" src/fiction/pipeline/novel_pipeline/session.py`

5. Replace `sys.exit(1)` in `except KeyboardInterrupt:` with `raise KeyboardInterrupt`
   so it propagates to the caller. Locate it with:
   `grep -n "KeyboardInterrupt" src/fiction/pipeline/novel_pipeline/session.py`

6. Return `SessionResult` at the 2 early-exit points and the normal completion
   fall-through — the current code has exactly 2 early `return` statements plus the
   post-loop fall-through. Locate the early exits with:
   `grep -n "should_continue\|Proceed" src/fiction/pipeline/novel_pipeline/session.py`

   - Early exit when `should_continue` is False →
     `return SessionResult(chapters_written=0, final_chapter_number=0, cost_usd=0.0, completed=False, state_path=Path(config["state_file_path"]))`
   - Early exit when "Proceed?" is declined → same pattern
   - Normal completion (post-loop fall-through) →
     `return SessionResult(chapters_written=completed, final_chapter_number=current_chapter, cost_usd=current_totals(config)["session_total"], completed=True, state_path=Path(config["state_file_path"]))`

**`input()` Done condition — scope clarification**:

`session.py` also contains `_prompt_yes_no()` and `_prompt_choice()`, both of which call
`input()`. These helpers are gated by `auto=True` paths and are intentionally preserved
for interactive use.

```
grep "input()" src/fiction/pipeline/novel_pipeline/session.py | \
  grep -v "_prompt_yes_no\|_prompt_choice"
# returns empty

grep "sys.exit" src/fiction/pipeline/novel_pipeline/session.py
# returns empty

# Behavioral test:
# run_session(config, auto_approve=True, approve_chapter=lambda n, t: True)
# completes without touching stdin
```

---

### Pass 6.3 — Novel Pipeline CLI Update

| File | Change |
|------|--------|
| `src/fiction/pipeline/novel_pipeline/cli.py` | modify — add `approve_fn`; pass `approve_chapter=approve_fn` to `run_session()`; import `prompt_user` |

**`novel_pipeline/cli.py` update**:

> The `--auto-approve` flag already exists and is already wired. Do NOT add it again.

1. Import `prompt_user`:
   ```python
   from util.prompt import prompt_user
   ```

2. After parsing args, construct:
   ```python
   if args.auto_approve:
       approve_fn = lambda n, t: True
   else:
       approve_fn = prompt_user
   ```

3. Pass `approve_chapter=approve_fn` to `run_session()`.

**Done**:

```
PYTHONPATH=src python src/fiction/pipeline/novel_pipeline/cli.py \
  --auto-approve <config>
# runs without any stdin prompts
```

---

### Pass 6.4 — Fiction Endpoint Wrapper

| File | Change |
|------|--------|
| `src/endpoints/fiction.py` | add |

**No `sys.path.insert`** — `PYTHONPATH=src` covers all imports.

**Pre-condition** — `novel_pipeline` must be importable before writing this file.
The `novel_pipeline.egg-info` at `src/fiction/pipeline/novel_pipeline.egg-info/` means
the package was installed in editable mode. With the venv active, the egg-link makes it
importable. Verify before proceeding:

```
PYTHONPATH=src python -c "import novel_pipeline; print('ok')"
# Must exit 0. If this fails, run:
#   cd src/fiction/pipeline && pip install -e . && cd -
# then re-run the check before continuing.
```

**Import resolution** — with the venv active and the egg installed:

```python
from novel_pipeline.config import load_config
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult
```

**No fallback `sys.path.insert`** — if the import fails, the fix is to reinstall the
package (see pre-condition above), not to add a runtime path hack. A fallback
`sys.path.insert` here would contradict Pass 0.0's convention.

> The TOML loader is `load_config(path)` in `novel_pipeline/config.py`. There is no
> `load_config_toml()` alias — do not create one.

**Function signature**:
```python
def run_novel_session(
    config_path: str | Path,
    resume: bool = False,
    auto_approve: bool = False,
    dry_run: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: ApproveChapterFn | None = None,
) -> SessionResult:
```

**Implementation**:
```python
def run_novel_session(config_path, resume=False, auto_approve=False,
                      dry_run=False, chapter_start=None,
                      ignore_cost_limit=False, approve_chapter=None) -> SessionResult:
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

# Calling run_novel_session(..., approve_chapter=lambda n, t: n != 2)
# rejects chapter 2 without touching stdin
```

---

### Pass 6.5 — Fiction CLI Shim

| File | Change |
|------|--------|
| `src/cli/fiction.py` | add — thin argparse wrapper |

**No `sys.path.insert`** — `PYTHONPATH=src` covers all imports.

**PYTHONPATH guard** — same guard as Pass 5.2, add at the top of `src/cli/fiction.py`:

```python
import sys
from pathlib import Path
if str(Path(__file__).parent.parent) not in sys.path:
    raise RuntimeError(
        "PYTHONPATH is not set correctly. Run with:\n"
        "  PYTHONPATH=src python src/cli/fiction.py ..."
    )
```

Mirror the exact flag set from `src/fiction/pipeline/novel_pipeline/cli.py`:
`--config` (required), `--auto-approve`, `--dry-run`, `--resume`, `--chapter-start`,
`--ignore-cost-limit`.

**Import `prompt_user` from `src/util/prompt.py`** — do NOT redefine it here:
```python
from util.prompt import prompt_user
```

Construct `approve_fn` the same way as Pass 6.3. Call `run_novel_session()` from
`src/endpoints/fiction.py`.

**Done**:

```
PYTHONPATH=src python src/cli/fiction.py --help
# exposes the same flags as src/fiction/pipeline/novel_pipeline/cli.py

PYTHONPATH=src python src/cli/fiction.py --auto-approve <config>
# produces no stdin prompts
```

---

## Phase 7 — Cleanup

**Goal**: Dead code removed. Root-level entry points shimmed. README reflects new CLI paths.

---

### Pass 7.1 — Remove Private Config Loaders

**Pre-condition**: Pass 1.1 is complete and all four files use `load_config` from
`src/config.py`. Verify with:
```
grep -rn "from config import load_config" src/run_chapter.py src/run_book.py \
  src/tts/cli.py src/podcast_script_generator/llm/call_api.py
```
Must return 4 hits before proceeding.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — delete `_load_config()` definition |
| `src/run_book.py` | modify — same |
| `src/tts/cli.py` | modify — same |
| `src/podcast_script_generator/llm/call_api.py` | modify — same |

Locate each definition with:
`grep -n "def _load_config" src/run_chapter.py src/run_book.py src/tts/cli.py src/podcast_script_generator/llm/call_api.py`

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

Verify no remaining imports first:
```
grep -rn "run_simple" src/
# must return empty before deletion
```

The file uses `sys.exit()`, `input()`, and hardcoded global config — none of these need
cleanup before deletion. It is an orphaned prototype superseded by the novel_pipeline.

**Done**:

```
ls src/fiction/run_simple.py
# returns "No such file"

grep -rn "run_simple" src/
# returns empty
```

---

### Pass 7.3 — Delete Legacy Helpers

| File | Change |
|------|--------|
| `src/endpoints/podcast.py` | modify — delete `run_local()`, `run_llm()`, `run_tts()` if present |
| `src/run_chapter.py` | modify — delete `run_local()`, `run_llm()`, `run_tts()` definitions |

In v9 the engines live in `src/engines/` as adapter classes; the old helper functions
should never have been moved into `endpoints/podcast.py`. If they were (from an earlier
partial implementation), delete them now.

Verify nothing imports them from `endpoints/podcast.py`:

```
grep -rn "from endpoints.podcast import.*run_" src/
# must return empty
```

**Done**:

```
grep "def run_local\|def run_llm\|def run_tts" src/endpoints/podcast.py src/run_chapter.py
# returns empty
```

---

### Pass 7.4 — Remove `sys.path.insert` from Engine Adapters

| File | Change |
|------|--------|
| `src/engines/local_script.py` | modify — remove constructor path hack if packages are importable without it |
| `src/engines/llm_script.py` | modify — same |
| `src/engines/wavespeed_audio.py` | modify — same |

**When to remove**: once Pass 3.0's `__init__.py` additions and `PYTHONPATH=src` make the
packages resolvable without extra path manipulation.

If `decide_later.local` still cannot be imported without the path insert, keep the
constructor parameter but document it as a transitional workaround.

**Done**:

```
grep -rn "sys.path.insert" src/engines/
# returns empty (or only documented transitional lines)
```

---

### Pass 7.5 — Shim run_chapter.py and run_book.py

**Pre-conditions** — verify ALL of these before proceeding:

1. Passes 4.1, 4.2, and 5.2 are complete.

2. `src/cli/podcast.py` has all book-level flags:
   ```
   PYTHONPATH=src python src/cli/podcast.py --help | grep -- "--book"
   # returns a hit
   ```

3. Helper functions have been deleted from `run_chapter.py` and `endpoints/podcast.py`.
   Verify:
   ```
   grep "def run_local\|def run_llm\|def run_tts" src/run_chapter.py
   # returns empty
   ```

4. `run_book.py` no longer references `run_chapter`:
   ```
   grep "import run_chapter" src/run_book.py
   # must return empty before proceeding
   ```

> **Critical**: Apply BOTH shims in the same commit.

| File | Change |
|------|--------|
| `src/run_chapter.py` | modify — replace entire body with `from cli.podcast import main; main()` |
| `src/run_book.py` | modify — replace entire body with `from cli.podcast import main; main()` |

**Done**:

```
PYTHONPATH=src python src/run_chapter.py <fixture_pdf>
# produces output identical to:
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf>

PYTHONPATH=src python src/run_book.py --help
# exits 0 and exposes the --book flag
```

---

### Pass 7.6 — Update initial_readme.md

| File | Change |
|------|--------|
| `src/initial_readme.md` | modify — update Entry Points section |

List `src/cli/podcast.py` and `src/cli/fiction.py` as primary CLIs. Document
`run_chapter.py` and `run_book.py` as shims forwarding to `src/cli/podcast.py`. Document
the `PYTHONPATH=src` invocation convention.

**Done**:

```
grep "src/cli/podcast.py" src/initial_readme.md
# returns a hit

grep "PYTHONPATH" src/initial_readme.md
# returns a hit
```

---

## Phase 8 — Behavioral Verification

**Goal**: Confirm end-to-end behavior of each new endpoint. Import verification runs
first in a dedicated pass — if it fails, behavioral passes do not run and the failure
cannot be misread as a logic bug.

---

### Pass 8.0 — Import Surface Verification

Run before any behavioral pass. A failure here means a package is missing or
PYTHONPATH is wrong — not a logic error in the endpoint code.

```bash
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast, generate_book_podcast
from endpoints.podcast_types import PodcastResult, ScriptMode
from endpoints.slicer import run_splitter
from endpoints.fiction import run_novel_session
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
from util.normalize import normalize_speakers
from util.prompt import prompt_user
print('all imports ok')
"
# Must exit 0 before running passes 8.1–8.6.
# If this fails: check PYTHONPATH, __init__.py files, and novel_pipeline installation.
```

---

### Pass 8.1 — Podcast Endpoint Smoke Tests

Run only after Pass 8.0 succeeds. All checks should exit 0.

```bash
# PodcastResult invariants
PYTHONPATH=src python -c "
from endpoints.podcast_types import PodcastResult
from pathlib import Path
r1 = PodcastResult(error=ValueError('x'))
r2 = PodcastResult(script_path=Path('/tmp/x'))
r3 = PodcastResult()
assert not r1.ok, 'ok should be False when error is set'
assert r2.ok,     'ok should be True when error is None'
assert r3.ok,     'empty PodcastResult should be ok'
print('PodcastResult invariants ok')
"

# Missing PDF returns failure result, not a raised exception
PYTHONPATH=src python -c "
from endpoints.podcast import generate_chapter_podcast
from pathlib import Path
r = generate_chapter_podcast(Path('/nonexistent/file.pdf'))
assert not r.ok, f'expected ok=False, got: {r}'
assert r.error is not None
print('missing PDF handled gracefully ok')
"

# fiction_meta without fiction_dir returns failure result
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

Run only after Pass 8.0 succeeds.

```bash
# prompt_user has the expected signature
PYTHONPATH=src python -c "
from util.prompt import prompt_user
import inspect
sig = inspect.signature(prompt_user)
params = list(sig.parameters)
assert params == ['chapter_num', 'draft_text'], f'unexpected signature: {params}'
print('prompt_user signature ok')
"
```

---

### Pass 8.3 — Shim Equivalence Check

Run after Pass 7.5.

```bash
# Both shims expose the expected flags
PYTHONPATH=src python src/run_chapter.py --help | grep -q "\-\-help" \
  && echo "run_chapter shim ok"
PYTHONPATH=src python src/run_book.py --help | grep -q "\-\-book" \
  && echo "run_book shim ok"

# No private symbols leak through the shim into the module namespace
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

### Pass 8.5 — Local vs LLM Mode Selection from CLI

```bash
# Without --llm, the CLI assembles LocalScriptEngine.
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf> --skip-audio
# exits 0 (local generator)

# With --llm, the CLI assembles LLMScriptEngine.
PYTHONPATH=src python src/cli/podcast.py <fixture_pdf> --llm --skip-audio
# exits 0 (LLM generator)
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
| `PYTHONPATH=src` invocation model in place | All passes | Pass 0.0 |
| `src/config.py` exists | Passes 1.2–7.1 | Pass 1.1 |
| `_load_config()` call sites renamed (all 9 across 4 files) | Pass 7.1 Done condition | Pass 1.1 |
| `PodcastError` hierarchy exists | Passes 4.1, 5.2 | Pass 1.2 |
| `src/util/__init__.py`, `src/util/normalize.py` exist | Pass 3.3, 3.4 | Pass 2.1 |
| `src/util/prompt.py` exists | Passes 6.3, 6.5 | Pass 2.3 |
| `PodcastResult`, `ScriptMode` defined with correct types (`ok` as property) | Pass 4.1 | Pass 2.2 |
| `engines.protocols` exists | All adapters + endpoints | Pass 3.1 |
| `PodcastSettings` exists | Endpoints, CLI, tests | Pass 3.2 |
| `__init__.py` files make packages importable | Pass 7.4 | Pass 3.0 |
| `LocalScriptEngine` exists | Endpoints, factory, CLI | Pass 3.3 |
| `LLMScriptEngine` exists | Endpoints, factory, CLI | Pass 3.4 |
| `WaveSpeedAudioEngine` exists | Endpoints, factory, CLI | Pass 3.5 |
| `PDFSplitterEngine` exists | Endpoints, factory, CLI | Pass 3.6 |
| `engines.factory` assembles defaults | CLI | Pass 3.7 |
| `generate_chapter_podcast()` accepts injected engines | Pass 5.2, 8.4 | Pass 4.1 |
| `generate_book_podcast()` accepts injected splitter | Pass 5.2, 8.6 | Pass 4.2 |
| `src/endpoints/slicer.py` exists | Import surface | Pass 4.3 |
| `logging.basicConfig` configured in `cli/podcast.py main()` | Pass 7.5 (shim removes it from run_chapter) | Pass 5.2 |
| `src/cli/podcast.py` has full book flags incl. `--slice-only` | Pass 7.5 pre-condition | Pass 5.2 |
| `SessionResult` + `ApproveChapterFn` defined | Pass 6.2 | Pass 6.1 |
| `approve_chapter` wired in `run_session()` + `_run_one_chapter()` | Passes 6.3, 6.4 | Pass 6.2 |
| `novel_pipeline` importable (egg installed) | Pass 6.4 | Pre-condition: `pip install -e .` |
| `run_novel_session()` exists | Pass 6.5 | Pass 6.4 |
| All four files use shared `load_config` | Pass 7.1 | Pass 1.1 |
| `src/endpoints/podcast.py` has full book logic | Pass 7.5 | Pass 4.2 |
| Pass 8.0 import surface verified | Passes 8.1–8.6 | Pass 8.0 |
| Old `run_local/run_llm/run_tts` removed | Clean decoupling | Pass 7.3 |
| `sys.path.insert` removed from adapters | Clean decoupling | Pass 7.4 |

---

## What v9 Does and Does Not Decouple

**Now decoupled:**
- Script generator implementation (local vs LLM) ↔ endpoint
- TTS engine implementation ↔ endpoint
- PDF splitter implementation ↔ endpoint
- Output paths ↔ endpoint (via `PodcastSettings`)
- Speaker config ↔ `WaveSpeedAudioEngine` (can be injected)
- Shared types (`PodcastResult`, `ScriptMode`) ↔ endpoint implementation
- Approval logic ↔ fiction pipeline (via `ApproveChapterFn` callback)

**Still coupled:**
- The CLI still knows which engine classes exist (through the factory). This is acceptable;
  the next decoupling step would be a plugin registry or configuration-driven engine
  selection.
- `generate_chapter_podcast()` still knows that "script → optional audio" is the pipeline
  shape. Changing the pipeline shape (e.g., adding a validation stage) would require
  editing the endpoint.

v9 is therefore a **practical, type-safe, complete** decoupling: engines are swappable,
settings are injectable, tests can use fakes, factory functions expose protocol types,
and the fiction pipeline is fully callback-driven.
