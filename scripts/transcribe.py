#!/usr/bin/env python3
"""
Unified transcription script for audio interviews
Replaces all person-specific transcription scripts with a single configurable tool

Usage:
    python scripts/transcribe.py --audio "Person/Person.m4a" --name Person --language da
    python scripts/transcribe.py --audio "Speaker/Speaker.m4a" --name Speaker --language en
    python scripts/transcribe.py --segments "Person_segment_*.m4a" --name Person --language da
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.whisper_helpers import load_model, transcribe_file, save_transcription, format_timestamp
import config


def transcribe_single_file(model, audio_file, language, name, interviewer=None, output_dir=None):
    """
    Transcribe a single audio file

    Args:
        model: Loaded Whisper model
        audio_file (Path): Path to audio file
        language (str): Language code (da, en)
        name (str): Interviewee name
        interviewer (str, optional): Interviewer name
        output_dir (Path, optional): Output directory
    """
    # Transcribe
    transcription, info = transcribe_file(
        model,
        audio_file,
        language=language,
        beam_size=config.BEAM_SIZE,
        vad_filter=config.VAD_FILTER,
        word_timestamps=config.WORD_TIMESTAMPS
    )

    # Determine output path
    if output_dir is None:
        output_dir = Path.cwd()

    output_file = output_dir / config.get_output_filename(name, language)

    # Prepare metadata
    metadata = {
        'audio_file': audio_file.name,
        'language': language,
        'duration': info['duration'],
        'interviewee': name,
        'interviewer': interviewer or config.DEFAULT_INTERVIEWER,
    }

    # Save transcription
    save_transcription(transcription, output_file, metadata)

    # Show preview
    preview_lines = transcription.split('\n')[:2]
    preview = '\n  '.join(preview_lines)
    print(f"  Preview:\n  {preview}\n")

    return output_file, transcription, info


def transcribe_segments(model, segment_pattern, language, name, interviewer=None, output_dir=None):
    """
    Transcribe multiple audio segments and combine them

    Args:
        model: Loaded Whisper model
        segment_pattern (str): Glob pattern for segment files (e.g., "T_segment_*.m4a")
        language (str): Language code (da, en)
        name (str): Interviewee name
        interviewer (str, optional): Interviewer name
        output_dir (Path, optional): Output directory for combined file

    Returns:
        tuple: (combined_file_path, segment_files_list)
    """
    # Find all segment files
    audio_files = sorted(Path(".").glob(segment_pattern))

    if not audio_files:
        print(f"Error: No files found matching pattern '{segment_pattern}'")
        sys.exit(1)

    print(f"Found {len(audio_files)} audio segments to transcribe\n")

    # Store all transcriptions
    all_transcriptions = []
    segment_files = []

    # Transcribe each segment
    for audio_file in audio_files:
        transcription, info = transcribe_file(
            model,
            audio_file,
            language=language,
            beam_size=config.BEAM_SIZE,
            vad_filter=config.VAD_FILTER,
            word_timestamps=config.WORD_TIMESTAMPS
        )

        # Save individual segment
        segment_output = audio_file.stem + config.TRANSCRIPTION_SUFFIX + ".txt"
        metadata = {
            'audio_file': audio_file.name,
            'language': language,
            'duration': info['duration']
        }
        save_transcription(transcription, segment_output, metadata)

        all_transcriptions.append(transcription)
        segment_files.append(segment_output)

        # Show preview
        preview = transcription.split('\n')[0] if transcription else ""
        print(f"  Preview: {preview[:80]}...\n")

    # Create combined transcription
    print("Creating combined transcription file...")

    if output_dir is None:
        output_dir = Path.cwd()

    combined_file = output_dir / config.get_output_filename(name, language)

    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("# Complete Interview Transcription\n")
        if interviewer:
            f.write(f"# Interviewer: {interviewer} | Interviewee: {name}\n")
        else:
            f.write(f"# Interviewee: {name}\n")

        lang_name = "Danish" if language == "da" else "English"
        f.write(f"# Language: {lang_name}\n\n")
        f.write("=" * 60 + "\n\n")

        for i, transcription in enumerate(all_transcriptions, 1):
            f.write(f"## Segment {i}\n\n")
            f.write(transcription)
            f.write("\n\n" + "=" * 60 + "\n\n")

    print(f"✓ Combined transcription saved to {combined_file}")
    print(f"\nAll done! Created files:")
    for sf in segment_files:
        print(f"  - {sf}")
    print(f"  - {combined_file}")

    return combined_file, segment_files


def main():
    parser = argparse.ArgumentParser(
        description="Unified transcription script for audio interviews",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single audio file
  python scripts/transcribe.py --audio "Person/Person.m4a" --name Person --language da

  # Multiple segments
  python scripts/transcribe.py --segments "Person_segment_*.m4a" --name Person --language da

  # With custom interviewer
  python scripts/transcribe.py --audio "Speaker/Speaker.m4a" --name Speaker --language en --interviewer Alex

  # CPU-only mode
  python scripts/transcribe.py --audio "audio.m4a" --name Person --language da --device cpu
        """
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--audio",
        type=str,
        help="Single audio file to transcribe"
    )
    input_group.add_argument(
        "--segments",
        type=str,
        help="Glob pattern for audio segments (e.g., 'Person_segment_*.m4a')"
    )

    # Required arguments
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Interviewee name (used in output filename)"
    )
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        choices=config.SUPPORTED_LANGUAGES,
        help="Transcription language"
    )

    # Optional arguments
    parser.add_argument(
        "--interviewer",
        type=str,
        default=config.DEFAULT_INTERVIEWER,
        help=f"Interviewer name (default: {config.DEFAULT_INTERVIEWER})"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=config.DEFAULT_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help=f"Whisper model size (default: {config.DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=config.DEFAULT_DEVICE,
        choices=["cuda", "cpu"],
        help=f"Device to use (default: {config.DEFAULT_DEVICE})"
    )

    args = parser.parse_args()

    # Prepare output directory
    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    model, device_used = load_model(
        model_size=args.model,
        device_preference=args.device,
        gpu_compute_type=config.GPU_COMPUTE_TYPE,
        cpu_compute_type=config.CPU_COMPUTE_TYPE
    )

    print(f"Device: {device_used}")
    print(f"Language: {args.language}")
    print(f"Interviewee: {args.name}\n")

    # Transcribe based on input type
    if args.audio:
        # Single file
        audio_file = Path(args.audio)
        if not audio_file.exists():
            print(f"Error: Audio file not found: {audio_file}")
            sys.exit(1)

        output_file, _, _ = transcribe_single_file(
            model,
            audio_file,
            args.language,
            args.name,
            args.interviewer,
            output_dir
        )

        print(f"\n[OK] Transcription complete: {output_file}")
        print("\nNote: You may need to manually review and add speaker labels based on the content.")

    else:
        # Multiple segments
        combined_file, segment_files = transcribe_segments(
            model,
            args.segments,
            args.language,
            args.name,
            args.interviewer,
            output_dir
        )

        print("\nNote: You may need to manually review and add speaker labels based on the content.")


if __name__ == "__main__":
    main()
