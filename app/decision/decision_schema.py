from dataclasses import dataclass

@dataclass
class DecisionResult:
    should_trade: bool
    signal_id: str | None
    market_id: str | None
    side: str | None
    confidence: float
    reason: str
