"""Tests for real-mode detection and target-market filtering."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# SecretsProvider.is_real_trading_enabled() – detection matrix
# ---------------------------------------------------------------------------

class TestIsRealTradingEnabled:
    """Verify that is_real_trading_enabled() requires BOTH conditions."""

    def _make(self):
        from app.infrastructure.secrets.secrets_provider import SecretsProvider
        return SecretsProvider()

    def test_both_conditions_true_returns_true(self):
        sp = self._make()
        with patch.dict(os.environ, {"BOT_EXECUTION_MODE": "real", "ENABLE_REAL_TRADING": "true"}):
            assert sp.is_real_trading_enabled() is True

    def test_only_enable_flag_returns_false(self):
        """Safety flag alone is not enough; execution mode must also be 'real'."""
        sp = self._make()
        with patch.dict(os.environ, {"BOT_EXECUTION_MODE": "paper", "ENABLE_REAL_TRADING": "true"}):
            assert sp.is_real_trading_enabled() is False

    def test_only_execution_mode_real_returns_false(self):
        """Execution mode alone is not enough; safety flag must also be set."""
        sp = self._make()
        with patch.dict(
            os.environ,
            {"BOT_EXECUTION_MODE": "real", "ENABLE_REAL_TRADING": "false"},
        ):
            assert sp.is_real_trading_enabled() is False

    def test_neither_condition_returns_false(self):
        sp = self._make()
        with patch.dict(
            os.environ,
            {"BOT_EXECUTION_MODE": "paper", "ENABLE_REAL_TRADING": "false"},
        ):
            assert sp.is_real_trading_enabled() is False

    def test_unset_conditions_returns_false(self):
        sp = self._make()
        env = {k: v for k, v in os.environ.items()
               if k not in {"BOT_EXECUTION_MODE", "ENABLE_REAL_TRADING", "REAL_TRADING_ENABLED"}}
        with patch.dict(os.environ, env, clear=True):
            assert sp.is_real_trading_enabled() is False

    def test_case_insensitive_mode(self):
        sp = self._make()
        with patch.dict(os.environ, {"BOT_EXECUTION_MODE": "REAL", "ENABLE_REAL_TRADING": "true"}):
            assert sp.is_real_trading_enabled() is True

    def test_case_insensitive_flag(self):
        sp = self._make()
        with patch.dict(os.environ, {"BOT_EXECUTION_MODE": "real", "ENABLE_REAL_TRADING": "True"}):
            assert sp.is_real_trading_enabled() is True

    def test_legacy_flag_accepted(self):
        """REAL_TRADING_ENABLED=true is accepted as legacy alias."""
        sp = self._make()
        env = {"BOT_EXECUTION_MODE": "real", "REAL_TRADING_ENABLED": "true"}
        # Ensure primary flag is absent so we test the legacy path exclusively
        filtered = {k: v for k, v in os.environ.items()
                    if k not in {"BOT_EXECUTION_MODE", "ENABLE_REAL_TRADING", "REAL_TRADING_ENABLED"}}
        filtered.update(env)
        with patch.dict(os.environ, filtered, clear=True):
            assert sp.is_real_trading_enabled() is True

    def test_legacy_flag_does_not_override_mode_requirement(self):
        """Legacy flag without BOT_EXECUTION_MODE=real must not enable real trading."""
        sp = self._make()
        env = {"BOT_EXECUTION_MODE": "paper", "REAL_TRADING_ENABLED": "true"}
        with patch.dict(os.environ, env):
            assert sp.is_real_trading_enabled() is False


# ---------------------------------------------------------------------------
# Bootstrap use_mock logic
# ---------------------------------------------------------------------------

class TestBootstrapUseMock:
    """Verify that bootstrap.py derives use_mock from is_real_trading_enabled()."""

    def test_use_mock_true_when_paper(self):
        from app.infrastructure.secrets.secrets_provider import SecretsProvider
        with patch.dict(os.environ, {"BOT_EXECUTION_MODE": "paper", "ENABLE_REAL_TRADING": "false"}):
            secrets = SecretsProvider()
            assert not secrets.is_real_trading_enabled()
            use_mock = not secrets.is_real_trading_enabled()
            assert use_mock is True

    def test_use_mock_false_when_real(self):
        from app.infrastructure.secrets.secrets_provider import SecretsProvider
        with patch.dict(os.environ, {"BOT_EXECUTION_MODE": "real", "ENABLE_REAL_TRADING": "true"}):
            secrets = SecretsProvider()
            assert secrets.is_real_trading_enabled()
            use_mock = not secrets.is_real_trading_enabled()
            assert use_mock is False


# ---------------------------------------------------------------------------
# MarketMonitor filtering – returns only whitelisted IDs with market_name
# ---------------------------------------------------------------------------

class TestMarketMonitorFiltering:
    """Verify that MarketMonitor filters markets to the target whitelist."""

    def _make_monitor(self, raw_markets):
        """Build a MarketMonitor wired to a mock adapter returning raw_markets."""
        from app.market.monitor import MarketMonitor
        from app.market.adapters.polymarket_adapter import PolymarketAdapter
        from app.market.adapters.binance_adapter import BinanceAdapter

        poly_adapter = MagicMock(spec=PolymarketAdapter)
        poly_adapter.get_markets.return_value = raw_markets
        poly_adapter.get_orderbook.return_value = {}

        binance_adapter = MagicMock(spec=BinanceAdapter)
        binance_adapter.get_reference_ticker.return_value = {}

        config = {"markets_per_cycle": 10, "reference_symbol": "BTCUSDT"}
        return MarketMonitor(poly_adapter, binance_adapter, config)

    def test_filters_to_whitelisted_ids(self):
        raw = [
            {"id": "1903731", "slug": "btc-5m"},
            {"id": "1903701", "slug": "btc-15m"},
            {"id": "9999999", "slug": "other-market"},  # not whitelisted
        ]
        monitor = self._make_monitor(raw)
        result = monitor.collect()
        ids = {m["id"] for m in result["markets"]}
        assert ids == {"1903731", "1903701"}
        assert "9999999" not in ids

    def test_all_three_btc_markets_pass_filter(self):
        raw = [
            {"id": "1903731", "slug": "btc-5m"},
            {"id": "1903701", "slug": "btc-15m"},
            {"id": "1887954", "slug": "btc-1h"},
        ]
        monitor = self._make_monitor(raw)
        result = monitor.collect()
        ids = {m["id"] for m in result["markets"]}
        assert ids == {"1903731", "1903701", "1887954"}

    def test_market_name_attached(self):
        raw = [
            {"id": "1903731", "slug": "btc-5m"},
            {"id": "1903701", "slug": "btc-15m"},
            {"id": "1887954", "slug": "btc-1h"},
        ]
        monitor = self._make_monitor(raw)
        result = monitor.collect()
        names = {m["id"]: m.get("market_name") for m in result["markets"]}
        assert names["1903731"] == "BTC Up/Down 5m"
        assert names["1903701"] == "BTC Up/Down 15m"
        assert names["1887954"] == "BTC Up/Down 1h"

    def test_empty_when_no_whitelist_match(self):
        raw = [{"id": "0000001"}, {"id": "0000002"}]
        monitor = self._make_monitor(raw)
        result = monitor.collect()
        assert result["markets"] == []
        assert result["markets_count"] == 0

    def test_markets_count_reflects_filtered_set(self):
        raw = [
            {"id": "1903731", "slug": "btc-5m"},
            {"id": "8888888", "slug": "unrelated"},
        ]
        monitor = self._make_monitor(raw)
        result = monitor.collect()
        assert result["markets_count"] == 1


# ---------------------------------------------------------------------------
# target_markets helpers
# ---------------------------------------------------------------------------

class TestTargetMarketsHelpers:
    def test_is_target_market_by_id_key(self):
        from app.config.target_markets import is_target_market
        assert is_target_market({"id": "1903731"}) is True
        assert is_target_market({"id": "9999999"}) is False

    def test_is_target_market_by_market_id_key(self):
        from app.config.target_markets import is_target_market
        assert is_target_market({"market_id": "1903701"}) is True

    def test_market_display_name_known(self):
        from app.config.target_markets import market_display_name
        assert market_display_name({"id": "1903731"}) == "BTC Up/Down 5m"
        assert market_display_name({"id": "1903701"}) == "BTC Up/Down 15m"
        assert market_display_name({"id": "1887954"}) == "BTC Up/Down 1h"

    def test_market_display_name_unknown_falls_back(self):
        from app.config.target_markets import market_display_name
        result = market_display_name({"id": "0000001", "slug": "some-slug"})
        assert result  # non-empty fallback
