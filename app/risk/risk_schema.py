from dataclasses import dataclass

@dataclass
class RiskCheckResult:
    approved: bool
    approved_size: float
    rejection_reason: str | None
    capital_available: float
    exposure_before: float
