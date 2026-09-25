"""Functions for matching word sequences across alignment systems."""

from collections.abc import Sequence

from .file_utils import normalize_word


class SequenceMatchError(ValueError):
    """Represents an error when a word sequence cannot be matched uniquely."""


def find_contiguous_sequence(
    target_labels: Sequence[str],
    candidate_labels: Sequence[str],
) -> list[int]:
    """Returns all positions where the target sequence occurs."""

    target = list(target_labels)
    candidate = list(candidate_labels)

    n_target = len(target)
    n_candidate = len(candidate)

    if n_target == 0 or n_target > n_candidate:
        return []

    starts = []

    # Match words only by their labels and order, not by timing.
    for start in range(n_candidate - n_target + 1):
        candidate_part = candidate[start : start + n_target]

        if candidate_part == target:
            starts.append(start)

    return starts


def normalized_labels(intervals: Sequence) -> list[str]:
    """Returns normalized word labels from a sequence of intervals."""

    return [
        normalize_word(interval.mark)
        for interval in intervals
    ]


def find_unique_sequence_start(
    target_labels: Sequence[str],
    candidate_labels: Sequence[str],
    source_label: str,
) -> int:
    """Returns the starting position of one unique sequence match."""

    starts = find_contiguous_sequence(
        target_labels,
        candidate_labels,
    )

    if len(starts) != 1:
        raise SequenceMatchError(
            f"Expected exactly one complete manual sequence in "
            f"{source_label}; found {len(starts)}."
        )

    return starts[0]