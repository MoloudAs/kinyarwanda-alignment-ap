"""Runs the complete Kinyarwanda alignment evaluation pipeline."""

import json
from pathlib import Path

import pandas as pd

from .dataset import build_evaluation_dataframe
from .diagnostics import large_error_summary, top_error_words
from .metrics import (
    add_error_columns,
    build_edge_dataframe,
    complete_word_tolerance_summary,
    overall_edge_summary,
)
from .plots import (
    save_cumulative_edge_error,
    save_paired_recording_mae,
)
from .statistics import (
    paired_recording_test,
    recording_level_summary,
)


def _save_dataframe(
    df: pd.DataFrame,
    path: Path,
) -> None:
    """Saves a dataframe as a UTF-8 CSV file."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )


def run_pipeline(config: dict) -> dict:
    """Runs all stages of the alignment evaluation."""

    inputs = config["inputs"]
    outputs = config["outputs"]

    expected = config.get(
        "expected",
        {},
    )

    analysis_config = config.get(
        "analysis",
        {},
    )

    expected_annotators = set(
        expected["annotators"]
    )

    # 1. Build and validate the word-level dataset.
    evaluation_df = build_evaluation_dataframe(
        inputs["manual_reference_dir"],
        inputs["webmaus_dir"],
        expected_files=expected.get(
            "evaluation_files",
            16,
        ),
        expected_words=expected.get(
            "manual_words",
            3676,
        ),
        expected_annotators=expected_annotators,
    )

    canonical_csv = Path(
        outputs["canonical_csv"]
    )

    _save_dataframe(
        evaluation_df,
        canonical_csv,
    )

    # 2. Calculate boundary errors.
    analysis_df = add_error_columns(
        evaluation_df
    )

    edge_df = build_edge_dataframe(
        analysis_df
    )

    # 3. Calculate descriptive summaries.
    overall_df = overall_edge_summary(
        edge_df,
        n_words=len(analysis_df),
    )

    tolerance_df = complete_word_tolerance_summary(
        analysis_df
    )

    # 4. Compare the aligners at the recording level.
    recording_df = recording_level_summary(
        analysis_df
    )

    recording_test = paired_recording_test(
        recording_df
    )

    # 5. Inspect large errors.
    large_errors_df = large_error_summary(
        edge_df
    )

    top_errors_df = top_error_words(
        analysis_df,
        top_n_per_aligner=analysis_config.get(
            "top_error_words_per_aligner",
            10,
        ),
    )

    # 6. Prepare output folders.
    tables_dir = Path(
        outputs["tables_dir"]
    )

    figures_dir = Path(
        outputs["figures_dir"]
    )

    tables_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    figures_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 7. Save result tables.
    _save_dataframe(
        overall_df,
        tables_dir / "overall_edge_summary.csv",
    )

    _save_dataframe(
        tolerance_df,
        tables_dir / "word_tolerance_summary.csv",
    )

    _save_dataframe(
        recording_df,
        tables_dir / "recording_level_summary.csv",
    )

    _save_dataframe(
        large_errors_df,
        tables_dir / "large_error_summary.csv",
    )

    _save_dataframe(
        top_errors_df,
        tables_dir / "top_error_words.csv",
    )

    # 8. Save the recording-level statistical result.
    test_path = (
        tables_dir
        / "recording_level_test.json"
    )

    test_path.write_text(
        json.dumps(
            recording_test,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # 9. Create figures.
    save_cumulative_edge_error(
        edge_df,
        figures_dir
        / "cumulative_word_edge_error.pdf",
    )

    save_paired_recording_mae(
        recording_df,
        figures_dir
        / "paired_recording_mae.pdf",
    )

    return {
        "evaluation_df": evaluation_df,
        "analysis_df": analysis_df,
        "edge_df": edge_df,
        "overall_summary": overall_df,
        "tolerance_summary": tolerance_df,
        "recording_summary": recording_df,
        "recording_test": recording_test,
        "large_error_summary": large_errors_df,
        "top_error_words": top_errors_df,
        "canonical_csv": canonical_csv,
        "tables_dir": tables_dir,
        "figures_dir": figures_dir,
    }