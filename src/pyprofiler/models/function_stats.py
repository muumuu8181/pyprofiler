"""
Function statistics data structure
"""
from dataclasses import dataclass


@dataclass
class FunctionStats:
    """
    Statistics for a single function

    Attributes:
        name: Function name
        call_count: Number of times the function was called
        total_time: Total execution time across all calls (including children)
        avg_time: Average execution time per call
        own_time: Total time spent in the function itself (excluding children)
        percentage: Percentage of total execution time
    """

    name: str
    call_count: int
    total_time: float
    avg_time: float
    own_time: float
    percentage: float

    def __repr__(self) -> str:
        return (
            f"FunctionStats(name={self.name!r}, "
            f"calls={self.call_count}, "
            f"total={self.total_time:.6f}s, "
            f"own={self.own_time:.6f}s, "
            f"{self.percentage:.1f}%)"
        )
