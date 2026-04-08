from typing import Any
from app.config.loader import load_core_config, load_profile_config
from app.config.merger import deep_merge
from app.config.validator import validate_config
from pathlib import Path

class ProfileManager:
    def __init__(self, config_dir: str = "config"):
        self._config_dir = config_dir
        self._core = load_core_config(config_dir)

    def get_config(self, profile: str = "default") -> dict[str, Any]:
        profile_cfg = load_profile_config(profile, self._config_dir)

        # Support one level of inheritance
        parent = profile_cfg.pop("extends", None)
        if parent:
            parent_cfg = load_profile_config(parent, self._config_dir)
            merged = deep_merge(self._core, parent_cfg)
            merged = deep_merge(merged, profile_cfg)
        else:
            merged = deep_merge(self._core, profile_cfg)

        validate_config(merged)
        return merged
