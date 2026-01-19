"""
Sample script for testing profiler
This simulates a real workload without profiler decorators
"""


def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_data():
    """Process some data"""
    result = []
    for i in range(1000):
        result.append(i ** 2)
    return sum(result)


def calculate_stats():
    """Calculate some statistics"""
    data = list(range(10000))
    return sum(data) / len(data)


def main():
    """Main function"""
    print("Running sample workload...")

    # Some heavy computation
    for _ in range(5):
        process_data()

    # Fibonacci calculation
    fib_result = fibonacci(20)

    # Stats calculation
    stats = calculate_stats()

    print(f"Fibonacci(20) = {fib_result}")
    print(f"Average = {stats}")


if __name__ == '__main__':
    main()
