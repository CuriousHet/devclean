from dataclasses import dataclass
from pathlib import Path
import shutil

from src.devclean.exceptions import CleanError
from src.devclean.scanner import ScanResult


@dataclass(frozen=True)
class CleanResult:
    path: Path
    name: str
    size_mb: float
    deleted: bool


def get_size(path: Path) -> float:
    """Return total folder size in MB."""
    total_bytes = 0
    for p in path.rglob("*"):
        try:
            if p.exists() and p.is_file():
                total_bytes += p.stat().st_size
        except (PermissionError, OSError):
            continue
    return total_bytes / (1024 * 1024)


def clean(result: ScanResult, dry_run: bool = False) -> CleanResult:
    path = result.path

    if not path.exists():
        return CleanResult(path=path, name=result.name, size_mb=0.0, deleted=False)

    try:
        size_mb = get_size(path)
    except OSError as e:
        raise CleanError(str(path), f"Failed to calculate size: {e}")

    if dry_run:
        return CleanResult(path=path, name=result.name, size_mb=size_mb, deleted=False)

    try:
        shutil.rmtree(path)
        return CleanResult(path=path, name=result.name, size_mb=size_mb, deleted=True)
    except OSError as e:
        raise CleanError(str(path), f"Failed to delete: {e}")