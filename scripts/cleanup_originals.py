#!/usr/bin/env python3
"""
Quick cleanup script to delete original transcription files, keeping only reviewed versions
"""
import os
from pathlib import Path

# Find all transcription files
interviews_dir = Path("interviews")
deleted_count = 0

for txt_file in interviews_dir.rglob("*_transcription_*.txt"):
    # Keep reviewed files and review reports
    if "_reviewed" not in txt_file.name and "_review_report" not in txt_file.name:
        print(f"Deleting: {txt_file}")
        txt_file.unlink()
        deleted_count += 1

print(f"\n[OK] Deleted {deleted_count} original transcription files")
print("[OK] Only reviewed transcriptions remain")
