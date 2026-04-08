from dataclasses import dataclass, field
from typing import Any

@dataclass
class Position:
    position_id: str
    market_id: str
    side: str
    size: float
    entry_price: float
    current_price: float
    pnl: float = 0.0
    opened_at: str = ""
    order_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
