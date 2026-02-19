# Whisper Transcription Reference

Quick reference for common transcription tasks and commands.

## Quick Start Commands

### Single File Transcription
```bash
# GPU-accelerated (automatic CPU fallback)
python transcribe_faster_gpu.py audio.m4a

# Danish language
python transcribe_danish.py audio.m4a

# Specific segments
python transcribe_faster_gpu_segments_2_3.py
```

### Batch Transcription
```bash
# Process all m4a files in current directory
python .claude/skills/whisper-transcription/scripts/batch_transcribe.py \
  --input-dir . \
  --pattern "*.m4a" \
  --gpu

# Process with specific model size
python .claude/skills/whisper-transcription/scripts/batch_transcribe.py \
  --input-dir ./audio \
  --output-dir ./transcriptions \
  --model-size medium \
  --gpu
```

## GPU Diagnostics

### Check GPU Status
```bash
# Basic GPU info
nvidia-smi

# Detailed GPU properties
python -c "import torch; print(torch.cuda.get_device_properties(0))"

# Check CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Version: {torch.version.cuda}')"
```

### Hardware Specifications
- **GPU Model:** NVIDIA GeForce RTX 5060 Laptop GPU
- **Compute Capability:** sm_120 (CUDA 12.0)
- **PyTorch Requirement:** CUDA 12.8+ for full sm_120 support
- **Current Limitation:** Standard PyTorch only supports sm_50-sm_90

### Install Compatible PyTorch
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

## Audio File Management

### List and Count Files
```bash
# List all m4a files
ls -lh *.m4a

# Count audio segments
ls *.m4a | wc -l

# Find by pattern
find . -name "segment_*.m4a" -type f
```

### Validate Audio Files
```bash
# Check file sizes (detect corrupted files)
ls -lh *.m4a | awk '$5 == "0" {print "Empty:", $9}'

# Verify m4a format
file *.m4a

# Get audio duration (requires ffprobe)
ffprobe -i audio.m4a -show_entries format=duration -v quiet -of csv="p=0"
```

## Transcription Output Management

### Check Output Files
```bash
# List transcription outputs
ls -lh *.txt

# Preview first 5 lines of each transcription
for f in *.txt; do echo "=== $f ==="; head -n 5 "$f"; echo; done

# Count words in transcriptions
wc -w *.txt

# Search transcriptions for keyword
grep -i "keyword" *.txt
```

### Merge Transcriptions
```bash
# Combine all transcriptions into one file
cat *.txt > complete_transcription.txt

# With file markers
for f in *.txt; do echo "=== $f ===" >> merged.txt; cat "$f" >> merged.txt; echo >> merged.txt; done
```

## Model Sizes and Performance

| Model Size | Parameters | VRAM Required | Speed | Quality |
|------------|------------|---------------|-------|---------|
| tiny       | 39M        | ~1GB          | Fast  | Basic   |
| base       | 74M        | ~1GB          | Fast  | Good    |
| small      | 244M       | ~2GB          | Medium| Better  |
| medium     | 769M       | ~5GB          | Slow  | High    |
| large      | 1550M      | ~10GB         | Slowest| Best  |

**Recommendation:** Start with `base` model for testing, upgrade to `medium` for production quality.

## Error Messages Reference

### CUDA Errors
- `no CUDA-capable device`: GPU not detected → Check nvidia-smi
- `compute capability sm_120 not supported`: PyTorch version too old → Upgrade to CUDA 12.8+ build
- `out of memory`: GPU memory exhausted → Use smaller model or CPU mode

### File Errors
- `FileNotFoundError`: Audio file path incorrect → Check file exists with `ls`
- `Unsupported format`: Not m4a or corrupted → Verify with `file` command
- `Permission denied`: File access restricted → Check permissions with `ls -l`

### Model Errors
- `Model not found`: faster-whisper not installed → `pip install faster-whisper`
- `Failed to load model`: Incompatible ctranslate2 → Reinstall dependencies
- `Language not supported`: Wrong language model → Use appropriate script

## Environment Variables

### Useful Settings
```bash
# Force CPU mode (disable CUDA)
export CUDA_VISIBLE_DEVICES=""

# Set specific GPU
export CUDA_VISIBLE_DEVICES=0

# Enable PyTorch CUDA debugging
export CUDA_LAUNCH_BLOCKING=1

# Set faster-whisper cache directory
export HF_HOME=/path/to/cache
```

## Performance Optimization

### GPU Mode Tips
1. Process files in batches to amortize model loading time
2. Use larger model sizes for better quality (if VRAM allows)
3. Monitor GPU utilization with `nvidia-smi -l 1`
4. Close other GPU applications to free memory

### CPU Mode Tips
1. Use smaller models (tiny/base) for faster processing
2. Process files in parallel if multiple CPU cores available
3. Consider using `int8` compute type for speed
4. Expect 10-20x slower than GPU mode

## Dependencies Quick Check

```bash
# Check all dependencies at once
python -c "
import sys
try:
    import torch
    print(f'✓ torch {torch.__version__} (CUDA: {torch.version.cuda})')
    import faster_whisper
    print(f'✓ faster-whisper')
    import ctranslate2
    print(f'✓ ctranslate2')
    print(f'✓ CUDA available: {torch.cuda.is_available()}')
except ImportError as e:
    print(f'✗ Missing: {e}')
    sys.exit(1)
"
```

## Logging and Debugging

### Enable Verbose Output
```python
# In Python scripts, set logging level
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Capture Output
```bash
# Save stdout and stderr
python transcribe_faster_gpu.py audio.m4a > output.log 2>&1

# Timestamp each run
python transcribe_faster_gpu.py audio.m4a 2>&1 | tee "log_$(date +%Y%m%d_%H%M%S).txt"
```

## Common Workflows

### Workflow 1: Process New Audio Batch
```bash
# 1. Verify files
ls *.m4a | wc -l

# 2. Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# 3. Run batch transcription
python .claude/skills/whisper-transcription/scripts/batch_transcribe.py --gpu

# 4. Verify outputs
ls transcriptions/*.txt | wc -l
```

### Workflow 2: Resume Interrupted Job
```bash
# Script automatically skips completed files
python .claude/skills/whisper-transcription/scripts/batch_transcribe.py \
  --skip-completed \
  --gpu
```

### Workflow 3: Troubleshoot Failed Transcription
```bash
# 1. Test with single file
python transcribe_faster_gpu.py problem_file.m4a

# 2. Check file integrity
file problem_file.m4a

# 3. Try CPU mode
CUDA_VISIBLE_DEVICES="" python transcribe_faster_gpu.py problem_file.m4a

# 4. Use smaller model
# (edit script to use model_size="tiny")
```
