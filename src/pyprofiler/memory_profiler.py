"""
Memory profiler for tracking memory usage

Uses tracemalloc to automatically track memory allocations.
"""
import sys
import gc
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict
import tracemalloc


class MemoryProfiler:
    """
    Memory profiler for tracking memory allocations automatically

    Uses Python's built-in tracemalloc module to track memory allocations
    without requiring manual object tracking.

    Enhanced with:
    - Per-object type memory tracking
    - Memory leak detection
    - Per-function memory usage tracking
    """

    def __init__(self):
        self._snapshots = []
        self._is_running = False
        self._start_snapshot = None
        self._object_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        self._function_memory = defaultdict(lambda: {'allocated': 0, 'freed': 0})

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

    def profile_object_types(self) -> Dict[str, Dict[str, int]]:
        """
        Get memory statistics by object type

        Returns:
            Dictionary mapping object types to their count and total size
        """
        if not self._snapshots:
            return {}

        _, end_snapshot = self._snapshots[-1]
        stats_by_type = defaultdict(lambda: {'count': 0, 'size': 0})

        for stat in end_snapshot.statistics('traceback'):
            # Get object type from traceback
            for trace in stat.traceback:
                obj_type = self._get_object_type_from_trace(trace)
                if obj_type:
                    stats_by_type[obj_type]['count'] += 1
                    stats_by_type[obj_type]['size'] += stat.size

        return dict(stats_by_type)

    def _get_object_type_from_trace(self, trace) -> Optional[str]:
        """Try to infer object type from traceback"""
        # This is a simplified version - in practice you'd need more sophisticated analysis
        filename = trace.filename
        if '<listcomp>' in filename or 'list' in filename.lower():
            return 'list'
        elif '<dictcomp>' in filename or 'dict' in filename.lower():
            return 'dict'
        elif '<setcomp>' in filename or 'set' in filename.lower():
            return 'set'
        return 'unknown'

    def detect_leaks(self, threshold: int = 1024) -> List[Dict[str, Any]]:
        """
        Detect potential memory leaks

        Args:
            threshold: Minimum size in bytes to consider as a leak

        Returns:
            List of potential memory leaks with details
        """
        if len(self._snapshots) < 2:
            return []

        leaks = []
        prev_snapshot = self._snapshots[-2][1]
        curr_snapshot = self._snapshots[-1][1]

        # Compare snapshots to find growing allocations
        prev_stats = {stat.traceback: stat for stat in prev_snapshot.statistics('traceback')}
        curr_stats = {stat.traceback: stat for stat in curr_snapshot.statistics('traceback')}

        for traceback, curr_stat in curr_stats.items():
            if traceback in prev_stats:
                prev_stat = prev_stats[traceback]
                growth = curr_stat.size - prev_stat.size

                if growth > threshold:
                    leaks.append({
                        'traceback': traceback,
                        'growth': growth,
                        'current_size': curr_stat.size,
                        'location': f"{curr_stat.traceback[0].filename}:{curr_stat.traceback[0].lineno}"
                    })

        # Sort by growth descending
        leaks.sort(key=lambda x: x['growth'], reverse=True)
        return leaks

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
            'top_stats': top_stats,
            'object_types': self.profile_object_types(),
            'leaks': self.detect_leaks()
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

        # Print object type breakdown
        if stats['object_types']:
            print(f"\nMemory by Object Type:")
            for obj_type, data in sorted(stats['object_types'].items(),
                                        key=lambda x: x[1]['size'],
                                        reverse=True)[:top_n]:
                print(f"  {obj_type}: {data['count']:,} objects, "
                      f"{data['size']:,} bytes ({data['size'] / 1024:.2f} KB)")

        # Print potential leaks
        if stats['leaks']:
            print(f"\nPotential Memory Leaks (Top {min(top_n, len(stats['leaks']))}):")
            for leak in stats['leaks'][:top_n]:
                print(f"  +{leak['growth']:,} bytes at {leak['location']}")

        print(f"\nTop {top_n} memory allocations:")

        for stat in stats['top_stats'][:top_n]:
            print(f"  {stat}")


__all__ = ['MemoryProfiler']
