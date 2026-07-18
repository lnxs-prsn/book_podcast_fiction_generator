"""Bridge: assembled_prompt.md → call_api() → chapter_draft.md.

Usage (from project root):
  PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py \\
    --prompt fiction_loop/prompts/assembled_prompt.md \\
    --config fiction_loop/tools/pipeline_config.toml \\
    --output fiction_loop/prompts/chapter_draft.md

Zero-token label check:
  PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py \\
    --check-labels fiction_loop/chapters/chapter_007.md

Structured prose check:
  PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py \\
    --check-prose fiction_loop/chapters/chapter_007.md
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
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
    from novel_pipeline.api import call_api
    from novel_pipeline.exceptions import (
        ContextOverflowError,
        CostLimitError,
        ChapterValidationError,
        APIResponseError,
        APIRateLimitError,
        ConfigError,
    )
    from llm.factory import create_transport
    from llm.env import resolve_from_env
    from llm.exceptions import LLMConfigError
except ImportError as e:
    print(
        f"Import error: {e}\n"
        "Run with PYTHONPATH=src, e.g.:\n"
        "  PYTHONPATH=src .venv/bin/python fiction_loop/tools/invoke_writer.py ...",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def build_messages(assembled_prompt: str, config: dict) -> list[dict]:
    return [
        {"role": "system", "content": config["system_prompt_generate_chapter"]},
        {"role": "user",   "content": assembled_prompt},
    ]


def validate_word_count(text: str, min_words: int) -> None:
    wc = len(text.split())
    if wc < min_words:
        raise ChapterValidationError(
            f"Chapter too short: {wc} words, minimum {min_words}. "
            f"First 200 chars: {text[:200]!r}"
        )


class LabelLeakError(Exception):
    """Raised when an internal failure-mode label leaks into narration."""


class RevisionOverreachError(Exception):
    """Raised when a targeted revision changes too much of the draft."""


REVISION_MAX_DIFF_RATIO = 0.25
PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("pipeline_config.toml")


def load_forbidden_labels(
    state_path: Path | None = None,
) -> tuple[str, ...]:
    """Load the book-specific failure-mode labels from process state."""
    if state_path is None:
        state_path = Path(__file__).resolve().parents[1] / "state" / "process_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    labels: set[str] = set()
    for operation in state["operations"].values():
        for field in ("failure_modes_shown", "failure_modes_not_yet_shown"):
            labels.update(
                label.strip()
                for label in operation.get(field, [])
                if isinstance(label, str) and label.strip()
            )
    return tuple(sorted(labels, key=str.casefold))


def _artifact_spans(line: str) -> list[tuple[int, int]]:
    """Return spans inside Markdown italic markers on a prose line."""
    content = line.strip()
    while content.startswith(">"):
        content = content[1:].lstrip()
    return [
        match.span(1)
        for match in re.finditer(r"(?<!\*)\*([^*\n]+)\*(?!\*)", content)
    ]


def _label_pattern(label: str) -> re.Pattern[str]:
    variants = [label]
    if label.casefold().startswith("the "):
        variants.append(label[4:])
    alternatives = "|".join(
        re.escape(variant) for variant in sorted(variants, key=len, reverse=True)
    )
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.IGNORECASE)


def validate_forbidden_labels(text: str) -> list[dict]:
    """Warn on artifact hits and return structured narration deficiencies."""
    labels = load_forbidden_labels()
    patterns = [(label, _label_pattern(label)) for label in labels]
    deficiencies: list[dict] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        content = line.strip()
        while content.startswith(">"):
            content = content[1:].lstrip()
        italic_spans = _artifact_spans(line)
        matches = [
            (label, match)
            for label, pattern in patterns
            if (match := pattern.search(content))
        ]
        if not matches:
            continue
        excerpt = line.strip()[:60]
        for label, match in matches:
            artifact = any(
                start <= match.start() and match.end() <= end
                for start, end in italic_spans
            )
            kind = "WARN artifact label" if artifact else "VIOLATION"
            report = (
                f"{kind}: line {line_number}: label {label!r}: {excerpt}"
            )
            print(report, file=sys.stderr)
            if kind == "VIOLATION":
                deficiencies.append({
                    "check": "forbidden_label",
                    "rule": "HARD RULE 1",
                    "line": line_number,
                    "detail": f"narration label {label!r}",
                    "excerpt": line.strip(),
                })
    return deficiencies


def check_forbidden_labels(text: str) -> None:
    """Preserve the original raise-on-violation label-check contract."""
    deficiencies = validate_forbidden_labels(text)
    if deficiencies:
        raise LabelLeakError(
            f"LabelLeakError: {len(deficiencies)} forbidden narration label "
            f"hit(s); internal planning labels must not appear in prose."
        )


def write_prose_deficiencies(text: str) -> list[dict]:
    """Run prose checks and write their shared transient report."""
    deficiencies = validate_forbidden_labels(text)
    path = PROMPTS_DIR / "prose_deficiencies.json"
    path.write_text(
        json.dumps(deficiencies, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return deficiencies


def revision_diff_ratio(original: str, revised: str) -> float:
    """Return the fraction of line slots changed by a revision."""
    original_lines = original.splitlines()
    revised_lines = revised.splitlines()
    denominator = max(len(original_lines), len(revised_lines), 1)
    changed = sum(
        max(i2 - i1, j2 - j1)
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, original_lines, revised_lines
        ).get_opcodes()
        if tag != "equal"
    )
    return changed / denominator


def build_revision_prompt(draft: str, deficiencies: list[dict]) -> str:
    """Render the fixed targeted-revision instruction and checklist."""
    checklist = "\n".join(
        f"- Line {item['line']} — {item['rule']} / {item['check']}: "
        f"{item['detail']}\n  Excerpt: {item['excerpt']}"
        for item in deficiencies
    )
    return (
        "# TARGETED REVISION\n\n"
        "Return the chapter unchanged EXCEPT for the flagged problems; "
        "correct ONLY those; do not rewrite, re-order, or re-invent anything "
        "else.\n\n## Correction checklist\n\n"
        f"{checklist}\n\n## Current draft\n\n{draft}"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="fiction_loop Writer bridge")
    p.add_argument("--prompt", help="Path to assembled_prompt.md")
    p.add_argument("--config", help="Path to pipeline_config.toml")
    p.add_argument("--output", help="Where to write chapter_draft.md")
    p.add_argument(
        "--check-labels",
        metavar="PATH",
        help="Check an existing chapter for forbidden planning labels; no API call",
    )
    p.add_argument("--check-prose", metavar="PATH",
                   help="Write structured prose deficiencies; no API call")
    p.add_argument("--revise", metavar="DRAFT",
                   help="Target-revise an existing draft")
    p.add_argument("--deficiencies", metavar="FILE",
                   help="Deficiency JSON for --revise")
    p.add_argument("--dry-run", action="store_true",
                   help="Write revision_prompt.md without an API call")
    p.add_argument(
        "--ignore-cost-limit",
        action="store_true",
        default=False,
        help="Skip cost-limit enforcement",
    )
    args = p.parse_args()
    modes = sum(bool(value) for value in
                (args.check_labels, args.check_prose, args.revise))
    if modes > 1:
        p.error("--check-labels, --check-prose, and --revise are mutually exclusive")
    if args.check_labels or args.check_prose:
        if any((args.prompt, args.config, args.output, args.deficiencies,
                args.dry_run, args.ignore_cost_limit)):
            mode = "--check-labels" if args.check_labels else "--check-prose"
            p.error(f"{mode} cannot be combined with generation arguments")
    elif args.revise:
        if not args.deficiencies:
            p.error("--revise requires --deficiencies")
        if any((args.prompt, args.output)):
            p.error("--revise cannot be combined with generation arguments")
    elif args.deficiencies or args.dry_run:
        p.error("--deficiencies and --dry-run require --revise")
    elif not all((args.prompt, args.config, args.output)):
        p.error("--prompt, --config, and --output are required for generation")
    return args


def main() -> None:
    args = parse_args()

    try:
        if args.check_labels:
            chapter_path = Path(args.check_labels)
            if not chapter_path.exists():
                print(f"Chapter not found: {chapter_path}", file=sys.stderr)
                sys.exit(1)
            check_forbidden_labels(chapter_path.read_text(encoding="utf-8"))
            print(f"OK: no forbidden narration labels → {chapter_path}", file=sys.stderr)
            sys.exit(0)

        if args.check_prose:
            chapter_path = Path(args.check_prose)
            if not chapter_path.exists():
                print(f"Chapter not found: {chapter_path}", file=sys.stderr)
                sys.exit(1)
            deficiencies = write_prose_deficiencies(
                chapter_path.read_text(encoding="utf-8")
            )
            if deficiencies:
                print(
                    f"LabelLeakError: {len(deficiencies)} prose deficiency "
                    f"record(s) → {PROMPTS_DIR / 'prose_deficiencies.json'}",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(f"OK: no prose deficiencies → "
                  f"{PROMPTS_DIR / 'prose_deficiencies.json'}", file=sys.stderr)
            sys.exit(0)

        if args.revise and args.dry_run:
            draft_path = Path(args.revise)
            deficiency_path = Path(args.deficiencies)
            if not draft_path.exists():
                print(f"Input not found at {draft_path}.", file=sys.stderr)
                sys.exit(1)
            if not deficiency_path.exists():
                print(f"Deficiencies not found: {deficiency_path}", file=sys.stderr)
                sys.exit(1)
            deficiencies = json.loads(deficiency_path.read_text(encoding="utf-8"))
            if not isinstance(deficiencies, list) or not deficiencies:
                print("Deficiencies must be a non-empty JSON list.", file=sys.stderr)
                sys.exit(1)
            revision_prompt_path = PROMPTS_DIR / "revision_prompt.md"
            revision_prompt_path.write_text(
                build_revision_prompt(
                    draft_path.read_text(encoding="utf-8"), deficiencies
                ),
                encoding="utf-8",
            )
            print(f"OK: revision prompt → {revision_prompt_path}", file=sys.stderr)
            sys.exit(0)

        # 1. Load config
        try:
            config = load_config(args.config or str(DEFAULT_CONFIG_PATH))
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
                f"LLM config error: {e}. Check BOOKGEN_LLM_API_KEY.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 4. Build the generation or targeted-revision prompt.
        prompt_path = Path(args.revise or args.prompt)
        if not prompt_path.exists():
            print(f"Input not found at {prompt_path}.", file=sys.stderr)
            sys.exit(1)
        original = prompt_path.read_text(encoding="utf-8")
        if args.revise:
            deficiency_path = Path(args.deficiencies)
            if not deficiency_path.exists():
                print(f"Deficiencies not found: {deficiency_path}", file=sys.stderr)
                sys.exit(1)
            deficiencies = json.loads(deficiency_path.read_text(encoding="utf-8"))
            if not isinstance(deficiencies, list) or not deficiencies:
                print("Deficiencies must be a non-empty JSON list.", file=sys.stderr)
                sys.exit(1)
            assembled = build_revision_prompt(original, deficiencies)
            revision_prompt_path = PROMPTS_DIR / "revision_prompt.md"
            revision_prompt_path.write_text(assembled, encoding="utf-8")
        else:
            assembled = original

        # 5. Build messages and call API
        messages = build_messages(assembled, config)
        chapter = call_api(
            messages,
            config["model"],
            config,
            client=transport,
            timeout=config.get("timeout_seconds"),
            expected_output_tokens=config.get("expected_output_tokens_chapter"),
            ignore_cost_limit=args.ignore_cost_limit,
            task_label="revise_chapter" if args.revise else "generate_chapter",
        )

        if args.revise:
            ratio = revision_diff_ratio(original, chapter)
            output_path = PROMPTS_DIR / "chapter_draft.md"
            if ratio > REVISION_MAX_DIFF_RATIO:
                output_path.write_text(original, encoding="utf-8")
                raise RevisionOverreachError(
                    f"RevisionOverreachError: changed-line ratio {ratio:.3f} "
                    f"exceeds {REVISION_MAX_DIFF_RATIO:.2f}; original restored."
                )
            output_path.write_text(chapter, encoding="utf-8")
            deficiencies = write_prose_deficiencies(chapter)
            if deficiencies:
                raise LabelLeakError(
                    f"LabelLeakError: revision left {len(deficiencies)} prose "
                    "deficiency record(s)."
                )
            print(f"OK: targeted revision adopted (diff ratio {ratio:.3f}) → "
                  f"{output_path}", file=sys.stderr)
            sys.exit(0)

        # 6. Validate word count. A failed draft is a paid artifact — salvage it
        # to <output>.rejected.md instead of discarding, so it can be inspected
        # (and so --output never silently retains a PREVIOUS chapter's draft as
        # if it were this one).
        try:
            validate_word_count(chapter, int(config.get("min_chapter_words", 2000)))
            check_forbidden_labels(chapter)
        except (ChapterValidationError, LabelLeakError):
            rejected = Path(str(args.output) + ".rejected.md")
            rejected.write_text(chapter, encoding="utf-8")
            print(f"Rejected draft salvaged to {rejected}", file=sys.stderr)
            raise

        # 7. Write output
        Path(args.output).write_text(chapter, encoding="utf-8")
        print(
            f"OK: {len(chapter.split())} words → {args.output}",
            file=sys.stderr,
        )
        sys.exit(0)

    except ContextOverflowError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except CostLimitError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except APIRateLimitError as e:
        print(f"Rate limit: {e}. All retries exhausted.", file=sys.stderr)
        sys.exit(1)
    except APIResponseError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except ChapterValidationError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except LabelLeakError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except RevisionOverreachError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception:
        print(f"Unexpected error:\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
