from pathlib import Path
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
import logging

from devclean.scanner import scan
from devclean.cleaner import clean
from devclean.reporter import print_result, print_summary, print_header
from devclean.exceptions import ScanError, CleanError
from devclean.config import load_config

logger = logging.getLogger(__name__)

DEFAULT_TARGETS = [
    "node_modules", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "dist", "build",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="devclean — clean development junk folders"
    )
    parser.add_argument("path", type=Path, help="Root directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Scan but do not delete")
    parser.add_argument("--targets", nargs="+", help="Override default target folder names")
    parser.add_argument("--min-size", type=float, default=0.0, help="Skip folders smaller than N MB")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    root: Path = args.path
    
    # load config
    config = load_config(root)

    #defaults
    dry_run: bool = False
    targets: list[str] = DEFAULT_TARGETS
    min_size: float = 0.0

    # config file overrides defaults
    if "targets" in config:
        targets = config["targets"]
    if "min_size" in config:
        min_size = config["min_size"]
    if "dry_run" in config:
        dry_run = config["dry_run"]

    # CLI flags override config file
    if args.dry_run:
        dry_run = args.dry_run
    if args.targets:
        targets = args.targets
    if args.min_size is not None:
        min_size = args.min_size

    print_header(str(root))
    results = []

    try:
        scan_results = list(scan(root, targets))
        logger.debug("Found %d candidate folders", len(scan_results))

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(clean, sr, dry_run=dry_run)
                for sr in scan_results
            ]

            for future, scan_result in zip(futures, scan_results):
                try:
                    clean_result = future.result()

                    if not clean_result.path.exists() and clean_result.size_mb == 0.0:
                        logger.debug("Skipped '%s' — already gone", scan_result.name)
                        continue

                    if clean_result.size_mb < min_size:
                        logger.debug(
                            "Skipped '%s' (%.2f MB < %.2f MB min)",
                            scan_result.name,
                            clean_result.size_mb,
                            min_size,
                        )
                        continue

                    print_result(clean_result)
                    results.append(clean_result)

                except CleanError as e:
                    logger.warning("Error cleaning '%s': %s", scan_result.name, e)

        print_summary(results, dry_run)

    except ScanError as e:
        logger.error("Scan error: %s", e)
        sys.exit(1)