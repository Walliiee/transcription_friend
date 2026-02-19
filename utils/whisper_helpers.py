"""
Shared Whisper model utilities for transcription
Provides model loading, timestamp formatting, and transcription functions
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format

    Args:
        seconds (float): Time in seconds

    Returns:
        str: Formatted timestamp string (HH:MM:SS)
    """
    total = int(timedelta(seconds=seconds).total_seconds())
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def load_model(
    model_size: str = "medium",
    device_preference: str = "cuda",
    gpu_compute_type: str = "float16",
    cpu_compute_type: str = "int8",
) -> tuple[WhisperModel, str]:
    """
    Load Whisper model with automatic GPU/CPU fallback

    Args:
        model_size: Model size (tiny, base, small, medium, large)
        device_preference: Preferred device ("cuda" or "cpu")
        gpu_compute_type: Compute type for GPU (default: "float16")
        cpu_compute_type: Compute type for CPU (default: "int8")

    Returns:
        Tuple of (model, device_used) where device_used is "cuda" or "cpu"
    """
    print(f"Loading Whisper {model_size} model...")

    if device_preference == "cuda":
        try:
            print("Attempting to load model on GPU with CUDA acceleration...")
            model = WhisperModel(model_size, device="cuda", compute_type=gpu_compute_type)
            print("[OK] Successfully loaded model on GPU!")
            return model, "cuda"
        except Exception as e:
            print(f"GPU failed: {e}")
            print("Falling back to CPU...")

    # Use CPU (either as preference or fallback)
    model = WhisperModel(model_size, device="cpu", compute_type=cpu_compute_type)
    print("[OK] Model loaded on CPU")
    return model, "cpu"


def transcribe_file(
    model: WhisperModel,
    audio_file: str | Path,
    language: str = "da",
    beam_size: int = 5,
    vad_filter: bool = True,
    word_timestamps: bool = True,
) -> tuple[str, dict[str, Any]]:
    """
    Transcribe a single audio file with the given parameters

    Args:
        model: Loaded WhisperModel instance
        audio_file: Path to audio file
        language: Language code (e.g., "da", "en")
        beam_size: Beam size for transcription (default: 5)
        vad_filter: Enable voice activity detection (default: True)
        word_timestamps: Generate word-level timestamps (default: True)

    Returns:
        Tuple of (formatted_transcription, info_dict) where info_dict contains
        language, language_probability, and duration.
    """
    audio_path = Path(audio_file)
    print(f"Transcribing {audio_path.name}...")

    # Perform transcription
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
        word_timestamps=word_timestamps
    )

    print(f"  Detected language: {info.language} (probability: {info.language_probability:.2f})")

    # Format with timestamps
    output_lines = []
    for segment in segments:
        timestamp = format_timestamp(segment.start)
        text = segment.text.strip()
        output_lines.append(f"[{timestamp}] {text}")

    formatted_transcription = "\n\n".join(output_lines)

    # Build info dictionary
    info_dict = {
        'language': info.language,
        'language_probability': info.language_probability,
        'duration': info.duration
    }

    return formatted_transcription, info_dict


def save_transcription(
    transcription: str,
    output_path: str | Path,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Save transcription to file with optional metadata header

    Args:
        transcription: The formatted transcription text
        output_path: Output file path
        metadata: Metadata to include in header.
            Supported keys: 'audio_file', 'language', 'duration', 'interviewee', 'interviewer'
    """
    output_path = Path(output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        if metadata:
            # Write metadata header
            if 'audio_file' in metadata:
                f.write(f"# Transcription of {metadata['audio_file']}\n")
            if 'interviewer' in metadata and 'interviewee' in metadata:
                f.write(f"# Interviewer: {metadata['interviewer']} | Interviewee: {metadata['interviewee']}\n")
            if 'language' in metadata:
                lang_name = "Danish" if metadata['language'] == "da" else "English"
                f.write(f"# Language: {lang_name}\n")
            if 'duration' in metadata:
                f.write(f"# Duration: {metadata['duration']:.2f} seconds\n")
            f.write("\n")

        f.write(transcription)

    print(f"  [OK] Saved to {output_path}")
