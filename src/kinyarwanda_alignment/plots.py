"""Creates figures for the alignment evaluation."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_cumulative_edge_error(
    edge_df: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Saves a cumulative boundary-error figure."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    for aligner in ("MFA", "WebMAUS"):
        aligner_edges = edge_df[
            edge_df["aligner"] == aligner
        ]

        errors = (
            aligner_edges["absolute_error_ms"]
            .to_numpy()
        )

        errors = np.sort(errors)

        ranks = np.arange(
            1,
            len(errors) + 1,
        )

        cumulative = ranks / len(errors)

        ax.step(
            errors,
            cumulative,
            where="post",
            label=aligner,
        )

    ax.set_xlabel(
        "Absolute word-edge displacement (ms)"
    )

    ax.set_ylabel(
        "Cumulative proportion"
    )

    ax.set_title(
        "Automatic word edges relative to manual annotation"
    )

    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.01)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path)

    plt.close(fig)


def save_paired_recording_mae(
    per_file_df: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Saves the paired recording-level error figure."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(7, 5)
    )

    for row in per_file_df.itertuples(
        index=False
    ):
        ax.plot(
            [0, 1],
            [
                row.MFA_MAE_ms,
                row.WebMAUS_MAE_ms,
            ],
            marker="o",
            alpha=0.7,
        )

    ax.set_xticks(
        [0, 1],
        ["MFA", "WebMAUS"],
    )

    ax.set_ylabel(
        "Mean absolute word-boundary error (ms)"
    )

    ax.set_title(
        "Paired performance across recordings"
    )

    fig.tight_layout()
    fig.savefig(output_path)

    plt.close(fig)