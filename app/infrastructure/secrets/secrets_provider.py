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
        """Return True only when BOTH execution mode is 'real' AND safety flag is set.

        Safety flag: ENABLE_REAL_TRADING=true (primary) or
                     REAL_TRADING_ENABLED=true (legacy alias).
        Both checks are case-insensitive.
        """
        execution_mode = os.environ.get("BOT_EXECUTION_MODE", "").strip().lower()
        if execution_mode != "real":
            return False
        primary = os.environ.get("ENABLE_REAL_TRADING", "").strip().lower()
        legacy = os.environ.get("REAL_TRADING_ENABLED", "").strip().lower()
        return primary == "true" or legacy == "true"
