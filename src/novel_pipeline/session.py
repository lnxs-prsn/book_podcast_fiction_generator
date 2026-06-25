"""The session conductor.

Handles:
- Starting chapter determination (--chapter-start, --resume, or fresh)
- Pre-session summary with cost gate
- The N-chapter loop with draft → approve → promote → update living doc
- Interrupt-mid-cycle detection and recovery prompts
- Atomic state file updates at each commit point

I15: EOF convention used throughout this module:
  * _prompt_yes_no:  EOF -> False (treated as "no")
  * _prompt_choice:  EOF -> the explicit abort key if present in choices
                     (matched by key 'a' OR by description starting with
                     "abort"). If no abort entry exists, EOF -> last key.
  * Approval prompt: EOF -> "q" (quit), aligned with the pattern that
                     interrupt-during-input should not auto-approve work.
This convention is documented here and not redefined inline at each call site.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

ApproveChapterFn = Callable[[int, str], bool]
# (chapter_number, full_chapter_text) → True = approve, False = reject


@dataclass
class SessionResult:
    chapters_written: int
    final_chapter_number: int
    cost_usd: float
    completed: bool
    state_path: Path

from .cost import current_totals, estimate_cost
from .docs import (
    find_unpromoted_drafts,
    load_living_doc,
    load_static_docs,
    promote_chapter,
    save_chapter_draft,
    save_living_doc,
)
from .exceptions import (
    APIResponseError,
    ChapterValidationError,
    ConfigError,
    ContextOverflowError,
    CostLimitError,
    LivingDocValidationError,
    PromotionCollisionError,
    RejectionLimitReachedError,
)
from .logging_ import log_event
from .prompts import build_prompt
from llm.protocol import LLMTransport

from .requests_ import request_chapter, request_living_doc_update
from .state import (
    compute_gaps,
    detect_resume_state,
    find_next_chapter_number,
    list_canonical_chapters,
    read_state,
    write_state,
)
from .tokens import count_tokens


# ---------------------------------------------------------------------------
# Small interaction helpers
# ---------------------------------------------------------------------------

def _prompt_yes_no(prompt: str, *, auto: bool = False, default_no: bool = True) -> bool:
    """Yes/no prompt. I15: EOF -> False ('no'). auto=True returns True."""
    if auto:
        return True
    suffix = " [y/N]: " if default_no else " [Y/n]: "
    try:
        ans = input(prompt + suffix).strip().lower()
    except EOFError:
        return False
    if not ans:
        return not default_no
    return ans in ("y", "yes")


def _abort_key(choices: dict[str, str]) -> str:
    """I15: pick the abort key for a choice dict.

    Heuristic, in priority order:
      1. an entry with key 'a' if present (conventional abort key)
      2. an entry whose description starts with 'abort'
      3. the last key (back-compat fallback)
    """
    if "a" in choices:
        return "a"
    for k, desc in choices.items():
        if desc.lower().startswith("abort"):
            return k
    return list(choices.keys())[-1]


def _prompt_choice(prompt: str, choices: dict[str, str], *, auto: bool = False) -> str:
    """Return the key the user picked. `choices` is {letter: description}.

    I15: EOF -> abort entry if present, else last key.
    auto=True returns the first key (callers should pre-screen for safety).
    """
    if auto:
        return next(iter(choices))
    print(prompt)
    for letter, desc in choices.items():
        print(f"  [{letter}] {desc}")
    while True:
        try:
            ans = input("Choice: ").strip().lower()
        except EOFError:
            return _abort_key(choices)
        if ans in choices:
            return ans
        print(f"Please pick one of: {', '.join(choices.keys())}")


# ---------------------------------------------------------------------------
# First-run / starting-chapter resolution
# ---------------------------------------------------------------------------

def _enforce_first_run_template(
    config: dict, living_doc: str, output_dir: str
) -> None:
    """C2: refuse to start with an empty living doc on a true first run.

    "True first run" means: no canonical chapters on disk AND living doc
    file is missing or empty. The original behaviour would happily generate
    chapter 1 from a blank template and then fail living-doc validation
    *after* a paid API call. We catch this before any API call instead.
    """
    has_chapters = bool(list_canonical_chapters(output_dir, config))
    if has_chapters:
        return  # not a first run
    living_path = Path(config["living_doc_path"])
    if not living_doc.strip():
        sections_hint = "\n  ".join(
            config.get("required_living_doc_sections", []) or ["(none configured)"]
        )
        raise ConfigError(
            "First-run guard: living doc is missing or empty at "
            f"{living_path}, and no canonical chapters exist yet.\n"
            "The pipeline requires a starting living-doc template so the "
            "model has structural anchors to extend. Without it, the first "
            "living-doc-update call will fail structural validation after "
            "you have already paid for one chapter generation.\n"
            f"Create {living_path} with at minimum the configured "
            "required_living_doc_sections headers:\n  "
            f"{sections_hint}\n"
            "Then re-run."
        )


def _resolve_starting_chapter(
    config: dict,
    client: LLMTransport,
    timeout: float | None,
    *,
    chapter_start: int | None,
    resume: bool,
    auto_approve: bool,
    static_docs: dict[str, str],
    living_doc_ref: list,  # mutable wrapper so we can rebind on regenerate
) -> tuple[int, bool]:
    """Decide which chapter number to begin writing.

    Returns (chapter_number, should_continue). If should_continue is False,
    caller exits clean.
    """
    output_dir = config["output_dir"]
    state_file_path = config["state_file_path"]
    living_doc_path = config["living_doc_path"]

    # -- Explicit --chapter-start wins, with a loud warning on skipped gaps --
    if chapter_start is not None:
        natural = find_next_chapter_number(output_dir, config)
        if chapter_start != natural:
            gaps = compute_gaps(output_dir, config)
            chapters = list_canonical_chapters(output_dir, config)
            # Compute the set of chapter numbers that would be skipped.
            present = set(chapters)
            would_skip = [
                n for n in range(natural, chapter_start) if n not in present
            ]
            print(
                f"--chapter-start {chapter_start} specified.\n"
                f"Natural next chapter (first gap or append point) would be "
                f"{natural}.\n"
                f"Canonical chapters present: {chapters}.\n"
                f"Missing in sequence: {gaps}.\n"
                f"Would skip writing chapters: {would_skip or 'none'}.\n"
                f"Proceeding with --chapter-start {chapter_start} will skip "
                f"these."
            )
            # C4: under auto-approve, refuse to silently skip gaps.
            if auto_approve and would_skip:
                log_event(
                    "chapter_start_gap_skip_blocked_under_auto_approve",
                    {"chapter_start": chapter_start, "would_skip": would_skip},
                )
                raise ConfigError(
                    f"--chapter-start {chapter_start} would skip chapter(s) "
                    f"{would_skip}, and --auto-approve is set. Silent gap "
                    f"skipping under auto-approve is refused. Either:\n"
                    f"  (a) drop --auto-approve for this run and confirm the "
                    f"skip interactively, or\n"
                    f"  (b) write the missing chapter(s) explicitly first."
                )
            if not _prompt_yes_no("Continue?", auto=False, default_no=True):
                log_event("chapter_start_override_declined", {"chapter_start": chapter_start})
                return (0, False)
        log_event("chapter_start_override", {"chapter_start": chapter_start})
        return (chapter_start, True)

    # -- --resume path --
    if resume:
        state = detect_resume_state(output_dir, state_file_path, config)

        if state["gaps_present"]:
            print(
                f"Chapters present: {state['chapters_on_disk']} "
                f"with gaps at {state['gaps_present']}. "
                f"Resuming at chapter {state['next_chapter']}."
            )

        if not state["consistent"]:
            last_p = state["last_promoted"]
            last_d = state["last_doc_updated"]
            print(
                "Interrupted state detected:\n"
                f"  Chapter {last_p} was promoted but living doc was not "
                f"updated.\n"
                f"  Living doc currently reflects state through chapter "
                f"{last_d}."
            )
            # C3: under auto-approve, refuse to auto-pick the most expensive
            # option (regenerate). Abort with a clear message asking the
            # human to run interactively.
            if auto_approve:
                log_event(
                    "resume_inconsistent_blocked_under_auto_approve",
                    {"last_promoted": last_p, "last_doc_updated": last_d},
                )
                raise ConfigError(
                    "Resume detected an inconsistent state "
                    f"(last_promoted={last_p}, last_doc_updated={last_d}) "
                    "and --auto-approve is set.\n"
                    "Automatic recovery would silently call the API to "
                    "regenerate the living doc — that is refused under "
                    "--auto-approve to avoid unexpected spend.\n"
                    "Re-run interactively (drop --auto-approve) to choose "
                    "regenerate / continue-stale / abort."
                )
            choice = _prompt_choice(
                "Options:",
                {
                    "r": f"Regenerate living doc from chapter {last_p} "
                         f"(calls API, costs tokens)",
                    "c": "Continue anyway — living doc will be stale; next "
                         "chapter prompt will use outdated context",
                    "a": "Abort",
                },
                auto=False,
            )
            if choice == "a":
                log_event("resume_aborted_by_user", {})
                return (0, False)
            if choice == "c":
                log_event("resumed_with_stale_living_doc", {"last_promoted": last_p})
                # Fall through with the existing living_doc.
            else:  # "r"
                # Read the promoted chapter and ask the model to update.
                name_fmt = config.get(
                    "canonical_chapter_name_format", "chapter_{nn:02d}.md"
                )
                chapter_path = Path(output_dir) / name_fmt.format(nn=last_p)
                if not chapter_path.exists():
                    print(
                        f"Expected canonical chapter {chapter_path} not "
                        f"found; cannot regenerate. Aborting."
                    )
                    log_event("resume_regenerate_missing_chapter", {"path": str(chapter_path)})
                    return (0, False)
                chapter_text = chapter_path.read_text(encoding="utf-8")
                try:
                    new_living = request_living_doc_update(
                        static_docs,
                        living_doc_ref[0],
                        chapter_text,
                        config["model"],
                        config,
                        client=client,
                        timeout=timeout,
                    )
                except (LivingDocValidationError, APIResponseError) as e:
                    print(f"Regeneration failed: {e}")
                    log_event("resume_regenerate_failed", {"error": str(e)})
                    return (0, False)
                save_living_doc(living_doc_path, new_living, config)
                living_doc_ref[0] = new_living
                write_state(
                    state_file_path,
                    last_chapter_promoted=last_p,
                    last_chapter_living_doc_updated=last_p,
                )
                log_event("resume_living_doc_regenerated", {"chapter": last_p})

        # H7: surface unpromoted drafts (if any) for the next chapter slot.
        next_chap = state["next_chapter"]
        _maybe_surface_unpromoted_draft(config, next_chap, auto_approve)

        return (next_chap, True)

    # -- No --resume, no --chapter-start: fresh start guard --
    next_chap = find_next_chapter_number(output_dir, config)
    if next_chap > 1:
        chapters = list_canonical_chapters(output_dir, config)
        log_event("fresh_start_blocked_by_existing_chapters", {"chapters": chapters})
        raise ConfigError(
            f"Output directory contains chapters but --resume not specified.\n"
            f"Canonical chapters present: {chapters}\n"
            f"Next chapter would be {next_chap}. Re-run with --resume to "
            f"continue, or with --chapter-start to override."
        )

    return (1, True)


def _maybe_surface_unpromoted_draft(
    config: dict, chapter_num: int, auto_approve: bool
) -> None:
    """H7: on resume, if there are unpromoted drafts for the next chapter,
    inform the user. Non-blocking — purely advisory. Under auto-approve we
    only log; the user did not opt into interactive recovery."""
    drafts = find_unpromoted_drafts(config["output_dir"], chapter_num)
    if not drafts:
        return
    log_event(
        "resume_unpromoted_drafts_found",
        {
            "chapter": chapter_num,
            "drafts": [str(p) for p in drafts],
        },
    )
    if auto_approve:
        return
    print(
        f"\nNote: {len(drafts)} unpromoted draft(s) exist for chapter "
        f"{chapter_num:02d} in .rejected/.\n"
        f"  Most recent: {drafts[0]}\n"
        f"  These will NOT be auto-used — a fresh generation will run. "
        f"Review them manually if you want to recover work.\n"
    )


# ---------------------------------------------------------------------------
# Pre-session summary
# ---------------------------------------------------------------------------

def _estimate_chapter_prompt_tokens(
    static_docs: dict[str, str],
    living_doc: str,
    model: str,
    config: dict,
) -> int:
    """Build a generate_chapter prompt and count its tokens. Used in the
    summary and in the per-iteration re-print.

    H3: applies the same per-message overhead used in actual pre-flight.
    """
    messages = build_prompt(
        static_docs,
        living_doc,
        task="generate_chapter",
        extra="=== TASK ===\nplaceholder\n",
        config=config,
    )
    per_message = int(config.get("token_count_per_message_overhead", 4))
    priming = int(config.get("token_count_completion_priming", 3))
    total = 0
    for m in messages:
        total += count_tokens(m.get("content", ""), model, config)
        total += per_message
    total += priming
    return total


def _print_pre_session_summary(
    config: dict,
    static_docs: dict[str, str],
    living_doc: str,
) -> None:
    model = config["model"]
    static_total_tokens = sum(
        count_tokens(t, model, config) for t in static_docs.values()
    )
    living_tokens = count_tokens(living_doc, model, config)

    chap_prompt_tokens = _estimate_chapter_prompt_tokens(
        static_docs, living_doc, model, config
    )
    expected_chap_out = int(config.get("expected_output_tokens_chapter", 4000))
    expected_update_out = int(config.get("expected_output_tokens_update", 2000))

    cost_chapter = estimate_cost(chap_prompt_tokens, expected_chap_out, config)
    # I12 (per user: leave as-is): update_living_doc prompt approximated as
    # chapter-prompt + new chapter.
    update_prompt_tokens = chap_prompt_tokens + expected_chap_out
    cost_update = estimate_cost(update_prompt_tokens, expected_update_out, config)
    cost_total = cost_chapter + cost_update

    totals = current_totals(config)
    session_limit = float(config["cost_limit_usd_per_session"])
    total_limit = float(config["cost_limit_usd_total"])

    print(
        f"Model: {model}\n"
        f"Static docs: {len(static_docs)} files, {static_total_tokens} tokens\n"
        f"Living doc: {living_tokens} tokens\n"
        f"Estimated cost — next chapter (gen + update): "
        f"${cost_total:.4f} "
        f"(generate=${cost_chapter:.4f}, update=${cost_update:.4f})\n"
        f"Session budget: ${session_limit:.2f}\n"
        f"Lifetime spent: ${totals['lifetime_total']:.4f} / "
        f"${total_limit:.2f}\n"
        f"Note: Per-chapter cost grows as living doc grows. Estimate is for "
        f"the *next* chapter only."
    )


# ---------------------------------------------------------------------------
# Dry-run output (M5: size to expected_output_tokens × chars_per_token)
# ---------------------------------------------------------------------------

def _build_dry_run_chapter(chapter_num: int, config: dict) -> str:
    """M5: produce a dry-run chapter sized realistically so that the next
    iteration's cost estimate isn't wildly under the real number."""
    template = config.get(
        "dry_run_chapter_template", "Lorem ipsum dolor sit amet. "
    )
    chars_per_token = int(config.get("tokenizer_chars_per_token", 4))
    expected_tokens = int(config.get("expected_output_tokens_chapter", 4000))
    target_chars = expected_tokens * chars_per_token
    if not template:
        template = "Lorem ipsum dolor sit amet. "
    # Build up to at least target_chars.
    reps = max(1, (target_chars // max(1, len(template))) + 1)
    body = template * reps
    body = body[:target_chars] if target_chars > 0 else body
    return f"# Chapter {chapter_num:02d} (dry-run placeholder)\n\n{body}"


# ---------------------------------------------------------------------------
# The main loop
# ---------------------------------------------------------------------------

def run_session(
    config: dict,
    client: LLMTransport,
    timeout: float | None = None,
    *,
    auto_approve: bool = False,
    dry_run: bool = False,
    resume: bool = False,
    chapter_start: int | None = None,
    ignore_cost_limit: bool = False,
    approve_chapter: ApproveChapterFn = lambda n, text: True,
) -> SessionResult:
    """Run one pipeline session: up to chapters_per_session chapters."""
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".rejected").mkdir(exist_ok=True)

    state_file_path = config["state_file_path"]
    living_doc_path = config["living_doc_path"]
    model = config["model"]

    # --- Load all files BEFORE any API call (spec) ---
    static_docs = load_static_docs(config["static_doc_paths"])
    living_doc = load_living_doc(living_doc_path)
    living_doc_ref = [living_doc]

    # C2: refuse blank-template first runs *before* any API call.
    _enforce_first_run_template(config, living_doc, str(output_dir))

    log_event(
        "session_loaded_docs",
        {
            "static_doc_keys": sorted(static_docs.keys()),
            "living_doc_chars": len(living_doc),
        },
    )

    # --- Determine starting chapter ---
    next_chapter, should_continue = _resolve_starting_chapter(
        config,
        client,
        timeout,
        chapter_start=chapter_start,
        resume=resume,
        auto_approve=auto_approve,
        static_docs=static_docs,
        living_doc_ref=living_doc_ref,
    )
    if not should_continue:
        return SessionResult(
            chapters_written=0,
            final_chapter_number=0,
            cost_usd=0.0,
            completed=False,
            state_path=Path(config["state_file_path"]),
        )
    living_doc = living_doc_ref[0]

    # --- Pre-session summary + gate ---
    _print_pre_session_summary(config, static_docs, living_doc)
    if not _prompt_yes_no("Proceed?", auto=auto_approve, default_no=True):
        log_event("session_declined_at_summary", {})
        return SessionResult(
            chapters_written=0,
            final_chapter_number=next_chapter,
            cost_usd=0.0,
            completed=False,
            state_path=Path(config["state_file_path"]),
        )

    chapters_per_session = int(config.get("chapters_per_session", 3))
    completed = 0
    current_chapter = next_chapter

    log_event(
        "session_started",
        {
            "starting_chapter": current_chapter,
            "chapters_per_session": chapters_per_session,
            "dry_run": dry_run,
            "auto_approve": auto_approve,
        },
    )

    try:
        for _ in range(chapters_per_session):
            ok = _run_one_chapter(
                chapter_num=current_chapter,
                static_docs=static_docs,
                living_doc=living_doc,
                config=config,
                output_dir=str(output_dir),
                state_file_path=state_file_path,
                living_doc_path=living_doc_path,
                model=model,
                auto_approve=auto_approve,
                approve_chapter=approve_chapter,
                dry_run=dry_run,
                ignore_cost_limit=ignore_cost_limit,
                client=client,
                timeout=timeout,
            )
            if ok is None:
                # user quit
                log_event("session_quit_by_user", {"completed": completed})
                break
            new_living, advanced = ok
            if advanced:
                living_doc = new_living
                completed += 1
                current_chapter += 1
                print()
                _print_pre_session_summary(config, static_docs, living_doc)
            else:
                # H2: chapter was promoted but living doc was kept stale.
                # Stopping here is mandatory — the next chapter prompt
                # would use the outdated living doc and silently introduce
                # narrative drift. The user must repair the living doc
                # manually and re-run --resume.
                completed += 1
                print(
                    f"\nChapter {current_chapter:02d} was promoted but the "
                    f"living doc was NOT updated. The living doc is now "
                    f"stale relative to disk.\n"
                    f"Session is stopping here to prevent narrative drift. "
                    f"Repair the living doc manually, then re-run with "
                    f"--resume."
                )
                log_event(
                    "session_stopped_after_keep_old_living_doc",
                    {"chapter": current_chapter, "completed": completed},
                )
                break

        log_event("session_complete", {"completed": completed})
        print(
            f"\nSession complete. Wrote {completed} chapter(s). "
            f"Next chapter will be {current_chapter}."
        )

    except KeyboardInterrupt:
        print(
            "\nInterrupted. State preserved. "
            "Re-run with --resume to continue. Exit code 1."
        )
        log_event("session_keyboard_interrupt", {"completed": completed})
        raise KeyboardInterrupt

    return SessionResult(
        chapters_written=completed,
        final_chapter_number=current_chapter,
        cost_usd=current_totals(config)["session_total"],
        completed=True,
        state_path=Path(config["state_file_path"]),
    )


# ---------------------------------------------------------------------------
# One chapter iteration
# ---------------------------------------------------------------------------

def _generate_chapter_text(
    *,
    chapter_num: int,
    static_docs: dict[str, str],
    living_doc: str,
    config: dict,
    model: str,
    dry_run: bool,
    ignore_cost_limit: bool,
    client: LLMTransport,
    timeout: float | None,
) -> str | None:
    """Step 1: generate (or dry-run) a chapter, with retry-on-failure UI.

    Returns the chapter text, or None on abort. May raise KeyboardInterrupt
    if the user picks abort on a retry/skip/abort prompt.

    "skip this chapter" returns a sentinel (empty string) so the caller
    can distinguish from successful generation.
    """
    SKIP_SENTINEL = ""
    while True:
        try:
            if dry_run:
                return _build_dry_run_chapter(chapter_num, config)
            return request_chapter(
                static_docs,
                living_doc,
                model,
                config,
                client=client,
                timeout=timeout,
                ignore_cost_limit=ignore_cost_limit,
            )
        except (
            ChapterValidationError,
            APIResponseError,
            ContextOverflowError,
            CostLimitError,
        ) as e:
            print(f"\nChapter generation failed: {type(e).__name__}: {e}")
            choice = _prompt_choice(
                "What now?",
                {"r": "retry", "s": "skip this chapter", "a": "abort session"},
                auto=False,
            )
            if choice == "a":
                log_event("chapter_generation_aborted", {"chapter": chapter_num})
                return None
            if choice == "s":
                log_event("chapter_skipped", {"chapter": chapter_num})
                return SKIP_SENTINEL
            # retry: loop


def _run_one_chapter(
    *,
    chapter_num: int,
    static_docs: dict[str, str],
    living_doc: str,
    config: dict,
    output_dir: str,
    state_file_path: str,
    living_doc_path: str,
    model: str,
    auto_approve: bool,
    approve_chapter: ApproveChapterFn,
    dry_run: bool,
    ignore_cost_limit: bool,
    client: LLMTransport,
    timeout: float | None,
) -> tuple[str, bool] | None:
    """Run one iteration of the loop.

    Returns:
      (new_living_doc, True)  - chapter approved AND living doc updated
      (old_living_doc, False) - chapter approved but living doc kept old
      None                    - user quit or generation aborted

    M4: rejection loop is bounded by `max_rejection_retries` (default 5)
    and implemented as iteration, not recursion — eliminates the latent
    stack-overflow on ~1000 rejections.
    """
    print(f"\n=== Chapter {chapter_num:02d} ===")

    max_rejections = int(config.get("max_rejection_retries", 5))
    chapter_text: str | None = None
    draft_path: str = ""

    # M4: bounded outer loop covering generation → save draft → approval.
    # Each iteration is one full attempt at producing an approved chapter.
    for attempt in range(1, max_rejections + 1):
        # ----- Step 1: generate chapter -----
        result = _generate_chapter_text(
            chapter_num=chapter_num,
            static_docs=static_docs,
            living_doc=living_doc,
            config=config,
            model=model,
            dry_run=dry_run,
            ignore_cost_limit=ignore_cost_limit,
            client=client,
            timeout=timeout,
        )
        if result is None:
            # user picked abort during generation
            return None
        if result == "":
            # user picked skip during generation
            return (living_doc, False)
        chapter_text = result

        # ----- Step 2: save draft to .rejected/ -----
        if dry_run:
            draft_path = f"<dry-run draft for chapter {chapter_num}>"
            print(f"[dry-run] would save draft to {draft_path}")
        else:
            draft_path = save_chapter_draft(
                output_dir, chapter_num, chapter_text, config
            )
            # H7: persist that a draft exists for this chapter, so resume
            # can surface it. We don't yet know last_promoted/last_doc_updated
            # have changed; preserve whatever they were.
            prev_state = read_state(state_file_path)
            prev_promoted = (
                prev_state["last_chapter_promoted"] if prev_state else 0
            )
            prev_doc_updated = (
                prev_state["last_chapter_living_doc_updated"] if prev_state else 0
            )
            write_state(
                state_file_path,
                last_chapter_promoted=prev_promoted,
                last_chapter_living_doc_updated=prev_doc_updated,
                last_chapter_drafted=chapter_num,
            )
        word_count = len(chapter_text.split())
        logger.info(
            "Draft saved: %s | Word count: %d | First 200 chars: %r",
            draft_path, word_count, chapter_text[:200],
        )

        # ----- Step 3: approval -----
        approved = approve_chapter(chapter_num, chapter_text)
        if not approved:
            log_event("chapter_rejected", {"chapter": chapter_num, "attempt": attempt})
            print(f"Rejected. Draft remains at {draft_path}. Attempt {attempt}/{max_rejections}.")
            chapter_text = None
            continue
        break

    else:
        # M4: ran the loop to completion without any approval.
        log_event(
            "rejection_limit_reached",
            {"chapter": chapter_num, "max_rejection_retries": max_rejections},
        )
        raise RejectionLimitReachedError(
            f"Chapter {chapter_num}: hit the max_rejection_retries limit "
            f"({max_rejections}) without an approval. The latest draft "
            f"remains at {draft_path}. Stopping to avoid runaway spend. "
            f"Either approve a draft, raise the limit in config, or take a "
            f"break and inspect what the model is producing."
        )

    assert chapter_text is not None  # guaranteed by the break above

    # ----- Step 4: promote draft -----
    if dry_run:
        print(f"[dry-run] would promote chapter {chapter_num}")
    else:
        try:
            promote_chapter(draft_path, output_dir, chapter_num, config)
        except PromotionCollisionError as e:
            # M1: surface as an abort. The caller (cli.main) will convert
            # this into a non-zero exit; we re-raise rather than swallowing.
            log_event(
                "promote_collision_aborting_session",
                {"chapter": chapter_num, "error": str(e)},
            )
            print(f"\nPromotion failed: {e}")
            raise

    # ----- Step 5: update state file (last_chapter_promoted advanced) -----
    prev_state = None if dry_run else read_state(state_file_path)
    last_doc_updated = (
        prev_state["last_chapter_living_doc_updated"] if prev_state else 0
    )
    last_drafted = (
        prev_state.get("last_chapter_drafted") if prev_state else None
    )
    if not dry_run:
        write_state(
            state_file_path,
            last_chapter_promoted=chapter_num,
            last_chapter_living_doc_updated=last_doc_updated,
            last_chapter_drafted=last_drafted,
        )

    # ----- Step 6: request living doc update -----
    new_living: str | None = None
    keep_old = False
    while new_living is None and not keep_old:
        try:
            if dry_run:
                new_living = (
                    living_doc + f"\n\n# (dry-run update for chapter {chapter_num})\n"
                )
            else:
                new_living = request_living_doc_update(
                    static_docs,
                    living_doc,
                    chapter_text,
                    model,
                    config,
                    client=client,
                    timeout=timeout,
                    ignore_cost_limit=ignore_cost_limit,
                )
        except LivingDocValidationError as e:
            print(f"\nLiving doc validation failed: {e}")
            if e.missing:
                print(f"  Missing or out-of-order sections: {e.missing}")
            if e.diff:
                print("  Diff against previous living doc:")
                for line in e.diff.splitlines():
                    print(f"    {line}")
            choice = _prompt_choice(
                "What now?",
                {
                    "r": "retry the update",
                    "k": "keep the OLD living doc (chapter stays promoted; "
                         "session will stop after this iteration)",
                    "a": "abort session",
                },
                auto=False,
            )
            if choice == "a":
                log_event("living_doc_update_aborted", {"chapter": chapter_num})
                raise KeyboardInterrupt
            if choice == "k":
                keep_old = True
                log_event(
                    "chapter_approved_but_living_doc_unchanged",
                    {"chapter": chapter_num, "reason": "validation_failed"},
                )
                break
            # retry
        except (APIResponseError, ContextOverflowError, CostLimitError) as e:
            print(f"\nLiving doc update failed: {type(e).__name__}: {e}")
            choice = _prompt_choice(
                "What now?",
                {
                    "r": "retry",
                    "k": "keep the OLD living doc (session will stop after "
                         "this iteration)",
                    "a": "abort session",
                },
                auto=False,
            )
            if choice == "a":
                raise KeyboardInterrupt
            if choice == "k":
                keep_old = True
                log_event(
                    "chapter_approved_but_living_doc_unchanged",
                    {"chapter": chapter_num, "reason": "api_error"},
                )
                break

    if keep_old:
        # H2: caller will stop the session loop after seeing False.
        return (living_doc, False)

    # ----- Step 7: save new living doc -----
    assert new_living is not None
    if dry_run:
        print(f"[dry-run] would save living doc ({len(new_living)} chars)")
    else:
        save_living_doc(living_doc_path, new_living, config)

    # ----- Step 8: state file shows doc-update caught up -----
    if not dry_run:
        write_state(
            state_file_path,
            last_chapter_promoted=chapter_num,
            last_chapter_living_doc_updated=chapter_num,
            last_chapter_drafted=last_drafted,
        )

    log_event(
        "chapter_cycle_complete",
        {"chapter": chapter_num, "living_doc_chars": len(new_living)},
    )
    print(f"Chapter {chapter_num:02d} complete. Living doc updated.")
    return (new_living, True)
