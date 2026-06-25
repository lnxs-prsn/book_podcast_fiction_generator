"""Prompt construction for the two pipeline tasks.

Concatenation order is fixed by spec (default; configurable via
`static_doc_order` in config):
  world_laws → curriculum → style_contract → full_map → living_doc → task

Each doc is wrapped using `doc_wrap_open_format` /
`doc_wrap_close_format` from config. System prompts are pulled from
`system_prompt_generate_chapter` / `system_prompt_update_living_doc`.

I1, I2, I3: all wrap/order/system-prompt details come from config
(see novel_pipeline/config.py DEFAULTS for the defaults).
"""

from __future__ import annotations

from .config import (
    DEFAULT_STATIC_DOC_ORDER,
    DEFAULT_SYSTEM_PROMPT_GENERATE_CHAPTER,
    DEFAULT_SYSTEM_PROMPT_UPDATE_LIVING_DOC,
)


# Backwards-compatible module-level constants for tests/imports that
# still want the defaults directly.
SYSTEM_PROMPT_GENERATE_CHAPTER = DEFAULT_SYSTEM_PROMPT_GENERATE_CHAPTER
SYSTEM_PROMPT_UPDATE_LIVING_DOC = DEFAULT_SYSTEM_PROMPT_UPDATE_LIVING_DOC


def _wrap(
    name: str,
    content: str,
    open_format: str,
    close_format: str,
) -> str:
    """Wrap `content` with config-driven open/close lines.

    Placeholders in the formats:
      {name_upper}  uppercase name
      {name_lower}  lowercase name
    """
    open_line = open_format.format(name_upper=name.upper(), name_lower=name.lower())
    close_line = close_format.format(name_upper=name.upper(), name_lower=name.lower())
    return f"{open_line}\n{content}\n{close_line}\n\n"


def build_prompt(
    static_docs: dict[str, str],
    living_doc: str,
    task: str,
    extra: str = "",
    config: dict | None = None,
) -> list[dict]:
    """Assemble the OpenRouter-compatible message list.

    `task` must be "generate_chapter" or "update_living_doc".
    `extra` is appended after the living doc (used to inject the task
    instruction and, for update_living_doc, the just-written chapter).
    `config` carries system prompts, wrap formats, and the static-doc order
    overrides. If omitted, hardcoded defaults are used (preserves the older
    call signature for tests).
    """
    cfg = config or {}

    system_generate = cfg.get(
        "system_prompt_generate_chapter", DEFAULT_SYSTEM_PROMPT_GENERATE_CHAPTER
    )
    system_update = cfg.get(
        "system_prompt_update_living_doc", DEFAULT_SYSTEM_PROMPT_UPDATE_LIVING_DOC
    )
    open_fmt = cfg.get("doc_wrap_open_format", "=== {name_upper} ===")
    close_fmt = cfg.get("doc_wrap_close_format", "=== END {name_upper} ===")
    static_order = list(cfg.get("static_doc_order", DEFAULT_STATIC_DOC_ORDER))

    if task == "generate_chapter":
        system = system_generate
    elif task == "update_living_doc":
        system = system_update
    else:
        raise ValueError(
            f"unknown task: {task!r} "
            f"(expected 'generate_chapter' or 'update_living_doc')"
        )

    parts: list[str] = []
    for key in static_order:
        if key in static_docs:
            parts.append(_wrap(key, static_docs[key], open_fmt, close_fmt))

    # Any extra static docs the user supplied that aren't in the canonical
    # order get appended after the known ones, alphabetised for determinism.
    extras_in_static = sorted(set(static_docs) - set(static_order))
    for key in extras_in_static:
        parts.append(_wrap(key, static_docs[key], open_fmt, close_fmt))

    # Living doc — may be empty on first run.
    # Not wrapped with the generic envelope: the living doc already opens with
    # === LIVING DOCUMENT === so adding === LIVING_DOC === on top confuses the
    # model into echoing the outer wrapper instead of the inner format.
    living_content = living_doc if living_doc.strip() else "(empty — first chapter)"
    parts.append(f"{living_content.rstrip()}\n=== END LIVING DOCUMENT ===\n\n")

    if extra:
        parts.append(extra if extra.endswith("\n") else extra + "\n")

    user_content = "".join(parts).rstrip() + "\n"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]
