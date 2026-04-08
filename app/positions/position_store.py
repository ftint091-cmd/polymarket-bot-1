import json
import logging
from pathlib import Path
from app.positions.position_model import Position
from app.shared.time_utils import utcnow_iso
import dataclasses

logger = logging.getLogger(__name__)

class PositionStore:
    """Source of truth for live positions."""

    def __init__(self, store_path: str = "data/positions/positions.json"):
        self._store_path = Path(store_path)
        self._positions: dict[str, Position] = {}
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                with open(self._store_path) as f:
                    data = json.load(f)
                for pos_data in data.get("positions", []):
                    pos = Position(**pos_data)
                    self._positions[pos.position_id] = pos
            except Exception as e:
                logger.warning("Failed to load positions: %s", e)

    def save(self) -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {"positions": [dataclasses.asdict(p) for p in self._positions.values()]}
            with open(self._store_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning("Failed to save positions: %s", e)

    def add(self, position: Position) -> None:
        self._positions[position.position_id] = position
        self.save()

    def get(self, position_id: str) -> Position | None:
        return self._positions.get(position_id)

    def get_all(self) -> list[Position]:
        return list(self._positions.values())

    def get_total_exposure(self) -> float:
        return sum(p.size * p.entry_price for p in self._positions.values())

    def remove(self, position_id: str) -> None:
        self._positions.pop(position_id, None)
        self.save()
