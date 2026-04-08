import logging
import threading
import time
from app.controller.command_model import Command, CommandResult
from app.controller.command_handler import validate_command
from app.controller.lifecycle_state import LifecycleStateModel
from app.controller.fault_policy import FaultPolicy
from app.shared.enums import CommandType, LifecycleState
from app.shared.exceptions import InvalidCommandError
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, orchestrator, config):
        self._orchestrator = orchestrator
        self._config = config
        self._state = LifecycleStateModel()
        self._fault_policy = FaultPolicy(
            max_consecutive_errors=config.get("fault_policy", {}).get("max_consecutive_errors", 5)
        )
        self._lock = threading.Lock()
        self._run_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def execute(self, command: Command) -> CommandResult:
        with self._lock:
            try:
                validate_command(command.type, self._state.state)
            except InvalidCommandError as e:
                return CommandResult(success=False, message=str(e))

            return self._dispatch(command)

    def _dispatch(self, command: Command) -> CommandResult:
        handlers = {
            CommandType.START: self._cmd_start,
            CommandType.STOP: self._cmd_stop,
            CommandType.PAUSE: self._cmd_pause,
            CommandType.RESUME: self._cmd_resume,
            CommandType.STATUS: self._cmd_status,
            CommandType.SET_PROFILE: self._cmd_set_profile,
            CommandType.RELOAD_CONFIG: self._cmd_reload_config,
            CommandType.EMERGENCY_STOP: self._cmd_emergency_stop,
        }
        handler = handlers.get(command.type)
        if handler is None:
            return CommandResult(success=False, message=f"Unknown command: {command.type}")
        return handler(command)

    def _cmd_start(self, command: Command) -> CommandResult:
        self._state.state = LifecycleState.RUNNING
        self._state.started_at = utcnow_iso()
        self._stop_event.clear()
        self._run_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._run_thread.start()
        logger.info("Controller started, profile=%s", self._state.profile)
        return CommandResult(success=True, message="Started")

    def _cmd_stop(self, command: Command) -> CommandResult:
        self._state.state = LifecycleState.STOPPED
        self._state.stopped_at = utcnow_iso()
        self._stop_event.set()
        logger.info("Controller stopped")
        return CommandResult(success=True, message="Stopped")

    def _cmd_pause(self, command: Command) -> CommandResult:
        self._state.state = LifecycleState.PAUSED
        logger.info("Controller paused")
        return CommandResult(success=True, message="Paused")

    def _cmd_resume(self, command: Command) -> CommandResult:
        self._state.state = LifecycleState.RUNNING
        logger.info("Controller resumed")
        return CommandResult(success=True, message="Resumed")

    def _cmd_status(self, command: Command) -> CommandResult:
        return CommandResult(
            success=True,
            message="OK",
            data={
                "state": self._state.state.value,
                "profile": self._state.profile,
                "cycle_count": self._state.cycle_count,
                "error_count": self._state.error_count,
                "started_at": self._state.started_at,
            },
        )

    def _cmd_set_profile(self, command: Command) -> CommandResult:
        profile = (command.payload or {}).get("profile", "default")
        self._state.profile = profile
        logger.info("Profile set to %s", profile)
        return CommandResult(success=True, message=f"Profile set to {profile}")

    def _cmd_reload_config(self, command: Command) -> CommandResult:
        logger.info("Config reload requested")
        return CommandResult(success=True, message="Config reloaded")

    def _cmd_emergency_stop(self, command: Command) -> CommandResult:
        self._state.state = LifecycleState.STOPPED
        self._state.stopped_at = utcnow_iso()
        self._stop_event.set()
        logger.warning("EMERGENCY STOP executed")
        return CommandResult(success=True, message="Emergency stop executed")

    def _run_loop(self) -> None:
        cycle_interval = self._config.get("cycle_interval_seconds", 60)
        while not self._stop_event.is_set():
            if self._state.state == LifecycleState.PAUSED:
                time.sleep(1)
                continue
            if self._state.state != LifecycleState.RUNNING:
                break
            try:
                outcome = self._orchestrator.run_cycle()
                self._state.cycle_count += 1
                self._fault_policy.record_success()
                logger.info("Cycle %d completed: %s", self._state.cycle_count, outcome.status)
            except Exception as e:
                self._state.error_count += 1
                should_fault = self._fault_policy.record_error()
                logger.error("Cycle error: %s", e, exc_info=True)
                if should_fault:
                    self._state.state = LifecycleState.FAULT
                    self._state.fault_reason = str(e)
                    logger.critical("Escalated to FAULT state after %d consecutive errors", self._fault_policy.consecutive_errors)
                    break
            self._stop_event.wait(timeout=cycle_interval)
