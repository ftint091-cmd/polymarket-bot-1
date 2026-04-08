import os
from pathlib import Path
from typing import Any

def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return as dict."""
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data

def load_core_config(config_dir: str | Path = "config") -> dict[str, Any]:
    core_path = Path(config_dir) / "core.yaml"
    if core_path.exists():
        return load_yaml(core_path)
    return {}

def load_profile_config(profile: str, config_dir: str | Path = "config") -> dict[str, Any]:
    profile_path = Path(config_dir) / "profiles" / f"{profile}.yaml"
    if profile_path.exists():
        return load_yaml(profile_path)
    return {}
