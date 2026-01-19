#!/usr/bin/env python3
"""
Import test for pyprofiler package
Run this to verify all modules can be imported without errors
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all imports"""
    print("Testing imports...")

    try:
        from profiler import CPUProfiler, MemoryProfiler
        print("✓ profiler module imported successfully")

        from profiler.models import CallFrame, FunctionStats, ProfilerStats
        print("✓ profiler.models imported successfully")

        from profiler.utils import Timer, StackTrace
        print("✓ profiler.utils imported successfully")

        from profiler.reporters import ConsoleReporter, FlameGraphReporter
        print("✓ profiler.reporters imported successfully")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
