"""
Shared utilities for audio transcription workspace
"""

from .corrections import CORRECTIONS_DA, CORRECTIONS_EN, REVIEW_FLAGS_DA, REVIEW_FLAGS_EN
from .whisper_helpers import format_timestamp, save_transcription

__all__ = [
    "CORRECTIONS_DA",
    "CORRECTIONS_EN",
    "REVIEW_FLAGS_DA",
    "REVIEW_FLAGS_EN",
    "format_timestamp",
    "save_transcription",
]


def __getattr__(name: str):
    """Lazy imports for functions that require faster_whisper at runtime."""
    if name in ("load_model", "transcribe_file"):
        from . import whisper_helpers

        return getattr(whisper_helpers, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
