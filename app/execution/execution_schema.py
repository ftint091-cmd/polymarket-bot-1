from dataclasses import dataclass

@dataclass
class ExecutionResult:
    attempted: bool
    success: bool
    order_id: str | None
    filled_size: float
    filled_price: float
    mode: str
    error: str | None = None
