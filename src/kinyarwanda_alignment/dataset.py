"""Build the canonical Manual–MFA–WebMAUS word-level evaluation dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .file_utils import (
    extract_file_id,
    extract_gender,
    extract_recording_location,
    normalize_word,
)
from .matching import find_unique_sequence_start, normalized_labels
from .textgrid_io import (
    get_required_tier,
    get_single_manual_tier,
    load_textgrid,
    nonempty_intervals,
)


class DatasetConstructionError(ValueError):
    """Raised when the canonical evaluation table cannot be built safely."""


def build_id_lookup(paths: list[Path]) -> dict[str, Path]:
    """Build a unique ``recording_id -> path`` lookup."""
    lookup: dict[str, Path] = {}
    for path in paths:
        file_id = extract_file_id(path.name)
        if file_id is None:
            raise DatasetConstructionError(f"Could not extract recording ID from: {path}")
        if file_id in lookup:
            raise DatasetConstructionError(
                f"Duplicate recording ID {file_id}:\n{lookup[file_id]}\n{path}"
            )
        lookup[file_id] = path
    return lookup


def collect_evaluation_files(
    manual_reference_dir: str | Path,
    webmaus_dir: str | Path,
) -> tuple[dict[str, Path], dict[str, Path]]:
    """Collect and cross-check Manual and WebMAUS evaluation TextGrids."""
    manual_dir = Path(manual_reference_dir)
    web_dir = Path(webmaus_dir)

    manual_paths = sorted(manual_dir.rglob("*.TextGrid"))
    webmaus_paths = sorted(web_dir.glob("*.TextGrid"))

    manual_lookup = build_id_lookup(manual_paths)
    webmaus_lookup = build_id_lookup(webmaus_paths)

    if set(manual_lookup) != set(webmaus_lookup):
        missing_in_web = sorted(set(manual_lookup) - set(webmaus_lookup))
        missing_in_manual = sorted(set(webmaus_lookup) - set(manual_lookup))
        raise DatasetConstructionError(
            "Manual and WebMAUS recording-ID sets differ. "
            f"Missing in WebMAUS={missing_in_web}; missing in Manual={missing_in_manual}."
        )

    return manual_lookup, webmaus_lookup


def build_evaluation_dataframe(
    manual_reference_dir: str | Path,
    webmaus_dir: str | Path,
    *,
    expected_files: int | None = 16,
    expected_words: int | None = 3676,
    expected_annotators: set[str] | None = None,
) -> pd.DataFrame:
    """Construct the canonical word-level boundary table.

    Correspondence is determined from normalized lexical identity + order.
    Boundary times are extracted only after the complete manual sequence has
    been verified to occur exactly once in both ``wordsMFA`` and ``ORT-MAU``.
    """
    manual_lookup, webmaus_lookup = collect_evaluation_files(
        manual_reference_dir,
        webmaus_dir,
    )

    if expected_files is not None and len(manual_lookup) != expected_files:
        raise DatasetConstructionError(
            f"Expected {expected_files} evaluation recordings; found {len(manual_lookup)}."
        )

    expected_annotators = expected_annotators or {
        "Annotator_1",
        "Annotator_2",
        "Annotator_3",
        "Annotator_4",
    }

    rows: list[dict] = []

    for file_id in sorted(manual_lookup):
        manual_path = manual_lookup[file_id]
        webmaus_path = webmaus_lookup[file_id]
        annotator = manual_path.parent.name

        if annotator not in expected_annotators:
            raise DatasetConstructionError(
                f"Unexpected annotator folder {annotator!r} for {manual_path.name}."
            )

        merged_tg = load_textgrid(manual_path)
        manual_tier, manual_tier_name = get_single_manual_tier(
            merged_tg,
            expected_annotator=annotator,
        )
        mfa_tier = get_required_tier(merged_tg, "wordsMFA")

        web_tg = load_textgrid(webmaus_path)
        web_tier = get_required_tier(web_tg, "ORT-MAU")

        manual_words = nonempty_intervals(manual_tier)
        mfa_words = nonempty_intervals(mfa_tier)
        web_words = nonempty_intervals(web_tier)

        if not manual_words:
            raise DatasetConstructionError(
                f"{manual_path.name}: {manual_tier_name} contains no labelled intervals."
            )

        manual_labels = normalized_labels(manual_words)
        mfa_labels = normalized_labels(mfa_words)
        web_labels = normalized_labels(web_words)

        mfa_start = find_unique_sequence_start(
            manual_labels,
            mfa_labels,
            source_label="wordsMFA",
        )
        web_start = find_unique_sequence_start(
            manual_labels,
            web_labels,
            source_label="ORT-MAU",
        )

        for local_index, manual_interval in enumerate(manual_words):
            mfa_interval = mfa_words[mfa_start + local_index]
            web_interval = web_words[web_start + local_index]

            manual_norm = normalize_word(manual_interval.mark)
            mfa_norm = normalize_word(mfa_interval.mark)
            web_norm = normalize_word(web_interval.mark)

            if not (manual_norm == mfa_norm == web_norm):
                raise DatasetConstructionError(
                    f"{manual_path.name}, word {local_index + 1}: lexical mismatch "
                    "after sequence matching."
                )

            rows.append(
                {
                    "filename": manual_path.name,
                    "file_id": file_id,
                    "annotator": annotator,
                    "gender": extract_gender(manual_path.name),
                    "recording_location": extract_recording_location(manual_path.name),
                    "word_index": local_index + 1,
                    "word": str(manual_interval.mark).strip(),
                    "manual_start": float(manual_interval.minTime),
                    "manual_end": float(manual_interval.maxTime),
                    "mfa_start": float(mfa_interval.minTime),
                    "mfa_end": float(mfa_interval.maxTime),
                    "webmaus_start": float(web_interval.minTime),
                    "webmaus_end": float(web_interval.maxTime),
                }
            )

    df = pd.DataFrame(rows).sort_values(["file_id", "word_index"]).reset_index(drop=True)

    if expected_words is not None and len(df) != expected_words:
        raise DatasetConstructionError(
            f"Expected {expected_words} manual words; constructed {len(df)} rows."
        )

    validate_canonical_dataframe(
        df,
        expected_files=expected_files,
        expected_words=expected_words,
        expected_annotators=len(expected_annotators),
    )
    return df


def validate_canonical_dataframe(
    df: pd.DataFrame,
    *,
    expected_files: int | None = 16,
    expected_words: int | None = 3676,
    expected_annotators: int | None = 4,
) -> None:
    """Validate structural invariants of the canonical evaluation dataframe."""
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

    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise DatasetConstructionError(f"Canonical dataframe missing columns: {missing}")

    if expected_words is not None and len(df) != expected_words:
        raise DatasetConstructionError(f"Expected {expected_words} rows; found {len(df)}.")
    if expected_files is not None and df["file_id"].nunique() != expected_files:
        raise DatasetConstructionError(
            f"Expected {expected_files} recordings; found {df['file_id'].nunique()}."
        )
    if expected_annotators is not None and df["annotator"].nunique() != expected_annotators:
        raise DatasetConstructionError(
            f"Expected {expected_annotators} annotators; found {df['annotator'].nunique()}."
        )

    boundary_columns = [
        "manual_start",
        "manual_end",
        "mfa_start",
        "mfa_end",
        "webmaus_start",
        "webmaus_end",
    ]
    if df[boundary_columns].isna().any().any():
        raise DatasetConstructionError("Missing boundary values detected.")

    for source in ("manual", "mfa", "webmaus"):
        invalid = (df[f"{source}_start"] > df[f"{source}_end"]).sum()
        if invalid:
            raise DatasetConstructionError(
                f"Found {invalid} {source} intervals with start > end."
            )

    if df.duplicated(["file_id", "word_index"]).any():
        raise DatasetConstructionError("Duplicate file_id + word_index rows detected.")

    for file_id, group in df.groupby("file_id"):
        observed = group.sort_values("word_index")["word_index"].tolist()
        expected = list(range(1, len(group) + 1))
        if observed != expected:
            raise DatasetConstructionError(
                f"Non-continuous word indices in recording {file_id}."
            )

    if df[["gender", "recording_location"]].isna().any().any():
        raise DatasetConstructionError("Filename-derived metadata are incomplete.")
