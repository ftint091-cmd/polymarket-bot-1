import logging
import dataclasses
from app.orchestration.cycle_outcome import CycleOutcome
from app.market.monitor import MarketMonitor
from app.state.state_builder import StateBuilder
from app.state.state_snapshot import save_snapshot
from app.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.decision.aggregate_decision import AggregateDecision
from app.sizing.size_recommender import SizeRecommender
from app.risk.capital_risk_check import CapitalRiskCheck
from app.execution.executor import Executor
from app.positions.position_service import PositionService
from app.observability.cycle_logger import CycleLogger
from app.observability.signal_logger import SignalLogger
from app.observability.execution_logger import ExecutionLogger
from app.observability.performance_stats import PerformanceStats
from app.shared.enums import CycleStatus
from app.shared.ids import new_cycle_id
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(
        self,
        monitor: MarketMonitor,
        state_builder: StateBuilder,
        analytics: AnalyticsOrchestrator,
        decision: AggregateDecision,
        sizer: SizeRecommender,
        risk: CapitalRiskCheck,
        executor: Executor,
        position_service: PositionService,
        config: dict,
    ):
        self._monitor = monitor
        self._state_builder = state_builder
        self._analytics = analytics
        self._decision = decision
        self._sizer = sizer
        self._risk = risk
        self._executor = executor
        self._position_service = position_service
        self._config = config
        self._cycle_logger = CycleLogger()
        self._signal_logger = SignalLogger()
        self._execution_logger = ExecutionLogger()
        self._stats = PerformanceStats()

    def run_cycle(self) -> CycleOutcome:
        started_at = utcnow_iso()
        cycle_id = new_cycle_id()

        try:
            # 1. Market monitor
            market_data = self._monitor.collect()

            # 2. State builder
            state = self._state_builder.build(market_data)
            state.cycle_id = cycle_id

            # 3. Analytics
            state.analytics = self._analytics.run(state, self._config)

            # 4. Decision (writes only state.decision)
            self._decision.decide(state, self._config)

            # 5. Sizing (writes only state.sizing)
            self._sizer.recommend(state, self._config)

            # 6. Capital/Risk (writes only state.capital_risk)
            capital = self._position_service.get_total_exposure()
            wallet_capital = self._config.get("paper_capital", 10000.0)
            existing_exposure = capital
            self._risk.check(state, wallet_capital, existing_exposure, self._config)

            # 7. Execution (writes only state.execution)
            self._executor.execute(state, self._config)

            # 8. Positions
            self._position_service.update_from_execution(
                state.decision,
                _make_execution_result(state),
            )

            # 9. Observability
            self._signal_logger.log(cycle_id, state.analytics.signals)
            self._execution_logger.log(cycle_id, dataclasses.asdict(state.execution))

            trades_executed = 1 if state.execution.success else 0
            signals_generated = len(state.analytics.signals)

            self._cycle_logger.log(cycle_id, {
                "status": CycleStatus.OK.value,
                "markets_scanned": state.market_data.markets_count,
                "signals_generated": signals_generated,
                "trades_executed": trades_executed,
                "decision": {"should_trade": state.decision.should_trade, "confidence": state.decision.confidence},
            })

            # Save snapshot
            save_snapshot(state)

            # Stats
            self._stats.save()

            serialized_signals = [
                dataclasses.asdict(s) for s in state.analytics.signals
            ]

            return CycleOutcome(
                cycle_id=cycle_id,
                status=CycleStatus.OK,
                started_at=started_at,
                finished_at=utcnow_iso(),
                markets_scanned=state.market_data.markets_count,
                signals_generated=signals_generated,
                trades_attempted=1 if state.execution.attempted else 0,
                trades_executed=trades_executed,
                found_signals=serialized_signals,
            )

        except Exception as e:
            logger.error("Cycle %s failed: %s", cycle_id, e, exc_info=True)
            self._cycle_logger.log(cycle_id, {"status": CycleStatus.ERROR.value, "error": str(e)})
            return CycleOutcome(
                cycle_id=cycle_id,
                status=CycleStatus.ERROR,
                started_at=started_at,
                finished_at=utcnow_iso(),
                error=str(e),
            )

def _make_execution_result(state):
    from app.execution.execution_schema import ExecutionResult
    return ExecutionResult(
        attempted=state.execution.attempted,
        success=state.execution.success,
        order_id=state.execution.order_id,
        filled_size=state.execution.filled_size,
        filled_price=state.execution.filled_price,
        mode=state.execution.mode,
        error=state.execution.error,
    )
