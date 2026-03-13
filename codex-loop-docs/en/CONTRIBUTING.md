# Contributing

## Development Setup

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Rules

- Keep the CLI cross-platform.
- Treat generated docs as stable templates and evolve them deliberately.
- Preserve compatibility with the existing shell-loop behavior where practical.
- Update both English and Chinese docs when user-facing behavior changes.
