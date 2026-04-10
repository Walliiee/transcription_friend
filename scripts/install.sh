#!/usr/bin/env bash
set -euo pipefail

echo "==> Audio Transcription Workspace installer"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but not found in PATH."
  exit 1
fi

PYTHON_BIN="python3"

if ! command -v pip3 >/dev/null 2>&1; then
  echo "pip3 not found; trying python3 -m pip"
  if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
    echo "Error: pip is not available. Install pip and rerun."
    exit 1
  fi
  PIP_CMD=("$PYTHON_BIN" -m pip)
else
  PIP_CMD=("pip3")
fi

echo "==> Upgrading pip"
"${PIP_CMD[@]}" install --upgrade pip

echo "==> Installing PyTorch CUDA 12.8 wheels"
"${PIP_CMD[@]}" install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo "==> Installing project dependencies"
"${PIP_CMD[@]}" install -r requirements.txt

echo
echo "Install complete."
echo "Next step:"
echo '  python scripts/transcribe.py --audio "interview.m4a" --name Person --language da'
