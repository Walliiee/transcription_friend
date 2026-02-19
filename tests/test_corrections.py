"""Tests for utils/corrections.py -- correction dicts and review flags."""

import pytest

from utils.corrections import (
    CORRECTIONS_DA,
    CORRECTIONS_EN,
    REVIEW_FLAGS_DA,
    REVIEW_FLAGS_EN,
    get_corrections,
    get_review_flags,
)


class TestGetCorrections:
    def test_english_corrections(self):
        result = get_corrections("en")
        assert result is CORRECTIONS_EN

    def test_danish_corrections(self):
        result = get_corrections("da")
        assert result is CORRECTIONS_DA

    def test_default_is_danish(self):
        assert get_corrections() is CORRECTIONS_DA

    def test_unsupported_language_raises(self):
        with pytest.raises(ValueError, match="Unsupported language"):
            get_corrections("fr")


class TestGetReviewFlags:
    def test_english_flags(self):
        result = get_review_flags("en")
        assert result is REVIEW_FLAGS_EN

    def test_danish_flags(self):
        result = get_review_flags("da")
        assert result is REVIEW_FLAGS_DA

    def test_default_is_danish(self):
        assert get_review_flags() is REVIEW_FLAGS_DA

    def test_unsupported_language_raises(self):
        with pytest.raises(ValueError, match="Unsupported language"):
            get_review_flags("fr")


class TestCorrectionDictContents:
    def test_en_corrections_not_empty(self):
        assert len(CORRECTIONS_EN) > 0

    def test_da_corrections_not_empty(self):
        assert len(CORRECTIONS_DA) > 0

    def test_corrections_are_str_to_str(self):
        for wrong, correct in CORRECTIONS_EN.items():
            assert isinstance(wrong, str)
            assert isinstance(correct, str)

    def test_review_flags_are_strings(self):
        for flag in REVIEW_FLAGS_EN:
            assert isinstance(flag, str) and len(flag) > 0
        for flag in REVIEW_FLAGS_DA:
            assert isinstance(flag, str) and len(flag) > 0
