import logging
from app.execution.execution_schema import ExecutionResult
from app.execution.paper_executor import PaperExecutor
from app.execution.fake_real_executor import FakeRealExecutor
from app.state.state_schema import CycleState, ExecutionOutput
from app.shared.enums import ExecutionMode

logger = logging.getLogger(__name__)

class Executor:
    """Routes execution to the appropriate executor based on mode."""

    def __init__(self, mode: str = "paper", real_executor=None):
        self._mode = ExecutionMode(mode)
        self._paper = PaperExecutor()
        self._fake_real = FakeRealExecutor()
        self._real = real_executor

    def execute(self, state: CycleState, config: dict) -> ExecutionOutput:
        if not state.decision.should_trade:
            state.execution.attempted = False
            state.execution.mode = self._mode.value
            return state.execution

        result: ExecutionResult
        if self._mode == ExecutionMode.PAPER:
            result = self._paper.execute(state, config)
        elif self._mode == ExecutionMode.FAKE_REAL:
            result = self._fake_real.execute(state, config)
        elif self._mode == ExecutionMode.REAL:
            if self._real is None:
                from app.shared.exceptions import ExecutionError
                raise ExecutionError("Real executor not configured")
            result = self._real.execute(state, config)
        else:
            raise ValueError(f"Unknown execution mode: {self._mode}")

        state.execution.attempted = result.attempted
        state.execution.success = result.success
        state.execution.order_id = result.order_id
        state.execution.filled_size = result.filled_size
        state.execution.filled_price = result.filled_price
        state.execution.mode = result.mode
        state.execution.error = result.error

        return state.execution
