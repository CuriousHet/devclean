from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


def load_config(root: Path) -> dict:
    """
    Load devclean.toml from root if it exists.
    Returns the [devclean] section as a dict.
    Returns empty dict if file not found.
    """
    config_path = root / "devclean.toml"
    if not config_path.exists():
        return {}
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    return data.get("devclean", {})