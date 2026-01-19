"""
Flame graph generation example
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pyprofiler import CPUProfiler
from pyprofiler.reporters.flamegraph import FlameGraphReporter


def fibonacci(n: int) -> int:
    """Calculate fibonacci number (recursive, inefficient)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_data():
    """Process some data"""
    result = 0
    for i in range(100):
        result += fibonacci(10)
    return result


def main():
    """Main function"""
    print("Starting flame graph example...\n")

    # Create profiler
    profiler = CPUProfiler()

    # Profile code
    with profiler.profile():
        for _ in range(5):
            process_data()

    # Generate flame graph
    stats = profiler.get_stats()
    reporter = FlameGraphReporter()

    # Generate JSON
    reporter.report(stats, output='flamegraph.json')

    # Generate HTML
    reporter.generate_html(stats, output='flamegraph.html')

    print("\nFlame graphs generated!")
    print("  - flamegraph.json (Chrome DevTools format)")
    print("  - flamegraph.html (standalone viewer)")


if __name__ == "__main__":
    main()
