from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass(slots=True)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    message: str
    file_path: str
    line: int | None = None
    column: int | None = None


@dataclass(slots=True)
class GraphNode:
    node_id: str
    kind: Literal["file", "import", "function"]
    label: str


@dataclass(slots=True)
class GraphEdge:
    source: str
    target: str
    relation: Literal["imports", "calls", "contains"]


@dataclass(slots=True)
class GraphData:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


@dataclass(slots=True)
class AnalysisResult:
    findings: list[Finding] = field(default_factory=list)
    graph: GraphData = field(default_factory=GraphData)
    metadata: dict[str, str | int | bool] = field(default_factory=dict)
