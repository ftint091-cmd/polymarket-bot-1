import json
import logging
from pathlib import Path
from app.state.state_schema import CycleState
from app.shared.time_utils import utcnow_iso
import dataclasses

logger = logging.getLogger(__name__)

def save_snapshot(state: CycleState, snapshot_dir: str = "data/state_snapshots") -> None:
    path = Path(snapshot_dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = path / f"{state.cycle_id}_{utcnow_iso().replace(':', '-')}.json"
    try:
        with open(filename, "w") as f:
            json.dump(dataclasses.asdict(state), f, indent=2, default=str)
        logger.debug("State snapshot saved: %s", filename)
    except Exception as e:
        logger.warning("Failed to save snapshot: %s", e)
