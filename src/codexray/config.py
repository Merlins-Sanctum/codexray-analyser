from dataclasses import dataclass


@dataclass(slots=True)
class AnalyserConfig:
    """Runtime safety controls and feature flags."""

    allow_network: bool = False
    max_file_size_bytes: int = 2 * 1024 * 1024
    max_notebook_cells: int = 500
    max_notebook_json_bytes: int = 5 * 1024 * 1024
    max_ast_nodes: int = 200_000
    max_snippet_chars: int = 50_000
