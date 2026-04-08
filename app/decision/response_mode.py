class ResponseMode:
    """Determines response aggressiveness based on confidence level."""

    def get_mode(self, confidence: float, config: dict) -> str:
        thresholds = config.get("decision", {}).get("response_mode", {})
        aggressive_threshold = thresholds.get("aggressive", 0.8)
        moderate_threshold = thresholds.get("moderate", 0.5)

        if confidence >= aggressive_threshold:
            return "aggressive"
        elif confidence >= moderate_threshold:
            return "moderate"
        else:
            return "conservative"
