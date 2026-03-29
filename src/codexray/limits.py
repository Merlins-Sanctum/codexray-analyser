from __future__ import annotations

import ast

from .config import AnalyzerConfig


class AnalyzerLimitError(ValueError):
    """Raised when user input exceeds configured safety limits."""


def enforce_text_limit(text: str, max_chars: int, context: str) -> None:
    if len(text) > max_chars:
        raise AnalyzerLimitError(f"{context} exceeds {max_chars} characters")


def enforce_bytes_limit(size_bytes: int, max_bytes: int, context: str) -> None:
    if size_bytes > max_bytes:
        raise AnalyzerLimitError(f"{context} exceeds {max_bytes} bytes")


def enforce_ast_limit(tree: ast.AST, config: AnalyzerConfig) -> None:
    node_count = sum(1 for _ in ast.walk(tree))
    if node_count > config.max_ast_nodes:
        raise AnalyzerLimitError(f"AST exceeds configured node limit ({config.max_ast_nodes})")
