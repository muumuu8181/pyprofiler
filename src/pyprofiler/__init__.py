"""
pyprofiler - Python profiler for CPU and memory profiling
"""
from .profiler import Profiler, CPUProfiler, profile_function
from .memory_profiler import MemoryProfiler
from .models import ProfilerStats, FunctionStats

__version__ = "0.2.0"

__all__ = [
    'Profiler',
    'CPUProfiler',
    'profile_function',
    'MemoryProfiler',
    'ProfilerStats',
    'FunctionStats',
    'run',
    'runctx',
]


def run(statement, filename=None, sort=-1, output=None, sampling_rate=1.0):
    """
    Run a statement under profiler profiling (cProfile compatible)

    This is the main entry point for profiling without code modification.
    It uses sys.setprofile() to automatically trace all function calls.

    Args:
        statement: String containing Python code to execute
        filename: Optional filename for reporting (defaults to '<profiler>')
        sort: Sort key for results (default: -1 for cumulative time)
        output: Output file object (default: sys.stdout)
        sampling_rate: Fraction of calls to profile (0.0-1.0). 1.0 = profile all (default)

    Returns:
        ProfilerStats object with profiling results

    Examples:
        >>> import pyprofiler
        >>> pyprofiler.run('my_function()')
        >>> pyprofiler.run('import math; math.factorial(10000)')
        >>> pyprofiler.run('my_function()', sampling_rate=0.1)  # Profile 10% of calls
    """
    import sys
    import threading

    if output is None:
        output = sys.stdout

    profiler = CPUProfiler(sampling_rate=sampling_rate)

    # Track call start times for accurate measurement
    profiler._call_start_times = {}

    # Sampling support
    import random
    import _thread

    def profile_hook(frame, event, arg):
        """Profile hook for sys.setprofile()"""
        func_name = frame.f_code.co_name
        filename_local = frame.f_code.co_filename

        # Fast-path: skip private/special functions first (no string operations)
        if func_name.startswith('_'):
            return
        if func_name in ('<module>', '<listcomp>', '<dictcomp>', '<setcomp>', '<genexpr>'):
            return

        # Normalize path once for filename checks
        normalized_path = filename_local.replace('\\', '/')

        # Skip profiler internals and Python internals
        if 'pyprofiler' in normalized_path:
            return
        if 'site-packages' in normalized_path:
            return
        if 'lib/python' in normalized_path:
            return

        # Sampling: only profile fraction of calls
        if event == 'call' and random.random() > sampling_rate:
            return

        if event == 'call':
            profiler._call_counts[func_name] += 1
            profiler._call_start_times[func_name] = profiler._timer.get_time()

        elif event == 'return':
            start_time = profiler._call_start_times.pop(func_name, None)
            if start_time is not None:
                elapsed = profiler._timer.get_time() - start_time
                if func_name not in profiler._function_times:
                    profiler._function_times[func_name] = []
                profiler._function_times[func_name].append(elapsed)

    profiler.start()
    sys.setprofile(profile_hook)
    threading.setprofile(profile_hook)

    try:
        exec(statement, globals())
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
        profiler.stop()

    # Print and return stats
    stats = profiler.get_stats()
    if stats:
        profiler.print_stats()

    return stats


def runctx(statement, globals, locals, filename=None, sort=-1, output=None):
    """
    Run a statement under profiler with custom context

    Args:
        statement: String containing Python code to execute
        globals: Global namespace for execution
        locals: Local namespace for execution
        filename: Optional filename for reporting
        sort: Sort key for results
        output: Output file object

    Returns:
        ProfilerStats object with profiling results
    """
    import sys

    if output is None:
        output = sys.stdout

    profiler = CPUProfiler()
    profiler.start()

    # Use sys.setprofile for automatic tracing
    def profile_hook(frame, event, arg):
        if event == 'call':
            func_name = frame.f_code.co_name
            profiler._call_counts[func_name] += 1

    sys.setprofile(profile_hook)

    try:
        exec(statement, globals, locals)
    finally:
        sys.setprofile(None)
        profiler.stop()

    stats = profiler.get_stats()
    if stats:
        profiler.print_stats()

    return stats
