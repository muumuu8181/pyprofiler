"""
Real-world workload baseline (no profiler)
Simulates actual user data processing
"""
import time


def fetch_user_from_db(user_id: int) -> dict:
    """Simulate fetching user from database"""
    time.sleep(0.001)  # 1ms per query
    return {
        'id': user_id,
        'name': f'User{user_id}',
        'email': f'user{user_id}@example.com'
    }


def process_user_data(user_data: dict) -> dict:
    """Simulate processing user data"""
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
        time.sleep(0.0005)  # 0.5ms per notification
        count += 1
    return count


def main():
    """Main application - user data processing pipeline"""
    user_ids = list(range(100))

    # Fetch all users
    user_data_list = [fetch_user_from_db(uid) for uid in user_ids]

    # Process all users
    results = {ud['id']: process_user_data(ud) for ud in user_data_list}

    # Calculate analytics
    analytics = calculate_analytics(results)

    # Send notifications
    notifications_sent = send_notifications(results)

    return analytics, notifications_sent


if __name__ == "__main__":
    start = time.perf_counter()
    analytics, notifications_sent = main()
    elapsed = time.perf_counter() - start

    print(f"Processing complete:")
    print(f"  - Processed: {analytics['total_users']} users")
    print(f"  - Active: {analytics['active_users']} users")
    print(f"  - Notifications sent: {notifications_sent}")
    print(f"  - Total time: {elapsed:.4f} seconds")
