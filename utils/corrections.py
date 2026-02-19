"""
Correction dictionaries and review flags for post-processing transcriptions
Separated by language (English and Danish)
"""

from __future__ import annotations

# English transcription corrections
CORRECTIONS_EN = {
    # AI model/tool names
    "Germany": "Gemini",
    "germany": "Gemini",
    "cloud": "Claude",
    "Cloud": "Claude",
    "BQR": "Bard",

    # Common mistranscriptions
    "transfer books": "transcribe this",
    "Transfer books": "Transcribe this",
    "rapper from Germany": "report from Gemini",
    "the rapper from Germany": "the report from Gemini",
    "rapper from Gemini": "report from Gemini",
    "the rapper from Gemini": "the report from Gemini",

    # Grammar/spelling
    "get bored": "onboard",
    "unboard": "onboard",
    "blah blah blah blah": "etc.",

    # Common filler corrections
    "boop, boop, boop, boop, boop, boop, boop": "[onomatopoeia]",

    # Technical terms
    "ArtBytes, Meteor": "Arbejdsmiljø",  # Danish: work environment
}

# Danish transcription corrections
CORRECTIONS_DA = {
    # AI tools and models
    "Germany": "Gemini",
    "germany": "Gemini",
    "cloud": "Claude",
    "Cloud": "Claude",
    "BQR": "Bard",

    # Company/product names
    "Faros A": "Faros AI",
    "faros a": "Faros AI",

    # Danish grammar corrections
    "din navn": "dit navn",  # Correct gender agreement (neuter)
    "en kabel": "et kabel",  # Correct gender for "cable"

    # Common Danish mistranscriptions
    "kolot": "kolonne",  # Column (technical term)
    "den kolot": "den kolonne",  # The column
    "mapper den kolot": "mapper den kolonne",  # Maps the column
    "mapper det her, den kolot": "mapper det her, den kolonne",  # Maps this, the column
    "grænser du så det, eller normaliserer": "renser du så det, eller normaliserer",  # Do you clean/normalize it
    "grænserne hinne": "grænserne henne",  # The boundaries there/over there
    "Cloud Codes": "Cloud Code",  # Google Cloud Code (product name)

    # Common filler corrections
    "boop, boop, boop, boop, boop, boop, boop": "[onomatopoeia]",
}

# English review flags - phrases to manually check
REVIEW_FLAGS_EN = [
    "compile, oops",  # Likely "ChatGPT" or similar
    "crazy busy",
    "trust that terrible",  # Likely "transform that data"
    "pulling out from my brain",
]

# Danish review flags - technical terms that may need verification
REVIEW_FLAGS_DA = [
    "loading",  # Could be English term or Danish "belastning"
    "deploye",  # Check if should be "deployment" or Danish equivalent
    "merging",  # Could be correct or Danish "sammenlægning"
    "debugge",  # Danish verb form of "debug" - check consistency
    "repository",  # Often used in English in Danish tech context
    "SaaS-platform",  # Check hyphenation/capitalization
]


def get_corrections(language: str = "da") -> dict[str, str]:
    """
    Get corrections dictionary for specified language

    Args:
        language: Language code ("en" or "da")

    Returns:
        Corrections dictionary mapping wrong text to correct text
    """
    if language == "en":
        return CORRECTIONS_EN
    elif language == "da":
        return CORRECTIONS_DA
    else:
        raise ValueError(f"Unsupported language: {language}. Use 'en' or 'da'")


def get_review_flags(language: str = "da") -> list[str]:
    """
    Get review flags list for specified language

    Args:
        language: Language code ("en" or "da")

    Returns:
        List of phrases to flag for manual review
    """
    if language == "en":
        return REVIEW_FLAGS_EN
    elif language == "da":
        return REVIEW_FLAGS_DA
    else:
        raise ValueError(f"Unsupported language: {language}. Use 'en' or 'da'")
