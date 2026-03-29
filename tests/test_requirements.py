from pathlib import Path

from codexray import analyze_path
from codexray.parsers import parse_requirements_text


def test_requirements_parser() -> None:
    deps = parse_requirements_text("""
# comment
requests==2.32.0
--extra-index-url x
flask>=3
""")
    assert deps == ["requests==2.32.0", "flask>=3"]


def test_requirements_rule(tmp_path: Path) -> None:
    req = tmp_path / "requirements.txt"
    req.write_text("requests>=2.31.0\nnumpy==1.26.4\n", encoding="utf-8")
    result = analyze_path(tmp_path)
    assert any(item.rule_id == "DEP001" for item in result.findings)
