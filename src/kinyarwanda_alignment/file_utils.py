"""Utility functions for filenames and word labels."""

import re
import unicodedata
from pathlib import Path


APOSTROPHE_VARIANTS = ("’", "‘", "ʼ", "ʹ", "`", "´")


def extract_file_id(filename: str | Path) -> str | None:
    """Extract the three-digit recording ID from a project filename."""

    name = Path(filename).name

    match = re.search(r"_([0-9]{3})_", name)

    if match:
        return match.group(1)

    return None


def extract_gender(filename: str | Path) -> str | None:
    """Extract the speaker gender from a project filename."""

    name = Path(filename).name

    match = re.search(r"_([FM])_[0-9]{3}_", name)

    if not match:
        return None

    gender_code = match.group(1)

    if gender_code == "F":
        return "Female"

    if gender_code == "M":
        return "Male"

    return None


def extract_recording_location(filename: str | Path) -> str | None:
    """Extract the recording location from a project filename."""

    name = Path(filename).name

    if "_Kigali_" in name:
        return "Kigali"

    if "_UR-CE_" in name:
        return "UR-CE"

    return None


def normalize_word(text: object) -> str:
    """Normalize a word before comparing labels from different alignments."""

    word = str(text)

    # Normalize Unicode characters while preserving accents and diacritics.
    word = unicodedata.normalize("NFC", word)

    # Replace different apostrophe symbols with the standard apostrophe.
    for apostrophe in APOSTROPHE_VARIANTS:
        word = word.replace(apostrophe, "'")

    # Remove extra spaces.
    word = " ".join(word.split())

    # Ignore capitalization during lexical matching.
    word = word.casefold()

    return word
