#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "==> Audio Transcription Workspace installer"

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or not on PATH."
}

$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "==> Python version: $pythonVersion"

# Create virtual environment if needed
if (-not (Test-Path ".venv")) {
    Write-Host "==> Creating .venv"
    python -m venv .venv
}

$venvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment python executable not found at $venvPython"
}

Write-Host "==> Upgrading pip"
& $venvPython -m pip install --upgrade pip

Write-Host "==> Installing PyTorch (CUDA 12.8 wheels)"
& $venvPython -m pip install torch --index-url https://download.pytorch.org/whl/cu128

Write-Host "==> Installing project requirements"
& $venvPython -m pip install -r requirements.txt

Write-Host ""
Write-Host "Install complete."
Write-Host "Use this interpreter for commands:"
Write-Host "  .venv\Scripts\python.exe scripts\transcribe.py --help"
