# Codexray

[![PyPI version](https://img.shields.io/pypi/v/codexray-analyser)](https://pypi.org/project/codexray-analyser/)
[![Python versions](https://img.shields.io/pypi/pyversions/codexray-analyser)](https://pypi.org/project/codexray-analyser/)
[![License](https://img.shields.io/pypi/l/codexray-analyser)](https://github.com/Merlins-Sanctum/codexray-analyser/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Merlins-Sanctum/codexray-analyser/ci.yml?branch=main&label=CI)](https://github.com/Merlins-Sanctum/codexray-analyser/actions/workflows/ci.yml)

Latest stable package: `0.1.2` (tag `v0.1.3`)

![Codexray CLI demo](https://raw.githubusercontent.com/Merlins-Sanctum/codexray-analyser/main/assets/demo.gif)

```bash
codexray "C:\path\to\database.py" --summary --findings-only --min-severity high
```

Codexray is an offline-first Python static analyser for `.py` and `.ipynb` files.
It helps teams inspect security risks, code quality problems, and dependency patterns
without sending source code outside the local machine.

## Why Codexray?

You are about to send a notebook or script to a client and want confidence that nothing risky is hidden inside. Run Codexray first. It checks for risky patterns such as shell execution and dangerous builtins, highlights dependency concerns, and gives you a graph of call and import relationships while keeping all source analysis local to your machine.

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
pip install codexray-analyser
```

## Quick start with CLI

Analyse a folder:

```bash
codexray ./my_project
```

Analyse a single file:

```bash
codexray ./my_project/app.py
```

Analyse a code snippet:

```bash
codexray --snippet "import os; os.system('whoami')"
```

Analyse only specific lines from one file:

```bash
codexray ./my_project/app.py --start-line 40 --end-line 80
```

Save output to JSON:

```bash
codexray ./my_project --output codexray-report.json
```

Print only a compact summary:

```bash
codexray ./my_project --summary
```

Print findings only (no graph payload):

```bash
codexray ./my_project --findings-only
```

Show only high and critical findings:

```bash
codexray ./my_project --findings-only --min-severity high
```

Export graph for Graphviz:

```bash
codexray ./my_project --graph-dot codexray-graph.dot
```

Export graph to an offline HTML visual:

```bash
codexray ./my_project --graph-html codexray-graph.html
```

## Dependency graph preview

![Codexray tree graph example](https://raw.githubusercontent.com/Merlins-Sanctum/codexray-analyser/main/assets/graph-tree-style.png)

Sample graph JSON snippet:

```json
{
  "nodes": [
    { "node_id": "file:database.py", "kind": "file", "label": "database.py" },
    { "node_id": "function:database.py:get_conn", "kind": "function", "label": "get_conn" },
    { "node_id": "import:psycopg2.connect", "kind": "import", "label": "psycopg2.connect" }
  ],
  "edges": [
    { "source": "file:database.py", "target": "function:database.py:get_conn", "relation": "contains" },
    { "source": "function:database.py:get_conn", "target": "import:psycopg2.connect", "relation": "calls" }
  ]
}
```

## Python API usage

```python
from codexray import analyse_file_snippet, analyse_path, analyse_snippet

project_result = analyse_path("./my_project")
snippet_result = analyse_snippet("import os\nos.system('whoami')")
range_result = analyse_file_snippet("./my_project/app.py", 20, 50)
```

## Understanding the report

Each result returns:

- `findings`: list of detected issues.
- `graph`: nodes and edges representing imports, files, and function relationships.
- `metadata`: run information such as analysed path and offline mode state.

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
- DOT export for Graphviz via `--graph-dot`
- offline HTML graph visual via `--graph-html`

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

## How to create the demo GIF

Record a short terminal run (10 to 20 seconds) that shows:

1. `codexray --summary`
2. `codexray --graph-html`
3. opening the generated graph HTML

Then convert to GIF with `ffmpeg` and save as `assets/demo.gif`:

```bash
ffmpeg -i demo.mp4 -vf "fps=10,scale=1200:-1:flags=lanczos" -loop 0 assets/demo.gif
```

Keep file size lightweight so README loads quickly.

## Social preview asset

For LinkedIn posts, use this card:

![Codexray LinkedIn card](https://raw.githubusercontent.com/Merlins-Sanctum/codexray-analyser/main/assets/linkedin-card-v2.png)

## Launch checklist

- Share a short product post on LinkedIn with the demo GIF.
- Post in Python and data engineering communities with one practical use case.
- Add one issue template for feature requests and invite feedback.
- Ask first users to share real files where summary mode helped.

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
