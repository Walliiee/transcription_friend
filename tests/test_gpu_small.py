from faster_whisper import WhisperModel
import torch

print("Checking GPU availability...")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Compute capability: {torch.cuda.get_device_capability(0)}")

print("\nTrying to load small model on GPU...")
try:
    model = WhisperModel("small", device="cuda", compute_type="float16")
    print("✓ Small model loaded successfully on GPU!")
except Exception as e:
    print(f"✗ Failed: {e}")
