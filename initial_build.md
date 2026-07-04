# Initial Build — EPUB Format Support

## Goal
Add EPUB as a supported source format across the entire pipeline (seed generation, single-chapter podcast, whole-book podcast, interactive menu) by introducing a format adapter registry. New formats plug into one place; no core pipeline file changes when a format is added.

## Implementation Order

| Phase | Name | Features | Leaves system in state |
|---|---|---|---|
| 1 | Registry Foundation | F1, F4 | Registry API works; protocols use format-agnostic names; nothing registered yet |
| 2 | Source Format Adapters | F2, F3a, F3b | PDF and EPUB both registered; extractors and splitters callable |
| 3 | Engine Layer | F5a, F5b | Engines and factory route through registry; PDF and EPUB extraction works |
| 4 | Podcast Pipeline Endpoints | F6, F7a, F7b | All podcast endpoints format-agnostic; EPUB whole-book podcast works |
| 5 | Consumer Pipelines and UI | F8, F9, F10 | Every consumer (seed_gen, main.py, menu) format-agnostic; full EPUB support |

Complete each phase in order. Run the end-of-phase verification before starting the next phase.

---

## Phase 1 — Registry Foundation

**Goal:** Create the `format_adapters` package with a stable registry API and rename PDF-specific parameter names in the engine protocols. No adapters are registered at the end of this phase.

**Unlocks:** Every other phase. F1 is the foundation all downstream features import from.

---

### Pass 1.1 — Create registry module

**What changes:** Creates `src/format_adapters/registry.py` with the full registry implementation: `register_adapters`, `get_extractor`, `get_splitter`, `registered_extensions`, `UnsupportedFormatError`.

**Files:** `src/format_adapters/registry.py`

**Done when:**
- [ ] `src/format_adapters/registry.py` exists
- [ ] `UnsupportedFormatError` is defined as a subclass of `Exception`
- [ ] `register_adapters(extension: str, extractor: Callable, splitter: type | None) -> None` stores the pair keyed by `extension.lower()`; calling it twice for the same extension overwrites (last write wins)
- [ ] `get_extractor(path_or_ext: str | Path) -> Callable` normalizes input to lowercase extension, returns the extractor or raises `UnsupportedFormatError`
- [ ] `get_splitter(path_or_ext: str | Path) -> type` normalizes input, returns the splitter class or raises `UnsupportedFormatError`; raises `UnsupportedFormatError` when `splitter=None` was passed at registration (extractor-only entry)
- [ ] `registered_extensions() -> list[str]` returns a sorted list of all extensions that have at least an extractor registered (including extractor-only entries)
- [ ] Registry state is a module-level plain dict; no class instantiation required

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from format_adapters.registry import register_adapters, get_extractor, get_splitter, registered_extensions, UnsupportedFormatError

def fake_extractor(path): return 'text'
class FakeSplitter: pass
register_adapters('.pdf', fake_extractor, FakeSplitter)

assert get_extractor('.pdf') is fake_extractor
assert get_splitter('.pdf') is FakeSplitter
assert '.pdf' in registered_extensions()
assert registered_extensions() == sorted(registered_extensions())
print('registry pair ok')
"
Expected: "registry pair ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from format_adapters.registry import register_adapters, get_extractor, get_splitter, registered_extensions, UnsupportedFormatError

def fake_extractor(path): return 'text'
register_adapters('.epub', fake_extractor, None)

assert get_extractor('.epub') is fake_extractor
assert '.epub' in registered_extensions()
try:
    get_splitter('.epub')
    assert False, 'should have raised UnsupportedFormatError'
except UnsupportedFormatError:
    pass
print('extractor-only registration ok')
"
Expected: "extractor-only registration ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from format_adapters.registry import get_extractor, get_splitter, UnsupportedFormatError

try:
    get_extractor('.docx')
    assert False
except UnsupportedFormatError:
    pass

try:
    get_splitter('.docx')
    assert False
except UnsupportedFormatError:
    pass
print('unregistered extension raises ok')
"
Expected: "unregistered extension raises ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from format_adapters.registry import register_adapters, get_extractor
from pathlib import Path

def fake_extractor(path): return 'text'
register_adapters('.pdf', fake_extractor, None)

result = get_extractor(Path('/some/book.PDF'))
assert result is fake_extractor
print('case-insensitive Path lookup ok')
"
Expected: "case-insensitive Path lookup ok" (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/registry.py`

---

### Pass 1.2 — Create format_adapters package `__init__.py`

**What changes:** Creates `src/format_adapters/__init__.py` that re-exports the registry API so callers write `from format_adapters import get_extractor` without knowing the internal module layout. At the end of Phase 1 this file contains only re-exports; concrete adapter imports are added in Phase 2.

**Files:** `src/format_adapters/__init__.py`

**Done when:**
- [ ] `src/format_adapters/__init__.py` exists
- [ ] `from format_adapters import register_adapters` succeeds
- [ ] `from format_adapters import get_extractor` succeeds
- [ ] `from format_adapters import get_splitter` succeeds
- [ ] `from format_adapters import registered_extensions` succeeds
- [ ] `from format_adapters import UnsupportedFormatError` succeeds
- [ ] The file contains only re-exports from `format_adapters.registry` at this stage

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from format_adapters import register_adapters, get_extractor, get_splitter, registered_extensions, UnsupportedFormatError
print('package-level imports ok')
"
Expected: "package-level imports ok" (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/__init__.py`

---

### Pass 1.3 — Add registry unit tests

**What changes:** Adds `src/tests/test_registry.py` covering the full public API with isolated state per test.

**Files:** `src/tests/test_registry.py`

**Done when:**
- [ ] Each test resets registry state before running (clears the module-level dict or imports a fresh registry)
- [ ] Test: `register_adapters` stores an extractor/splitter pair retrievable via `get_extractor` and `get_splitter`
- [ ] Test: `register_adapters` with `splitter=None` registers extractor-only; `get_extractor` succeeds, `get_splitter` raises `UnsupportedFormatError`
- [ ] Test: `get_extractor` accepts a full `Path` and normalizes extension
- [ ] Test: `get_splitter` accepts a full `Path` and normalizes extension
- [ ] Test: `get_extractor` raises `UnsupportedFormatError` for unregistered extension
- [ ] Test: `get_splitter` raises `UnsupportedFormatError` for unregistered extension
- [ ] Test: `registered_extensions()` returns a sorted list
- [ ] Test: `registered_extensions()` includes extractor-only extensions
- [ ] Test: calling `register_adapters` twice overwrites the first entry
- [ ] Test: registering `.PDF` (uppercase) and looking up `.pdf` (lowercase) succeeds
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_registry.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_registry.py`

---

### Pass 1.4 — Rename protocol parameters

**What changes:** Replaces PDF-specific parameter names in the core engine protocols with format-agnostic names.

**Files:** `src/engines/protocols.py`

**Done when:**
- [ ] `ScriptEngine.generate` declares `source_path: Path` as its first positional parameter (was `pdf_path`)
- [ ] `SplitterEngine.split` declares `book_path: Path` as its first positional parameter (was `book_pdf`)
- [ ] No `pdf_path` or `book_pdf` parameter names remain in `src/engines/protocols.py`
- [ ] All other parameters, defaults, and return types are unchanged

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && python -c "
import engines.protocols as p, inspect
s = inspect.signature(p.ScriptEngine.generate)
assert 'source_path' in s.parameters and 'pdf_path' not in s.parameters
t = inspect.signature(p.SplitterEngine.split)
assert 'book_path' in t.parameters and 'book_pdf' not in t.parameters
print('protocols ok')
"
Expected: "protocols ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/engines/protocols.py`

---

### Pass 1.5 — Update engine implementers to match renamed protocols

**What changes:** Renames matching parameters in `LLMScriptEngine` and `PDFSplitterEngine` so they continue to satisfy the renamed protocols.

**Files:** `src/engines/llm_script.py`, `src/engines/pdf_splitter.py`

**Done when:**
- [ ] `LLMScriptEngine.generate` declares `source_path: Path`; all internal uses of the old parameter name updated
- [ ] `PDFSplitterEngine.split` declares `book_path: Path`; all internal uses of the old parameter name updated
- [ ] No `pdf_path` or `book_pdf` parameter names remain in the method signatures of these files
- [ ] Existing engine tests still pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && python -c "
import inspect
from engines.protocols import ScriptEngine, SplitterEngine
from engines.llm_script import LLMScriptEngine
from engines.pdf_splitter import PDFSplitterEngine
assert list(inspect.signature(LLMScriptEngine.generate).parameters) == list(inspect.signature(ScriptEngine.generate).parameters)
assert list(inspect.signature(PDFSplitterEngine.split).parameters) == list(inspect.signature(SplitterEngine.split).parameters)
print('implementers ok')
"
Expected: "implementers ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/engines/llm_script.py /home/mr/Desktop/python/harness_design/harnessv8/src/engines/pdf_splitter.py`

---

### Phase 1 — End-of-Phase Verification

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_registry.py src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

---

## Phase 2 — Source Format Adapters

**Goal:** Register the PDF adapter (wrapping existing code) and implement + register the EPUB extractor and splitter. At the end of this phase `import format_adapters` makes `get_extractor` and `get_splitter` work for both `.pdf` and `.epub`.

**Unlocks:** Phase 3 (engines can route through registry), Phase 4 (endpoints can be made format-agnostic), Phase 5 (consumers use registry).

---

### Pass 2.1 — Create PDF adapter registration module

**What changes:** Adds `src/format_adapters/pdf.py` that imports the existing PDF extractor and splitter and registers them for `.pdf`. The implementations stay in their original files.

**Files:** `src/format_adapters/pdf.py`

**Done when:**
- [ ] `src/format_adapters/pdf.py` exists
- [ ] Importing `format_adapters.pdf` calls `register_adapters(".pdf", extract_pdf, PDFSplitterEngine)`
- [ ] `extract_pdf` imported from `podcast_script_generator.llm.extract_pdf` (not moved)
- [ ] `PDFSplitterEngine` imported from `engines.pdf_splitter` (not moved)
- [ ] After importing `format_adapters.pdf`, `get_extractor(".pdf")` returns `extract_pdf`
- [ ] After importing `format_adapters.pdf`, `get_splitter(".pdf")` returns `PDFSplitterEngine`
- [ ] After importing `format_adapters.pdf`, `registered_extensions()` includes `".pdf"`
- [ ] `src/format_adapters/pdf.py` contains no implementation logic — only imports and a single `register_adapters` call

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import format_adapters.pdf
from format_adapters import get_extractor, get_splitter, registered_extensions
from podcast_script_generator.llm.extract_pdf import extract_pdf
from engines.pdf_splitter import PDFSplitterEngine
assert get_extractor('.pdf') is extract_pdf
assert get_splitter('.pdf') is PDFSplitterEngine
assert '.pdf' in registered_extensions()
print('pdf adapter registered ok')
"
Expected: "pdf adapter registered ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from pathlib import Path
import format_adapters.pdf
from format_adapters import get_extractor
from podcast_script_generator.llm.extract_pdf import extract_pdf
result = get_extractor(Path('book.Pdf'))
assert result is extract_pdf
print('case-insensitive Path lookup ok')
"
Expected: "case-insensitive Path lookup ok" (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/pdf.py`

---

### Pass 2.2 — Wire PDF adapter into `__init__.py`

**What changes:** `src/format_adapters/__init__.py` imports `format_adapters.pdf` so a bare `import format_adapters` registers the PDF adapter pair automatically.

**Files:** `src/format_adapters/__init__.py`

**Done when:**
- [ ] `import format_adapters` (with no explicit `import format_adapters.pdf`) causes `get_extractor(".pdf")` and `get_splitter(".pdf")` to succeed
- [ ] `get_extractor(".pdf")` returns `extract_pdf` after a bare `import format_adapters`
- [ ] `get_splitter(".pdf")` returns `PDFSplitterEngine` after a bare `import format_adapters`
- [ ] `registered_extensions()` includes `".pdf"` after a bare `import format_adapters`
- [ ] Registry API re-exports (`register_adapters`, `get_extractor`, `get_splitter`, `registered_extensions`, `UnsupportedFormatError`) still work

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import format_adapters
from format_adapters import get_extractor, get_splitter, registered_extensions
from podcast_script_generator.llm.extract_pdf import extract_pdf
from engines.pdf_splitter import PDFSplitterEngine
assert get_extractor('.pdf') is extract_pdf
assert get_splitter('.pdf') is PDFSplitterEngine
assert '.pdf' in registered_extensions()
print('package-level pdf registration ok')
"
Expected: "package-level pdf registration ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/__init__.py`

---

### Pass 2.3 — Add PDF adapter registration tests

**What changes:** Adds `src/tests/test_pdf_adapter.py` covering PDF adapter registration and backward-compatibility invariants.

**Files:** `src/tests/test_pdf_adapter.py`

**Done when:**
- [ ] Test: `get_extractor(".pdf")` returns `extract_pdf` after `import format_adapters.pdf`
- [ ] Test: `get_splitter(".pdf")` returns `PDFSplitterEngine` after `import format_adapters.pdf`
- [ ] Test: `registered_extensions()` includes `".pdf"`
- [ ] Test: `get_extractor(Path("some/book.PDF"))` returns `extract_pdf` (case-insensitive full-path lookup)
- [ ] Test: `get_splitter(Path("some/book.PDF"))` returns `PDFSplitterEngine`
- [ ] Test: `extract_pdf` importable from `podcast_script_generator.llm.extract_pdf` (not relocated)
- [ ] Test: `PDFSplitterEngine` importable from `engines.pdf_splitter` (not relocated)
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_pdf_adapter.py -v
Expected: All tests pass (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_registry.py src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_pdf_adapter.py`

---

### Pass 2.4 — Confirm existing PDF workflow tests still pass

**What changes:** No code changes. Regression check after wiring the PDF adapter.

**Files:** `src/tests/test_cli_podcast.py`, `src/tests/test_seed_gen_smoke.py`, `src/tests/test_slicer_smoke.py`, `src/tests/test_engines.py`

**Done when:**
- [ ] `test_cli_podcast.py` passes
- [ ] `test_seed_gen_smoke.py` passes
- [ ] `test_slicer_smoke.py` passes
- [ ] `test_engines.py` passes

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_cli_podcast.py src/tests/test_seed_gen_smoke.py src/tests/test_slicer_smoke.py src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** N/A — no files modified.

---

### Pass 2.5 — Add `ebooklib` dependency

**What changes:** Adds `ebooklib` to the project dependency manifest.

**Files:** `src/pyproject.toml`

**Done when:**
- [ ] `ebooklib` appears in the dependency list of `src/pyproject.toml`
- [ ] `pip show ebooklib` returns version information without error
- [ ] No existing dependency is removed or pinned to an incompatible version

**Proof tests:**
```
python -c "import ebooklib; print('ebooklib available:', ebooklib.__version__)"
Expected: "ebooklib available: <version string>" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/pyproject.toml`

---

### Pass 2.6 — Implement `extract_epub`

**What changes:** Creates `src/format_adapters/epub.py` with the `extract_epub` function that reads an EPUB and returns its full text as a plain string.

**Files:** `src/format_adapters/epub.py`

**Done when:**
- [ ] `src/format_adapters/epub.py` exists
- [ ] `extract_epub(path: str | Path) -> str` is defined
- [ ] Opens the EPUB using `ebooklib.epub.read_epub`
- [ ] Spine items iterated in spine order
- [ ] HTML markup stripped; result is plain text
- [ ] Consecutive blank lines collapsed to at most one; leading/trailing whitespace per paragraph removed
- [ ] Returns a single string of all spine items concatenated
- [ ] Raises `FileNotFoundError` if path does not exist
- [ ] Returns a non-empty string for a valid `.epub` file

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import inspect
from format_adapters.epub import extract_epub
sig = inspect.signature(extract_epub)
assert 'path' in sig.parameters
print('extract_epub signature ok')
"
Expected: "extract_epub signature ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from pathlib import Path
from format_adapters.epub import extract_epub
try:
    extract_epub(Path('/tmp/does_not_exist.epub'))
    assert False
except FileNotFoundError:
    pass
print('missing file raises ok')
"
Expected: "missing file raises ok" (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/epub.py`

---

### Pass 2.7 — Register the EPUB extractor (extractor-only)

**What changes:** `src/format_adapters/epub.py` calls `register_adapters(".epub", extract_epub, splitter=None)` at module level. At this point `get_splitter(".epub")` intentionally raises `UnsupportedFormatError`; that is by design until Pass 2.10 overwrites the entry.

**Files:** `src/format_adapters/epub.py`

**Done when:**
- [ ] `epub.py` calls `register_adapters(".epub", extract_epub, splitter=None)` at module level
- [ ] After `import format_adapters.epub`, `get_extractor(".epub")` returns `extract_epub`
- [ ] After `import format_adapters.epub`, `".epub"` appears in `registered_extensions()`
- [ ] `get_splitter(".epub")` raises `UnsupportedFormatError` at this stage (intentional)

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import format_adapters.epub
from format_adapters import get_extractor, registered_extensions
from format_adapters.epub import extract_epub
assert get_extractor('.epub') is extract_epub
assert '.epub' in registered_extensions()
print('epub extractor registration ok')
"
Expected: "epub extractor registration ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/epub.py`

---

### Pass 2.8 — Wire EPUB extractor into `__init__.py`

**What changes:** `src/format_adapters/__init__.py` imports `format_adapters.epub` so a bare `import format_adapters` registers the EPUB extractor alongside the PDF adapter pair.

**Files:** `src/format_adapters/__init__.py`

**Done when:**
- [ ] `import format_adapters` causes `get_extractor(".epub")` to succeed
- [ ] `get_extractor(".epub")` returns `extract_epub` after bare import
- [ ] `".epub"` appears in `registered_extensions()` after bare import
- [ ] `get_extractor(".pdf")` and `get_splitter(".pdf")` still return the PDF adapter pair (no regression from Pass 2.2)

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import format_adapters
from format_adapters import get_extractor, get_splitter, registered_extensions
from format_adapters.epub import extract_epub
from podcast_script_generator.llm.extract_pdf import extract_pdf
from engines.pdf_splitter import PDFSplitterEngine
assert get_extractor('.epub') is extract_epub
assert get_extractor('.pdf') is extract_pdf
assert get_splitter('.pdf') is PDFSplitterEngine
assert '.epub' in registered_extensions()
assert '.pdf' in registered_extensions()
print('package-level epub+pdf registration ok')
"
Expected: "package-level epub+pdf registration ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/__init__.py`

---

### Pass 2.9 — Add `extract_epub` unit tests

**What changes:** Adds `src/tests/test_epub_extractor.py` covering `extract_epub` behavior and the extractor-only registry state.

**Files:** `src/tests/test_epub_extractor.py`

**Done when:**
- [ ] Test: `extract_epub` raises `FileNotFoundError` for a non-existent path
- [ ] Test: `extract_epub` on a valid `.epub` fixture returns a non-empty string
- [ ] Test: returned string contains no raw HTML tags (`<html`, `<body`, `<p` do not appear)
- [ ] Test: `get_extractor(".epub")` returns `extract_epub` after `import format_adapters.epub`
- [ ] Test: `".epub"` appears in `registered_extensions()` after `import format_adapters.epub`
- [ ] Test: `get_splitter(".epub")` raises `UnsupportedFormatError` — confirms extractor-only registration; **do not replay this assertion after Pass 2.10**
- [ ] Test: `get_extractor(Path("book.EPUB"))` returns `extract_epub` (case-insensitive, full-path lookup)
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_epub_extractor.py -v
Expected: All tests pass (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_registry.py src/tests/test_pdf_adapter.py src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_epub_extractor.py`

---

### Pass 2.10 — Implement `EPUBSplitterEngine`

**What changes:** Creates `src/format_adapters/epub_splitter.py` with `EPUBSplitterEngine` that splits a whole EPUB into per-chapter `.txt` files.

**Files:** `src/format_adapters/epub_splitter.py`

**Done when:**
- [ ] `src/format_adapters/epub_splitter.py` exists
- [ ] `EPUBSplitterEngine` satisfies the `SplitterEngine` protocol from `src/engines/protocols.py`
- [ ] `split(self, book_path: Path, *, toc_page: int | None, output_dir: Path, no_ocr: bool) -> None`
- [ ] `toc_page` and `no_ocr` accepted and silently ignored (PDF-specific concepts)
- [ ] Chapter boundaries taken from EPUB TOC (NCX `navPoint` entries or EPUB3 `nav` document); if no TOC, each spine item is one chapter
- [ ] Chapter text extracted by stripping HTML from spine items belonging to each chapter
- [ ] Chapter files written to `output_dir` as `chapter_001.txt`, `chapter_002.txt`, … (zero-padded to three digits, one-based)
- [ ] `output_dir` created if it does not exist
- [ ] Raises `FileNotFoundError` for a non-existent `book_path`
- [ ] Writes at least one `.txt` file when called on a valid `.epub` file

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import inspect
from format_adapters.epub_splitter import EPUBSplitterEngine
sig = inspect.signature(EPUBSplitterEngine.split)
params = list(sig.parameters.keys())
assert 'book_path' in params
assert 'toc_page' in params
assert 'output_dir' in params
assert 'no_ocr' in params
print('EPUBSplitterEngine signature ok')
"
Expected: "EPUBSplitterEngine signature ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from pathlib import Path
from format_adapters.epub_splitter import EPUBSplitterEngine
engine = EPUBSplitterEngine()
try:
    engine.split(Path('/tmp/does_not_exist.epub'), toc_page=None, output_dir=Path('/tmp/epub_out'), no_ocr=False)
    assert False
except FileNotFoundError:
    pass
print('missing file raises ok')
"
Expected: "missing file raises ok" (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/epub_splitter.py`

---

### Pass 2.11 — Update EPUB adapter registration to include the splitter

**What changes:** `src/format_adapters/epub.py` updated to call `register_adapters(".epub", extract_epub, splitter=EPUBSplitterEngine)`, overwriting the extractor-only registration from Pass 2.7. After this, `get_splitter(".epub")` returns `EPUBSplitterEngine` instead of raising `UnsupportedFormatError`.

**Files:** `src/format_adapters/epub.py`

**Done when:**
- [ ] `epub.py` imports `EPUBSplitterEngine` from `format_adapters.epub_splitter`
- [ ] `epub.py` calls `register_adapters(".epub", extract_epub, splitter=EPUBSplitterEngine)`
- [ ] After `import format_adapters.epub`, `get_splitter(".epub")` returns `EPUBSplitterEngine`
- [ ] After `import format_adapters.epub`, `get_extractor(".epub")` still returns `extract_epub`
- [ ] `registered_extensions()` still includes `".epub"`

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import format_adapters.epub
from format_adapters import get_extractor, get_splitter, registered_extensions
from format_adapters.epub import extract_epub
from format_adapters.epub_splitter import EPUBSplitterEngine
assert get_extractor('.epub') is extract_epub
assert get_splitter('.epub') is EPUBSplitterEngine
assert '.epub' in registered_extensions()
print('epub full adapter registration ok')
"
Expected: "epub full adapter registration ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/epub.py`

---

### Pass 2.12 — Add `EPUBSplitterEngine` unit tests

**What changes:** Adds `src/tests/test_epub_splitter.py` covering `EPUBSplitterEngine` behavior and the updated full registration.

**Files:** `src/tests/test_epub_splitter.py`

**Done when:**
- [ ] Test: `EPUBSplitterEngine.split` raises `FileNotFoundError` for a non-existent path
- [ ] Test: `EPUBSplitterEngine.split` on a valid `.epub` fixture writes at least one `chapter_NNN.txt` file
- [ ] Test: output filenames match `chapter_NNN.txt` (zero-padded, one-based)
- [ ] Test: `toc_page` and `no_ocr` accepted without error
- [ ] Test: `get_splitter(".epub")` returns `EPUBSplitterEngine` after `import format_adapters.epub`
- [ ] Test: `get_extractor(".epub")` still returns `extract_epub` after `import format_adapters.epub`
- [ ] Test: `get_splitter(".epub")` does NOT raise `UnsupportedFormatError` (confirming the `splitter=None` entry was overwritten)
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_epub_splitter.py -v
Expected: All tests pass (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_epub_extractor.py src/tests/test_registry.py src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_epub_splitter.py`

---

### Phase 2 — End-of-Phase Verification

Both PDF and EPUB adapters fully registered; all four registry calls (`get_extractor`, `get_splitter` for both formats) work on a bare `import format_adapters`.

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import format_adapters
from format_adapters import get_extractor, get_splitter, registered_extensions
from format_adapters.epub import extract_epub
from format_adapters.epub_splitter import EPUBSplitterEngine
from podcast_script_generator.llm.extract_pdf import extract_pdf
from engines.pdf_splitter import PDFSplitterEngine
assert get_extractor('.epub') is extract_epub
assert get_splitter('.epub') is EPUBSplitterEngine
assert get_extractor('.pdf') is extract_pdf
assert get_splitter('.pdf') is PDFSplitterEngine
assert '.epub' in registered_extensions()
assert '.pdf' in registered_extensions()
print('package-level full registration ok')
"
Expected: "package-level full registration ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_registry.py src/tests/test_pdf_adapter.py src/tests/test_epub_extractor.py src/tests/test_epub_splitter.py src/tests/test_engines.py src/tests/test_cli_podcast.py src/tests/test_seed_gen_smoke.py src/tests/test_slicer_smoke.py -v
Expected: All tests pass (exit code 0)
```

---

## Phase 3 — Engine Layer

**Goal:** Route `LLMScriptEngine`, `seed_gen/cli.py`, and the splitter factory through the registry instead of calling PDF-specific functions directly.

**Unlocks:** Phase 4 (endpoints can invoke format-aware engines), Phase 5 (consumers already wired through seed_gen cli change here).

---

### Pass 3.1 — Update `LLMScriptEngine.generate` to use the registry

**What changes:** `src/engines/llm_script.py` resolves the extractor for `source_path` through `get_extractor` instead of calling `extract_pdf` directly.

**Files:** `src/engines/llm_script.py`

**Done when:**
- [ ] `LLMScriptEngine.generate` imports `get_extractor` from `format_adapters`
- [ ] `LLMScriptEngine.generate` calls `get_extractor(source_path)` to obtain the extractor
- [ ] `LLMScriptEngine.generate` calls the returned extractor with `source_path` to obtain input text
- [ ] `LLMScriptEngine.generate` no longer imports or calls `extract_pdf`
- [ ] `UnsupportedFormatError` propagates unchanged for unsupported extensions
- [ ] Existing engine tests still pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast
tree = ast.parse(open('engines/llm_script.py').read())
imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
assert any(n.module == 'format_adapters' and any(a.name == 'get_extractor' for a in n.names) for n in imports)
assert not any('extract_pdf' in [a.name for a in n.names] for n in imports)
print('engine uses registry')
"
Expected: "engine uses registry" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from unittest.mock import MagicMock, patch
from pathlib import Path
from engines.llm_script import LLMScriptEngine
engine = LLMScriptEngine(mode='chapter', llm=MagicMock())
with patch('engines.llm_script.get_extractor') as mock_get:
    mock_get.return_value = MagicMock(return_value='fake chapter text')
    engine.generate(Path('book.epub'), context=None, fiction_dir=None)
    mock_get.assert_called_once_with(Path('book.epub'))
    print('extractor lookup ok')
"
Expected: "extractor lookup ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/engines/llm_script.py`

---

### Pass 3.2 — Update `seed_gen` CLI to use the registry

**What changes:** `src/fiction/seed_gen/cli.py` replaces `extract_pdf(args.source_pdf)` with `get_extractor(args.source_pdf)(args.source_pdf)`.

**Files:** `src/fiction/seed_gen/cli.py`

**Done when:**
- [ ] `cli.py` imports `get_extractor` from `format_adapters`
- [ ] `cli.py` calls `get_extractor(args.source_pdf)(args.source_pdf)` for extraction
- [ ] `cli.py` no longer imports `extract_pdf`
- [ ] External CLI argument `source_pdf` unchanged
- [ ] Internal constants `PDF_CHAR_LIMIT` and `truncate_pdf_text` unchanged
- [ ] `call_api(pdf_text=book_text, ...)` keyword argument name `pdf_text` unchanged
- [ ] Existing seed_gen tests still pass with PDF inputs

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
source = pathlib.Path('fiction/seed_gen/cli.py').read_text()
tree = ast.parse(source)
imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
assert any(n.module == 'format_adapters' and any(a.name == 'get_extractor' for a in n.names) for n in imports)
assert not any('extract_pdf' in [a.name for a in n.names] for n in imports)
assert 'source_pdf' in source
assert 'PDF_CHAR_LIMIT' in source
assert 'truncate_pdf_text' in source
assert 'pdf_text=' in source
print('seed_gen uses registry and invariants ok')
"
Expected: "seed_gen uses registry and invariants ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/fiction/seed_gen/cli.py`

---

### Pass 3.3 — Add format-aware extractor regression tests

**What changes:** Adds `src/tests/test_format_aware_extractor.py` covering registry-based selection in the script engine and direct callers.

**Files:** `src/tests/test_format_aware_extractor.py`

**Done when:**
- [ ] Test: `LLMScriptEngine.generate` calls `get_extractor` with the provided `source_path`
- [ ] Test: `get_extractor('.pdf')` returns `extract_pdf`
- [ ] Test: `get_extractor('.epub')` returns `extract_epub`
- [ ] Test: `UnsupportedFormatError` raised when `LLMScriptEngine.generate` given an unregistered extension
- [ ] Test: seed_gen CLI path uses `get_extractor` (mock inspection or call chain)
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_format_aware_extractor.py -v
Expected: All tests pass (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_engines.py src/tests/test_seed_gen_smoke.py src/tests/test_cli_podcast.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_format_aware_extractor.py`

---

### Pass 3.4 — Update `default_splitter_engine` to use the registry

**What changes:** `src/engines/factory.py` calls `get_splitter(source)` to look up the splitter class; removes the hard-coded `PDFSplitterEngine` import.

**Files:** `src/engines/factory.py`

**Done when:**
- [ ] `default_splitter_engine` accepts a `source: str | Path` parameter
- [ ] `default_splitter_engine` calls `get_splitter(source)` from `format_adapters` to obtain the splitter class
- [ ] `default_splitter_engine` instantiates the returned class with `llm=client`
- [ ] `src/engines/factory.py` no longer contains `from engines.pdf_splitter import PDFSplitterEngine`
- [ ] `src/engines/pdf_splitter.py` is unchanged
- [ ] `UnsupportedFormatError` from `get_splitter` propagates to the caller
- [ ] `default_splitter_engine(Path("book.pdf"))` returns a `PDFSplitterEngine` instance
- [ ] `default_splitter_engine(Path("book.epub"))` returns an `EPUBSplitterEngine` instance

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
tree = ast.parse(pathlib.Path('engines/factory.py').read_text())
imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
assert not any('PDFSplitterEngine' in [a.name for a in n.names] for n in imports)
assert any(n.module == 'format_adapters' and any(a.name == 'get_splitter' for a in n.names) for n in imports)
print('factory imports ok')
"
Expected: "factory imports ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from pathlib import Path
from engines.factory import default_splitter_engine
from engines.pdf_splitter import PDFSplitterEngine
from format_adapters.epub_splitter import EPUBSplitterEngine
assert isinstance(default_splitter_engine(Path('book.pdf')), PDFSplitterEngine)
assert isinstance(default_splitter_engine(Path('book.epub')), EPUBSplitterEngine)
print('format-aware splitter selection ok')
"
Expected: "format-aware splitter selection ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/engines/factory.py`

---

### Pass 3.5 — Update all `default_splitter_engine` call sites

**What changes:** Every call site that invokes `default_splitter_engine()` with no argument is updated to pass the source book path.

**Files:** `src/endpoints/podcast.py`, `src/endpoints/slicer.py`

**Done when:**
- [ ] Every call to `default_splitter_engine()` in `podcast.py` passes the source book `Path` as `source`
- [ ] Every call to `default_splitter_engine()` in `slicer.py` passes the source book `Path` as `source`
- [ ] No bare no-argument `default_splitter_engine()` calls remain

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
for fname in ['endpoints/podcast.py', 'endpoints/slicer.py']:
    tree = ast.parse(pathlib.Path(fname).read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'default_splitter_engine']
    for call in calls:
        assert len(call.args) + len(call.keywords) >= 1, f'{fname}: default_splitter_engine called with no arguments'
print('all call sites pass source ok')
"
Expected: "all call sites pass source ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/endpoints/podcast.py /home/mr/Desktop/python/harness_design/harnessv8/src/endpoints/slicer.py`

---

### Pass 3.6 — Add format-aware splitter factory tests

**What changes:** Adds `src/tests/test_splitter_factory.py` covering PDF and EPUB selection, `UnsupportedFormatError` propagation, and case-insensitive extension handling.

**Files:** `src/tests/test_splitter_factory.py`

**Done when:**
- [ ] Test: `default_splitter_engine(Path("book.pdf"))` returns a `PDFSplitterEngine` instance
- [ ] Test: `default_splitter_engine(Path("book.epub"))` returns an `EPUBSplitterEngine` instance
- [ ] Test: `default_splitter_engine` raises `UnsupportedFormatError` for an unregistered extension
- [ ] Test: `default_splitter_engine(Path("book.PDF"))` returns a `PDFSplitterEngine` instance (case-insensitive)
- [ ] Existing `test_engines.py` still passes
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_splitter_factory.py -v
Expected: All tests pass (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_engines.py src/tests/test_slicer_smoke.py src/tests/test_cli_podcast.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_splitter_factory.py`

---

### Phase 3 — End-of-Phase Verification

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_engines.py src/tests/test_splitter_factory.py src/tests/test_format_aware_extractor.py src/tests/test_seed_gen_smoke.py src/tests/test_cli_podcast.py src/tests/test_slicer_smoke.py -v
Expected: All tests pass (exit code 0)
```

---

## Phase 4 — Podcast Pipeline Endpoints

**Goal:** Make `generate_chapter_podcast` and `generate_book_podcast` format-agnostic. Remove PDF-specific parameter names and hard-coded glob patterns from the endpoint layer. At the end of this phase, the whole-book podcast command works on EPUB inputs.

**Unlocks:** Phase 5 (consumers verified against fully wired endpoints).

---

### Pass 4.1 — Rename chapter endpoint parameter and fix error messages

**What changes:** Replaces PDF-specific naming in `generate_chapter_podcast` with format-agnostic names and messages.

**Files:** `src/endpoints/podcast.py`

**Done when:**
- [ ] `generate_chapter_podcast` declares `source_path: Path | None = None` as its first parameter (was `pdf_path`)
- [ ] `ValueError` for missing input references `source_path`
- [ ] `FileNotFoundError` for missing source file uses message `"Source file not found: ..."` (was `"PDF not found: ..."`)
- [ ] All internal uses of `pdf_path` inside `generate_chapter_podcast` renamed to `source_path`
- [ ] `script_engine.generate` called with `source_path`
- [ ] No `pdf_path` references remain inside `generate_chapter_podcast`

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import inspect
from endpoints.podcast import generate_chapter_podcast
sig = inspect.signature(generate_chapter_podcast)
assert 'source_path' in sig.parameters and 'pdf_path' not in sig.parameters
print('signature ok')
"
Expected: "signature ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast
tree = ast.parse(open('endpoints/podcast.py').read())
func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'generate_chapter_podcast')
names = {n.id for n in ast.walk(func) if isinstance(n, ast.Name)}
assert 'pdf_path' not in names
print('no pdf_path naming in endpoint')
"
Expected: "no pdf_path naming in endpoint" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from pathlib import Path
from endpoints.podcast import generate_chapter_podcast
from settings import PodcastSettings
root = Path('/tmp/f6_test_root')
root.mkdir(parents=True, exist_ok=True)
r = generate_chapter_podcast(source_path=Path('/tmp/does_not_exist.epub'), settings=PodcastSettings(root=root), skip_audio=True)
assert not r.ok
assert isinstance(r.error, FileNotFoundError)
assert 'Source file not found' in str(r.error)
print('error message ok')
"
Expected: "error message ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/endpoints/podcast.py`

---

### Pass 4.2 — Verify CLI compatibility with renamed parameter

**What changes:** No code changes. Confirms the CLI call site passes positionally (not by keyword `pdf_path=`) and that help text is unchanged.

**Files:** `src/cli/podcast.py` (read-only verification)

**Done when:**
- [ ] `generate_chapter_podcast` called positionally in `src/cli/podcast.py`
- [ ] No `pdf_path=` keyword argument in the call
- [ ] CLI help text still shows `pdf` as the positional argument and `--book` with metavar `PDF`

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast
tree = ast.parse(open('cli/podcast.py').read())
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'generate_chapter_podcast']
assert len(calls) == 1
assert not any(k.arg == 'pdf_path' for k in calls[0].keywords)
print('cli call compatible')
"
Expected: "cli call compatible" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python src/cli/podcast.py --help | grep -A1 "PDF file for single chapter"
Expected: output contains "PDF file for single chapter" (exit code 0)
```

**Rollback:** N/A — no files modified.

---

### Pass 4.3 — Add chapter endpoint regression tests

**What changes:** Adds `src/tests/test_endpoint_chapter_podcast.py` covering PDF, EPUB, and missing-source behavior.

**Files:** `src/tests/test_endpoint_chapter_podcast.py`

**Done when:**
- [ ] Test: PDF source with mocked script engine returns `PodcastResult` with a written script file
- [ ] Test: EPUB source with mocked script engine returns `PodcastResult` with a written script file
- [ ] Test: missing source returns `PodcastResult` whose error is `FileNotFoundError` with message `"Source file not found"`
- [ ] Test: mocked script engine receives the source `Path` unchanged
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_endpoint_chapter_podcast.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_endpoint_chapter_podcast.py`

---

### Pass 4.4 — Make `generate_book_podcast` format-agnostic

**What changes:** Renames `book_pdf` to `book_path` in `generate_book_podcast`; endpoint obtains splitter through `default_splitter_engine(book_path)`; removes direct `PDFSplitterEngine` reference from the endpoint; updates the single CLI call site.

**Files:** `src/endpoints/podcast.py`, `src/cli/podcast.py`

**Done when:**
- [ ] `generate_book_podcast` declares `book_path: Path` as its first parameter (was `book_pdf`)
- [ ] `generate_book_podcast` calls `default_splitter_engine(book_path)` and invokes `.split(book_path, ...)` on the returned splitter
- [ ] No `book_pdf` parameter name remains in `generate_book_podcast`
- [ ] No `PDFSplitterEngine` import or direct reference in `src/endpoints/podcast.py`
- [ ] `src/cli/podcast.py` calls `generate_book_podcast(book_path=book_path, ...)` (was `book_pdf=book_path`)
- [ ] `UnsupportedFormatError` propagates unchanged

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import inspect
from endpoints.podcast import generate_book_podcast
sig = inspect.signature(generate_book_podcast)
assert 'book_path' in sig.parameters and 'book_pdf' not in sig.parameters
print('signature ok')
"
Expected: "signature ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast
tree = ast.parse(open('endpoints/podcast.py').read())
imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
assert not any('PDFSplitterEngine' in [a.name for a in n.names] for n in imports)
func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'generate_book_podcast')
names = {n.id for n in ast.walk(func) if isinstance(n, ast.Name)}
assert 'book_pdf' not in names and 'PDFSplitterEngine' not in names
print('endpoint format-agnostic ok')
"
Expected: "endpoint format-agnostic ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast
tree = ast.parse(open('cli/podcast.py').read())
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'generate_book_podcast']
assert len(calls) == 1
assert any(k.arg == 'book_path' for k in calls[0].keywords)
print('cli call updated')
"
Expected: "cli call updated" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/endpoints/podcast.py /home/mr/Desktop/python/harness_design/harnessv8/src/cli/podcast.py`

---

### Pass 4.5 — Add whole-book endpoint regression tests

**What changes:** Adds `src/tests/test_endpoint_book_podcast.py` covering splitter selection and invocation through `generate_book_podcast`.

**Files:** `src/tests/test_endpoint_book_podcast.py`

**Done when:**
- [ ] Test: `.pdf` path calls `default_splitter_engine` with that path and invokes `PDFSplitterEngine.split`
- [ ] Test: `.epub` path calls `default_splitter_engine` with that path and invokes `EPUBSplitterEngine.split`
- [ ] Test: per-chapter output files written to configured output directory
- [ ] Test: `UnsupportedFormatError` propagates for unregistered extension
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_endpoint_book_podcast.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_endpoint_book_podcast.py`

---

### Pass 4.6 — Add `chapter_glob` to the `SplitterEngine` protocol and implementers

**What changes:** Adds the `chapter_glob` property to the `SplitterEngine` protocol; implements it on `PDFSplitterEngine` (returns `"*.pdf"`) and `EPUBSplitterEngine` (returns `"chapter_*.txt"`).

**Files:** `src/engines/protocols.py`, `src/engines/pdf_splitter.py`, `src/format_adapters/epub_splitter.py`

**Done when:**
- [ ] `SplitterEngine` protocol declares `chapter_glob: str`
- [ ] `PDFSplitterEngine.chapter_glob` returns `"*.pdf"`
- [ ] `EPUBSplitterEngine.chapter_glob` returns `"chapter_*.txt"`
- [ ] No if/elif on file extension appears inside `chapter_glob` in either class

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
from engines.pdf_splitter import PDFSplitterEngine
from format_adapters.epub_splitter import EPUBSplitterEngine
pdf_engine = PDFSplitterEngine.__new__(PDFSplitterEngine)
epub_engine = EPUBSplitterEngine.__new__(EPUBSplitterEngine)
assert pdf_engine.chapter_glob == '*.pdf'
assert epub_engine.chapter_glob == 'chapter_*.txt'
print('chapter_glob values ok')
"
Expected: "chapter_glob values ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/engines/protocols.py /home/mr/Desktop/python/harness_design/harnessv8/src/engines/pdf_splitter.py /home/mr/Desktop/python/harness_design/harnessv8/src/format_adapters/epub_splitter.py`

---

### Pass 4.7 — Replace hard-coded glob with `chapter_glob` in `generate_book_podcast`

**What changes:** Replaces `resolve_dir.glob("*.pdf")` with `resolve_dir.glob(splitter.chapter_glob)` so chapter discovery is driven by the adapter interface.

**Files:** `src/endpoints/podcast.py`

**Done when:**
- [ ] `generate_book_podcast` no longer contains the literal `"*.pdf"` as a glob argument
- [ ] `generate_book_podcast` calls `resolve_dir.glob(splitter.chapter_glob)` to enumerate chapter files
- [ ] The `splitter` instance used is the same one from `default_splitter_engine(book_path)` — no second registry call
- [ ] Sorted order of discovered files preserved
- [ ] No if/elif branching on file extension anywhere inside `generate_book_podcast`

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
source = pathlib.Path('endpoints/podcast.py').read_text()
tree = ast.parse(source)
func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'generate_book_podcast')
func_source = ast.unparse(func)
assert '*.pdf' not in func_source
assert 'chapter_glob' in func_source
print('glob replacement ok')
"
Expected: "glob replacement ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
source = pathlib.Path('endpoints/podcast.py').read_text()
tree = ast.parse(source)
func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'generate_book_podcast')
ext_literals = {'.pdf', '.epub', '.PDF', '.EPUB', '.txt'}
for node in ast.walk(func):
    if isinstance(node, ast.If):
        seg = ast.unparse(node.test)
        for ext in ext_literals:
            assert ext not in seg, f'extension branch on {ext!r} found: {seg!r}'
print('no extension branching in generate_book_podcast ok')
"
Expected: "no extension branching in generate_book_podcast ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/endpoints/podcast.py`

---

### Pass 4.8 — Add chapter discovery regression tests

**What changes:** Adds `src/tests/test_chapter_discovery.py` covering `chapter_glob`-driven discovery for both PDF and EPUB.

**Files:** `src/tests/test_chapter_discovery.py`

**Done when:**
- [ ] Test: `PDFSplitterEngine().chapter_glob == "*.pdf"`
- [ ] Test: `EPUBSplitterEngine().chapter_glob == "chapter_*.txt"`
- [ ] Test: `generate_book_podcast` with mocked `PDFSplitterEngine` discovers only `.pdf` files
- [ ] Test: `generate_book_podcast` with mocked `EPUBSplitterEngine` discovers only `chapter_*.txt` files
- [ ] Test: no extension string literal (`.pdf`, `.epub`) appears as argument to `.glob(...)` inside `generate_book_podcast` (AST-level check)
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_chapter_discovery.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_chapter_discovery.py`

---

### Phase 4 — End-of-Phase Verification

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_endpoint_chapter_podcast.py src/tests/test_endpoint_book_podcast.py src/tests/test_chapter_discovery.py src/tests/test_splitter_factory.py src/tests/test_cli_podcast.py src/tests/test_engines.py -v
Expected: All tests pass (exit code 0)
```

---

## Phase 5 — Consumer Pipelines and UI

**Goal:** Update `seed_gen` smoke tests, the standalone script generator (`main.py`), and the interactive menu (`menu.py`) to be format-agnostic. This is the final phase; at the end every pipeline entry point accepts EPUB inputs.

---

### Pass 5.1 — Update `seed_gen` smoke test mock targets

**What changes:** Any test in `test_seed_gen_smoke.py` that previously mocked `fiction.seed_gen.cli.extract_pdf` is updated to mock `fiction.seed_gen.cli.get_extractor` (the import changed in Pass 3.2).

**Files:** `src/tests/test_seed_gen_smoke.py`

**Done when:**
- [ ] No test patches `fiction.seed_gen.cli.extract_pdf`
- [ ] Any previously-mocking test now patches `fiction.seed_gen.cli.get_extractor` or `format_adapters.get_extractor`
- [ ] All tests in `test_seed_gen_smoke.py` pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
source = pathlib.Path('tests/test_seed_gen_smoke.py').read_text()
assert 'fiction.seed_gen.cli.extract_pdf' not in source
print('smoke test mock targets updated ok')
"
Expected: "smoke test mock targets updated ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_seed_gen_smoke.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_seed_gen_smoke.py`

---

### Pass 5.2 — Add targeted seed_gen format-agnostic tests

**What changes:** Adds `src/tests/test_seed_gen_format_agnostic.py` covering registry-based extractor selection, EPUB acceptance, PDF backward compatibility, and invariant checks.

**Files:** `src/tests/test_seed_gen_format_agnostic.py`

**Done when:**
- [ ] Test `test_seed_gen_uses_registry_for_epub`: mocked `get_extractor` returns callable producing `"fake epub text"`; `.epub` path invokes mock
- [ ] Test `test_seed_gen_uses_registry_for_pdf`: same for `.pdf` path
- [ ] Test `test_seed_gen_source_pdf_argument_unchanged`: `parser.add_argument("source_pdf", ...)` present in `cli.py` (AST check)
- [ ] Test `test_seed_gen_pdf_char_limit_unchanged`: `PDF_CHAR_LIMIT` defined in `cli.py`
- [ ] Test `test_seed_gen_unsupported_format_propagates`: `UnsupportedFormatError` propagates for unregistered extension
- [ ] Each test patches `fiction.seed_gen.cli.get_extractor`
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_seed_gen_format_agnostic.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_seed_gen_format_agnostic.py`

---

### Pass 5.3 — Route `main.py` through format adapter registry

**What changes:** `src/podcast_script_generator/llm/main.py` replaces the direct `extract_pdf` import and call with `get_extractor` from the registry.

**Files:** `src/podcast_script_generator/llm/main.py`

**Done when:**
- [ ] `from podcast_script_generator.llm.extract_pdf import extract_pdf` no longer in `main.py`
- [ ] `from format_adapters import get_extractor` in `main.py`
- [ ] `extract_pdf(pdf_path)` replaced with `get_extractor(pdf_path)(pdf_path)`
- [ ] All existing CLI arguments in `main.py` unchanged
- [ ] `python -c "import podcast_script_generator.llm.main"` succeeds

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && python -c "
import pathlib
src = pathlib.Path('src/podcast_script_generator/llm/main.py').read_text()
assert 'extract_pdf' not in src
assert 'from format_adapters import get_extractor' in src
assert 'get_extractor(' in src
print('F9.1 import check ok')
"
Expected: "F9.1 import check ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/podcast_script_generator/llm/main.py`

---

### Pass 5.4 — Update `main.py` test mock targets

**What changes:** Any test that patches `podcast_script_generator.llm.extract_pdf.extract_pdf` in tests for `main.py` is updated to patch `podcast_script_generator.llm.main.get_extractor`.

**Files:** `src/tests/test_podcast.py`

**Done when:**
- [ ] No test patches `podcast_script_generator.llm.extract_pdf.extract_pdf` in a test exercising `main.py`
- [ ] Replacement patch target is `podcast_script_generator.llm.main.get_extractor`
- [ ] All previously-passing tests still pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && python -c "
import pathlib, glob
test_files = glob.glob('src/tests/**/*.py', recursive=True)
hits = [f for f in test_files if 'llm.extract_pdf.extract_pdf' in pathlib.Path(f).read_text()]
assert not hits, f'Old mock target still present in: {hits}'
print('F9.2 mock target check ok')
"
Expected: "F9.2 mock target check ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_podcast.py src/tests/test_cli_podcast.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_podcast.py`

---

### Pass 5.5 — Replace PDF suffix check in `ask_pdf` with registry lookup

**What changes:** `menu.py` imports `registered_extensions` from `format_adapters` and replaces the fixed `.pdf` check with a registry-driven check; updates the rejection message.

**Files:** `menu.py`

**Done when:**
- [ ] `menu.py` contains `from format_adapters import registered_extensions`
- [ ] `p.suffix.lower() == ".pdf"` no longer appears inside `ask_pdf`
- [ ] `p.suffix.lower() in registered_extensions()` used inside `ask_pdf`
- [ ] Rejection message `"not a PDF file"` removed; format-agnostic message (e.g., `"not a supported source file"`) printed instead
- [ ] Function name `ask_pdf` unchanged
- [ ] No caller-side label strings changed
- [ ] `ask_pdf` accepts a `.pdf` path when `.pdf` in `registered_extensions()`
- [ ] `ask_pdf` accepts a `.epub` path when `.epub` in `registered_extensions()`
- [ ] `ask_pdf` rejects a `.txt` path when `.txt` not in `registered_extensions()`

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8/src && PYTHONPATH=. python -c "
import ast, pathlib
tree = ast.parse(pathlib.Path('../menu.py').read_text())
source = pathlib.Path('../menu.py').read_text()
assert 'registered_extensions' in source
assert 'not a PDF file' not in source
print('menu.py ask_pdf uses registry ok')
"
Expected: "menu.py ask_pdf uses registry ok" (exit code 0)
```

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -c "
from unittest.mock import patch
from pathlib import Path
import tempfile, os

with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
    epub_path = f.name
with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
    txt_path = f.name

try:
    import menu
    with patch('menu.registered_extensions', return_value=['.epub', '.pdf']):
        with patch('builtins.input', side_effect=[epub_path]):
            result = menu.ask_pdf('Source book')
            assert result == Path(epub_path).resolve()
        print('epub accepted ok')

        with patch('builtins.input', side_effect=[txt_path, txt_path, txt_path]):
            result = menu.ask_pdf('Source book')
            assert result is None
        print('txt rejected ok')
finally:
    os.unlink(epub_path)
    os.unlink(txt_path)
"
Expected: "epub accepted ok" followed by "txt rejected ok" (exit code 0)
```

**Rollback:** `git checkout -- /home/mr/Desktop/python/harness_design/harnessv8/menu.py`

---

### Pass 5.6 — Add menu format-agnostic tests

**What changes:** Adds `src/tests/test_menu_format_agnostic.py` covering `ask_pdf` acceptance and rejection behavior with a patched registry.

**Files:** `src/tests/test_menu_format_agnostic.py`

**Done when:**
- [ ] Test `test_ask_pdf_accepts_registered_epub`: `ask_pdf` returns resolved `Path` for an existing `.epub` file when `.epub` in `registered_extensions()`
- [ ] Test `test_ask_pdf_accepts_registered_pdf`: same for `.pdf`
- [ ] Test `test_ask_pdf_rejects_unregistered_extension`: `ask_pdf` returns `None` after three attempts when `.txt` not in `registered_extensions()`
- [ ] Each test patches `menu.registered_extensions`
- [ ] Each test uses `tempfile.NamedTemporaryFile` so `p.exists()` returns `True`
- [ ] All tests pass

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_menu_format_agnostic.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** `rm /home/mr/Desktop/python/harness_design/harnessv8/src/tests/test_menu_format_agnostic.py`

---

### Pass 5.7 — Final regression check

**What changes:** No code changes. Runs the complete test suite to confirm all five phases are coherent.

**Done when:**
- [ ] `test_cli_podcast.py` passes
- [ ] `test_seed_gen_smoke.py` passes
- [ ] `test_seed_gen_format_agnostic.py` passes
- [ ] `test_slicer_smoke.py` passes
- [ ] `test_engines.py` passes
- [ ] `test_format_aware_extractor.py` passes

**Proof tests:**
```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/test_seed_gen_smoke.py src/tests/test_seed_gen_format_agnostic.py src/tests/test_cli_podcast.py src/tests/test_engines.py src/tests/test_format_aware_extractor.py -v
Expected: All tests pass (exit code 0)
```

**Rollback:** N/A — no files modified.

---

### Phase 5 — End-of-Phase Verification (Full Suite)

```
cd /home/mr/Desktop/python/harness_design/harnessv8 && PYTHONPATH=src python -m pytest src/tests/ -v
Expected: All tests pass (exit code 0)
```

---

## Deferred (out of scope)

- DOCX, TXT, HTML, or any format beyond EPUB
- The fiction writing pipeline (novel generation)
- Changing any output formats
- Changing the LLM provider layer or audio engine
- Improving existing PDF handling (OCR quality, slicer improvements)
- Docker / containerization
- Renaming internal constants `PDF_CHAR_LIMIT`, `truncate_pdf_text`, `pdf_text` in seed_gen
