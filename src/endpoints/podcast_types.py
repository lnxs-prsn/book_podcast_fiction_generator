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
