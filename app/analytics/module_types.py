from enum import Enum

class ModuleType(str, Enum):
    SPREAD_PRESSURE = "spread_pressure"
    EDGE_ESTIMATOR = "edge_estimator"
    BOOK_IMBALANCE = "book_imbalance"
    BINANCE_MOVE_CONTEXT = "binance_move_context"
    MARKET_FILTER = "market_filter"
    STRATEGY_FILTER = "strategy_filter"
    ADMISSION_FILTER = "admission_filter"
    SYSTEM_FILTER = "system_filter"
