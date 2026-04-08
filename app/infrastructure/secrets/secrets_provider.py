import os
from app.shared.exceptions import SecretsError

class SecretsProvider:
    """Read secrets from environment variables only. Never hardcode."""

    def get(self, key: str, required: bool = False) -> str | None:
        value = os.environ.get(key)
        if required and not value:
            raise SecretsError(f"Required secret {key} not found in environment")
        return value

    def get_polymarket_api_key(self) -> str | None:
        return self.get("POLYMARKET_API_KEY")

    def get_polymarket_api_secret(self) -> str | None:
        return self.get("POLYMARKET_API_SECRET")

    def get_binance_api_key(self) -> str | None:
        return self.get("BINANCE_API_KEY")

    def get_binance_api_secret(self) -> str | None:
        return self.get("BINANCE_API_SECRET")

    def is_real_trading_enabled(self) -> bool:
        return os.environ.get("ENABLE_REAL_TRADING", "").lower() == "true"
