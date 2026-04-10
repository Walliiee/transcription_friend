"""Shared utilities for audio transcription workspace."""

from .corrections import CORRECTIONS_DA, CORRECTIONS_EN, REVIEW_FLAGS_DA, REVIEW_FLAGS_EN

__all__ = ["CORRECTIONS_DA", "CORRECTIONS_EN", "REVIEW_FLAGS_DA", "REVIEW_FLAGS_EN"]

try:
    # Optional dependency path: importing whisper helpers requires faster-whisper.
    from .whisper_helpers import format_timestamp, load_model, transcribe_file

    __all__ += ["format_timestamp", "load_model", "transcribe_file"]
except ModuleNotFoundError:
    # Keep corrections utilities importable in environments without transcription deps.
    pass
