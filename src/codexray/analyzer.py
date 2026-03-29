from __future__ import annotations

from pathlib import Path

from .config import AnalyzerConfig
from .graph import build_graph, merge_graphs
from .limits import AnalyzerLimitError
from .models import AnalysisResult, Finding
from .parsers import (
    discover_input_files,
    parse_notebook,
    parse_python_source,
    parse_requirements_text,
    read_file_text,
    select_line_range,
)
from .rules import RuleContext, run_requirements_rules, run_rules


def analyze_path(path: str | Path, config: AnalyzerConfig | None = None) -> AnalysisResult:
    cfg = config or AnalyzerConfig()
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if root.is_file():
        files = [root]
    else:
        files = list(discover_input_files(root))

    all_findings = []
    graphs = []

    for file_path in files:
        suffix = file_path.suffix.lower()
        if _is_requirements_file(file_path):
            try:
                source = read_file_text(file_path, cfg)
                requirements = parse_requirements_text(source)
                all_findings.extend(run_requirements_rules(requirements, file_path))
            except (ValueError, OSError) as exc:
                all_findings.append(_parsing_finding(file_path, str(exc)))
            continue

        if suffix not in {".py", ".ipynb"}:
            continue

        try:
            source = _load_source(file_path, cfg)
            tree = parse_python_source(source, cfg)
            all_findings.extend(
                run_rules(RuleContext(file_path=file_path, source=source, tree=tree))
            )
            graphs.append(build_graph(file_path, tree))
        except (AnalyzerLimitError, SyntaxError, OSError, ValueError) as exc:
            all_findings.append(_parsing_finding(file_path, str(exc)))

    return AnalysisResult(
        findings=sorted(
            all_findings, key=lambda item: (item.file_path, item.rule_id, item.line or 0)
        ),
        graph=merge_graphs(graphs),
        metadata={
            "analyzed_path": str(root),
            "offline_mode": not cfg.allow_network,
            "files_analyzed": len(files),
        },
    )


def analyze_snippet(
    source: str,
    file_path: str = "snippet.py",
    config: AnalyzerConfig | None = None,
) -> AnalysisResult:
    cfg = config or AnalyzerConfig()
    tree = parse_python_source(source, cfg)
    path = Path(file_path)
    findings = run_rules(RuleContext(file_path=path, source=source, tree=tree))
    graph = build_graph(path, tree)
    return AnalysisResult(
        findings=findings,
        graph=graph,
        metadata={"snippet": True, "offline_mode": not cfg.allow_network},
    )


def analyze_file_snippet(
    path: str | Path,
    start_line: int,
    end_line: int,
    config: AnalyzerConfig | None = None,
) -> AnalysisResult:
    cfg = config or AnalyzerConfig()
    target = Path(path)
    source = read_file_text(target, cfg)
    snippet = select_line_range(source, start_line, end_line)
    return analyze_snippet(snippet, file_path=str(target), config=cfg)


def _load_source(path: Path, config: AnalyzerConfig) -> str:
    if path.suffix.lower() == ".ipynb":
        return parse_notebook(path, config)
    if path.suffix.lower() == ".py":
        return read_file_text(path, config)
    raise ValueError(f"Unsupported source type: {path.suffix}")


def _is_requirements_file(path: Path) -> bool:
    lower_name = path.name.lower()
    return lower_name.startswith("requirements") and path.suffix.lower() in {
        ".txt",
        ".in",
        ".cfg",
    }


def _parsing_finding(path: Path, error_message: str) -> Finding:
    return Finding(
        rule_id="PARSE001",
        title="File parsing failed",
        severity="medium",
        message=error_message,
        file_path=str(path),
    )
