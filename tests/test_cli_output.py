from __future__ import annotations

from pathlib import Path

from codexray.cli import (
    _build_summary_text,
    _filter_findings,
    _write_graph_dot,
    _write_graph_html,
)


def test_filter_findings_by_min_severity() -> None:
    findings = [
        {"rule_id": "A", "severity": "low"},
        {"rule_id": "B", "severity": "medium"},
        {"rule_id": "C", "severity": "high"},
        {"rule_id": "D", "severity": "critical"},
    ]
    filtered = _filter_findings(findings, "high")
    ids = [item["rule_id"] for item in filtered]
    assert ids == ["C", "D"]


def test_summary_text_contains_counts() -> None:
    findings = [
        {"rule_id": "SEC001", "severity": "high", "title": "shell", "file_path": "a.py"},
        {"rule_id": "SEC002", "severity": "critical", "title": "eval", "file_path": "b.py"},
    ]
    metadata = {"analysed_path": "demo.py", "files_analysed": 1, "offline_mode": True}
    text = _build_summary_text(findings, metadata)
    assert "Path: demo.py" in text
    assert "critical: 1" in text
    assert "high: 1" in text


def test_graph_exports_are_written(tmp_path: Path) -> None:
    graph = {
        "nodes": [
            {"node_id": "file:a.py", "label": "a.py"},
            {"node_id": "import:os", "label": "os"},
        ],
        "edges": [
            {"source": "file:a.py", "target": "import:os", "relation": "imports"},
        ],
    }
    dot_path = tmp_path / "graph.dot"
    html_path = tmp_path / "graph.html"

    _write_graph_dot(graph, dot_path)
    _write_graph_html(graph, html_path)

    assert dot_path.exists()
    assert html_path.exists()
    assert "digraph codexray" in dot_path.read_text(encoding="utf-8")
    assert "<svg" in html_path.read_text(encoding="utf-8")
