import logging
from app.execution.execution_schema import ExecutionResult
from app.execution.paper_executor import PaperExecutor
from app.state.state_schema import CycleState

logger = logging.getLogger(__name__)

class FakeRealExecutor:
    """Like paper executor but logs as if real, for integration testing."""

    mode = "fake_real"

    def __init__(self):
        self._paper = PaperExecutor()

    def execute(self, state: CycleState, config: dict) -> ExecutionResult:
        result = self._paper.execute(state, config)
        result.mode = self.mode
        logger.info("[FAKE_REAL] Simulated real execution: order_id=%s size=%.2f",
                    result.order_id, result.filled_size)
        return result
