import os
import tomllib
from pathlib import Path


def get_fluxqueue_config():
    toml_path = Path(os.getcwd()) / "pyproject.toml"

    if not toml_path.exists():
        return {}

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("tool", {}).get("fluxqueue_cli", {})

    except (tomllib.TOMLDecodeError, PermissionError):
        return {}
