"""Configuration loading for the AP pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised for missing or invalid configuration values."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Load YAML configuration and resolve project-relative paths."""
    config_path = Path(path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    if "project_root" not in config:
        raise ConfigurationError("Configuration must define 'project_root'.")

    configured_root = Path(config["project_root"])
    project_root = (
        configured_root.resolve()
        if configured_root.is_absolute()
        else (config_path.parent.parent / configured_root).resolve()
    )
    config["project_root"] = project_root

    for section_name in ("inputs", "outputs"):
        section = config.get(section_name, {})
        for key, value in list(section.items()):
            path_value = Path(value)
            section[key] = (
                path_value.resolve()
                if path_value.is_absolute()
                else (project_root / path_value).resolve()
            )
        config[section_name] = section

    return config
