from dataclasses import dataclass, field
from typing import Any
from app.shared.enums import CycleStatus

@dataclass
class CycleOutcome:
    cycle_id: str
    status: CycleStatus
    started_at: str
    finished_at: str
    markets_scanned: int = 0
    signals_generated: int = 0
    trades_attempted: int = 0
    trades_executed: int = 0
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    found_signals: list[dict[str, Any]] = field(default_factory=list)
