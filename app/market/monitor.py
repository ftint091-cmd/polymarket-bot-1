from app.config.target_markets import is_target_market, market_display_name
import logging
from typing import Any
from app.market.adapters.polymarket_adapter import PolymarketAdapter
from app.market.adapters.binance_adapter import BinanceAdapter

logger = logging.getLogger(__name__)

class MarketMonitor:
    """Collects market data from all sources each cycle."""

    def __init__(self, polymarket: PolymarketAdapter, binance: BinanceAdapter, config: dict):
        self._polymarket = polymarket
        self._binance = binance
        self._config = config

    def collect(self) -> dict[str, Any]:
        limit = self._config.get("markets_per_cycle", 5)
        markets = self._polymarket.get_markets(limit)
        markets = [m for m in markets if is_target_market(m)]
        for m in markets:
            m["market_name"] = market_display_name(m)

        # Enrich with orderbook data
        for market in markets:
            try:
                market["orderbook"] = self._polymarket.get_orderbook(market["id"])
            except Exception as e:
                logger.warning("Failed to get orderbook for %s: %s", market["id"], e)
                market["orderbook"] = None

        # Reference context from Binance
        reference_symbol = self._config.get("reference_symbol", "BTCUSDT")
        try:
            binance_ctx = self._binance.get_reference_ticker(reference_symbol)
        except Exception as e:
            logger.warning("Failed to get Binance context: %s", e)
            binance_ctx = {}

        return {
            "markets": markets,
            "binance_context": binance_ctx,
            "markets_count": len(markets),
        }

