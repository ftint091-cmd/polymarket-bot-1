import logging
from app.risk.exposure_policy import ExposurePolicy
from app.risk.risk_schema import RiskCheckResult
from app.state.state_schema import CycleState, CapitalRiskOutput

logger = logging.getLogger(__name__)

class CapitalRiskCheck:
    def check(self, state: CycleState, capital: float, existing_exposure: float, config: dict) -> CapitalRiskOutput:
        policy = ExposurePolicy(
            max_position_pct=config.get("risk", {}).get("max_position_pct", 0.05),
            max_total_exposure_pct=config.get("risk", {}).get("max_total_exposure_pct", 0.25),
            min_capital_reserve_pct=config.get("risk", {}).get("min_capital_reserve_pct", 0.10),
        )

        recommended_size = state.sizing.recommended_size

        if not state.decision.should_trade or recommended_size == 0:
            state.capital_risk.approved = False
            state.capital_risk.rejection_reason = "No trade decision"
            state.capital_risk.capital_available = capital
            state.capital_risk.exposure_before = existing_exposure
            return state.capital_risk

        max_position = capital * policy.max_position_pct
        max_new_exposure = capital * policy.max_total_exposure_pct - existing_exposure
        reserve = capital * policy.min_capital_reserve_pct
        available_capital = capital - reserve - existing_exposure

        approved_size = min(recommended_size, max_position, max(0, max_new_exposure), available_capital)

        min_size = config.get("sizing", {}).get("min_size", 1.0)

        if approved_size < min_size:
            reason = f"Approved size {approved_size:.2f} below min {min_size}"
            logger.warning("Risk rejected: %s", reason)
            state.capital_risk.approved = False
            state.capital_risk.approved_size = 0.0
            state.capital_risk.rejection_reason = reason
            state.capital_risk.capital_available = capital
            state.capital_risk.exposure_before = existing_exposure
        else:
            logger.info("Risk approved: size=%.2f (requested=%.2f)", approved_size, recommended_size)
            state.capital_risk.approved = True
            state.capital_risk.approved_size = approved_size
            state.capital_risk.rejection_reason = None
            state.capital_risk.capital_available = capital
            state.capital_risk.exposure_before = existing_exposure

        return state.capital_risk
