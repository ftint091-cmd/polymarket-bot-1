from dataclasses import dataclass, field
from typing import Any

@dataclass
class MarketData:
    markets: list[dict[str, Any]] = field(default_factory=list)
    binance_context: dict[str, Any] = field(default_factory=dict)
    markets_count: int = 0

@dataclass
class AnalyticsOutput:
    signals: list[dict[str, Any]] = field(default_factory=list)
    module_outputs: dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionOutput:
    should_trade: bool = False
    signal_id: str | None = None
    market_id: str | None = None
    side: str | None = None
    confidence: float = 0.0
    reason: str = ""

@dataclass
class SizingOutput:
    recommended_size: float = 0.0
    raw_size: float = 0.0
    applied_multiplier: float = 1.0
    capped: bool = False

@dataclass
class CapitalRiskOutput:
    approved: bool = False
    approved_size: float = 0.0
    rejection_reason: str | None = None
    capital_available: float = 0.0
    exposure_before: float = 0.0

@dataclass
class ExecutionOutput:
    attempted: bool = False
    success: bool = False
    order_id: str | None = None
    filled_size: float = 0.0
    filled_price: float = 0.0
    mode: str = "paper"
    error: str | None = None

@dataclass
class CycleState:
    cycle_id: str = ""
    market_data: MarketData = field(default_factory=MarketData)
    analytics: AnalyticsOutput = field(default_factory=AnalyticsOutput)
    decision: DecisionOutput = field(default_factory=DecisionOutput)
    sizing: SizingOutput = field(default_factory=SizingOutput)
    capital_risk: CapitalRiskOutput = field(default_factory=CapitalRiskOutput)
    execution: ExecutionOutput = field(default_factory=ExecutionOutput)
