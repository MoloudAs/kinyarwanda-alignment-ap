from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kinyarwanda_alignment.file_utils import (
    extract_file_id,
    extract_gender,
    extract_recording_location,
    normalize_word,
)


def test_extract_file_id_preserves_leading_zero():
    filename = "2024-10-26_F_051_CookSickFootballParty_UR-CE_muted.TextGrid"
    assert extract_file_id(filename) == "051"


def test_extract_file_id_returns_none_without_project_id():
    assert extract_file_id("example.TextGrid") is None


def test_filename_metadata():
    filename = "2024-10-26_F_051_CookSickFootballParty_UR-CE_muted.TextGrid"
    assert extract_gender(filename) == "Female"
    assert extract_recording_location(filename) == "UR-CE"


def test_normalize_word_is_conservative():
    assert normalize_word("  Á’B  ") == "á'b"
