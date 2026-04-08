from dataclasses import dataclass

@dataclass
class SizingPolicy:
    base_size: float = 10.0
    min_size: float = 1.0
    max_size: float = 500.0
    confidence_multiplier: bool = True
