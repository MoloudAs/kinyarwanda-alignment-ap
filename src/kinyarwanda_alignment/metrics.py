"""Core word-boundary error metrics for Manual–MFA–WebMAUS comparison."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_error_columns(evaluation_df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with signed/absolute boundary errors and word-level MAE."""
    df = evaluation_df.copy()

    for aligner in ("mfa", "webmaus"):
        df[f"{aligner}_start_error_ms"] = (
            df[f"{aligner}_start"] - df["manual_start"]
        ) * 1000
        df[f"{aligner}_end_error_ms"] = (
            df[f"{aligner}_end"] - df["manual_end"]
        ) * 1000
        df[f"{aligner}_abs_start_error_ms"] = df[
            f"{aligner}_start_error_ms"
        ].abs()
        df[f"{aligner}_abs_end_error_ms"] = df[
            f"{aligner}_end_error_ms"
        ].abs()
        df[f"{aligner}_word_mae_ms"] = (
            df[f"{aligner}_abs_start_error_ms"]
            + df[f"{aligner}_abs_end_error_ms"]
        ) / 2

    df["webmaus_minus_mfa_mae_ms"] = (
        df["webmaus_word_mae_ms"] - df["mfa_word_mae_ms"]
    )
    return df


def build_edge_dataframe(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """Convert word rows into start/end boundary observations for each aligner."""
    rows: list[dict] = []

    for row in analysis_df.itertuples(index=False):
        for aligner, prefix in (("MFA", "mfa"), ("WebMAUS", "webmaus")):
            for edge_type in ("start", "end"):
                rows.append(
                    {
                        "file_id": row.file_id,
                        "word_index": row.word_index,
                        "word": row.word,
                        "aligner": aligner,
                        "edge_type": edge_type,
                        "signed_error_ms": getattr(
                            row, f"{prefix}_{edge_type}_error_ms"
                        ),
                        "absolute_error_ms": getattr(
                            row, f"{prefix}_abs_{edge_type}_error_ms"
                        ),
                    }
                )

    return pd.DataFrame(rows)


def overall_edge_summary(edge_df: pd.DataFrame, n_words: int) -> pd.DataFrame:
    """Return the main descriptive error measures used in the AP."""
    rows: list[dict] = []

    for aligner in ("MFA", "WebMAUS"):
        sub = edge_df[edge_df["aligner"] == aligner]
        abs_values = sub["absolute_error_ms"].to_numpy()
        start_values = sub.loc[
            sub["edge_type"] == "start", "absolute_error_ms"
        ]
        end_values = sub.loc[
            sub["edge_type"] == "end", "absolute_error_ms"
        ]

        rows.append(
            {
                "aligner": aligner,
                "N_words": n_words,
                "N_word_edges": len(abs_values),
                "MAE_ms": float(np.mean(abs_values)),
                "median_absolute_error_ms": float(np.median(abs_values)),
                "start_MAE_ms": float(start_values.mean()),
                "end_MAE_ms": float(end_values.mean()),
                "edges_within_20ms_pct": float(100 * np.mean(abs_values <= 20)),
                "edges_within_50ms_pct": float(100 * np.mean(abs_values <= 50)),
                "edges_within_100ms_pct": float(100 * np.mean(abs_values <= 100)),
            }
        )

    return pd.DataFrame(rows)


def complete_word_tolerance_summary(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """Percentage of words whose start and end both fall within each tolerance."""
    rows: list[dict] = []

    for aligner, prefix in (("MFA", "mfa"), ("WebMAUS", "webmaus")):
        result: dict[str, float | str] = {"aligner": aligner}

        for threshold in (20, 50, 100):
            both_edges = (
                analysis_df[f"{prefix}_abs_start_error_ms"] <= threshold
            ) & (
                analysis_df[f"{prefix}_abs_end_error_ms"] <= threshold
            )
            result[f"words_both_edges_within_{threshold}ms_pct"] = float(
                100 * both_edges.mean()
            )

        rows.append(result)

    return pd.DataFrame(rows)
