"""
Simple profiling example
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pyprofiler import CPUProfiler
from pyprofiler.reporters.console import ConsoleReporter


def fibonacci(n: int) -> int:
    """Calculate fibonacci number (recursive, inefficient)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def heavy_computation():
    """Simulate heavy computation"""
    result = 0
    for i in range(1000):
        result += sum(range(100))
    return result


def light_computation():
    """Simulate light computation"""
    return sum(range(10))


def main():
    """Main function"""
    print("Starting profiling example...\n")

    # Create profiler
    profiler = CPUProfiler()

    # Start profiling
    profiler.start()

    # Profile some code
    print("Running code...")
    for _ in range(3):
        heavy_computation()

    for _ in range(10):
        light_computation()

    fibonacci(15)

    # Stop profiling
    profiler.stop()

    # Print statistics
    profiler.print_stats()

    # Alternatively, use console reporter
    print("\n\nUsing ConsoleReporter:")
    stats = profiler.get_stats()
    reporter = ConsoleReporter(top_n=10)
    reporter.report(stats)


if __name__ == "__main__":
    main()
