---
name: whisper-transcription
description: Provides expertise for audio transcription workflows using faster-whisper, including m4a audio processing, GPU-accelerated transcription, batch processing of audio segments, and troubleshooting transcription issues
---

# Whisper Transcription Skill

This skill provides comprehensive guidance for audio transcription workflows in this repository, using GPU-accelerated Whisper models via faster-whisper.

## When to Use This Skill

Invoke this skill when:
- Processing m4a audio files for transcription
- Running transcription scripts (transcribe_faster_gpu.py, transcribe_danish.py, etc.)
- Batch processing audio segments (especially 30-second intervals)
- Troubleshooting transcription failures or errors
- Validating audio inputs or transcription outputs
- Switching between GPU and CPU transcription modes

## Available Transcription Scripts

### 1. Main GPU Script: `transcribe_faster_gpu.py`
Primary script for GPU-accelerated transcription using faster-whisper.

**Usage:**
```bash
python transcribe_faster_gpu.py <audio_file.m4a>
```

**Features:**
- CUDA-accelerated when GPU available
- Automatic CPU fallback if GPU unavailable
- Optimized for 30-second audio segments
- Supports m4a format

### 2. Segment-Specific: `transcribe_faster_gpu_segments_2_3.py`
Processes specific audio segment ranges.

**Usage:**
```bash
python transcribe_faster_gpu_segments_2_3.py
```

**Use Case:**
- Processing specific segment ranges
- Resuming interrupted batch jobs
- Testing individual segments

### 3. Danish Language: `transcribe_danish.py`
Specialized for Danish language transcription.

**Usage:**
```bash
python transcribe_danish.py <audio_file.m4a>
```

**Features:**
- Danish language model
- Same GPU/CPU flexibility
- Optimized for Danish phonetics

## Workflow Steps

### Step 1: Validate Audio Input

Before transcription, verify:

```bash
# Check audio files exist
ls *.m4a

# Verify file integrity (check size, not corrupted)
ls -lh *.m4a

# Count total segments
ls *.m4a | wc -l
```

**Expected Format:**
- File extension: `.m4a`
- Typical segment duration: 30 seconds
- File naming: Usually numbered or timestamped segments

### Step 2: Check GPU Availability

Verify GPU status before running:

```bash
# Check if GPU is detected
nvidia-smi

# Verify PyTorch can access GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check CUDA version
python -c "import torch; print(f'CUDA version: {torch.version.cuda}')"
```

**Known Limitation:**
- RTX 5060 requires PyTorch with CUDA 12.8+ support (sm_120)
- Current PyTorch may only support up to sm_90
- If GPU unavailable, scripts automatically fall back to CPU

### Step 3: Run Transcription

**Single File:**
```bash
python transcribe_faster_gpu.py audio_segment_001.m4a
```

**Batch Processing:**
Use the provided helper script (see scripts/batch_transcribe.py below):

```bash
python .claude/skills/whisper-transcription/scripts/batch_transcribe.py --input-dir . --pattern "*.m4a"
```

### Step 4: Verify Output

After transcription completes:

```bash
# Check for output files (txt, json, or stdout)
ls *.txt

# Verify transcription content
cat output.txt

# Count completed transcriptions
ls *.txt | wc -l
```

## Troubleshooting Guide

### Issue: "No CUDA-capable device detected"

**Cause:** GPU not accessible to PyTorch

**Solutions:**
1. Verify GPU is present: `nvidia-smi`
2. Check PyTorch CUDA build: `python -c "import torch; print(torch.version.cuda)"`
3. If sm_120 incompatibility, install CUDA 12.8+ PyTorch:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
   ```
4. Script will automatically use CPU mode as fallback

### Issue: "Audio file not found"

**Cause:** Incorrect file path or missing file

**Solutions:**
1. Verify file exists: `ls <filename>`
2. Check current directory: `pwd`
3. Use absolute paths if needed
4. Verify file extension is `.m4a`

### Issue: "Out of memory" (GPU)

**Cause:** GPU memory exhausted

**Solutions:**
1. Process fewer files concurrently
2. Reduce batch size in script
3. Use CPU mode instead: `device="cpu"` in script
4. Free GPU memory: restart Python process

### Issue: Transcription produces no output

**Cause:** Script error or silent failure

**Solutions:**
1. Run with verbose output to see errors
2. Check Python traceback for exceptions
3. Verify faster-whisper is installed: `pip show faster-whisper`
4. Test with single small file first

### Issue: Poor transcription quality

**Cause:** Wrong model or language settings

**Solutions:**
1. Verify correct language model (use `transcribe_danish.py` for Danish)
2. Check audio quality (corrupted files, too noisy)
3. Try different Whisper model size (small, medium, large)
4. Verify audio is actually speech (not silence or music)

## Batch Processing Pattern

For processing multiple m4a segments efficiently:

1. **Organize files:**
   ```bash
   # List all m4a files
   ls -1 *.m4a > file_list.txt
   ```

2. **Use helper script:**
   ```bash
   python .claude/skills/whisper-transcription/scripts/batch_transcribe.py --input-dir . --output-dir ./transcriptions
   ```

3. **Monitor progress:**
   - Script shows progress per file
   - Logs completed files
   - Reports any failures

4. **Resume interrupted jobs:**
   - Script skips already-transcribed files
   - Safe to rerun on same directory

## Helper Scripts

### Batch Transcription Script

Located at: `.claude/skills/whisper-transcription/scripts/batch_transcribe.py`

A Python script for processing multiple audio files with progress tracking, error handling, and resume capability.

**Usage:**
```bash
python .claude/skills/whisper-transcription/scripts/batch_transcribe.py \
  --input-dir /path/to/audio/files \
  --output-dir /path/to/output \
  --pattern "*.m4a" \
  --gpu
```

**Features:**
- Automatic GPU/CPU detection
- Progress tracking
- Error handling per file
- Resume capability (skips completed files)
- Detailed logging

## Best Practices

1. **Test First:** Always test with one file before batch processing
2. **Verify GPU:** Check GPU availability before large batches
3. **Monitor Memory:** Watch GPU/CPU memory during processing
4. **Save Outputs:** Redirect output to files for large batches
5. **Checkpoint Progress:** Use helper script's resume feature for large jobs
6. **Validate Results:** Spot-check transcriptions for quality
7. **Keep Logs:** Save transcription logs for troubleshooting

## Dependencies

Ensure these are installed (see `requirements.txt`):

- `torch` (with CUDA 12.8+ support for GPU)
- `faster-whisper` (GPU-accelerated transcription)
- `ctranslate2` (inference backend)
- `ffmpeg` (audio processing, system-level)

**Install command:**
```bash
pip install -r requirements.txt
```

**For GPU support:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

## Additional Resources

- **Hardware Config:** See CLAUDE.md for RTX 5060 GPU specifications
- **Requirements:** See requirements.txt for dependencies
- **Scripts:** All transcription scripts are in the repository root
