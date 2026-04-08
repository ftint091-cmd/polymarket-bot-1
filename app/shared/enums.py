from enum import Enum, auto

class ExecutionMode(str, Enum):
    PAPER = "paper"
    FAKE_REAL = "fake_real"
    REAL = "real"

class LifecycleState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FAULT = "fault"
    STOPPED = "stopped"

class CommandType(str, Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    STATUS = "status"
    SET_PROFILE = "set_profile"
    RELOAD_CONFIG = "reload_config"
    EMERGENCY_STOP = "emergency_stop"

class Side(str, Enum):
    YES = "yes"
    NO = "no"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class SignalStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"

class CycleStatus(str, Enum):
    OK = "ok"
    SKIPPED = "skipped"
    ERROR = "error"
    PAUSED = "paused"
