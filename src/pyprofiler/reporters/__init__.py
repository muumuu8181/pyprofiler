"""
Reporters for outputting profiling results
"""
from .console import ConsoleReporter
from .flamegraph import FlameGraphReporter

__all__ = ['ConsoleReporter', 'FlameGraphReporter']
