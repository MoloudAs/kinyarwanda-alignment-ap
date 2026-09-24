"""Top-level orchestration for the presentation-friendly AP pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .dataset import build_evaluation_dataframe
from .diagnostics import large_error_summary, top_error_words
from .file_utils import sha256_file
from .metrics import (
    add_error_columns,
    build_edge_dataframe,
    complete_word_tolerance_summary,
    overall_edge_summary,
)
from .plots import save_cumulative_edge_error, save_paired_recording_mae
from .statistics import paired_recording_test, recording_level_summary


def _save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Save a dataframe as UTF-8 CSV, creating its parent folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def run_pipeline(config: dict) -> dict[str, object]:
    """Run the complete but intentionally compact AP evaluation pipeline."""
    inputs = config["inputs"]
    outputs = config["outputs"]
    expected = config.get("expected", {})
    analysis_cfg = config.get("analysis", {})

    expected_annotators = set(
        expected["annotators"]
    )

    # 1. Build and validate the canonical Manual–MFA–WebMAUS word table.
    evaluation_df = build_evaluation_dataframe(
        inputs["manual_reference_dir"],
        inputs["webmaus_dir"],
        expected_files=expected.get("evaluation_files", 16),
        expected_words=expected.get("manual_words", 3676),
        expected_annotators=expected_annotators,
    )

    canonical_csv = Path(outputs["canonical_csv"])
    _save_dataframe(evaluation_df, canonical_csv)

    # 2. Calculate boundary errors.
    analysis_df = add_error_columns(evaluation_df)
    edge_df = build_edge_dataframe(analysis_df)

    # 3. Summarize the main descriptive measures.
    overall_df = overall_edge_summary(edge_df, n_words=len(analysis_df))
    tolerance_df = complete_word_tolerance_summary(analysis_df)

    # 4. Compare MFA and WebMAUS once per recording.
    per_file_df = recording_level_summary(analysis_df)
    recording_test = paired_recording_test(per_file_df)

    # 5. Keep error inspection small and interpretable.
    large_errors_df = large_error_summary(edge_df)
    top_errors_df = top_error_words(
        analysis_df,
        top_n_per_aligner=analysis_cfg.get("top_error_words_per_aligner", 10),
    )

    tables_dir = Path(outputs["tables_dir"])
    figures_dir = Path(outputs["figures_dir"])
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    _save_dataframe(overall_df, tables_dir / "overall_edge_summary.csv")
    _save_dataframe(tolerance_df, tables_dir / "word_tolerance_summary.csv")
    _save_dataframe(per_file_df, tables_dir / "recording_level_summary.csv")
    _save_dataframe(large_errors_df, tables_dir / "large_error_summary.csv")
    _save_dataframe(top_errors_df, tables_dir / "top_error_words.csv")

    (tables_dir / "recording_level_test.json").write_text(
        json.dumps(recording_test, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    (tables_dir / "canonical_dataset_sha256.txt").write_text(
        sha256_file(canonical_csv) + "  " + canonical_csv.name + "\n",
        encoding="utf-8",
    )

    save_cumulative_edge_error(
        edge_df,
        figures_dir / "cumulative_word_edge_error.pdf",
    )
    save_paired_recording_mae(
        per_file_df,
        figures_dir / "paired_recording_mae.pdf",
    )

    return {
        "evaluation_df": evaluation_df,
        "analysis_df": analysis_df,
        "edge_df": edge_df,
        "overall_summary": overall_df,
        "tolerance_summary": tolerance_df,
        "recording_summary": per_file_df,
        "recording_test": recording_test,
        "large_error_summary": large_errors_df,
        "top_error_words": top_errors_df,
        "canonical_csv": canonical_csv,
        "tables_dir": tables_dir,
        "figures_dir": figures_dir,
    }
