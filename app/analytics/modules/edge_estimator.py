from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput, AnalyticsSignal
from app.state.state_schema import CycleState
from app.shared.ids import new_signal_id

class EdgeEstimatorModule(BaseAnalyticsModule):
    name = "edge_estimator"

    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        signals = []
        min_edge = config.get("analytics", {}).get("edge_estimator", {}).get("min_edge", 0.03)

        for market in state.market_data.markets:
            yes_price = market.get("yes_price", 0.5)
            no_price = market.get("no_price", 0.5)

            # Simple edge: distance from 0.5 probability
            yes_edge = abs(yes_price - 0.5)
            no_edge = abs(no_price - 0.5)

            best_edge = max(yes_edge, no_edge)
            best_side = "yes" if yes_edge > no_edge else "no"

            if best_edge >= min_edge:
                signals.append(AnalyticsSignal(
                    signal_id=new_signal_id(),
                    market_id=market["id"],
                    module=self.name,
                    score=best_edge,
                    side=best_side,
                    confidence=min(best_edge * 3, 1.0),
                    metadata={"yes_price": yes_price, "no_price": no_price, "edge": best_edge},
                ))

        return ModuleOutput(module_name=self.name, success=True, signals=signals)
