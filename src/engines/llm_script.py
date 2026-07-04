from __future__ import annotations

import re
from pathlib import Path

from engines.protocols import ScriptEngine
from format_adapters import get_extractor
from llm.protocol import LLMClient


class LLMScriptEngine(ScriptEngine):
    """Adapter for the OpenRouter LLM script generator."""

    def __init__(self, mode: str = "2person", *, llm: LLMClient) -> None:
        self.mode = mode
        self.llm = llm

    def generate(
        self,
        source_path: Path,
        *,
        context: str | None = None,
        fiction_dir: Path | None = None,
    ) -> str:
        from podcast_script_generator.llm.read_prompt import read_prompt, resolve_prompt_path
        from util.normalize import normalize_speakers

        extractor = get_extractor(source_path)
        pdf_text = extractor(source_path)
        fiction_content = self._resolve_fiction_content(source_path, fiction_dir)
        prompt = read_prompt(resolve_prompt_path(self.mode), context, fiction_content)

        if self.mode == "fiction_meta":
            prompt = prompt.replace("{TECHNICAL_CONTENT}", pdf_text)
            return normalize_speakers(self.llm.call(prompt))

        combined = f"{prompt}\n\n---\n\n{pdf_text}" if pdf_text else prompt

        return normalize_speakers(self.llm.call(combined))

    def _resolve_fiction_content(
        self, source_path: Path, fiction_dir: Path | None
    ) -> str | None:
        if self.mode != "fiction_meta":
            return None
        if fiction_dir is None:
            raise ValueError("mode 'fiction_meta' requires fiction_dir")
        if not fiction_dir.is_dir():
            raise ValueError(f"fiction directory not found: {fiction_dir}")
        match = re.match(r"^(\d+)", source_path.stem)
        if not match:
            raise ValueError(
                f"cannot extract chapter number from source stem: {source_path.stem}"
            )
        chapter_num = int(match.group(1))
        fiction_file = fiction_dir / f"chapter_{chapter_num:02d}.md"
        if not fiction_file.exists():
            candidates = sorted(fiction_dir.glob(f"*{match.group(1)}*.md"))
            if not candidates:
                raise ValueError(
                    f"no fiction chapter found for chapter {chapter_num:02d} in {fiction_dir}"
                )
            fiction_file = candidates[0]
        return fiction_file.read_text(encoding="utf-8").strip()
