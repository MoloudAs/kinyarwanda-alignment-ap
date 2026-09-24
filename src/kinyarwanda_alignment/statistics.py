"""Simple recording-level comparison for MFA and WebMAUS."""

from __future__ import annotations

import pandas as pd
from scipy.stats import wilcoxon


def recording_level_summary(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate word-level MAE to one paired observation per recording."""
    per_file = (
        analysis_df.groupby("file_id", as_index=False)
        .agg(
            words=("word_index", "count"),
            MFA_MAE_ms=("mfa_word_mae_ms", "mean"),
            WebMAUS_MAE_ms=("webmaus_word_mae_ms", "mean"),
        )
        .sort_values("file_id")
    )

    per_file["WebMAUS_minus_MFA_ms"] = (
        per_file["WebMAUS_MAE_ms"] - per_file["MFA_MAE_ms"]
    )
    return per_file


def paired_recording_test(per_file_df: pd.DataFrame) -> dict[str, float | int]:
    """Compare paired recording-level MAEs with a Wilcoxon signed-rank test."""
    result = wilcoxon(
        per_file_df["MFA_MAE_ms"],
        per_file_df["WebMAUS_MAE_ms"],
        alternative="two-sided",
        zero_method="wilcox",
    )

    differences = per_file_df["WebMAUS_minus_MFA_ms"]

    return {
        "N_paired_recordings": int(len(per_file_df)),
        "wilcoxon_statistic": float(result.statistic),
        "wilcoxon_p": float(result.pvalue),
        "mean_WebMAUS_minus_MFA_ms": float(differences.mean()),
        "median_WebMAUS_minus_MFA_ms": float(differences.median()),
        "MFA_lower_MAE_recordings": int((differences > 0).sum()),
        "WebMAUS_lower_MAE_recordings": int((differences < 0).sum()),
        "ties": int((differences == 0).sum()),
    }
