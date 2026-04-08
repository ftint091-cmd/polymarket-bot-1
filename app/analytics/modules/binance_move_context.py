from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput
from app.state.state_schema import CycleState

class BinanceMoveContextModule(BaseAnalyticsModule):
    name = "binance_move_context"

    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        ctx = state.market_data.binance_context
        change_pct = ctx.get("change_pct", 0.0)

        return ModuleOutput(
            module_name=self.name,
            success=True,
            signals=[],
            data={
                "symbol": ctx.get("symbol", ""),
                "price": ctx.get("price", 0),
                "change_pct": change_pct,
                "high_volatility": abs(change_pct) > 3.0,
            }
        )
