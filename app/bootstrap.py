from app.config.profile_manager import ProfileManager
from app.config.runtime_config import RuntimeConfig
from app.infrastructure.secrets.secrets_provider import SecretsProvider
from app.infrastructure.api.polymarket_market_client import PolymarketMarketClient
from app.infrastructure.api.binance_market_client import BinanceMarketClient
from app.infrastructure.api.wallet_client import WalletClient
from app.market.adapters.polymarket_adapter import PolymarketAdapter
from app.market.adapters.binance_adapter import BinanceAdapter
from app.market.monitor import MarketMonitor
from app.state.state_builder import StateBuilder
from app.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.analytics.modules.spread_pressure import SpreadPressureModule
from app.analytics.modules.edge_estimator import EdgeEstimatorModule
from app.analytics.modules.book_imbalance import BookImbalanceModule
from app.analytics.modules.binance_move_context import BinanceMoveContextModule
from app.analytics.modules.filters.market_filters import MarketFiltersModule
from app.analytics.modules.filters.strategy_filters import StrategyFiltersModule
from app.analytics.modules.filters.admission_filters import AdmissionFiltersModule
from app.analytics.modules.filters.system_filters import SystemFiltersModule
from app.decision.aggregate_decision import AggregateDecision
from app.sizing.size_recommender import SizeRecommender
from app.risk.capital_risk_check import CapitalRiskCheck
from app.execution.executor import Executor
from app.positions.position_store import PositionStore
from app.positions.position_service import PositionService
from app.orchestration.orchestrator import Orchestrator
from app.controller.controller import Controller

def build_orchestrator(config: dict) -> Orchestrator:
    secrets = SecretsProvider()

    use_mock = not secrets.is_real_trading_enabled()

    poly_client = PolymarketMarketClient(use_mock=use_mock)
    binance_client = BinanceMarketClient(use_mock=use_mock)

    poly_adapter = PolymarketAdapter(poly_client)
    binance_adapter = BinanceAdapter(binance_client)

    monitor = MarketMonitor(poly_adapter, binance_adapter, config)
    state_builder = StateBuilder()

    analytics = AnalyticsOrchestrator([
        SystemFiltersModule(),
        MarketFiltersModule(),
        StrategyFiltersModule(),
        AdmissionFiltersModule(),
        BinanceMoveContextModule(),
        SpreadPressureModule(),
        EdgeEstimatorModule(),
        BookImbalanceModule(),
    ])

    decision = AggregateDecision()
    sizer = SizeRecommender()
    risk = CapitalRiskCheck()

    execution_mode = config.get("execution_mode", "paper")
    executor = Executor(mode=execution_mode)

    position_store = PositionStore()
    position_service = PositionService(position_store)

    return Orchestrator(
        monitor=monitor,
        state_builder=state_builder,
        analytics=analytics,
        decision=decision,
        sizer=sizer,
        risk=risk,
        executor=executor,
        position_service=position_service,
        config=config,
    )

def build_controller(profile: str = "default", config_dir: str = "config") -> Controller:
    profile_manager = ProfileManager(config_dir)
    config = profile_manager.get_config(profile)
    orchestrator = build_orchestrator(config)
    return Controller(orchestrator, config)
