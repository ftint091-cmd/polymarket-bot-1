from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput, AnalyticsSignal
from app.state.state_schema import CycleState
from app.shared.ids import new_signal_id

class SpreadPressureModule(BaseAnalyticsModule):
    name = "spread_pressure"

    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        signals = []
        min_spread = config.get("analytics", {}).get("spread_pressure", {}).get("min_spread", 0.01)
        max_spread = config.get("analytics", {}).get("spread_pressure", {}).get("max_spread", 0.10)

        for market in state.market_data.markets:
            ob = market.get("orderbook")
            if not ob:
                continue
            spread = ob.get("spread", 0)
            if spread < min_spread or spread > max_spread:
                continue
            # Simple edge: if spread is tight, there's pressure
            score = max(0, 1 - spread / max_spread)
            if score > 0.3:
                signals.append(AnalyticsSignal(
                    signal_id=new_signal_id(),
                    market_id=market["id"],
                    module=self.name,
                    score=score,
                    side="yes" if market.get("yes_price", 0.5) < 0.5 else "no",
                    confidence=score,
                    metadata={"spread": spread},
                ))

        return ModuleOutput(module_name=self.name, success=True, signals=signals)
