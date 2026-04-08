import json
import logging
from pathlib import Path
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger("execution")

class ExecutionLogger:
    def __init__(self, log_dir: str = "logs/execution"):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, cycle_id: str, execution_data: dict) -> None:
        filename = self._log_dir / f"{cycle_id}_execution.json"
        try:
            with open(filename, "w") as f:
                json.dump({"cycle_id": cycle_id, "timestamp": utcnow_iso(), **execution_data}, f, indent=2, default=str)
        except Exception as e:
            logger.warning("Failed to write execution log: %s", e)
        logger.info("EXECUTION cycle=%s attempted=%s success=%s",
                    cycle_id, execution_data.get("attempted"), execution_data.get("success"))
