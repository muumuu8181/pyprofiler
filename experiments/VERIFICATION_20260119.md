# ドキュメント検証結果

**検証日**: 2026-01-19

---

## 検証概要

ドキュメントに記載されている使用例が実際に動作するかを検証しました。

---

## 結果サマリー

| 項目 | 状態 | 問題 |
|------|------|------|
| README.mdのインポート例 | ❌ | 古いパスのまま |
| `pyprofiler.run()` 使用例 | ✅ | 正常に動作 |
| `python -m pyprofiler` CLI | ⚠️ | 動作するが出力が重複 |
| examples/simple_profile.py | ❌ | インポートエラー |
| examples/flamegraph_example.py | ❌ | インポートエラー |
| examples/memory_profile.py | ✅ | 動作するがメモリ計測が0 |
| experiments/verify_improvement.py | ✅ | 正常に動作 |

---

## 詳細な検証結果

### 1. README.md の使用例

#### 問題: インポートパスが古い

**記載されているコード**:
```python
from profiler import CPUProfiler
```

**実際のエラー**:
```python
Traceback (most recent call last):
  File "...", line 11, in <module>
    from profiler import CPUProfiler
  File ".../src/profiler.py", line 7, in <module>
    from .models import ProfilerStats
ImportError: attempted relative import with no known parent package
```

**正しいコード**:
```python
from pyprofiler import CPUProfiler
```

→ **既に修正済み（2026-01-19）**

---

### 2. `pyprofiler.run()` の使用例

**記載されているコード**:
```python
import pyprofiler

pyprofiler.run('''
def my_function():
    result = sum(range(10000))
    return result

my_function()
''')
```

**検証結果**: ✅ **正常に動作**

**実行例** (experiments/verify_improvement.py):
```
BEFORE: Using filter + lambda (slow)
Function                       Calls      Total(s)     Own(s)       %
filter_method                  5          0.018758     0.018758       97.7%

AFTER: Using list comprehension (fast)
list_comp_method               5          0.000349     0.000349       63.7%
```

---

### 3. `python -m pyprofiler` CLI

**記載されている使用例**:
```bash
python -m pyprofiler my_script.py
```

**検証結果**: ⚠️ **動作するが問題あり**

#### 問題1: 出力が重複する

__main__.py に重複したコードがあるため、同じ処理が2回実行されています。

**原因**: `src/pyprofiler/__main__.py` の行124-210で、同じプロファイリング処理が2回記述されている

**実際の出力**:
```
Profiling experiments/verify_improvement.py...
============================================================
（1回目の出力）

Function                       Calls      Total(s)     Own(s)       %
popitem                        2          0.001100     0.001100        4.2%
...
================================================================================
BEFORE: Using filter + lambda (slow)
================================================================================
（2回目の出力 - 重複）
```

---

### 4. examples/simple_profile.py

**記載されているコード**:
```python
from profiler import CPUProfiler
from reporters import ConsoleReporter
```

**実際のエラー**:
```
ImportError: attempted relative import with no known parent package
```

**正しいコード**:
```python
from pyprofiler import CPUProfiler
from pyprofiler.reporters.console import ConsoleReporter
```

→ **修正が必要**

---

### 5. examples/flamegraph_example.py

**記載されているコード**:
```python
from profiler import CPUProfiler
from reporters import FlameGraphReporter
```

**実際のエラー**:
```
ImportError: attempted relative import with no known parent package
```

**正しいコード**:
```python
from pyprofiler import CPUProfiler
from pyprofiler.reporters.flamegraph import FlameGraphReporter
```

→ **修正が必要**

---

### 6. examples/memory_profile.py

**記載されているコード**:
```python
from memory_profiler import MemoryProfiler
```

**検証結果**: ✅ **動作する**

**実際の出力**:
```
Starting memory profiling example...
Allocating memory...

Memory Statistics:
  Initial: 0 bytes
  Final: 0 bytes
  Growth: +0 bytes

Top object types:
```

**問題**: メモリ計測が0バイトのまま（実装が不十分？）

---

## 改善が必要な箇所

### 優先度高

| ファイル | 問題 | 修正内容 |
|---------|------|----------|
| `examples/simple_profile.py` | 古いインポートパス | `from pyprofiler import CPUProfiler` に修正 |
| `examples/flamegraph_example.py` | 古いインポートパス | `from pyprofiler import CPUProfiler` に修正 |
| `src/pyprofiler/__main__.py` | 重複したコード | 行136-210の重複部分を削除 |

### 優先中

| ファイル | 問題 | 検討事項 |
|---------|------|----------|
| `examples/memory_profile.py` | メモリ計測が0 | MemoryProfilerの実装を確認 |

---

## 結論

1. **README.md**: 修正済み（インポートパス）
2. **基本機能 (`pyprofiler.run()`)**: 正常に動作
3. **CLI (`python -m pyprofiler`)**: 動作するが出力重複の問題あり
4. **サンプルコード (`examples/`)**: 全て古いインポートパスを使用しているため動作しない

**推奨アクション**:
- examples/ のサンプルコードを修正して、実際に動く状態にする
- __main__.py の重複コードを削除
