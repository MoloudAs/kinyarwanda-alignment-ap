from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kinyarwanda_alignment.statistics import (
    recording_level_summary,
)


def test_recording_level_summary_calculates_recording_means():
    df = pd.DataFrame(
        {
            "file_id": [
                "001",
                "001",
                "002",
                "002",
            ],
            "word_index": [
                1,
                2,
                1,
                2,
            ],
            "mfa_word_mae_ms": [
                10.0,
                30.0,
                20.0,
                40.0,
            ],
            "webmaus_word_mae_ms": [
                30.0,
                50.0,
                40.0,
                60.0,
            ],
        }
    )

    result = recording_level_summary(df)

    first_recording = result[
        result["file_id"] == "001"
    ].iloc[0]

    assert first_recording["words"] == 2
    assert first_recording["MFA_MAE_ms"] == 20.0
    assert first_recording["WebMAUS_MAE_ms"] == 40.0
    assert first_recording["WebMAUS_minus_MFA_ms"] == 20.0