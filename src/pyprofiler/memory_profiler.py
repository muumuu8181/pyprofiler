"""
Memory profiler for tracking memory usage

Uses tracemalloc to automatically track memory allocations.
"""
import sys
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import tracemalloc


class MemoryProfiler:
    """
    Memory profiler for tracking memory allocations automatically

    Uses Python's built-in tracemalloc module to track memory allocations
    without requiring manual object tracking.
    """

    def __init__(self):
        self._snapshots = []
        self._is_running = False
        self._start_snapshot = None

    def start(self) -> None:
        """Start memory profiling"""
        if not self._is_running:
            tracemalloc.start()
            self._start_snapshot = tracemalloc.take_snapshot()
            self._is_running = True

    def stop(self) -> None:
        """Stop memory profiling"""
        if self._is_running:
            snapshot = tracemalloc.take_snapshot()
            self._snapshots.append((self._start_snapshot, snapshot))
            tracemalloc.stop()
            self._is_running = False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with memory statistics
        """
        if not self._snapshots:
            return {}

        # Use the most recent profiling session
        start_snapshot, end_snapshot = self._snapshots[-1]

        # Calculate total memory growth
        start_stats = start_snapshot.statistics('lineno')
        end_stats = end_snapshot.statistics('lineno')

        start_total = sum(stat.size for stat in start_stats)
        end_total = sum(stat.size for stat in end_stats)
        growth = end_total - start_total

        # Get top memory allocations
        top_stats = end_stats[:10]

        return {
            'initial_total': start_total,
            'final_total': end_total,
            'growth': growth,
            'top_stats': top_stats
        }

    def print_stats(self, top_n: int = 10) -> None:
        """Print memory statistics to console"""
        stats = self.get_stats()
        if not stats:
            print("No memory profiling data available")
            return

        print("\nMemory Statistics:")
        print(f"  Initial: {stats['initial_total']:,} bytes ({stats['initial_total'] / 1024:.2f} KB)")
        print(f"  Final:   {stats['final_total']:,} bytes ({stats['final_total'] / 1024:.2f} KB)")
        print(f"  Growth:  {stats['growth']:+,} bytes ({stats['growth'] / 1024:+.2f} KB)")
        print(f"\nTop {top_n} memory allocations:")

        for stat in stats['top_stats'][:top_n]:
            print(f"  {stat}")


__all__ = ['MemoryProfiler']
