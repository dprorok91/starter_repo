# Python upgrade example

The application starts on Python 3.10. The directory name records its starting point.
Its `.python-version`, `pyproject.toml`, and `uv.lock` own the runtime requirement.

```bash
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
```

The starter's orchestration Python is independent. Run the full verification from the repository root.
