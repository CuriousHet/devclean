from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from src.devclean.exceptions import ScanError


@dataclass(frozen=True)
class ScanResult:
    path: Path
    name: str
    parent: Path


def scan(root: Path, targets: list[str]) -> Iterator[ScanResult]:
    """
    Yields ScanResult for every matching folder found under root.

    Raises:
        ScanError: if root doesn't exist or isn't a directory
    Skips:
        folders that raise PermissionError or OSError
    """
    if not root.exists():
        raise ScanError(str(root), "Path does not exist")
    if not root.is_dir():
        raise ScanError(str(root), "Path is not a directory")

    target_set = set(targets)

    for path in root.rglob("*"):
        try:
            if not path.is_dir():
                continue
            if path.name in target_set:
                yield ScanResult(
                    path=path,
                    name=path.name,
                    parent=path.parent,
                )
        except (PermissionError, OSError):
            continue

# def main():

#     path = Path("test_dir")
#     targets = ["node_modules"]

#     res = scan(path, targets)
#     for a in res:
#         print(a)


# if __name__ == "__main__":
#     main()