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
| src/chapters/ | package | **MISSING** | |
| src/chapters/.rejected/ | package | **MISSING** | |
| src/cli/ | package | yes | |
| src/cli/__init__.py | module | n/a | |
| src/cli/fiction.py | module | n/a | |
| src/cli/podcast.py | module | n/a | |
| src/config.py | module | n/a | |
| src/docs/ | package | **MISSING** | |
| src/docs/harness_history/ | package | **MISSING** | |
| src/docs/session_notes/ | package | **MISSING** | |
| src/endpoints/ | package | yes | |
| src/endpoints/__init__.py | module | n/a | |
| src/endpoints/fiction.py | module | n/a | |
| src/endpoints/podcast.py | module | n/a | |
| src/endpoints/podcast_types.py | module | n/a | |
| src/endpoints/slicer.py | module | n/a | |
| src/engines/ | package | yes | |
| src/engines/__init__.py | module | n/a | |
| src/engines/factory.py | module | n/a | |
| src/engines/llm_script.py | module | n/a | |
| src/engines/pdf_splitter.py | module | n/a | |
| src/engines/protocols.py | module | n/a | |
| src/engines/wavespeed_audio.py | module | n/a | |
| src/fiction/ | package | **MISSING** | |
| src/fiction/pipeline/ | package | **MISSING** | |
| src/fiction/pipeline/chapters/ | package | **MISSING** | |
| src/fiction/pipeline/chapters/.rejected/ | package | **MISSING** | |
| src/fiction/pipeline/templates/ | package | **MISSING** | |
| src/fiction/seed_gen/ | package | yes | |
| src/fiction/seed_gen/__init__.py | module | n/a | |
| src/fiction/seed_gen/__main__.py | module | n/a | |
| src/fiction/seed_gen/cli.py | module | n/a | |
| src/fiction/seed_gen/prompts/ | package | **MISSING** | |
| src/fiction/seed_gen/templates/ | package | **MISSING** | |
| src/fiction/specs/ | package | **MISSING** | |
| src/novel_pipeline/ | package | yes | |
| src/novel_pipeline/__init__.py | module | n/a | |
| src/novel_pipeline/__main__.py | module | n/a | |
| src/novel_pipeline/api.py | module | n/a | |
| src/novel_pipeline/cli.py | module | n/a | |
| src/novel_pipeline/config.py | module | n/a | |
| src/novel_pipeline/cost.py | module | n/a | |
| src/novel_pipeline/docs.py | module | n/a | |
| src/novel_pipeline/exceptions.py | module | n/a | |
| src/novel_pipeline/logging_.py | module | n/a | |
| src/novel_pipeline/prompt.py | module | n/a | |
| src/novel_pipeline/prompts.py | module | n/a | |
| src/novel_pipeline/requests_.py | module | n/a | |
| src/novel_pipeline/session.py | module | n/a | |
| src/novel_pipeline/state.py | module | n/a | |
| src/novel_pipeline/tests/ | package | **MISSING** | |
| src/novel_pipeline/tests/test_pipeline.py | module | n/a | |
| src/novel_pipeline/tokens.py | module | n/a | |
| src/pdfslicer/ | package | **MISSING** | |
| src/phases/ | package | **MISSING** | |
| src/phases/phase_01/ | package | **MISSING** | |
| src/phases/phase_02/ | package | **MISSING** | |
| src/phases/phase_03/ | package | **MISSING** | |
| src/phases/phase_04/ | package | **MISSING** | |
| src/phases/phase_05/ | package | **MISSING** | |
| src/phases/phase_06/ | package | **MISSING** | |
| src/phases/phase_07/ | package | **MISSING** | |
| src/podcast_script_generator/ | package | yes | |
| src/podcast_script_generator/__init__.py | module | n/a | |
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
| src/run_book.py | module | n/a | |
| src/run_chapter.py | module | n/a | |
| src/settings.py | module | n/a | |
| src/slicer/ | package | yes | |
| src/slicer/__init__.py | module | n/a | |
| src/slicer/pdf_splitter.py | module | n/a | |
| src/tts/ | package | yes | |
| src/tts/__init__.py | module | n/a | |
| src/tts/cli.py | module | n/a | |
| src/tts/recover.py | module | n/a | |
| src/unwanted_from_the_project_dir/ | package | **MISSING** | |
| src/unwanted_from_the_project_dir/main.py | module | n/a | |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | module | n/a | |
| src/unwanted_from_the_project_dir/splitter_V1.py | module | n/a | |
| src/util/ | package | yes | |
| src/util/__init__.py | module | n/a | |
| src/util/normalize.py | module | n/a | |

## 2. Import Graph (Cross-Module)

| Source Module | Imports From | Imported Names | Line |
|---------------|--------------|----------------|------|
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
| src/endpoints/podcast_types.py | dataclasses | dataclass | 1 |
| src/endpoints/podcast_types.py | enum | Enum | 2 |
| src/endpoints/podcast_types.py | pathlib | Path | 3 |
| src/endpoints/slicer.py | engines.pdf_splitter | PDFSplitterEngine | 1 |
| src/endpoints/slicer.py | slicer.pdf_splitter | run_splitter | 2 |
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
| src/engines/protocols.py | typing | Protocol, runtime_checkable | 1 |
| src/engines/protocols.py | pathlib | Path | 2 |
| src/engines/wavespeed_audio.py | os | os | 1 |
| src/engines/wavespeed_audio.py | pathlib | Path | 2 |
| src/engines/wavespeed_audio.py | typing | Any | 3 |
| src/engines/wavespeed_audio.py | config | load_config | 5 |
| src/engines/wavespeed_audio.py | engines.protocols | AudioEngine | 6 |
| src/engines/wavespeed_audio.py | tts.cli | main | 22 |
| src/fiction/seed_gen/__main__.py | cli | main | 1 |
| src/fiction/seed_gen/cli.py | argparse | argparse | 1 |
| src/fiction/seed_gen/cli.py | re | re | 2 |
| src/fiction/seed_gen/cli.py | sys | sys | 3 |
| src/fiction/seed_gen/cli.py | pathlib | Path | 4 |
| src/fiction/seed_gen/cli.py | extract_pdf | extract_pdf | 9 |
| src/fiction/seed_gen/cli.py | call_api | call_api | 10 |
| src/fiction/seed_gen/cli.py | parse_output | parse_output | 11 |
| src/fiction/seed_gen/cli.py | save_output | save_output | 12 |
| src/novel_pipeline/__init__.py | cli | main | 10 |
| src/novel_pipeline/__init__.py | config | load_config | 11 |
| src/novel_pipeline/__init__.py | exceptions | APIResponseError, ChapterValidationError, ConfigError, ContextOverflowError, CostLimitError, DocumentLoadError, LivingDocValidationError, PipelineError, PromotionCollisionError, RejectionLimitReachedError, ResumeStateError | 12 |
| src/novel_pipeline/__init__.py | session | run_session | 25 |
| src/novel_pipeline/__main__.py | sys | sys | 1 |
| src/novel_pipeline/__main__.py | cli | main | 3 |
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
| src/novel_pipeline/cost.py | __future__ | annotations | 17 |
| src/novel_pipeline/cost.py | json | json | 19 |
| src/novel_pipeline/cost.py | os | os | 20 |
| src/novel_pipeline/cost.py | tempfile | tempfile | 21 |
| src/novel_pipeline/cost.py | datetime | datetime, timezone | 22 |
| src/novel_pipeline/cost.py | pathlib | Path | 23 |
| src/novel_pipeline/cost.py | logging_ | log_event | 25 |
| src/novel_pipeline/docs.py | __future__ | annotations | 15 |
| src/novel_pipeline/docs.py | difflib | difflib | 17 |
| src/novel_pipeline/docs.py | os | os | 18 |
| src/novel_pipeline/docs.py | shutil | shutil | 19 |
| src/novel_pipeline/docs.py | tempfile | tempfile | 20 |
| src/novel_pipeline/docs.py | datetime | datetime, timezone | 21 |
| src/novel_pipeline/docs.py | pathlib | Path | 22 |
| src/novel_pipeline/docs.py | exceptions | DocumentLoadError, PromotionCollisionError | 24 |
| src/novel_pipeline/docs.py | logging_ | log_event | 25 |
| src/novel_pipeline/docs.py | docx | docx | 102 |
| src/novel_pipeline/logging_.py | __future__ | annotations | 6 |
| src/novel_pipeline/logging_.py | json | json | 8 |
| src/novel_pipeline/logging_.py | sys | sys | 9 |
| src/novel_pipeline/logging_.py | threading | threading | 10 |
| src/novel_pipeline/logging_.py | datetime | datetime, timezone | 11 |
| src/novel_pipeline/logging_.py | pathlib | Path | 12 |
| src/novel_pipeline/prompts.py | __future__ | annotations | 15 |
| src/novel_pipeline/prompts.py | config | DEFAULT_STATIC_DOC_ORDER, DEFAULT_SYSTEM_PROMPT_GENERATE_CHAPTER, DEFAULT_SYSTEM_PROMPT_UPDATE_LIVING_DOC | 17 |
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
| src/novel_pipeline/state.py | __future__ | annotations | 24 |
| src/novel_pipeline/state.py | json | json | 26 |
| src/novel_pipeline/state.py | os | os | 27 |
| src/novel_pipeline/state.py | re | re | 28 |
| src/novel_pipeline/state.py | tempfile | tempfile | 29 |
| src/novel_pipeline/state.py | datetime | datetime, timezone | 30 |
| src/novel_pipeline/state.py | pathlib | Path | 31 |
| src/novel_pipeline/state.py | exceptions | ResumeStateError | 33 |
| src/novel_pipeline/state.py | logging_ | log_event | 34 |
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
| src/novel_pipeline/tokens.py | __future__ | annotations | 13 |
| src/novel_pipeline/tokens.py | functools | lru_cache | 15 |
| src/novel_pipeline/tokens.py | logging_ | log_event | 17 |
| src/novel_pipeline/tokens.py | tiktoken | tiktoken | 33 |
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
| src/run_book.py | cli.podcast | main | 1 |
| src/run_chapter.py | cli.podcast | main | 1 |
| src/settings.py | dataclasses | dataclass, field | 1 |
| src/settings.py | datetime | datetime | 2 |
| src/settings.py | pathlib | Path | 3 |
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
| src/tts/cli.py | json | json | 7 |
| src/tts/cli.py | logging | logging | 8 |
| src/tts/cli.py | os | os | 9 |
| src/tts/cli.py | re | re | 10 |
| src/tts/cli.py | sys | sys | 11 |
| src/tts/cli.py | time | time | 12 |
| src/tts/cli.py | datetime | datetime | 13 |
| src/tts/cli.py | pathlib | Path | 14 |
| src/tts/cli.py | requests | requests | 19 |
| src/tts/cli.py | wavespeed | wavespeed | 20 |
| src/tts/cli.py | config | load_config | 24 |
| src/tts/cli.py | podcast_script_generator.llm.exceptions | PodcastError, TTSSubmissionError, TTSTimeoutError | 25 |
| src/tts/cli.py | argparse | argparse | 213 |
| src/tts/recover.py | json | json | 18 |
| src/tts/recover.py | os | os | 19 |
| src/tts/recover.py | sys | sys | 20 |
| src/tts/recover.py | time | time | 21 |
| src/tts/recover.py | pathlib | Path | 22 |
| src/tts/recover.py | requests | requests | 24 |
| src/tts/recover.py | wavespeed | wavespeed | 25 |
| src/unwanted_from_the_project_dir/main.py | pdfslicer.pdf_splitter | run_splitter | 1 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | argparse | argparse | 20 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | os | os | 21 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | re | re | 22 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | sys | sys | 23 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | logging | logging | 24 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pathlib | Path | 25 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | typing | List, Tuple, Optional, Dict, Any | 26 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | fitz | fitz | 153 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pdfplumber | pdfplumber | 197 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pdfminer.high_level | extract_text_to_fp | 270 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pdfminer.layout | LAParams | 271 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | io | io | 272 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | fitz | fitz | 316 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pdf2image | convert_from_path | 353 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pytesseract | pytesseract | 354 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | anthropic | anthropic | 396 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | json | json | 397 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | fitz | fitz | 460 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pdf2image | convert_from_path | 472 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pytesseract | pytesseract | 473 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | fitz | fitz | 488 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | pdfplumber | pdfplumber | 496 |
| src/unwanted_from_the_project_dir/pdf_splitter_copy1.py | fitz | fitz | 577 |
| src/unwanted_from_the_project_dir/splitter_V1.py | argparse | argparse | 15 |
| src/unwanted_from_the_project_dir/splitter_V1.py | fitz | fitz | 16 |
| src/unwanted_from_the_project_dir/splitter_V1.py | pytesseract | pytesseract | 17 |
| src/unwanted_from_the_project_dir/splitter_V1.py | pdf2image | convert_from_path | 18 |
| src/unwanted_from_the_project_dir/splitter_V1.py | os | os | 19 |
| src/unwanted_from_the_project_dir/splitter_V1.py | re | re | 20 |
| src/unwanted_from_the_project_dir/splitter_V1.py | sys | sys | 21 |
| src/unwanted_from_the_project_dir/splitter_V1.py | logging | logging | 22 |
| src/unwanted_from_the_project_dir/splitter_V1.py | pathlib | Path | 23 |
| src/util/normalize.py | re | re | 1 |

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

### src/endpoints/podcast_types.py::PodcastResult.ok
```python
def ok(self)
    # Line: 21
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

### src/engines/protocols.py::ScriptEngine.generate
```python
def generate(self, pdf_path: Path, context: str | None, fiction_dir: Path | None)
    # Line: 7
```

### src/engines/protocols.py::AudioEngine.generate
```python
def generate(self, script_path: Path, audio_dir: Path, mode: str)
    # Line: 18
```

### src/engines/protocols.py::SplitterEngine.split
```python
def split(self, book_pdf: Path, toc_page: int | None, output_dir: Path, no_ocr: bool)
    # Line: 29
```

### src/engines/wavespeed_audio.py::WaveSpeedAudioEngine.__init__
```python
def __init__(self, speakers: dict[str, Any] | None)
    # Line: 12
```

### src/engines/wavespeed_audio.py::WaveSpeedAudioEngine.generate
```python
def generate(self, script_path: Path, audio_dir: Path, mode: str)
    # Line: 15
    # Raises: RuntimeError
    # Env vars: WAVESPEED_API_KEY
    # Calls: os.environ.get, RuntimeError, audio_dir.mkdir, self._resolve_speakers, tts.cli.main
```

### src/engines/wavespeed_audio.py::WaveSpeedAudioEngine._resolve_speakers
```python
def _resolve_speakers(self, mode: str)
    # Line: 34
    # Calls: get, config.load_config, cfg_speakers.get, cfg_speakers.get, cfg_speakers.get
```

### src/fiction/seed_gen/cli.py::load_templates
```python
def load_templates()
    # Line: 24
    # Raises: FileNotFoundError
    # Calls: exists, FileNotFoundError, read_text
```

### src/fiction/seed_gen/cli.py::truncate_pdf_text
```python
def truncate_pdf_text(text: str)
    # Line: 34
    # Calls: len, print, len
```

### src/fiction/seed_gen/cli.py::parse_args
```python
def parse_args()
    # Line: 41
    # Calls: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args
```

### src/fiction/seed_gen/cli.py::_format_templates
```python
def _format_templates(templates: dict[str, str])
    # Line: 48
    # Calls: join, templates.items
```

### src/fiction/seed_gen/cli.py::build_pass1_prompt
```python
def build_pass1_prompt(templates: dict[str, str])
    # Line: 54
    # Calls: read_text, prompt.replace, _format_templates
```

### src/fiction/seed_gen/cli.py::validate_pass1_response
```python
def validate_pass1_response(response: str)
    # Line: 59
    # Raises: ValueError
    # Calls: re.search, print, print, print, ValueError
```

### src/fiction/seed_gen/cli.py::_prompt_field
```python
def _prompt_field(prompt: str, validator, max_retries: int)
    # Line: 71
    # Calls: range, strip, input, validator, print
```

### src/fiction/seed_gen/cli.py::_parse_concept_list
```python
def _parse_concept_list(pass1_response: str)
    # Line: 81
    # Calls: re.search, lstrip, l.strip, splitlines, strip
```

### src/fiction/seed_gen/cli.py::collect_user_plan
```python
def collect_user_plan(pass1_response: str)
    # Line: 89
    # Calls: _parse_concept_list, re.findall, max, int, print
```

### src/fiction/seed_gen/cli.py::write_config_toml
```python
def write_config_toml(output_dir: Path)
    # Line: 235
    # Calls: write_text
```

### src/fiction/seed_gen/cli.py::_format_user_plan
```python
def _format_user_plan(user_plan: dict)
    # Line: 239
    # Calls: join
```

### src/fiction/seed_gen/cli.py::build_pass2_prompt
```python
def build_pass2_prompt(user_plan: dict, pass1_response: str, templates: dict[str, str])
    # Line: 250
    # Calls: read_text, replace, replace, prompt.replace, _format_user_plan
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

### src/novel_pipeline/config.py::_validate_numerics
```python
def _validate_numerics(cfg: dict)
    # Line: 177
    # Docstring: M2: Sanity-check numeric fields. Raise ConfigError on bad combinations....
    # Raises: exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError
    # Calls: exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError
```

### src/novel_pipeline/config.py::_validate_formats
```python
def _validate_formats(cfg: dict)
    # Line: 254
    # Docstring: M2: Sanity-check format strings have the required placeholders....
    # Raises: exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError
    # Calls: exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, exceptions.ConfigError, isinstance
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

### src/novel_pipeline/cost.py::estimate_cost
```python
def estimate_cost(prompt_tokens: int, expected_output_tokens: int, config: dict)
    # Line: 34
    # Docstring: Return estimated USD cost for one call given configured per-1M prices....
    # Calls: float, float
```

### src/novel_pipeline/cost.py::_atomic_write_json
```python
def _atomic_write_json(path: Path, data: dict)
    # Line: 47
    # Calls: path.parent.mkdir, tempfile.mkstemp, str, os.fdopen, json.dump
```

### src/novel_pipeline/cost.py::_load_spend
```python
def _load_spend(path: Path)
    # Line: 66
    # Calls: path.exists, isoformat, datetime.datetime.now, path.open, json.load
```

### src/novel_pipeline/cost.py::track_spend
```python
def track_spend(amount: float, config: dict, note: str)
    # Line: 92
    # Docstring: Append a spend entry and return current totals.

Returns: {"session_total": float, "lifetime_total":...
    # Calls: pathlib.Path, config.get, _load_spend, float, data.get
```

### src/novel_pipeline/cost.py::current_totals
```python
def current_totals(config: dict)
    # Line: 129
    # Docstring: Read current totals without modifying anything....
    # Calls: pathlib.Path, config.get, _load_spend, float, data.get
```

### src/novel_pipeline/cost.py::reset_session_spend
```python
def reset_session_spend()
    # Line: 139
    # Docstring: Used by tests; resets the in-process session accumulator....
```

### src/novel_pipeline/docs.py::_utc_timestamp
```python
def _utc_timestamp()
    # Line: 32
    # Docstring: Compact UTC timestamp suitable for filenames: 20260515T142301Z....
    # Calls: strftime, datetime.datetime.now
```

### src/novel_pipeline/docs.py::_next_non_colliding
```python
def _next_non_colliding(parent: Path, render)
    # Line: 37
    # Docstring: Given a `render(suffix_index: int | None) -> str` callable that
produces a candidate filename for a ...
    # Calls: render, candidate.exists, render, candidate.exists
```

### src/novel_pipeline/docs.py::_format_with_collision_suffix
```python
def _format_with_collision_suffix(base_name: str, suffix_index: int | None)
    # Line: 52
    # Docstring: Apply a collision suffix to a rendered filename.

The suffix is inserted before the file extension (...
    # Calls: base_name.rpartition, ext.isalnum, len
```

### src/novel_pipeline/docs.py::_atomic_write
```python
def _atomic_write(path: Path, content: str)
    # Line: 74
    # Docstring: Write `content` to `path` atomically: tmp + fsync + os.replace....
    # Calls: path.parent.mkdir, tempfile.mkstemp, str, os.fdopen, f.write
```

### src/novel_pipeline/docs.py::_load_docx
```python
def _load_docx(path: Path)
    # Line: 100
    # Raises: exceptions.DocumentLoadError, exceptions.DocumentLoadError
    # Calls: exceptions.DocumentLoadError, docx.Document, str, exceptions.DocumentLoadError, join
```

### src/novel_pipeline/docs.py::load_static_docs
```python
def load_static_docs(paths: list[str])
    # Line: 115
    # Docstring: Load template files once. Returns {filename_without_ext: content}....
    # Raises: FileNotFoundError, exceptions.DocumentLoadError, ValueError, exceptions.DocumentLoadError, exceptions.DocumentLoadError, exceptions.DocumentLoadError
    # Calls: pathlib.Path, path.exists, FileNotFoundError, path.resolve, path.suffix.lower
```

### src/novel_pipeline/docs.py::load_living_doc
```python
def load_living_doc(path: str)
    # Line: 159
    # Docstring: Load the mutable living doc. Missing → empty string + warning log....
    # Raises: exceptions.DocumentLoadError
    # Calls: pathlib.Path, p.exists, logging_.log_event, str, p.read_text
```

### src/novel_pipeline/docs.py::save_living_doc
```python
def save_living_doc(path: str, content: str, config: dict | None)
    # Line: 172
    # Docstring: Atomic save with indefinite backup retention.

I7: backup file naming format is configurable via
`li...
    # Raises: ValueError
    # Calls: content.strip, ValueError, cfg.get, pathlib.Path, p.exists
```

### src/novel_pipeline/docs.py::render
```python
def render(suffix_index)
    # Line: 194
    # Calls: backup_fmt.format, _format_with_collision_suffix
```

### src/novel_pipeline/docs.py::save_chapter_draft
```python
def save_chapter_draft(output_dir: str, chapter_num: int, content: str, config: dict | None)
    # Line: 210
    # Docstring: Write a draft chapter to the .rejected/ staging directory.

I8: filename format is configurable via ...
    # Raises: ValueError
    # Calls: content.strip, ValueError, cfg.get, pathlib.Path, rejected.mkdir
```

### src/novel_pipeline/docs.py::render
```python
def render(suffix_index)
    # Line: 234
    # Calls: name_fmt.format, _format_with_collision_suffix
```

### src/novel_pipeline/docs.py::promote_chapter
```python
def promote_chapter(draft_path: str, output_dir: str, chapter_num: int, config: dict | None)
    # Line: 247
    # Docstring: Move an approved draft from .rejected/ to canonical chapter_NN.md.

M1: if the target already exists...
    # Raises: FileNotFoundError, exceptions.PromotionCollisionError
    # Calls: pathlib.Path, src.exists, FileNotFoundError, cfg.get, pathlib.Path
```

### src/novel_pipeline/docs.py::find_unpromoted_drafts
```python
def find_unpromoted_drafts(output_dir: str, chapter_num: int)
    # Line: 297
    # Docstring: H7: list .rejected/ files matching this chapter, newest first.

Used on resume to surface unpromoted...
    # Calls: pathlib.Path, rejected.exists, rejected.iterdir, p.is_file, p.name.startswith
```

### src/novel_pipeline/docs.py::validate_living_doc_structure
```python
def validate_living_doc_structure(content: str, required_sections: list[str])
    # Line: 317
    # Docstring: Check that all required section headers appear, in order.

Substring match (case-sensitive) on a lin...
    # Calls: content.splitlines, enumerate, problems.append, problems.append, len
```

### src/novel_pipeline/docs.py::build_living_doc_diff
```python
def build_living_doc_diff(old: str, new: str, context_lines: int)
    # Line: 349
    # Docstring: Unified diff of old vs new living doc, for surfacing to humans on
validation failure....
    # Calls: difflib.unified_diff, old.splitlines, new.splitlines, join
```

### src/novel_pipeline/exceptions.py::LivingDocValidationError.__init__
```python
def __init__(self, message: str, missing: list[str] | None, diff: str | None)
    # Line: 32
    # Calls: __init__, super
```

### src/novel_pipeline/logging_.py::configure
```python
def configure(log_path: str)
    # Line: 18
    # Docstring: Set the log file path. Called once at startup from load_config consumers....
    # Calls: pathlib.Path
```

### src/novel_pipeline/logging_.py::log_event
```python
def log_event(event: str, data: dict | None)
    # Line: 24
    # Docstring: Write one JSONL line. Never raises....
    # Calls: isoformat, datetime.datetime.now, record.update, json.dumps, print
```

### src/novel_pipeline/prompt.py::prompt_user
```python
def prompt_user(chapter_num: int, draft_text: str)
    # Line: 1
    # Raises: KeyboardInterrupt
    # Calls: print, lower, strip, input
```

### src/novel_pipeline/prompts.py::_wrap
```python
def _wrap(name: str, content: str, open_format: str, close_format: str)
    # Line: 30
    # Docstring: Wrap `content` with config-driven open/close lines.

Placeholders in the formats:
  {name_upper}  up...
    # Calls: open_format.format, name.upper, name.lower, close_format.format, name.upper
```

### src/novel_pipeline/prompts.py::build_prompt
```python
def build_prompt(static_docs: dict[str, str], living_doc: str, task: str, extra: str, config: dict | None)
    # Line: 47
    # Docstring: Assemble the OpenRouter-compatible message list.

`task` must be "generate_chapter" or "update_livin...
    # Raises: ValueError
    # Calls: cfg.get, cfg.get, cfg.get, cfg.get, list
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

### src/novel_pipeline/state.py::_chapter_re
```python
def _chapter_re(config: dict | None)
    # Line: 40
    # Calls: cfg.get, re.compile
```

### src/novel_pipeline/state.py::list_canonical_chapters
```python
def list_canonical_chapters(output_dir: str, config: dict | None)
    # Line: 50
    # Docstring: Return sorted list of canonical chapter numbers present in output_dir.

I9: regex is config-driven, ...
    # Calls: pathlib.Path, p.exists, _chapter_re, p.iterdir, entry.is_file
```

### src/novel_pipeline/state.py::find_next_chapter_number
```python
def find_next_chapter_number(output_dir: str, config: dict | None)
    # Line: 69
    # Docstring: Return the first missing positive integer in the canonical chapter
sequence starting at 1....
    # Calls: set, list_canonical_chapters
```

### src/novel_pipeline/state.py::compute_gaps
```python
def compute_gaps(output_dir: str, config: dict | None)
    # Line: 80
    # Docstring: Return integers missing below the maximum present chapter number....
    # Calls: list_canonical_chapters, set, range, max
```

### src/novel_pipeline/state.py::_atomic_write_json
```python
def _atomic_write_json(path: Path, data: dict)
    # Line: 93
    # Calls: path.parent.mkdir, tempfile.mkstemp, str, os.fdopen, json.dump
```

### src/novel_pipeline/state.py::read_state
```python
def read_state(state_file_path: str)
    # Line: 112
    # Docstring: Read state file. None if missing. ResumeStateError on malformed JSON.

H7: `last_chapter_drafted` is...
    # Raises: exceptions.ResumeStateError, exceptions.ResumeStateError, exceptions.ResumeStateError
    # Calls: pathlib.Path, p.exists, p.open, json.load, exceptions.ResumeStateError
```

### src/novel_pipeline/state.py::write_state
```python
def write_state(state_file_path: str, last_chapter_promoted: int, last_chapter_living_doc_updated: int, last_chapter_drafted: int | None)
    # Line: 144
    # Docstring: Atomically write the state file.

H7: `last_chapter_drafted` is optional. When provided, it's persis...
    # Calls: isoformat, datetime.datetime.now, int, _atomic_write_json, pathlib.Path
```

### src/novel_pipeline/state.py::detect_resume_state
```python
def detect_resume_state(output_dir: str, state_file_path: str, config: dict | None)
    # Line: 171
    # Docstring: Cross-check filesystem against the state file.

Returns:
  {
    "next_chapter": int,
    "last_prom...
    # Raises: exceptions.ResumeStateError
    # Calls: list_canonical_chapters, read_state, exceptions.ResumeStateError, int, int
```

### src/novel_pipeline/tests/test_pipeline.py::reset_spend
```python
def reset_spend()
    # Line: 82
    # Docstring: Each test starts with a clean session spend counter....
    # Calls: novel_pipeline.cost.reset_session_spend, novel_pipeline.cost.reset_session_spend, pytest.fixture
```

### src/novel_pipeline/tests/test_pipeline.py::_make_config
```python
def _make_config(tmp_path: Path)
    # Line: 773
    # Docstring: Return a config dict suitable for testing call_api in isolation.

Carries enough defaults that the n...
    # Calls: str
```

### src/novel_pipeline/tests/test_pipeline.py::_session_setup
```python
def _session_setup(tmp_path)
    # Line: 1131
    # Docstring: Build a working project skeleton with a seed living doc and one
static template. Returns a config di...
    # Calls: static.write_text, living_doc.write_text, join, output_dir.mkdir, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestTokens.test_count_tokens_empty
```python
def test_count_tokens_empty(self)
    # Line: 94
    # Calls: novel_pipeline.tokens.count_tokens
```

### src/novel_pipeline/tests/test_pipeline.py::TestTokens.test_count_tokens_nonempty
```python
def test_count_tokens_nonempty(self)
    # Line: 97
    # Calls: novel_pipeline.tokens.count_tokens
```

### src/novel_pipeline/tests/test_pipeline.py::TestTokens.test_count_tokens_unknown_model_falls_back
```python
def test_count_tokens_unknown_model_falls_back(self)
    # Line: 101
    # Calls: novel_pipeline.tokens.count_tokens
```

### src/novel_pipeline/tests/test_pipeline.py::TestTokens.test_count_tokens_with_config_fallback_encoding
```python
def test_count_tokens_with_config_fallback_encoding(self)
    # Line: 106
    # Calls: novel_pipeline.tokens.count_tokens
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_loads_md
```python
def test_loads_md(self, tmp_path)
    # Line: 118
    # Calls: f.write_text, novel_pipeline.docs.load_static_docs, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_missing_file_raises
```python
def test_missing_file_raises(self, tmp_path)
    # Line: 124
    # Calls: pytest.raises, novel_pipeline.docs.load_static_docs, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_empty_file_raises
```python
def test_empty_file_raises(self, tmp_path)
    # Line: 128
    # Calls: f.write_text, pytest.raises, novel_pipeline.docs.load_static_docs, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_unsupported_extension_raises
```python
def test_unsupported_extension_raises(self, tmp_path)
    # Line: 134
    # Calls: f.write_text, pytest.raises, novel_pipeline.docs.load_static_docs, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_pdf_raises_with_hint
```python
def test_pdf_raises_with_hint(self, tmp_path)
    # Line: 140
    # Calls: f.write_bytes, pytest.raises, novel_pipeline.docs.load_static_docs, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_collision_raises
```python
def test_collision_raises(self, tmp_path)
    # Line: 146
    # Calls: d1.mkdir, d2.mkdir, f1.write_text, f2.write_text, pytest.raises
```

### src/novel_pipeline/tests/test_pipeline.py::TestLoadStaticDocs.test_utf8_decode_failure_raises
```python
def test_utf8_decode_failure_raises(self, tmp_path)
    # Line: 158
    # Calls: f.write_bytes, pytest.raises, novel_pipeline.docs.load_static_docs, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLivingDoc.test_load_missing_returns_empty
```python
def test_load_missing_returns_empty(self, tmp_path)
    # Line: 171
    # Calls: novel_pipeline.docs.load_living_doc, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLivingDoc.test_save_then_load_roundtrip
```python
def test_save_then_load_roundtrip(self, tmp_path)
    # Line: 175
    # Calls: novel_pipeline.docs.save_living_doc, str, novel_pipeline.docs.load_living_doc, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLivingDoc.test_save_empty_raises
```python
def test_save_empty_raises(self, tmp_path)
    # Line: 180
    # Calls: pytest.raises, novel_pipeline.docs.save_living_doc, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestLivingDoc.test_save_creates_backup_of_existing
```python
def test_save_creates_backup_of_existing(self, tmp_path)
    # Line: 184
    # Calls: novel_pipeline.docs.save_living_doc, str, novel_pipeline.docs.save_living_doc, str, list
```

### src/novel_pipeline/tests/test_pipeline.py::TestLivingDoc.test_save_keeps_all_backups_not_just_10
```python
def test_save_keeps_all_backups_not_just_10(self, tmp_path)
    # Line: 192
    # Calls: range, novel_pipeline.docs.save_living_doc, str, list, tmp_path.glob
```

### src/novel_pipeline/tests/test_pipeline.py::TestLivingDoc.test_save_uses_configured_backup_format
```python
def test_save_uses_configured_backup_format(self, tmp_path)
    # Line: 201
    # Calls: novel_pipeline.docs.save_living_doc, str, novel_pipeline.docs.save_living_doc, str, list
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_save_chapter_draft_goes_to_rejected
```python
def test_save_chapter_draft_goes_to_rejected(self, tmp_path)
    # Line: 216
    # Calls: novel_pipeline.docs.save_chapter_draft, str, pathlib.Path, p.name.startswith, p.read_text
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_save_empty_draft_raises
```python
def test_save_empty_draft_raises(self, tmp_path)
    # Line: 223
    # Calls: pytest.raises, novel_pipeline.docs.save_chapter_draft, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_save_chapter_draft_uses_configured_name_format
```python
def test_save_chapter_draft_uses_configured_name_format(self, tmp_path)
    # Line: 227
    # Calls: novel_pipeline.docs.save_chapter_draft, str, pathlib.Path, p.name.startswith, p.name.endswith
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_promote_moves_to_canonical
```python
def test_promote_moves_to_canonical(self, tmp_path)
    # Line: 236
    # Calls: novel_pipeline.docs.save_chapter_draft, str, novel_pipeline.docs.promote_chapter, str, pathlib.Path
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_promote_collision_now_raises
```python
def test_promote_collision_now_raises(self, tmp_path)
    # Line: 243
    # Calls: canonical.write_text, novel_pipeline.docs.save_chapter_draft, str, pytest.raises, novel_pipeline.docs.promote_chapter
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_promote_missing_draft_raises
```python
def test_promote_missing_draft_raises(self, tmp_path)
    # Line: 257
    # Calls: pytest.raises, novel_pipeline.docs.promote_chapter, str, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestDraftAndPromote.test_promote_uses_configured_canonical_format
```python
def test_promote_uses_configured_canonical_format(self, tmp_path)
    # Line: 261
    # Calls: novel_pipeline.docs.save_chapter_draft, str, novel_pipeline.docs.promote_chapter, str, pathlib.Path
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindUnpromotedDrafts.test_returns_empty_when_no_rejected_dir
```python
def test_returns_empty_when_no_rejected_dir(self, tmp_path)
    # Line: 270
    # Calls: novel_pipeline.docs.find_unpromoted_drafts, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindUnpromotedDrafts.test_returns_matching_drafts_newest_first
```python
def test_returns_matching_drafts_newest_first(self, tmp_path)
    # Line: 274
    # Calls: novel_pipeline.docs.save_chapter_draft, str, time.sleep, novel_pipeline.docs.save_chapter_draft, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindUnpromotedDrafts.test_ignores_other_chapter_numbers
```python
def test_ignores_other_chapter_numbers(self, tmp_path)
    # Line: 287
    # Calls: novel_pipeline.docs.save_chapter_draft, str, novel_pipeline.docs.save_chapter_draft, str, novel_pipeline.docs.find_unpromoted_drafts
```

### src/novel_pipeline/tests/test_pipeline.py::TestStructuralValidation.test_all_present_in_order
```python
def test_all_present_in_order(self)
    # Line: 306
    # Calls: join, novel_pipeline.docs.validate_living_doc_structure
```

### src/novel_pipeline/tests/test_pipeline.py::TestStructuralValidation.test_missing_section
```python
def test_missing_section(self)
    # Line: 321
    # Calls: novel_pipeline.docs.validate_living_doc_structure
```

### src/novel_pipeline/tests/test_pipeline.py::TestStructuralValidation.test_out_of_order
```python
def test_out_of_order(self)
    # Line: 327
    # Calls: join, novel_pipeline.docs.validate_living_doc_structure, any
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_unknown_task_raises
```python
def test_unknown_task_raises(self)
    # Line: 346
    # Calls: pytest.raises, novel_pipeline.prompts.build_prompt
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_order_is_fixed
```python
def test_order_is_fixed(self)
    # Line: 350
    # Calls: novel_pipeline.prompts.build_prompt, user.find, user.find, user.find, user.find
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_system_prompt_per_task
```python
def test_system_prompt_per_task(self)
    # Line: 370
    # Calls: novel_pipeline.prompts.build_prompt, novel_pipeline.prompts.build_prompt
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_empty_living_doc_marked_first_chapter
```python
def test_empty_living_doc_marked_first_chapter(self)
    # Line: 376
    # Calls: novel_pipeline.prompts.build_prompt
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_extra_static_docs_appended_alphabetised
```python
def test_extra_static_docs_appended_alphabetised(self)
    # Line: 380
    # Calls: novel_pipeline.prompts.build_prompt, user.find, user.find, user.find, user.find
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_system_prompt_can_be_overridden_via_config
```python
def test_system_prompt_can_be_overridden_via_config(self)
    # Line: 387
    # Calls: novel_pipeline.prompts.build_prompt, novel_pipeline.prompts.build_prompt
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_wrap_format_can_be_overridden_via_config
```python
def test_wrap_format_can_be_overridden_via_config(self)
    # Line: 398
    # Calls: novel_pipeline.prompts.build_prompt
```

### src/novel_pipeline/tests/test_pipeline.py::TestPrompts.test_static_doc_order_overridable_via_config
```python
def test_static_doc_order_overridable_via_config(self)
    # Line: 409
    # Calls: novel_pipeline.prompts.build_prompt, user.find, user.find
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_empty_dir_returns_1
```python
def test_empty_dir_returns_1(self, tmp_path)
    # Line: 424
    # Calls: novel_pipeline.state.find_next_chapter_number, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_nonexistent_dir_returns_1
```python
def test_nonexistent_dir_returns_1(self, tmp_path)
    # Line: 427
    # Calls: novel_pipeline.state.find_next_chapter_number, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_no_gaps_returns_n_plus_1
```python
def test_no_gaps_returns_n_plus_1(self, tmp_path)
    # Line: 430
    # Calls: write_text, novel_pipeline.state.find_next_chapter_number, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_gap_mid_sequence_returned
```python
def test_gap_mid_sequence_returned(self, tmp_path)
    # Line: 435
    # Calls: write_text, write_text, novel_pipeline.state.find_next_chapter_number, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_ignores_rejected
```python
def test_ignores_rejected(self, tmp_path)
    # Line: 440
    # Calls: mkdir, write_text, novel_pipeline.state.find_next_chapter_number, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_ignores_timestamped_duplicates
```python
def test_ignores_timestamped_duplicates(self, tmp_path)
    # Line: 447
    # Calls: write_text, write_text, novel_pipeline.state.find_next_chapter_number, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_list_and_gaps
```python
def test_list_and_gaps(self, tmp_path)
    # Line: 452
    # Calls: write_text, novel_pipeline.state.list_canonical_chapters, str, novel_pipeline.state.compute_gaps, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestFindNextChapter.test_custom_canonical_regex
```python
def test_custom_canonical_regex(self, tmp_path)
    # Line: 458
    # Calls: write_text, write_text, novel_pipeline.state.list_canonical_chapters, str, novel_pipeline.state.list_canonical_chapters
```

### src/novel_pipeline/tests/test_pipeline.py::TestStateFile.test_read_missing_returns_none
```python
def test_read_missing_returns_none(self, tmp_path)
    # Line: 474
    # Calls: novel_pipeline.state.read_state, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestStateFile.test_write_then_read_roundtrip
```python
def test_write_then_read_roundtrip(self, tmp_path)
    # Line: 477
    # Calls: novel_pipeline.state.write_state, str, novel_pipeline.state.read_state, str, data.get
```

### src/novel_pipeline/tests/test_pipeline.py::TestStateFile.test_write_with_last_chapter_drafted
```python
def test_write_with_last_chapter_drafted(self, tmp_path)
    # Line: 487
    # Calls: novel_pipeline.state.write_state, str, novel_pipeline.state.read_state, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestStateFile.test_old_state_without_drafted_still_readable
```python
def test_old_state_without_drafted_still_readable(self, tmp_path)
    # Line: 499
    # Calls: p.write_text, json.dumps, novel_pipeline.state.read_state, str, data.get
```

### src/novel_pipeline/tests/test_pipeline.py::TestStateFile.test_malformed_json_raises_resume_state_error
```python
def test_malformed_json_raises_resume_state_error(self, tmp_path)
    # Line: 516
    # Calls: p.write_text, pytest.raises, novel_pipeline.state.read_state, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestStateFile.test_missing_keys_raises
```python
def test_missing_keys_raises(self, tmp_path)
    # Line: 522
    # Calls: p.write_text, json.dumps, pytest.raises, novel_pipeline.state.read_state, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestDetectResumeState.test_consistent_state
```python
def test_consistent_state(self, tmp_path)
    # Line: 530
    # Calls: out.mkdir, write_text, novel_pipeline.state.write_state, str, novel_pipeline.state.detect_resume_state
```

### src/novel_pipeline/tests/test_pipeline.py::TestDetectResumeState.test_inconsistent_state
```python
def test_inconsistent_state(self, tmp_path)
    # Line: 548
    # Calls: out.mkdir, write_text, novel_pipeline.state.write_state, str, novel_pipeline.state.detect_resume_state
```

### src/novel_pipeline/tests/test_pipeline.py::TestDetectResumeState.test_chapters_present_but_no_state_file_raises
```python
def test_chapters_present_but_no_state_file_raises(self, tmp_path)
    # Line: 564
    # Calls: out.mkdir, write_text, pytest.raises, novel_pipeline.state.detect_resume_state, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestDetectResumeState.test_gaps_reported
```python
def test_gaps_reported(self, tmp_path)
    # Line: 572
    # Calls: out.mkdir, write_text, write_text, novel_pipeline.state.write_state, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_missing_file_raises
```python
def test_missing_file_raises(self, tmp_path)
    # Line: 599
    # Calls: pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_minimal_config_applies_defaults
```python
def test_minimal_config_applies_defaults(self, tmp_path)
    # Line: 603
    # Calls: p.write_text, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_missing_required_raises
```python
def test_missing_required_raises(self, tmp_path)
    # Line: 621
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_env_overrides
```python
def test_env_overrides(self, tmp_path, monkeypatch)
    # Line: 627
    # Calls: p.write_text, monkeypatch.setenv, monkeypatch.setenv, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_v2_default_sections_are_character_agnostic
```python
def test_v2_default_sections_are_character_agnostic(self)
    # Line: 636
    # Calls: join
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_context_limit_too_low
```python
def test_validation_context_limit_too_low(self, tmp_path)
    # Line: 644
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_chapters_per_session_zero
```python
def test_validation_chapters_per_session_zero(self, tmp_path)
    # Line: 651
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_price_zero_rejected
```python
def test_validation_price_zero_rejected(self, tmp_path)
    # Line: 658
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_temperature_out_of_range
```python
def test_validation_temperature_out_of_range(self, tmp_path)
    # Line: 673
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_bad_doc_wrap_format
```python
def test_validation_bad_doc_wrap_format(self, tmp_path)
    # Line: 680
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_bad_rejected_draft_format
```python
def test_validation_bad_rejected_draft_format(self, tmp_path)
    # Line: 687
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_validation_backoff_must_be_list
```python
def test_validation_backoff_must_be_list(self, tmp_path)
    # Line: 694
    # Calls: p.write_text, pytest.raises, novel_pipeline.config.load_config, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestConfig.test_temperature_passthrough
```python
def test_temperature_passthrough(self, tmp_path)
    # Line: 701
    # Calls: p.write_text, novel_pipeline.config.load_config, str, pytest.approx, pytest.approx
```

### src/novel_pipeline/tests/test_pipeline.py::TestCost.test_estimate_cost
```python
def test_estimate_cost(self)
    # Line: 721
    # Calls: novel_pipeline.cost.estimate_cost, pytest.approx
```

### src/novel_pipeline/tests/test_pipeline.py::TestCost.test_estimate_cost_fractional
```python
def test_estimate_cost_fractional(self)
    # Line: 725
    # Calls: novel_pipeline.cost.estimate_cost, pytest.approx
```

### src/novel_pipeline/tests/test_pipeline.py::TestCost.test_track_spend_persists
```python
def test_track_spend_persists(self, tmp_path)
    # Line: 728
    # Calls: str, novel_pipeline.cost.track_spend, pytest.approx, pytest.approx, novel_pipeline.cost.track_spend
```

### src/novel_pipeline/tests/test_pipeline.py::TestCost.test_lifetime_persists_across_session_reset
```python
def test_lifetime_persists_across_session_reset(self, tmp_path)
    # Line: 745
    # Calls: str, novel_pipeline.cost.track_spend, novel_pipeline.cost.reset_session_spend, novel_pipeline.cost.track_spend, pytest.approx
```

### src/novel_pipeline/tests/test_pipeline.py::FakeResponse.__init__
```python
def __init__(self, status_code, json_data, headers, text)
    # Line: 762
```

### src/novel_pipeline/tests/test_pipeline.py::FakeResponse.json
```python
def json(self)
    # Line: 769
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI._good_payload
```python
def _good_payload(self, content, finish_reason)
    # Line: 803
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_happy_path
```python
def test_happy_path(self, tmp_path)
    # Line: 809
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_payload_includes_max_tokens
```python
def test_payload_includes_max_tokens(self, tmp_path)
    # Line: 825
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_payload_includes_creativity_controls_when_set
```python
def test_payload_includes_creativity_controls_when_set(self, tmp_path)
    # Line: 843
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_payload_omits_creativity_controls_when_unset
```python
def test_payload_omits_creativity_controls_when_unset(self, tmp_path)
    # Line: 865
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_finish_reason_length_raises
```python
def test_finish_reason_length_raises(self, tmp_path)
    # Line: 884
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_finish_reason_content_filter_raises
```python
def test_finish_reason_content_filter_raises(self, tmp_path)
    # Line: 902
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_context_overflow_includes_breakdown
```python
def test_context_overflow_includes_breakdown(self, tmp_path)
    # Line: 920
    # Calls: _make_config, pytest.raises, novel_pipeline.api.call_api, str
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_cost_limit_enforced
```python
def test_cost_limit_enforced(self, tmp_path)
    # Line: 941
    # Calls: _make_config, pytest.raises, novel_pipeline.api.call_api
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_cost_limit_bypass
```python
def test_cost_limit_bypass(self, tmp_path)
    # Line: 952
    # Calls: _make_config, unittest.mock.patch, FakeResponse, self._good_payload, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_retry_on_429_then_success
```python
def test_retry_on_429_then_success(self, tmp_path)
    # Line: 968
    # Calls: _make_config, unittest.mock.patch, unittest.mock.patch, type, type
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_no_retry_on_401
```python
def test_no_retry_on_401(self, tmp_path)
    # Line: 990
    # Calls: _make_config, unittest.mock.patch, type, type, FakeResponse
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_missing_api_key_raises
```python
def test_missing_api_key_raises(self, tmp_path, monkeypatch)
    # Line: 1005
    # Calls: _make_config, monkeypatch.delenv, pytest.raises, novel_pipeline.api.call_api
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_malformed_response_raises
```python
def test_malformed_response_raises(self, tmp_path)
    # Line: 1017
    # Calls: _make_config, unittest.mock.patch, type, type, FakeResponse
```

### src/novel_pipeline/tests/test_pipeline.py::TestCallAPI.test_actual_cost_tracked
```python
def test_actual_cost_tracked(self, tmp_path)
    # Line: 1031
    # Calls: _make_config, unittest.mock.patch, type, type, FakeResponse
```

### src/novel_pipeline/tests/test_pipeline.py::TestRequestWrappers.test_request_chapter_too_short_raises
```python
def test_request_chapter_too_short_raises(self, tmp_path)
    # Line: 1064
    # Calls: _make_config, unittest.mock.patch, pytest.raises, novel_pipeline.requests_.request_chapter
```

### src/novel_pipeline/tests/test_pipeline.py::TestRequestWrappers.test_request_chapter_long_enough_passes
```python
def test_request_chapter_long_enough_passes(self, tmp_path)
    # Line: 1071
    # Calls: _make_config, unittest.mock.patch, novel_pipeline.requests_.request_chapter
```

### src/novel_pipeline/tests/test_pipeline.py::TestRequestWrappers.test_update_living_doc_validation_passes
```python
def test_update_living_doc_validation_passes(self, tmp_path)
    # Line: 1079
    # Calls: _make_config, unittest.mock.patch, novel_pipeline.requests_.request_living_doc_update
```

### src/novel_pipeline/tests/test_pipeline.py::TestRequestWrappers.test_update_living_doc_validation_fails
```python
def test_update_living_doc_validation_fails(self, tmp_path)
    # Line: 1090
    # Calls: _make_config, unittest.mock.patch, pytest.raises, novel_pipeline.requests_.request_living_doc_update
```

### src/novel_pipeline/tests/test_pipeline.py::TestAtomicity.test_no_tmp_files_after_save
```python
def test_no_tmp_files_after_save(self, tmp_path)
    # Line: 1110
    # Calls: novel_pipeline.docs.save_living_doc, str, list, tmp_path.glob
```

### src/novel_pipeline/tests/test_pipeline.py::TestAtomicity.test_state_write_no_tmp_leftover
```python
def test_state_write_no_tmp_leftover(self, tmp_path)
    # Line: 1116
    # Calls: novel_pipeline.state.write_state, str, list, tmp_path.glob
```

### src/novel_pipeline/tests/test_pipeline.py::TestC2FirstRunGuard.test_empty_living_doc_and_no_chapters_refuses
```python
def test_empty_living_doc_and_no_chapters_refuses(self, tmp_path, _session_setup)
    # Line: 1217
    # Calls: write_text, pathlib.Path, pytest.raises, novel_pipeline.session.run_session
```

### src/novel_pipeline/tests/test_pipeline.py::TestC3AutoApproveResumeRefuses.test_inconsistent_resume_under_auto_approve_aborts
```python
def test_inconsistent_resume_under_auto_approve_aborts(self, _session_setup)
    # Line: 1228
    # Calls: write_text, pathlib.Path, novel_pipeline.state.write_state, pytest.raises, novel_pipeline.session.run_session
```

### src/novel_pipeline/tests/test_pipeline.py::TestC4AutoApproveSkipGap.test_chapter_start_skipping_gap_under_auto_approve_aborts
```python
def test_chapter_start_skipping_gap_under_auto_approve_aborts(self, _session_setup)
    # Line: 1244
    # Calls: pytest.raises, novel_pipeline.session.run_session
```

### src/novel_pipeline/tests/test_pipeline.py::TestH2KeepOldStopsSession.test_keep_old_living_doc_stops_session
```python
def test_keep_old_living_doc_stops_session(self, _session_setup, monkeypatch)
    # Line: 1254
    # Raises: novel_pipeline.LivingDocValidationError
    # Calls: monkeypatch.setattr, monkeypatch.setattr, iter, monkeypatch.setattr, next
```

### src/novel_pipeline/tests/test_pipeline.py::TestH2KeepOldStopsSession.fake_request_chapter
```python
def fake_request_chapter(*a, **kw)
    # Line: 1266
```

### src/novel_pipeline/tests/test_pipeline.py::TestH2KeepOldStopsSession.fake_request_update
```python
def fake_request_update(*a, **kw)
    # Line: 1269
    # Raises: novel_pipeline.exceptions.LivingDocValidationError
    # Calls: novel_pipeline.exceptions.LivingDocValidationError
```

### src/novel_pipeline/tests/test_pipeline.py::TestM4RejectionLimitBounded.test_runaway_rejections_eventually_raise
```python
def test_runaway_rejections_eventually_raise(self, _session_setup, monkeypatch)
    # Line: 1290
    # Calls: monkeypatch.setattr, iter, monkeypatch.setattr, next, pytest.raises
```

### src/novel_pipeline/tests/test_pipeline.py::TestI15EOFAbortInPromptChoice.test_eof_picks_abort_key
```python
def test_eof_picks_abort_key(self, monkeypatch)
    # Line: 1308
    # Raises: EOFError
    # Calls: monkeypatch.setattr, novel_pipeline.session._prompt_choice
```

### src/novel_pipeline/tests/test_pipeline.py::TestI15EOFAbortInPromptChoice.raise_eof
```python
def raise_eof(*a, **k)
    # Line: 1312
    # Raises: EOFError
```

### src/novel_pipeline/tests/test_pipeline.py::TestI15EOFAbortInPromptChoice.test_eof_no_a_key_falls_back_to_last
```python
def test_eof_no_a_key_falls_back_to_last(self, monkeypatch)
    # Line: 1322
    # Raises: EOFError
    # Calls: monkeypatch.setattr, novel_pipeline.session._prompt_choice
```

### src/novel_pipeline/tests/test_pipeline.py::TestI15EOFAbortInPromptChoice.raise_eof
```python
def raise_eof(*a, **k)
    # Line: 1325
    # Raises: EOFError
```

### src/novel_pipeline/tests/test_pipeline.py::TestM5DryRunPlaceholderSized.test_dry_run_chapter_sized_to_expected_tokens
```python
def test_dry_run_chapter_sized_to_expected_tokens(self, _session_setup)
    # Line: 1337
    # Calls: novel_pipeline.session._build_dry_run_chapter, len
```

### src/novel_pipeline/tokens.py::_get_encoding
```python
def _get_encoding(model: str, fallback_encoding: str)
    # Line: 27
    # Docstring: Resolve a tiktoken encoder. Per-model first, fallback encoding next.

Raises whatever tiktoken raise...
    # Calls: tiktoken.encoding_for_model, tiktoken.get_encoding, functools.lru_cache
```

### src/novel_pipeline/tokens.py::_heuristic_token_count
```python
def _heuristic_token_count(text: str, chars_per_token: int)
    # Line: 41
    # Docstring: Coarse fallback when tiktoken is unavailable.

Uses configurable chars-per-token (default 4) which i...
    # Calls: len, max, max
```

### src/novel_pipeline/tokens.py::count_tokens
```python
def count_tokens(text: str, model: str, config: dict | None)
    # Line: 56
    # Docstring: Count tokens in `text` for `model`.

Uses tiktoken's model-specific encoding when available, otherwi...
    # Calls: cfg.get, int, cfg.get, _get_encoding, len
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

### src/podcast_script_generator/llm/test_all.py::_p
```python
def _p(*args, file)
    # Line: 25
    # Docstring: Drop-in print() replacement that doesn't trigger the print-grep....
    # Calls: out.write, join, str
```

### src/podcast_script_generator/llm/test_all.py::make_pdf
```python
def make_pdf(path: str, text: str)
    # Line: 39
    # Calls: fitz.open, doc.new_page, page.insert_text, doc.save, doc.close
```

### src/podcast_script_generator/llm/test_all.py::make_empty_pdf
```python
def make_empty_pdf(path: str)
    # Line: 47
    # Calls: fitz.open, doc.new_page, doc.save, doc.close
```

### src/podcast_script_generator/llm/test_all.py::check
```python
def check(name: str, cond: bool, extra: str)
    # Line: 58
    # Calls: _p, _p
```

### src/settings.py::PodcastSettings.__post_init__
```python
def __post_init__(self)
    # Line: 18
```

### src/settings.py::PodcastSettings._run_dir
```python
def _run_dir(self, base: Path)
    # Line: 28
```

### src/settings.py::PodcastSettings.script_path_for
```python
def script_path_for(self, pdf_path: Path)
    # Line: 31
    # Calls: self._run_dir
```

### src/settings.py::PodcastSettings.audio_dir_for
```python
def audio_dir_for(self, pdf_path: Path)
    # Line: 34
    # Calls: self._run_dir
```

### src/slicer/pdf_splitter.py::setup_logging
```python
def setup_logging(verbose: bool)
    # Line: 31
    # Calls: logging.basicConfig
```

### src/slicer/pdf_splitter.py::get_toc_from_bookmarks
```python
def get_toc_from_bookmarks(pdf_path: str, target_level: int)
    # Line: 36
    # Docstring: Stage 1: Try to get TOC from PDF's internal bookmarks....
    # Calls: fitz.open, doc.get_toc, doc.close, title.strip, int
```

### src/slicer/pdf_splitter.py::get_text_from_toc_page
```python
def get_text_from_toc_page(pdf_path: str, page_num: int)
    # Line: 56
    # Docstring: Stage 2: Extract raw text from a specific PDF page using PyMuPDF....
    # Calls: fitz.open, len, get_text, doc.load_page, doc.close
```

### src/slicer/pdf_splitter.py::get_ocr_text_from_toc_page
```python
def get_ocr_text_from_toc_page(pdf_path: str, page_num: int)
    # Line: 71
    # Docstring: Stage 3: Use OCR to extract text from image-based pages....
    # Calls: pdf2image.convert_from_path, pytesseract.image_to_string, text.strip, text.strip, logging.warning
```

### src/slicer/pdf_splitter.py::parse_toc_from_text
```python
def parse_toc_from_text(toc_text: str)
    # Line: 84
    # Docstring: Stage 2/3 parsing: Extract chapter titles and start pages from TOC text....
    # Calls: toc_text.splitlines, re.compile, re.compile, re.compile, line.strip
```

### src/slicer/pdf_splitter.py::_ocr_pages_text
```python
def _ocr_pages_text(pdf_path: str, first_page: int, last_page: int, dpi: int)
    # Line: 121
    # Docstring: OCR a range of pages and return combined text with [PDF PAGE N] markers....
    # Calls: pdf2image.convert_from_path, enumerate, pytesseract.image_to_string, parts.append, text.strip
```

### src/slicer/pdf_splitter.py::_get_total_pages
```python
def _get_total_pages(pdf_path: str)
    # Line: 131
    # Calls: fitz.open, len, doc.close
```

### src/slicer/pdf_splitter.py::_detect_page_offset
```python
def _detect_page_offset(sample_text: str, total_pages: int)
    # Line: 141
    # Docstring: Infer PDF_page minus printed_page from OCR'd sample pages.

Each block is prefixed [PDF PAGE N]. Sca...
    # Calls: re.split, len, int, ln.strip, text.splitlines
```

### src/slicer/pdf_splitter.py::_validate_toc
```python
def _validate_toc(toc: List[TocEntry], total_pages: int)
    # Line: 185
    # Docstring: Return True if TOC entries are spread plausibly across the PDF.

Fails when:
- All entries cluster w...
    # Calls: bool, max, min, max, len
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

### src/slicer/pdf_splitter.py::get_toc_from_content_scan
```python
def get_toc_from_content_scan(pdf_path: str)
    # Line: 340
    # Docstring: Stage 5: scan page content for part/chapter headings.

Used when Stage 4 output fails validation and...
    # Calls: logging.warning, re.compile, fitz.open, len, logging.warning
```

### src/slicer/pdf_splitter.py::_normalize_title
```python
def _normalize_title(title: str)
    # Line: 401
    # Calls: title.lower, re.sub, strip, re.sub
```

### src/slicer/pdf_splitter.py::_titles_match
```python
def _titles_match(t1: str, t2: str)
    # Line: 408
    # Docstring: True if two titles are close enough to represent the same section....
    # Calls: _normalize_title, _normalize_title
```

### src/slicer/pdf_splitter.py::combine_llm_and_scan
```python
def combine_llm_and_scan(toc4: List[TocEntry], toc5: List[TocEntry], total_pages: int)
    # Line: 414
    # Docstring: Merge Stage 4 (rich titles, possibly wrong pages) with Stage 5 (verified positions).

For each Stage...
    # Calls: set, enumerate, _titles_match, used4.add, offsets.append
```

### src/slicer/pdf_splitter.py::filter_chapters_only
```python
def filter_chapters_only(toc: List[TocEntry])
    # Line: 465
    # Docstring: Keep only entries from Chapter 1 onward.
Drops front matter like Cover, Copyright, Dedication, Prefa...
    # Calls: enumerate, re.search, title.strip, logging.info, logging.warning
```

### src/slicer/pdf_splitter.py::sanitize_filename
```python
def sanitize_filename(title: str, max_length: int)
    # Line: 482
    # Docstring: Clean chapter title for use as a filename....
    # Calls: re.sub, re.sub, cleaned.strip
```

### src/slicer/pdf_splitter.py::extract_toc
```python
def extract_toc(pdf_path: str, toc_page_num: int, target_level: int, no_ocr: bool)
    # Line: 490
    # Docstring: Run the multi-stage TOC extraction pipeline. Returns (toc_list, source_name)....
    # Calls: get_toc_from_bookmarks, get_text_from_toc_page, parse_toc_from_text, get_ocr_text_from_toc_page, parse_toc_from_text
```

### src/slicer/pdf_splitter.py::_page_is_scanned
```python
def _page_is_scanned(doc: fitz.Document, page_idx: int)
    # Line: 551
    # Docstring: Return True if a page has no extractable text (image-only / scanned)....
    # Calls: strip, get_text
```

### src/slicer/pdf_splitter.py::_ocr_pages_to_pdf
```python
def _ocr_pages_to_pdf(pdf_path: str, first_page: int, last_page: int)
    # Line: 556
    # Docstring: Render pages to images, OCR each one, return a searchable fitz.Document.

first_page / last_page are...
    # Calls: pdf2image.convert_from_path, fitz.open, pytesseract.image_to_pdf_or_hocr, fitz.open, result_doc.insert_pdf
```

### src/slicer/pdf_splitter.py::split_pdf_by_chapters
```python
def split_pdf_by_chapters(pdf_path: str, chapters: List[TocEntry], output_dir: str, prefix: str, dry_run: bool, ocr_embed: bool)
    # Line: 571
    # Docstring: Split PDF into separate files based on chapter start pages.
Returns a list of metadata dicts for eac...
    # Calls: os.makedirs, fitz.open, len, enumerate, max
```

### src/slicer/pdf_splitter.py::run_splitter
```python
def run_splitter(input_path: str, toc_page: int, output_dir: str, prefix: str, level: int, no_ocr: bool, dry_run: bool, chapters_only: bool, verbose: bool, ocr_embed: bool)
    # Line: 650
    # Docstring: Orchestration-friendly entry point. Can be called directly from another Python script.

Returns a di...
    # Calls: setup_logging, os.path.exists, logging.error, logging.info, logging.info
```

### src/slicer/pdf_splitter.py::main
```python
def main()
    # Line: 712
    # Calls: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument
```

### src/tts/cli.py::read_script
```python
def read_script(file_path: str)
    # Line: 30
    # Docstring: Opens the script file and returns all the words inside as a single
block of text. This text is the `...
    # Raises: FileNotFoundError
    # Calls: pathlib.Path, path.exists, FileNotFoundError, path.read_text
```

### src/tts/cli.py::build_api_payload
```python
def build_api_payload(script: str, speakers: dict)
    # Line: 41
    # Docstring: Packages the script and voice choices into the exact JSON shape
WaveSpeed expects. The script text b...
    # Raises: ValueError
    # Env vars: WAVESPEED_SCALE
    # Calls: set, re.findall, config.load_config, float, os.environ.get
```

### src/tts/cli.py::send_to_api
```python
def send_to_api(payload: dict, api_key: str, output_folder: str | None)
    # Line: 77
    # Docstring: Submit to WaveSpeed, save request_id for recovery, poll with live progress.

Saves a tts_job.json fi...
    # Raises: podcast_script_generator.llm.exceptions.TTSSubmissionError, podcast_script_generator.llm.exceptions.TTSSubmissionError, podcast_script_generator.llm.exceptions.TTSSubmissionError, podcast_script_generator.llm.exceptions.TTSTimeoutError
    # Env vars: WAVESPEED_MODEL
    # Calls: pathlib.Path, config.load_config, os.environ.get, cfg.get, wavespeed.Client
```

### src/tts/cli.py::get_audio_url
```python
def get_audio_url(response: dict)
    # Line: 150
    # Docstring: Digs into the response and pulls out the first audio URL.
WaveSpeed returns an array, but for TTS we...
    # Raises: ValueError
    # Calls: response.get, isinstance, ValueError
```

### src/tts/cli.py::download_and_save
```python
def download_and_save(url: str, output_folder: str)
    # Line: 161
    # Docstring: Downloads the audio from the link and saves it into the folder
the user chose....
    # Raises: OSError, OSError
    # HTTP: Yes — requests/httpx call inside
    # Calls: pathlib.Path, out_dir.exists, OSError, os.access, OSError
```

### src/tts/cli.py::main
```python
def main(script_path: str, output_folder: str, api_key: str, speakers: dict)
    # Line: 192
    # Docstring: Calls each worker in order, passes results along, and returns the
final file path so the user sees w...
    # Calls: read_script, build_api_payload, send_to_api, get_audio_url, download_and_save
```

### src/tts/cli.py::cli_entrypoint
```python
def cli_entrypoint()
    # Line: 207
    # Docstring: Reads what the user typed, checks the required args exist, fills in
default voices for any speaker f...
    # Env vars: WAVESPEED_API_KEY
    # Calls: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, get
```

### src/tts/recover.py::poll_and_download
```python
def poll_and_download(request_id: str, output_folder: str, api_key: str)
    # Line: 28
    # Raises: RuntimeError, ValueError
    # HTTP: Yes — requests/httpx call inside
    # Calls: wavespeed.Client, pathlib.Path, out_dir.mkdir, print, print
```

### src/tts/recover.py::main
```python
def main()
    # Line: 84
    # Env vars: WAVESPEED_API_KEY
    # Calls: os.environ.get, print, sys.exit, len, pathlib.Path
```

### src/unwanted_from_the_project_dir/main.py::main
```python
def main()
    # Line: 5
    # Calls: print, pdfslicer.pdf_splitter.run_splitter, print
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::setup_logging
```python
def setup_logging(verbose: bool)
    # Line: 80
    # Calls: logging.basicConfig
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::sanitize_filename
```python
def sanitize_filename(title: str, max_length: int)
    # Line: 85
    # Calls: re.sub, re.sub, cleaned.strip
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::validate_toc
```python
def validate_toc(toc: List[TocEntry], total_pages: int)
    # Line: 92
    # Docstring: Remove entries with out-of-range page numbers and enforce monotonic order.
Logs a warning for every ...
    # Calls: logging.warning, logging.warning, valid.append, len, len
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::parse_toc_from_text
```python
def parse_toc_from_text(toc_text: str, source_label: str)
    # Line: 113
    # Docstring: Apply all improved regex patterns to raw text lines.
Returns list of TocEntry; empty list if nothing...
    # Calls: toc_text.splitlines, line.strip, PATTERN_CHAPTER_KEYWORD.match, PATTERN_DOTS.match, PATTERN_SPACES.match
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::stage1_bookmarks
```python
def stage1_bookmarks(pdf_path: str, target_level: int)
    # Line: 146
    # Docstring: Extract TOC from embedded PDF bookmarks at the requested level only.
If bookmarks exist but none are...
    # Calls: fitz.open, doc.get_toc, len, doc.close, logging.debug
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::stage2a_pdfplumber
```python
def stage2a_pdfplumber(pdf_path: str, toc_page_num: int)
    # Line: 189
    # Docstring: Use pdfplumber word bounding boxes to detect TOC entries geometrically.
The right-margin threshold i...
    # Calls: pdfplumber.open, len, page.extract_words, logging.debug, max
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::stage2b_pdfminer
```python
def stage2b_pdfminer(pdf_path: str, toc_page_num: int)
    # Line: 264
    # Docstring: Use pdfminer.six for character-level layout analysis on the TOC page,
then run the improved regex pa...
    # Calls: pdfminer.layout.LAParams, io.StringIO, open, pdfminer.high_level.extract_text_to_fp, strip
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::stage3_pymupdf_text
```python
def stage3_pymupdf_text(pdf_path: str, toc_page_num: int)
    # Line: 313
    # Docstring: Direct text extraction via PyMuPDF then improved regex parsing....
    # Calls: fitz.open, len, doc.close, get_text, doc.load_page
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::stage4_ocr
```python
def stage4_ocr(pdf_path: str, toc_page_num: int)
    # Line: 350
    # Docstring: Rasterise the TOC page and run Tesseract OCR, then improved regex....
    # Calls: pdf2image.convert_from_path, logging.debug, pytesseract.image_to_string, text.strip, logging.debug
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::stage5_llm
```python
def stage5_llm(pdf_path: str, toc_page_num: int)
    # Line: 390
    # Docstring: Send the raw TOC page text to Claude and ask it to return structured JSON.
Requires the 'anthropic' ...
    # Calls: _get_raw_toc_text, logging.warning, anthropic.Anthropic, client.messages.create, text.strip
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::_get_raw_toc_text
```python
def _get_raw_toc_text(pdf_path: str, toc_page_num: int)
    # Line: 457
    # Docstring: Try PyMuPDF then OCR to get raw page text for the LLM stage....
    # Calls: fitz.open, len, get_text, doc.load_page, doc.close
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::_get_total_pages
```python
def _get_total_pages(pdf_path: str)
    # Line: 485
    # Docstring: Return total page count using the first available library....
    # Calls: fitz.open, len, doc.close, pdfplumber.open, len
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::extract_toc
```python
def extract_toc(pdf_path: str, toc_page_num: int, target_level: int, no_ocr: bool, no_llm: bool)
    # Line: 508
    # Docstring: Run all TOC extraction stages in order, returning on the first success.
Returns (toc_list, stage_nam...
    # Calls: stage1_bookmarks, stage2a_pdfplumber, stage2b_pdfminer, stage3_pymupdf_text, stages.append
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::filter_chapters_only
```python
def filter_chapters_only(toc: List[TocEntry])
    # Line: 548
    # Docstring: Drop front matter (Cover, Copyright, Preface, etc.) and keep entries
from 'Chapter 1' / '1 Introduct...
    # Calls: enumerate, re.search, title.strip, logging.info, logging.warning
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::split_pdf_by_chapters
```python
def split_pdf_by_chapters(pdf_path: str, chapters: List[TocEntry], output_dir: str, prefix: str, dry_run: bool)
    # Line: 565
    # Docstring: Split PDF into per-chapter files. Returns metadata list for each file.
Pages before the first chapte...
    # Calls: os.makedirs, fitz.open, len, os.path.join, logging.info
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::run_splitter
```python
def run_splitter(input_path: str, toc_page: int, output_dir: str, prefix: str, level: int, no_ocr: bool, no_llm: bool, dry_run: bool, chapters_only: bool, verbose: bool)
    # Line: 657
    # Docstring: Orchestration-friendly entry point.

Returns a dict with:
    success    : bool
    source     : str...
    # Calls: setup_logging, os.path.exists, logging.error, logging.info, logging.info
```

### src/unwanted_from_the_project_dir/pdf_splitter_copy1.py::main
```python
def main()
    # Line: 723
    # Calls: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument
```

### src/unwanted_from_the_project_dir/splitter_V1.py::setup_logging
```python
def setup_logging(verbose)
    # Line: 32
    # Calls: logging.basicConfig
```

### src/unwanted_from_the_project_dir/splitter_V1.py::get_toc_from_bookmarks
```python
def get_toc_from_bookmarks(pdf_path, target_level)
    # Line: 39
    # Docstring: Stage 1: Try to get TOC from PDF's internal bookmarks....
    # Calls: fitz.open, doc.get_toc, doc.close, chapters.append, title.strip
```

### src/unwanted_from_the_project_dir/splitter_V1.py::get_text_from_toc_page
```python
def get_text_from_toc_page(pdf_path, page_num)
    # Line: 58
    # Docstring: Stage 2: Extract raw text from a specific PDF page using PyMuPDF....
    # Calls: fitz.open, len, doc.load_page, page.get_text, doc.close
```

### src/unwanted_from_the_project_dir/splitter_V1.py::get_ocr_text_from_toc_page
```python
def get_ocr_text_from_toc_page(pdf_path, page_num)
    # Line: 73
    # Docstring: Stage 3: Use OCR to extract text from image-based pages....
    # Calls: pdf2image.convert_from_path, pytesseract.image_to_string, text.strip, text.strip, logging.warning
```

### src/unwanted_from_the_project_dir/splitter_V1.py::parse_toc_from_text
```python
def parse_toc_from_text(toc_text)
    # Line: 85
    # Docstring: Stage 2/3 parsing: Extract chapter titles and start pages from TOC text.
Handles dot-leaders, space-...
    # Calls: toc_text.splitlines, re.compile, re.compile, re.compile, line.strip
```

### src/unwanted_from_the_project_dir/splitter_V1.py::get_toc_from_llm
```python
def get_toc_from_llm(fallback_text)
    # Line: 124
    # Docstring: Stage 4: LLM fallback (placeholder)....
    # Calls: logging.warning
```

### src/unwanted_from_the_project_dir/splitter_V1.py::sanitize_filename
```python
def sanitize_filename(title, max_length)
    # Line: 129
    # Docstring: Clean chapter title for use as a filename....
    # Calls: re.sub, re.sub, cleaned.strip, len
```

### src/unwanted_from_the_project_dir/splitter_V1.py::split_pdf_by_chapters
```python
def split_pdf_by_chapters(pdf_path, chapters, output_dir, prefix, dry_run)
    # Line: 138
    # Docstring: Split PDF into separate files based on chapter start pages....
    # Calls: logging.info, os.makedirs, fitz.open, len, enumerate
```

### src/unwanted_from_the_project_dir/splitter_V1.py::extract_toc
```python
def extract_toc(pdf_path, toc_page_num, target_level, no_ocr)
    # Line: 187
    # Docstring: Run the 4-stage TOC extraction pipeline....
    # Calls: get_toc_from_bookmarks, get_text_from_toc_page, parse_toc_from_text, get_ocr_text_from_toc_page, parse_toc_from_text
```

### src/unwanted_from_the_project_dir/splitter_V1.py::main
```python
def main()
    # Line: 227
    # Calls: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument
```

### src/util/normalize.py::normalize_speakers
```python
def normalize_speakers(text: str)
    # Line: 4
    # Docstring: Convert speaker label variants to clean 'Speaker N: content' lines for TTS.

WaveSpeed VibeVoice exp...
    # Calls: text.split, line.strip, s.startswith, re.sub, re.sub
```


## 4. Class Hierarchies

### ScriptMode
- File: src/endpoints/podcast_types.py
- Line: 6
- Bases: str, enum.Enum

### PodcastResult
- File: src/endpoints/podcast_types.py
- Line: 15
- Bases: object
  - ok() — line 21

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

### ScriptEngine
- File: src/engines/protocols.py
- Line: 6
- Bases: typing.Protocol
  - generate() — line 7

### AudioEngine
- File: src/engines/protocols.py
- Line: 17
- Bases: typing.Protocol
  - generate() — line 18

### SplitterEngine
- File: src/engines/protocols.py
- Line: 28
- Bases: typing.Protocol
  - split() — line 29

### WaveSpeedAudioEngine
- File: src/engines/wavespeed_audio.py
- Line: 9
- Bases: engines.protocols.AudioEngine
  - __init__() — line 12
  - generate() — line 15
  - _resolve_speakers() — line 34

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

### PodcastSettings
- File: src/settings.py
- Line: 7
- Bases: object
  - __post_init__() — line 18
  - _run_dir() — line 28
  - script_path_for() — line 31
  - audio_dir_for() — line 34


## 5. Transport/HTTP Call Sites

| File | Class | Function | Line | Env Vars |
|------|-------|----------|------|----------|
| src/novel_pipeline/api.py | - | call_api | 248 | OPENROUTER_URL |
| src/podcast_script_generator/llm/call_api.py | - | call_api | 62 | OPENROUTER_API_KEY |
| src/tts/cli.py | - | download_and_save | 161 | - |
| src/tts/recover.py | - | poll_and_download | 28 | - |

## 6. sys.path.insert & Runtime Path Hacks

| File | Lines | Code |
|------|-------|------|
| src/fiction/seed_gen/cli.py | 7 | `sys.path.insert(0, str(SRC / 'podcast_script_generator' / 'llm'))` |
| src/novel_pipeline/tests/test_pipeline.py | 41 | `sys.path.insert(0, str(Path(__file__).resolve().parent))` |
| src/podcast_script_generator/llm/test_all.py | 22 | `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` |
| src/slicer/pdf_splitter.py | 216 | `sys.path.insert(0, llm_dir)` |

## 7. Env Access Patterns

| File | Env Var | Line |
|------|---------|------|
| src/engines/wavespeed_audio.py | WAVESPEED_API_KEY | 24 |
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
| src/tts/cli.py | WAVESPEED_SCALE | 59 |
| src/tts/cli.py | WAVESPEED_MODEL | 90 |
| src/tts/cli.py | WAVESPEED_API_KEY | 237 |
| src/tts/recover.py | WAVESPEED_API_KEY | 85 |

## 8. Test Inventory

| Test File | Target | Notes |
|-----------|--------|-------|
| src/novel_pipeline/tests/test_pipeline.py | — | |
| src/podcast_script_generator/llm/test_all.py | — | |
