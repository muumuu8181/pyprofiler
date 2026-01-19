# Pythonプロファイラー - 仕様書

> **プロジェクト番号**: #27
> **作成日**: 2026-01-18
> **想定行数**: 8,000〜15,000行
> **品質目標**: 30点（MVP）→ 65点（実用）→ 90点（市販品レベル）

---

## 📋 プロジェクト概要

### 目的
Pythonコードの性能ボトルネックを可視化・分析するプロファイラーをスクラッチ実装する

### 特徴
- **CPUプロファイリング**: 関数呼び出しの回数・実行時間を計測
- **メモリプロファイリング**: メモリ割り当て・リークを検出
- **フレームグラフ生成**: 実行パスを可視化
- **低オーバーヘッド**: 計測による性能劣化を最小限に
- **CUIベース**: 使いやすいコマンドラインインターフェース

---

## 🎯 主要機能

### 1. CPUプロファイリング

```
機能:
- 関数ごとの実行時間計測
- 呼び出し回数の記録
- コールグラフの生成
- ホットスポットの特定

出力形式:
- テキストレポート（ターミナル出力）
- フレームグラフ（HTML/JSON）
- CSV（スプレッドシート用）
```

### 2. メモリプロファイリング

```
機能:
- オブジェクトごとのメモリ使用量
- メモリリークの検出
- メモリ割り当てのタイムライン
- ガベージコレクションの監視

出力形式:
- メモリ使用量のサマリー
- オブジェクト別の内訳
- メモリ増加のグラフ
```

### 3. フレームグラフ生成

```
機能:
- 呼び出し階層の可視化
- 実行時間に応じた幅の表示
- インタラクティブなHTML出力
- 色分けによるパスの識別

フォーマット:
- Chrome DevTools互換のJSON
- 独自HTMLビューア（オプション）
```

### 4. 統計的プロファイリング（オプション）

```
機能:
- サンプリングベースの計測
- より低オーバーヘッド
- 一定間隔でのコールスタック取得
```

---

## 🏗️ アーキテクチャ

### 全体構成

```
profiler/
├── src/
│   ├── profiler.py          # メインのプロファイラークラス
│   ├── cpu_profiler.py      # CPUプロファイラー
│   ├── memory_profiler.py   # メモリプロファイラー
│   ├── frame_graph.py       # フレームグラフ生成
│   ├── reporters/           # 出力形式ごとのレポーター
│   │   ├── console.py       # コンソール出力
│   │   ├── flamegraph.py    # フレームグラフ出力
│   │   ├── csv.py           # CSV出力
│   │   └── html.py          # HTML出力
│   ├── samplers/            # サンプラー
│   │   ├── deterministic.py # 決定論的サンプリング
│   │   └── statistical.py   # 統計的サンプリング
│   └── utils/
│       ├── timer.py         # 高精度タイマー
│       └── stack_trace.py   # コールスタック取得
├── tests/
├── examples/
└── docs/
```

### コアコンポーネント

#### 1. Profilerクラス（基底クラス）

```python
class Profiler(ABC):
    """プロファイラーの基底クラス"""

    @abstractmethod
    def start(self):
        """計測開始"""

    @abstractmethod
    def stop(self):
        """計測停止"""

    @abstractmethod
    def get_stats(self) -> ProfilerStats:
        """統計情報を取得"""
```

#### 2. CPUProfilerクラス

```python
class CPUProfiler(Profiler):
    """CPUプロファイラー"""

    def __init__(self, interval: float = 0.001):
        self.interval = interval  # サンプリング間隔
        self.call_stack = []      # 呼び出しスタック
        self.function_stats = {}  # 関数ごとの統計

    def profile_function(self, func):
        """デコレーターとして関数をプロファイル"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = self._get_time()
            result = func(*args, **kwargs)
            end_time = self._get_time()
            self._record_function(func.__name__, start_time, end_time)
            return result
        return wrapper
```

#### 3. MemoryProfilerクラス

```python
class MemoryProfiler(Profiler):
    """メモリプロファイラー"""

    def __init__(self):
        self.memory_snapshots = []  # メモリスナップショット
        self.object_tracker = {}     # オブジェクト追跡

    def track_object(self, obj):
        """オブジェクトを追跡"""
        obj_id = id(obj)
        size = sys.getsizeof(obj)
        self.object_tracker[obj_id] = {
            'type': type(obj).__name__,
            'size': size,
            'created_at': self._get_time()
        }
```

#### 4. FlameGraphGeneratorクラス

```python
class FlameGraphGenerator:
    """フレームグラフ生成器"""

    def generate(self, call_stack: List[CallFrame]) -> FlameGraph:
        """コールスタックからフレームグラフを生成"""
        root = FlameGraphNode(name="root", value=0)

        for frame in call_stack:
            self._insert_frame(root, frame)

        return FlameGraph(root=root)

    def to_json(self, graph: FlameGraph) -> str:
        """Chrome DevTools互換のJSONを出力"""

    def to_html(self, graph: FlameGraph) -> str:
        """インタラクティブなHTMLを出力"""
```

---

## 📊 データ構造

### CallFrame（呼び出しフレーム）

```python
@dataclass
class CallFrame:
    """関数呼び出しフレーム"""
    name: str              # 関数名
    filename: str          # ファイル名
    line_no: int           # 行番号
    start_time: float      # 開始時刻
    end_time: float        # 終了時刻
    children: List['CallFrame'] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """実行時間"""
        return self.end_time - self.start_time
```

### ProfilerStats（統計情報）

```python
@dataclass
class ProfilerStats:
    """プロファイリング統計"""
    total_time: float              # 合計実行時間
    function_stats: Dict[str, FunctionStats]  # 関数ごとの統計

@dataclass
class FunctionStats:
    """関数ごとの統計"""
    name: str
    call_count: int                # 呼び出し回数
    total_time: float              # 合計実行時間
    avg_time: float                # 平均実行時間
    own_time: float                # 自身の実行時間（子呼び出しを除く）
    percentage: float              # 合計時間に占める割合
```

---

## 🎨 出力形式

### 1. コンソール出力

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

### 2. フレームグラフ（HTML）

```
+------------------+
|     main         |
+------------------+
|  process_data   |
+----------------+
|parse|validate  |
+----------------+
```

### 3. CSV出力

```csv
function_name,filename,line_no,call_count,total_time,own_time,percentage
main,main.py,10,1,5.234,0.001,100.0
process_data,main.py,15,10,5.200,0.500,99.4
```

---

## 🔧 実装の優先順位

### Phase 1: 基本機能（30点目標）

```
✓ CPUプロファイリングの基本実装
  - 関数の実行時間計測
  - 呼び出し回数の記録
  - コンソール出力

✓ 基本的なテスト
  - サンプルコードのプロファイリング
  - 統計情報の正確性検証
```

### Phase 2: 実用機能（65点目標）

```
✓ メモリプロファイリング
  - オブジェクト追跡
  - メモリ使用量の可視化

✓ フレームグラフ生成
  - Chrome DevTools互換のJSON出力
  - インタラクティブなHTML出力

✓ 複数の出力形式
  - CSV、JSON、HTML
```

### Phase 3: 運用レベル（90点目標）

```
✓ 統計的プロファイリング
  - サンプリングベースの計測
  - より低オーバーヘッド

✓ 高度な可視化
  - タイムラインビュー
  - メモリ増加のグラフ

✓ パフォーマンスの最適化
  - 計測オーバーヘッドの最小化
  - 大規模プロジェクト対応
```

---

## 📚 参考資料

### 既存プロファイラー

- **cProfile**: Python標準のプロファイラー
- **py-spy**: サンプリングベースのプロファイラー
- **memory_profiler**: メモリプロファイラー
- **pyflame**: フレームグラフ生成ツール

### 読むべき資料

- Pythonの `sys.setprofile()` ドキュメント
- Chrome DevToolsのプロファイラーフォーマット
- Brendan Greggのフレームグラフに関する記事

---

## ✅ 成功の定義

### 30点（MVP）
```
✓ 簡単なPythonスクリプトのプロファイリングができる
✓ ボトルネックが特定できる
✓ 基本的な統計情報が出力される
```

### 65点（実用）
```
✓ 実務のプロジェクトで使える
✓ 複数の出力形式に対応
✓ フレームグラフが見やすい
```

### 90点（市販品レベル）
```
✓ cProfile, py-spyと同等の機能
✓ 計測オーバーヘッドが最小
✓ 本番環境での運用が可能
```

---

**作成者**: Claude (Sonnet 4.5)
**最終更新**: 2026-01-18 02:01
