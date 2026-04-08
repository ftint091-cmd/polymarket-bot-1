from dataclasses import dataclass, field
from typing import Any

@dataclass
class AnalyticsSignal:
    signal_id: str
    market_id: str
    module: str
    score: float
    side: str  # "yes" or "no"
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ModuleOutput:
    module_name: str
    success: bool
    signals: list[AnalyticsSignal] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
