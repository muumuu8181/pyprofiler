"""
Console reporter for profiling statistics
"""
from typing import Optional

from ..models import ProfilerStats


class ConsoleReporter:
    """Reporter for console output"""

    def __init__(self, top_n: int = 10, sort_by: str = 'total'):
        """
        Initialize console reporter

        Args:
            top_n: Number of top functions to display
            sort_by: Sort by 'total', 'own', 'calls', or 'name'
        """
        self.top_n = top_n
        self.sort_by = sort_by

    def report(self, stats: ProfilerStats, output: Optional[str] = None) -> None:
        """
        Generate console report

        Args:
            stats: Profiler statistics to report
            output: Optional file path to write report to
        """
        lines = self._generate_report(stats)

        if output:
            with open(output, 'w') as f:
                f.write('\n'.join(lines))
        else:
            print('\n'.join(lines))

    def _generate_report(self, stats: ProfilerStats) -> list:
        """Generate report lines"""
        lines = [
            "",
            "=" * 80,
            "CPU Profiling Report",
            "=" * 80,
            f"Total time: {stats.total_time:.6f}s",
            "",
            f"{'Function':<30} {'Calls':<10} {'Total(s)':<12} {'Own(s)':<12} {'%'}",
            "-" * 80
        ]

        # Sort functions based on sort_by
        functions = list(stats.function_stats.values())
        if self.sort_by == 'total':
            functions.sort(key=lambda x: x.total_time, reverse=True)
        elif self.sort_by == 'own':
            functions.sort(key=lambda x: x.own_time, reverse=True)
        elif self.sort_by == 'calls':
            functions.sort(key=lambda x: x.call_count, reverse=True)
        elif self.sort_by == 'name':
            functions.sort(key=lambda x: x.name)

        # Add top N functions
        for func_stats in functions[:self.top_n]:
            lines.append(
                f"{func_stats.name:<30} "
                f"{func_stats.call_count:<10} "
                f"{func_stats.total_time:<12.6f} "
                f"{func_stats.own_time:<12.6f} "
                f"{func_stats.percentage:>6.1f}%"
            )

        lines.extend([
            "-" * 80,
            ""
        ])

        return lines


__all__ = ['ConsoleReporter']
