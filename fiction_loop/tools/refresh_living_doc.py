"""Bridge: approved chapter → request_living_doc_update() → living_document.md.

Usage (from project root):
  PYTHONPATH=src .venv/bin/python fiction_loop/tools/refresh_living_doc.py \\
    --chapter fiction_loop/chapters/chapter_001.md \\
    --config  fiction_loop/tools/pipeline_config.toml
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path


def _load_dotenv_fallback() -> None:
    """Minimal .env fallback: if repo-root .env exists, set any KEY=VALUE lines
    not already present in the environment (shell env always wins)."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v


_load_dotenv_fallback()

# ---------------------------------------------------------------------------
# src/ imports (PYTHONPATH=src required)
# ---------------------------------------------------------------------------
try:
    from novel_pipeline.config import load_config
    from novel_pipeline.requests_ import request_living_doc_update
    from novel_pipeline.exceptions import (
        LivingDocValidationError,
        APIResponseError,
        ContextOverflowError,
        CostLimitError,
        ConfigError,
    )
    from novel_pipeline.docs import load_static_docs, load_living_doc, save_living_doc
    from llm.factory import create_transport
    from llm.env import resolve_from_env
    from llm.exceptions import LLMConfigError
except ImportError as e:
    print(
        f"Import error: {e}\n"
        "Run with PYTHONPATH=src, e.g.:\n"
        "  PYTHONPATH=src .venv/bin/python fiction_loop/tools/refresh_living_doc.py ...",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="fiction_loop Living Doc refresh bridge")
    p.add_argument("--chapter", required=True, help="Path to approved chapter file")
    p.add_argument("--config",  required=True, help="Path to pipeline_config.toml")
    p.add_argument(
        "--ignore-cost-limit",
        action="store_true",
        default=False,
        help="Skip cost-limit enforcement",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    try:
        # 1. Load config
        try:
            config = load_config(args.config)
        except FileNotFoundError:
            print(f"Config not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        except ConfigError as e:
            print(f"Config error: {e}", file=sys.stderr)
            sys.exit(1)

        from novel_pipeline.logging_ import configure as _configure_log
        _configure_log(config["log_path"])

        # 2. Env overrides — env always wins (resolve_from_env only returns
        # non-empty values; filtering on `k in config` would drop api_key,
        # which the TOML never defines).
        env = resolve_from_env()
        config = {**config, **env}

        # 3. Build transport
        try:
            transport = create_transport(
                api_key=config.get("api_key"),
                model=config["model"],
                api_url=config.get("api_url"),
                max_retries=config["max_retries"],
                backoff_seconds=tuple(config["retry_backoff_seconds"]),
                jitter_max=config["retry_jitter_seconds_max"],
            )
        except LLMConfigError as e:
            print(
                f"LLM config error: {e}. Check OPENROUTER_API_KEY.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 4. Load static docs
        static_doc_paths = config.get("static_doc_paths") or []
        if static_doc_paths:
            static_docs = load_static_docs(static_doc_paths)
        else:
            # Fallback: load fiction_loop core docs relative to CWD
            static_docs = {
                "world_rules":    Path("fiction_loop/core/world_rules.md").read_text(encoding="utf-8"),
                "style_contract": Path("fiction_loop/core/style_contract.md").read_text(encoding="utf-8"),
                "curriculum":     Path("fiction_loop/core/concept_curriculum.md").read_text(encoding="utf-8"),
            }

        # 5. Load living doc
        living_doc_path = config["living_doc_path"]
        if not Path(living_doc_path).exists():
            print(
                f"living_document.md not found: {living_doc_path}",
                file=sys.stderr,
            )
            sys.exit(1)
        living_doc = load_living_doc(living_doc_path)
        # Strip the closing wrapper that build_prompt() injects so it cannot
        # accumulate across iterations if a model echoes it back into its output.
        living_doc = living_doc.rstrip()
        if living_doc.endswith("=== END LIVING DOCUMENT ==="):
            living_doc = living_doc[: -len("=== END LIVING DOCUMENT ===")].rstrip()

        # 6. Read chapter
        chapter_path = Path(args.chapter)
        if not chapter_path.exists():
            print(f"Chapter not found: {args.chapter}", file=sys.stderr)
            sys.exit(1)
        chapter_text = chapter_path.read_text(encoding="utf-8")

        # 6b. Inject authoritative state (owner decision F7): the state JSONs are
        # the source of truth for PROCESS STATE SUMMARY / POPULATION INDEX /
        # NEXT CHAPTER TARGET — the LLM must copy them, never infer from prose.
        state_dir = Path(living_doc_path).parent.parent / "state"
        state_block = ""
        for name in ("master_state.json", "process_state.json"):
            sp = state_dir / name
            if sp.exists():
                state_block += (
                    f"=== AUTHORITATIVE STATE: {name} ===\n"
                    f"{sp.read_text(encoding='utf-8')}\n"
                    f"=== END AUTHORITATIVE STATE: {name} ===\n\n"
                )
        if state_block:
            chapter_text = (
                state_block
                + "The PROCESS STATE SUMMARY, POPULATION INDEX, and NEXT CHAPTER "
                  "TARGET sections of the living document MUST be derived from the "
                  "authoritative state above, not inferred from the chapter prose.\n\n"
                + chapter_text
            )

        # 7. Call LLM to update living doc
        new_living = request_living_doc_update(
            static_docs,
            living_doc,
            chapter_text,
            config["model"],
            config,
            client=transport,
            timeout=config.get("timeout_seconds"),
            ignore_cost_limit=args.ignore_cost_limit,
        )

        # 8. Save (atomic write with backup)
        save_living_doc(living_doc_path, new_living, config)
        print("OK: living_document.md updated.", file=sys.stderr)
        sys.exit(0)

    except LivingDocValidationError as e:
        print(str(e), file=sys.stderr)
        if e.diff:
            print("\n--- diff ---", file=sys.stderr)
            print(e.diff, file=sys.stderr)
        sys.exit(1)
    except ContextOverflowError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except CostLimitError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except APIResponseError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print(f"Unexpected error:\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
