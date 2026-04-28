# devclean

Clean development junk folders from your repos — `node_modules`, `venv`, `__pycache__`, and more.

---

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# see what would be deleted — safe, nothing is touched
devclean F:\projects --dry-run

# delete everything found
devclean F:\projects

# only show folders larger than 50 MB
devclean F:\projects --min-size 50

# custom targets only
devclean F:\projects --targets __pycache__ .pytest_cache
```

## Default targets

`node_modules` `venv` `.venv` `env` `__pycache__` `.pytest_cache` `.mypy_cache` `dist` `build`

## Run tests

```bash
pytest tests/ -v
```

---