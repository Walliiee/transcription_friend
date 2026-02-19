"""Tests for scripts/postprocess.py -- correction application and formatting."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.postprocess import apply_corrections, clean_formatting, flag_potential_issues


class TestApplyCorrections:
    def test_simple_replacement(self):
        text = "I asked Germany about it"
        corrections = {"Germany": "Gemini"}
        result, changes = apply_corrections(text, corrections)
        assert result == "I asked Gemini about it"
        assert len(changes) == 1

    def test_multiple_occurrences(self):
        text = "Germany said Germany is great"
        corrections = {"Germany": "Gemini"}
        result, changes = apply_corrections(text, corrections)
        assert result == "Gemini said Gemini is great"
        assert "2 occurrences" in changes[0]

    def test_no_match_returns_unchanged(self):
        text = "nothing to fix here"
        corrections = {"xyz": "abc"}
        result, changes = apply_corrections(text, corrections)
        assert result == text
        assert len(changes) == 0

    def test_longer_phrases_matched_first(self):
        corrections = {"cloud": "Claude", "Cloud Codes": "Cloud Code"}
        text = "Use Cloud Codes for cloud tasks"
        result, _ = apply_corrections(text, corrections)
        assert "Cloud Code" in result
        assert "Claude" in result

    def test_empty_corrections(self):
        text = "some text"
        result, changes = apply_corrections(text, {})
        assert result == text
        assert changes == []


class TestCleanFormatting:
    def test_removes_excessive_newlines(self):
        text = "line1\n\n\n\n\nline2"
        assert clean_formatting(text) == "line1\n\nline2"

    def test_fixes_spacing_before_punctuation(self):
        assert clean_formatting("hello , world .") == "hello, world."

    def test_adds_space_after_timestamp(self):
        text = "[01:02:03]Hello"
        result = clean_formatting(text)
        assert result == "[01:02:03] Hello"

    def test_preserves_correct_formatting(self):
        text = "[00:00:00] Good text, here.\n\nMore text."
        assert clean_formatting(text) == text


class TestFlagPotentialIssues:
    def test_finds_flagged_phrase(self):
        text = "We need to loading the data into the system"
        issues = flag_potential_issues(text, ["loading"])
        assert len(issues) == 1
        assert "loading" in issues[0]

    def test_case_insensitive_matching(self):
        text = "The LOADING time was slow"
        issues = flag_potential_issues(text, ["loading"])
        assert len(issues) == 1

    def test_no_flags_found(self):
        text = "Clean text without issues"
        issues = flag_potential_issues(text, ["missing_term"])
        assert len(issues) == 0

    def test_limits_to_three_occurrences(self):
        text = "loading " * 10
        issues = flag_potential_issues(text, ["loading"])
        assert len(issues) <= 3
