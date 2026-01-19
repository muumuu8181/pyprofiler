# Pythonプロファイラー

> **プロジェクト番号**: #27
> **提案元**: GLM
> **品質目標**: 30点（MVP）→ 65点（実用）→ 90点（市販品レベル）

Pythonコードの性能ボトルネックを可視化・分析するプロファイラーをスクラッチ実装

---

## 🎯 特徴

- **CPUプロファイリング**: 関数呼び出しの回数・実行時間を計測
- **メモリプロファイリング**: メモリ割り当て・リークを検出
- **フレームグラフ生成**: 実行パスを可視化（Chrome DevTools互換）
- **低オーバーヘッド**: 計測による性能劣化を最小限
- **CUIベース**: 使いやすいコマンドラインインターフェース

---

## 🚀 クイックスタート

### インストール

```bash
cd task04_glm-idea_no027_profiler
pip install -r requirements.txt
```

### 基本的な使用方法

```python
from pyprofiler import CPUProfiler

# プロファイラーを作成
profiler = CPUProfiler()

# 関数をプロファイル
@profiler.profile_function
def my_function():
    # 計測したい処理
    result = sum(range(1000))
    return result

# 実行
my_function()

# 結果を表示
profiler.print_stats()
```

### コンテキストマネージャーを使用

```python
from pyprofiler import CPUProfiler

profiler = CPUProfiler()

with profiler.profile():
    # 計測したいコードブロック
    for i in range(100):
        heavy_computation()

# 統計を表示
profiler.print_stats()
```

### コード修正なしでプロファイリング（推奨）

**既存のスクリプトをコード修正なしでプロファイリングできます。**

#### 方法1: コマンドラインから実行

```bash
# スクリプトをプロファイリング
python -m pyprofiler my_script.py

# 統計情報をファイルに保存
python -m pyprofiler -o output.stats my_script.py
```

#### 方法2: Pythonコードから実行

```python
import pyprofiler

# 文字列としてコードを実行してプロファイリング
pyprofiler.run('''
def my_function():
    result = sum(range(10000))
    return result

my_function()
''')

# 結果は自動的に表示されます
```

#### 方法3: cProfile互換の使い方

```python
import pyprofiler

# cProfileと同じ使い方
pyprofiler.run('my_function()')
pyprofiler.run('import math; math.factorial(10000)')
```

### フレームグラフの生成

```python
from pyprofiler import CPUProfiler
from pyprofiler.reporters.flamegraph import FlameGraphGenerator

profiler = CPUProfiler()

# プロファイリング実行
with profiler.profile():
    my_application()

# フレームグラフを生成
generator = FlameGraphGenerator()
graph = generator.generate(profiler.call_stack)

# HTMLで出力
generator.to_html(graph, 'flamegraph.html')
```

### メモリプロファイリング

```python
from pyprofiler import MemoryProfiler

# プロファイラーを作成
profiler = MemoryProfiler()

# プロファイリング開始
profiler.start()

# メモリを割り当てる処理
data = allocate_memory()
process_data(data)

# プロファイリング終了
profiler.stop()

# 結果を表示
profiler.print_stats()
```

**出力例**:
```
Memory Statistics:
  Initial: 0 bytes (0.00 KB)
  Final:   862,552 bytes (842.34 KB)
  Growth:  +862,552 bytes (+842.34 KB)

Top 10 memory allocations:
  examples/memory_profile.py:18: size=841 KiB, count=1930, average=446 B
  examples/memory_profile.py:26: size=864 B, count=1, average=864 B
```

---

## 📊 出力例

### コンソール出力

```
Function                    Calls    Total(s)   Own(s)   %
---------------------------------------------------------------
main                        1        5.234      0.001    100.0%
  └─process_data           10       5.200      0.500    99.4%
      └─parse_line         1000     4.500      4.500    86.0%
      └─validate_data       1000     0.200      0.200    3.8%
  └─save_results            1        0.033      0.033    0.6%
---------------------------------------------------------------
```

### フレームグラフ

Chrome DevToolsで開けるインタラクティブなフレームグラフを生成

---

## 🛠️ 開発

### 依存パッケージ

```bash
pip install -r requirements.txt
```

### テストの実行

```bash
pytest tests/
```

### サンプルコードの実行

```bash
# 基本的なプロファイリング
python examples/simple_profile.py

# フレームグラフ生成
python examples/flamegraph_example.py

# メモリプロファイリング
python examples/memory_profile.py
```

---

## 📚 ドキュメント

- [仕様書](docs/design.md) - 詳細な仕様とアーキテクチャ
- [実装計画](docs/implementation_plan.md) - 開発ロードマップ
- [APIドキュメント](docs/api.md) - APIリファレンス

---

## 🎯 品質目標

| スコア | レベル | 説明 | 達成基準 |
|--------|--------|------|----------|
| **30点** | MVP | 基本機能が動く | 簡単なスクリプトのプロファイリングができる |
| **65点** | 実用 | 実用的に使える | 実務のプロジェクトで使える |
| **90点** | 市販品 | 市販品レベル | cProfile, py-spyと同等の機能 |

---

## 📝 作業ログ

詳細な開発ログは [logs/development_log.md](logs/development_log.md) を参照

---

## 🙏 謝辞

本プロジェクトは以下の既存プロファイラーにインスパイアされています：

- cProfile (Python標準)
- py-spy (サンプリングプロファイラー)
- memory_profiler (メモリプロファイラー)

---

**作成者**: Claude (Sonnet 4.5)
**最終更新**: 2026-01-18
