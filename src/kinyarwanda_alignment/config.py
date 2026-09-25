"""Loads and prepares the YAML configuration for the evaluation pipeline."""

from pathlib import Path

import yaml


class ConfigurationError(ValueError):
    """Represents an error in the project configuration."""


def load_config(path: str | Path) -> dict:
    """Loads the YAML configuration and resolves project paths."""

    config_path = Path(path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file)

    if config is None:
        config = {}

    if "project_root" not in config:
        raise ConfigurationError(
            "Configuration must define 'project_root'."
        )

    configured_root = Path(
        config["project_root"]
    )

    if configured_root.is_absolute():
        project_root = configured_root.resolve()
    else:
        project_root = (
            config_path.parent.parent
            / configured_root
        ).resolve()

    config["project_root"] = project_root

    for section_name in ("inputs", "outputs"):
        section = config.get(
            section_name,
            {},
        )

        for key, value in section.items():
            path_value = Path(value)

            if path_value.is_absolute():
                resolved_path = path_value.resolve()
            else:
                resolved_path = (
                    project_root / path_value
                ).resolve()

            section[key] = resolved_path

        config[section_name] = section

    return config