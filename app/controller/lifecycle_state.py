from dataclasses import dataclass, field
from app.shared.enums import LifecycleState
from app.shared.time_utils import utcnow_iso

@dataclass
class LifecycleStateModel:
    state: LifecycleState = LifecycleState.IDLE
    profile: str = "default"
    started_at: str | None = None
    stopped_at: str | None = None
    fault_reason: str | None = None
    cycle_count: int = 0
    error_count: int = 0
