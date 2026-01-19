"""
High-precision timer for profiling
"""
import time
from contextlib import contextmanager
from typing import Generator


class Timer:
    """
    High-precision timer using monotonic clock

    Uses time.monotonic() which is guaranteed to not go backwards
    and is not affected by system clock changes.
    """

    def __init__(self):
        self._start_time: float = 0.0
        self._end_time: float = 0.0

    def start(self) -> None:
        """Start the timer"""
        self._start_time = time.monotonic()

    def stop(self) -> float:
        """
        Stop the timer and return elapsed time

        Returns:
            Elapsed time in seconds
        """
        self._end_time = time.monotonic()
        return self.elapsed

    @property
    def elapsed(self) -> float:
        """Get elapsed time without stopping the timer"""
        if self._end_time == 0.0:
            # Timer is still running
            return time.monotonic() - self._start_time
        else:
            # Timer has been stopped
            return self._end_time - self._start_time

    @staticmethod
    def get_time() -> float:
        """Get current monotonic time"""
        return time.monotonic()

    def reset(self) -> None:
        """Reset the timer"""
        self._start_time = 0.0
        self._end_time = 0.0

    @contextmanager
    def context(self) -> Generator['Timer', None, None]:
        """Context manager for automatic timing"""
        self.start()
        try:
            yield self
        finally:
            self.stop()


def get_time() -> float:
    """Convenience function to get current monotonic time"""
    return time.monotonic()
