"""Basic CUDA tensor operation tests (require CUDA hardware)."""

import pytest

torch = pytest.importorskip("torch")


@pytest.mark.gpu
def test_cuda_available():
    assert torch.cuda.is_available()


@pytest.mark.gpu
def test_cuda_version_string():
    assert torch.version.cuda is not None


@pytest.mark.gpu
def test_gpu_tensor_matmul():
    x = torch.randn(100, 100, device="cuda")
    y = torch.randn(100, 100, device="cuda")
    z = x @ y
    assert z.shape == (100, 100)
    assert z.device.type == "cuda"
