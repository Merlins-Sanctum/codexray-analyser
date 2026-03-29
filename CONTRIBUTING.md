# Contributing

Thanks for contributing to `codexray-analyser`.

## Local setup

1. Fork and clone the repo.
2. Install development tools:

```bash
python -m pip install -e .
python -m pip install pytest ruff bandit pip-audit build twine
```

## Before opening a PR

Run all checks locally:

```bash
python -m ruff check .
python -m pytest
python -m bandit -q -r src
```

## Development guidelines

- Keep offline-first behavior as the default.
- Avoid adding network dependencies in default analysis flow.
- Add tests for new rules and parser behavior.
- Keep dependencies minimal and justified.

## Pull requests

- Use clear titles and explain why the change is needed.
- Include tests for bug fixes and new features.
- Keep changes focused and small when possible.
