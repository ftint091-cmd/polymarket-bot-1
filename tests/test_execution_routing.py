"""Tests for execution mode routing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def _make_state_with_trade(market_id="test_market"):
    from app.state.state_schema import CycleState, MarketData, DecisionOutput, SizingOutput, CapitalRiskOutput
    state = CycleState(cycle_id="test_cycle")
    state.market_data = MarketData(
        markets=[{
            "id": market_id,
            "yes_price": 0.4,
            "no_price": 0.6,
            "volume": 5000,
            "active": True,
            "orderbook": {"best_ask": 0.42, "best_bid": 0.38, "spread": 0.04, "bids": [], "asks": []}
        }],
        markets_count=1,
    )
    state.decision = DecisionOutput(
        should_trade=True,
        signal_id="sig_test",
        market_id=market_id,
        side="yes",
        confidence=0.8,
    )
    state.sizing = SizingOutput(recommended_size=10.0, raw_size=10.0)
    state.capital_risk = CapitalRiskOutput(
        approved=True, approved_size=10.0, capital_available=10000.0
    )
    return state

def test_paper_executor_returns_success():
    from app.execution.paper_executor import PaperExecutor
    state = _make_state_with_trade()
    executor = PaperExecutor()
    result = executor.execute(state, {})
    assert result.success is True
    assert result.mode == "paper"
    assert result.filled_size > 0

def test_fake_real_executor_returns_success():
    from app.execution.fake_real_executor import FakeRealExecutor
    state = _make_state_with_trade()
    executor = FakeRealExecutor()
    result = executor.execute(state, {})
    assert result.success is True
    assert result.mode == "fake_real"

def test_executor_routes_to_paper():
    from app.execution.executor import Executor
    state = _make_state_with_trade()
    executor = Executor(mode="paper")
    state_execution = executor.execute(state, {})
    assert state_execution.mode == "paper"

def test_executor_routes_to_fake_real():
    from app.execution.executor import Executor
    state = _make_state_with_trade()
    executor = Executor(mode="fake_real")
    state_execution = executor.execute(state, {})
    assert state_execution.mode == "fake_real"

def test_real_executor_requires_env_flag():
    import os
    import pytest
    os.environ.pop("ENABLE_REAL_TRADING", None)
    from app.execution.real_executor import RealExecutor
    from app.shared.exceptions import ExecutionError
    with pytest.raises(ExecutionError):
        RealExecutor(execution_client=None, secrets_provider=None)
