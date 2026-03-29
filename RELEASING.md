# Releasing to PyPI

This project uses GitHub Actions trusted publishing for PyPI.

## One-time setup

1. Create a GitHub repository named `pyscope`.
2. Push this code to the default branch (`main`).
3. Create the PyPI project once with the exact package name:
   - `codexray-analyzer`
4. In PyPI project settings, add a trusted publisher:
   - Owner: your GitHub user/org
   - Repository: `pyscope`
   - Workflow: `.github/workflows/publish.yml`
   - Environment: `pypi`
5. In GitHub repository settings, create environment `pypi`.

## Release flow

1. Update version in `pyproject.toml`.
2. Commit and push to `main`.
3. Create and push a tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

4. GitHub Actions runs `.github/workflows/publish.yml`.
5. On success, package is available on PyPI.

## Local validation before tagging

```bash
python -m pip install --upgrade pip build twine
python -m build
python -m twine check dist/*
```
