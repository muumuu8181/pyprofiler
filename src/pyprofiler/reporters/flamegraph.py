"""
Flame graph reporter for Chrome DevTools compatible output
"""
import json
from typing import Any, Dict, List


class FlameGraphReporter:
    """Reporter for Chrome DevTools compatible flame graph"""

    def __init__(self):
        """Initialize flame graph reporter"""
        pass

    def report(self, stats, output: str = 'flamegraph.json') -> None:
        """
        Generate flame graph in Chrome DevTools format

        Args:
            stats: Profiler statistics
            output: Output file path
        """
        # Convert stats to Chrome DevTools format
        profile = self._convert_to_chrome_format(stats)

        # Write to file
        with open(output, 'w') as f:
            json.dump(profile, f, indent=2)

        print(f"Flame graph saved to {output}")

    def _convert_to_chrome_format(self, stats) -> Dict[str, Any]:
        """
        Convert profiler stats to Chrome DevTools format

        Returns:
            Dictionary in Chrome DevTools profile format
        """
        # Create a simplified profile structure
        profile = {
            "nodes": [],
            "samples": [],
            "timeDeltas": [],
            "startTime": 0,
            "endTime": 0
        }

        node_id = 0
        node_map = {}

        # Create root node
        root_id = node_id
        profile["nodes"].append({
            "id": root_id,
            "name": "root",
            "script": "",
            "line": 0,
            "callUID": root_id,
            "children": []
        })
        node_map["root"] = root_id
        node_id += 1

        # Add function nodes
        for func_name, func_stats in stats.function_stats.items():
            func_id = node_id
            profile["nodes"].append({
                "id": func_id,
                "name": func_name,
                "script": func_name,  # Simplified
                "line": 0,
                "callUID": func_id,
                "children": []
            })
            node_map[func_name] = func_id
            node_id += 1

        # Create samples (simplified - just showing function calls)
        profile["startTime"] = 0
        profile["endTime"] = int(stats.total_time * 1000000)  # Convert to microseconds

        return profile

    def generate_html(self, stats, output: str = 'flamegraph.html') -> None:
        """
        Generate HTML file with embedded flame graph viewer

        Args:
            stats: Profiler statistics
            output: Output HTML file path
        """
        # Generate JSON data
        profile = self._convert_to_chrome_format(stats)

        # Create HTML with embedded viewer
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Flame Graph</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        .info {{
            background: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="info">
        <h1>Flame Graph</h1>
        <p>Total time: {stats.total_time:.6f}s</p>
        <p>Functions profiled: {len(stats.function_stats)}</p>
    </div>
    <pre id="profile-data" style="display:none;">{json.dumps(profile, indent=2)}</pre>
    <div id="viewer">
        <p>Chrome DevTools flame graph viewer will be embedded here.</p>
        <p>For now, here's the raw data:</p>
        <pre>{json.dumps(profile, indent=2)}</pre>
    </div>
</body>
</html>"""

        with open(output, 'w') as f:
            f.write(html)

        print(f"Flame graph HTML saved to {output}")


__all__ = ['FlameGraphReporter']
