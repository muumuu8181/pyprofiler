"""
Memory profiler for tracking memory usage
"""
import sys
from typing import Dict, Any
from collections import defaultdict


class MemoryProfiler:
    """
    Memory profiler for tracking object allocations and memory usage

    Note: This is a simplified implementation. For production use,
    consider using tools like memory_profiler or tracemalloc.
    """

    def __init__(self):
        self._snapshots = []
        self._object_tracker = defaultdict(int)
        self._is_running = False

    def start(self) -> None:
        """Start memory profiling"""
        self._is_running = True
        self._take_snapshot()

    def stop(self) -> None:
        """Stop memory profiling"""
        self._is_running = False
        self._take_snapshot()

    def track_object(self, obj: Any) -> None:
        """
        Track an object's memory allocation

        Args:
            obj: Object to track
        """
        if not self._is_running:
            return

        obj_type = type(obj).__name__
        size = sys.getsizeof(obj)
        self._object_tracker[obj_type] += size

    def _take_snapshot(self) -> None:
        """Take a snapshot of current memory usage"""
        import gc

        # Force garbage collection to get accurate numbers
        gc.collect()

        snapshot = {
            'objects': dict(self._object_tracker),
            'total': sum(self._object_tracker.values())
        }
        self._snapshots.append(snapshot)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with memory statistics
        """
        if not self._snapshots:
            return {}

        first = self._snapshots[0]
        last = self._snapshots[-1]

        return {
            'initial_total': first['total'],
            'final_total': last['total'],
            'growth': last['total'] - first['total'],
            'object_types': last['objects']
        }

    def print_stats(self) -> None:
        """Print memory statistics to console"""
        stats = self.get_stats()
        if not stats:
            print("No memory profiling data available")
            return

        print("\nMemory Statistics:")
        print(f"  Initial: {stats['initial_total']:,} bytes")
        print(f"  Final: {stats['final_total']:,} bytes")
        print(f"  Growth: {stats['growth']:+,} bytes")
        print("\nTop object types:")

        # Sort by size
        sorted_objects = sorted(
            stats['object_types'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        for obj_type, size in sorted_objects[:10]:
            print(f"  {obj_type:<30} {size:>12,} bytes")


__all__ = ['MemoryProfiler']
