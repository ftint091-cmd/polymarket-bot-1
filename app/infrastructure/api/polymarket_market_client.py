import logging
from typing import Any
from app.infrastructure.transport.http_session import HttpSession
from app.shared.exceptions import MarketDataError

logger = logging.getLogger(__name__)

POLYMARKET_API_BASE = "https://gamma-api.polymarket.com"

class PolymarketMarketClient:
    """Fetches market data from Polymarket. Falls back to mock data if API unavailable."""

    def __init__(self, session: HttpSession | None = None, use_mock: bool = True):
        self._session = session or HttpSession(base_url=POLYMARKET_API_BASE)
        self._use_mock = use_mock

    def get_markets(self, limit: int = 10) -> list[dict[str, Any]]:
        if self._use_mock:
            return self._mock_markets(limit)
        try:
            return self._session.get("/markets", {"limit": limit})
        except Exception as e:
            logger.warning("Polymarket API unavailable, using mock: %s", e)
            return self._mock_markets(limit)

    def get_orderbook(self, market_id: str) -> dict[str, Any]:
        if self._use_mock:
            return self._mock_orderbook(market_id)
        try:
            return self._session.get(f"/book", {"market": market_id})
        except Exception as e:
            logger.warning("Polymarket orderbook unavailable, using mock: %s", e)
            return self._mock_orderbook(market_id)

    def _mock_markets(self, limit: int) -> list[dict[str, Any]]:
        return [
            {
                "id": f"mock_market_{i}",
                "question": f"Mock Market Question {i}?",
                "yes_price": 0.45 + i * 0.02,
                "no_price": 0.55 - i * 0.02,
                "volume": 10000 + i * 1000,
                "active": True,
            }
            for i in range(min(limit, 5))
        ]

    def _mock_orderbook(self, market_id: str) -> dict[str, Any]:
        return {
            "market": market_id,
            "bids": [{"price": 0.44, "size": 100}, {"price": 0.43, "size": 200}],
            "asks": [{"price": 0.46, "size": 100}, {"price": 0.47, "size": 200}],
            "best_bid": 0.44,
            "best_ask": 0.46,
            "spread": 0.02,
        }
