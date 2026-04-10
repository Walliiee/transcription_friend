from pathlib import Path

import config


def test_get_interview_paths_uses_expected_structure():
    base_dir = Path("/tmp/project")
    paths = config.get_interview_paths("Alice", base_dir=base_dir)

    assert paths["base"] == base_dir / "interviews" / "Alice"
    assert paths["audio"] == base_dir / "interviews" / "Alice" / "audio"
    assert paths["audio_segments"] == base_dir / "interviews" / "Alice" / "audio" / "segments"
    assert paths["transcriptions"] == base_dir / "interviews" / "Alice" / "transcriptions"
    assert (
        paths["transcription_segments"]
        == base_dir / "interviews" / "Alice" / "transcriptions" / "segments"
    )


def test_get_output_filename_variants():
    assert config.get_output_filename("Bob", "da") == "Bob_transcription_da.txt"
    assert config.get_output_filename("Bob", "da", reviewed=True) == "Bob_transcription_da_reviewed.txt"
    assert config.get_output_filename("Bob", "da", is_report=True) == "Bob_transcription_da_review_report.txt"
