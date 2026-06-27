import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a .env file at module import time.
# DOTENV_PATH can be used to point at a specific env file.
load_dotenv(os.environ.get("DOTENV_PATH") or Path(__file__).resolve().parent.parent / ".env")


@dataclass
class PodcastSettings:
    """Path + behavior settings for the podcast pipeline."""

    root: Path = field(default_factory=lambda: Path(
        os.environ.get("HARNESS_ROOT", Path(__file__).parent)
    ))
    scripts_out: Path | None = None
    audio_out: Path | None = None
    chapters_dir: Path | None = None
    summary_out: Path | None = None
    mode: str = "2person"
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S_%f"))

    def __post_init__(self) -> None:
        if self.scripts_out is None:
            self.scripts_out = self.root / "data" / "output" / "scripts"
        if self.audio_out is None:
            self.audio_out = self.root / "data" / "output" / "audio"
        if self.chapters_dir is None:
            self.chapters_dir = self.root / "data" / "chapters"
        if self.summary_out is None:
            self.summary_out = self.root / "data" / "output" / "run_summary.txt"

    def _run_dir(self, base: Path) -> Path:
        return base / self.mode / self.run_id

    def script_path_for(self, pdf_path: Path) -> Path:
        return self._run_dir(self.scripts_out) / f"{pdf_path.stem}_podcast.txt"

    def audio_dir_for(self, pdf_path: Path) -> Path:
        return self._run_dir(self.audio_out) / pdf_path.stem
