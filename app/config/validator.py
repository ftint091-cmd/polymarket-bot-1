import os
from typing import Any
from app.shared.exceptions import ConfigError

REQUIRED_KEYS = ["execution_mode", "cycle_interval_seconds"]

def validate_config(config: dict[str, Any]) -> None:
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing required config key: {key}")

    mode = config.get("execution_mode", "paper")
    if mode not in ("paper", "fake_real", "real"):
        raise ConfigError(f"Invalid execution_mode: {mode}")

    if mode == "real":
        if os.environ.get("ENABLE_REAL_TRADING", "").lower() != "true":
            raise ConfigError("execution_mode=real requires ENABLE_REAL_TRADING=true env var")
