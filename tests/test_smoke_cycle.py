"""Smoke test: run a single cycle end-to-end."""
import os
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_single_cycle_smoke():
    """Run one complete cycle in paper mode and verify outcome."""
    from app.config.profile_manager import ProfileManager
    from app.bootstrap import build_orchestrator
    from app.shared.enums import CycleStatus

    pm = ProfileManager("config")
    config = pm.get_config("paper_test")

    orchestrator = build_orchestrator(config)
    outcome = orchestrator.run_cycle()

    assert outcome.cycle_id is not None
    assert outcome.status == CycleStatus.OK
    assert outcome.markets_scanned >= 0
    assert outcome.error is None

def test_cycle_returns_valid_outcome():
    """Verify CycleOutcome has all required fields."""
    from app.config.profile_manager import ProfileManager
    from app.bootstrap import build_orchestrator

    pm = ProfileManager("config")
    config = pm.get_config("paper_test")

    orchestrator = build_orchestrator(config)
    outcome = orchestrator.run_cycle()

    assert hasattr(outcome, "cycle_id")
    assert hasattr(outcome, "status")
    assert hasattr(outcome, "started_at")
    assert hasattr(outcome, "finished_at")
    assert hasattr(outcome, "markets_scanned")
    assert hasattr(outcome, "signals_generated")
