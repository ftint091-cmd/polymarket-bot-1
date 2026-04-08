from dataclasses import dataclass
from typing import Any
from app.shared.enums import CommandType

@dataclass
class Command:
    type: CommandType
    payload: dict[str, Any] | None = None

@dataclass
class CommandResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None
