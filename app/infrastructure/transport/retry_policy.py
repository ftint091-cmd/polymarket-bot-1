from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    backoff_factor: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

    def execute(self, func, *args, **kwargs):
        last_exc = None
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                delay = self.base_delay_seconds * (self.backoff_factor ** attempt)
                logger.warning("Attempt %d/%d failed: %s. Retrying in %.1fs",
                               attempt + 1, self.max_attempts, e, delay)
                time.sleep(delay)
        raise last_exc
