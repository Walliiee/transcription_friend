#!/usr/bin/env python3
"""
Batch Transcription Script
Processes multiple audio files using faster-whisper with progress tracking
"""

import argparse
import glob
import os
import sys
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import torch
        import faster_whisper
    except ImportError as e:
        print(f"Error: Missing required dependency: {e}")
        print("Install with: pip install torch faster-whisper")
        sys.exit(1)

    return torch

def check_gpu_availability(torch_module):
    """Check if GPU is available for transcription"""
    cuda_available = torch_module.cuda.is_available()

    if cuda_available:
        gpu_name = torch_module.cuda.get_device_name(0)
        print(f"✓ GPU available: {gpu_name}")
        return True
    else:
        print("⚠ GPU not available, will use CPU mode")
        return False

def get_audio_files(input_dir, pattern="*.m4a"):
    """Get list of audio files matching pattern"""
    search_path = os.path.join(input_dir, pattern)
    files = glob.glob(search_path)
    files.sort()
    return files

def get_output_path(audio_file, output_dir):
    """Generate output file path for transcription"""
    base_name = Path(audio_file).stem
    output_file = os.path.join(output_dir, f"{base_name}.txt")
    return output_file

def is_already_transcribed(audio_file, output_dir):
    """Check if audio file has already been transcribed"""
    output_file = get_output_path(audio_file, output_dir)
    return os.path.exists(output_file)

def transcribe_file(audio_file, output_file, use_gpu=True, model_size="base"):
    """Transcribe a single audio file"""
    from faster_whisper import WhisperModel

    # Determine device
    device = "cuda" if use_gpu else "cpu"
    compute_type = "float16" if use_gpu else "int8"

    try:
        # Load model (cached after first load)
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        # Transcribe
        segments, info = model.transcribe(audio_file, beam_size=5)

        # Collect transcription text
        transcription = []
        for segment in segments:
            transcription.append(segment.text)

        # Write to output file
        full_text = " ".join(transcription)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)

        return True, full_text

    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(
        description="Batch transcribe audio files using faster-whisper"
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Directory containing audio files (default: current directory)"
    )
    parser.add_argument(
        "--output-dir",
        default="./transcriptions",
        help="Directory to save transcription outputs (default: ./transcriptions)"
    )
    parser.add_argument(
        "--pattern",
        default="*.m4a",
        help="File pattern to match (default: *.m4a)"
    )
    parser.add_argument(
        "--model-size",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU acceleration if available"
    )
    parser.add_argument(
        "--skip-completed",
        action="store_true",
        default=True,
        help="Skip files that already have transcriptions (default: True)"
    )

    args = parser.parse_args()

    # Check dependencies
    print("Checking dependencies...")
    torch = check_dependencies()

    # Check GPU availability
    use_gpu = args.gpu and check_gpu_availability(torch)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"✓ Output directory: {args.output_dir}")

    # Get audio files
    audio_files = get_audio_files(args.input_dir, args.pattern)

    if not audio_files:
        print(f"✗ No audio files found matching pattern: {args.pattern}")
        sys.exit(1)

    print(f"✓ Found {len(audio_files)} audio files")
    print(f"✓ Model: {args.model_size}")
    print(f"✓ Device: {'GPU (CUDA)' if use_gpu else 'CPU'}")
    print()

    # Process files
    start_time = datetime.now()
    completed = 0
    skipped = 0
    failed = 0

    for idx, audio_file in enumerate(audio_files, 1):
        file_name = os.path.basename(audio_file)
        output_file = get_output_path(audio_file, args.output_dir)

        # Skip if already transcribed
        if args.skip_completed and is_already_transcribed(audio_file, args.output_dir):
            print(f"[{idx}/{len(audio_files)}] ⊘ Skipping {file_name} (already transcribed)")
            skipped += 1
            continue

        print(f"[{idx}/{len(audio_files)}] ⧗ Processing {file_name}...")

        # Transcribe
        success, result = transcribe_file(audio_file, output_file, use_gpu, args.model_size)

        if success:
            preview = result[:80] + "..." if len(result) > 80 else result
            print(f"[{idx}/{len(audio_files)}] ✓ Completed: {preview}")
            completed += 1
        else:
            print(f"[{idx}/{len(audio_files)}] ✗ Failed: {result}")
            failed += 1

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print()
    print("=" * 60)
    print("BATCH TRANSCRIPTION SUMMARY")
    print("=" * 60)
    print(f"Total files:      {len(audio_files)}")
    print(f"Completed:        {completed}")
    print(f"Skipped:          {skipped}")
    print(f"Failed:           {failed}")
    print(f"Duration:         {duration}")
    print(f"Output directory: {args.output_dir}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
