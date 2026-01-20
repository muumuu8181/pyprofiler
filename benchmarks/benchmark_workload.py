"""
Benchmark workload for profiler comparison
This simulates realistic Python code with various function call patterns
"""
import time
import random
from typing import List, Dict


def fibonacci(n: int) -> int:
    """Recursive fibonacci (many function calls)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_list(n: int) -> List[int]:
    """List processing (moderate function calls)"""
    result = []
    for i in range(n):
        result.append(i ** 2)
    return result


def dict_operations(n: int) -> Dict[str, int]:
    """Dictionary operations (moderate function calls)"""
    result = {}
    for i in range(n):
        result[f"key_{i}"] = i * 2
    return result


def string_operations(n: int) -> str:
    """String operations (moderate function calls)"""
    parts = []
    for i in range(n):
        parts.append(f"item_{i}")
    return ",".join(parts)


def mathematical_heavy():
    """Heavy mathematical computation"""
    total = 0
    for i in range(1000):
        total += i ** 2 + i ** 3
    return total


def light_io_simulation():
    """Simulate light I/O operations"""
    result = []
    for i in range(10):
        result.append(i)
    return result


def mixed_workload():
    """Mixed workload combining all operations"""
    # Fibonacci: many recursive calls
    fibonacci(15)

    # List processing
    process_list(1000)

    # Dict operations
    dict_operations(100)

    # String operations
    string_operations(50)

    # Mathematical computation
    mathematical_heavy()

    # Light I/O
    light_io_simulation()


def main(iterations: int = 10):
    """Main benchmark function"""
    for i in range(iterations):
        mixed_workload()


if __name__ == "__main__":
    iterations = 50

    # First run without profiler to get baseline
    print("Running baseline benchmark (no profiler)...")
    start = time.perf_counter()
    main(iterations=iterations)
    baseline_time = time.perf_counter() - start
    print(f"Baseline time: {baseline_time:.4f} seconds\n")

    # Run with profiler
    print("Running with profiler...")
    main(iterations=iterations)
