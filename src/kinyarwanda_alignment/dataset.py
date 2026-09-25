"""Builds the Manual-MFA-WebMAUS word-level evaluation dataset."""

from pathlib import Path

import pandas as pd

from .file_utils import (
    extract_file_id,
    extract_gender,
    extract_recording_location,
)
from .matching import find_unique_sequence_start, normalized_labels
from .textgrid_io import (
    get_required_tier,
    get_single_manual_tier,
    load_textgrid,
    nonempty_intervals,
)


DEFAULT_ANNOTATORS = {
    "Annotator_1",
    "Annotator_2",
    "Annotator_3",
    "Annotator_4",
}


class DatasetConstructionError(ValueError):
    """Represents an error while building the evaluation dataset."""


def build_id_lookup(paths: list[Path]) -> dict[str, Path]:
    """Builds a dictionary that maps recording IDs to file paths."""

    lookup = {}

    for path in paths:
        file_id = extract_file_id(path.name)

        if file_id is None:
            raise DatasetConstructionError(
                f"Could not extract recording ID from: {path}"
            )

        if file_id in lookup:
            raise DatasetConstructionError(
                f"Duplicate recording ID {file_id}: "
                f"{lookup[file_id]} and {path}"
            )

        lookup[file_id] = path

    return lookup


def collect_evaluation_files(
    manual_reference_dir: str | Path,
    webmaus_dir: str | Path,
) -> tuple[dict[str, Path], dict[str, Path]]:
    """Collects Manual and WebMAUS TextGrid files and compares their IDs."""

    manual_dir = Path(manual_reference_dir)
    web_dir = Path(webmaus_dir)

    manual_paths = sorted(manual_dir.rglob("*.TextGrid"))
    webmaus_paths = sorted(web_dir.glob("*.TextGrid"))

    manual_lookup = build_id_lookup(manual_paths)
    webmaus_lookup = build_id_lookup(webmaus_paths)

    manual_ids = set(manual_lookup)
    webmaus_ids = set(webmaus_lookup)

    if manual_ids != webmaus_ids:
        missing_in_webmaus = sorted(manual_ids - webmaus_ids)
        missing_in_manual = sorted(webmaus_ids - manual_ids)

        raise DatasetConstructionError(
            "Manual and WebMAUS recording IDs do not match. "
            f"Missing in WebMAUS: {missing_in_webmaus}. "
            f"Missing in Manual: {missing_in_manual}."
        )

    return manual_lookup, webmaus_lookup


def _build_recording_rows(
    file_id: str,
    manual_path: Path,
    webmaus_path: Path,
    expected_annotators: set[str],
) -> list[dict]:
    """Builds the evaluation rows for one recording."""

    annotator = manual_path.parent.name

    if annotator not in expected_annotators:
        raise DatasetConstructionError(
            f"Unexpected annotator folder {annotator!r} "
            f"for {manual_path.name}."
        )

    # Load the Manual and MFA tiers.
    merged_tg = load_textgrid(manual_path)

    manual_tier, manual_tier_name = get_single_manual_tier(
        merged_tg,
        expected_annotator=annotator,
    )

    mfa_tier = get_required_tier(merged_tg, "wordsMFA")

    # Load the WebMAUS tier.
    webmaus_tg = load_textgrid(webmaus_path)
    webmaus_tier = get_required_tier(webmaus_tg, "ORT-MAU")

    # Keep only intervals that contain words.
    manual_words = nonempty_intervals(manual_tier)
    mfa_words = nonempty_intervals(mfa_tier)
    webmaus_words = nonempty_intervals(webmaus_tier)

    if not manual_words:
        raise DatasetConstructionError(
            f"{manual_path.name}: "
            f"{manual_tier_name} contains no labelled intervals."
        )

    # Normalize labels before matching.
    manual_labels = normalized_labels(manual_words)
    mfa_labels = normalized_labels(mfa_words)
    webmaus_labels = normalized_labels(webmaus_words)

    # Find the Manual sequence inside MFA and WebMAUS.
    mfa_start = find_unique_sequence_start(
        manual_labels,
        mfa_labels,
        source_label="wordsMFA",
    )

    webmaus_start = find_unique_sequence_start(
        manual_labels,
        webmaus_labels,
        source_label="ORT-MAU",
    )

    rows = []

    for local_index, manual_interval in enumerate(manual_words):
        mfa_index = mfa_start + local_index
        webmaus_index = webmaus_start + local_index

        mfa_interval = mfa_words[mfa_index]
        webmaus_interval = webmaus_words[webmaus_index]

        manual_label = manual_labels[local_index]
        mfa_label = mfa_labels[mfa_index]
        webmaus_label = webmaus_labels[webmaus_index]

        if not (manual_label == mfa_label == webmaus_label):
            raise DatasetConstructionError(
                f"{manual_path.name}, word {local_index + 1}: "
                "lexical mismatch after sequence matching."
            )

        row = {
            "filename": manual_path.name,
            "file_id": file_id,
            "annotator": annotator,
            "gender": extract_gender(manual_path.name),
            "recording_location": extract_recording_location(
                manual_path.name
            ),
            "word_index": local_index + 1,
            "word": str(manual_interval.mark).strip(),
            "manual_start": float(manual_interval.minTime),
            "manual_end": float(manual_interval.maxTime),
            "mfa_start": float(mfa_interval.minTime),
            "mfa_end": float(mfa_interval.maxTime),
            "webmaus_start": float(webmaus_interval.minTime),
            "webmaus_end": float(webmaus_interval.maxTime),
        }

        rows.append(row)

    return rows


def build_evaluation_dataframe(
    manual_reference_dir: str | Path,
    webmaus_dir: str | Path,
    expected_files: int | None = 16,
    expected_words: int | None = 3676,
    expected_annotators: set[str] | None = None,
) -> pd.DataFrame:
    """Builds the complete word-level evaluation dataframe."""

    manual_lookup, webmaus_lookup = collect_evaluation_files(
        manual_reference_dir,
        webmaus_dir,
    )

    if expected_files is not None:
        if len(manual_lookup) != expected_files:
            raise DatasetConstructionError(
                f"Expected {expected_files} evaluation recordings; "
                f"found {len(manual_lookup)}."
            )

    if expected_annotators is None:
        expected_annotators = DEFAULT_ANNOTATORS

    rows = []

    for file_id in sorted(manual_lookup):
        manual_path = manual_lookup[file_id]
        webmaus_path = webmaus_lookup[file_id]

        recording_rows = _build_recording_rows(
            file_id,
            manual_path,
            webmaus_path,
            expected_annotators,
        )

        rows.extend(recording_rows)

    df = pd.DataFrame(rows)

    df = df.sort_values(
        ["file_id", "word_index"]
    ).reset_index(drop=True)

    validate_canonical_dataframe(
        df,
        expected_files=expected_files,
        expected_words=expected_words,
        expected_annotators=len(expected_annotators),
    )

    return df


def validate_canonical_dataframe(
    df: pd.DataFrame,
    expected_files: int | None = 16,
    expected_words: int | None = 3676,
    expected_annotators: int | None = 4,
) -> None:
    """Checks the structure and contents of the evaluation dataframe."""

    required_columns = [
        "filename",
        "file_id",
        "annotator",
        "gender",
        "recording_location",
        "word_index",
        "word",
        "manual_start",
        "manual_end",
        "mfa_start",
        "mfa_end",
        "webmaus_start",
        "webmaus_end",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise DatasetConstructionError(
            f"Canonical dataframe missing columns: {missing_columns}"
        )

    if expected_words is not None:
        if len(df) != expected_words:
            raise DatasetConstructionError(
                f"Expected {expected_words} rows; found {len(df)}."
            )

    recording_count = df["file_id"].nunique()

    if expected_files is not None:
        if recording_count != expected_files:
            raise DatasetConstructionError(
                f"Expected {expected_files} recordings; "
                f"found {recording_count}."
            )

    annotator_count = df["annotator"].nunique()

    if expected_annotators is not None:
        if annotator_count != expected_annotators:
            raise DatasetConstructionError(
                f"Expected {expected_annotators} annotators; "
                f"found {annotator_count}."
            )

    boundary_columns = [
        "manual_start",
        "manual_end",
        "mfa_start",
        "mfa_end",
        "webmaus_start",
        "webmaus_end",
    ]

    missing_boundaries = (
        df[boundary_columns]
        .isna()
        .any()
        .any()
    )

    if missing_boundaries:
        raise DatasetConstructionError(
            "Missing boundary values detected."
        )

    for source in ["manual", "mfa", "webmaus"]:
        invalid_intervals = (
            df[f"{source}_start"] > df[f"{source}_end"]
        ).sum()

        if invalid_intervals:
            raise DatasetConstructionError(
                f"Found {invalid_intervals} {source} intervals "
                "with start > end."
            )

    duplicate_rows = df.duplicated(
        ["file_id", "word_index"]
    ).any()

    if duplicate_rows:
        raise DatasetConstructionError(
            "Duplicate file_id + word_index rows detected."
        )

    for file_id, group in df.groupby("file_id"):
        observed_indices = (
            group
            .sort_values("word_index")["word_index"]
            .tolist()
        )

        expected_indices = list(
            range(1, len(group) + 1)
        )

        if observed_indices != expected_indices:
            raise DatasetConstructionError(
                f"Non-continuous word indices "
                f"in recording {file_id}."
            )

    metadata_columns = [
        "gender",
        "recording_location",
    ]

    missing_metadata = (
        df[metadata_columns]
        .isna()
        .any()
        .any()
    )

    if missing_metadata:
        raise DatasetConstructionError(
            "Filename-derived metadata are incomplete."
        )