import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger(__name__)

@dataclass
class PerformanceStats:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades

    def record_trade(self, pnl: float) -> None:
        self.total_trades += 1
        self.total_pnl += pnl
        self.realized_pnl += pnl
        if pnl > 0:
            self.winning_trades += 1
        elif pnl < 0:
            self.losing_trades += 1

    def save(self, data_dir: str = "data/performance") -> None:
        path = Path(data_dir)
        path.mkdir(parents=True, exist_ok=True)
        filename = path / "stats.json"
        try:
            data = asdict(self)
            data["win_rate"] = self.win_rate
            data["updated_at"] = utcnow_iso()
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save performance stats: %s", e)
