from __future__ import annotations

import ast
from pathlib import Path

from .models import GraphData, GraphEdge, GraphNode


def build_graph(file_path: Path, tree: ast.AST) -> GraphData:
    graph = GraphData()
    file_node = _file_node_id(file_path)
    graph.nodes.append(GraphNode(node_id=file_node, kind="file", label=str(file_path)))

    import_nodes: set[str] = set()
    function_nodes: set[str] = set()

    call_targets: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                import_id = f"import:{module}"
                if import_id not in import_nodes:
                    graph.nodes.append(GraphNode(node_id=import_id, kind="import", label=module))
                    import_nodes.add(import_id)
                graph.edges.append(
                    GraphEdge(source=file_node, target=import_id, relation="imports")
                )

        if isinstance(node, ast.ImportFrom) and node.module:
            module = node.module
            import_id = f"import:{module}"
            if import_id not in import_nodes:
                graph.nodes.append(GraphNode(node_id=import_id, kind="import", label=module))
                import_nodes.add(import_id)
            graph.edges.append(
                GraphEdge(source=file_node, target=import_id, relation="imports")
            )

        if isinstance(node, ast.FunctionDef):
            fn_id = f"function:{file_path}:{node.name}"
            if fn_id not in function_nodes:
                graph.nodes.append(GraphNode(node_id=fn_id, kind="function", label=node.name))
                function_nodes.add(fn_id)
            graph.edges.append(GraphEdge(source=file_node, target=fn_id, relation="contains"))

            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                callee = _get_call_name(child)
                if not callee:
                    continue
                call_id = f"import:{callee}"
                if call_id not in call_targets:
                    graph.nodes.append(GraphNode(node_id=call_id, kind="import", label=callee))
                    call_targets.add(call_id)
                graph.edges.append(GraphEdge(source=fn_id, target=call_id, relation="calls"))

    return graph


def merge_graphs(graphs: list[GraphData]) -> GraphData:
    merged = GraphData()
    seen_nodes: set[str] = set()
    seen_edges: set[tuple[str, str, str]] = set()

    for graph in graphs:
        for node in graph.nodes:
            if node.node_id in seen_nodes:
                continue
            merged.nodes.append(node)
            seen_nodes.add(node.node_id)

        for edge in graph.edges:
            key = (edge.source, edge.target, edge.relation)
            if key in seen_edges:
                continue
            merged.edges.append(edge)
            seen_edges.add(key)

    return merged


def _file_node_id(path: Path) -> str:
    return f"file:{path}"


def _get_call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        segments: list[str] = []
        current: ast.AST = node.func
        while isinstance(current, ast.Attribute):
            segments.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            segments.append(current.id)
            return ".".join(reversed(segments))
    return ""
