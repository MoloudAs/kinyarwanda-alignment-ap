from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kinyarwanda_alignment.config import (
    ConfigurationError,
    load_config,
)


def test_load_config_resolves_relative_paths(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "config.yaml"

    config_file.write_text(
        """
project_root: .

inputs:
  manual_reference_dir: data/manual_reference

outputs:
  tables_dir: results/tables
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    expected_root = tmp_path.resolve()

    assert config["project_root"] == expected_root

    assert config["inputs"]["manual_reference_dir"] == (
        expected_root / "data" / "manual_reference"
    )

    assert config["outputs"]["tables_dir"] == (
        expected_root / "results" / "tables"
    )


def test_load_config_requires_project_root(tmp_path):
    config_file = tmp_path / "config.yaml"

    config_file.write_text(
        """
inputs:
  manual_reference_dir: data/manual_reference
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        load_config(config_file)