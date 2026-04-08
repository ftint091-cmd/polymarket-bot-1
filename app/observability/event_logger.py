import json
import logging
from pathlib import Path
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger("event")

class EventLogger:
    def __init__(self, log_dir: str = "logs/events"):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, event_type: str, data: dict) -> None:
        filename = self._log_dir / f"events.jsonl"
        try:
            with open(filename, "a") as f:
                f.write(json.dumps({"timestamp": utcnow_iso(), "event": event_type, **data}, default=str) + "\n")
        except Exception as e:
            logger.warning("Failed to write event log: %s", e)
        logger.debug("EVENT %s", event_type)
