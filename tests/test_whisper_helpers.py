"""Tests for utils/whisper_helpers.py -- timestamp formatting and save logic."""

import pytest

from utils.whisper_helpers import format_timestamp, save_transcription


class TestFormatTimestamp:
    def test_zero(self):
        assert format_timestamp(0) == "00:00:00"

    def test_seconds_only(self):
        assert format_timestamp(45) == "00:00:45"

    def test_minutes_and_seconds(self):
        assert format_timestamp(125) == "00:02:05"

    def test_hours_minutes_seconds(self):
        assert format_timestamp(3661) == "01:01:01"

    def test_fractional_seconds_truncated(self):
        assert format_timestamp(59.9) == "00:00:59"

    def test_large_duration(self):
        """Durations over 24 hours should still render correctly."""
        assert format_timestamp(90000) == "25:00:00"

    def test_exactly_one_hour(self):
        assert format_timestamp(3600) == "01:00:00"


class TestSaveTranscription:
    def test_saves_plain_text(self, tmp_path):
        out = tmp_path / "out.txt"
        save_transcription("Hello world", out)
        assert out.read_text(encoding="utf-8") == "Hello world"

    def test_saves_with_metadata(self, tmp_path):
        out = tmp_path / "out.txt"
        metadata = {
            "audio_file": "test.m4a",
            "language": "da",
            "duration": 123.45,
            "interviewer": "Alex",
            "interviewee": "Bob",
        }
        save_transcription("content here", out, metadata)
        text = out.read_text(encoding="utf-8")
        assert "test.m4a" in text
        assert "Danish" in text
        assert "123.45" in text
        assert "Alex" in text
        assert "Bob" in text
        assert text.endswith("content here")

    def test_saves_english_language_label(self, tmp_path):
        out = tmp_path / "out.txt"
        save_transcription("text", out, {"language": "en"})
        assert "English" in out.read_text(encoding="utf-8")

    def test_creates_file(self, tmp_path):
        out = tmp_path / "subdir" / "out.txt"
        out.parent.mkdir()
        save_transcription("data", out)
        assert out.exists()
