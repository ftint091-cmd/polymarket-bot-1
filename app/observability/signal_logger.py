import json
import logging
from pathlib import Path
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger("signal")

class SignalLogger:
    def __init__(self, log_dir: str = "logs/signal"):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, cycle_id: str, signals: list) -> None:
        if not signals:
            return
        filename = self._log_dir / f"{cycle_id}_signals.json"
        try:
            with open(filename, "w") as f:
                json.dump({"cycle_id": cycle_id, "timestamp": utcnow_iso(), "signals": signals}, f, indent=2, default=str)
        except Exception as e:
            logger.warning("Failed to write signal log: %s", e)
        logger.info("SIGNALS cycle=%s count=%d", cycle_id, len(signals))
