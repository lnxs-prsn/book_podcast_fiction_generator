"""Tests for util.normalize.normalize_speakers — all speaker-label variant transformations."""

import pytest

from util.normalize import normalize_speakers


class TestMode2PersonCharacterNames:
    """ALEX / JORDAN character names (mode_2person) — bold and plain."""

    def test_alex_plain(self):
        result = normalize_speakers("ALEX: Hello there.")
        assert result == "Speaker 0: Hello there."

    def test_alex_bold(self):
        result = normalize_speakers("**ALEX:** Hello there.")
        assert result == "Speaker 0: Hello there."

    def test_jordan_plain(self):
        result = normalize_speakers("JORDAN: Good point.")
        assert result == "Speaker 1: Good point."

    def test_jordan_bold(self):
        result = normalize_speakers("**JORDAN:** Good point.")
        assert result == "Speaker 1: Good point."


class TestHostGuestExpert:
    """HOST / GUEST / EXPERT labels map to Speaker 0 or Speaker 1."""

    def test_host_plain(self):
        result = normalize_speakers("HOST: Welcome.")
        assert result == "Speaker 0: Welcome."

    def test_guest_plain(self):
        result = normalize_speakers("GUEST: Thank you.")
        assert result == "Speaker 1: Thank you."

    def test_expert_plain(self):
        result = normalize_speakers("EXPERT: Indeed.")
        assert result == "Speaker 1: Indeed."

    def test_bold_h(self):
        result = normalize_speakers("**H:** Welcome to the show.")
        assert result == "Speaker 0: Welcome to the show."

    def test_bold_e(self):
        result = normalize_speakers("**E:** Absolutely.")
        assert result == "Speaker 1: Absolutely."

    def test_named_expert_bold(self):
        result = normalize_speakers("**EXPERT Jordan:** Right.")
        assert result == "Speaker 1: Right."

    def test_named_expert_plain(self):
        result = normalize_speakers("EXPERT Jordan: Right.")
        assert result == "Speaker 1: Right."

    def test_named_guest_bold(self):
        result = normalize_speakers("**GUEST Alex:** Hello.")
        assert result == "Speaker 1: Hello."

    def test_named_guest_plain(self):
        result = normalize_speakers("GUEST Alex: Hello.")
        assert result == "Speaker 1: Hello."


class TestCriticNewcomer:
    """CRITIC and NEWCOMER labels."""

    def test_critic_plain(self):
        result = normalize_speakers("CRITIC: I disagree.")
        assert result == "Speaker 2: I disagree."

    def test_newcomer_plain(self):
        result = normalize_speakers("NEWCOMER: Can you explain?")
        assert result == "Speaker 3: Can you explain?"


class TestAlreadyCleanSpeakerLabels:
    """Lines already in Speaker N: format are preserved."""

    def test_speaker_0_kept(self):
        result = normalize_speakers("Speaker 0: This is fine.")
        assert result == "Speaker 0: This is fine."

    def test_speaker_1_kept(self):
        result = normalize_speakers("Speaker 1: Also fine.")
        assert result == "Speaker 1: Also fine."

    def test_bold_speaker_label_normalised(self):
        result = normalize_speakers("**Speaker 2:** With role.")
        assert result == "Speaker 2: With role."

    def test_bold_speaker_label_with_role_description(self):
        result = normalize_speakers("**Speaker 0:** (Host) Welcome.")
        assert result == "Speaker 0: Welcome."


class TestStandaloneLabelMerge:
    """Standalone 'Speaker N: ' line merges with following content line."""

    def test_standalone_label_merges_with_next_line(self):
        text = "Speaker 0: \nHello world."
        result = normalize_speakers(text)
        assert result == "Speaker 0: Hello world."

    def test_standalone_label_does_not_merge_with_another_speaker(self):
        text = "Speaker 0: \nSpeaker 1: Actually..."
        result = normalize_speakers(text)
        # Both lines should be kept; standalone Speaker 0 stays as-is before Speaker 1
        assert "Speaker 0:" in result
        assert "Speaker 1: Actually..." in result


class TestNonSpeakerLines:
    """Non-speaker lines (headers, noise) are dropped."""

    def test_section_header_dropped(self):
        text = "Speaker 0: Intro.\n# Section Header\nSpeaker 1: Response."
        result = normalize_speakers(text)
        assert "Section Header" not in result
        assert "Speaker 0: Intro." in result
        assert "Speaker 1: Response." in result

    def test_bare_narrative_dropped(self):
        text = "Speaker 0: Yes.\nWord count: ~500 words\nSpeaker 1: Good."
        result = normalize_speakers(text)
        assert "Word count" not in result

    def test_separator_dropped(self):
        text = "Speaker 0: Start.\n---\nSpeaker 1: End."
        result = normalize_speakers(text)
        assert "---" not in result
        assert "Speaker 0: Start." in result
        assert "Speaker 1: End." in result

    def test_empty_lines_ignored(self):
        text = "Speaker 0: One.\n\n\nSpeaker 1: Two."
        result = normalize_speakers(text)
        assert "Speaker 0: One." in result
        assert "Speaker 1: Two." in result


class TestTimestampMarkers:
    """[0:00-6:00] timestamp markers are stripped before processing."""

    def test_timestamp_marker_stripped(self):
        result = normalize_speakers("**[0:00-6:00]** Speaker 0: Hello.")
        assert "[0:00" not in result
        assert "Speaker 0: Hello." in result


class TestMultiLineMix:
    """Multi-line input with mixed speaker variants normalises correctly."""

    def test_multiple_speakers_in_sequence(self):
        text = (
            "ALEX: First line.\n"
            "JORDAN: Second line.\n"
            "HOST: Third line.\n"
            "CRITIC: Fourth line."
        )
        result = normalize_speakers(text)
        lines = result.split("\n\n")
        assert lines[0] == "Speaker 0: First line."
        assert lines[1] == "Speaker 1: Second line."
        assert lines[2] == "Speaker 0: Third line."
        assert lines[3] == "Speaker 2: Fourth line."

    def test_output_joined_by_double_newline(self):
        text = "Speaker 0: A.\nSpeaker 1: B."
        result = normalize_speakers(text)
        assert result == "Speaker 0: A.\n\nSpeaker 1: B."
