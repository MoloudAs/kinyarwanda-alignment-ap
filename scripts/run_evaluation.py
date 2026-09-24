#!/usr/bin/env python3
"""Command-line entry point for the Kinyarwanda alignment AP project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kinyarwanda_alignment.config import load_config  # noqa: E402
from kinyarwanda_alignment.pipeline import run_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Build and evaluate the canonical Manual–MFA–WebMAUS "
            "Kinyarwanda word-alignment dataset."
        )
    )
    parser.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config" / "config.yaml"),
        help="Path to the YAML configuration file.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the complete evaluation pipeline."""
    args = parse_args()
    config = load_config(args.config)
    result = run_pipeline(config)

    print("=" * 72)
    print("KINYARWANDA ALIGNMENT EVALUATION: COMPLETE")
    print("=" * 72)
    print(f"Words: {len(result['evaluation_df']):,}")
    print(
        "Recordings:",
        result["evaluation_df"]["file_id"].nunique(),
    )
    print(f"Canonical CSV: {result['canonical_csv']}")
    print(f"Tables: {result['tables_dir']}")
    print(f"Figures: {result['figures_dir']}")
    print("\nInterpretation: in-domain validation of the final Storyboard-adapted MFA system.")
    print("=" * 72)


if __name__ == "__main__":
    main()
