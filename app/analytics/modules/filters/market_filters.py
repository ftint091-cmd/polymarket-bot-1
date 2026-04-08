from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput
from app.state.state_schema import CycleState

class MarketFiltersModule(BaseAnalyticsModule):
    name = "market_filters"

    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        min_volume = config.get("filters", {}).get("min_volume", 1000)
        active_markets = [m for m in state.market_data.markets if m.get("active", True) and m.get("volume", 0) >= min_volume]
        return ModuleOutput(
            module_name=self.name,
            success=True,
            data={"active_markets": len(active_markets), "total_markets": len(state.market_data.markets)}
        )
