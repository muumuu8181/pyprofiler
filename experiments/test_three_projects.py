#!/usr/bin/env python3
"""
プロファイラー検証スクリプト - 3つのプロジェクトをプロファイリング

対象プロジェクト:
1. workflow-engine (159_workflow-engine)
2. load-balancer (161_load-balancer)
3. task-scheduler (268_task-scheduler)
"""

import sys
import os
from pathlib import Path

# プロファイラーのパスを追加
profiler_path = Path(__file__).parent / "src"
sys.path.insert(0, str(profiler_path))

from pyprofiler.profiler import CPUProfiler


def simulate_workflow_engine():
    """workflow-engineのシミュレーション"""
    print("\n" + "=" * 60)
    print("Project 1: Workflow Engine Simulation")
    print("=" * 60)

    # DAG操作のシミュレーション
    import time
    import random

    def validate_dag():
        """DAGバリデーション"""
        time.sleep(0.01)  # 擬似的な処理時間
        # 循環依存チェック
        for _ in range(100):
            _ = hash(random.random())

    def parse_workflow():
        """ワークフローパース"""
        time.sleep(0.005)
        # YAMLパースのシミュレーション
        for _ in range(50):
            _ = hash(random.random())

    def schedule_tasks():
        """タスクスケジューリング"""
        time.sleep(0.008)
        # 依存関係解決のシミュレーション
        for _ in range(200):
            _ = hash(random.random())

    def execute_task():
        """タスク実行"""
        time.sleep(0.02)
        # タスク実行のシミュレーション
        for _ in range(500):
            _ = hash(random.random())

    # プロファイラーで計測
    profiler = CPUProfiler()
    profiler.start()

    # ワークフロー処理シミュレーション
    for _ in range(10):
        validate_dag()
        parse_workflow()
        schedule_tasks()
        execute_task()

    profiler.stop()

    # 結果表示
    profiler.print_stats(top_n=5)

    return profiler


def simulate_load_balancer():
    """load-balancerのシミュレーション"""
    print("\n" + "=" * 60)
    print("Project 2: Load Balancer Simulation")
    print("=" * 60)

    import time
    import random

    def round_robin_selection(servers):
        """ラウンドロビン方式のサーバー選択"""
        time.sleep(0.001)
        idx = random.randint(0, len(servers) - 1)
        return servers[idx]

    def weighted_selection(servers, weights):
        """重み付けサーバー選択"""
        time.sleep(0.002)
        # 重み計算のシミュレーション
        total_weight = sum(weights)
        for _ in range(100):
            _ = hash(random.random() * total_weight)
        return random.choice(servers)

    def health_check(server):
        """ヘルスチェック"""
        time.sleep(0.005)
        # ヘルスチェック処理のシミュレーション
        for _ in range(200):
            _ = hash(random.random())
        return True

    def route_request(request):
        """リクエストルーティング"""
        time.sleep(0.003)
        # ルーティング処理のシミュレーション
        for _ in range(150):
            _ = hash(random.random())
        return "routed"

    # プロファイラーで計測
    profiler = CPUProfiler()
    profiler.start()

    servers = ["server1", "server2", "server3", "server4"]
    weights = [1, 2, 3, 4]

    # 負荷分散処理シミュレーション
    for _ in range(100):
        server = round_robin_selection(servers)
        health_check(server)
        weighted_selection(servers, weights)
        route_request(f"request_{_}")

    profiler.stop()

    # 結果表示
    profiler.print_stats(top_n=5)

    return profiler


def simulate_task_scheduler():
    """task-schedulerのシミュレーション"""
    print("\n" + "=" * 60)
    print("Project 3: Task Scheduler Simulation")
    print("=" * 60)

    import time
    import random

    def parse_cron_expression(cron_expr):
        """cron式のパース"""
        time.sleep(0.002)
        # cronパースのシミュレーション
        parts = cron_expr.split()
        for _ in range(50):
            _ = hash(random.random())
        return parts

    def check_dependencies(task, tasks):
        """タスク依存関係チェック"""
        time.sleep(0.005)
        # 依存関係解決のシミュレーション
        for _ in range(300):
            _ = hash(random.random())
        return True

    def execute_task(task):
        """タスク実行"""
        time.sleep(0.015)
        # タスク実行のシミュレーション
        for _ in range(400):
            _ = hash(random.random())
        return True

    def update_task_history(task, status):
        """タスク履歴更新"""
        time.sleep(0.003)
        # 履歴更新のシミュレーション
        for _ in range(100):
            _ = hash(random.random())

    # プロファイラーで計測
    profiler = CPUProfiler()
    profiler.start()

    # タスクスケジューリング処理シミュレーション
    tasks = [
        {"name": "backup", "cron": "0 2 * * *"},
        {"name": "cleanup", "cron": "0 3 * * *"},
        {"name": "update", "cron": "*/30 * * * *"},
    ]

    for _ in range(50):
        for task in tasks:
            parse_cron_expression(task["cron"])
            check_dependencies(task, tasks)
            execute_task(task)
            update_task_history(task, "completed")

    profiler.stop()

    # 結果表示
    profiler.print_stats(top_n=5)

    return profiler


def main():
    """メイン処理"""
    print("\n" + "=" * 60)
    print("プロファイラー検証 - 3プロジェクト")
    print("=" * 60)

    results = {}

    # プロジェクト1: Workflow Engine
    print("\n[1/3] Workflow Engine プロファイリング中...")
    results["workflow_engine"] = simulate_workflow_engine()

    # プロジェクト2: Load Balancer
    print("\n[2/3] Load Balancer プロファイリング中...")
    results["load_balancer"] = simulate_load_balancer()

    # プロジェクト3: Task Scheduler
    print("\n[3/3] Task Scheduler プロファイリング中...")
    results["task_scheduler"] = simulate_task_scheduler()

    # まとめ
    print("\n" + "=" * 60)
    print("サマリー")
    print("=" * 60)

    for name, profiler in results.items():
        stats = profiler.get_stats()
        if stats:
            print(f"\n{name}:")
            print(f"  Total time: {stats.total_time:.6f}s")
            print(f"  Functions profiled: {len(stats.function_stats)}")
            print(f"  Top function: {stats.function_list[0].name if stats.function_list else 'N/A'}")

    print("\n" + "=" * 60)
    print("プロファイリング完了！")
    print("=" * 60)


if __name__ == "__main__":
    main()
