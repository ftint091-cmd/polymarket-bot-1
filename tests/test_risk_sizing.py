"""Tests for risk and sizing layers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def _make_state(should_trade=True, confidence=0.7):
    from app.state.state_schema import CycleState, DecisionOutput, SizingOutput
    state = CycleState(cycle_id="test")
    state.decision = DecisionOutput(
        should_trade=should_trade,
        market_id="m1",
        side="yes",
        confidence=confidence,
    )
    state.sizing = SizingOutput()
    return state

def test_sizing_respects_base_size():
    from app.sizing.size_recommender import SizeRecommender
    state = _make_state(should_trade=True, confidence=1.0)
    config = {"sizing": {"base_size": 20.0, "min_size": 1.0, "max_size": 500.0}}
    SizeRecommender().recommend(state, config)
    assert state.sizing.recommended_size == 20.0

def test_sizing_applies_max_cap():
    from app.sizing.size_recommender import SizeRecommender
    state = _make_state(should_trade=True, confidence=1.0)
    config = {"sizing": {"base_size": 1000.0, "min_size": 1.0, "max_size": 50.0}}
    SizeRecommender().recommend(state, config)
    assert state.sizing.recommended_size == 50.0
    assert state.sizing.capped is True

def test_risk_can_cut_size():
    from app.sizing.size_recommender import SizeRecommender
    from app.risk.capital_risk_check import CapitalRiskCheck
    state = _make_state(should_trade=True, confidence=1.0)
    config = {
        "sizing": {"base_size": 500.0, "min_size": 1.0, "max_size": 1000.0},
        "risk": {"max_position_pct": 0.01, "max_total_exposure_pct": 0.05, "min_capital_reserve_pct": 0.10},
    }
    SizeRecommender().recommend(state, config)
    CapitalRiskCheck().check(state, capital=1000.0, existing_exposure=0.0, config=config)
    # max_position = 1000 * 0.01 = 10, so approved_size should be <= 10
    assert state.capital_risk.approved_size <= 10.0

def test_risk_rejects_when_no_capital():
    from app.sizing.size_recommender import SizeRecommender
    from app.risk.capital_risk_check import CapitalRiskCheck
    state = _make_state(should_trade=True, confidence=1.0)
    config = {
        "sizing": {"base_size": 100.0, "min_size": 50.0, "max_size": 500.0},
        "risk": {"max_position_pct": 0.001, "max_total_exposure_pct": 0.002, "min_capital_reserve_pct": 0.999},
    }
    SizeRecommender().recommend(state, config)
    CapitalRiskCheck().check(state, capital=100.0, existing_exposure=0.0, config=config)
    assert state.capital_risk.approved is False

def test_no_trade_decision_skips_sizing():
    from app.sizing.size_recommender import SizeRecommender
    state = _make_state(should_trade=False)
    config = {"sizing": {"base_size": 50.0, "min_size": 1.0, "max_size": 500.0}}
    SizeRecommender().recommend(state, config)
    assert state.sizing.recommended_size == 0.0
