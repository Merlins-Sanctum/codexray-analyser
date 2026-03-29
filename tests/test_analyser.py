import json
from pathlib import Path

from codexray import (
    AnalyserConfig,
    analyse_file_snippet,
    analyse_path,
    analyse_snippet,
)


def test_analyse_snippet_detects_eval() -> None:
    result = analyse_snippet("eval('2+2')")
    ids = {item.rule_id for item in result.findings}
    assert "SEC002" in ids


def test_analyse_path_for_python_file(tmp_path: Path) -> None:
    content = "import os\nos.system('ls')\n"
    sample = tmp_path / "sample.py"
    sample.write_text(content, encoding="utf-8")

    result = analyse_path(sample)
    ids = {item.rule_id for item in result.findings}
    assert "SEC001" in ids
    assert result.metadata["offline_mode"] is True


def test_analyse_ipynb(tmp_path: Path) -> None:
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# test"]},
            {
                "cell_type": "code",
                "source": ["import requests\n", "requests.get('https://x', verify=False)"],
            },
        ]
    }
    sample = tmp_path / "sample.ipynb"
    sample.write_text(json.dumps(notebook), encoding="utf-8")

    result = analyse_path(sample)
    assert any(f.rule_id == "SEC003" for f in result.findings)


def test_snippet_size_limit() -> None:
    config = AnalyserConfig(max_snippet_chars=10)
    try:
        analyse_snippet("x" * 100, config=config)
    except ValueError as exc:
        assert "exceeds" in str(exc)
    else:
        raise AssertionError("Expected limit error")


def test_analyse_file_snippet(tmp_path: Path) -> None:
    sample = tmp_path / "snippet_target.py"
    sample.write_text("print('safe')\neval('1+1')\n", encoding="utf-8")
    result = analyse_file_snippet(sample, start_line=2, end_line=2)
    assert any(item.rule_id == "SEC002" for item in result.findings)
