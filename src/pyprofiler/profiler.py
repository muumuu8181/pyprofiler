"""
Main profiler module
"""
from abc import ABC, abstractmethod
from typing import Optional
import threading

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

    def __init__(self, interval: float = 0.001, sampling_rate: float = 1.0, adaptive_sampling: bool = False,
                 real_time_monitoring: bool = False, monitor_interval: float = 1.0):
        """
        Initialize CPU profiler

        Args:
            interval: Sampling interval (currently unused, reserved for future)
            sampling_rate: Fraction of calls to profile (0.0-1.0). 1.0 = profile all, 0.1 = profile 10%
            adaptive_sampling: If True, adjust sampling rate based on function execution time
            real_time_monitoring: If True, print stats in real-time while profiling
            monitor_interval: Seconds between real-time updates
        """
        super().__init__()
        self.interval = interval
        self.sampling_rate = max(0.0, min(1.0, sampling_rate))
        self.adaptive_sampling = adaptive_sampling
        self.real_time_monitoring = real_time_monitoring
        self.monitor_interval = monitor_interval
        self._call_stack = []
        self._function_times = {}
        from collections import defaultdict
        self._call_counts = defaultdict(int)
        self._enabled = True
        self._sample_counter = 0
        # Thread-safe locks
        self._lock = threading.Lock()
        self._call_start_times_lock = threading.Lock()
        # Call tree tracking
        self._call_tree = []  # List of root CallFrame objects
        self._current_call_frames = []  # Stack of currently executing calls
        self._caller_callee_counts = defaultdict(lambda: defaultdict(int))  # (caller, callee) -> count
        # Adaptive sampling
        self._function_avg_times = defaultdict(float)  # Track average times for adaptive sampling
        # Real-time monitoring
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()

    def start(self) -> None:
        """Start profiling"""
        self._is_running = True
        self._timer.start()

        # Start real-time monitoring thread if enabled
        if self.real_time_monitoring:
            self._stop_monitoring.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()

    def stop(self) -> None:
        """Stop profiling"""
        self._is_running = False
        self._timer.stop()

        # Stop real-time monitoring
        if self._monitor_thread is not None:
            self._stop_monitoring.set()
            self._monitor_thread.join(timeout=2.0)
            self._monitor_thread = None

    def _monitor_loop(self):
        """Background thread for real-time monitoring"""
        import sys
        while not self._stop_monitoring.is_set() and self._is_running:
            self._stop_monitoring.wait(self.monitor_interval)

            if not self._is_running:
                break

            # Print current stats
            stats = self.get_stats()
            if stats and stats.function_list:
                print(f"\n[Real-time] Top 5 functions:")
                for i, func_stats in enumerate(stats.get_top_functions(5), 1):
                    print(f"  {i}. {func_stats.name}: {func_stats.call_count} calls, "
                          f"{func_stats.total_time:.6f}s total")
                print(f"  Total time: {stats.total_time:.6f}s\n")

    def save_real_time_log(self, filepath: str, interval: float = 1.0) -> threading.Thread:
        """
        Save profiling stats to file in real-time

        Args:
            filepath: Path to output log file
            interval: Seconds between updates

        Returns:
            Thread object for the logger
        """
        import time
        import json

        def log_loop():
            with open(filepath, 'w', buffering=8192) as f:
                f.write("[\n")
                first = True
                while self._is_running:
                    stats = self.get_stats()
                    if stats and stats.function_list:
                        if not first:
                            f.write(",\n")
                        first = False

                        log_entry = {
                            'timestamp': time.time(),
                            'total_time': stats.total_time,
                            'functions': [
                                {
                                    'name': fs.name,
                                    'calls': fs.call_count,
                                    'total_time': fs.total_time,
                                    'own_time': fs.own_time
                                }
                                for fs in stats.get_top_functions(10)
                            ]
                        }
                        f.write(json.dumps(log_entry, indent=2))

                    time.sleep(interval)
                f.write("\n]\n")

        log_thread = threading.Thread(target=log_loop, daemon=True)
        log_thread.start()
        return log_thread

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

            func_name = func.__name__

            # Adaptive sampling: adjust rate based on historical execution time
            sample_rate = self.sampling_rate
            if self.adaptive_sampling and func_name in self._function_avg_times:
                avg_time = self._function_avg_times[func_name]
                # Slower functions get higher sampling rate
                if avg_time > 0.001:  # > 1ms
                    sample_rate = min(1.0, sample_rate * 2)
                elif avg_time > 0.0001:  # > 0.1ms
                    sample_rate = sample_rate
                else:  # Very fast functions
                    sample_rate = max(0.1, sample_rate / 2)

            # Sampling: only profile fraction of calls
            self._sample_counter += 1
            import random
            if random.random() > sample_rate:
                return func(*args, **kwargs)

            # Record function name (thread-safe)
            with self._lock:
                self._call_counts[func_name] += 1

            # Track caller-callee relationship
            caller_name = self._current_call_frames[-1].name if self._current_call_frames else '<module>'

            # Create call frame for call tree tracking
            try:
                from .models import CallFrame
            except ImportError:
                from models import CallFrame

            start_time = self._timer.get_time()
            call_frame = CallFrame(
                name=func_name,
                filename=func.__code__.co_filename,
                line_no=func.__code__.co_firstlineno,
                start_time=start_time,
                end_time=0.0  # Will be set on return
            )

            # Add to call tree
            with self._lock:
                if self._current_call_frames:
                    self._current_call_frames[-1].add_child(call_frame)
                else:
                    self._call_tree.append(call_frame)
                self._current_call_frames.append(call_frame)
                self._caller_callee_counts[caller_name][func_name] += 1

            # Execute the function
            try:
                result = func(*args, **kwargs)
            finally:
                end_time = self._timer.get_time()
                elapsed = end_time - start_time

                # Update average time for adaptive sampling
                if self.adaptive_sampling:
                    with self._lock:
                        old_avg = self._function_avg_times[func_name]
                        # Exponential moving average
                        self._function_avg_times[func_name] = 0.9 * old_avg + 0.1 * elapsed

                # Update call frame
                with self._lock:
                    call_frame.end_time = end_time
                    self._current_call_frames.pop()

                # Record execution time (thread-safe)
                with self._lock:
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

        # Build function stats with call tree information
        try:
            from .models import FunctionStats
        except ImportError:
            from models import FunctionStats
        function_stats = {}

        # Calculate own time from call tree (excluding children)
        own_times = {}
        for root in self._call_tree:
            self._calculate_own_time_recursive(root, own_times)

        for func_name, times in self._function_times.items():
            call_count = len(times)
            total = sum(times)
            avg = total / call_count if call_count > 0 else 0
            own_time = own_times.get(func_name, total)  # Use call tree data if available
            percentage = (total / total_time * 100) if total_time > 0 else 0

            # Collect callers and callees
            callers = {}
            callees = {}
            for caller, callee_dict in self._caller_callee_counts.items():
                for callee, count in callee_dict.items():
                    if callee == func_name:
                        callers[caller] = callers.get(caller, 0) + count
                    if caller == func_name:
                        callees[callee] = callees.get(callee, 0) + count

            function_stats[func_name] = FunctionStats(
                name=func_name,
                call_count=call_count,
                total_time=total,
                avg_time=avg,
                own_time=own_time,
                percentage=percentage,
                callers=callers,
                callees=callees
            )

        return ProfilerStats(
            total_time=total_time,
            function_stats=function_stats
        )

    def _calculate_own_time_recursive(self, frame, own_times):
        """Recursively calculate own time (excluding children) from call tree"""
        children_time = sum(child.duration for child in frame.children)
        own = max(0, frame.duration - children_time)

        if frame.name not in own_times:
            own_times[frame.name] = 0
        own_times[frame.name] += own

        for child in frame.children:
            self._calculate_own_time_recursive(child, own_times)

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

    def save_stats(self, filepath: str, top_n: int = 10) -> None:
        """
        Save profiling statistics to file with buffering

        Args:
            filepath: Path to output file
            top_n: Number of top functions to display
        """
        stats = self.get_stats()
        if stats is None:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("No profiling data available\n")
            return

        # Build output in memory for efficiency
        lines = []
        lines.append(f"{'Function':<30} {'Calls':<10} {'Total(s)':<12} {'Own(s)':<12} {'%'}")
        lines.append("-" * 80)

        for func_stats in stats.get_top_functions(top_n):
            lines.append(
                f"{func_stats.name:<30} "
                f"{func_stats.call_count:<10} "
                f"{func_stats.total_time:<12.6f} "
                f"{func_stats.own_time:<12.6f} "
                f"{func_stats.percentage:>6.1f}%"
            )

        lines.append("-" * 80)
        lines.append(f"Total time: {stats.total_time:.6f}s")

        # Write all at once with buffering
        with open(filepath, 'w', encoding='utf-8', buffering=8192) as f:
            f.write('\n'.join(lines) + '\n')

    def dump_stats(self, filename: str) -> None:
        """
        Dump profiling statistics to file (cProfile compatible)

        Args:
            filename: Path to output file (will be saved as pickle format)
        """
        import pickle
        stats = self.get_stats()
        if stats is None:
            stats = ProfilerStats(total_time=0, function_stats={})
        with open(filename, 'wb') as f:
            pickle.dump(stats, f)

    def load_stats(self, filename: str) -> ProfilerStats:
        """
        Load profiling statistics from file (cProfile compatible)

        Args:
            filename: Path to input file

        Returns:
            ProfilerStats object
        """
        import pickle
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def strip_dirs(self) -> None:
        """
        Strip directory paths from function names (cProfile compatible)

        This is a no-op for our implementation since we use function names only.
        Kept for API compatibility.
        """
        pass

    def print_pstats(self, filename: str = None) -> None:
        """
        Print statistics in pstats format (cProfile compatible)

        Args:
            filename: Optional file path to write pstats output
        """
        import sys
        stats = self.get_stats()
        if stats is None:
            return

        lines = []
        lines.append(f"   ncalls  tottime  percall  cumtime  percall filename:lineno(function)")

        for func_stats in stats.function_list:
            # Format: ncalls tottime percall cumtime percall filename:lineno(function)
            lines.append(
                f"{func_stats.call_count:8d}  "
                f"{func_stats.own_time:8.6f}  "
                f"{func_stats.own_time / max(1, func_stats.call_count):8.6f}  "
                f"{func_stats.total_time:8.6f}  "
                f"{func_stats.total_time / max(1, func_stats.call_count):8.6f}  "
                f"~:{0}({func_stats.name})"
            )

        output = '\n'.join(lines)

        if filename:
            with open(filename, 'w') as f:
                f.write(output)
        else:
            print(output)

    def get_pstats_data(self) -> dict:
        """
        Get profiling data in pstats-compatible format

        Returns:
            Dictionary with pstats-style data structure
        """
        stats = self.get_stats()
        if stats is None:
            return {}

        pstats_data = {
            'total_time': stats.total_time,
            'profiles': {}
        }

        for func_stats in stats.function_list:
            func_key = (func_stats.name, 0, func_stats.name)  # (filename, line, funcname)
            pstats_data['profiles'][func_key] = {
                'ncalls': func_stats.call_count,
                'tottime': func_stats.own_time,
                'cumtime': func_stats.total_time,
                'callers': { (caller, 0, caller): count for caller, count in func_stats.callers.items() }
            }

        return pstats_data

    def reset(self) -> None:
        """Reset all profiling data"""
        from collections import defaultdict
        self._call_stack = []
        self._function_times = {}
        self._call_counts = defaultdict(int)
        self._call_tree = []
        self._current_call_frames = []
        self._caller_callee_counts.clear()
        self._function_avg_times.clear()
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
