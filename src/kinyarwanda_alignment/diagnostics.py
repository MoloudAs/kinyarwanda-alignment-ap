"""Provides simple helpers for reviewing large alignment errors."""

import pandas as pd


def large_error_summary(
    edge_df: pd.DataFrame,
    thresholds: tuple[int, ...] = (100, 250, 500),
) -> pd.DataFrame:
    """Counts large boundary errors for each aligner."""

    rows = []

    for aligner in ("MFA", "WebMAUS"):
        aligner_edges = edge_df[
            edge_df["aligner"] == aligner
        ]

        result = {
            "aligner": aligner,
            "word_edges": len(aligner_edges),
        }

        for threshold in thresholds:
            large_errors = (
                aligner_edges["absolute_error_ms"] > threshold
            )

            count = int(large_errors.sum())

            percentage = float(
                100 * count / len(aligner_edges)
            )

            result[f"n_gt_{threshold}ms"] = count
            result[f"pct_gt_{threshold}ms"] = percentage

        rows.append(result)

    return pd.DataFrame(rows)


def top_error_words(
    analysis_df: pd.DataFrame,
    top_n_per_aligner: int = 10,
) -> pd.DataFrame:
    """Returns the words with the largest error for each aligner."""

    frames = []

    for aligner, error_column in (
        ("MFA", "mfa_word_mae_ms"),
        ("WebMAUS", "webmaus_word_mae_ms"),
    ):
        selected_columns = [
            "file_id",
            "word_index",
            "word",
            error_column,
        ]

        largest_errors = analysis_df[
            selected_columns
        ].nlargest(
            top_n_per_aligner,
            error_column,
        )

        largest_errors = largest_errors.rename(
            columns={
                error_column: "word_MAE_ms"
            }
        ).copy()

        largest_errors["aligner"] = aligner

        largest_errors = largest_errors[
            [
                "aligner",
                "file_id",
                "word_index",
                "word",
                "word_MAE_ms",
            ]
        ]

        frames.append(largest_errors)

    return pd.concat(
        frames,
        ignore_index=True,
    )