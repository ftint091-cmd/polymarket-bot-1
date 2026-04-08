from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class RuntimeConfig:
    execution_mode: str
    cycle_interval_seconds: int
    profile: str
    raw: dict  # original merged config dict

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)

    @classmethod
    def from_dict(cls, config: dict[str, Any], profile: str = "default") -> "RuntimeConfig":
        return cls(
            execution_mode=config.get("execution_mode", "paper"),
            cycle_interval_seconds=int(config.get("cycle_interval_seconds", 60)),
            profile=profile,
            raw=config,
        )
