from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from kinyarwanda_alignment.metrics import add_error_columns


def test_add_error_columns_converts_seconds_to_milliseconds():
    df = pd.DataFrame(
        {
            "manual_start": [1.0],
            "manual_end": [2.0],
            "mfa_start": [1.010],
            "mfa_end": [1.980],
            "webmaus_start": [0.950],
            "webmaus_end": [2.100],
        }
    )
    result = add_error_columns(df)
    assert round(result.loc[0, "mfa_start_error_ms"], 8) == 10.0
    assert round(result.loc[0, "mfa_end_error_ms"], 8) == -20.0
    assert round(result.loc[0, "mfa_word_mae_ms"], 8) == 15.0
