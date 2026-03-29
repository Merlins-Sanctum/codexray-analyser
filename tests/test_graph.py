import ast
from pathlib import Path

from codexray.graph import build_graph


def test_graph_import_nodes() -> None:
    tree = ast.parse("import os\nfrom pathlib import Path\n")
    graph = build_graph(Path("a.py"), tree)
    labels = {node.label for node in graph.nodes}
    assert "os" in labels
    assert "pathlib" in labels
