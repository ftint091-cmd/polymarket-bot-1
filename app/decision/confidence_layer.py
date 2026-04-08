from typing import Any

class ConfidenceLayer:
    """Aggregates signal confidence into a single decision confidence."""

    def aggregate(self, signals: list[dict[str, Any]], config: dict) -> tuple[str | None, str | None, str | None, float]:
        """Returns (signal_id, market_id, side, confidence)."""
        if not signals:
            return None, None, None, 0.0

        # Pick the signal with highest confidence
        best = max(signals, key=lambda s: s.get("confidence", 0))
        return (
            best.get("signal_id"),
            best.get("market_id"),
            best.get("side"),
            float(best.get("confidence", 0)),
        )
