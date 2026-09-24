"""Lexical sequence matching for Manual–MFA–WebMAUS correspondence."""

from __future__ import annotations

from collections.abc import Sequence

from .file_utils import normalize_word


class SequenceMatchError(ValueError):
    """Raised when a manual word sequence cannot be matched uniquely."""


def find_contiguous_sequence(
    target_labels: Sequence[str],
    candidate_labels: Sequence[str],
) -> list[int]:
    """Return every start index where ``target_labels`` occurs contiguously.

    No timing information is used. This intentionally follows the validated
    research design: lexical identity and word order establish correspondence
    before boundary times are inspected.
    """
    n_target = len(target_labels)
    n_candidate = len(candidate_labels)

    if n_target == 0 or n_target > n_candidate:
        return []

    starts: list[int] = []
    for start in range(n_candidate - n_target + 1):
        if list(candidate_labels[start : start + n_target]) == list(target_labels):
            starts.append(start)
    return starts


def normalized_labels(intervals: Sequence) -> list[str]:
    """Normalize interval labels for conservative lexical matching."""
    return [normalize_word(interval.mark) for interval in intervals]


def find_unique_sequence_start(
    target_labels: Sequence[str],
    candidate_labels: Sequence[str],
    *,
    source_label: str,
) -> int:
    """Return the unique contiguous match start or raise ``SequenceMatchError``."""
    starts = find_contiguous_sequence(target_labels, candidate_labels)
    if len(starts) != 1:
        raise SequenceMatchError(
            f"Expected exactly one occurrence of the complete manual sequence "
            f"in {source_label}; found {len(starts)}."
        )
    return starts[0]
