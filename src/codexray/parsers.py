from __future__ import annotations

import ast
import json
from collections.abc import Iterable
from pathlib import Path

from .config import AnalyzerConfig
from .limits import AnalyzerLimitError, enforce_ast_limit, enforce_bytes_limit, enforce_text_limit

SUPPORTED_SUFFIXES = {".py", ".ipynb", ".txt", ".in", ".cfg"}


def read_file_text(path: Path, config: AnalyzerConfig) -> str:
    size = path.stat().st_size
    enforce_bytes_limit(size, config.max_file_size_bytes, f"File {path}")
    return path.read_text(encoding="utf-8", errors="strict")


def parse_python_source(source: str, config: AnalyzerConfig) -> ast.AST:
    enforce_text_limit(source, config.max_snippet_chars, "Python source")
    tree = ast.parse(source)
    enforce_ast_limit(tree, config)
    return tree


def parse_notebook(path: Path, config: AnalyzerConfig) -> str:
    size = path.stat().st_size
    enforce_bytes_limit(size, config.max_notebook_json_bytes, f"Notebook {path}")
    raw = path.read_text(encoding="utf-8")
    try:
        notebook = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AnalyzerLimitError(f"Notebook JSON is invalid: {exc}") from exc
    cells = notebook.get("cells", [])
    if not isinstance(cells, list):
        raise AnalyzerLimitError("Notebook cells payload is invalid")
    if len(cells) > config.max_notebook_cells:
        raise AnalyzerLimitError(
            f"Notebook has {len(cells)} cells, over max {config.max_notebook_cells}"
        )

    lines: list[str] = []
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", [])
        if isinstance(source, list):
            joined = "".join(str(part) for part in source)
        else:
            joined = str(source)
        if joined.strip():
            lines.append(joined)
    source = "\n\n".join(lines)
    enforce_text_limit(source, config.max_snippet_chars, "Notebook extracted code")
    return source


def parse_requirements_text(text: str) -> list[str]:
    dependencies: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("--"):
            continue
        dependencies.append(line)
    return dependencies


def select_line_range(source: str, start_line: int, end_line: int) -> str:
    if start_line < 1 or end_line < start_line:
        raise ValueError("Invalid line range")
    lines = source.splitlines()
    if end_line > len(lines):
        raise ValueError("Requested line range exceeds file length")
    return "\n".join(lines[start_line - 1 : end_line])


def discover_input_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.parts):
            continue
        if any(part in {"venv", ".venv", "__pycache__", "node_modules"} for part in path.parts):
            continue
        if path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path
