"""Filename and label utilities used across the evaluation pipeline."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path


_FILE_ID_RE = re.compile(r"_([0-9]{3})_")
_GENDER_RE = re.compile(r"_([FM])_[0-9]{3}_")
_APOSTROPHE_VARIANTS = ("’", "‘", "ʼ", "ʹ", "`", "´")


def extract_file_id(filename: str | Path) -> str | None:
    """Extract the three-digit recording ID from a project filename.

    Parameters
    ----------
    filename:
        A filename or path containing an ID such as ``_051_``.

    Returns
    -------
    str | None
        The three-digit ID, preserving leading zeros, or ``None`` if no
        project-style ID is present.
    """
    match = _FILE_ID_RE.search(Path(filename).name)
    return match.group(1) if match else None


def extract_gender(filename: str | Path) -> str | None:
    """Extract speaker gender encoded as ``F`` or ``M`` in a filename."""
    match = _GENDER_RE.search(Path(filename).name)
    if not match:
        return None
    return {"F": "Female", "M": "Male"}[match.group(1)]


def extract_recording_location(filename: str | Path) -> str | None:
    """Extract the project location label encoded in a recording filename."""
    name = Path(filename).name
    if "_Kigali_" in name:
        return "Kigali"
    if "_UR-CE_" in name:
        return "UR-CE"
    return None


def normalize_word(text: object) -> str:
    """Normalize a word conservatively for lexical correspondence.

    The validated research workflow ignores only capitalization, common
    apostrophe-glyph variants, and redundant whitespace. Accents/diacritics
    and all other lexical content are preserved.
    """
    normalized = unicodedata.normalize("NFC", str(text))
    for variant in _APOSTROPHE_VARIANTS:
        normalized = normalized.replace(variant, "'")
    normalized = " ".join(normalized.split()).strip()
    return normalized.casefold()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 checksum of a file without loading it all at once."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()
