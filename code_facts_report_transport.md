> **CRITICAL CONTEXT for spec generation:**
> - `src/phases/`, `src/chapters/`, `src/docs/`, `src/unwanted_from_the_project_dir/` are NOT source code — ignore them.
> - `src/engines/protocols.py` already defines domain protocols (ScriptEngine, AudioEngine, SplitterEngine). The new `LLMTransport` and `LLMClient` protocols go in `src/llm/protocol.py`, not here.
> - There are TWO incompatible `call_api` functions (podcast domain vs. novel domain). They must both be deleted and replaced by DI calls to the new transport layer — they cannot be merged.
> - `novel_pipeline/api.py` contains retry/backoff/jitter logic that is transport-level, not domain-level, and must move to `src/llm/providers/openrouter.py`.

# Code Facts Report
Generated: 2026-06-18T13:39:26.119744
Project Root: harnessv5/
PYTHONPATH Convention: src/

---

## 1. Project Structure

| Path | Type | Has __init__.py | Notes |
|------|------|-----------------|-------|
| src/cli/ | package | yes | |
| src/cli/fiction.py | module | n/a | |
| src/cli/podcast.py | module | n/a | |
| src/config.py | module | n/a | |
| src/endpoints/ | package | yes | |
| src/endpoints/fiction.py | module | n/a | |
| src/endpoints/podcast.py | module | n/a | |
| src/engines/ | package | yes | |
| src/engines/factory.py | module | n/a | |
| src/engines/llm_script.py | module | n/a | |
| src/engines/pdf_splitter.py | module | n/a | |
| src/fiction/ | package | **MISSING** | |
| src/fiction/seed_gen/ | package | yes | |
| src/fiction/seed_gen/cli.py | module | n/a | |
| src/novel_pipeline/ | package | yes | |
| src/novel_pipeline/api.py | module | n/a | |
| src/novel_pipeline/cli.py | module | n/a | |
| src/novel_pipeline/config.py | module | n/a | |
| src/novel_pipeline/exceptions.py | module | n/a | |
| src/novel_pipeline/requests_.py | module | n/a | |
| src/novel_pipeline/session.py | module | n/a | |
| src/novel_pipeline/tests/ | package | **MISSING** | |
| src/novel_pipeline/tests/test_pipeline.py | module | n/a | |
| src/podcast_script_generator/ | package | yes | |
| src/podcast_script_generator/llm/ | package | yes | |
| src/podcast_script_generator/llm/__init__.py | module | n/a | |
| src/podcast_script_generator/llm/call_api.py | module | n/a | |
| src/podcast_script_generator/llm/exceptions.py | module | n/a | |
| src/podcast_script_generator/llm/extract_pdf.py | module | n/a | |
| src/podcast_script_generator/llm/main.py | module | n/a | |
| src/podcast_script_generator/llm/parse_args.py | module | n/a | |
| src/podcast_script_generator/llm/parse_output.py | module | n/a | |
| src/podcast_script_generator/llm/prompts/ | package | **MISSING** | |
| src/podcast_script_generator/llm/read_prompt.py | module | n/a | |
| src/podcast_script_generator/llm/save_output.py | module | n/a | |
| src/podcast_script_generator/llm/test_all.py | module | n/a | |
| src/slicer/ | package | yes | |
| src/slicer/pdf_splitter.py | module | n/a | |

## 2. Import Graph (Cross-Module)

| src/cli/fiction.py | sys | sys | 1 |
| src/cli/fiction.py | pathlib | Path | 2 |
| src/cli/fiction.py | logging | logging | 10 |
| src/cli/fiction.py | argparse | argparse | 14 |
| src/cli/fiction.py | novel_pipeline.prompt | prompt_user | 28 |
| src/cli/fiction.py | endpoints.fiction | run_novel_session | 29 |
| src/cli/podcast.py | sys | sys | 1 |
| src/cli/podcast.py | pathlib | Path | 2 |
| src/cli/podcast.py | logging | logging | 10 |
| src/cli/podcast.py | argparse | argparse | 17 |
| src/cli/podcast.py | settings | PodcastSettings | 69 |
| src/cli/podcast.py | engines.factory | default_llm_script_engine, default_audio_engine, default_splitter_engine | 77 |
| src/cli/podcast.py | endpoints.podcast | generate_book_podcast | 91 |
| src/cli/podcast.py | endpoints.podcast | generate_chapter_podcast | 120 |
| src/config.py | json | json | 1 |
| src/config.py | pathlib | Path | 2 |
| src/endpoints/fiction.py | pathlib | Path | 1 |
| src/endpoints/fiction.py | typing | Callable | 2 |
| src/endpoints/fiction.py | novel_pipeline.config | load_config | 4 |
| src/endpoints/fiction.py | novel_pipeline.session | run_session, ApproveChapterFn, SessionResult | 5 |
| src/endpoints/podcast.py | re | re | 1 |
| src/endpoints/podcast.py | pathlib | Path | 2 |
| src/endpoints/podcast.py | endpoints.podcast_types | PodcastResult | 4 |
| src/endpoints/podcast.py | engines.protocols | ScriptEngine, AudioEngine, SplitterEngine | 5 |
| src/endpoints/podcast.py | settings | PodcastSettings | 6 |
| src/endpoints/podcast.py | engines.factory | default_llm_script_engine | 44 |
| src/endpoints/podcast.py | engines.factory | default_audio_engine | 62 |
| src/endpoints/podcast.py | config | load_config | 92 |
| src/endpoints/podcast.py | engines.factory | default_splitter_engine | 98 |
| src/engines/factory.py | engines.llm_script | LLMScriptEngine | 1 |
| src/engines/factory.py | engines.wavespeed_audio | WaveSpeedAudioEngine | 2 |
| src/engines/factory.py | engines.pdf_splitter | PDFSplitterEngine | 3 |
| src/engines/factory.py | engines.protocols | ScriptEngine, AudioEngine, SplitterEngine | 4 |
| src/engines/llm_script.py | re | re | 1 |
| src/engines/llm_script.py | pathlib | Path | 2 |
| src/engines/llm_script.py | engines.protocols | ScriptEngine | 4 |
| src/engines/llm_script.py | podcast_script_generator.llm.extract_pdf | extract_pdf | 20 |
| src/engines/llm_script.py | podcast_script_generator.llm.read_prompt | read_prompt, resolve_prompt_path | 21 |
| src/engines/llm_script.py | podcast_script_generator.llm.call_api | call_api | 22 |
| src/engines/llm_script.py | util.normalize | normalize_speakers | 23 |
| src/engines/pdf_splitter.py | pathlib | Path | 1 |
| src/engines/pdf_splitter.py | engines.protocols | SplitterEngine | 3 |
| src/engines/pdf_splitter.py | slicer.pdf_splitter | run_splitter | 21 |
| src/fiction/seed_gen/cli.py | argparse | argparse | 1 |
| src/fiction/seed_gen/cli.py | re | re | 2 |
| src/fiction/seed_gen/cli.py | sys | sys | 3 |
| src/fiction/seed_gen/cli.py | pathlib | Path | 4 |
| src/fiction/seed_gen/cli.py | extract_pdf | extract_pdf | 9 |
| src/fiction/seed_gen/cli.py | call_api | call_api | 10 |
| src/fiction/seed_gen/cli.py | parse_output | parse_output | 11 |
| src/fiction/seed_gen/cli.py | save_output | save_output | 12 |
| src/novel_pipeline/api.py | __future__ | annotations | 14 |
| src/novel_pipeline/api.py | json | json | 16 |
| src/novel_pipeline/api.py | os | os | 17 |
| src/novel_pipeline/api.py | random | random | 18 |
| src/novel_pipeline/api.py | time | time | 19 |
| src/novel_pipeline/api.py | email.utils | parsedate_to_datetime | 20 |
| src/novel_pipeline/api.py | datetime | datetime, timezone | 21 |
| src/novel_pipeline/api.py | requests | requests | 25 |
| src/novel_pipeline/api.py | exceptions | ConfigError | 27 |
| src/novel_pipeline/api.py | cost | current_totals, estimate_cost, track_spend | 33 |
| src/novel_pipeline/api.py | exceptions | APIResponseError, ChapterValidationError, ConfigError, ContextOverflowError, CostLimitError | 34 |
| src/novel_pipeline/api.py | logging_ | log_event | 41 |
| src/novel_pipeline/api.py | tokens | count_tokens | 42 |
| src/novel_pipeline/api.py | config | DEFAULT_STATIC_DOC_ORDER | 281 |
| src/novel_pipeline/cli.py | __future__ | annotations | 10 |
| src/novel_pipeline/cli.py | argparse | argparse | 12 |
| src/novel_pipeline/cli.py | sys | sys | 13 |
| src/novel_pipeline/cli.py | traceback | traceback | 14 |
| src/novel_pipeline/cli.py | config | load_config | 16 |
| src/novel_pipeline/cli.py | exceptions | APIResponseError, ConfigError, ContextOverflowError, CostLimitError, DocumentLoadError, PromotionCollisionError, RejectionLimitReachedError, ResumeStateError | 17 |
| src/novel_pipeline/cli.py | logging_ | configure | 27 |
| src/novel_pipeline/cli.py | logging_ | log_event | 28 |
| src/novel_pipeline/cli.py | session | run_session, ApproveChapterFn | 29 |
| src/novel_pipeline/cli.py | prompt | prompt_user | 30 |
| src/novel_pipeline/config.py | __future__ | annotations | 17 |
| src/novel_pipeline/config.py | os | os | 19 |
| src/novel_pipeline/config.py | sys | sys | 20 |
| src/novel_pipeline/config.py | pathlib | Path | 21 |
| src/novel_pipeline/config.py | exceptions | ConfigError | 23 |
| src/novel_pipeline/config.py | logging_ | log_event | 24 |
| src/novel_pipeline/config.py | tomllib | tomllib | 30 |
| src/novel_pipeline/config.py | tomli | tomli | 33 |
| src/novel_pipeline/requests_.py | __future__ | annotations | 3 |
| src/novel_pipeline/requests_.py | api | call_api | 5 |
| src/novel_pipeline/requests_.py | docs | build_living_doc_diff, validate_living_doc_structure | 6 |
| src/novel_pipeline/requests_.py | exceptions | ChapterValidationError, LivingDocValidationError | 7 |
| src/novel_pipeline/requests_.py | logging_ | log_event | 8 |
| src/novel_pipeline/requests_.py | prompts | build_prompt | 9 |
| src/novel_pipeline/session.py | __future__ | annotations | 20 |
| src/novel_pipeline/session.py | logging | logging | 22 |
| src/novel_pipeline/session.py | sys | sys | 23 |
| src/novel_pipeline/session.py | dataclasses | dataclass | 24 |
| src/novel_pipeline/session.py | pathlib | Path | 25 |
| src/novel_pipeline/session.py | typing | Callable | 26 |
| src/novel_pipeline/session.py | cost | current_totals, estimate_cost | 42 |
| src/novel_pipeline/session.py | docs | find_unpromoted_drafts, load_living_doc, load_static_docs, promote_chapter, save_chapter_draft, save_living_doc | 43 |
| src/novel_pipeline/session.py | exceptions | APIResponseError, ChapterValidationError, ConfigError, ContextOverflowError, CostLimitError, LivingDocValidationError, PromotionCollisionError, RejectionLimitReachedError | 51 |
| src/novel_pipeline/session.py | logging_ | log_event | 61 |
| src/novel_pipeline/session.py | prompts | build_prompt | 62 |
| src/novel_pipeline/session.py | requests_ | request_chapter, request_living_doc_update | 63 |
| src/novel_pipeline/session.py | state | compute_gaps, detect_resume_state, find_next_chapter_number, list_canonical_chapters, read_state, write_state | 64 |
| src/novel_pipeline/session.py | tokens | count_tokens | 72 |
| src/novel_pipeline/tests/test_pipeline.py | __future__ | annotations | 29 |
| src/novel_pipeline/tests/test_pipeline.py | json | json | 31 |
| src/novel_pipeline/tests/test_pipeline.py | os | os | 32 |
| src/novel_pipeline/tests/test_pipeline.py | re | re | 33 |
| src/novel_pipeline/tests/test_pipeline.py | sys | sys | 34 |
| src/novel_pipeline/tests/test_pipeline.py | pathlib | Path | 35 |
| src/novel_pipeline/tests/test_pipeline.py | unittest.mock | MagicMock, patch | 36 |
| src/novel_pipeline/tests/test_pipeline.py | pytest | pytest | 38 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline | cost | 43 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline | APIResponseError, ChapterValidationError, ConfigError, ContextOverflowError, CostLimitError, DocumentLoadError, LivingDocValidationError, PromotionCollisionError, RejectionLimitReachedError, ResumeStateError | 44 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.api | call_api | 56 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.config | DEFAULTS, load_config | 57 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.cost | estimate_cost, reset_session_spend, track_spend | 58 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.docs | find_unpromoted_drafts, load_living_doc, load_static_docs, promote_chapter, save_chapter_draft, save_living_doc, validate_living_doc_structure | 59 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.prompts | build_prompt | 68 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.requests_ | request_chapter, request_living_doc_update | 69 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.state | compute_gaps, detect_resume_state, find_next_chapter_number, list_canonical_chapters, read_state, write_state | 70 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.tokens | count_tokens | 78 |
| src/novel_pipeline/tests/test_pipeline.py | time | time | 278 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.session | run_session | 1221 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.session | run_session | 1237 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.session | run_session | 1247 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline | session | 1263 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.exceptions | LivingDocValidationError | 1264 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline | session | 1294 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.session | _prompt_choice | 1310 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.session | _prompt_choice | 1323 |
| src/novel_pipeline/tests/test_pipeline.py | novel_pipeline.session | _build_dry_run_chapter | 1339 |
| src/podcast_script_generator/llm/call_api.py | json | json | 3 |
| src/podcast_script_generator/llm/call_api.py | logging | logging | 4 |
| src/podcast_script_generator/llm/call_api.py | os | os | 5 |
| src/podcast_script_generator/llm/call_api.py | time | time | 6 |
| src/podcast_script_generator/llm/call_api.py | urllib.error | urllib.error | 7 |
| src/podcast_script_generator/llm/call_api.py | urllib.request | urllib.request | 8 |
| src/podcast_script_generator/llm/call_api.py | config | load_config | 12 |
| src/podcast_script_generator/llm/extract_pdf.py | fitz | fitz | 3 |
| src/podcast_script_generator/llm/extract_pdf.py | io | io | 9 |
| src/podcast_script_generator/llm/extract_pdf.py | pytesseract | pytesseract | 10 |
| src/podcast_script_generator/llm/extract_pdf.py | PIL | Image | 11 |
| src/podcast_script_generator/llm/main.py | sys | sys | 10 |
| src/podcast_script_generator/llm/main.py | parse_args | parse_args | 12 |
| src/podcast_script_generator/llm/main.py | extract_pdf | extract_pdf | 13 |
| src/podcast_script_generator/llm/main.py | read_prompt | read_prompt | 14 |
| src/podcast_script_generator/llm/main.py | call_api | call_api | 15 |
| src/podcast_script_generator/llm/main.py | parse_output | parse_output | 16 |
| src/podcast_script_generator/llm/main.py | save_output | save_output | 17 |
| src/podcast_script_generator/llm/main.py | podcast_script_generator.llm.exceptions | PodcastError | 18 |
| src/podcast_script_generator/llm/parse_args.py | argparse | argparse | 3 |
| src/podcast_script_generator/llm/parse_args.py | os | os | 4 |
| src/podcast_script_generator/llm/parse_args.py | read_prompt | resolve_prompt_path, VALID_MODES | 6 |
| src/podcast_script_generator/llm/parse_output.py | re | re | 3 |
| src/podcast_script_generator/llm/read_prompt.py | pathlib | Path | 3 |
| src/podcast_script_generator/llm/save_output.py | logging | logging | 3 |
| src/podcast_script_generator/llm/save_output.py | os | os | 4 |
| src/podcast_script_generator/llm/test_all.py | os | os | 13 |
| src/podcast_script_generator/llm/test_all.py | subprocess | subprocess | 14 |
| src/podcast_script_generator/llm/test_all.py | sys | sys | 15 |
| src/podcast_script_generator/llm/test_all.py | tempfile | tempfile | 16 |
| src/podcast_script_generator/llm/test_all.py | textwrap | textwrap | 17 |
| src/podcast_script_generator/llm/test_all.py | unittest.mock | patch | 18 |
| src/podcast_script_generator/llm/test_all.py | fitz | fitz | 20 |
| src/podcast_script_generator/llm/test_all.py | parse_args | parse_args | 30 |
| src/podcast_script_generator/llm/test_all.py | extract_pdf | extract_pdf | 31 |
| src/podcast_script_generator/llm/test_all.py | read_prompt | read_prompt | 32 |
| src/podcast_script_generator/llm/test_all.py | parse_output | parse_output | 33 |
| src/podcast_script_generator/llm/test_all.py | save_output | save_output | 34 |
| src/slicer/pdf_splitter.py | argparse | argparse | 9 |
| src/slicer/pdf_splitter.py | fitz | fitz | 10 |
| src/slicer/pdf_splitter.py | pytesseract | pytesseract | 11 |
| src/slicer/pdf_splitter.py | pdf2image | convert_from_path | 12 |
| src/slicer/pdf_splitter.py | os | os | 13 |
| src/slicer/pdf_splitter.py | re | re | 14 |
| src/slicer/pdf_splitter.py | sys | sys | 15 |
| src/slicer/pdf_splitter.py | logging | logging | 16 |
| src/slicer/pdf_splitter.py | pathlib | Path | 17 |
| src/slicer/pdf_splitter.py | typing | List, Tuple, Optional, Dict, Any | 18 |
| src/slicer/pdf_splitter.py | sys | sys | 211 |
| src/slicer/pdf_splitter.py | pathlib | Path | 212 |
| src/slicer/pdf_splitter.py | call_api | call_api | 219 |
| src/slicer/pdf_splitter.py | io | io | 348 |
| src/slicer/pdf_splitter.py | PIL | Image | 350 |

## 3. Function Signatures (Transport & Domain Boundaries)

### src/cli/fiction.py::main
```python
def main()
    # Line: 13
    # Calls: logging.basicConfig, argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument
```

### src/cli/podcast.py::main
```python
def main()
    # Line: 16
    # Calls: logging.basicConfig, argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument
```

### src/config.py::load_config
```python
def load_config(path)
    # Line: 6
    # Calls: pathlib.Path, p.exists, json.loads, p.read_text
```

### src/endpoints/fiction.py::run_novel_session
```python
def run_novel_session(config_path: str | Path, resume: bool, auto_approve: bool, dry_run: bool, chapter_start: int | None, ignore_cost_limit: bool, approve_chapter: ApproveChapterFn | None)
    # Line: 8
    # Calls: novel_pipeline.config.load_config, str, novel_pipeline.session.run_session
```

### src/endpoints/podcast.py::generate_chapter_podcast
```python
def generate_chapter_podcast(pdf_path: Path | None, script_path: Path | None, script_engine: ScriptEngine | None, audio_engine: AudioEngine | None, settings: PodcastSettings | None, skip_audio: bool, mode: str, context: str | None, fiction_dir: Path | None)
    # Line: 12
    # Calls: settings.PodcastSettings, resolve, pathlib.Path, script_path.exists, endpoints.podcast_types.PodcastResult
```

### src/endpoints/podcast.py::generate_book_podcast
```python
def generate_book_podcast(book_pdf: Path | None, chapters_dir: Path | None, toc_page: int | None, script_engine: ScriptEngine | None, audio_engine: AudioEngine | None, splitter_engine: SplitterEngine | None, settings: PodcastSettings | None, no_ocr: bool, force: bool, skip_audio: bool, mode: str, context: str | None, slice_only: bool)
    # Line: 73
    # Calls: settings.PodcastSettings, get, config.load_config, resolve, pathlib.Path
```

### src/engines/factory.py::default_llm_script_engine
```python
def default_llm_script_engine(mode: str)
    # Line: 7
    # Calls: engines.llm_script.LLMScriptEngine
```

### src/engines/factory.py::default_audio_engine
```python
def default_audio_engine(speakers: dict | None)
    # Line: 11
    # Calls: engines.wavespeed_audio.WaveSpeedAudioEngine
```

### src/engines/factory.py::default_splitter_engine
```python
def default_splitter_engine()
    # Line: 15
    # Calls: engines.pdf_splitter.PDFSplitterEngine
```

### src/engines/llm_script.py::LLMScriptEngine.__init__
```python
def __init__(self, mode: str)
    # Line: 10
```

### src/engines/llm_script.py::LLMScriptEngine.generate
```python
def generate(self, pdf_path: Path, context: str | None, fiction_dir: Path | None)
    # Line: 13
    # Calls: podcast_script_generator.llm.extract_pdf.extract_pdf, str, self._resolve_fiction_content, podcast_script_generator.llm.read_prompt.read_prompt, podcast_script_generator.llm.read_prompt.resolve_prompt_path
```

### src/engines/llm_script.py::LLMScriptEngine._resolve_fiction_content
```python
def _resolve_fiction_content(self, pdf_path: Path, fiction_dir: Path | None)
    # Line: 34
    # Raises: ValueError, ValueError, ValueError, ValueError
    # Calls: ValueError, fiction_dir.is_dir, ValueError, re.match, ValueError
```

### src/engines/pdf_splitter.py::PDFSplitterEngine.split
```python
def split(self, book_pdf: Path, toc_page: int | None, output_dir: Path, no_ocr: bool)
    # Line: 13
    # Raises: RuntimeError
    # Calls: output_dir.mkdir, slicer.pdf_splitter.run_splitter, str, str, result.get
```

### src/fiction/seed_gen/cli.py::main
```python
def main()
    # Line: 260
    # Calls: parse_args, pathlib.Path, output_dir.mkdir, load_templates, truncate_pdf_text
```

### src/novel_pipeline/api.py::_resolve_api_key
```python
def _resolve_api_key(config: dict)
    # Line: 60
    # Raises: exceptions.ConfigError
    # Env vars: OPENROUTER_API_KEY
    # Calls: config.get, os.environ.get, exceptions.ConfigError
```

### src/novel_pipeline/api.py::_messages_to_text
```python
def _messages_to_text(messages: list[dict])
    # Line: 70
    # Docstring: Concatenate message contents for token counting (system + user)....
    # Calls: join, m.get
```

### src/novel_pipeline/api.py::_count_prompt_tokens
```python
def _count_prompt_tokens(messages: list[dict], model: str, config: dict)
    # Line: 75
    # Docstring: H3: token counting that accounts for chat-template overhead.

OpenAI's documented chat format adds ~...
    # Calls: int, config.get, int, config.get, m.get
```

### src/novel_pipeline/api.py::_per_document_tokens
```python
def _per_document_tokens(static_docs: dict[str, str] | None, living_doc: str | None, model: str, config: dict)
    # Line: 97
    # Docstring: Token counts per document for the overflow error message....
    # Calls: static_docs.items, tokens.count_tokens, tokens.count_tokens
```

### src/novel_pipeline/api.py::_format_overflow_message
```python
def _format_overflow_message(prompt_tokens: int, context_limit: int, safety_margin: int, doc_breakdown: dict[str, int], static_doc_order: list[str])
    # Line: 113
    # Calls: set, lines.append, seen.add, sorted, set
```

### src/novel_pipeline/api.py::_parse_retry_after
```python
def _parse_retry_after(value: str)
    # Line: 149
    # Docstring: Parse a Retry-After header value (seconds or HTTP date)....
    # Calls: value.strip, max, float, email.utils.parsedate_to_datetime, dt.replace
```

### src/novel_pipeline/api.py::_backoff_seconds
```python
def _backoff_seconds(config: dict, attempt: int)
    # Line: 170
    # Docstring: I5: return the configured backoff for this attempt (with bounds)....
    # Calls: config.get, float, min, len, float
```

### src/novel_pipeline/api.py::_jittered_sleep
```python
def _jittered_sleep(config: dict, base: float)
    # Line: 179
    # Docstring: L2: configurable jitter upper bound....
    # Calls: float, config.get, random.uniform
```

### src/novel_pipeline/api.py::_enforce_cost_limits
```python
def _enforce_cost_limits(estimated: float, config: dict, ignore_limit: bool)
    # Line: 187
    # Raises: exceptions.CostLimitError, exceptions.CostLimitError
    # Calls: cost.current_totals, float, config.get, float, config.get
```

### src/novel_pipeline/api.py::_build_payload
```python
def _build_payload(messages: list[dict], model: str, config: dict, max_tokens: int)
    # Line: 219
    # Docstring: C1 + L1: build the JSON payload with creativity controls and
max_tokens. Optional fields are only in...
    # Calls: int, config.get, float, config.get, float
```

### src/novel_pipeline/api.py::call_api
```python
def call_api(messages: list[dict], model: str, config: dict, expected_output_tokens: int | None, ignore_cost_limit: bool, static_docs: dict[str, str] | None, living_doc: str | None, task_label: str)
    # Line: 248
    # Docstring: Call OpenRouter chat-completions and return the assistant text.

Pre-flight:
  1. Token count vs con...
    # Raises: exceptions.APIResponseError, exceptions.ContextOverflowError, exceptions.APIResponseError, exceptions.APIResponseError, exceptions.ChapterValidationError, exceptions.APIResponseError, exceptions.APIResponseError, exceptions.APIResponseError, exceptions.APIResponseError
    # HTTP: Yes — requests/httpx call inside
    # Env vars: OPENROUTER_URL
    # Calls: _resolve_api_key, float, config.get, int, config.get
```

### src/novel_pipeline/cli.py::_build_parser
```python
def _build_parser()
    # Line: 33
    # Calls: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_argument
```

### src/novel_pipeline/cli.py::main
```python
def main(argv: list[str] | None)
    # Line: 76
    # Calls: parse_args, _build_parser, config.load_config, print, print
```

### src/novel_pipeline/config.py::load_config
```python
def load_config(path: str)
    # Line: 304
    # Docstring: Read TOML config, apply defaults, validate required keys, apply env
overrides. Unknown keys are logg...
    # Raises: FileNotFoundError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError
    # Env vars: OPENROUTER_API_KEY, OPENROUTER_MODEL
    # Calls: pathlib.Path, p.exists, FileNotFoundError, p.resolve, p.open
```

### src/novel_pipeline/exceptions.py::LivingDocValidationError.__init__
```python
def __init__(self, message: str, missing: list[str] | None, diff: str | None)
    # Line: 32
    # Calls: __init__, super
```

### src/novel_pipeline/requests_.py::_word_count
```python
def _word_count(text: str)
    # Line: 29
    # Calls: len, text.split
```

### src/novel_pipeline/requests_.py::request_chapter
```python
def request_chapter(static_docs: dict[str, str], living_doc: str, model: str, config: dict, ignore_cost_limit: bool)
    # Line: 33
    # Docstring: Ask the model for the next chapter.

Validates that the response has >= min_chapter_words words....
    # Raises: exceptions.ChapterValidationError
    # Calls: prompts.build_prompt, api.call_api, int, config.get, int
```

### src/novel_pipeline/requests_.py::request_living_doc_update
```python
def request_living_doc_update(static_docs: dict[str, str], old_living_doc: str, new_chapter: str, model: str, config: dict, ignore_cost_limit: bool)
    # Line: 83
    # Docstring: Ask the model to update the living doc after a chapter is approved.

Structural validation (all requ...
    # Raises: exceptions.LivingDocValidationError
    # Calls: prompts.build_prompt, api.call_api, int, config.get, list
```

### src/novel_pipeline/session.py::_prompt_yes_no
```python
def _prompt_yes_no(prompt: str, auto: bool, default_no: bool)
    # Line: 79
    # Docstring: Yes/no prompt. I15: EOF -> False ('no'). auto=True returns True....
    # Calls: lower, strip, input
```

### src/novel_pipeline/session.py::_abort_key
```python
def _abort_key(choices: dict[str, str])
    # Line: 93
    # Docstring: I15: pick the abort key for a choice dict.

Heuristic, in priority order:
  1. an entry with key 'a'...
    # Calls: choices.items, startswith, desc.lower, list, choices.keys
```

### src/novel_pipeline/session.py::_prompt_choice
```python
def _prompt_choice(prompt: str, choices: dict[str, str], auto: bool)
    # Line: 109
    # Docstring: Return the key the user picked. `choices` is {letter: description}.

I15: EOF -> abort entry if pres...
    # Calls: next, iter, print, choices.items, print
```

### src/novel_pipeline/session.py::_enforce_first_run_template
```python
def _enforce_first_run_template(config: dict, living_doc: str, output_dir: str)
    # Line: 134
    # Docstring: C2: refuse to start with an empty living doc on a true first run.

"True first run" means: no canoni...
    # Raises: exceptions.ConfigError
    # Calls: bool, state.list_canonical_chapters, pathlib.Path, living_doc.strip, join
```

### src/novel_pipeline/session.py::_resolve_starting_chapter
```python
def _resolve_starting_chapter(config: dict, chapter_start: int | None, resume: bool, auto_approve: bool, static_docs: dict[str, str], living_doc_ref: list)
    # Line: 166
    # Docstring: Decide which chapter number to begin writing.

Returns (chapter_number, should_continue). If should_...
    # Raises: exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError
    # Calls: state.find_next_chapter_number, state.compute_gaps, state.list_canonical_chapters, set, range
```

### src/novel_pipeline/session.py::_maybe_surface_unpromoted_draft
```python
def _maybe_surface_unpromoted_draft(config: dict, chapter_num: int, auto_approve: bool)
    # Line: 337
    # Docstring: H7: on resume, if there are unpromoted drafts for the next chapter,
inform the user. Non-blocking — ...
    # Calls: docs.find_unpromoted_drafts, logging_.log_event, str, print, len
```

### src/novel_pipeline/session.py::_estimate_chapter_prompt_tokens
```python
def _estimate_chapter_prompt_tokens(static_docs: dict[str, str], living_doc: str, model: str, config: dict)
    # Line: 368
    # Docstring: Build a generate_chapter prompt and count its tokens. Used in the
summary and in the per-iteration r...
    # Calls: prompts.build_prompt, int, config.get, int, config.get
```

### src/novel_pipeline/session.py::_print_pre_session_summary
```python
def _print_pre_session_summary(config: dict, static_docs: dict[str, str], living_doc: str)
    # Line: 396
    # Calls: sum, tokens.count_tokens, static_docs.values, tokens.count_tokens, _estimate_chapter_prompt_tokens
```

### src/novel_pipeline/session.py::_build_dry_run_chapter
```python
def _build_dry_run_chapter(chapter_num: int, config: dict)
    # Line: 443
    # Docstring: M5: produce a dry-run chapter sized realistically so that the next
iteration's cost estimate isn't w...
    # Calls: config.get, int, config.get, int, config.get
```

### src/novel_pipeline/session.py::run_session
```python
def run_session(config: dict, auto_approve: bool, dry_run: bool, resume: bool, chapter_start: int | None, ignore_cost_limit: bool, approve_chapter: ApproveChapterFn)
    # Line: 465
    # Docstring: Run one pipeline session: up to chapters_per_session chapters....
    # Raises: KeyboardInterrupt
    # Calls: pathlib.Path, output_dir.mkdir, mkdir, docs.load_static_docs, docs.load_living_doc
```

### src/novel_pipeline/session.py::_generate_chapter_text
```python
def _generate_chapter_text(chapter_num: int, static_docs: dict[str, str], living_doc: str, config: dict, model: str, dry_run: bool, ignore_cost_limit: bool)
    # Line: 620
    # Docstring: Step 1: generate (or dry-run) a chapter, with retry-on-failure UI.

Returns the chapter text, or Non...
    # Calls: _build_dry_run_chapter, requests_.request_chapter, print, type, _prompt_choice
```

### src/novel_pipeline/session.py::_run_one_chapter
```python
def _run_one_chapter(chapter_num: int, static_docs: dict[str, str], living_doc: str, config: dict, output_dir: str, state_file_path: str, living_doc_path: str, model: str, auto_approve: bool, approve_chapter: ApproveChapterFn, dry_run: bool, ignore_cost_limit: bool)
    # Line: 671
    # Docstring: Run one iteration of the loop.

Returns:
  (new_living_doc, True)  - chapter approved AND living doc...
    # Raises: exceptions.RejectionLimitReachedError, KeyboardInterrupt, KeyboardInterrupt
    # Calls: print, int, config.get, range, _generate_chapter_text
```

### src/podcast_script_generator/llm/call_api.py::_resolve_model
```python
def _resolve_model()
    # Line: 22
    # Docstring: Priority: OPENROUTER_MODEL env var > config.json > default....
    # Env vars: OPENROUTER_MODEL
    # Calls: os.environ.get, get, config.load_config
```

### src/podcast_script_generator/llm/call_api.py::_resolve_max_tokens
```python
def _resolve_max_tokens()
    # Line: 31
    # Docstring: Priority: OPENROUTER_MAX_TOKENS env var > config.json > default....
    # Env vars: OPENROUTER_MAX_TOKENS
    # Calls: os.environ.get, int, get, config.load_config, int
```

### src/podcast_script_generator/llm/call_api.py::_resolve_api_url
```python
def _resolve_api_url()
    # Line: 40
    # Docstring: Priority: OPENROUTER_URL env var > config.json api_url > default....
    # Env vars: OPENROUTER_URL
    # Calls: os.environ.get, get, config.load_config
```

### src/podcast_script_generator/llm/call_api.py::_resolve_retry_after
```python
def _resolve_retry_after()
    # Line: 49
    # Docstring: Priority: OPENROUTER_RETRY_AFTER env var > config.json > None.

Returns a fixed override in seconds,...
    # Env vars: OPENROUTER_RETRY_AFTER
    # Calls: os.environ.get, float, get, config.load_config, float
```

### src/podcast_script_generator/llm/call_api.py::call_api
```python
def call_api(pdf_text: str, prompt_text: str)
    # Line: 62
    # Docstring: Send prompt + PDF text to OpenRouter and return the response text.

Model resolution priority: OPENR...
    # Raises: RuntimeError, RuntimeError, RuntimeError
    # HTTP: Yes — requests/httpx call inside
    # Env vars: OPENROUTER_API_KEY
    # Calls: _resolve_api_url, _resolve_model, _resolve_max_tokens, encode, json.dumps
```

### src/podcast_script_generator/llm/extract_pdf.py::_ocr_page
```python
def _ocr_page(doc: fitz.Document, page_idx: int)
    # Line: 6
    # Docstring: OCR a single image-based page via pytesseract....
    # Calls: get_pixmap, fitz.Matrix, PIL.Image.open, io.BytesIO, pix.tobytes
```

### src/podcast_script_generator/llm/extract_pdf.py::extract_pdf
```python
def extract_pdf(pdf_path: str)
    # Line: 20
    # Docstring: Return all page text from pdf_path joined with double newlines.

Falls back to OCR (pytesseract) for...
    # Raises: ValueError, ValueError
    # Calls: fitz.open, ValueError, enumerate, strip, page.get_text
```

### src/podcast_script_generator/llm/main.py::main
```python
def main()
    # Line: 21
    # Calls: parse_args.parse_args, extract_pdf.extract_pdf, read_prompt.read_prompt, call_api.call_api, parse_output.parse_output
```

### src/podcast_script_generator/llm/parse_args.py::parse_args
```python
def parse_args()
    # Line: 9
    # Docstring: Parse CLI args: pdf_path, output_dir, --mode, --context / --context-file.

Returns (pdf_path, prompt...
    # Raises: FileNotFoundError, ValueError, FileNotFoundError
    # Calls: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, list
```

### src/podcast_script_generator/llm/parse_output.py::parse_output
```python
def parse_output(response_text: str)
    # Line: 10
    # Docstring: Parse the LLM response into a list of (filename, content) tuples.

Files are separated by `### FILE:...
    # Raises: ValueError, ValueError
    # Calls: list, _FILE_HEADER.finditer, response_text.strip, ValueError, enumerate
```

### src/podcast_script_generator/llm/read_prompt.py::resolve_prompt_path
```python
def resolve_prompt_path(mode: str)
    # Line: 9
    # Docstring: Return the absolute path to the prompt file for the given mode.

Raises ValueError for unknown modes...
    # Raises: ValueError, FileNotFoundError
    # Calls: ValueError, join, path.exists, FileNotFoundError, str
```

### src/podcast_script_generator/llm/read_prompt.py::read_prompt
```python
def read_prompt(prompt_path: str, context: str | None, fiction_content: str | None)
    # Line: 22
    # Docstring: Read the prompt file and return its contents with trailing whitespace stripped.

If context is provi...
    # Raises: ValueError, ValueError
    # Calls: open, f.read, ValueError, content.rstrip, ValueError
```

### src/podcast_script_generator/llm/save_output.py::save_output
```python
def save_output(files: list[tuple[str, str]], output_dir: str)
    # Line: 9
    # Docstring: Write each (filename, content) pair to output_dir as a UTF-8 file.

- Creates output_dir if it does ...
    # Raises: ValueError
    # Calls: os.makedirs, os.path.isabs, ValueError, os.path.join, open
```

### src/slicer/pdf_splitter.py::get_toc_from_llm
```python
def get_toc_from_llm(pdf_path: str)
    # Line: 209
    # Docstring: Stage 4: send OCR'd front matter + page samples to the LLM to identify structure....
    # Env vars: OPENROUTER_API_KEY
    # sys.path: Runtime path manipulation detected
    # Calls: str, pathlib.Path, sys.path.insert, logging.warning, os.environ.get
```

### src/slicer/pdf_splitter.py::extract_toc
```python
def extract_toc(pdf_path: str, toc_page_num: int, target_level: int, no_ocr: bool)
    # Line: 490
    # Docstring: Run the multi-stage TOC extraction pipeline. Returns (toc_list, source_name)....
    # Calls: get_toc_from_bookmarks, get_text_from_toc_page, parse_toc_from_text, get_ocr_text_from_toc_page, parse_toc_from_text
```

### src/slicer/pdf_splitter.py::run_splitter
```python
def run_splitter(input_path: str, toc_page: int, output_dir: str, prefix: str, level: int, no_ocr: bool, dry_run: bool, chapters_only: bool, verbose: bool, ocr_embed: bool)
    # Line: 650
    # Docstring: Orchestration-friendly entry point. Can be called directly from another Python script.

Returns a di...
    # Calls: setup_logging, os.path.exists, logging.error, logging.info, logging.info
```

## 4. Class Hierarchies

### LLMScriptEngine
- File: src/engines/llm_script.py
- Line: 7
- Bases: engines.protocols.ScriptEngine
  - __init__() — line 10
  - generate() — line 13
  - _resolve_fiction_content() — line 34

### PDFSplitterEngine
- File: src/engines/pdf_splitter.py
- Line: 6
- Bases: engines.protocols.SplitterEngine
  - split() — line 13

### PipelineError
- File: src/novel_pipeline/exceptions.py
- Line: 8
- Bases: Exception

### DocumentLoadError
- File: src/novel_pipeline/exceptions.py
- Line: 12
- Bases: PipelineError

### ConfigError
- File: src/novel_pipeline/exceptions.py
- Line: 16
- Bases: PipelineError

### APIResponseError
- File: src/novel_pipeline/exceptions.py
- Line: 20
- Bases: PipelineError

### ChapterValidationError
- File: src/novel_pipeline/exceptions.py
- Line: 24
- Bases: PipelineError

### LivingDocValidationError
- File: src/novel_pipeline/exceptions.py
- Line: 29
- Bases: PipelineError
  - __init__() — line 32

### ContextOverflowError
- File: src/novel_pipeline/exceptions.py
- Line: 38
- Bases: PipelineError

### CostLimitError
- File: src/novel_pipeline/exceptions.py
- Line: 42
- Bases: PipelineError

### ResumeStateError
- File: src/novel_pipeline/exceptions.py
- Line: 46
- Bases: PipelineError

### PromotionCollisionError
- File: src/novel_pipeline/exceptions.py
- Line: 51
- Bases: PipelineError

### RejectionLimitReachedError
- File: src/novel_pipeline/exceptions.py
- Line: 56
- Bases: PipelineError

### SessionResult
- File: src/novel_pipeline/session.py
- Line: 35
- Bases: object

### TestTokens
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 93
- Bases: object
  - test_count_tokens_empty() — line 94
  - test_count_tokens_nonempty() — line 97
  - test_count_tokens_unknown_model_falls_back() — line 101
  - test_count_tokens_with_config_fallback_encoding() — line 106

### TestLoadStaticDocs
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 117
- Bases: object
  - test_loads_md() — line 118
  - test_missing_file_raises() — line 124
  - test_empty_file_raises() — line 128
  - test_unsupported_extension_raises() — line 134
  - test_pdf_raises_with_hint() — line 140
  - test_collision_raises() — line 146
  - test_utf8_decode_failure_raises() — line 158

### TestLivingDoc
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 170
- Bases: object
  - test_load_missing_returns_empty() — line 171
  - test_save_then_load_roundtrip() — line 175
  - test_save_empty_raises() — line 180
  - test_save_creates_backup_of_existing() — line 184
  - test_save_keeps_all_backups_not_just_10() — line 192
  - test_save_uses_configured_backup_format() — line 201

### TestDraftAndPromote
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 215
- Bases: object
  - test_save_chapter_draft_goes_to_rejected() — line 216
  - test_save_empty_draft_raises() — line 223
  - test_save_chapter_draft_uses_configured_name_format() — line 227
  - test_promote_moves_to_canonical() — line 236
  - test_promote_collision_now_raises() — line 243
  - test_promote_missing_draft_raises() — line 257
  - test_promote_uses_configured_canonical_format() — line 261

### TestFindUnpromotedDrafts
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 269
- Bases: object
  - test_returns_empty_when_no_rejected_dir() — line 270
  - test_returns_matching_drafts_newest_first() — line 274
  - test_ignores_other_chapter_numbers() — line 287

### TestStructuralValidation
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 299
- Bases: object
  - test_all_present_in_order() — line 306
  - test_missing_section() — line 321
  - test_out_of_order() — line 327

### TestPrompts
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 345
- Bases: object
  - test_unknown_task_raises() — line 346
  - test_order_is_fixed() — line 350
  - test_system_prompt_per_task() — line 370
  - test_empty_living_doc_marked_first_chapter() — line 376
  - test_extra_static_docs_appended_alphabetised() — line 380
  - test_system_prompt_can_be_overridden_via_config() — line 387
  - test_wrap_format_can_be_overridden_via_config() — line 398
  - test_static_doc_order_overridable_via_config() — line 409

### TestFindNextChapter
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 423
- Bases: object
  - test_empty_dir_returns_1() — line 424
  - test_nonexistent_dir_returns_1() — line 427
  - test_no_gaps_returns_n_plus_1() — line 430
  - test_gap_mid_sequence_returned() — line 435
  - test_ignores_rejected() — line 440
  - test_ignores_timestamped_duplicates() — line 447
  - test_list_and_gaps() — line 452
  - test_custom_canonical_regex() — line 458

### TestStateFile
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 473
- Bases: object
  - test_read_missing_returns_none() — line 474
  - test_write_then_read_roundtrip() — line 477
  - test_write_with_last_chapter_drafted() — line 487
  - test_old_state_without_drafted_still_readable() — line 499
  - test_malformed_json_raises_resume_state_error() — line 516
  - test_missing_keys_raises() — line 522

### TestDetectResumeState
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 529
- Bases: object
  - test_consistent_state() — line 530
  - test_inconsistent_state() — line 548
  - test_chapters_present_but_no_state_file_raises() — line 564
  - test_gaps_reported() — line 572

### TestConfig
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 588
- Bases: object
  - test_missing_file_raises() — line 599
  - test_minimal_config_applies_defaults() — line 603
  - test_missing_required_raises() — line 621
  - test_env_overrides() — line 627
  - test_v2_default_sections_are_character_agnostic() — line 636
  - test_validation_context_limit_too_low() — line 644
  - test_validation_chapters_per_session_zero() — line 651
  - test_validation_price_zero_rejected() — line 658
  - test_validation_temperature_out_of_range() — line 673
  - test_validation_bad_doc_wrap_format() — line 680
  - test_validation_bad_rejected_draft_format() — line 687
  - test_validation_backoff_must_be_list() — line 694
  - test_temperature_passthrough() — line 701

### TestCost
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 715
- Bases: object
  - test_estimate_cost() — line 721
  - test_estimate_cost_fractional() — line 725
  - test_track_spend_persists() — line 728
  - test_lifetime_persists_across_session_reset() — line 745

### FakeResponse
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 761
- Bases: object
  - __init__() — line 762
  - json() — line 769

### TestCallAPI
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 802
- Bases: object
  - _good_payload() — line 803
  - test_happy_path() — line 809
  - test_payload_includes_max_tokens() — line 825
  - test_payload_includes_creativity_controls_when_set() — line 843
  - test_payload_omits_creativity_controls_when_unset() — line 865
  - test_finish_reason_length_raises() — line 884
  - test_finish_reason_content_filter_raises() — line 902
  - test_context_overflow_includes_breakdown() — line 920
  - test_cost_limit_enforced() — line 941
  - test_cost_limit_bypass() — line 952
  - test_retry_on_429_then_success() — line 968
  - test_no_retry_on_401() — line 990
  - test_missing_api_key_raises() — line 1005
  - test_malformed_response_raises() — line 1017
  - test_actual_cost_tracked() — line 1031

### TestRequestWrappers
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1063
- Bases: object
  - test_request_chapter_too_short_raises() — line 1064
  - test_request_chapter_long_enough_passes() — line 1071
  - test_update_living_doc_validation_passes() — line 1079
  - test_update_living_doc_validation_fails() — line 1090

### TestAtomicity
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1109
- Bases: object
  - test_no_tmp_files_after_save() — line 1110
  - test_state_write_no_tmp_leftover() — line 1116

### TestC2FirstRunGuard
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1216
- Bases: object
  - test_empty_living_doc_and_no_chapters_refuses() — line 1217

### TestC3AutoApproveResumeRefuses
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1227
- Bases: object
  - test_inconsistent_resume_under_auto_approve_aborts() — line 1228

### TestC4AutoApproveSkipGap
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1243
- Bases: object
  - test_chapter_start_skipping_gap_under_auto_approve_aborts() — line 1244

### TestH2KeepOldStopsSession
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1253
- Bases: object
  - test_keep_old_living_doc_stops_session() — line 1254
  - fake_request_chapter() — line 1266
  - fake_request_update() — line 1269

### TestM4RejectionLimitBounded
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1289
- Bases: object
  - test_runaway_rejections_eventually_raise() — line 1290

### TestI15EOFAbortInPromptChoice
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1307
- Bases: object
  - test_eof_picks_abort_key() — line 1308
  - raise_eof() — line 1312
  - test_eof_no_a_key_falls_back_to_last() — line 1322
  - raise_eof() — line 1325

### TestM5DryRunPlaceholderSized
- File: src/novel_pipeline/tests/test_pipeline.py
- Line: 1336
- Bases: object
  - test_dry_run_chapter_sized_to_expected_tokens() — line 1337

### PodcastError
- File: src/podcast_script_generator/llm/exceptions.py
- Line: 1
- Bases: Exception

### PDFExtractionError
- File: src/podcast_script_generator/llm/exceptions.py
- Line: 4
- Bases: PodcastError

### ScriptGenerationError
- File: src/podcast_script_generator/llm/exceptions.py
- Line: 7
- Bases: PodcastError

### TTSSubmissionError
- File: src/podcast_script_generator/llm/exceptions.py
- Line: 10
- Bases: PodcastError

### TTSTimeoutError
- File: src/podcast_script_generator/llm/exceptions.py
- Line: 13
- Bases: PodcastError

## 5. Transport/HTTP Call Sites

| src/novel_pipeline/api.py | - | call_api | 248 | OPENROUTER_URL |
| src/podcast_script_generator/llm/call_api.py | - | call_api | 62 | OPENROUTER_API_KEY |

## 6. sys.path.insert & Runtime Path Hacks

| src/fiction/seed_gen/cli.py | 7 | `sys.path.insert(0, str(SRC / 'podcast_script_generator' / 'llm'))` |
| src/novel_pipeline/tests/test_pipeline.py | 41 | `sys.path.insert(0, str(Path(__file__).resolve().parent))` |
| src/podcast_script_generator/llm/test_all.py | 22 | `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` |
| src/slicer/pdf_splitter.py | 216 | `sys.path.insert(0, llm_dir)` |

## 7. Env Access Patterns

| src/novel_pipeline/api.py | OPENROUTER_API_KEY | 61 |
| src/novel_pipeline/api.py | OPENROUTER_URL | 335 |
| src/novel_pipeline/config.py | OPENROUTER_API_KEY | 340 |
| src/novel_pipeline/config.py | OPENROUTER_MODEL | 342 |
| src/podcast_script_generator/llm/call_api.py | OPENROUTER_MODEL | 24 |
| src/podcast_script_generator/llm/call_api.py | OPENROUTER_MAX_TOKENS | 33 |
| src/podcast_script_generator/llm/call_api.py | OPENROUTER_URL | 42 |
| src/podcast_script_generator/llm/call_api.py | OPENROUTER_RETRY_AFTER | 55 |
| src/podcast_script_generator/llm/call_api.py | OPENROUTER_API_KEY | 69 |
| src/slicer/pdf_splitter.py | OPENROUTER_API_KEY | 224 |

## 8. Test Inventory

| src/novel_pipeline/tests/test_pipeline.py | — | |
| src/podcast_script_generator/llm/test_all.py | — | |
## 9. Function Bodies (Read Source Files Directly)

### src/engines/llm_script.py::LLMScriptEngine.generate
```python
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
```

### src/engines/factory.py::default_llm_script_engine
```python
def default_llm_script_engine(mode: str = "2person") -> ScriptEngine:
    return LLMScriptEngine(mode=mode)
```

### src/engines/factory.py::default_splitter_engine
```python
def default_splitter_engine() -> SplitterEngine:
    return PDFSplitterEngine()
```

### src/endpoints/podcast.py::generate_book_podcast
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
    settings = settings or PodcastSettings()

    if toc_page is None:
        from config import load_config
        toc_page = load_config().get("toc_page")

    if book_pdf is not None:
        book_pdf = Path(book_pdf).resolve()
        if splitter_engine is None:
            from engines.factory import default_splitter_engine
            splitter_engine = default_splitter_engine()
        chapters_out = settings.chapters_dir
        existing = list(chapters_out.glob("*.pdf")) if chapters_out.exists() else []
        if force or not existing:
            chapters_out.mkdir(parents=True, exist_ok=True)
            splitter_engine.split(
                book_pdf,
                toc_page=toc_page,
                output_dir=chapters_out,
                no_ocr=no_ocr,
            )

    if slice_only:
        return [PodcastResult()]

    resolve_dir = chapters_dir or settings.chapters_dir
    if not resolve_dir or not resolve_dir.exists():
        return []

    pdfs = sorted(
        resolve_dir.glob("*.pdf"),
        key=lambda p: [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", p.stem)],
    )

    results = []
    for pdf in pdfs:
        r = generate_chapter_podcast(
            pdf,
            script_engine=script_engine,
            audio_engine=audio_engine,
            settings=settings,
            skip_audio=skip_audio,
            mode=mode,
            context=context,
        )
        results.append(r)
    return results
```

### src/endpoints/podcast.py::generate_chapter_podcast
```python
def generate_chapter_podcast(
    pdf_path: Path | None = None,
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
    settings = settings or PodcastSettings()

    try:
        if script_path is not None:
            script_path = Path(script_path).resolve()
            if not script_path.exists():
                return PodcastResult(error=FileNotFoundError(f"Script not found: {script_path}"))
            script_out = script_path
            naming_path = script_path
        else:
            if pdf_path is None:
                return PodcastResult(error=ValueError("pdf_path is required when not using --skip-script"))
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
            naming_path = pdf_path

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
```

### src/novel_pipeline/config.py::load_config
```python
def load_config(path: str) -> dict:
    """Read TOML config, apply defaults, validate required keys, apply env
    overrides. Unknown keys are logged as warnings.

    Returns a flat dict.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p.resolve()}")

    try:
        with p.open("rb") as f:
            raw = _toml.load(f)
    except _toml.TOMLDecodeError as e:
        raise ConfigError(f"invalid TOML in {p}: {e}") from e

    # TOML is hierarchical; we accept either a flat structure or a [pipeline]
    # section. Anything in a top-level table key is merged in.
    cfg: dict = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            cfg.update(v)
        else:
            cfg[k] = v

    # Required keys check.
    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        raise ConfigError(f"config missing required keys: {missing}")

    # Apply defaults for anything not specified.
    for k, default in DEFAULTS.items():
        cfg.setdefault(k, default)

    # Env overrides.
    if "OPENROUTER_API_KEY" in os.environ:
        cfg["api_key"] = os.environ["OPENROUTER_API_KEY"]
    if "OPENROUTER_MODEL" in os.environ:
        cfg["model"] = os.environ["OPENROUTER_MODEL"]

    # Warn on unknown keys (anything not required/defaulted/known).
    known = set(REQUIRED_KEYS) | set(DEFAULTS.keys()) | {"api_key"}
    unknown = [k for k in cfg.keys() if k not in known]
    if unknown:
        log_event("config_unknown_keys", {"keys": unknown})

    # Type coercion of integer fields.
    int_keys = (
        "context_limit",
        "chapters_per_session",
        "max_retries",
        "min_chapter_words",
        "context_safety_margin",
        "expected_output_tokens_chapter",
        "expected_output_tokens_update",
        "max_rejection_retries",
        "tokenizer_chars_per_token",
        "token_count_per_message_overhead",
        "token_count_completion_priming",
    )
    for k in int_keys:
        cfg[k] = int(cfg[k])

    float_keys = (
        "timeout_seconds",
        "price_per_1m_input_tokens",
        "price_per_1m_output_tokens",
        "cost_limit_usd_per_session",
        "cost_limit_usd_total",
        "retry_jitter_seconds_max",
    )
    for k in float_keys:
        cfg[k] = float(cfg[k])

    # Optional numeric fields — coerce only if set.
    if cfg.get("temperature") is not None:
        cfg["temperature"] = float(cfg["temperature"])
    if cfg.get("top_p") is not None:
        cfg["top_p"] = float(cfg["top_p"])
    if cfg.get("seed") is not None:
        cfg["seed"] = int(cfg["seed"])
    if cfg.get("api_default_max_tokens_chapter") is not None:
        cfg["api_default_max_tokens_chapter"] = int(cfg["api_default_max_tokens_chapter"])
    if cfg.get("api_default_max_tokens_update") is not None:
        cfg["api_default_max_tokens_update"] = int(cfg["api_default_max_tokens_update"])

    # static_doc_paths must be a list of strings.
    if not isinstance(cfg["static_doc_paths"], list) or not all(
        isinstance(s, str) for s in cfg["static_doc_paths"]
    ):
        raise ConfigError("static_doc_paths must be a list of strings")

    # M2: Numeric sanity validation.
    _validate_numerics(cfg)
    # M2: Format-string sanity validation.
    _validate_formats(cfg)

    return cfg
```

### src/fiction/seed_gen/cli.py::main
```python
def main() -> None:
    try:
        args = parse_args()
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        templates = load_templates()
        book_text = truncate_pdf_text(extract_pdf(args.source_pdf))
        pass1_prompt = build_pass1_prompt(templates)

        print("Running Pass 1: genre evaluation...")
        pass1_response = call_api(pdf_text=book_text, prompt_text=pass1_prompt)
        validate_pass1_response(pass1_response)
        print(pass1_response)

        user_plan = collect_user_plan(pass1_response)

        print("\nRunning Pass 2: generating files...")
        pass2_prompt = build_pass2_prompt(user_plan, pass1_response, templates)
        pass2_response = call_api(pdf_text="", prompt_text=pass2_prompt)
        files = parse_output(pass2_response)
        save_output(files, str(output_dir))
        write_config_toml(output_dir)
        print(f"\nSeed files written to {output_dir}.")
        print(f"Review and edit them, then run: novel-pipeline --config {output_dir}/config.toml")

    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### src/slicer/pdf_splitter.py::get_toc_from_llm
```python
def get_toc_from_llm(pdf_path: str) -> Optional[List[TocEntry]]:
    """Stage 4: send OCR'd front matter + page samples to the LLM to identify structure."""
    import sys
    from pathlib import Path

    llm_dir = str(Path(__file__).parent.parent / "podcast_script_generator" / "llm")
    if llm_dir not in sys.path:
        sys.path.insert(0, llm_dir)

    try:
        from call_api import call_api
    except ImportError:
        logging.warning("Stage 4: call_api not importable — skipping.")
        return None

    if not os.environ.get("OPENROUTER_API_KEY"):
        logging.warning("Stage 4: OPENROUTER_API_KEY not set — skipping.")
        return None

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
    except Exception as e:
        logging.warning(f"Stage 4: cannot open PDF: {e}")
        return None

    # OCR first 20 pages — TOC and front matter live here
    scan_end = min(20, total_pages)
    logging.info(f"Stage 4: OCR-ing pages 1–{scan_end} for LLM analysis...")
    front_text = _ocr_pages_text(pdf_path, 1, scan_end, dpi=200)

    # OCR 3 sample pages spread across the first half — lets LLM compute the page offset
    sample_pages = sorted({max(1, int(total_pages * f)) for f in (0.2, 0.35, 0.5)})
    logging.info(f"Stage 4: OCR-ing sample pages {sample_pages} for offset detection...")
    sample_parts = []
    for p in sample_pages:
        sample_parts.append(_ocr_pages_text(pdf_path, p, p, dpi=150))
    sample_text = "\n\n".join(sample_parts)

    prompt = f"""\
You are analyzing a scanned book PDF to extract its structure for automated splitting.

You are given:
1. OCR text from the first {scan_end} PDF pages (front matter and table of contents).
2. OCR samples from three pages deeper in the book, each marked [PDF PAGE N].

Your task — follow these steps exactly:

STEP 1 — Find the Table of Contents in the front matter text.
STEP 2 — For each top-level division (PART, Chapter, or equivalent major section), read the
          PRINTED page number listed next to it in the TOC (e.g. "Chapter 2 ..... 47" → printed page 47).
STEP 3 — Compute the page offset using the sample pages:
          offset = [PDF PAGE N] − (printed page number visible on that sample page).
          Use the most consistent offset across all samples.
STEP 4 — Convert: PDF_PAGE = printed_page_from_TOC + offset.
STEP 5 — Output one line per top-level division.

CRITICAL RULES:
- NEVER output the [PDF PAGE N] of the TOC row itself. Those are where entries are LISTED,
  not where the content STARTS. The content starts pages later.
- Use only the printed page numbers from the TOC entries, then add the offset.
- Skip front matter (cover, copyright, preface, foreword).
- Aim for major structural divisions only (PARTs or numbered Chapters), not subsections.

Output format — ONLY these lines, no explanation:
ENTRY: <title> | PDF_PAGE: <number>

=== FRONT MATTER + TOC (PDF pages 1–{scan_end}) ===
{front_text}

=== SAMPLE PAGES (for offset detection) ===
{sample_text}
"""

    logging.info("Stage 4: calling LLM...")
    try:
        response = call_api(pdf_text="", prompt_text=prompt)
    except Exception as e:
        logging.warning(f"Stage 4: LLM call failed: {e}")
        return None

    toc: List[TocEntry] = []
    for line in response.splitlines():
        # re.search handles leading markdown (**, -, etc); separator tolerates |, -, /
        m = re.search(
            r"ENTRY:\s*(.+?)\s*[|\-/]\s*PDF_PAGE:\s*(\d+)",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            title = m.group(1).strip().strip("*_")
            page = int(m.group(2))
            if 1 <= page <= total_pages:
                toc.append((1, title, page))

    if not toc:
        logging.warning("Stage 4: LLM response had no parseable ENTRY lines.")
        logging.debug(f"Stage 4 raw response:\n{response}")
        return None

    # Sort by page and deduplicate (same title+page)
    toc.sort(key=lambda x: x[2])
    seen: set = set()
    deduped: List[TocEntry] = []
    for entry in toc:
        key = (entry[1], entry[2])
        if key not in seen:
            seen.add(key)
            deduped.append(entry)
    toc = deduped

    # Option 2: if entries cluster in a small page range the LLM likely returned
    # printed page numbers rather than PDF positions. Compute offset from the
    # sample pages and re-apply it; if that passes validation, use the result.
    if not _validate_toc(toc, total_pages):
        offset = _detect_page_offset(sample_text, total_pages)
        if offset is not None and offset > 0:
            adjusted = [
                (level, title, page + offset)
                for level, title, page in toc
                if 1 <= page + offset <= total_pages
            ]
            if adjusted and _validate_toc(adjusted, total_pages):
                logging.info(f"Stage 4: offset +{offset} corrected entries to span PDF correctly.")
                toc = adjusted

    logging.info(f"Stage 4: LLM identified {len(toc)} sections.")
    return toc
```

### src/novel_pipeline/api.py::call_api
```python
def call_api(
    messages: list[dict],
    model: str,
    config: dict,
    *,
    expected_output_tokens: int | None = None,
    ignore_cost_limit: bool = False,
    # Optional metadata for richer error reporting:
    static_docs: dict[str, str] | None = None,
    living_doc: str | None = None,
    task_label: str = "",
) -> str:
    """Call OpenRouter chat-completions and return the assistant text.

    Pre-flight:
      1. Token count vs context_limit - safety_margin.
      2. Estimated cost vs session/lifetime limits.
    Retries on 429/5xx/network errors with Retry-After or configurable
    exponential backoff. Tracks actual spend from response.usage. Detects
    truncation via choices[0].finish_reason (C1).
    """
    api_key = _resolve_api_key(config)
    timeout = float(config.get("timeout_seconds", 120))
    max_retries = int(config.get("max_retries", 3))
    context_limit = int(config["context_limit"])
    safety_margin = int(config.get("context_safety_margin", 8000))

    # --- Token pre-flight ---------------------------------------------------
    # H3: use chat-overhead-aware counting.
    prompt_tokens = _count_prompt_tokens(messages, model, config)
    if prompt_tokens + safety_margin > context_limit:
        breakdown = _per_document_tokens(static_docs, living_doc, model, config)
        # Build the doc-order list from config for the breakdown print order.
        from .config import DEFAULT_STATIC_DOC_ORDER
        static_order = list(config.get("static_doc_order", DEFAULT_STATIC_DOC_ORDER))
        raise ContextOverflowError(
            _format_overflow_message(
                prompt_tokens, context_limit, safety_margin, breakdown, static_order
            )
        )

    # --- Cost pre-flight ----------------------------------------------------
    if expected_output_tokens is None:
        expected_output_tokens = int(
            config.get("expected_output_tokens_chapter", 4000)
        )

    # C1: max_tokens on the request itself. Honour explicit override; else
    # default to expected_output_tokens.
    explicit_max = None
    label_lc = (task_label or "").lower()
    if "update" in label_lc:
        explicit_max = config.get("api_default_max_tokens_update")
    else:
        explicit_max = config.get("api_default_max_tokens_chapter")
    max_tokens_for_payload = int(explicit_max) if explicit_max else int(expected_output_tokens)

    estimated = estimate_cost(prompt_tokens, expected_output_tokens, config)
    _enforce_cost_limits(estimated, config, ignore_limit=ignore_cost_limit)

    log_event(
        "api_call_preflight",
        {
            "task": task_label,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "expected_output_tokens": expected_output_tokens,
            "max_tokens_in_payload": max_tokens_for_payload,
            "estimated_cost_usd": round(estimated, 6),
            "temperature": config.get("temperature"),
            "top_p": config.get("top_p"),
            "seed": config.get("seed"),
        },
    )

    # --- Request loop -------------------------------------------------------
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "novel-pipeline",
    }
    payload = _build_payload(
        messages, model, config, max_tokens=max_tokens_for_payload
    )

    api_url = (
        config.get("api_url")
        or os.environ.get("OPENROUTER_URL")
        or _DEFAULT_API_URL
    )

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as e:
            last_error = e
            log_event(
                "api_call_network_error",
                {"attempt": attempt + 1, "error": str(e), "task": task_label},
            )
            if attempt >= max_retries:
                break
            sleep = _backoff_seconds(config, attempt)
            sleep = _jittered_sleep(config, sleep)
            time.sleep(sleep)
            continue

        # Non-retryable client errors → fail fast.
        if response.status_code in (400, 401, 403):
            raise APIResponseError(
                f"OpenRouter returned {response.status_code} "
                f"(non-retryable): {response.text[:500]}"
            )

        if response.status_code in _RETRYABLE_STATUS:
            retry_after_hdr = response.headers.get("Retry-After", "")
            wait = _parse_retry_after(retry_after_hdr)
            if wait is None:
                wait = _backoff_seconds(config, attempt)
            log_event(
                "api_call_retryable_status",
                {
                    "attempt": attempt + 1,
                    "status": response.status_code,
                    "retry_after_header": retry_after_hdr,
                    "sleep_seconds": wait,
                    "task": task_label,
                },
            )
            if attempt >= max_retries:
                last_error = APIResponseError(
                    f"OpenRouter returned {response.status_code} after "
                    f"{max_retries} retries: {response.text[:500]}"
                )
                break
            time.sleep(wait)
            continue

        # Other non-2xx not in our retry set.
        if not response.ok:
            raise APIResponseError(
                f"OpenRouter returned {response.status_code}: "
                f"{response.text[:500]}"
            )

        # --- Parse response -------------------------------------------------
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise APIResponseError(f"non-JSON response: {e}: {response.text[:500]}") from e

        try:
            choice0 = data["choices"][0]
            content = choice0["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise APIResponseError(
                f"malformed response (no choices[0].message.content): "
                f"{json.dumps(data)[:500]}"
            ) from e

        # C1: detect truncation/refusal via finish_reason.
        finish_reason = choice0.get("finish_reason")
        if finish_reason == "length":
            log_event(
                "api_call_truncated_by_length",
                {
                    "task": task_label,
                    "max_tokens_in_payload": max_tokens_for_payload,
                    "content_chars": len(content or ""),
                },
            )
            raise ChapterValidationError(
                "Model hit max_tokens before completing the response "
                f"(finish_reason='length'; max_tokens={max_tokens_for_payload}). "
                "The output is truncated and unsafe to use. Either increase "
                "expected_output_tokens_chapter / "
                "api_default_max_tokens_chapter in config, or retry the "
                "request."
            )
        if finish_reason == "content_filter":
            log_event(
                "api_call_content_filtered",
                {"task": task_label},
            )
            raise APIResponseError(
                "Response was rejected by the model's content filter "
                "(finish_reason='content_filter'). Adjust the prompt or "
                "switch models."
            )

        if content is None:
            content = ""
        content = content.strip()

        if not content:
            # Empty content: treat like a retryable failure.
            log_event(
                "api_call_empty_content",
                {"attempt": attempt + 1, "task": task_label},
            )
            if attempt >= max_retries:
                raise APIResponseError(
                    "OpenRouter returned empty content after retries"
                )
            time.sleep(_backoff_seconds(config, attempt))
            continue

        # --- Actual cost from usage ----------------------------------------
        usage = data.get("usage") or {}
        actual_in = int(usage.get("prompt_tokens", prompt_tokens))
        actual_out = int(usage.get("completion_tokens", expected_output_tokens))
        actual_cost = estimate_cost(actual_in, actual_out, config)
        track_spend(
            actual_cost,
            config,
            note=f"{task_label} model={model} in={actual_in} out={actual_out}",
        )
        log_event(
            "api_call_success",
            {
                "task": task_label,
                "model": model,
                "actual_prompt_tokens": actual_in,
                "actual_completion_tokens": actual_out,
                "actual_cost_usd": round(actual_cost, 6),
                "content_chars": len(content),
                "finish_reason": finish_reason,
            },
        )
        return content

    # Fell out of the retry loop without success.
    if last_error is None:
        last_error = APIResponseError("exhausted retries with no specific error")
    raise APIResponseError(str(last_error)) from last_error
```

### src/podcast_script_generator/llm/call_api.py::call_api
```python
def call_api(pdf_text: str, prompt_text: str) -> str:
    """Send prompt + PDF text to OpenRouter and return the response text.

    Model resolution priority: OPENROUTER_MODEL env var > src/config.json > default.
    Reads the API key from the OPENROUTER_API_KEY environment variable.
    Lets any exception propagate — no silent swallowing.
    """
    api_key = os.environ["OPENROUTER_API_KEY"]
    api_url = _resolve_api_url()
    model = _resolve_model()
    max_tokens = _resolve_max_tokens()

    user_message = f"{prompt_text}\n\n---\n\n{pdf_text}" if pdf_text else prompt_text

    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user_message}],
    }).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code != 429:
                raise RuntimeError(f"OpenRouter HTTP {e.code}: {body}") from e

            # Priority: OPENROUTER_RETRY_AFTER / config.json > API body > exponential backoff.
            override = _resolve_retry_after()
            if override is not None:
                wait = override
            else:
                wait = 30.0 * (2 ** attempt)
                try:
                    err_data = json.loads(body)
                    wait = float(
                        err_data.get("error", {})
                        .get("metadata", {})
                        .get("retry_after_seconds", wait)
                    )
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass
            if attempt == _MAX_RETRIES:
                raise RuntimeError(f"OpenRouter HTTP 429 after {_MAX_RETRIES} retries: {body}") from e
            logger.debug(f"OpenRouter 429 — waiting {wait:.0f}s before retry {attempt + 1}/{_MAX_RETRIES}...")
            last_error = e
            time.sleep(wait)

    raise RuntimeError("call_api: exceeded retry loop") from last_error
```

### src/novel_pipeline/cli.py::main
```python
def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    approve_fn: ApproveChapterFn = (lambda n, t: True) if args.auto_approve else prompt_user

    # --- Config + logging ---
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2

    configure_log(config["log_path"])
    log_event(
        "cli_start",
        {
            "config_path": args.config,
            "auto_approve": args.auto_approve,
            "dry_run": args.dry_run,
            "resume": args.resume,
            "chapter_start": args.chapter_start,
            "ignore_cost_limit": args.ignore_cost_limit,
        },
    )

    # --- Run ---
    try:
        run_session(
            config,
            auto_approve=args.auto_approve,
            dry_run=args.dry_run,
            resume=args.resume,
            chapter_start=args.chapter_start,
            ignore_cost_limit=args.ignore_cost_limit,
            approve_chapter=approve_fn,
        )
    except KeyboardInterrupt:
        print("\nInterrupted. State preserved. Exit code 1.", file=sys.stderr)
        return 1
    except ResumeStateError as e:
        print(f"Resume state error: {e}", file=sys.stderr)
        log_event("cli_resume_state_error", {"error": str(e)})
        return 2
    except PromotionCollisionError as e:
        print(f"Promotion collision (state drift): {e}", file=sys.stderr)
        log_event("cli_promotion_collision", {"error": str(e)})
        return 2
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2
    except DocumentLoadError as e:
        print(f"Document load error: {e}", file=sys.stderr)
        log_event("cli_document_load_error", {"error": str(e)})
        return 2
    except CostLimitError as e:
        print(f"Cost limit hit: {e}", file=sys.stderr)
        log_event("cli_cost_limit", {"error": str(e)})
        return 1
    except RejectionLimitReachedError as e:
        print(f"Rejection limit reached: {e}", file=sys.stderr)
        log_event("cli_rejection_limit_reached", {"error": str(e)})
        return 1
    except ContextOverflowError as e:
        print(str(e), file=sys.stderr)
        log_event("cli_context_overflow", {})
        return 3
    except APIResponseError as e:
        print(f"API error after retries: {e}", file=sys.stderr)
        log_event("cli_api_error", {"error": str(e)})
        return 3
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        log_event(
            "cli_unexpected_error",
            {"error": str(e), "traceback": traceback.format_exc()},
        )
        return 3

    return 0
```

### src/endpoints/fiction.py::run_novel_session
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

### src/cli/podcast.py::main
```python
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

    from engines.factory import default_llm_script_engine, default_audio_engine, default_splitter_engine
    script_engine = None if args.skip_script else default_llm_script_engine(mode=args.mode)
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
            splitter_engine=default_splitter_engine(),
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
```

### src/novel_pipeline/exceptions.py (entire file)
```python
"""Custom exception hierarchy for the pipeline.

All pipeline-specific errors inherit from PipelineError so callers can catch
the whole family with one except clause when they want to.
"""


class PipelineError(Exception):
    """Base class for all pipeline-specific errors."""


class DocumentLoadError(PipelineError):
    """Raised when a template or living-doc file cannot be loaded."""


class ConfigError(PipelineError):
    """Raised when configuration is missing or invalid."""


class APIResponseError(PipelineError):
    """Raised when the OpenRouter response is malformed or unusable."""


class ChapterValidationError(PipelineError):
    """Raised when a generated chapter fails validation (too short,
    truncated by length, etc.)."""


class LivingDocValidationError(PipelineError):
    """Raised when an updated living doc fails structural validation."""

    def __init__(self, message: str, missing: list[str] | None = None, diff: str | None = None):
        super().__init__(message)
        self.missing = missing or []
        self.diff = diff or ""


class ContextOverflowError(PipelineError):
    """Raised when the prompt + safety margin would exceed the model context."""


class CostLimitError(PipelineError):
    """Raised when a session or lifetime cost limit would be exceeded."""


class ResumeStateError(PipelineError):
    """Raised when .pipeline_state.json is missing/malformed in a way that
    cannot be reconciled with the filesystem automatically."""


class PromotionCollisionError(PipelineError):
    """M1: Raised when promote_chapter would overwrite an existing canonical
    chapter. Indicates a state-drift bug that the human must resolve."""


class RejectionLimitReachedError(PipelineError):
    """M4: Raised when the rejection-retry loop exceeds the configured
    maximum number of iterations (`max_rejection_retries`)."""

```

