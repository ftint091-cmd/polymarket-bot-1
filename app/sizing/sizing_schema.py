from dataclasses import dataclass

@dataclass
class SizingResult:
    raw_size: float
    recommended_size: float
    applied_multiplier: float
    capped: bool
    cap_reason: str | None = None
