from typing import Any
from app.infrastructure.api.binance_market_client import BinanceMarketClient

class BinanceAdapter:
    """Normalizes Binance market data into internal format."""

    def __init__(self, client: BinanceMarketClient):
        self._client = client

    def get_reference_ticker(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        raw = self._client.get_ticker(symbol)
        return {
            "symbol": raw.get("symbol", symbol),
            "price": float(raw.get("lastPrice", 0)),
            "change_pct": float(raw.get("priceChangePercent", 0)),
            "volume": float(raw.get("volume", 0)),
        }
