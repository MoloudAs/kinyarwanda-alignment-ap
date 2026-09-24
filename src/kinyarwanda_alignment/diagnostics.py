"""Small error-review helpers for the AP project."""

from __future__ import annotations

import pandas as pd


def large_error_summary(
    edge_df: pd.DataFrame,
    thresholds: tuple[int, ...] = (100, 250, 500),
) -> pd.DataFrame:
    """Count large word-boundary errors without excluding observations."""
    rows: list[dict] = []

    for aligner, group in edge_df.groupby("aligner"):
        result: dict[str, float | int | str] = {
            "aligner": aligner,
            "word_edges": len(group),
        }

        for threshold in thresholds:
            count = int((group["absolute_error_ms"] > threshold).sum())
            result[f"n_gt_{threshold}ms"] = count
            result[f"pct_gt_{threshold}ms"] = float(100 * count / len(group))

        rows.append(result)

    return pd.DataFrame(rows)


def top_error_words(
    analysis_df: pd.DataFrame,
    top_n_per_aligner: int = 10,
) -> pd.DataFrame:
    """Return the words with the largest mean boundary error for each aligner."""
    frames = []

    for aligner, column in (
        ("MFA", "mfa_word_mae_ms"),
        ("WebMAUS", "webmaus_word_mae_ms"),
    ):
        frame = (
            analysis_df[
                ["file_id", "word_index", "word", column]
            ]
            .nlargest(top_n_per_aligner, column)
            .rename(columns={column: "word_MAE_ms"})
            .copy()
        )
        frame.insert(0, "aligner", aligner)
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)
