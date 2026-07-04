import os
from pathlib import Path

from config import load_config
from engines.llm_script import LLMScriptEngine
from engines.wavespeed_audio import WaveSpeedAudioEngine
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from format_adapters import get_splitter
from llm.env import resolve_from_env
from llm.factory import create_client


def _timeout_from_env() -> float | None:
    value = os.environ.get("OPENROUTER_TIMEOUT_SECONDS")
    if not value:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"OPENROUTER_TIMEOUT_SECONDS must be a float, got: {value!r}"
        ) from e


def _llm_client_kwargs() -> dict:
    cfg = load_config()
    kwargs = {
        "api_key": cfg.get("api_key"),
        "model": cfg.get("model"),
        "api_url": cfg.get("api_url"),
        "max_tokens": cfg.get("max_tokens"),
        "retry_after_override": cfg.get("retry_after_seconds"),
        **resolve_from_env(),  # env wins over config
    }
    timeout = _timeout_from_env()
    if timeout is not None:
        kwargs["timeout"] = timeout
    return kwargs


def default_llm_script_engine(mode: str = "2person") -> ScriptEngine:
    client = create_client(**_llm_client_kwargs())
    return LLMScriptEngine(mode=mode, llm=client)


def default_audio_engine(speakers: dict | None = None) -> AudioEngine:
    return WaveSpeedAudioEngine(speakers=speakers)


def default_splitter_engine(source: str | Path) -> SplitterEngine:
    splitter_cls = get_splitter(source)
    client = create_client(**_llm_client_kwargs())
    return splitter_cls(llm=client)
