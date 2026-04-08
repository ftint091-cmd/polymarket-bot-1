import json
import logging
from pathlib import Path
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger("cycle")

class CycleLogger:
    def __init__(self, log_dir: str = "logs/cycle"):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, cycle_id: str, data: dict) -> None:
        filename = self._log_dir / f"{cycle_id}.json"
        try:
            with open(filename, "w") as f:
                json.dump({"cycle_id": cycle_id, "timestamp": utcnow_iso(), **data}, f, indent=2, default=str)
        except Exception as e:
            logger.warning("Failed to write cycle log: %s", e)
        logger.info("CYCLE %s: status=%s trades=%s", cycle_id, data.get("status"), data.get("trades_executed"))
