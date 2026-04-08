import logging
from typing import Any
from app.infrastructure.secrets.secrets_provider import SecretsProvider
from app.shared.exceptions import ExecutionError

logger = logging.getLogger(__name__)

class PolymarketExecutionClient:
    """Client for executing orders on Polymarket. Requires explicit real mode activation."""

    def __init__(self, secrets: SecretsProvider, dry_run: bool = True):
        self._secrets = secrets
        self._dry_run = dry_run
        if not dry_run and not secrets.is_real_trading_enabled():
            raise ExecutionError("Real execution requires ENABLE_REAL_TRADING=true")

    def place_order(self, market_id: str, side: str, size: float, price: float) -> dict[str, Any]:
        if self._dry_run:
            logger.info("[DRY RUN] Would place order: market=%s side=%s size=%s price=%s",
                        market_id, side, size, price)
            return {"status": "dry_run", "order_id": "dry_run_order"}
        # Real execution would go here
        raise ExecutionError("Real order placement not implemented in this version")
