from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from kinyarwanda_alignment.matching import (
    SequenceMatchError,
    find_contiguous_sequence,
    find_unique_sequence_start,
)


def test_find_contiguous_sequence():
    assert find_contiguous_sequence(["b", "c"], ["a", "b", "c", "d"]) == [1]


def test_unique_match_rejects_ambiguous_sequence():
    with pytest.raises(SequenceMatchError):
        find_unique_sequence_start(
            ["a"],
            ["a", "a"],
            source_label="example",
        )
