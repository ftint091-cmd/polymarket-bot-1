from app.shared.enums import CommandType, LifecycleState
from app.shared.exceptions import InvalidCommandError

# Map of allowed commands per lifecycle state
ALLOWED_COMMANDS: dict[LifecycleState, set[CommandType]] = {
    LifecycleState.IDLE: {
        CommandType.START,
        CommandType.STATUS,
        CommandType.SET_PROFILE,
        CommandType.RELOAD_CONFIG,
    },
    LifecycleState.RUNNING: {
        CommandType.STOP,
        CommandType.PAUSE,
        CommandType.STATUS,
        CommandType.EMERGENCY_STOP,
        CommandType.SET_PROFILE,
        CommandType.RELOAD_CONFIG,
    },
    LifecycleState.PAUSED: {
        CommandType.RESUME,
        CommandType.STOP,
        CommandType.STATUS,
        CommandType.EMERGENCY_STOP,
        CommandType.SET_PROFILE,
        CommandType.RELOAD_CONFIG,
    },
    LifecycleState.FAULT: {
        CommandType.STOP,
        CommandType.STATUS,
        CommandType.EMERGENCY_STOP,
        CommandType.RELOAD_CONFIG,
    },
    LifecycleState.STOPPED: {
        CommandType.START,
        CommandType.STATUS,
        CommandType.SET_PROFILE,
        CommandType.RELOAD_CONFIG,
    },
}

def validate_command(command_type: CommandType, current_state: LifecycleState) -> None:
    allowed = ALLOWED_COMMANDS.get(current_state, set())
    if command_type not in allowed:
        raise InvalidCommandError(
            f"Command {command_type} is not allowed in state {current_state}. "
            f"Allowed: {[c.value for c in allowed]}"
        )
