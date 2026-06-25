from config import load_config
from engines.llm_script import LLMScriptEngine
from engines.pdf_splitter import PDFSplitterEngine
from engines.wavespeed_audio import WaveSpeedAudioEngine
from engines.protocols import ScriptEngine, AudioEngine, SplitterEngine
from llm.env import resolve_from_env
from llm.factory import create_client


def default_llm_script_engine(mode: str = "2person") -> ScriptEngine:
    cfg = load_config()
    client = create_client(**{
        "api_key": cfg.get("api_key"),
        "model": cfg.get("model"),
        "api_url": cfg.get("api_url"),
        "max_tokens": cfg.get("max_tokens"),
        "retry_after_override": cfg.get("retry_after_seconds"),
        **resolve_from_env(),  # env wins over config
    })
    return LLMScriptEngine(mode=mode, llm=client)


def default_audio_engine(speakers: dict | None = None) -> AudioEngine:
    return WaveSpeedAudioEngine(speakers=speakers)


def default_splitter_engine() -> SplitterEngine:
    cfg = load_config()
    client = create_client(**{
        "api_key": cfg.get("api_key"),
        "model": cfg.get("model"),
        "api_url": cfg.get("api_url"),
        "max_tokens": cfg.get("max_tokens"),
        "retry_after_override": cfg.get("retry_after_seconds"),
        **resolve_from_env(),  # env wins over config
    })
    return PDFSplitterEngine(llm=client)
