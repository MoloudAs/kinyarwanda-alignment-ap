"""Compares MFA and WebMAUS at the recording level."""

import pandas as pd
from scipy.stats import wilcoxon


def recording_level_summary(
    analysis_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates one mean error value per recording and aligner."""

    grouped = analysis_df.groupby(
        "file_id",
        as_index=False,
    )

    per_file = grouped.agg(
        words=("word_index", "count"),
        MFA_MAE_ms=("mfa_word_mae_ms", "mean"),
        WebMAUS_MAE_ms=("webmaus_word_mae_ms", "mean"),
    )

    per_file = per_file.sort_values(
        "file_id"
    )

    per_file["WebMAUS_minus_MFA_ms"] = (
        per_file["WebMAUS_MAE_ms"]
        - per_file["MFA_MAE_ms"]
    )

    return per_file


def paired_recording_test(
    per_file_df: pd.DataFrame,
) -> dict[str, float | int]:
    """Compares paired recording-level errors with a Wilcoxon test."""

    mfa_errors = per_file_df["MFA_MAE_ms"]
    webmaus_errors = per_file_df["WebMAUS_MAE_ms"]

    test_result = wilcoxon(
        mfa_errors,
        webmaus_errors,
        alternative="two-sided",
        zero_method="wilcox",
    )

    differences = per_file_df["WebMAUS_minus_MFA_ms"]

    mfa_lower = (differences > 0).sum()
    webmaus_lower = (differences < 0).sum()
    ties = (differences == 0).sum()

    results = {
        "N_paired_recordings": int(len(per_file_df)),
        "wilcoxon_statistic": float(test_result.statistic),
        "wilcoxon_p": float(test_result.pvalue),
        "mean_WebMAUS_minus_MFA_ms": float(
            differences.mean()
        ),
        "median_WebMAUS_minus_MFA_ms": float(
            differences.median()
        ),
        "MFA_lower_MAE_recordings": int(mfa_lower),
        "WebMAUS_lower_MAE_recordings": int(webmaus_lower),
        "ties": int(ties),
    }

    return results