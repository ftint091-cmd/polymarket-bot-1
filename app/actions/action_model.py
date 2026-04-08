from dataclasses import dataclass
from typing import Any

@dataclass
class Action:
    action_type: str  # "place_order", "skip", "cancel"
    market_id: str | None
    side: str | None
    size: float
    price: float | None
    signal_id: str | None
    metadata: dict[str, Any] | None = None
