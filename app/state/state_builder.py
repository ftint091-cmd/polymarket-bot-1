from app.state.state_schema import CycleState, MarketData
from app.shared.ids import new_cycle_id
from typing import Any

class StateBuilder:
    """Builds the initial CycleState from raw market data."""

    def build(self, market_data: dict[str, Any]) -> CycleState:
        state = CycleState(cycle_id=new_cycle_id())
        state.market_data = MarketData(
            markets=market_data.get("markets", []),
            binance_context=market_data.get("binance_context", {}),
            markets_count=market_data.get("markets_count", 0),
        )
        return state
