"""
Sample code for profiling tests
"""
import time


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


def mixed_workload():
    """Mix of light and heavy computations"""
    for _ in range(5):
        light_computation()

    for _ in range(3):
        heavy_computation()


def sleep_function():
    """Sleep for a short time"""
    time.sleep(0.01)


def sample_function():
    """Sample function combining different operations"""
    heavy_computation()
    light_computation()
    fibonacci(10)
    sleep_function()
