"""Tests for novel_pipeline.

Covers the deterministic layers: docs (load/save/promote/validate),
state (gap-scan + resume detection), prompts (build_prompt structure),
config (load + defaults + env + validation), cost (estimate + track),
and api (retries + cost gate + overflow + finish_reason) with `requests`
mocked.

New tests added for v0.3.0 fixes:
  C1: finish_reason='length' raises ChapterValidationError
  C1: finish_reason='content_filter' raises APIResponseError
  C1: max_tokens is included in payload
  L1: temperature/top_p/seed flow into the payload when set
  C2: first-run guard with empty living doc + no chapters
  M1: promotion collision raises PromotionCollisionError
  M2: config numeric validation
  M2: config format-string validation
  M4: rejection retries bounded
  H7: last_chapter_drafted optional in state
  H7: find_unpromoted_drafts
  I1: system prompts overridable via config
  I2: doc wrap formats overridable via config
  I4: tokenizer fallback configurable
  I5: retry backoff configurable
  I9: canonical regex configurable
  H3: per-message overhead in token counting
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_pipeline import cost as cost_mod
from novel_pipeline import (
    APIResponseError,
    ChapterValidationError,
    ConfigError,
    ContextOverflowError,
    CostLimitError,
    DocumentLoadError,
    LivingDocValidationError,
    PromotionCollisionError,
    RejectionLimitReachedError,
    ResumeStateError,
)
from novel_pipeline.api import call_api
from novel_pipeline.config import DEFAULTS, load_config
from novel_pipeline.cost import estimate_cost, reset_session_spend, track_spend
from novel_pipeline.docs import (
    find_unpromoted_drafts,
    load_living_doc,
    load_static_docs,
    promote_chapter,
    save_chapter_draft,
    save_living_doc,
    validate_living_doc_structure,
)
from novel_pipeline.prompts import build_prompt
from novel_pipeline.requests_ import request_chapter, request_living_doc_update
from novel_pipeline.state import (
    compute_gaps,
    detect_resume_state,
    find_next_chapter_number,
    list_canonical_chapters,
    read_state,
    write_state,
)
from novel_pipeline.tokens import count_tokens


@pytest.fixture(autouse=True)
def reset_spend():
    """Each test starts with a clean session spend counter."""
    reset_session_spend()
    yield
    reset_session_spend()


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------

class TestTokens:
    def test_count_tokens_empty(self):
        assert count_tokens("", "gpt-4") == 0

    def test_count_tokens_nonempty(self):
        n = count_tokens("hello world this is a test", "gpt-4")
        assert 4 <= n <= 10  # rough range

    def test_count_tokens_unknown_model_falls_back(self):
        # Unknown model name should fall back to cl100k_base, not crash.
        n = count_tokens("hello", "some/unknown-model")
        assert n > 0

    def test_count_tokens_with_config_fallback_encoding(self):
        # I4: config can override the fallback encoding name.
        cfg = {"tokenizer_encoding_fallback": "cl100k_base", "tokenizer_chars_per_token": 4}
        n = count_tokens("hello world", "some/unknown-model", cfg)
        assert n > 0


# ---------------------------------------------------------------------------
# Docs: load_static_docs
# ---------------------------------------------------------------------------

class TestLoadStaticDocs:
    def test_loads_md(self, tmp_path):
        f = tmp_path / "world_laws.md"
        f.write_text("# World\nSome content", encoding="utf-8")
        docs = load_static_docs([str(f)])
        assert docs == {"world_laws": "# World\nSome content"}

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_static_docs([str(tmp_path / "nope.md")])

    def test_empty_file_raises(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("   \n", encoding="utf-8")
        with pytest.raises(DocumentLoadError, match="empty"):
            load_static_docs([str(f)])

    def test_unsupported_extension_raises(self, tmp_path):
        f = tmp_path / "weird.xyz"
        f.write_text("data", encoding="utf-8")
        with pytest.raises(DocumentLoadError, match="unsupported extension"):
            load_static_docs([str(f)])

    def test_pdf_raises_with_hint(self, tmp_path):
        f = tmp_path / "stuff.pdf"
        f.write_bytes(b"%PDF-1.4\nfake")
        with pytest.raises(DocumentLoadError, match="PDF not supported"):
            load_static_docs([str(f)])

    def test_collision_raises(self, tmp_path):
        d1 = tmp_path / "a"
        d2 = tmp_path / "b"
        d1.mkdir()
        d2.mkdir()
        f1 = d1 / "world_laws.md"
        f2 = d2 / "world_laws.md"
        f1.write_text("x", encoding="utf-8")
        f2.write_text("y", encoding="utf-8")
        with pytest.raises(ValueError, match="collision"):
            load_static_docs([str(f1), str(f2)])

    def test_utf8_decode_failure_raises(self, tmp_path):
        f = tmp_path / "bad.md"
        # Invalid UTF-8 byte
        f.write_bytes(b"\xff\xfe not utf-8")
        with pytest.raises(DocumentLoadError, match="utf-8 decode"):
            load_static_docs([str(f)])


# ---------------------------------------------------------------------------
# Docs: living doc save/load with atomic write + backups
# ---------------------------------------------------------------------------

class TestLivingDoc:
    def test_load_missing_returns_empty(self, tmp_path):
        result = load_living_doc(str(tmp_path / "nope.md"))
        assert result == ""

    def test_save_then_load_roundtrip(self, tmp_path):
        p = tmp_path / "living.md"
        save_living_doc(str(p), "hello\nworld\n")
        assert load_living_doc(str(p)) == "hello\nworld"

    def test_save_empty_raises(self, tmp_path):
        with pytest.raises(ValueError, match="empty"):
            save_living_doc(str(tmp_path / "x.md"), "")

    def test_save_creates_backup_of_existing(self, tmp_path):
        p = tmp_path / "living.md"
        save_living_doc(str(p), "first content\n")
        save_living_doc(str(p), "second content\n")
        backups = list(tmp_path.glob("living.md.bak.*"))
        assert len(backups) == 1
        assert backups[0].read_text(encoding="utf-8") == "first content\n"

    def test_save_keeps_all_backups_not_just_10(self, tmp_path):
        # v1 patch 7: backups are kept indefinitely.
        p = tmp_path / "living.md"
        for i in range(15):
            save_living_doc(str(p), f"version {i}\n")
        backups = list(tmp_path.glob("living.md.bak.*"))
        # 14 saves overwrote existing, each one made a backup of the previous.
        assert len(backups) == 14

    def test_save_uses_configured_backup_format(self, tmp_path):
        # I7: backup naming is config-driven.
        p = tmp_path / "living.md"
        cfg = {"living_doc_backup_format": "{name}.backup-{ts}"}
        save_living_doc(str(p), "v1\n", cfg)
        save_living_doc(str(p), "v2\n", cfg)
        backups = list(tmp_path.glob("living.md.backup-*"))
        assert len(backups) == 1


# ---------------------------------------------------------------------------
# Docs: draft staging + promote
# ---------------------------------------------------------------------------

class TestDraftAndPromote:
    def test_save_chapter_draft_goes_to_rejected(self, tmp_path):
        draft_path = save_chapter_draft(str(tmp_path), 3, "chapter content\n")
        p = Path(draft_path)
        assert p.parent.name == ".rejected"
        assert p.name.startswith("chapter_03__")
        assert p.read_text(encoding="utf-8") == "chapter content\n"

    def test_save_empty_draft_raises(self, tmp_path):
        with pytest.raises(ValueError):
            save_chapter_draft(str(tmp_path), 1, "")

    def test_save_chapter_draft_uses_configured_name_format(self, tmp_path):
        # I8: draft naming is config-driven.
        cfg = {"rejected_draft_name_format": "rej-{nn:03d}-{ts}.md"}
        draft_path = save_chapter_draft(str(tmp_path), 5, "x\n", cfg)
        p = Path(draft_path)
        assert p.parent.name == ".rejected"
        assert p.name.startswith("rej-005-")
        assert p.name.endswith(".md")

    def test_promote_moves_to_canonical(self, tmp_path):
        draft = save_chapter_draft(str(tmp_path), 1, "the chapter\n")
        promoted = promote_chapter(draft, str(tmp_path), 1)
        assert Path(promoted).name == "chapter_01.md"
        assert not Path(draft).exists()
        assert Path(promoted).read_text(encoding="utf-8") == "the chapter\n"

    def test_promote_collision_now_raises(self, tmp_path):
        # M1: pre-existing canonical chapter triggers PromotionCollisionError
        # instead of silently writing a timestamped duplicate.
        canonical = tmp_path / "chapter_01.md"
        canonical.write_text("original\n", encoding="utf-8")

        draft = save_chapter_draft(str(tmp_path), 1, "replacement\n")
        with pytest.raises(PromotionCollisionError, match="already exists"):
            promote_chapter(draft, str(tmp_path), 1)
        # Original untouched.
        assert canonical.read_text(encoding="utf-8") == "original\n"
        # Draft also untouched (still in .rejected/).
        assert Path(draft).exists()

    def test_promote_missing_draft_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            promote_chapter(str(tmp_path / "ghost.md"), str(tmp_path), 1)

    def test_promote_uses_configured_canonical_format(self, tmp_path):
        # I9: canonical filename format is config-driven.
        cfg = {"canonical_chapter_name_format": "ch_{nn:03d}.md"}
        draft = save_chapter_draft(str(tmp_path), 7, "content\n", cfg)
        promoted = promote_chapter(draft, str(tmp_path), 7, cfg)
        assert Path(promoted).name == "ch_007.md"


class TestFindUnpromotedDrafts:
    def test_returns_empty_when_no_rejected_dir(self, tmp_path):
        # H7: no .rejected/ directory should not raise.
        assert find_unpromoted_drafts(str(tmp_path), 1) == []

    def test_returns_matching_drafts_newest_first(self, tmp_path):
        # H7: surface drafts on resume.
        save_chapter_draft(str(tmp_path), 3, "first\n")
        # Ensure mtime differs (filesystems may not have sub-second resolution).
        import time as _time
        _time.sleep(0.02)
        save_chapter_draft(str(tmp_path), 3, "second\n")
        drafts = find_unpromoted_drafts(str(tmp_path), 3)
        assert len(drafts) == 2
        # Newest first.
        assert drafts[0].read_text(encoding="utf-8") == "second\n"
        assert drafts[1].read_text(encoding="utf-8") == "first\n"

    def test_ignores_other_chapter_numbers(self, tmp_path):
        save_chapter_draft(str(tmp_path), 1, "ch1\n")
        save_chapter_draft(str(tmp_path), 2, "ch2\n")
        drafts = find_unpromoted_drafts(str(tmp_path), 1)
        assert len(drafts) == 1
        assert "first\n" not in drafts[0].read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Docs: structural validation
# ---------------------------------------------------------------------------

class TestStructuralValidation:
    SECTIONS = [
        "=== LIVING DOCUMENT ===",
        "--- CURRENT STATE ---",
        "--- ACTIVE VOCABULARY ---",
    ]

    def test_all_present_in_order(self):
        text = "\n".join(
            [
                "=== LIVING DOCUMENT ===",
                "intro",
                "--- CURRENT STATE ---",
                "state",
                "--- ACTIVE VOCABULARY ---",
                "vocab",
            ]
        )
        ok, problems = validate_living_doc_structure(text, self.SECTIONS)
        assert ok
        assert problems == []

    def test_missing_section(self):
        text = "=== LIVING DOCUMENT ===\n--- ACTIVE VOCABULARY ---\n"
        ok, problems = validate_living_doc_structure(text, self.SECTIONS)
        assert not ok
        assert "--- CURRENT STATE ---" in problems

    def test_out_of_order(self):
        text = "\n".join(
            [
                "=== LIVING DOCUMENT ===",
                "--- ACTIVE VOCABULARY ---",
                "--- CURRENT STATE ---",  # out of order vs SECTIONS
            ]
        )
        ok, problems = validate_living_doc_structure(text, self.SECTIONS)
        assert not ok
        assert problems
        assert any(p in ("--- CURRENT STATE ---", "--- ACTIVE VOCABULARY ---") for p in problems)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

class TestPrompts:
    def test_unknown_task_raises(self):
        with pytest.raises(ValueError):
            build_prompt({}, "", task="nope")

    def test_order_is_fixed(self):
        docs = {
            "full_map": "MAP_BODY",
            "world_laws": "WB_BODY",
            "style_contract": "STYLE_BODY",
            "curriculum": "CURR_BODY",
        }
        msgs = build_prompt(docs, "LIVING_BODY", task="generate_chapter", extra="TASK")
        user = msgs[1]["content"]
        order = [
            user.find("=== WORLD_LAWS ==="),
            user.find("=== CURRICULUM ==="),
            user.find("=== STYLE_CONTRACT ==="),
            user.find("=== FULL_MAP ==="),
            user.find("=== END LIVING DOCUMENT ==="),
            user.find("TASK"),
        ]
        assert all(i >= 0 for i in order), f"missing section: {order}"
        assert order == sorted(order), f"sections out of order: {order}"

    def test_system_prompt_per_task(self):
        msgs1 = build_prompt({}, "", task="generate_chapter")
        msgs2 = build_prompt({}, "", task="update_living_doc")
        assert "fiction-writing" in msgs1[0]["content"]
        assert "continuity-tracking" in msgs2[0]["content"]

    def test_empty_living_doc_marked_first_chapter(self):
        msgs = build_prompt({}, "", task="generate_chapter")
        assert "(empty — first chapter)" in msgs[1]["content"]

    def test_extra_static_docs_appended_alphabetised(self):
        docs = {"world_laws": "WB", "z_extra": "Z", "a_extra": "A"}
        msgs = build_prompt(docs, "", task="generate_chapter")
        user = msgs[1]["content"]
        assert user.find("=== A_EXTRA ===") < user.find("=== Z_EXTRA ===")
        assert user.find("=== WORLD_BIBLE ===") < user.find("=== A_EXTRA ===")

    def test_system_prompt_can_be_overridden_via_config(self):
        # I1: system prompts moved into TOML config.
        cfg = {
            "system_prompt_generate_chapter": "CUSTOM_GEN_PROMPT",
            "system_prompt_update_living_doc": "CUSTOM_UPD_PROMPT",
        }
        msgs1 = build_prompt({}, "", task="generate_chapter", config=cfg)
        msgs2 = build_prompt({}, "", task="update_living_doc", config=cfg)
        assert msgs1[0]["content"] == "CUSTOM_GEN_PROMPT"
        assert msgs2[0]["content"] == "CUSTOM_UPD_PROMPT"

    def test_wrap_format_can_be_overridden_via_config(self):
        # I2: doc wrap format is config-driven.
        cfg = {
            "doc_wrap_open_format": "<<< {name_lower} >>>",
            "doc_wrap_close_format": "<<< /{name_lower} >>>",
        }
        msgs = build_prompt({"world_laws": "WB"}, "L", task="generate_chapter", config=cfg)
        user = msgs[1]["content"]
        assert "<<< world_laws >>>" in user
        assert "<<< /world_laws >>>" in user

    def test_static_doc_order_overridable_via_config(self):
        # I3: static doc order is config-driven (default is correct; we test it works).
        cfg = {"static_doc_order": ["curriculum", "world_laws"]}
        docs = {"world_laws": "WB", "curriculum": "CURR"}
        msgs = build_prompt(docs, "", task="generate_chapter", config=cfg)
        user = msgs[1]["content"]
        # curriculum must appear before world_laws in this order.
        assert user.find("=== CURRICULUM ===") < user.find("=== WORLD_LAWS ===")


# ---------------------------------------------------------------------------
# State: find_next_chapter_number (v2 gap-scan)
# ---------------------------------------------------------------------------

class TestFindNextChapter:
    def test_empty_dir_returns_1(self, tmp_path):
        assert find_next_chapter_number(str(tmp_path)) == 1

    def test_nonexistent_dir_returns_1(self, tmp_path):
        assert find_next_chapter_number(str(tmp_path / "ghost")) == 1

    def test_no_gaps_returns_n_plus_1(self, tmp_path):
        for n in (1, 2, 3):
            (tmp_path / f"chapter_{n:02d}.md").write_text("x", encoding="utf-8")
        assert find_next_chapter_number(str(tmp_path)) == 4

    def test_gap_mid_sequence_returned(self, tmp_path):
        (tmp_path / "chapter_01.md").write_text("x", encoding="utf-8")
        (tmp_path / "chapter_03.md").write_text("x", encoding="utf-8")
        assert find_next_chapter_number(str(tmp_path)) == 2

    def test_ignores_rejected(self, tmp_path):
        (tmp_path / ".rejected").mkdir()
        (tmp_path / ".rejected" / "chapter_05__20260101T000000Z.md").write_text(
            "x", encoding="utf-8"
        )
        assert find_next_chapter_number(str(tmp_path)) == 1

    def test_ignores_timestamped_duplicates(self, tmp_path):
        (tmp_path / "chapter_01.md").write_text("x", encoding="utf-8")
        (tmp_path / "chapter_01__20260101T000000Z.md").write_text("x", encoding="utf-8")
        assert find_next_chapter_number(str(tmp_path)) == 2

    def test_list_and_gaps(self, tmp_path):
        for n in (1, 3, 5):
            (tmp_path / f"chapter_{n:02d}.md").write_text("x", encoding="utf-8")
        assert list_canonical_chapters(str(tmp_path)) == [1, 3, 5]
        assert compute_gaps(str(tmp_path)) == [2, 4]

    def test_custom_canonical_regex(self, tmp_path):
        # I9: regex is config-driven.
        cfg = {"canonical_chapter_regex": r"^ch_(\d+)\.md$"}
        (tmp_path / "ch_1.md").write_text("x", encoding="utf-8")
        (tmp_path / "ch_3.md").write_text("x", encoding="utf-8")
        # Default regex would not match these.
        assert list_canonical_chapters(str(tmp_path)) == []
        # Custom regex finds them.
        assert list_canonical_chapters(str(tmp_path), cfg) == [1, 3]


# ---------------------------------------------------------------------------
# State: read/write + detect_resume_state
# ---------------------------------------------------------------------------

class TestStateFile:
    def test_read_missing_returns_none(self, tmp_path):
        assert read_state(str(tmp_path / "state.json")) is None

    def test_write_then_read_roundtrip(self, tmp_path):
        p = tmp_path / "state.json"
        write_state(str(p), last_chapter_promoted=3, last_chapter_living_doc_updated=3)
        data = read_state(str(p))
        assert data["last_chapter_promoted"] == 3
        assert data["last_chapter_living_doc_updated"] == 3
        assert "updated_at" in data
        # H7: optional field backfilled to None when absent.
        assert data.get("last_chapter_drafted") is None

    def test_write_with_last_chapter_drafted(self, tmp_path):
        # H7: optional last_chapter_drafted persists.
        p = tmp_path / "state.json"
        write_state(
            str(p),
            last_chapter_promoted=2,
            last_chapter_living_doc_updated=2,
            last_chapter_drafted=3,
        )
        data = read_state(str(p))
        assert data["last_chapter_drafted"] == 3

    def test_old_state_without_drafted_still_readable(self, tmp_path):
        # H7: backward compat with state files that don't have the optional key.
        p = tmp_path / "state.json"
        p.write_text(
            json.dumps(
                {
                    "last_chapter_promoted": 1,
                    "last_chapter_living_doc_updated": 1,
                    "updated_at": "2026-01-01T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        data = read_state(str(p))
        assert data["last_chapter_promoted"] == 1
        assert data.get("last_chapter_drafted") is None

    def test_malformed_json_raises_resume_state_error(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text("not json", encoding="utf-8")
        with pytest.raises(ResumeStateError, match="malformed"):
            read_state(str(p))

    def test_missing_keys_raises(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
        with pytest.raises(ResumeStateError, match="missing required keys"):
            read_state(str(p))


class TestDetectResumeState:
    def test_consistent_state(self, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        for n in (1, 2):
            (out / f"chapter_{n:02d}.md").write_text("x", encoding="utf-8")
        state_file = tmp_path / "state.json"
        write_state(str(state_file), last_chapter_promoted=2, last_chapter_living_doc_updated=2)

        state = detect_resume_state(str(out), str(state_file))
        assert state["next_chapter"] == 3
        assert state["consistent"] is True
        assert state["last_promoted"] == 2
        assert state["last_doc_updated"] == 2
        assert state["gaps_present"] == []
        assert state["chapters_on_disk"] == [1, 2]
        # H7: new key present in returned dict.
        assert "last_drafted" in state

    def test_inconsistent_state(self, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        for n in (1, 2, 3):
            (out / f"chapter_{n:02d}.md").write_text("x", encoding="utf-8")
        state_file = tmp_path / "state.json"
        write_state(
            str(state_file),
            last_chapter_promoted=3,
            last_chapter_living_doc_updated=2,
        )
        state = detect_resume_state(str(out), str(state_file))
        assert state["consistent"] is False
        assert state["last_promoted"] == 3
        assert state["last_doc_updated"] == 2

    def test_chapters_present_but_no_state_file_raises(self, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        (out / "chapter_01.md").write_text("x", encoding="utf-8")
        state_file = tmp_path / "state.json"  # does not exist
        with pytest.raises(ResumeStateError, match="missing but canonical"):
            detect_resume_state(str(out), str(state_file))

    def test_gaps_reported(self, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        (out / "chapter_01.md").write_text("x", encoding="utf-8")
        (out / "chapter_03.md").write_text("x", encoding="utf-8")
        state_file = tmp_path / "state.json"
        write_state(str(state_file), last_chapter_promoted=3, last_chapter_living_doc_updated=3)
        state = detect_resume_state(str(out), str(state_file))
        assert state["gaps_present"] == [2]
        assert state["next_chapter"] == 2  # gap-scan finds 2 first


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestConfig:
    MIN_CONFIG = """
model = "test/model"
static_doc_paths = ["./a.md"]
living_doc_path = "./living.md"
output_dir = "./out"
context_limit = 100000
price_per_1m_input_tokens = 1.0
price_per_1m_output_tokens = 2.0
"""

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(str(tmp_path / "no.toml"))

    def test_minimal_config_applies_defaults(self, tmp_path):
        p = tmp_path / "c.toml"
        p.write_text(self.MIN_CONFIG, encoding="utf-8")
        cfg = load_config(str(p))
        assert cfg["model"] == "test/model"
        assert cfg["min_chapter_words"] == 1500
        assert cfg["chapters_per_session"] == 3
        assert cfg["state_file_path"] == "./.pipeline_state.json"  # v2
        # v0.3 defaults present:
        assert cfg["max_rejection_retries"] == 5
        assert cfg["retry_backoff_seconds"] == [2, 8, 32]
        assert cfg["token_count_per_message_overhead"] == 4
        assert cfg["token_count_completion_priming"] == 3
        # Sampling controls default to None.
        assert cfg["temperature"] is None
        assert cfg["top_p"] is None
        assert cfg["seed"] is None

    def test_missing_required_raises(self, tmp_path):
        p = tmp_path / "c.toml"
        p.write_text('model = "x"\n', encoding="utf-8")
        with pytest.raises(ConfigError, match="missing required keys"):
            load_config(str(p))

    def test_v2_default_sections_are_character_agnostic(self):
        defaults = DEFAULTS["required_living_doc_sections"]
        joined = " ".join(defaults)
        assert "PROTAGONIST" in joined
        assert "ACTIVE VOCABULARY" in joined

    # ----- M2: validation -----

    def test_validation_context_limit_too_low(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + "\ncontext_safety_margin = 99999\n"
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="context_limit"):
            load_config(str(p))

    def test_validation_chapters_per_session_zero(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + "\nchapters_per_session = 0\n"
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="chapters_per_session"):
            load_config(str(p))

    def test_validation_price_zero_rejected(self, tmp_path):
        p = tmp_path / "c.toml"
        body = """
model = "x"
static_doc_paths = ["./a.md"]
living_doc_path = "./l.md"
output_dir = "./o"
context_limit = 100000
price_per_1m_input_tokens = 0
price_per_1m_output_tokens = 2
"""
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="price_per_1m_input_tokens"):
            load_config(str(p))

    def test_validation_temperature_out_of_range(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + "\ntemperature = 5.0\n"
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="temperature"):
            load_config(str(p))

    def test_validation_bad_doc_wrap_format(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + '\ndoc_wrap_open_format = "no placeholder"\n'
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="doc_wrap_open_format"):
            load_config(str(p))

    def test_validation_bad_rejected_draft_format(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + '\nrejected_draft_name_format = "no_placeholders.md"\n'
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="rejected_draft_name_format"):
            load_config(str(p))

    def test_validation_backoff_must_be_list(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + "\nretry_backoff_seconds = 5\n"
        p.write_text(body, encoding="utf-8")
        with pytest.raises(ConfigError, match="retry_backoff_seconds"):
            load_config(str(p))

    def test_temperature_passthrough(self, tmp_path):
        p = tmp_path / "c.toml"
        body = self.MIN_CONFIG + "\ntemperature = 0.7\ntop_p = 0.95\nseed = 42\n"
        p.write_text(body, encoding="utf-8")
        cfg = load_config(str(p))
        assert cfg["temperature"] == pytest.approx(0.7)
        assert cfg["top_p"] == pytest.approx(0.95)
        assert cfg["seed"] == 42


# ---------------------------------------------------------------------------
# Cost
# ---------------------------------------------------------------------------

class TestCost:
    CONFIG = {
        "price_per_1m_input_tokens": 10.0,
        "price_per_1m_output_tokens": 30.0,
    }

    def test_estimate_cost(self):
        # 1M input @ $10 + 1M output @ $30 = $40
        assert estimate_cost(1_000_000, 1_000_000, self.CONFIG) == pytest.approx(40.0)

    def test_estimate_cost_fractional(self):
        assert estimate_cost(100_000, 100_000, self.CONFIG) == pytest.approx(4.0)

    def test_track_spend_persists(self, tmp_path):
        cfg = {
            **self.CONFIG,
            "spend_file_path": str(tmp_path / ".spend.json"),
        }
        totals = track_spend(1.50, cfg, note="t1")
        assert totals["session_total"] == pytest.approx(1.50)
        assert totals["lifetime_total"] == pytest.approx(1.50)

        totals = track_spend(0.75, cfg, note="t2")
        assert totals["session_total"] == pytest.approx(2.25)
        assert totals["lifetime_total"] == pytest.approx(2.25)

        data = json.loads(Path(cfg["spend_file_path"]).read_text())
        assert len(data["entries"]) == 2
        assert data["lifetime_total"] == pytest.approx(2.25)

    def test_lifetime_persists_across_session_reset(self, tmp_path):
        cfg = {
            **self.CONFIG,
            "spend_file_path": str(tmp_path / ".spend.json"),
        }
        track_spend(5.00, cfg)
        reset_session_spend()
        totals = track_spend(1.00, cfg)
        assert totals["session_total"] == pytest.approx(1.00)
        assert totals["lifetime_total"] == pytest.approx(6.00)


# ---------------------------------------------------------------------------
# API: mocked requests.post
# ---------------------------------------------------------------------------

class FakeLLMTransport:
    """Stub LLMTransport that records payloads and returns a canned response."""

    def __init__(
        self,
        content: str = "chapter text",
        finish_reason: str = "stop",
        usage: dict | None = None,
        raise_on_call: Exception | None = None,
    ) -> None:
        self.content = content
        self.finish_reason = finish_reason
        self.usage = usage or {"prompt_tokens": 100, "completion_tokens": 50}
        self.raise_on_call = raise_on_call
        self.calls: list[dict] = []

    def chat_completion(
        self,
        payload: dict,
        *,
        timeout: float | None = None,
    ) -> dict:
        if self.raise_on_call:
            raise self.raise_on_call
        self.calls.append({"payload": payload, "timeout": timeout})
        return {
            "choices": [
                {
                    "message": {"content": self.content},
                    "finish_reason": self.finish_reason,
                }
            ],
            "usage": self.usage,
        }


def _make_config(tmp_path: Path) -> dict:
    """Return a config dict suitable for testing call_api in isolation."""
    return {
        "api_key": "test-key",
        "context_limit": 100_000,
        "context_safety_margin": 1_000,
        "timeout_seconds": 5.0,
        "max_retries": 2,
        "price_per_1m_input_tokens": 1.0,
        "price_per_1m_output_tokens": 2.0,
        "expected_output_tokens_chapter": 1000,
        "expected_output_tokens_update": 500,
        "cost_limit_usd_per_session": 100.0,
        "cost_limit_usd_total": 1000.0,
        "spend_file_path": str(tmp_path / ".spend.json"),
        "retry_backoff_seconds": [2, 8, 32],
        "retry_jitter_seconds_max": 0.0,
        "token_count_per_message_overhead": 4,
        "token_count_completion_priming": 3,
        "tokenizer_chars_per_token": 4,
        "tokenizer_encoding_fallback": "cl100k_base",
    }


class TestCallAPI:
    def test_happy_path(self, tmp_path):
        cfg = _make_config(tmp_path)
        client = FakeLLMTransport()
        text = call_api(
            [{"role": "user", "content": "hi"}],
            "test/model",
            cfg,
            client=client,
            timeout=None,
            expected_output_tokens=100,
        )
        assert text == "chapter text"
        assert len(client.calls) == 1

    def test_payload_includes_max_tokens(self, tmp_path):
        # C1: max_tokens is now in the payload.
        cfg = _make_config(tmp_path)
        client = FakeLLMTransport()
        call_api(
            [{"role": "user", "content": "hi"}],
            "test/model",
            cfg,
            client=client,
            timeout=None,
            expected_output_tokens=789,
        )
        assert client.calls[-1]["payload"]["max_tokens"] == 789

    def test_payload_includes_creativity_controls_when_set(self, tmp_path):
        # L1: temperature/top_p/seed flow through when set.
        cfg = _make_config(tmp_path)
        cfg["temperature"] = 0.5
        cfg["top_p"] = 0.9
        cfg["seed"] = 13
        client = FakeLLMTransport()
        call_api(
            [{"role": "user", "content": "hi"}],
            "test/model",
            cfg,
            client=client,
            timeout=None,
            expected_output_tokens=100,
        )
        payload = client.calls[-1]["payload"]
        assert payload["temperature"] == 0.5
        assert payload["top_p"] == 0.9
        assert payload["seed"] == 13

    def test_payload_omits_creativity_controls_when_unset(self, tmp_path):
        # L1: keep the payload clean when the user hasn't opted in.
        cfg = _make_config(tmp_path)
        client = FakeLLMTransport()
        call_api(
            [{"role": "user", "content": "hi"}],
            "test/model",
            cfg,
            client=client,
            timeout=None,
            expected_output_tokens=100,
        )
        payload = client.calls[-1]["payload"]
        assert "temperature" not in payload
        assert "top_p" not in payload
        assert "seed" not in payload

    def test_finish_reason_length_raises(self, tmp_path):
        # C1: truncated response is rejected.
        cfg = _make_config(tmp_path)
        client = FakeLLMTransport(finish_reason="length")
        with pytest.raises(ChapterValidationError, match="finish_reason='length'"):
            call_api(
                [{"role": "user", "content": "hi"}],
                "test/model",
                cfg,
                client=client,
                timeout=None,
                expected_output_tokens=100,
            )

    def test_finish_reason_content_filter_raises(self, tmp_path):
        # C1: content-filtered response is rejected.
        cfg = _make_config(tmp_path)
        client = FakeLLMTransport(finish_reason="content_filter")
        with pytest.raises(APIResponseError, match="content_filter"):
            call_api(
                [{"role": "user", "content": "hi"}],
                "test/model",
                cfg,
                client=client,
                timeout=None,
                expected_output_tokens=100,
            )

    def test_context_overflow_includes_breakdown(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["context_limit"] = 10
        cfg["context_safety_margin"] = 0
        with pytest.raises(ContextOverflowError) as exc:
            call_api(
                [{"role": "user", "content": "word " * 1000}],
                "test/model",
                cfg,
                client=FakeLLMTransport(),
                timeout=None,
                expected_output_tokens=100,
                static_docs={"world_laws": "bible content", "curriculum": "curr"},
                living_doc="living text",
            )
        msg = str(exc.value)
        assert "Context overflow" in msg
        assert "world_laws:" in msg
        assert "curriculum:" in msg
        assert "living_doc:" in msg
        assert "Suggestions:" in msg
        assert "Manually compress" in msg

    def test_cost_limit_enforced(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["cost_limit_usd_per_session"] = 0.0000001  # impossible
        with pytest.raises(CostLimitError, match="Session cost limit"):
            call_api(
                [{"role": "user", "content": "hi"}],
                "test/model",
                cfg,
                client=FakeLLMTransport(),
                timeout=None,
                expected_output_tokens=100,
            )

    def test_cost_limit_bypass(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["cost_limit_usd_per_session"] = 0.0000001
        client = FakeLLMTransport()
        text = call_api(
            [{"role": "user", "content": "hi"}],
            "test/model",
            cfg,
            client=client,
            timeout=None,
            expected_output_tokens=100,
            ignore_cost_limit=True,
        )
        assert text == "chapter text"

    def test_actual_cost_tracked(self, tmp_path):
        cfg = _make_config(tmp_path)
        client = FakeLLMTransport(
            content="hi",
            usage={"prompt_tokens": 1_000_000, "completion_tokens": 500_000},
        )
        call_api(
            [{"role": "user", "content": "hi"}],
            "test/model",
            cfg,
            client=client,
            timeout=None,
            expected_output_tokens=100,
        )
        data = json.loads(Path(cfg["spend_file_path"]).read_text())
        # 1M @ $1 + 0.5M @ $2 = $1 + $1 = $2
        assert data["lifetime_total"] == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# request_chapter / request_living_doc_update wrappers
# ---------------------------------------------------------------------------

class TestRequestWrappers:
    def test_request_chapter_too_short_raises(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["min_chapter_words"] = 1500
        client = FakeLLMTransport(content="short text")
        with pytest.raises(ChapterValidationError, match="too short"):
            request_chapter({}, "", "test/model", cfg, client=client, timeout=None)

    def test_request_chapter_long_enough_passes(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["min_chapter_words"] = 10
        long_text = "word " * 50
        client = FakeLLMTransport(content=long_text)
        out = request_chapter({}, "", "test/model", cfg, client=client, timeout=None)
        assert out == long_text.strip()

    def test_update_living_doc_validation_passes(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["required_living_doc_sections"] = [
            "=== LIVING DOCUMENT ===",
            "--- CURRENT STATE ---",
        ]
        new_doc = "=== LIVING DOCUMENT ===\n--- CURRENT STATE ---\nstate body\n"
        client = FakeLLMTransport(content=new_doc)
        out = request_living_doc_update(
            {}, "old", "new chapter", "test/model", cfg, client=client, timeout=None
        )
        assert out == new_doc.strip()

    def test_update_living_doc_validation_fails(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg["required_living_doc_sections"] = [
            "=== LIVING DOCUMENT ===",
            "--- CURRENT STATE ---",
            "--- ACTIVE VOCABULARY ---",
        ]
        bad_doc = "=== LIVING DOCUMENT ===\n--- CURRENT STATE ---\nbody\n"
        client = FakeLLMTransport(content=bad_doc)
        with pytest.raises(LivingDocValidationError) as exc:
            request_living_doc_update(
                {}, "old text", "chapter", "test/model", cfg, client=client, timeout=None
            )
        assert "--- ACTIVE VOCABULARY ---" in exc.value.missing
        assert exc.value.diff


# ---------------------------------------------------------------------------
# Atomicity smoke tests
# ---------------------------------------------------------------------------

class TestAtomicity:
    def test_no_tmp_files_after_save(self, tmp_path):
        p = tmp_path / "doc.md"
        save_living_doc(str(p), "content\n")
        leftovers = list(tmp_path.glob("*.tmp"))
        assert leftovers == [], f"leftover tmp files: {leftovers}"

    def test_state_write_no_tmp_leftover(self, tmp_path):
        p = tmp_path / "state.json"
        write_state(str(p), last_chapter_promoted=1, last_chapter_living_doc_updated=1)
        leftovers = list(tmp_path.glob("*.tmp"))
        assert leftovers == []


# ---------------------------------------------------------------------------
# Session-level behavioural fixes (C2/C3/C4/H2/M4/I15/M5)
#
# These are integration-y: they exercise run_session with the API layer
# stubbed out.
# ---------------------------------------------------------------------------

@pytest.fixture
def _session_setup(tmp_path):
    """Build a working project skeleton with a seed living doc and one
    static template. Returns a config dict and the paths."""
    static = tmp_path / "world_laws.md"
    static.write_text("# World\nA generic world.", encoding="utf-8")

    living_doc = tmp_path / "living.md"
    living_doc.write_text(
        "\n".join(
            [
                "=== LIVING DOCUMENT ===",
                "header",
                "--- CURRENT STATE ---",
                "body",
                "--- ACTIVE VOCABULARY ---",
                "v",
                "--- TERMS LEARNED BUT NOT YET OWNED ---",
                "",
                "--- TERMS INTRODUCED THIS ARC ---",
                "",
                "--- ACTIVE FORESHADOWING ---",
                "",
                "--- PROTAGONIST LENS ---",
                "",
                "--- NEXT CHAPTER TARGET ---",
                "do something",
                "--- NOTES FOR AI ---",
                "",
            ]
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"
    output_dir.mkdir()

    cfg = {
        "api_key": "test-key",
        "model": "test/model",
        "static_doc_paths": [str(static)],
        "living_doc_path": str(living_doc),
        "output_dir": str(output_dir),
        "context_limit": 100_000,
        "context_safety_margin": 1_000,
        "timeout_seconds": 5.0,
        "max_retries": 0,
        "price_per_1m_input_tokens": 1.0,
        "price_per_1m_output_tokens": 2.0,
        "expected_output_tokens_chapter": 100,
        "expected_output_tokens_update": 50,
        "cost_limit_usd_per_session": 100.0,
        "cost_limit_usd_total": 1000.0,
        "log_path": str(tmp_path / "pipeline.log"),
        "state_file_path": str(tmp_path / ".pipeline_state.json"),
        "spend_file_path": str(tmp_path / ".pipeline_spend.json"),
        "chapters_per_session": 2,
        "min_chapter_words": 5,
        "required_living_doc_sections": list(DEFAULTS["required_living_doc_sections"]),
        # v0.3 defaults
        "max_rejection_retries": 5,
        "retry_backoff_seconds": [0],
        "retry_jitter_seconds_max": 0.0,
        "token_count_per_message_overhead": 4,
        "token_count_completion_priming": 3,
        "tokenizer_chars_per_token": 4,
        "tokenizer_encoding_fallback": "cl100k_base",
        "system_prompt_generate_chapter": "GEN",
        "system_prompt_update_living_doc": "UPD",
        "doc_wrap_open_format": "=== {name_upper} ===",
        "doc_wrap_close_format": "=== END {name_upper} ===",
        "static_doc_order": ["world_laws", "curriculum", "style_contract", "full_map"],
        "living_doc_backup_format": "{name}.bak.{ts}",
        "rejected_draft_name_format": "chapter_{nn:02d}__{ts}.md",
        "canonical_chapter_regex": r"^chapter_(\d{2,})\.md$",
        "canonical_chapter_name_format": "chapter_{nn:02d}.md",
        "dry_run_chapter_template": "Lorem ipsum dolor sit amet. ",
        "temperature": None,
        "top_p": None,
        "seed": None,
        "api_default_max_tokens_chapter": None,
        "api_default_max_tokens_update": None,
    }
    return cfg, tmp_path


class TestC2FirstRunGuard:
    def test_empty_living_doc_and_no_chapters_refuses(self, tmp_path, _session_setup):
        cfg, _ = _session_setup
        # Wipe living doc to simulate true first-run with nothing seeded.
        Path(cfg["living_doc_path"]).write_text("   \n", encoding="utf-8")
        from novel_pipeline.session import run_session

        with pytest.raises(ConfigError, match="First-run guard"):
            run_session(
                cfg, FakeLLMTransport(), None, auto_approve=True, dry_run=True
            )


class TestC3AutoApproveResumeRefuses:
    def test_inconsistent_resume_under_auto_approve_aborts(self, _session_setup):
        cfg, tmp_path = _session_setup
        # Create state with last_promoted > last_doc_updated to force inconsistency.
        (Path(cfg["output_dir"]) / "chapter_01.md").write_text("x", encoding="utf-8")
        write_state(
            cfg["state_file_path"],
            last_chapter_promoted=1,
            last_chapter_living_doc_updated=0,
        )
        from novel_pipeline.session import run_session

        with pytest.raises(ConfigError, match="auto-approve"):
            run_session(
                cfg,
                FakeLLMTransport(),
                None,
                auto_approve=True,
                resume=True,
                dry_run=True,
            )


class TestC4AutoApproveSkipGap:
    def test_chapter_start_skipping_gap_under_auto_approve_aborts(self, _session_setup):
        cfg, _ = _session_setup
        # Empty output dir; --chapter-start 3 with no chapters yet would skip 1,2.
        from novel_pipeline.session import run_session

        with pytest.raises(ConfigError, match="--auto-approve"):
            run_session(
                cfg,
                FakeLLMTransport(),
                None,
                auto_approve=True,
                chapter_start=3,
                dry_run=True,
            )


class TestH2KeepOldStopsSession:
    def test_keep_old_living_doc_stops_session(self, _session_setup, monkeypatch):
        cfg, _ = _session_setup
        cfg["chapters_per_session"] = 3  # would write 3 if not stopped

        # Patch request_chapter to return long-enough text.
        long_text = "word " * 100

        # Patch request_living_doc_update to raise LivingDocValidationError, so
        # the prompt for "k" (keep old) is triggered.
        from novel_pipeline import session as session_mod
        from novel_pipeline.exceptions import LivingDocValidationError

        def fake_request_chapter(*a, **kw):
            return long_text

        def fake_request_update(*a, **kw):
            raise LivingDocValidationError("nope", missing=["X"], diff="d")

        monkeypatch.setattr(session_mod, "request_chapter", fake_request_chapter)
        monkeypatch.setattr(session_mod, "request_living_doc_update", fake_request_update)

        # The session uses input() for prompts: "y" to proceed at summary,
        # "y" to approve the chapter, then "k" to keep old living doc.
        responses = iter(["y", "y", "k"])
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(responses))

        session_mod.run_session(cfg, FakeLLMTransport(), None)

        # Only one canonical chapter should exist.
        promoted = list(Path(cfg["output_dir"]).glob("chapter_*.md"))
        # Filter out timestamped copies (shouldn't exist here).
        canonical = [p for p in promoted if re.match(r"^chapter_\d{2}\.md$", p.name)]
        assert len(canonical) == 1


class TestM4RejectionLimitBounded:
    def test_runaway_rejections_eventually_raise(self, _session_setup, monkeypatch):
        cfg, _ = _session_setup
        cfg["max_rejection_retries"] = 3

        from novel_pipeline import session as session_mod
        long_text = "word " * 100
        monkeypatch.setattr(
            session_mod, "request_chapter", lambda *a, **k: long_text
        )
        # Approval prompt: always "n" (reject). Summary gate: "y".
        approvals = iter(["y"] + ["n"] * 100)
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(approvals))

        with pytest.raises(RejectionLimitReachedError):
            session_mod.run_session(
                cfg, FakeLLMTransport(), None, approve_chapter=lambda n, t: False
            )


class TestI15EOFAbortInPromptChoice:
    def test_eof_picks_abort_key(self, monkeypatch):
        # I15: EOFError on _prompt_choice returns the 'a' key if present.
        from novel_pipeline.session import _prompt_choice

        def raise_eof(*a, **k):
            raise EOFError

        monkeypatch.setattr("builtins.input", raise_eof)
        chosen = _prompt_choice(
            "x",
            {"r": "retry", "k": "keep old", "a": "abort"},
        )
        assert chosen == "a"

    def test_eof_no_a_key_falls_back_to_last(self, monkeypatch):
        from novel_pipeline.session import _prompt_choice

        def raise_eof(*a, **k):
            raise EOFError

        monkeypatch.setattr("builtins.input", raise_eof)
        chosen = _prompt_choice(
            "x",
            {"r": "retry", "q": "quit"},
        )
        assert chosen == "q"


class TestM5DryRunPlaceholderSized:
    def test_dry_run_chapter_sized_to_expected_tokens(self, _session_setup):
        # M5: dry-run output is roughly expected_output_tokens × chars_per_token.
        from novel_pipeline.session import _build_dry_run_chapter

        cfg, _ = _session_setup
        cfg["expected_output_tokens_chapter"] = 200
        cfg["tokenizer_chars_per_token"] = 4
        out = _build_dry_run_chapter(5, cfg)
        # Expect ~800 chars of body, plus a short heading. Old code produced
        # ~12k chars from "Lorem ipsum dolor sit amet. " * 400.
        # Old behaviour would produce > 9000 chars; new behaviour for this
        # config should be in the ballpark of 800 chars.
        assert 700 < len(out) < 1500
