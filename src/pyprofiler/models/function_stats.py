"""
Function statistics data structure
"""
from dataclasses import dataclass, field
from typing import Dict, List


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
        callers: Dictionary of caller function names and their call counts
        callees: Dictionary of callee function names and their call counts
    """

    name: str
    call_count: int
    total_time: float
    avg_time: float
    own_time: float
    percentage: float
    callers: Dict[str, int] = field(default_factory=dict)
    callees: Dict[str, int] = field(default_factory=dict)

    def add_caller(self, caller_name: str) -> None:
        """Record that this function was called by caller_name"""
        self.callers[caller_name] = self.callers.get(caller_name, 0) + 1

    def add_callee(self, callee_name: str) -> None:
        """Record that this function called callee_name"""
        self.callees[callee_name] = self.callees.get(callee_name, 0) + 1

    def __repr__(self) -> str:
        return (
            f"FunctionStats(name={self.name!r}, "
            f"calls={self.call_count}, "
            f"total={self.total_time:.6f}s, "
            f"own={self.own_time:.6f}s, "
            f"{self.percentage:.1f}%)"
        )
