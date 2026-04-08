import logging
from app.sizing.sizing_policy import SizingPolicy
from app.sizing.sizing_schema import SizingResult
from app.state.state_schema import CycleState, SizingOutput

logger = logging.getLogger(__name__)

class SizeRecommender:
    def recommend(self, state: CycleState, config: dict) -> SizingOutput:
        policy = SizingPolicy(
            base_size=config.get("sizing", {}).get("base_size", 10.0),
            min_size=config.get("sizing", {}).get("min_size", 1.0),
            max_size=config.get("sizing", {}).get("max_size", 500.0),
        )

        decision = state.decision
        if not decision.should_trade:
            state.sizing.recommended_size = 0.0
            state.sizing.raw_size = 0.0
            return state.sizing

        confidence = decision.confidence
        multiplier = confidence if policy.confidence_multiplier else 1.0
        raw_size = policy.base_size * max(multiplier, 0.1)

        capped = False
        cap_reason = None
        recommended_size = raw_size

        if recommended_size > policy.max_size:
            recommended_size = policy.max_size
            capped = True
            cap_reason = "max_size cap"
        if recommended_size < policy.min_size:
            recommended_size = policy.min_size

        logger.debug("Sizing: raw=%.2f recommended=%.2f multiplier=%.2f", raw_size, recommended_size, multiplier)

        state.sizing.raw_size = raw_size
        state.sizing.recommended_size = recommended_size
        state.sizing.applied_multiplier = multiplier
        state.sizing.capped = capped

        return state.sizing
