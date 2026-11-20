import time
from enum import Enum


class State(Enum):
    CLOSED = 0
    HALF_OPEN = 1
    OPEN = 2

class CircuitBreaker:

    def __init__(self, failure_threshold: int = 5, cooldown_sec: float = 300.0):
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if cooldown_sec < 1:
            raise ValueError("cooldown_sec must be >= 1")
        self.state = State.CLOSED
        self.failure_threshold = failure_threshold
        self.cooldown_sec = cooldown_sec
        self.consecutive_failures = 0
        self.opened_at: float | None = None
        self.probe_in_flight: bool = False

    def allow_request(self) -> bool:
        if self.state == State.CLOSED:
            return True
        elif self.state == State.OPEN:
            if self.opened_at is not None and (time.monotonic() - self.opened_at >= self.cooldown_sec):
                self.probe_in_flight = True
                self.state = State.HALF_OPEN
                return True
            else:
                return False
        elif self.state == State.HALF_OPEN:
            if not self.probe_in_flight:
                self.probe_in_flight = True
                return True
            return False

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.opened_at = None
        self.state = State.CLOSED
        self.probe_in_flight = False

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.state == State.HALF_OPEN or (self.consecutive_failures >= self.failure_threshold):
            self.state = State.OPEN
            self.opened_at = time.monotonic()
        self.probe_in_flight = False