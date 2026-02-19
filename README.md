# Audio Transcription Workspace

GPU-accelerated audio transcription using Whisper models for interview processing.

## Features

- **GPU-Accelerated Transcription**: Uses faster-whisper with CUDA support
- **Multi-Language Support**: Danish and English transcriptions
- **Automatic Post-Processing**: Correction of common mistranscriptions
- **Batch Processing**: Handle single files or multiple segments
- **Flexible Configuration**: Centralized settings with command-line overrides

## How It Works

### Parallel Processing Architecture

This tool intelligently separates CPU-bound and GPU-bound tasks to maximize efficiency. Transcription runs sequentially on the GPU (memory-limited to one at a time on 8GB VRAM), while post-processing, reformatting, and file operations run in parallel on the CPU. This architectural separation allows the system to maintain optimal resource utilization throughout the entire transcription workflow.

### GPU-Accelerated Transcription

The core transcription engine uses faster-whisper with CUDA acceleration for maximum performance. The system automatically detects GPU availability and falls back to CPU when necessary. Currently, full GPU acceleration requires PyTorch with CUDA 12.8+ support to match the RTX 5060 Laptop GPU's sm_120 compute capability. Older PyTorch versions (supporting only sm_50 through sm_90) will use CPU processing until updated builds become available.

### Automation with Agents & Skills

The workflow leverages Claude Code's subagent system for parallel CPU tasks, enabling multiple reformatting or post-processing jobs to run simultaneously while the GPU handles transcription. Custom slash commands provide quick access to common workflows, and specialized skills handle operations like audio extraction and text processing. This multi-threaded approach to non-GPU tasks significantly reduces overall processing time.

### FFmpeg Integration

Built-in audio extraction handles video files (mp4, mov, avi) using ffmpeg with codec copy for fast, lossless conversion. The system automatically detects video inputs and extracts audio streams without re-encoding, preserving original quality while minimizing processing overhead. Audio splitting capabilities support segmented processing when working with lengthy recordings that benefit from parallel transcription.

### Post-Processing Pipeline

Automated text correction handles both Danish and English transcriptions with language-specific correction sets. Common issues like AI model name mistranscriptions ("Germany" instead of "Gemini"), technical term corrections, and grammar fixes are applied automatically. The pipeline also flags potential mistranscriptions for manual review, generating detailed change reports that maintain transparency throughout the correction process.

### Workflow Efficiency

A typical workflow processes transcription on the GPU while simultaneously handling repository setup, audio extraction, and reformatting tasks on the CPU. This parallel execution model reduces total processing time by 15-20 minutes per batch compared to sequential processing. The separation of concerns ensures that compute-intensive transcription never blocks lightweight file operations or text processing tasks.

## Quick Start

### Installation

1. **Install PyTorch with CUDA 12.8+ support** (required for RTX 5060):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Transcribe an interview
python scripts/transcribe.py --audio "interviews/Person/audio/interview.m4a" --name Person --language da

# Post-process for corrections
python scripts/postprocess.py --input "interviews/Person/transcriptions/Person_transcription_da.txt" --language da
```

## Hardware Requirements

- **GPU:** NVIDIA GeForce RTX 5060 Laptop GPU
- **Compute Capability:** sm_120 (CUDA 12.0+)
- **PyTorch Requirement:** CUDA 12.8+ build for sm_120 support
- **Fallback:** Automatically falls back to CPU if GPU unavailable

## Project Structure

```
Transcriptions/
├── README.md                   # This file
├── CLAUDE.md                   # Project instructions for Claude Code
├── config.py                   # Central configuration
├── requirements.txt            # Python dependencies
│
├── scripts/                    # Main executable scripts
│   ├── transcribe.py          # Unified transcription script
│   ├── postprocess.py         # Unified post-processing
│   ├── extract_audio.py       # Video-to-audio extraction
│   └── cleanup_originals.py   # Clean up redundant files
│
├── utils/                      # Shared utilities
│   ├── __init__.py
│   ├── whisper_helpers.py     # Model loading, transcription functions
│   └── corrections.py         # Language-specific corrections
│
├── tests/                      # Test scripts
│   ├── test_gpu.py
│   └── test_cuda.py
│
└── interviews/                 # Interview data (organized by person)
    └── Person/
        ├── audio/
        │   └── interview.m4a
        └── transcriptions/
            ├── Person_transcription_da_reviewed.txt
            └── Person_transcription_review_report.txt
```

## Configuration

Edit `config.py` to customize default settings:

- **Model Size**: Default is `"medium"` (options: tiny, base, small, medium, large)
- **Languages**: Default is Danish (`"da"`), also supports English (`"en"`)
- **Device**: Default is GPU (`"cuda"`), falls back to CPU automatically
- **Output Paths**: Standardized structure for all interviews

## Advanced Usage

### Additional Options

```bash
# Use different model size (tiny, base, small, medium, large)
python scripts/transcribe.py --audio "file.m4a" --name Person --language da --model large

# Force CPU-only mode
python scripts/transcribe.py --audio "file.m4a" --name Person --language da --device cpu

# Custom output directory
python scripts/transcribe.py --audio "file.m4a" --name Person --language da --output "custom/path/"

# Extract audio from video
python scripts/extract_audio.py "video.mp4"
```

## Post-Processing Features

The post-processing script (`postprocess.py`) automatically:

1. **Applies Corrections**: Fixes common mistranscriptions (e.g., "Germany" → "Gemini")
2. **Cleans Formatting**: Removes excessive whitespace, fixes punctuation
3. **Flags Issues**: Identifies phrases that may need manual review
4. **Generates Report**: Creates detailed change report for transparency

### Language-Specific Corrections

- **English**: AI tool names, technical terms, common grammar errors
- **Danish**: Gender agreement, compound words, tech terms in Danish context

## Troubleshooting

### GPU Not Detected

If you see "Falling back to CPU", your PyTorch version may not support sm_120:

```bash
# Reinstall with CUDA 12.8+ support
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Import Errors

Make sure you're running scripts from the project root directory:

```bash
# Correct (from project root)
python scripts/transcribe.py --audio "file.m4a" --name Person --language da

# Incorrect (from scripts/ directory)
cd scripts/
python transcribe.py --audio "../file.m4a" --name Person --language da  # Will fail
```

### Out of Memory

If you encounter GPU memory errors, try:

1. Use a smaller model: `--model small`
2. Use CPU mode: `--device cpu`
3. Process shorter segments

## Dependencies

- **faster-whisper**: GPU-accelerated Whisper implementation
- **torch**: PyTorch with CUDA 12.8+ support
- **ctranslate2**: Inference backend (auto-installed)

See `requirements.txt` for complete list with version constraints.

## Complete Workflow

```bash
# 1. (Optional) Extract audio from video if needed
python scripts/extract_audio.py "interviews/Person/audio/video.mp4"

# 2. Transcribe the interview
python scripts/transcribe.py --audio "interviews/Person/audio/interview.m4a" --name Person --language da

# 3. Post-process for corrections
python scripts/postprocess.py --input "interviews/Person/transcriptions/Person_transcription_da.txt" --language da

# 4. Review the report and manually verify flagged items
# Output: Person_transcription_da_reviewed.txt
# Report: Person_transcription_da_review_report.txt
```

## Contributing

This is a personal workspace. For improvements:

1. Update shared utilities in `utils/` to benefit all scripts
2. Add language-specific corrections to `utils/corrections.py`
3. Update `config.py` for project-wide settings
4. Document fixes in `docs/` for future reference

## License

Personal workspace - not licensed for external use.

## Support

For Claude Code usage and project-specific instructions, see `CLAUDE.md`.
