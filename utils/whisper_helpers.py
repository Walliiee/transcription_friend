"""
Shared Whisper model utilities for transcription
Provides model loading, timestamp formatting, and transcription functions
"""

from datetime import timedelta
from pathlib import Path

from faster_whisper import WhisperModel


def format_timestamp(seconds):
    """
    Convert seconds to HH:MM:SS format

    Args:
        seconds (float): Time in seconds

    Returns:
        str: Formatted timestamp string (HH:MM:SS)
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def load_model(
    model_size="medium",
    device_preference="cuda",
    gpu_compute_type="float16",
    cpu_compute_type="int8",
):
    """
    Load Whisper model with automatic GPU/CPU fallback

    Args:
        model_size (str): Model size (tiny, base, small, medium, large)
        device_preference (str): Preferred device ("cuda" or "cpu")
        gpu_compute_type (str): Compute type for GPU (default: "float16")
        cpu_compute_type (str): Compute type for CPU (default: "int8")

    Returns:
        tuple: (model, device_used) where device_used is "cuda" or "cpu"
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
    model, audio_file, language="da", beam_size=5, vad_filter=True, word_timestamps=True
):
    """
    Transcribe a single audio file with the given parameters

    Args:
        model: Loaded WhisperModel instance
        audio_file (str or Path): Path to audio file
        language (str): Language code (e.g., "da", "en")
        beam_size (int): Beam size for transcription (default: 5)
        vad_filter (bool): Enable voice activity detection (default: True)
        word_timestamps (bool): Generate word-level timestamps (default: True)

    Returns:
        tuple: (formatted_transcription, info_dict)
            formatted_transcription (str): Transcription with timestamps
            info_dict (dict): Metadata including language, duration, probability
    """
    audio_path = Path(audio_file)
    print(f"Transcribing {audio_path.name}...")

    # Perform transcription
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
        word_timestamps=word_timestamps,
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
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
    }

    return formatted_transcription, info_dict


def save_transcription(transcription, output_path, metadata=None):
    """
    Save transcription to file with optional metadata header

    Args:
        transcription (str): The formatted transcription text
        output_path (str or Path): Output file path
        metadata (dict, optional): Metadata to include in header
            Supported keys: 'audio_file', 'language', 'duration', 'interviewee', 'interviewer'
    """
    output_path = Path(output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        if metadata:
            # Write metadata header
            if "audio_file" in metadata:
                f.write(f"# Transcription of {metadata['audio_file']}\n")
            if "interviewer" in metadata and "interviewee" in metadata:
                f.write(
                    f"# Interviewer: {metadata['interviewer']} | Interviewee: {metadata['interviewee']}\n"
                )
            if "language" in metadata:
                lang_name = "Danish" if metadata["language"] == "da" else "English"
                f.write(f"# Language: {lang_name}\n")
            if "duration" in metadata:
                f.write(f"# Duration: {metadata['duration']:.2f} seconds\n")
            f.write("\n")

        f.write(transcription)

    print(f"  [OK] Saved to {output_path}")
