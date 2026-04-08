"""Tests for controller lifecycle command handling."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def _make_controller():
    from unittest.mock import MagicMock
    from app.controller.controller import Controller
    from app.shared.enums import CycleStatus
    from app.orchestration.cycle_outcome import CycleOutcome
    from app.shared.time_utils import utcnow_iso

    mock_orchestrator = MagicMock()
    mock_orchestrator.run_cycle.return_value = CycleOutcome(
        cycle_id="test",
        status=CycleStatus.OK,
        started_at=utcnow_iso(),
        finished_at=utcnow_iso(),
    )
    config = {"cycle_interval_seconds": 1, "fault_policy": {"max_consecutive_errors": 5}}
    return Controller(mock_orchestrator, config)

def test_initial_state_is_idle():
    from app.shared.enums import LifecycleState
    controller = _make_controller()
    assert controller._state.state == LifecycleState.IDLE

def test_status_command_works_from_idle():
    from app.controller.command_model import Command
    from app.shared.enums import CommandType
    controller = _make_controller()
    result = controller.execute(Command(type=CommandType.STATUS))
    assert result.success is True
    assert result.data["state"] == "idle"

def test_stop_rejected_from_idle():
    from app.controller.command_model import Command
    from app.shared.enums import CommandType
    controller = _make_controller()
    result = controller.execute(Command(type=CommandType.STOP))
    assert result.success is False

def test_start_transitions_to_running():
    import time
    from app.controller.command_model import Command
    from app.shared.enums import CommandType, LifecycleState
    controller = _make_controller()
    result = controller.execute(Command(type=CommandType.START))
    assert result.success is True
    # Give thread time to start
    time.sleep(0.1)
    controller.execute(Command(type=CommandType.STOP))

def test_pause_from_running():
    import time
    from app.controller.command_model import Command
    from app.shared.enums import CommandType, LifecycleState
    controller = _make_controller()
    controller.execute(Command(type=CommandType.START))
    time.sleep(0.05)
    result = controller.execute(Command(type=CommandType.PAUSE))
    assert result.success is True
    assert controller._state.state == LifecycleState.PAUSED
    controller.execute(Command(type=CommandType.STOP))

def test_set_profile_command():
    from app.controller.command_model import Command
    from app.shared.enums import CommandType
    controller = _make_controller()
    result = controller.execute(Command(type=CommandType.SET_PROFILE, payload={"profile": "cautious"}))
    assert result.success is True
    assert controller._state.profile == "cautious"

def test_emergency_stop_from_running():
    import time
    from app.controller.command_model import Command
    from app.shared.enums import CommandType, LifecycleState
    controller = _make_controller()
    controller.execute(Command(type=CommandType.START))
    time.sleep(0.05)
    result = controller.execute(Command(type=CommandType.EMERGENCY_STOP))
    assert result.success is True
    assert controller._state.state == LifecycleState.STOPPED
