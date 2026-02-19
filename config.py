"""
Central configuration for transcription project
Default settings for Whisper models, GPU, and output formatting
"""

from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Whisper Model Settings
DEFAULT_MODEL = "medium"  # Options: tiny, base, small, medium, large
BEAM_SIZE = 5
VAD_FILTER = True  # Voice activity detection
WORD_TIMESTAMPS = True

# Device Settings
DEFAULT_DEVICE = "cuda"  # Options: cuda, cpu
GPU_COMPUTE_TYPE = "float16"
CPU_COMPUTE_TYPE = "int8"

# Language Settings
DEFAULT_LANGUAGE = "da"  # Danish
SUPPORTED_LANGUAGES = ["da", "en"]

# Output Settings
OUTPUT_DIR_TEMPLATE = "interviews/{name}"
AUDIO_SUBDIR = "audio"
TRANSCRIPTION_SUBDIR = "transcriptions"
SEGMENTS_SUBDIR = "segments"

# Audio Segmentation
SEGMENT_LENGTH = 120  # seconds (2 minutes)

# File Naming
TRANSCRIPTION_SUFFIX = "_transcription"
REVIEWED_SUFFIX = "_reviewed"
REPORT_SUFFIX = "_review_report"

# Interview Metadata
DEFAULT_INTERVIEWER = "Alex"

# Hardware Information
GPU_INFO = {
    'model': 'NVIDIA GeForce RTX 5060 Laptop GPU',
    'compute_capability': 'sm_120',
    'cuda_version': '12.0',
    'notes': 'Requires PyTorch with CUDA 12.8+ for sm_120 support'
}


def get_interview_paths(name, base_dir=None):
    """
    Generate standardized paths for an interview

    Args:
        name (str): Interviewee name
        base_dir (Path, optional): Base directory (defaults to BASE_DIR)

    Returns:
        dict: Dictionary with paths for audio, transcriptions, segments
    """
    if base_dir is None:
        base_dir = BASE_DIR

    interview_dir = base_dir / "interviews" / name

    return {
        'base': interview_dir,
        'audio': interview_dir / AUDIO_SUBDIR,
        'audio_segments': interview_dir / AUDIO_SUBDIR / SEGMENTS_SUBDIR,
        'transcriptions': interview_dir / TRANSCRIPTION_SUBDIR,
        'transcription_segments': interview_dir / TRANSCRIPTION_SUBDIR / SEGMENTS_SUBDIR,
    }


def get_output_filename(name, language, reviewed=False, is_report=False):
    """
    Generate standardized output filename

    Args:
        name (str): Interviewee name
        language (str): Language code (da, en)
        reviewed (bool): Whether this is a reviewed version
        is_report (bool): Whether this is a report file

    Returns:
        str: Standardized filename
    """
    if is_report:
        return f"{name}{TRANSCRIPTION_SUFFIX}_{language}{REPORT_SUFFIX}.txt"

    if reviewed:
        return f"{name}{TRANSCRIPTION_SUFFIX}_{language}{REVIEWED_SUFFIX}.txt"

    return f"{name}{TRANSCRIPTION_SUFFIX}_{language}.txt"
