import logging
from typing import Any
from app.infrastructure.transport.http_session import HttpSession
from app.shared.exceptions import MarketDataError

logger = logging.getLogger(__name__)

BINANCE_API_BASE = "https://api.binance.com/api/v3"

class BinanceMarketClient:
    """Fetches reference market data from Binance. Falls back to mock data."""

    def __init__(self, session: HttpSession | None = None, use_mock: bool = True):
        self._session = session or HttpSession(base_url=BINANCE_API_BASE)
        self._use_mock = use_mock

    def get_ticker(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        if self._use_mock:
            return self._mock_ticker(symbol)
        try:
            return self._session.get("/ticker/24hr", {"symbol": symbol})
        except Exception as e:
            logger.warning("Binance API unavailable, using mock: %s", e)
            return self._mock_ticker(symbol)

    def _mock_ticker(self, symbol: str) -> dict[str, Any]:
        return {
            "symbol": symbol,
            "lastPrice": "45000.00",
            "priceChangePercent": "-1.50",
            "volume": "12345.67",
            "highPrice": "46000.00",
            "lowPrice": "44000.00",
        }
