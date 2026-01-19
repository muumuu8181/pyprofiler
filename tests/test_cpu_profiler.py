"""
Tests for CPU profiler
"""
import sys
from pathlib import Path

# Add src to path (for local development only)
# When package is installed, this is not needed
src_path = Path(__file__).parent.parent / "src"
if not (src_path / "pyprofiler").exists():
    sys.path.insert(0, str(src_path))

# Use installed package
try:
    from pyprofiler import CPUProfiler
except ImportError:
    # Fallback to local import
    from profiler import CPUProfiler

from tests.fixtures.sample_code import heavy_computation, light_computation


def test_profiler_decorator():
    """Test profiling with decorator"""
    profiler = CPUProfiler()
    profiler.start()

    @profiler.profile_function
    def test_function():
        return heavy_computation()

    result = test_function()

    profiler.stop()
    stats = profiler.get_stats()

    assert stats is not None
    assert 'test_function' in stats.function_stats
    assert stats.function_stats['test_function'].call_count == 1
    print("✓ Decorator test passed")


def test_profiler_context_manager():
    """Test profiling with context manager"""
    profiler = CPUProfiler()

    @profiler.profile_function
    def heavy_func():
        return heavy_computation()

    @profiler.profile_function
    def light_func():
        return light_computation()

    with profiler.profile():
        heavy_func()
        light_func()

    stats = profiler.get_stats()

    assert stats is not None
    assert len(stats.function_stats) > 0
    print("✓ Context manager test passed")


def test_profiler_multiple_calls():
    """Test profiling with multiple function calls"""
    profiler = CPUProfiler()
    profiler.start()

    @profiler.profile_function
    def test_function():
        return light_computation()

    for _ in range(10):
        test_function()

    profiler.stop()
    stats = profiler.get_stats()

    assert stats is not None
    assert stats.function_stats['test_function'].call_count == 10
    print("✓ Multiple calls test passed")


def test_profiler_stats():
    """Test profiler statistics accuracy"""
    profiler = CPUProfiler()
    profiler.start()

    @profiler.profile_function
    def test_func():
        return heavy_computation()

    for _ in range(3):
        test_func()

    profiler.stop()
    stats = profiler.get_stats()

    assert stats is not None
    assert stats.total_time > 0
    assert 'test_func' in stats.function_stats
    assert stats.function_stats['test_func'].call_count == 3
    print("✓ Stats accuracy test passed")


def run_all_tests():
    """Run all tests"""
    print("Running CPU profiler tests...\n")

    test_profiler_decorator()
    test_profiler_context_manager()
    test_profiler_multiple_calls()
    test_profiler_stats()

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()
