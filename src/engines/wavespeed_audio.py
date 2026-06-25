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
