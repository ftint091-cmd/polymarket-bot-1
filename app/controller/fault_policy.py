from dataclasses import dataclass, field

@dataclass
class FaultPolicy:
    max_consecutive_errors: int = 5
    max_errors_per_hour: int = 20
    _consecutive_errors: int = field(default=0, init=False, repr=False)
    _total_errors: int = field(default=0, init=False, repr=False)

    def record_error(self) -> bool:
        """Record error, return True if should escalate to fault state."""
        self._consecutive_errors += 1
        self._total_errors += 1
        return self._consecutive_errors >= self.max_consecutive_errors

    def record_success(self) -> None:
        self._consecutive_errors = 0

    def reset(self) -> None:
        self._consecutive_errors = 0
        self._total_errors = 0

    @property
    def consecutive_errors(self) -> int:
        return self._consecutive_errors
