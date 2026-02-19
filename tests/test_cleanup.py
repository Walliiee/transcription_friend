"""Tests for scripts/cleanup_originals.py -- file discovery logic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.cleanup_originals import find_originals


class TestFindOriginals:
    def _make_files(self, tmp_path, filenames):
        interviews = tmp_path / "interviews" / "Person" / "transcriptions"
        interviews.mkdir(parents=True)
        for name in filenames:
            (interviews / name).write_text("content")
        return tmp_path / "interviews"

    def test_finds_originals(self, tmp_path):
        d = self._make_files(tmp_path, [
            "Person_transcription_da.txt",
            "Person_transcription_da_reviewed.txt",
            "Person_transcription_da_review_report.txt",
        ])
        originals = find_originals(d)
        assert len(originals) == 1
        assert originals[0].name == "Person_transcription_da.txt"

    def test_skips_reviewed_files(self, tmp_path):
        d = self._make_files(tmp_path, [
            "Person_transcription_en_reviewed.txt",
        ])
        assert find_originals(d) == []

    def test_skips_report_files(self, tmp_path):
        d = self._make_files(tmp_path, [
            "Person_transcription_da_review_report.txt",
        ])
        assert find_originals(d) == []

    def test_empty_directory(self, tmp_path):
        d = tmp_path / "interviews"
        d.mkdir()
        assert find_originals(d) == []
