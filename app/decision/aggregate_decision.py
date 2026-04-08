import logging
from app.decision.gate_layer import GateLayer
from app.decision.confidence_layer import ConfidenceLayer
from app.decision.response_mode import ResponseMode
from app.decision.decision_schema import DecisionResult
from app.state.state_schema import CycleState, AnalyticsOutput, DecisionOutput

logger = logging.getLogger(__name__)

class AggregateDecision:
    def __init__(self):
        self._gate = GateLayer()
        self._confidence = ConfidenceLayer()
        self._response_mode = ResponseMode()

    def decide(self, state: CycleState, config: dict) -> DecisionOutput:
        analytics = state.analytics

        gate_pass, gate_reason = self._gate.check(analytics, config)
        if not gate_pass:
            logger.debug("Gate rejected: %s", gate_reason)
            state.decision.should_trade = False
            state.decision.reason = gate_reason
            return state.decision

        signal_id, market_id, side, confidence = self._confidence.aggregate(analytics.signals, config)
        mode = self._response_mode.get_mode(confidence, config)

        logger.info("Decision: trade=%s market=%s side=%s confidence=%.2f mode=%s",
                    confidence > 0, market_id, side, confidence, mode)

        state.decision.should_trade = confidence > 0 and market_id is not None
        state.decision.signal_id = signal_id
        state.decision.market_id = market_id
        state.decision.side = side
        state.decision.confidence = confidence
        state.decision.reason = f"mode={mode}, gate=passed"

        return state.decision
