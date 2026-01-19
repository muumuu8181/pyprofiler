"""
Real-world profiling example - Finding performance bottlenecks

This demonstrates the actual use case for a profiler:
finding which functions are slow and need optimization.
"""
import sys
from pathlib import Path

# Use installed package
try:
    from pyprofiler import CPUProfiler
except ImportError:
    # Fallback for local development
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from profiler import CPUProfiler


def process_user_data(user_ids: list) -> dict:
    """Simulate processing user data - this is the slow part"""
    results = {}

    for user_id in user_ids:
        # Simulate database query
        user_data = fetch_user_from_db(user_id)

        # Simulate data processing
        processed = process_user_data(user_data)

        results[user_id] = processed

    return results


def fetch_user_from_db(user_id: int) -> dict:
    """Simulate fetching user from database"""
    # Simulate slow database query
    import time
    time.sleep(0.001)  # 1ms per query

    return {
        'id': user_id,
        'name': f'User{user_id}',
        'email': f'user{user_id}@example.com'
    }


def process_user_data(user_data: dict) -> dict:
    """Simulate processing user data"""
    # Some computation
    result = {**user_data}
    result['processed'] = True
    return result


def calculate_analytics(results: dict) -> dict:
    """Calculate analytics on processed data"""
    analytics = {
        'total_users': len(results),
        'active_users': sum(1 for r in results.values() if r.get('processed', False))
    }
    return analytics


def send_notifications(results: dict) -> int:
    """Send notifications to users"""
    count = 0
    for user_data in results.values():
        # Simulate API call
        import time
        time.sleep(0.0005)  # 0.5ms per notification
        count += 1
    return count


def main():
    """Main application - let's profile it"""
    print("=" * 60)
    print("Performance Profiling Demo")
    print("=" * 60)
    print("\nScenario: Processing 100 users through the pipeline")
    print("Expected bottleneck: Database queries are slow\n")

    # Create profiler
    profiler = CPUProfiler()

    # Profile each function
    @profiler.profile_function
    def fetch_all_users(user_ids):
        """Fetch all users from database"""
        return [fetch_user_from_db(uid) for uid in user_ids]

    @profiler.profile_function
    def process_all_users(user_data_list):
        """Process all user data"""
        return {ud['id']: process_user_data(ud) for ud in user_data_list}

    @profiler.profile_function
    def calc_analytics(results):
        """Calculate analytics"""
        return calculate_analytics(results)

    @profiler_profile_function
    def notify_users(results):
        """Send notifications"""
        return send_notifications(results)

    # Start profiling
    profiler.start()

    # Run the application
    user_ids = list(range(100))

    user_data_list = fetch_all_users(user_ids)
    results = process_all_users(user_data_list)
    analytics = calc_analytics(results)
    notifications_sent = notify_users(results)

    # Stop profiling
    profiler.stop()

    # Show results
    print(f"\n✅ Processing complete:")
    print(f"  - Processed: {analytics['total_users']} users")
    print(f"  - Active: {analytics['active_users']} users")
    print(f"  - Notifications sent: {notifications_sent}")

    # Show profiling results
    print("\n" + "=" * 60)
    print("📊 PROFILING RESULTS")
    print("=" * 60)
    profiler.print_stats()

    print("\n💡 INSIGHTS:")
    print("   The profiler tells us which functions are slow.")
    print("   This helps us know where to optimize:")

    stats = profiler.get_stats()
    if stats:
        # Find the slowest function
        slowest = max(stats.function_stats.values(), key=lambda x: x.total_time)
        print(f"\n   🐌 Bottleneck: '{slowest.name}' takes {slowest.total_time*1000:.1f}ms")
        print(f"      → Optimization target: caching, batching, or async")


# For typing
def profiler_profile_function(func):
    """Temporary workaround - will be fixed in proper implementation"""
    return func


if __name__ == "__main__":
    main()
