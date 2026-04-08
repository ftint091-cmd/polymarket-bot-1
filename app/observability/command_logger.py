import json
import logging
from pathlib import Path
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger("command")

class CommandLogger:
    def __init__(self, log_dir: str = "logs/command"):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, command_type: str, result: dict) -> None:
        filename = self._log_dir / f"commands.jsonl"
        try:
            with open(filename, "a") as f:
                f.write(json.dumps({"timestamp": utcnow_iso(), "command": command_type, **result}, default=str) + "\n")
        except Exception as e:
            logger.warning("Failed to write command log: %s", e)
        logger.info("COMMAND %s: success=%s", command_type, result.get("success"))
