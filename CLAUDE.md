# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Audio transcription workspace using GPU-accelerated Whisper models.
- Input: m4a audio segments (30-second intervals)
- Processing: faster-whisper with CUDA acceleration
- Output: Text transcriptions

## Hardware Configuration

- **GPU:** NVIDIA GeForce RTX 5060 Laptop GPU
- **Compute Capability:** sm_120 (CUDA 12.0)
- **PyTorch Requirement:** Must use CUDA 12.8 or 13.0 build to support sm_120
  - Current PyTorch versions only support sm_50 through sm_90
  - Install command: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`
- **Limitation:** Cannot use GPU-accelerated transcription until PyTorch is updated to CUDA 12.8+
- faster-whisper for GPU-accelerated transcription (when compatible PyTorch installed)

## Available Scripts

- `scripts/transcribe.py` - Unified transcription script (single file or multi-segment)
- `scripts/postprocess.py` - Post-processing with language-specific corrections
- `scripts/extract_audio.py` - Video-to-audio extraction via ffmpeg
- `scripts/cleanup_originals.py` - Remove original transcriptions, keep reviewed versions

## Key Dependencies

- PyTorch (CUDA 12.8+ for sm_120 support)
- faster-whisper (GPU acceleration)
- ctranslate2 (inference backend)
- See requirements.txt for complete list

## User Preferences

- Use PowerShell commands (pwsh) when running shell commands
- Prefers concise communication with analogies when helpful
- When adding new Python packages, update requirements.txt

## Memory System

The `.remember/memory/` directory contains:
- `project.md` - Project-specific preferences and context
- `self.md` - Learning from mistakes and corrections

Read and update these memory files when relevant to maintain context across sessions.
