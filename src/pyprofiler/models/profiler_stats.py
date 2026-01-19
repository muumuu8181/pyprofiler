"""
Profiler statistics data structure
"""
from dataclasses import dataclass
from typing import Dict, List

from .function_stats import FunctionStats


@dataclass
class ProfilerStats:
    """
    Overall profiling statistics

    Attributes:
        total_time: Total execution time
        function_stats: Dictionary mapping function names to their statistics
        function_list: Sorted list of function statistics by total time
    """

    total_time: float
    function_stats: Dict[str, FunctionStats]
    function_list: List[FunctionStats]

    def __init__(self, total_time: float, function_stats: Dict[str, FunctionStats]):
        self.total_time = total_time
        self.function_stats = function_stats
        # Sort by total time descending
        self.function_list = sorted(
            function_stats.values(),
            key=lambda x: x.total_time,
            reverse=True
        )

    def get_top_functions(self, n: int = 10) -> List[FunctionStats]:
        """Get top N functions by total execution time"""
        return self.function_list[:n]

    def get_function_stats(self, name: str) -> FunctionStats:
        """Get statistics for a specific function"""
        return self.function_stats.get(name)

    def __repr__(self) -> str:
        return f"ProfilerStats(total_time={self.total_time:.6f}s, functions={len(self.function_stats)})"
