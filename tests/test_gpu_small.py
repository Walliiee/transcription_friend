"""GPU availability and model loading tests (require CUDA hardware)."""

import pytest

torch = pytest.importorskip("torch")


@pytest.mark.gpu
def test_cuda_is_available():
    assert torch.cuda.is_available(), "CUDA is not available on this machine"


@pytest.mark.gpu
def test_gpu_device_name():
    name = torch.cuda.get_device_name(0)
    assert isinstance(name, str) and len(name) > 0


@pytest.mark.gpu
def test_gpu_compute_capability():
    major, minor = torch.cuda.get_device_capability(0)
    assert major >= 5, f"Compute capability {major}.{minor} is too old"


@pytest.mark.gpu
def test_load_small_model_on_gpu():
    WhisperModel = pytest.importorskip("faster_whisper").WhisperModel
    model = WhisperModel("small", device="cuda", compute_type="float16")
    assert model is not None
