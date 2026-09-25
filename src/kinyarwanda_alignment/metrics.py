"""Calculates word-boundary error measures for MFA and WebMAUS."""

import numpy as np
import pandas as pd


def add_error_columns(evaluation_df: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy with boundary-error measures added."""

    df = evaluation_df.copy()

    for aligner in ("mfa", "webmaus"):
        start_error = (
            df[f"{aligner}_start"] - df["manual_start"]
        ) * 1000

        end_error = (
            df[f"{aligner}_end"] - df["manual_end"]
        ) * 1000

        df[f"{aligner}_start_error_ms"] = start_error
        df[f"{aligner}_end_error_ms"] = end_error

        df[f"{aligner}_abs_start_error_ms"] = start_error.abs()
        df[f"{aligner}_abs_end_error_ms"] = end_error.abs()

        df[f"{aligner}_word_mae_ms"] = (
            df[f"{aligner}_abs_start_error_ms"]
            + df[f"{aligner}_abs_end_error_ms"]
        ) / 2

    df["webmaus_minus_mfa_mae_ms"] = (
        df["webmaus_word_mae_ms"]
        - df["mfa_word_mae_ms"]
    )

    return df


def build_edge_dataframe(
    analysis_df: pd.DataFrame,
) -> pd.DataFrame:
    """Converts word rows into individual start and end boundary rows."""

    rows = []

    for row in analysis_df.itertuples(index=False):
        for aligner, prefix in (
            ("MFA", "mfa"),
            ("WebMAUS", "webmaus"),
        ):
            for edge_type in ("start", "end"):
                signed_error = getattr(
                    row,
                    f"{prefix}_{edge_type}_error_ms",
                )

                absolute_error = getattr(
                    row,
                    f"{prefix}_abs_{edge_type}_error_ms",
                )

                rows.append(
                    {
                        "file_id": row.file_id,
                        "word_index": row.word_index,
                        "word": row.word,
                        "aligner": aligner,
                        "edge_type": edge_type,
                        "signed_error_ms": signed_error,
                        "absolute_error_ms": absolute_error,
                    }
                )

    return pd.DataFrame(rows)


def overall_edge_summary(
    edge_df: pd.DataFrame,
    n_words: int,
) -> pd.DataFrame:
    """Calculates descriptive error measures for both aligners."""

    rows = []

    for aligner in ("MFA", "WebMAUS"):
        aligner_edges = edge_df[
            edge_df["aligner"] == aligner
        ]

        absolute_errors = (
            aligner_edges["absolute_error_ms"]
            .to_numpy()
        )

        start_errors = aligner_edges.loc[
            aligner_edges["edge_type"] == "start",
            "absolute_error_ms",
        ]

        end_errors = aligner_edges.loc[
            aligner_edges["edge_type"] == "end",
            "absolute_error_ms",
        ]

        within_20 = absolute_errors <= 20
        within_50 = absolute_errors <= 50
        within_100 = absolute_errors <= 100

        summary = {
            "aligner": aligner,
            "N_words": n_words,
            "N_word_edges": len(absolute_errors),
            "MAE_ms": float(np.mean(absolute_errors)),
            "median_absolute_error_ms": float(
                np.median(absolute_errors)
            ),
            "start_MAE_ms": float(start_errors.mean()),
            "end_MAE_ms": float(end_errors.mean()),
            "edges_within_20ms_pct": float(
                100 * np.mean(within_20)
            ),
            "edges_within_50ms_pct": float(
                100 * np.mean(within_50)
            ),
            "edges_within_100ms_pct": float(
                100 * np.mean(within_100)
            ),
        }

        rows.append(summary)

    return pd.DataFrame(rows)


def complete_word_tolerance_summary(
    analysis_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculates percentages of words within each error tolerance."""

    rows = []

    for aligner, prefix in (
        ("MFA", "mfa"),
        ("WebMAUS", "webmaus"),
    ):
        result = {
            "aligner": aligner,
        }

        for threshold in (20, 50, 100):
            start_within = (
                analysis_df[f"{prefix}_abs_start_error_ms"]
                <= threshold
            )

            end_within = (
                analysis_df[f"{prefix}_abs_end_error_ms"]
                <= threshold
            )

            both_edges_within = start_within & end_within

            percentage = float(
                100 * both_edges_within.mean()
            )

            result[
                f"words_both_edges_within_{threshold}ms_pct"
            ] = percentage

        rows.append(result)

    return pd.DataFrame(rows)