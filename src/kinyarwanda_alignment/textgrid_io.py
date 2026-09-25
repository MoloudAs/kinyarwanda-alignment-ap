"""Functions for loading TextGrid files and accessing their tiers."""

from pathlib import Path

import textgrid


class TextGridStructureError(ValueError):
    """Represents an error in the expected TextGrid tier structure."""


def load_textgrid(path: str | Path) -> textgrid.TextGrid:
    """Loads a TextGrid file from disk."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"TextGrid not found: {path}")

    return textgrid.TextGrid.fromFile(str(path))


def get_required_tier(
    tg: textgrid.TextGrid,
    tier_name: str,
):
    """Returns a tier with the requested name."""

    if tier_name not in tg.getNames():
        raise TextGridStructureError(
            f"Required tier {tier_name!r} not found. "
            f"Available tiers: {tg.getNames()}"
        )

    return tg.getFirst(tier_name)


def get_single_manual_tier(
    tg: textgrid.TextGrid,
    expected_annotator: str | None = None,
):
    """Returns the single manual tier from a reference TextGrid."""

    manual_names = [
        name
        for name in tg.getNames()
        if name.lower().startswith("manual")
    ]

    if len(manual_names) != 1:
        raise TextGridStructureError(
            f"Expected exactly one manual tier, found: {manual_names}"
        )

    manual_name = manual_names[0]

    if expected_annotator is not None:
        expected_name = f"manual{expected_annotator}"

        if manual_name.casefold() != expected_name.casefold():
            raise TextGridStructureError(
                f"Expected manual tier {expected_name!r}, "
                f"found {manual_name!r}."
            )

    return tg.getFirst(manual_name), manual_name


def nonempty_intervals(tier) -> list:
    """Returns intervals that contain a label."""

    if not hasattr(tier, "intervals"):
        return []

    return [
        interval
        for interval in tier.intervals
        if str(interval.mark).strip()
    ]
