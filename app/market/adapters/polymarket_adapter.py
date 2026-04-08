from typing import Any
from app.infrastructure.api.polymarket_market_client import PolymarketMarketClient

class PolymarketAdapter:
    """Normalizes Polymarket API data into internal format."""

    def __init__(self, client: PolymarketMarketClient):
        self._client = client

    def get_markets(self, limit: int = 10) -> list[dict[str, Any]]:
        raw = self._client.get_markets(limit)
        return [self._normalize_market(m) for m in raw]

    def get_orderbook(self, market_id: str) -> dict[str, Any]:
        return self._client.get_orderbook(market_id)

    def _normalize_market(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": raw.get("id", ""),
            "question": raw.get("question", ""),
            "yes_price": float(raw.get("yes_price", 0)),
            "no_price": float(raw.get("no_price", 0)),
            "volume": float(raw.get("volume", 0)),
            "active": bool(raw.get("active", True)),
        }
