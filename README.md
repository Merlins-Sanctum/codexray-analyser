# Codexray

Codexray is an offline-first Python static analyzer for `.py` and `.ipynb` files.
It helps teams inspect security risks, code quality problems, and dependency patterns
without sending source code outside the local machine.

## What Codexray does

- Scans Python files and notebooks.
- Supports project-level scans, full file scans, and targeted line-range checks.
- Produces a structured JSON report.
- Builds a dependency graph view with nodes and edges.
- Flags common security risks such as shell execution and dangerous builtins.

## Privacy and security behavior

- No telemetry.
- No source upload.
- Network features are disabled by default.
- Strict input limits for file size, notebook size, snippet length, and AST depth.

This tool is designed for local analysis workflows where proprietary code must stay on the client system.

## Installation

```bash
pip install codexray-analyzer
```

## Quick start with CLI

Analyze a folder:

```bash
codexray ./my_project
```

Analyze a single file:

```bash
codexray ./my_project/app.py
```

Analyze a code snippet:

```bash
codexray --snippet "import os; os.system('whoami')"
```

Analyze only specific lines from one file:

```bash
codexray ./my_project/app.py --start-line 40 --end-line 80
```

Save output to JSON:

```bash
codexray ./my_project --output codexray-report.json
```

## Python API usage

```python
from codexray import analyze_file_snippet, analyze_path, analyze_snippet

project_result = analyze_path("./my_project")
snippet_result = analyze_snippet("import os\nos.system('whoami')")
range_result = analyze_file_snippet("./my_project/app.py", 20, 50)
```

## Understanding the report

Each result returns:

- `findings`: list of detected issues.
- `graph`: nodes and edges representing imports, files, and function relationships.
- `metadata`: run information such as analyzed path and offline mode state.

Example finding shape:

```json
{
  "rule_id": "SEC002",
  "title": "Dangerous builtin eval",
  "severity": "critical",
  "message": "Avoid eval on untrusted content.",
  "file_path": "src/app.py",
  "line": 18,
  "column": 4
}
```

## Reading graph output

Graph output contains:

- `nodes`: entities such as files, imports, and functions
- `edges`: relationships such as `imports`, `contains`, and `calls`

Typical use:

1. Run Codexray and save JSON output.
2. Load `graph.nodes` and `graph.edges` into your graph viewer.
3. Track dependency hotspots and risky call paths.

## How to use findings to make code changes

Recommended workflow:

1. Sort findings by `severity`.
2. Fix `critical` and `high` findings first.
3. Re-run Codexray after each fix batch.
4. Keep evidence by committing report diffs in your internal workflow.

Examples:

- `SEC001` shell execution:
  - Replace dynamic shell calls with safe Python APIs.
  - Avoid passing untrusted input to command execution.
- `SEC002` dangerous builtin:
  - Replace `eval` or `exec` with safe parsing and strict allow-lists.
- `DEP001` unpinned dependency:
  - Pin versions in requirements files with `==` where practical.

## Troubleshooting

- `File parsing failed`:
  - Check syntax errors or unsupported file encoding.
- `exceeds ... bytes/chars`:
  - Increase limits in config for controlled internal usage.
- Empty findings:
  - Confirm the target path includes `.py` or `.ipynb` sources.

## Local development

```bash
python -m pip install -e .
python -m pip install pytest ruff bandit pip-audit build twine
python -m ruff check .
python -m pytest
python -m bandit -q -r src
python -m pip-audit
python -m build
python -m twine check dist/*
```

## Contributing

Read `CONTRIBUTING.md` before opening a pull request.
Security reports should follow `SECURITY.md`.

## License

MIT. See `LICENSE`.
