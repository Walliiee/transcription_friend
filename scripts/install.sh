#!/usr/bin/env bash
set -euo pipefail

echo "==> Audio Transcription Workspace installer"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but not found in PATH."
  exit 1
fi

PYTHON_BIN="python3"

echo "==> Creating virtual environment"
"$PYTHON_BIN" -m venv .venv
VENV_PYTHON=".venv/bin/python"

echo "==> Upgrading pip"
"$VENV_PYTHON" -m pip install --upgrade pip

echo "==> Installing PyTorch CUDA 12.8 wheels"
"$VENV_PYTHON" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo "==> Installing project dependencies"
"$VENV_PYTHON" -m pip install -r requirements.txt

echo
echo "Install complete."
echo "Next step:"
echo "  $VENV_PYTHON scripts/transcribe.py --audio \"interview.m4a\" --name Person --language da"
