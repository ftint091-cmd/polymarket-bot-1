from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput, AnalyticsSignal
from app.state.state_schema import CycleState
from app.shared.ids import new_signal_id

class BookImbalanceModule(BaseAnalyticsModule):
    name = "book_imbalance"

    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        signals = []
        imbalance_threshold = config.get("analytics", {}).get("book_imbalance", {}).get("threshold", 0.6)

        for market in state.market_data.markets:
            ob = market.get("orderbook")
            if not ob:
                continue
            bids = ob.get("bids", [])
            asks = ob.get("asks", [])

            total_bid = sum(b.get("size", 0) for b in bids)
            total_ask = sum(a.get("size", 0) for a in asks)
            total = total_bid + total_ask

            if total == 0:
                continue

            imbalance = total_bid / total

            if imbalance > imbalance_threshold:
                signals.append(AnalyticsSignal(
                    signal_id=new_signal_id(),
                    market_id=market["id"],
                    module=self.name,
                    score=imbalance,
                    side="yes",
                    confidence=imbalance,
                    metadata={"imbalance": imbalance, "total_bid": total_bid, "total_ask": total_ask},
                ))
            elif imbalance < (1 - imbalance_threshold):
                signals.append(AnalyticsSignal(
                    signal_id=new_signal_id(),
                    market_id=market["id"],
                    module=self.name,
                    score=1 - imbalance,
                    side="no",
                    confidence=1 - imbalance,
                    metadata={"imbalance": imbalance},
                ))

        return ModuleOutput(module_name=self.name, success=True, signals=signals)
