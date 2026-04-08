import logging
from typing import Any
from app.infrastructure.secrets.secrets_provider import SecretsProvider

logger = logging.getLogger(__name__)

class WalletClient:
    """Fetches wallet/capital information. Uses mock in paper mode."""

    def __init__(self, secrets: SecretsProvider, use_mock: bool = True):
        self._secrets = secrets
        self._use_mock = use_mock

    def get_balance(self) -> dict[str, Any]:
        if self._use_mock:
            return {"usdc": 10000.0, "currency": "USDC", "mock": True}
        # Real implementation would call contract/API
        return {"usdc": 0.0, "currency": "USDC", "mock": False}
