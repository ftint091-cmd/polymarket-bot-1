import logging
from app.execution.execution_schema import ExecutionResult
from app.state.state_schema import CycleState
from app.shared.exceptions import ExecutionError

logger = logging.getLogger(__name__)

class RealExecutor:
    """Real order execution. Requires ENABLE_REAL_TRADING=true and valid API keys."""

    mode = "real"

    def __init__(self, execution_client, secrets_provider):
        import os
        if os.environ.get("ENABLE_REAL_TRADING", "").lower() != "true":
            raise ExecutionError("RealExecutor requires ENABLE_REAL_TRADING=true")
        self._client = execution_client
        self._secrets = secrets_provider

    def execute(self, state: CycleState, config: dict) -> ExecutionResult:
        if not state.capital_risk.approved:
            return ExecutionResult(
                attempted=False, success=False, order_id=None,
                filled_size=0.0, filled_price=0.0, mode=self.mode,
                error=state.capital_risk.rejection_reason
            )
        logger.warning("[REAL] Real execution not implemented - this is a safety guard")
        raise ExecutionError("Real execution not implemented in this version")
