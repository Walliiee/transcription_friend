"""Tests for config.py -- path generation and filename helpers."""

from pathlib import Path

import config


class TestGetInterviewPaths:
    def test_default_base_dir(self):
        paths = config.get_interview_paths("Alice")
        assert paths["base"] == config.BASE_DIR / "interviews" / "Alice"
        assert paths["audio"].name == "audio"
        assert paths["transcriptions"].name == "transcriptions"

    def test_custom_base_dir(self, tmp_path):
        paths = config.get_interview_paths("Bob", base_dir=tmp_path)
        assert paths["base"] == tmp_path / "interviews" / "Bob"
        assert paths["audio_segments"] == tmp_path / "interviews" / "Bob" / "audio" / "segments"

    def test_all_expected_keys_present(self):
        paths = config.get_interview_paths("Test")
        expected_keys = {"base", "audio", "audio_segments", "transcriptions", "transcription_segments"}
        assert set(paths.keys()) == expected_keys


class TestGetOutputFilename:
    def test_basic_filename(self):
        result = config.get_output_filename("Alice", "da")
        assert result == "Alice_transcription_da.txt"

    def test_reviewed_filename(self):
        result = config.get_output_filename("Alice", "en", reviewed=True)
        assert result == "Alice_transcription_en_reviewed.txt"

    def test_report_filename(self):
        result = config.get_output_filename("Alice", "da", is_report=True)
        assert result == "Alice_transcription_da_review_report.txt"

    def test_report_takes_precedence_over_reviewed(self):
        result = config.get_output_filename("Alice", "en", reviewed=True, is_report=True)
        assert "review_report" in result


class TestConfigConstants:
    def test_supported_languages(self):
        assert "da" in config.SUPPORTED_LANGUAGES
        assert "en" in config.SUPPORTED_LANGUAGES

    def test_default_model_is_valid(self):
        assert config.DEFAULT_MODEL in ("tiny", "base", "small", "medium", "large")

    def test_base_dir_is_directory(self):
        assert config.BASE_DIR.is_dir()
