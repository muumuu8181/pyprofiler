"""
Run profiler comparison benchmark
Compares: No profiler, pyprofiler (Python), py-spy (Rust)
"""
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list, description: str) -> tuple[float, str]:
    """Run a command and return (elapsed_time, output)"""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*70)

    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    elapsed = time.perf_counter() - start

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return elapsed, result.stdout


def main():
    results = {}

    # 1. Baseline: No profiler
    cmd = [sys.executable, "benchmarks/benchmark_workload.py"]
    elapsed, output = run_command(cmd, "Baseline (No Profiler)")
    results["baseline"] = elapsed

    # 2. pyprofiler (Python implementation)
    cmd = [sys.executable, "-m", "pyprofiler", "--no-auto-save", "benchmarks/benchmark_workload.py"]
    elapsed, output = run_command(cmd, "pyprofiler (Python)")
    results["pyprofiler"] = elapsed

    # 3. py-spy (Rust implementation)
    # Use full path on Windows
    import shutil
    py_spy_exe = shutil.which("py-spy") or r"C:\Users\kakar\AppData\Local\Programs\Python\Python313\Scripts\py-spy.exe"
    cmd = [
        py_spy_exe, "record", "-o", "NUL", "-d", "30",
        "--", sys.executable, "benchmarks/benchmark_workload.py"
    ]
    elapsed, output = run_command(cmd, "py-spy (Rust)")
    results["py-spy"] = elapsed

    # Print summary
    print(f"\n{'='*70}")
    print("BENCHMARK RESULTS SUMMARY")
    print('='*70)
    baseline = results["baseline"]
    print(f"{'Method':<20} {'Time (s)':<15} {'Overhead':<15}")
    print('-'*70)

    for method, elapsed_time in results.items():
        overhead_pct = ((elapsed_time - baseline) / baseline) * 100 if baseline > 0 else 0
        print(f"{method:<20} {elapsed_time:<15.4f} {overhead_pct:>14.1f}%")

    print('-'*70)
    print(f"\nBaseline: {baseline:.4f}s")
    print(f"pyprofiler overhead: {((results['pyprofiler'] - baseline) / baseline * 100):.1f}%")
    print(f"py-spy overhead: {((results['py-spy'] - baseline) / baseline * 100):.1f}%")
    print()


if __name__ == "__main__":
    main()
