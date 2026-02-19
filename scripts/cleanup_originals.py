#!/usr/bin/env python3
"""
Cleanup script to delete original transcription files, keeping only reviewed versions.

Usage:
    python scripts/cleanup_originals.py                     # dry-run (default)
    python scripts/cleanup_originals.py --delete            # actually delete files
    python scripts/cleanup_originals.py --dir custom/path   # custom interviews directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_originals(interviews_dir: Path) -> list[Path]:
    """Find original transcription files that have been superseded by reviewed versions."""
    originals = []
    for txt_file in sorted(interviews_dir.rglob("*_transcription_*.txt")):
        if "_reviewed" not in txt_file.name and "_review_report" not in txt_file.name:
            originals.append(txt_file)
    return originals


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Delete original transcription files, keeping reviewed versions and reports",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="interviews",
        help="Interviews directory to scan (default: interviews)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete files (without this flag, only a dry-run is performed)",
    )
    args = parser.parse_args()

    interviews_dir = Path(args.dir)
    if not interviews_dir.is_dir():
        print(f"Error: Directory not found: {interviews_dir}")
        sys.exit(1)

    originals = find_originals(interviews_dir)

    if not originals:
        print("No original transcription files found to clean up.")
        return

    if not args.delete:
        print(f"DRY RUN - would delete {len(originals)} file(s):\n")
        for f in originals:
            print(f"  {f}")
        print(f"\nRe-run with --delete to remove these files.")
        return

    deleted = 0
    for f in originals:
        print(f"Deleting: {f}")
        f.unlink()
        deleted += 1

    print(f"\nDeleted {deleted} original transcription file(s).")
    print("Only reviewed transcriptions and reports remain.")


if __name__ == "__main__":
    main()
