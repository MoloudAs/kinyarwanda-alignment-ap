"""TextGrid loading and tier-access helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import textgrid


class TextGridStructureError(ValueError):
    """Raised when a TextGrid does not have the required tier structure."""


def load_textgrid(path: str | Path) -> textgrid.TextGrid:
    """Load a TextGrid from disk with a clear error message."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"TextGrid not found: {path}")
    try:
        return textgrid.TextGrid.fromFile(str(path))
    except Exception as exc:  # library exposes heterogeneous parse exceptions
        raise TextGridStructureError(f"Could not read TextGrid: {path}") from exc


def get_required_tier(tg: textgrid.TextGrid, tier_name: str):
    """Return a tier by exact name or raise a descriptive error."""
    if tier_name not in tg.getNames():
        raise TextGridStructureError(
            f"Required tier {tier_name!r} not found. Available tiers: {tg.getNames()}"
        )
    return tg.getFirst(tier_name)


def get_single_manual_tier(tg: textgrid.TextGrid, expected_annotator: str | None = None):
    """Return the single ``manual*`` tier from a merged reference TextGrid."""
    manual_names = [name for name in tg.getNames() if name.lower().startswith("manual")]
    if len(manual_names) != 1:
        raise TextGridStructureError(
            f"Expected exactly one manual* tier, found: {manual_names}"
        )

    manual_name = manual_names[0]
    if expected_annotator is not None:
        expected = f"manual{expected_annotator}"
        if manual_name.casefold() != expected.casefold():
            raise TextGridStructureError(
                f"Expected manual tier {expected!r}, found {manual_name!r}."
            )
    return tg.getFirst(manual_name), manual_name


def nonempty_intervals(tier) -> list:
    """Return intervals whose labels are not empty or whitespace-only."""
    if not hasattr(tier, "intervals"):
        return []
    return [interval for interval in tier.intervals if str(interval.mark).strip()]


def tier_names(tg: textgrid.TextGrid) -> list[str]:
    """Return tier names as a plain list."""
    return list(tg.getNames())


def require_tiers(tg: textgrid.TextGrid, required: Iterable[str]) -> None:
    """Validate that every required tier is present."""
    missing = [name for name in required if name not in tg.getNames()]
    if missing:
        raise TextGridStructureError(
            f"Missing required tiers {missing}; available tiers: {tg.getNames()}"
        )
