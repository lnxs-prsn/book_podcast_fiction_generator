# CLI / Endpoints / Engines Refactor — Fit Analysis & Spec

> Written: 2026-06-06. Based on source audit of `src/` submodule.
> This document does not prescribe implementation order — it identifies what must be decided before work begins.

---

## 1. The Proposed Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│  CLI Layer  │────▶│     Endpoints        │────▶│       Engines         │
│  (argparse) │     │ (typed inputs/outputs│     │ (PDF, LLM, TTS, etc.) │
│             │     │  no CLI side effects)│     │                       │
└─────────────┘     └─────────────────────┘     └──────────────────────┘
```

**Core claim**: endpoints are callable from tests, future APIs, or other programs without subprocess hacks.
**Corollary**: CLI becomes a translation layer only — no business logic, no side effects.

---

## 2. Fit Assessment by Pipeline

### 2A. Podcast Pipeline (`run_chapter.py`, `run_book.py`) — Good Fit

The podcast pipeline is the strongest candidate. The `llm/` submodules are already nearly side-effect-free functions (each file does one thing, exceptions propagate cleanly). The main problem is that `run_chapter.py` does three unrelated things inline:

1. argparse + validation
2. Speaker normalization (73-line regex block — belongs in a shared utility)
3. Orchestration calls to `run_local()`, `run_llm()`, `run_tts()`

Extracting an endpoint is straightforward: the orchestration logic becomes `generate_chapter_podcast()`, speaker normalization becomes a utility, and the CLI becomes ~30 lines.

**Config loading duplication is a blocker**: `run_chapter.py`, `run_book.py`, `tts/cli.py`, and `llm/call_api.py` each implement their own `_load_config()`. The endpoint layer needs a single shared config loader, or the duplication simply moves into each endpoint independently.

**Fit score: 8/10.** Most logic is already delegated; CLI extraction is clean.

---

### 2B. TTS Engine (`tts/cli.py`) — Partial Fit, One Complication

`tts/cli.py` already has a natural endpoint signature: `main(script_path, output_folder, api_key, speakers) → str`. The engine layer mostly works.

**The complication**: `send_to_api()` contains a polling loop with `time.sleep(5)`. This is inherently a side-effecting, long-running operation. It is **not pure** — it does I/O, network calls, and sleeps. The architecture label should be "no argparse or print() side effects," not "pure functions."

**Progress reporting gap**: the polling loop prints progress every 30 seconds. If `print()` is stripped from the engine, how does the user know TTS is running? A callback or structured logger is needed.

**Fit score: 6/10.** Already close structurally. Polling/progress pattern unaddressed.

---

### 2C. Novel Pipeline (`session.py`, `cli.py`) — Poor Fit As Written, Requires Design

This is where the proposal is most incomplete. `session.py` contains:

- `input()` calls for human approval gates (show draft → wait for user → approve/reject)
- `sys.exit(1)` inside business logic (KeyboardInterrupt handling)
- Print-heavy progress with no abstraction

The proposal shows:
```python
def run_novel_session(..., auto_approve: bool = False, ...) -> NovelSessionResult:
    """No CLI, no human prompts (returns/raises instead)."""
```

This works only for `auto_approve=True`. When `auto_approve=False`, the session *must* pause for human input mid-loop. A function that calls `input()` mid-execution is not testable without mocking stdin, and is not callable from a future API without a streaming/callback protocol.

**Three options exist (the proposal picks none):**

| Option | Description | Tradeoff |
|--------|-------------|----------|
| A. Approval callback | Endpoint accepts `approve_fn: Callable[[int, str], bool]` | Testable; CLI passes a lambda that calls `input()` |
| B. Generator/yield | Endpoint yields draft text; caller sends `True/False` back | Clean but uncommon pattern |
| C. Split endpoint | Endpoint writes draft and exits; separate endpoint promotes or rejects | Requires caller to manage state across calls |

None is wrong. But the spec must pick one before implementation begins. **Option A is recommended** — it is the most direct and keeps the endpoint as a single callable.

**Fit score: 3/10.** The approval gate is fundamentally incompatible with "no human prompts" unless one of these options is adopted.

---

### 2D. Seed Generator (`seed_gen/cli.py`) — Moderate Fit

`seed_gen/cli.py` has multiple `input()` calls for interactive user choices (genre, protagonist, concepts). The same approval-callback problem applies but in a simpler form — the interaction is at startup, not mid-loop.

The proposal's `generate_seed_project(source_pdf, output_dir) → Path` strips all interactivity, implying user selections are either pre-supplied as arguments or not supported. This is a real design choice:

- **Option A**: Add parameters for all user choices (genre index, protagonist name, concepts list) — removes interactivity, caller must supply everything upfront
- **Option B**: Keep `seed_gen` as CLI-only; it bootstraps one project, runs once, doesn't need programmatic calling

The endpoint form means Option A. This should be stated explicitly in the spec.

**Fit score: 5/10.** Workable, but interactivity disposition must be resolved.

---

### 2E. PDF Slicer (`slicer/pdf_splitter.py`) — Best Fit

`run_splitter(pdf_path, output_dir, toc_page, no_ocr, verbose)` already exists as a callable Python function. The slicer is already an engine. The proposal's `src/endpoints/slicer.py` would be a thin pass-through that documents and stabilizes the signature.

**Fit score: 9/10.** Almost nothing to do here.

---

## 3. What the Proposal Does Not Address

### 3.1 Interactive I/O Is Not "Eliminated" — It's Displaced

The proposal says endpoints have "no human prompts (returns/raises instead)." This is only achievable if all interactivity is injected via callbacks or pre-supplied parameters. The proposal does not show what replaces `input()` in `session.py`. This is the largest unresolved issue.

### 3.2 Progress Reporting Pattern

Long-running operations (TTS polling: 30s–10min; LLM calls: 10s–60s; novel session: multiple API round-trips) need to communicate progress. Stripping `print()` from engines means the CLI wrapper is silent unless something is added.

Options:
- **Structured logging** (Python `logging` module): engines log at DEBUG/INFO; CLI configures a handler — most standard, recommended
- **Progress callback**: `on_progress: Callable[[str], None] | None = None` — flexible, heavier API surface
- **Accept silent engines**: progress messages live at the CLI layer only

The proposal does not pick one.

### 3.3 Partial Failure in Batch Operations

`generate_book_podcast() -> list[PodcastResult]` — what happens when chapter 5 of 12 fails? Current `run_book.py` logs the error and continues. The endpoint must specify:
- Raise immediately (stops batch)?
- Return partial results with error markers?
- Accept an `on_error` callback?

A `PodcastResult` that can represent failure (`error: Exception | None`) is more useful than one that only represents success.

### 3.4 Config Loading Is Not Unified

The proposal restructures directories but does not consolidate the four independent `_load_config()` implementations across `run_chapter.py`, `run_book.py`, `tts/cli.py`, and `llm/call_api.py`. A `src/config.py` that all layers import is needed, or the duplication moves into each endpoint.

### 3.5 `run_simple.py` Has No Place in the New Structure

`run_simple.py` is ~300 lines of duplicated novel pipeline logic with no imports from `novel_pipeline`. The proposal's directory structure does not mention it. Must be explicitly:
- (a) Deleted — superseded by novel pipeline endpoint
- (b) Converted to a thin wrapper over the novel pipeline endpoint
- (c) Kept as-is and excluded from refactor scope

### 3.6 `src/` Is a Git Submodule

The proposed directory restructure (`src/endpoints/`, `src/cli/`, `src/engines/`) reorganizes the submodule. Any external consumers of the submodule see breaking path changes. This is a constraint that should be acknowledged — existing import paths break.

### 3.7 The `harness.py` Unified Entry Point Is Undefined

Listed as "optional, later." If it's out of scope, say so explicitly. If it's in scope, its interface needs to be specced before endpoint signatures are finalized — otherwise the endpoint layer may be designed in a way that makes unification harder later.

### 3.8 Exception Hierarchy for Podcast Pipeline

`novel_pipeline` has a well-defined exception hierarchy (`PipelineError` + 10 subclasses). The podcast pipeline uses `RuntimeError`, `ValueError`, and `sys.exit()` scattered across 5 files. The endpoint layer should define what exceptions `generate_chapter_podcast()` raises, or callers cannot handle failures programmatically.

---

## 4. Weaknesses in the Proposal

### 4.1 "Pure function" Is a Misnomer

TTS polling does network I/O and sleeps. LLM endpoints do HTTP with retry loops. These are not pure functions in any technical sense. The correct language is: **"no argparse, no print(), no sys.exit() — exceptions only."** Calling them pure creates confusion when engineers expect referential transparency.

### 4.2 `NovelSessionResult` Doesn't Handle Partial Sessions

```python
@dataclass
class NovelSessionResult:
    chapters_written: int
    final_chapter_number: int
    cost_usd: float
    state_path: Path
```

If a session is interrupted after 2 of 3 chapters, what does this return? The existing pipeline uses a state file for exactly this reason. The result type needs either a `completed: bool` field, or it only returns on clean exit and raises on interrupt.

### 4.3 The Approval Gate and `auto_approve` Are Not Symmetric

In tests you may want to simulate user *rejection* to test the retry loop. `auto_approve=True` always approves. Testing rejection requires either mocking stdin (hacky) or the callback pattern (clean). The boolean flag has no path to injecting a "reject on iteration N" test scenario.

### 4.4 Speaker Normalization Ownership Is Unresolved

The 73-line speaker label normalizer in `run_chapter.py` is neither CLI nor engine — it is a data transformation applied between LLM output and TTS input. In the new structure it belongs in a shared utility, but the three-layer diagram has no "utilities" box. Where it lives needs to be decided.

---

## 5. Spec Recommendations

### 5.1 Rename "Pure" to "Side-Effect-Free CLI"

Endpoint docstrings should read: **"No argparse. No print(). No sys.exit(). Raises exceptions on failure."**

### 5.2 Adopt Structured Logging, Not print()

```python
import logging
logger = logging.getLogger(__name__)
# engines use:
logger.info("TTS job submitted: %s", job_id)
# CLI layer sets up:
logging.basicConfig(level=logging.INFO)
```

All engines switch to `logger.*`. CLI layer configures the handler. This resolves the progress reporting gap without callbacks.

### 5.3 Adopt Approval Callback for Novel Session

```python
def run_novel_session(
    config_path: Path,
    resume: bool = False,
    auto_approve: bool = False,
    dry_run: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: Callable[[int, str], bool] = lambda n, text: True,
) -> NovelSessionResult:
    ...
```

CLI passes `lambda n, text: _prompt_user(text)`.
Tests pass `lambda n, text: n != 3` to simulate rejection on chapter 3.
`auto_approve=True` keeps the existing behavior as default.

### 5.4 Define a FailableResult Pattern for Batch

```python
@dataclass
class PodcastResult:
    chapter_pdf: Path
    script_path: Path | None
    audio_path: Path | None
    tts_job_id: str | None
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
```

Batch endpoint continues on failure, returns full list; CLI reports failures at the end.

### 5.5 Add a Shared `src/config.py`

Single function: `load_config(path: Path | None = None) -> dict`. All engines import this. Eliminates four independent implementations with different fallback behaviors.

### 5.6 Explicitly Scope `run_simple.py`

Decision required before implementation:
- [ ] Delete (superseded by novel_pipeline endpoint)
- [ ] Convert to thin wrapper over novel pipeline endpoint
- [ ] Exclude from refactor scope (keep as-is)

### 5.7 Define Podcast Pipeline Exception Hierarchy Before Coding Endpoints

Minimum needed:
```
PodcastError (base)
├── PDFExtractionError
├── ScriptGenerationError
├── TTSSubmissionError
└── TTSTimeoutError
```

### 5.8 Defer `harness.py` Explicitly

Mark out of scope for this refactor. Note as a future item. Do not let its hypothetical interface constrain endpoint signatures now.

---

## 6. Summary Table

| Pipeline | Fit | Primary Blocker |
|----------|-----|-----------------|
| PDF Slicer | 9/10 | None — already endpoint-shaped |
| Podcast (chapter/book) | 8/10 | Config loading duplication; speaker normalization ownership |
| TTS Engine | 6/10 | Progress reporting pattern unresolved |
| Seed Generator | 5/10 | Interactivity must be parameterized or excluded |
| Novel Pipeline (session) | 3/10 | Approval gate pattern fundamentally unresolved |

**Biggest unresolved issue**: interactive approval in `session.py`. Everything else is refactoring. This requires a design decision before any session.py work begins.

**Biggest quick win**: PDF slicer and podcast pipeline. These can be extracted cleanly with minimal risk and deliver immediate test coverage benefit.
