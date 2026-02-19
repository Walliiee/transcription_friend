#!/usr/bin/env python3
"""
Audio extraction script for video files using ffmpeg
Extracts audio from video files (mp4, mov, avi, etc.) to m4a format for transcription

Usage:
    python scripts/extract_audio.py <input_file>
    python scripts/extract_audio.py <input_file> --output <output_dir>
    python scripts/extract_audio.py --batch "videos/*.mp4"
    python scripts/extract_audio.py --batch "videos/*.mp4" --output audio/

Examples:
    # Extract audio from single video file
    python scripts/extract_audio.py "interviews/Person/Interview.mp4"

    # Extract with custom output directory
    python scripts/extract_audio.py "video.mov" --output "interviews/Person/audio/"

    # Batch process all mp4 files in a directory
    python scripts/extract_audio.py --batch "videos/*.mp4"

    # Batch process with output directory
    python scripts/extract_audio.py --batch "interviews/**/*.mov" --output "audio/"
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Tuple, Optional


def check_ffmpeg_installed() -> bool:
    """
    Check if ffmpeg and ffprobe are installed and accessible

    Returns:
        bool: True if both ffmpeg and ffprobe are available
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        subprocess.run(
            ["ffprobe", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_video_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Use ffprobe to verify if file is a video file

    Args:
        file_path (Path): Path to file to check

    Returns:
        tuple: (is_video: bool, error_message: Optional[str])
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "json",
                str(file_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )

        data = json.loads(result.stdout)
        has_video = len(data.get("streams", [])) > 0

        if not has_video:
            return False, "No video stream found in file"

        return True, None

    except subprocess.CalledProcessError as e:
        return False, f"ffprobe error: {e.stderr}"
    except json.JSONDecodeError:
        return False, "Could not parse ffprobe output"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def extract_audio(input_file: Path, output_file: Path, verbose: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Extract audio from video file using ffmpeg
    Uses codec copy for fast, lossless extraction

    Args:
        input_file (Path): Input video file
        output_file (Path): Output audio file (.m4a)
        verbose (bool): Print progress information

    Returns:
        tuple: (success: bool, error_message: Optional[str])
    """
    try:
        if verbose:
            print(f"Extracting: {input_file.name} -> {output_file.name}")

        # Extract audio with codec copy (fast, lossless)
        # -vn: no video
        # -acodec copy: copy audio codec without re-encoding
        # -y: overwrite output file if exists
        result = subprocess.run(
            [
                "ffmpeg",
                "-i", str(input_file),
                "-vn",  # No video
                "-acodec", "copy",  # Copy audio codec (fast, lossless)
                "-y",  # Overwrite output
                str(output_file)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # ffmpeg writes progress to stderr, so we check returncode instead
        if result.returncode != 0:
            # Check if error is due to codec incompatibility
            if "does not support codec" in result.stderr or "Could not write header" in result.stderr:
                if verbose:
                    print(f"  Codec copy failed, re-encoding to AAC...")

                # Fallback: re-encode to AAC
                result = subprocess.run(
                    [
                        "ffmpeg",
                        "-i", str(input_file),
                        "-vn",
                        "-acodec", "aac",
                        "-b:a", "192k",  # 192 kbps bitrate
                        "-y",
                        str(output_file)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode != 0:
                    return False, f"ffmpeg error: {result.stderr}"
            else:
                return False, f"ffmpeg error: {result.stderr}"

        if verbose:
            print(f"  Success: {output_file}")

        return True, None

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def process_single_file(input_file: Path, output_dir: Optional[Path] = None) -> Tuple[bool, Optional[Path]]:
    """
    Process a single video file

    Args:
        input_file (Path): Input video file
        output_dir (Path, optional): Output directory (defaults to same as input)

    Returns:
        tuple: (success: bool, output_file: Optional[Path])
    """
    # Verify input file exists
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return False, None

    # Verify it's a video file
    is_video, error = is_video_file(input_file)
    if not is_video:
        print(f"Error: {input_file.name} is not a valid video file")
        if error:
            print(f"  {error}")
        return False, None

    # Determine output path
    if output_dir is None:
        output_dir = input_file.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename (same name, .m4a extension)
    output_file = output_dir / (input_file.stem + ".m4a")

    # Extract audio
    success, error = extract_audio(input_file, output_file)

    if not success:
        print(f"Error extracting audio from {input_file.name}")
        if error:
            print(f"  {error}")
        return False, None

    return True, output_file


def process_batch(pattern: str, output_dir: Optional[Path] = None) -> Tuple[int, int, List[Path]]:
    """
    Process multiple video files matching a glob pattern

    Args:
        pattern (str): Glob pattern for video files (e.g., "videos/*.mp4")
        output_dir (Path, optional): Output directory for all files

    Returns:
        tuple: (success_count: int, fail_count: int, output_files: List[Path])
    """
    # Find all matching files
    files = sorted(Path(".").glob(pattern))

    if not files:
        print(f"Error: No files found matching pattern '{pattern}'")
        return 0, 0, []

    print(f"Found {len(files)} file(s) to process\n")

    success_count = 0
    fail_count = 0
    output_files = []

    for input_file in files:
        print(f"[{success_count + fail_count + 1}/{len(files)}] Processing {input_file.name}")

        success, output_file = process_single_file(input_file, output_dir)

        if success:
            success_count += 1
            output_files.append(output_file)
        else:
            fail_count += 1

        print()  # Blank line between files

    return success_count, fail_count, output_files


def main():
    parser = argparse.ArgumentParser(
        description="Extract audio from video files using ffmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract audio from single video file
  python scripts/extract_audio.py "interviews/Person/Interview.mp4"

  # Extract with custom output directory
  python scripts/extract_audio.py "video.mov" --output "interviews/Person/audio/"

  # Batch process all mp4 files
  python scripts/extract_audio.py --batch "videos/*.mp4"

  # Batch process with output directory
  python scripts/extract_audio.py --batch "interviews/**/*.mov" --output "audio/"

Output:
  - Extracted audio files are saved as .m4a format
  - By default, files are saved in the same directory as the input
  - Use --output to specify a different output directory
  - Audio is extracted using codec copy (fast) or AAC encoding (fallback)
        """
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "input_file",
        nargs="?",
        type=str,
        help="Input video file to process"
    )
    input_group.add_argument(
        "--batch",
        type=str,
        help="Glob pattern for batch processing (e.g., 'videos/*.mp4')"
    )

    # Optional arguments
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output directory (default: same directory as input file)"
    )

    args = parser.parse_args()

    # Check for ffmpeg/ffprobe
    if not check_ffmpeg_installed():
        print("Error: ffmpeg and ffprobe must be installed and accessible")
        print("\nInstall instructions:")
        print("  Windows (chocolatey): choco install ffmpeg")
        print("  macOS (homebrew): brew install ffmpeg")
        print("  Linux (apt): sudo apt install ffmpeg")
        sys.exit(1)

    # Prepare output directory
    output_dir = Path(args.output) if args.output else None

    # Process files
    if args.batch:
        # Batch processing
        print(f"Batch processing: {args.batch}\n")

        success_count, fail_count, output_files = process_batch(args.batch, output_dir)

        # Print summary
        print("=" * 60)
        print(f"Batch processing complete!")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {fail_count}")
        print(f"  Total: {success_count + fail_count}")

        if output_files:
            print("\nExtracted audio files:")
            for output_file in output_files:
                print(f"  - {output_file}")

        print("=" * 60)

        sys.exit(0 if fail_count == 0 else 1)

    else:
        # Single file processing
        input_file = Path(args.input_file)

        success, output_file = process_single_file(input_file, output_dir)

        if success:
            print("\n" + "=" * 60)
            print("Audio extraction complete!")
            print(f"  Input: {input_file}")
            print(f"  Output: {output_file}")
            print("=" * 60)
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
