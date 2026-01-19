"""
Command-line interface for pyprofiler

Usage:
    python -m pyprofiler script.py
    python -m pyprofiler -o output.stats script.py
    python -m pyprofiler --no-auto-save script.py  # Disable auto-save
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description='Profile Python code',
        usage='python -m pyprofiler [-o output_file] [--no-auto-save] script.py [args]'
    )

    parser.add_argument(
        '-o', '--outfile',
        help='Output file for statistics (default: auto-generated with timestamp)'
    )

    parser.add_argument(
        '--no-auto-save',
        action='store_true',
        help='Disable automatic saving of profiling results'
    )

    parser.add_argument(
        '-s', '--sort',
        default='cumulative',
        choices=['cumulative', 'time', 'calls', 'name'],
        help='Sort column (default: cumulative)'
    )

    parser.add_argument(
        'script',
        help='Python script to profile'
    )

    parser.add_argument(
        'script_args',
        nargs=argparse.REMAINDER,
        help='Arguments to pass to the script'
    )

    args = parser.parse_args()

    # Check if script exists
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Error: Script '{args.script}' not found", file=sys.stderr)
        sys.exit(1)

    # Read the script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_code = f.read()

    # Prepare the execution context
    script_globals = {
        '__name__': '__main__',
        '__file__': str(script_path.absolute()),
        '__package__': None,
        '__cached__': None,
        '__builtins__': __builtins__,
    }

    # Update sys.argv for the script
    old_argv = sys.argv
    sys.argv = [args.script] + args.script_args

    try:
        # Import and run profiler
        import runpy
        from . import CPUProfiler

        print(f"Profiling {args.script}...")
        print("=" * 60)

        # Set up profiling hook
        profiler = CPUProfiler()

        def profile_hook(frame, event, arg):
            func_name = frame.f_code.co_name
            filename_local = frame.f_code.co_filename

            # Skip profiler internals and Python internals
            skip_conditions = [
                'pyprofiler' in filename_local,
                'site-packages' in filename_local,
                'lib/python' in filename_local.replace('\\', '/'),
                func_name.startswith('_'),
                func_name in ['<module>', '<listcomp>', '<dictcomp>', '<setcomp>', '<genexpr>'],
                # Import-related functions
                func_name in ['exec_module', 'get_code', 'compile', 'get_data', 'parse',
                             'find_spec', 'create_module', 'module_from_spec', 'get',
                             'acquire', 'cache_from_source'],
                # Internal modules
                '_bootstrap' in filename_local,
                '_imp' in filename_local,
            ]

            if any(skip_conditions):
                return

            if event == 'call':
                profiler._call_counts[func_name] = profiler._call_counts.get(func_name, 0) + 1
                profiler._call_start_times = {}
                profiler._call_start_times[func_name] = profiler._timer.get_time()
            elif event == 'return':
                start_time = profiler._call_start_times.pop(func_name, None)
                if start_time is not None:
                    elapsed = profiler._timer.get_time() - start_time
                    if func_name not in profiler._function_times:
                        profiler._function_times[func_name] = []
                    profiler._function_times[func_name].append(elapsed)

        # Install profiling hook before running script
        sys.setprofile(profile_hook)
        profiler.start()

        try:
            # Run the script using runpy (this supports relative imports)
            runpy.run_path(args.script, run_name='__main__')
        finally:
            sys.setprofile(None)
            profiler.stop()

        # Print results
        print()
        profiler.print_stats(top_n=20)
        def profile_hook(frame, event, arg):
            if event == 'call':
                func_name = frame.f_code.co_name
                filename_local = frame.f_code.co_filename

                # Skip profiler internals and stdlib
                if 'pyprofiler' in filename_local:
                    return

                profiler._call_counts[func_name] = profiler._call_counts.get(func_name, 0) + 1
                profiler._function_times.setdefault(func_name, [])

            elif event == 'return':
                func_name = frame.f_code.co_name
                filename_local = frame.f_code.co_filename

                if 'pyprofiler' in filename_local:
                    return

                # Record elapsed time
                if hasattr(profiler, '_call_start_times'):
                    start_time = profiler._call_start_times.pop(func_name, None)
                    if start_time is not None:
                        elapsed = profiler._timer.get_time() - start_time
                        if func_name in profiler._function_times:
                            profiler._function_times[func_name].append(elapsed)

        profiler.start()
        profiler._call_start_times = {}

        # Override the event handler to track timing properly
        original_hook = profile_hook

        def profile_hook_with_timing(frame, event, arg):
            func_name = frame.f_code.co_name
            filename_local = frame.f_code.co_filename

            # Skip profiler internals and Python internals
            skip_conditions = [
                'pyprofiler' in filename_local,
                'site-packages' in filename_local,
                'lib/python' in filename_local.replace('\\', '/'),
                func_name.startswith('_'),
                func_name in ['<module>', '<listcomp>', '<dictcomp>', '<setcomp>', '<genexpr>'],
                # Import-related functions
                func_name in ['exec_module', 'get_code', 'compile', 'get_data', 'parse',
                             'find_spec', 'create_module', 'module_from_spec', 'get',
                             'acquire', 'cache_from_source'],
                # Internal modules
                '_bootstrap' in filename_local,
                '_imp' in filename_local,
            ]

            if any(skip_conditions):
                return

            if event == 'call':
                profiler._call_counts[func_name] = profiler._call_counts.get(func_name, 0) + 1
                profiler._call_start_times[func_name] = profiler._timer.get_time()
            elif event == 'return':
                start_time = profiler._call_start_times.pop(func_name, None)
                if start_time is not None:
                    elapsed = profiler._timer.get_time() - start_time
                    if func_name not in profiler._function_times:
                        profiler._function_times[func_name] = []
                    profiler._function_times[func_name].append(elapsed)

        sys.setprofile(profile_hook_with_timing)

        try:
            exec(script_code, script_globals)
        finally:
            sys.setprofile(None)
            profiler.stop()

        # Print results
        print()
        profiler.print_stats(top_n=20)

        # Auto-save statistics (unless --no-auto-save is specified)
        if not args.no_auto_save:
            import pickle

            # Determine output filename
            if args.outfile:
                outfile = args.outfile
            else:
                # Auto-generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                script_name = script_path.stem
                outfile = f"profile_{script_name}_{timestamp}.stats"

            # Save statistics
            stats = profiler.get_stats()
            with open(outfile, 'wb') as f:
                pickle.dump(stats, f)
            print(f"\n[*] Statistics saved to {outfile}")

            # Also save a human-readable text report
            txt_report = outfile.replace('.stats', '.txt')
            with open(txt_report, 'w', encoding='utf-8') as f:
                f.write(f"Profiling Report: {args.script}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Time: {stats.total_time:.4f}s\n")
                f.write(f"Functions Profiled: {len(stats.function_stats)}\n")
                f.write("=" * 80 + "\n\n")

                # Write top functions
                f.write(f"{'Function':<30} {'Calls':<10} {'Total(s)':<12} {'Own(s)':<12} {'%'}\n")
                f.write("-" * 80 + "\n")

                for func_stats in stats.get_top_functions(20):
                    f.write(
                        f"{func_stats.name:<30} "
                        f"{func_stats.call_count:<10} "
                        f"{func_stats.total_time:<12.6f} "
                        f"{func_stats.own_time:<12.6f} "
                        f"{func_stats.percentage:>6.1f}%\n"
                    )

            print(f"[*] Text report saved to {txt_report}")

    except FileNotFoundError:
        print(f"Error: Script '{args.script}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        sys.argv = old_argv


if __name__ == '__main__':
    main()
