"""High-level task wrappers around call_api."""

from __future__ import annotations

from llm.protocol import LLMTransport

from .api import call_api
from .docs import build_living_doc_diff, validate_living_doc_structure
from .exceptions import ChapterValidationError, LivingDocValidationError
from .logging_ import log_event
from .prompts import build_prompt


_CHAPTER_TASK_INSTRUCTION = (
    "=== TASK ===\n"
    "Write the next chapter following the NEXT CHAPTER TARGET section of "
    "the living document above. Output the chapter only.\n"
    "=== END TASK ===\n"
)


_UPDATE_TASK_INSTRUCTION = (
    "=== TASK ===\n"
    "Produce the updated living document reflecting the chapter just "
    "written. Preserve all section headers from the template. Output the "
    "updated living document only.\n"
    "=== END TASK ===\n"
)


def _word_count(text: str) -> int:
    return len(text.split())


def request_chapter(
    static_docs: dict[str, str],
    living_doc: str,
    model: str,
    config: dict,
    *,
    client: LLMTransport,
    timeout: float | None = None,
    ignore_cost_limit: bool = False,
) -> str:
    """Ask the model for the next chapter.

    Validates that the response has >= min_chapter_words words.
    """
    messages = build_prompt(
        static_docs,
        living_doc,
        task="generate_chapter",
        extra=_CHAPTER_TASK_INSTRUCTION,
        config=config,
    )

    text = call_api(
        messages,
        model,
        config,
        client=client,
        timeout=timeout,
        expected_output_tokens=int(
            config.get("expected_output_tokens_chapter", 4000)
        ),
        ignore_cost_limit=ignore_cost_limit,
        static_docs=static_docs,
        living_doc=living_doc,
        task_label="generate_chapter",
    )

    min_words = int(config.get("min_chapter_words", 1500))
    wc = _word_count(text)
    if wc < min_words:
        log_event(
            "chapter_validation_failed",
            {"word_count": wc, "min_required": min_words},
        )
        raise ChapterValidationError(
            f"Chapter too short: {wc} words, minimum {min_words}. "
            f"This usually means the model truncated or refused. "
            f"First 200 chars of response: {text[:200]!r}"
        )

    log_event("chapter_validated", {"word_count": wc})
    return text


def request_living_doc_update(
    static_docs: dict[str, str],
    old_living_doc: str,
    new_chapter: str,
    model: str,
    config: dict,
    *,
    client: LLMTransport,
    timeout: float | None = None,
    ignore_cost_limit: bool = False,
) -> str:
    """Ask the model to update the living doc after a chapter is approved.

    Structural validation (all required sections present and in order) is
    enforced; failures raise LivingDocValidationError carrying the missing
    sections and a unified diff for human review.
    """
    chapter_block = (
        "=== NEW CHAPTER JUST WRITTEN ===\n"
        f"{new_chapter}\n"
        "=== END NEW CHAPTER ===\n\n"
    )
    extra = chapter_block + _UPDATE_TASK_INSTRUCTION

    messages = build_prompt(
        static_docs,
        old_living_doc,
        task="update_living_doc",
        extra=extra,
        config=config,
    )

    text = call_api(
        messages,
        model,
        config,
        client=client,
        timeout=timeout,
        expected_output_tokens=int(
            config.get("expected_output_tokens_update", 2000)
        ),
        ignore_cost_limit=ignore_cost_limit,
        static_docs=static_docs,
        living_doc=old_living_doc,
        task_label="update_living_doc",
    )

    required = list(config.get("required_living_doc_sections", []))
    if required:
        ok, problems = validate_living_doc_structure(text, required)
        if not ok:
            diff = build_living_doc_diff(old_living_doc, text)
            log_event(
                "living_doc_validation_failed",
                {"missing_or_reordered": problems},
            )
            raise LivingDocValidationError(
                "Updated living doc failed structural validation. "
                f"Missing or out-of-order sections: {problems}",
                missing=problems,
                diff=diff,
            )

    log_event("living_doc_validated", {"chars": len(text)})
    return text
