from dataclasses import dataclass, field
from typing import Any

@dataclass
class SystemStatus:
    cycle_id: str
    timestamp: str
    lifecycle_state: str
    execution_mode: str
    cycle_count: int
    error_count: int
    last_cycle_status: str
    details: dict[str, Any] = field(default_factory=dict)
