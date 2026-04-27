from pathlib import Path
import argparse
import sys

from devclean.scanner import scan
from devclean.cleaner import clean
from devclean.reporter import print_result, print_summary
from devclean.exceptions import ScanError, CleanError


DEFAULT_TARGETS = [
    "node_modules", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "dist", "build",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="devclean — clean development junk folders"
    )

    # positional argument
    parser.add_argument(
        "path",
        type=Path,
        help="Root directory to scan"
    )

    # flag
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan but do not delete folders"
    )

    # optional list
    parser.add_argument(
        "--targets",
        nargs="+",
        help="Override default target folder names"
    )

    # optional float
    parser.add_argument(
        "--min-size",
        type=float,
        default=0.0,
        help="Skip folders smaller than this size (in MB)"
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    root: Path = args.path
    dry_run: bool = args.dry_run
    targets = args.targets if args.targets else DEFAULT_TARGETS
    min_size: float = args.min_size

    print(f"devclean — scanning {root}\n")

    results = []

    try:
        for scan_result in scan(root, targets):
            try:
                clean_result = clean(scan_result, dry_run=dry_run)

                # apply min-size filter
                if clean_result.size_mb < min_size:
                    continue

                print_result(clean_result)
                results.append(clean_result)

            except CleanError as e:
                print(f"Error cleaning '{scan_result.name}': {e}", file=sys.stderr)

        print_summary(results, dry_run)

    except ScanError as e:
        print(f"Scan error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()