import logging
from app.execution.execution_schema import ExecutionResult
from app.state.state_schema import CycleState
from app.shared.ids import new_order_id

logger = logging.getLogger(__name__)

class PaperExecutor:
    """Simulates execution without any real orders."""

    mode = "paper"

    def execute(self, state: CycleState, config: dict) -> ExecutionResult:
        if not state.capital_risk.approved:
            return ExecutionResult(
                attempted=False, success=False, order_id=None,
                filled_size=0.0, filled_price=0.0, mode=self.mode,
                error=state.capital_risk.rejection_reason
            )

        order_id = new_order_id()
        size = state.capital_risk.approved_size

        # Get price from orderbook
        market = next(
            (m for m in state.market_data.markets if m["id"] == state.decision.market_id),
            None
        )
        if market and market.get("orderbook"):
            ob = market["orderbook"]
            price = ob.get("best_ask", 0.5) if state.decision.side == "yes" else ob.get("best_bid", 0.5)
        else:
            if not market:
                logger.warning("[PAPER] Market %s not found in market data, using default price 0.5",
                               state.decision.market_id)
            price = 0.5

        logger.info("[PAPER] Order filled: id=%s market=%s side=%s size=%.2f price=%.4f",
                    order_id, state.decision.market_id, state.decision.side, size, price)

        return ExecutionResult(
            attempted=True, success=True, order_id=order_id,
            filled_size=size, filled_price=price, mode=self.mode
        )
