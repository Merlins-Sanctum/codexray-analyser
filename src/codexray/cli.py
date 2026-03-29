from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from xml.sax.saxutils import escape

from .analyser import analyse_file_snippet, analyse_path, analyse_snippet
from .config import AnalyserConfig

SEVERITY_ORDER = ("low", "medium", "high", "critical")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="codexray",
        description="Offline-first static analysis for Python files and notebooks.",
    )
    parser.add_argument(
        "target", nargs="?", help="Path to file or directory to analyse"
    )
    parser.add_argument("--snippet", help="Inline Python snippet to analyse")
    parser.add_argument(
        "--start-line", type=int, help="Start line for target file snippet analysis"
    )
    parser.add_argument(
        "--end-line", type=int, help="End line for target file snippet analysis"
    )
    parser.add_argument("--output", help="Write JSON result to this path")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact summary instead of full JSON output",
    )
    parser.add_argument(
        "--findings-only",
        action="store_true",
        help="Output only findings and metadata",
    )
    parser.add_argument(
        "--min-severity",
        choices=SEVERITY_ORDER,
        default="low",
        help="Filter findings by minimum severity",
    )
    parser.add_argument("--graph-dot", help="Write graph output as DOT file")
    parser.add_argument("--graph-html", help="Write graph output as HTML file")
    parser.add_argument(
        "--allow-network", action="store_true", help="Enable network-dependent features"
    )
    parser.add_argument("--max-file-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("--max-snippet-chars", type=int, default=50_000)

    args = parser.parse_args()

    if not args.target and not args.snippet:
        parser.error("Provide a target path or use --snippet")

    config = AnalyserConfig(
        allow_network=args.allow_network,
        max_file_size_bytes=args.max_file_bytes,
        max_snippet_chars=args.max_snippet_chars,
    )

    if args.snippet:
        result = analyse_snippet(args.snippet, config=config)
    elif args.start_line is not None and args.end_line is not None:
        if not args.target:
            parser.error("Line-range analysis requires a file target")
        result = analyse_file_snippet(
            Path(args.target),
            start_line=args.start_line,
            end_line=args.end_line,
            config=config,
        )
    else:
        result = analyse_path(Path(args.target), config=config)

    payload = asdict(result)
    payload["findings"] = _filter_findings(payload["findings"], args.min_severity)

    if args.findings_only:
        payload = {
            "findings": payload["findings"],
            "metadata": payload["metadata"],
        }

    if args.graph_dot:
        _write_graph_dot(asdict(result)["graph"], Path(args.graph_dot))
    if args.graph_html:
        _write_graph_html(asdict(result)["graph"], Path(args.graph_html))

    rendered = json.dumps(payload, indent=2)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")

    if args.summary:
        print(_build_summary_text(payload["findings"], payload.get("metadata", {})))
    elif not args.output:
        print(rendered)

    return 0


def _filter_findings(
    findings: list[dict[str, object]], min_severity: str
) -> list[dict[str, object]]:
    min_index = SEVERITY_ORDER.index(min_severity)
    return [
        finding
        for finding in findings
        if SEVERITY_ORDER.index(str(finding.get("severity", "low"))) >= min_index
    ]


def _build_summary_text(
    findings: list[dict[str, object]], metadata: dict[str, object]
) -> str:
    counts = Counter(str(finding.get("severity", "unknown")) for finding in findings)
    ordered_counts = ", ".join(
        f"{severity}: {counts.get(severity, 0)}" for severity in reversed(SEVERITY_ORDER)
    )
    top = findings[:5]
    lines = [
        "Codexray summary",
        f"Path: {metadata.get('analysed_path', 'n/a')}",
        f"Files analysed: {metadata.get('files_analysed', 'n/a')}",
        f"Offline mode: {metadata.get('offline_mode', 'n/a')}",
        f"Findings by severity: {ordered_counts}",
    ]
    if top:
        lines.append("Top findings:")
        for finding in top:
            lines.append(
                f"- [{finding.get('severity')}] {finding.get('rule_id')}: "
                f"{finding.get('title')} ({finding.get('file_path')})"
            )
    else:
        lines.append("Top findings: none")
    return "\n".join(lines)


def _write_graph_dot(graph: dict[str, object], path: Path) -> None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    lines = ["digraph codexray {", '  rankdir="LR";']
    for node in nodes:
        node_id = escape(str(node.get("node_id", ""))).replace('"', '\\"')
        label = escape(str(node.get("label", ""))).replace('"', '\\"')
        lines.append(f'  "{node_id}" [label="{label}"];')
    for edge in edges:
        source = escape(str(edge.get("source", ""))).replace('"', '\\"')
        target = escape(str(edge.get("target", ""))).replace('"', '\\"')
        relation = escape(str(edge.get("relation", ""))).replace('"', '\\"')
        lines.append(f'  "{source}" -> "{target}" [label="{relation}"];')
    lines.append("}")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_graph_html(graph: dict[str, object], path: Path) -> None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    width = 1200
    height = 800
    radius = 300
    cx = width // 2
    cy = height // 2

    positioned: dict[str, tuple[float, float, str]] = {}
    for idx, node in enumerate(nodes):
        angle = (2 * math.pi * idx / max(len(nodes), 1)) if nodes else 0
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        node_id = str(node.get("node_id", ""))
        label = escape(str(node.get("label", "")))
        positioned[node_id] = (x, y, label)

    svg_lines = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#111827"/>',
    ]

    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        relation = escape(str(edge.get("relation", "")))
        if source not in positioned or target not in positioned:
            continue
        x1, y1, _ = positioned[source]
        x2, y2, _ = positioned[target]
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        svg_lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            'stroke="#4b5563" stroke-width="1.5"/>'
        )
        svg_lines.append(
            f'<text x="{mx:.1f}" y="{my:.1f}" fill="#9ca3af" font-size="10">{relation}</text>'
        )

    for x, y, label in positioned.values():
        svg_lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#10b981" stroke="#a7f3d0" '
            'stroke-width="1.5"/>'
        )
        svg_lines.append(
            f'<text x="{x + 12:.1f}" y="{y + 4:.1f}" fill="#e5e7eb" font-size="11">{label}</text>'
        )

    svg_lines.append("</svg>")
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Codexray Graph</title>
    <style>
      body {{ font-family: Arial, sans-serif; background: #0b1020; color: #e5e7eb; margin: 0; }}
      main {{ padding: 16px; }}
      h1 {{ margin-top: 0; }}
      p {{ color: #9ca3af; }}
      svg {{ width: 100%; height: auto; border: 1px solid #1f2937; border-radius: 8px; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Codexray Graph</h1>
      <p>Nodes: {len(nodes)} | Edges: {len(edges)}</p>
      {''.join(svg_lines)}
    </main>
  </body>
</html>
"""
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
