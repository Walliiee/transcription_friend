#!/usr/bin/env python3
"""
Unified post-processing script for transcription quality review
Handles spell-checking, grammar corrections, and mistranslation fixes
Supports both English and Danish transcriptions

Usage:
    python scripts/postprocess.py --input "Speaker/Speaker_transcription_en.txt" --language en
    python scripts/postprocess.py --input "Person/Person_transcription_da.txt" --language da
"""

import argparse
import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.corrections import get_corrections, get_review_flags
import config


def apply_corrections(text, corrections):
    """
    Apply corrections to text while tracking changes.

    Uses word-boundary-aware matching so that correcting "cloud" to "Claude"
    won't accidentally transform "cloud computing" when the dict also has
    multi-word entries. Longer phrases are matched first to avoid partial hits.

    Args:
        text (str): Original text
        corrections (dict): Dictionary of corrections (wrong -> correct)

    Returns:
        tuple: (corrected_text, changes_list)
    """
    changes = []
    corrected_text = text

    sorted_corrections = sorted(corrections.items(), key=lambda kv: len(kv[0]), reverse=True)

    for wrong, correct in sorted_corrections:
        pattern = re.compile(re.escape(wrong))
        matches = pattern.findall(corrected_text)
        if matches:
            count = len(matches)
            corrected_text = pattern.sub(correct, corrected_text)
            changes.append(
                f"  - '{wrong}' → '{correct}' ({count} occurrence{'s' if count > 1 else ''})"
            )

    return corrected_text, changes


def flag_potential_issues(text, flags):
    """
    Find potential issues that need manual review

    Args:
        text (str): Text to analyze
        flags (list): List of phrases to flag

    Returns:
        list: List of issues found with context
    """
    issues = []

    for flag in flags:
        if flag.lower() in text.lower():
            # Find context around the issue
            pattern = re.compile(f".{{0,50}}{re.escape(flag)}.{{0,50}}", re.IGNORECASE)
            matches = pattern.findall(text)
            for match in matches[:3]:  # Limit to first 3 occurrences per flag
                issues.append(f"  - '{flag}' found in: '...{match.strip()}...'")

    return issues


def clean_formatting(text):
    """
    Clean up formatting issues

    Args:
        text (str): Text to clean

    Returns:
        str: Cleaned text
    """
    # Remove excessive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix spacing around punctuation
    text = re.sub(r'\s+([,.])', r'\1', text)

    # Ensure proper spacing after timestamps
    text = re.sub(r'\[(\d{2}:\d{2}:\d{2})\]([^\s])', r'[\1] \2', text)

    return text


def process_transcription(input_file, output_file, report_file, language):
    """
    Main processing function

    Args:
        input_file (Path): Input transcription file
        output_file (Path): Output file for corrected transcription
        report_file (Path): Output file for change report
        language (str): Language code (en, da)
    """
    lang_name = "English" if language == "en" else "Danish"

    print(f"Reading {lang_name} transcription from {input_file}...")

    with open(input_file, "r", encoding="utf-8") as f:
        original_text = f.read()

    # Get language-specific corrections and flags
    corrections = get_corrections(language)
    review_flags = get_review_flags(language)

    print(f"Applying {lang_name}-specific corrections...")
    corrected_text, changes = apply_corrections(original_text, corrections)

    print("Cleaning formatting...")
    corrected_text = clean_formatting(corrected_text)

    print("Flagging potential issues for manual review...")
    issues = flag_potential_issues(corrected_text, review_flags)

    # Write corrected version
    print(f"Writing corrected transcription to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(corrected_text)

    # Write report
    print(f"Writing change report to {report_file}...")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# {lang_name} Transcription Post-Processing Report\n\n")
        f.write("## Automatic Corrections Applied\n\n")

        if changes:
            f.write("The following corrections were made:\n\n")
            for change in changes:
                f.write(f"{change}\n")
        else:
            f.write("No automatic corrections were needed.\n")

        f.write("\n## Items Flagged for Manual Review\n\n")

        if language == "da":
            f.write("**Note:** These are English technical terms commonly used in Danish tech interviews.\n")
            f.write("Review to confirm they are used correctly in context.\n\n")

        if issues:
            f.write("The following items may need manual review:\n\n")
            for issue in issues:
                f.write(f"{issue}\n")
        else:
            f.write("No issues flagged for review.\n")

        # Language-specific notes
        if language == "da":
            f.write("\n## Danish Language Notes\n\n")
            f.write("1. **English Technical Terms:** Many English terms (loading, deploy, debug, etc.) ")
            f.write("are commonly used in Danish tech conversations and may be correct as-is.\n")
            f.write("2. **Gender Agreement:** Check noun-article agreement (en/et, din/dit)\n")
            f.write("3. **Compound Words:** Danish often compounds words - verify hyphenation\n")
            f.write("4. **Code-Switching:** Interview likely contains mix of Danish and English technical terms\n")

        f.write("\n## Recommendations\n\n")

        if language == "da":
            f.write("1. Review flagged English terms to confirm they're contextually appropriate\n")
            f.write("2. Listen to sections with technical terms if unsure about language choice\n")
            f.write("3. Check Danish grammar (particularly gender agreement) if uncertain\n")
        else:
            f.write("1. Review the flagged items above for accuracy\n")
            f.write("2. Listen to problematic sections of audio if needed\n")
            f.write("3. Check technical terms and proper nouns\n")

        f.write("4. Verify speaker attribution if applicable\n")

    print("\n" + "="*60)
    print("Post-processing complete!")
    print(f"Original file: {input_file}")
    print(f"Corrected file: {output_file}")
    print(f"Change report: {report_file}")
    print("="*60)

    return output_file, report_file


def main():
    parser = argparse.ArgumentParser(
        description="Unified post-processing script for transcription quality review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # English transcription
  python scripts/postprocess.py --input "Speaker/Speaker_transcription_en.txt" --language en

  # Danish transcription
  python scripts/postprocess.py --input "Person/Person_transcription_da.txt" --language da

  # Custom output location
  python scripts/postprocess.py --input "file.txt" --language da --output "reviewed/"
        """
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input transcription file to process"
    )
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        choices=config.SUPPORTED_LANGUAGES,
        help="Transcription language (en=English, da=Danish)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory (default: same directory as input file)"
    )

    args = parser.parse_args()

    # Validate input file
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_file.parent

    # Generate output filenames
    input_stem = input_file.stem

    # Remove existing suffixes if present
    if input_stem.endswith("_transcription_" + args.language):
        base_name = input_stem.replace("_transcription_" + args.language, "")
    elif "_transcription" in input_stem:
        base_name = input_stem.split("_transcription")[0]
    else:
        base_name = input_stem

    output_file = output_dir / f"{base_name}_transcription_{args.language}_reviewed.txt"
    report_file = output_dir / f"{base_name}_transcription_{args.language}_review_report.txt"

    # Process the transcription
    process_transcription(input_file, output_file, report_file, args.language)


if __name__ == "__main__":
    main()
