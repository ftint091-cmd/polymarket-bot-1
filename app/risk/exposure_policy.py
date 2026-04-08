from dataclasses import dataclass

@dataclass
class ExposurePolicy:
    max_position_pct: float = 0.05  # 5% of capital per position
    max_total_exposure_pct: float = 0.25  # 25% of capital total
    min_capital_reserve_pct: float = 0.10  # Keep 10% in reserve
