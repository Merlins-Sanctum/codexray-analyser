from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from .models import Finding


@dataclass(slots=True)
class RuleContext:
    file_path: Path
    source: str
    tree: ast.AST


class _ShellCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hits: list[tuple[int, int]] = []

    def visit_Call(self, node: ast.Call) -> None:
        func_name = _get_call_name(node)
        if func_name in {"os.system", "subprocess.call", "subprocess.run", "subprocess.Popen"}:
            self.hits.append((node.lineno, node.col_offset))
        self.generic_visit(node)


class _DangerousBuiltinsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hits: list[tuple[str, int, int]] = []

    def visit_Call(self, node: ast.Call) -> None:
        func_name = _get_call_name(node)
        if func_name in {"eval", "exec"}:
            self.hits.append((func_name, node.lineno, node.col_offset))
        self.generic_visit(node)


def _get_call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))
    return ""


def run_rules(ctx: RuleContext) -> list[Finding]:
    findings: list[Finding] = []

    shell_visitor = _ShellCallVisitor()
    shell_visitor.visit(ctx.tree)
    for line, col in shell_visitor.hits:
        findings.append(
            Finding(
                rule_id="SEC001",
                title="Shell command execution",
                severity="high",
                message="Shell execution can be dangerous with untrusted input.",
                file_path=str(ctx.file_path),
                line=line,
                column=col,
            )
        )

    builtin_visitor = _DangerousBuiltinsVisitor()
    builtin_visitor.visit(ctx.tree)
    for func_name, line, col in builtin_visitor.hits:
        findings.append(
            Finding(
                rule_id="SEC002",
                title=f"Dangerous builtin {func_name}",
                severity="critical",
                message=f"Avoid {func_name} on untrusted content.",
                file_path=str(ctx.file_path),
                line=line,
                column=col,
            )
        )

    if "verify=False" in ctx.source:
        findings.append(
            Finding(
                rule_id="SEC003",
                title="TLS verification disabled",
                severity="high",
                message="requests verify=False weakens TLS protection.",
                file_path=str(ctx.file_path),
            )
        )

    if "TODO" in ctx.source:
        findings.append(
            Finding(
                rule_id="QLT001",
                title="Unresolved TODO",
                severity="low",
                message="TODO comments should be tracked before release.",
                file_path=str(ctx.file_path),
            )
        )

    return findings


def run_requirements_rules(requirements: list[str], file_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for dep in requirements:
        # Prefer pinned dependencies for reproducibility and easier CVE response.
        if "==" not in dep:
            findings.append(
                Finding(
                    rule_id="DEP001",
                    title="Unpinned dependency",
                    severity="medium",
                    message=f"Dependency '{dep}' is not pinned with ==.",
                    file_path=str(file_path),
                )
            )
    return findings
