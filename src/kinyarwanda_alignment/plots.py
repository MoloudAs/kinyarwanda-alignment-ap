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
        figsize=(4.2, 3.6)
    )

    # Connect the two values for every recording.
    for row in per_file_df.itertuples(
        index=False
    ):
        if row.MFA_MAE_ms < row.WebMAUS_MAE_ms:
            color = "#009E73"
            linestyle = "-"
        else:
            color = "#CC79A7"
            linestyle = "--"

        ax.plot(
            [0, 1],
            [
                row.MFA_MAE_ms,
                row.WebMAUS_MAE_ms,
            ],
            color=color,
            linestyle=linestyle,
            linewidth=1.2,
            alpha=0.75,
            zorder=1,
        )

    # MFA points
    ax.scatter(
        np.zeros(len(per_file_df)),
        per_file_df["MFA_MAE_ms"],
        color="#0072B2",
        s=28,
        edgecolor="white",
        linewidth=0.4,
        zorder=3,
    )

    # WebMAUS points
    ax.scatter(
        np.ones(len(per_file_df)),
        per_file_df["WebMAUS_MAE_ms"],
        color="#E69F00",
        s=28,
        edgecolor="white",
        linewidth=0.4,
        zorder=3,
    )

    ax.set_xticks(
        [0, 1],
        ["MFA", "WebMAUS"],
    )

    ax.set_ylabel(
        "Recording MAE (ms)"
    )

    ax.set_ylim(bottom=0)

    # Light horizontal grid
    ax.grid(
        axis="y",
        linestyle=":",
        linewidth=0.6,
        color="0.82",
    )

    # Cleaner frame
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Small legend without another import
    ax.plot(
        [],
        [],
        color="#009E73",
        linestyle="-",
        label="MFA lower error (13)",
    )

    ax.plot(
        [],
        [],
        color="#CC79A7",
        linestyle="--",
        label="WebMAUS lower error (3)",
    )

    ax.legend(
    frameon=False,
    loc="lower center",
    bbox_to_anchor=(0.5, 1.02),
    fontsize=7,
    ncol=2,
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.03,
    )

    plt.close(fig)