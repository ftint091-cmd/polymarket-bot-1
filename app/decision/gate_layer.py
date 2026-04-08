from app.state.state_schema import CycleState, AnalyticsOutput

class GateLayer:
    """Binary gate: pass/reject based on minimum signal count and confidence."""

    def check(self, analytics: AnalyticsOutput, config: dict) -> tuple[bool, str]:
        min_signals = config.get("decision", {}).get("gate", {}).get("min_signals", 1)
        min_confidence = config.get("decision", {}).get("gate", {}).get("min_confidence", 0.3)

        signals = analytics.signals
        if not signals:
            return False, "No signals generated"

        strong_signals = [s for s in signals if s.get("confidence", 0) >= min_confidence]
        if len(strong_signals) < min_signals:
            return False, f"Insufficient strong signals: {len(strong_signals)}/{min_signals}"

        return True, "Gate passed"
