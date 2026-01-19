"""
Main profiler module
"""
from abc import ABC, abstractmethod
from typing import Optional

try:
    from .models import ProfilerStats
    from .utils import Timer
except ImportError:
    from models import ProfilerStats
    from utils import Timer


class Profiler(ABC):
    """Abstract base class for profilers"""

    def __init__(self):
        self._timer = Timer()
        self._is_running = False

    @abstractmethod
    def start(self) -> None:
        """Start profiling"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop profiling"""
        pass

    @abstractmethod
    def get_stats(self) -> Optional[ProfilerStats]:
        """Get profiling statistics"""
        pass


class CPUProfiler(Profiler):
    """
    CPU profiler for measuring function execution time

    Supports both decorator and context manager usage:

    As decorator:
        @profiler.profile_function
        def my_function():
            pass

    As context manager:
        with profiler.profile():
            my_function()
    """

    def __init__(self, interval: float = 0.001):
        """
        Initialize CPU profiler

        Args:
            interval: Sampling interval (currently unused, reserved for future)
        """
        super().__init__()
        self.interval = interval
        self._call_stack = []
        self._function_times = {}
        self._call_counts = {}
        self._enabled = True

    def start(self) -> None:
        """Start profiling"""
        self._is_running = True
        self._timer.start()

    def stop(self) -> None:
        """Stop profiling"""
        self._is_running = False
        self._timer.stop()

    @property
    def is_running(self) -> bool:
        """Check if profiler is running"""
        return self._is_running

    def profile_function(self, func):
        """
        Decorator to profile a function

        Args:
            func: Function to profile

        Returns:
            Wrapped function that records execution time
        """
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self._enabled or not self._is_running:
                return func(*args, **kwargs)

            # Record function name
            func_name = func.__name__
            self._call_counts[func_name] = self._call_counts.get(func_name, 0) + 1

            # Time the function
            start_time = self._timer.get_time()
            result = func(*args, **kwargs)
            end_time = self._timer.get_time()

            # Record execution time
            elapsed = end_time - start_time
            if func_name not in self._function_times:
                self._function_times[func_name] = []
            self._function_times[func_name].append(elapsed)

            return result

        return wrapper

    def profile(self, enabled: bool = True):
        """
        Context manager for profiling code blocks

        Args:
            enabled: Whether profiling is enabled

        Example:
            with profiler.profile():
                # Code to profile
                pass
        """
        from contextlib import contextmanager

        @contextmanager
        def _profile_context():
            old_enabled = self._enabled
            self._enabled = enabled
            old_running = self._is_running
            self._is_running = True
            self._timer.start()
            try:
                yield self
            finally:
                self._timer.stop()
                self._is_running = old_running
                self._enabled = old_enabled

        return _profile_context()

    def get_stats(self) -> Optional[ProfilerStats]:
        """
        Get profiling statistics

        Returns:
            ProfilerStats object with aggregated statistics
        """
        if not self._function_times:
            return None

        total_time = self._timer.elapsed

        # Build function stats
        try:
            from .models import FunctionStats
        except ImportError:
            from models import FunctionStats
        function_stats = {}

        for func_name, times in self._function_times.items():
            call_count = len(times)
            total = sum(times)
            avg = total / call_count if call_count > 0 else 0
            own_time = total  # Simplified: we're not tracking children separately yet
            percentage = (total / total_time * 100) if total_time > 0 else 0

            function_stats[func_name] = FunctionStats(
                name=func_name,
                call_count=call_count,
                total_time=total,
                avg_time=avg,
                own_time=own_time,
                percentage=percentage
            )

        return ProfilerStats(
            total_time=total_time,
            function_stats=function_stats
        )

    def print_stats(self, top_n: int = 10) -> None:
        """
        Print profiling statistics to console

        Args:
            top_n: Number of top functions to display
        """
        stats = self.get_stats()
        if stats is None:
            print("No profiling data available")
            return

        print(f"\n{'Function':<30} {'Calls':<10} {'Total(s)':<12} {'Own(s)':<12} {'%'}")
        print("-" * 80)

        for func_stats in stats.get_top_functions(top_n):
            print(
                f"{func_stats.name:<30} "
                f"{func_stats.call_count:<10} "
                f"{func_stats.total_time:<12.6f} "
                f"{func_stats.own_time:<12.6f} "
                f"{func_stats.percentage:>6.1f}%"
            )

        print("-" * 80)
        print(f"Total time: {stats.total_time:.6f}s")

    def reset(self) -> None:
        """Reset all profiling data"""
        self._call_stack = []
        self._function_times = {}
        self._call_counts = {}
        self._timer.reset()


# Convenience function
def profile_function(func):
    """
    Decorator to profile a function with default profiler

    Example:
        @profile_function
        def my_function():
            pass
    """
    profiler = CPUProfiler()
    return profiler.profile_function(func)


__all__ = ['Profiler', 'CPUProfiler', 'profile_function']
