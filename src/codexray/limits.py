from __future__ import annotations

import ast

from .config import AnalyserConfig


class AnalyserLimitError(ValueError):
    """Raised when user input exceeds configured safety limits."""


def enforce_text_limit(text: str, max_chars: int, context: str) -> None:
    if len(text) > max_chars:
        raise AnalyserLimitError(f"{context} exceeds {max_chars} characters")


def enforce_bytes_limit(size_bytes: int, max_bytes: int, context: str) -> None:
    if size_bytes > max_bytes:
        raise AnalyserLimitError(f"{context} exceeds {max_bytes} bytes")


def enforce_ast_limit(tree: ast.AST, config: AnalyserConfig) -> None:
    node_count = sum(1 for _ in ast.walk(tree))
    if node_count > config.max_ast_nodes:
        raise AnalyserLimitError(f"AST exceeds configured node limit ({config.max_ast_nodes})")
