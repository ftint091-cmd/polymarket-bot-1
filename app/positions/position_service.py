import logging
from app.positions.position_store import PositionStore
from app.positions.position_model import Position
from app.execution.execution_schema import ExecutionResult
from app.state.state_schema import CycleState, DecisionOutput
from app.shared.ids import new_position_id
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger(__name__)

class PositionService:
    def __init__(self, store: PositionStore):
        self._store = store

    def update_from_execution(self, decision: DecisionOutput, execution: ExecutionResult) -> None:
        if not execution.success or not execution.attempted:
            return
        if execution.filled_size <= 0:
            return

        position = Position(
            position_id=new_position_id(),
            market_id=decision.market_id or "",
            side=decision.side or "",
            size=execution.filled_size,
            entry_price=execution.filled_price,
            current_price=execution.filled_price,
            opened_at=utcnow_iso(),
            order_id=execution.order_id,
        )

        self._store.add(position)
        logger.info("Position opened: %s market=%s side=%s size=%.2f",
                    position.position_id, position.market_id, position.side, position.size)

    def get_positions_snapshot(self) -> list[dict]:
        import dataclasses
        return [dataclasses.asdict(p) for p in self._store.get_all()]

    def get_total_exposure(self) -> float:
        return self._store.get_total_exposure()
