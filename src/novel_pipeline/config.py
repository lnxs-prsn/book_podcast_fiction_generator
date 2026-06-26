"""Config loading from TOML.

Required keys:
  model, static_doc_paths, living_doc_path, output_dir, context_limit,
  price_per_1m_input_tokens, price_per_1m_output_tokens

Env overrides are applied by the wiring origins via llm.env.resolve_from_env().

Configurable previously-hardcoded knobs (all have safe defaults; see
DEFAULTS dict below for the full list and the source-comment tags
(I1 / I2 / I4 / I5 / I7 / I8 / I9 / I13, M4, L1, L2, C1, H3) explaining
which audit item each one addresses).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .exceptions import ConfigError
from .logging_ import log_event


# Python 3.11+ has tomllib stdlib; fall back to tomli for 3.10.
# M3: wrap import with friendly error message.
if sys.version_info >= (3, 11):
    import tomllib as _toml
else:  # pragma: no cover
    try:
        import tomli as _toml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ConfigError(
            "Python < 3.11 requires the `tomli` package to read TOML config "
            "files. Install it with: pip install tomli"
        ) from e


REQUIRED_KEYS = (
    "model",
    "static_doc_paths",
    "living_doc_path",
    "output_dir",
    "context_limit",
    "price_per_1m_input_tokens",
    "price_per_1m_output_tokens",
)


# v2 patch: generic character-agnostic defaults. Project configs override.
DEFAULT_LIVING_DOC_SECTIONS = [
    "=== LIVING DOCUMENT ===",
    "--- CURRENT STATE ---",
    "--- ACTIVE VOCABULARY ---",
    "--- TERMS LEARNED BUT NOT YET OWNED ---",
    "--- TERMS INTRODUCED THIS ARC ---",
    "--- ACTIVE FORESHADOWING ---",
    "--- PROTAGONIST LENS ---",
    "--- NEXT CHAPTER TARGET ---",
    "--- NOTES FOR AI ---",
]


# I1: Default system prompts; user can override via config.
DEFAULT_SYSTEM_PROMPT_GENERATE_CHAPTER = (
    "You are a fiction-writing assistant working inside a strict pedagogical "
    "novel pipeline. The user has provided immutable reference documents "
    "(world bible, concept curriculum, style contract, full system-design map) "
    "and a mutable living document tracking the current state of the novel. "
    "Your job is to write the next chapter only. The chapter MUST be at least "
    "1500 words — this is a hard requirement. Write fully developed scenes "
    "with rich description, dialogue, and interiority until you reach that "
    "length. Do not summarise or cut scenes short. Follow the style contract "
    "exactly: declarative, physical-before-philosophical, "
    "experience-before-label. Respect the curriculum: introduce only the "
    "concepts scheduled for this chapter. Honor the living doc: continue from "
    "the exact state described, use only vocabulary the protagonist has "
    "earned, and execute the planned key event and emotional beat. Output the "
    "chapter text only — no preamble, no commentary, no meta-discussion. "
    "Begin with the chapter heading."
)

DEFAULT_SYSTEM_PROMPT_UPDATE_LIVING_DOC = (
    "You are a continuity-tracking assistant for a pedagogical novel pipeline. "
    "The user will provide the immutable reference documents, the current "
    "living document, and the chapter that was just written and approved. "
    "Your job is to produce an updated living document reflecting the new "
    "state after this chapter. Preserve the exact section headers and "
    "structure of the living document template. Increment touch counts for "
    "terms used. Move terms between sections as they earn higher status. "
    "Update CURRENT STATE, ACTIVE VOCABULARY, FORESHADOWING, LENS, and NEXT "
    "CHAPTER TARGET. Output the updated living document only — no preamble, "
    "no commentary, no diff, no explanation. Begin with the first line of the "
    "living doc."
)


# I3: spec-defined canonical order (user confirmed current is correct).
DEFAULT_STATIC_DOC_ORDER = ["world_laws", "curriculum", "style_contract", "full_map"]


# I13: dry-run placeholder building block. Repeated to size the placeholder
# to expected_output_tokens_chapter * tokenizer_chars_per_token chars (M5).
DEFAULT_DRY_RUN_CHAPTER_TEMPLATE = "Lorem ipsum dolor sit amet. "


DEFAULTS: dict = {
    # Session shape ----------------------------------------------------------
    "chapters_per_session": 3,
    "max_retries": 3,
    "timeout_seconds": 120,
    "min_chapter_words": 1500,
    "log_path": "./pipeline.log",
    "context_safety_margin": 8000,
    "cost_limit_usd_per_session": 5.00,
    "cost_limit_usd_total": 50.00,
    "expected_output_tokens_chapter": 4000,
    "expected_output_tokens_update": 2000,
    "required_living_doc_sections": DEFAULT_LIVING_DOC_SECTIONS,
    "state_file_path": "./.pipeline_state.json",  # v2 patch
    "spend_file_path": "./.pipeline_spend.json",

    # I1: System prompts (default values; override in TOML to customise).
    "system_prompt_generate_chapter": DEFAULT_SYSTEM_PROMPT_GENERATE_CHAPTER,
    "system_prompt_update_living_doc": DEFAULT_SYSTEM_PROMPT_UPDATE_LIVING_DOC,

    # I2: Document wrapping format (placeholders: {name_upper}, {name_lower}).
    "doc_wrap_open_format": "=== {name_upper} ===",
    "doc_wrap_close_format": "=== END {name_upper} ===",

    # I3: Static doc ordering (user confirmed this default is correct).
    "static_doc_order": DEFAULT_STATIC_DOC_ORDER,

    # I4: Tokenizer config.
    "tokenizer_encoding_fallback": "cl100k_base",
    "tokenizer_chars_per_token": 4,

    # I5: Retry backoff (used by api.py when Retry-After header is absent).
    "retry_backoff_seconds": [2, 8, 32],
    # L2: jitter upper bound, added to each backoff.
    "retry_jitter_seconds_max": 2.0,

    # I7: Living-doc backup name template. Placeholders: {name}, {ts}.
    "living_doc_backup_format": "{name}.bak.{ts}",

    # I8: Rejected-draft name format. Placeholders: {nn}, {ts}.
    "rejected_draft_name_format": "chapter_{nn:02d}__{ts}.md",

    # I9: Canonical chapter regex + filename format.
    "canonical_chapter_regex": r"^chapter_(\d{2,})\.md$",
    "canonical_chapter_name_format": "chapter_{nn:02d}.md",

    # I13: Dry-run placeholder template (used by session.py).
    "dry_run_chapter_template": DEFAULT_DRY_RUN_CHAPTER_TEMPLATE,

    # M4: Maximum rejection-retry iterations before giving up.
    "max_rejection_retries": 5,

    # L1: Optional creativity controls (only included in payload if set).
    # Leave at None to omit from API requests.
    "temperature": None,
    "top_p": None,
    "seed": None,

    # C1: Max-tokens to request from the API. Defaults to the expected
    # output sizes; explicit override allowed.
    "api_default_max_tokens_chapter": None,
    "api_default_max_tokens_update": None,

    # H3: Per-message and per-completion token overhead estimates.
    # Mirrors OpenAI's chat-template overhead: ~4 tokens per message
    # (role + separator markers) and ~3 tokens to prime the completion.
    "token_count_per_message_overhead": 4,
    "token_count_completion_priming": 3,
}


def _validate_numerics(cfg: dict) -> None:
    """M2: Sanity-check numeric fields. Raise ConfigError on bad combinations."""
    if cfg["context_limit"] <= cfg["context_safety_margin"] + 1000:
        raise ConfigError(
            f"context_limit ({cfg['context_limit']}) must be greater than "
            f"context_safety_margin ({cfg['context_safety_margin']}) + 1000. "
            f"Current margin leaves no room for any prompt."
        )
    if cfg["chapters_per_session"] < 1:
        raise ConfigError(
            f"chapters_per_session must be >= 1 (got {cfg['chapters_per_session']})"
        )
    if cfg["min_chapter_words"] < 1:
        raise ConfigError(
            f"min_chapter_words must be >= 1 (got {cfg['min_chapter_words']})"
        )
    if cfg["max_retries"] < 0:
        raise ConfigError(
            f"max_retries must be >= 0 (got {cfg['max_retries']})"
        )
    if cfg["timeout_seconds"] <= 0:
        raise ConfigError(
            f"timeout_seconds must be > 0 (got {cfg['timeout_seconds']})"
        )
    if cfg["price_per_1m_input_tokens"] <= 0:
        raise ConfigError(
            f"price_per_1m_input_tokens must be > 0 "
            f"(got {cfg['price_per_1m_input_tokens']})"
        )
    if cfg["price_per_1m_output_tokens"] <= 0:
        raise ConfigError(
            f"price_per_1m_output_tokens must be > 0 "
            f"(got {cfg['price_per_1m_output_tokens']})"
        )
    if cfg["cost_limit_usd_per_session"] <= 0:
        raise ConfigError(
            f"cost_limit_usd_per_session must be > 0 "
            f"(got {cfg['cost_limit_usd_per_session']})"
        )
    if cfg["cost_limit_usd_total"] <= 0:
        raise ConfigError(
            f"cost_limit_usd_total must be > 0 (got {cfg['cost_limit_usd_total']})"
        )
    if cfg["expected_output_tokens_chapter"] < 1:
        raise ConfigError(
            f"expected_output_tokens_chapter must be >= 1 "
            f"(got {cfg['expected_output_tokens_chapter']})"
        )
    if cfg["expected_output_tokens_update"] < 1:
        raise ConfigError(
            f"expected_output_tokens_update must be >= 1 "
            f"(got {cfg['expected_output_tokens_update']})"
        )
    if cfg["max_rejection_retries"] < 1:
        raise ConfigError(
            f"max_rejection_retries must be >= 1 (got {cfg['max_rejection_retries']})"
        )
    if cfg["tokenizer_chars_per_token"] < 1:
        raise ConfigError(
            f"tokenizer_chars_per_token must be >= 1 "
            f"(got {cfg['tokenizer_chars_per_token']})"
        )
    # Optional sampling-control sanity.
    if cfg.get("temperature") is not None:
        t = cfg["temperature"]
        if not (0.0 <= t <= 2.0):
            raise ConfigError(
                f"temperature must be in [0.0, 2.0] when set (got {t})"
            )
    if cfg.get("top_p") is not None:
        tp = cfg["top_p"]
        if not (0.0 < tp <= 1.0):
            raise ConfigError(
                f"top_p must be in (0.0, 1.0] when set (got {tp})"
            )


def _validate_formats(cfg: dict) -> None:
    """M2: Sanity-check format strings have the required placeholders."""
    # Wrap formats must have {name_upper} OR {name_lower}.
    for key in ("doc_wrap_open_format", "doc_wrap_close_format"):
        fmt = cfg[key]
        if "{name_upper}" not in fmt and "{name_lower}" not in fmt:
            raise ConfigError(
                f"{key} must contain {{name_upper}} or {{name_lower}} "
                f"(got {fmt!r})"
            )
    # Rejected draft format must have {nn} and {ts}.
    fmt = cfg["rejected_draft_name_format"]
    if "{nn" not in fmt or "{ts}" not in fmt:
        raise ConfigError(
            f"rejected_draft_name_format must contain {{nn}} and {{ts}} "
            f"(got {fmt!r})"
        )
    # Canonical chapter name format must have {nn}.
    fmt = cfg["canonical_chapter_name_format"]
    if "{nn" not in fmt:
        raise ConfigError(
            f"canonical_chapter_name_format must contain {{nn}} "
            f"(got {fmt!r})"
        )
    # Living-doc backup format must have {name} and {ts}.
    fmt = cfg["living_doc_backup_format"]
    if "{name}" not in fmt or "{ts}" not in fmt:
        raise ConfigError(
            f"living_doc_backup_format must contain {{name}} and {{ts}} "
            f"(got {fmt!r})"
        )
    # Static doc order must be a list of strings.
    order = cfg["static_doc_order"]
    if not isinstance(order, list) or not all(isinstance(s, str) for s in order):
        raise ConfigError(
            f"static_doc_order must be a list of strings (got {order!r})"
        )
    # Retry backoff must be a list of non-negative numbers.
    backoff = cfg["retry_backoff_seconds"]
    if (
        not isinstance(backoff, list)
        or not backoff
        or not all(isinstance(n, (int, float)) and n >= 0 for n in backoff)
    ):
        raise ConfigError(
            f"retry_backoff_seconds must be a non-empty list of "
            f"non-negative numbers (got {backoff!r})"
        )


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

    # Resolve relative paths in the config against the config file's directory
    # so the CLI can be invoked from any CWD.
    config_dir = p.parent.resolve()
    _path_keys = ("living_doc_path", "output_dir", "log_path", "state_file_path", "spend_file_path")
    for key in _path_keys:
        if key in cfg and cfg[key] and not Path(cfg[key]).is_absolute():
            cfg[key] = str((config_dir / cfg[key]).resolve())
    if "static_doc_paths" in cfg and isinstance(cfg["static_doc_paths"], list):
        cfg["static_doc_paths"] = [
            str((config_dir / s).resolve()) if s and not Path(s).is_absolute() else s
            for s in cfg["static_doc_paths"]
        ]

    # Required keys check.
    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        raise ConfigError(f"config missing required keys: {missing}")

    # Apply defaults for anything not specified.
    for k, default in DEFAULTS.items():
        cfg.setdefault(k, default)

    # Env overrides have moved to the wiring origins via llm.env.resolve_from_env().

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
