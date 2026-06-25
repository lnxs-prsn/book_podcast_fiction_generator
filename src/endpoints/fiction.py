from __future__ import annotations

from pathlib import Path
from typing import Callable

from llm.env import resolve_from_env
from llm.exceptions import LLMConfigError
from llm.factory import create_transport
from llm.protocol import LLMTransport

from novel_pipeline.config import load_config
from novel_pipeline.exceptions import ConfigError
from novel_pipeline.session import run_session, ApproveChapterFn, SessionResult


def run_novel_session(
    config_path: str | Path,
    client: LLMTransport | None = None,
    *,
    resume: bool = False,
    auto_approve: bool = False,
    dry_run: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: ApproveChapterFn | None = None,
) -> SessionResult:
    _raw_config = load_config(str(config_path))
    env = resolve_from_env()
    config = {**_raw_config, **{k: v for k, v in env.items() if k in _raw_config}}
    if approve_chapter is None:
        approve_chapter = lambda n, t: True

    if client is None:
        cfg_kwargs = {
            "api_key": config.get("api_key"),
            "model": config["model"],
            "api_url": config.get("api_url"),
            "max_retries": config["max_retries"],
            "backoff_seconds": tuple(config["retry_backoff_seconds"]),
            "jitter_max": config["retry_jitter_seconds_max"],
            "max_tokens": config.get("max_tokens"),
            "retry_after_override": config.get("retry_after_seconds"),
        }
        try:
            client = create_transport(**{**cfg_kwargs, **env})
        except LLMConfigError as e:
            raise ConfigError(str(e)) from e

    timeout = config.get("timeout_seconds")

    return run_session(
        config,
        client,
        timeout,
        resume=resume,
        auto_approve=auto_approve,
        dry_run=dry_run,
        chapter_start=chapter_start,
        ignore_cost_limit=ignore_cost_limit,
        approve_chapter=approve_chapter,
    )
