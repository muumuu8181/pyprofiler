"""
Memory profiling example
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pyprofiler import MemoryProfiler


def allocate_memory():
    """Allocate some memory"""
    data = []
    for i in range(1000):
        data.append([0] * 100)
    return data


def allocate_strings():
    """Allocate string data"""
    strings = []
    for i in range(100):
        strings.append("x" * 1000)
    return strings


def main():
    """Main function"""
    print("Starting memory profiling example...\n")

    # Create memory profiler
    profiler = MemoryProfiler()

    # Start profiling
    profiler.start()

    # Allocate some memory
    print("Allocating memory...")
    data = allocate_memory()
    strings = allocate_strings()

    # Stop profiling
    profiler.stop()

    # Print statistics
    profiler.print_stats()


if __name__ == "__main__":
    main()
