from unittest.mock import patch, call
from pathlib import Path

from src.devclean.cli import main
from src.devclean.scanner import ScanResult
from src.devclean.cleaner import CleanResult

def test_output_order_matches_scan_order(tmp_path):
    
    fake_scan_results = [
        ScanResult(path=tmp_path / "a" / "node_modules", name="node_modules", parent=tmp_path / "a"),
        ScanResult(path=tmp_path / "b" / "venv",         name="venv",         parent=tmp_path / "b"),
        ScanResult(path=tmp_path / "c" / "__pycache__",  name="__pycache__",  parent=tmp_path / "c"),
    ]

    fake_clean_results = [
        CleanResult(path=r.path, name=r.name, size_mb=1.0, deleted=False)
        for r in fake_scan_results
    ]

    # --- Fake args ---
    class Args:
        path = tmp_path
        dry_run = True
        targets = None
        min_size = 0

    with patch("src.devclean.cli.scan", return_value=fake_scan_results), \
         patch("src.devclean.cli.clean", side_effect=fake_clean_results), \
         patch("src.devclean.cli.print_result") as mock_print, \
         patch("src.devclean.cli.print_summary"), \
         patch("src.devclean.cli.print_header"), \
         patch("src.devclean.cli.parse_args", return_value=Args()):

        # --- Run ---
        main()

        # --- Assert order ---
        expected_calls = [call(r) for r in fake_clean_results]
        assert mock_print.call_args_list == expected_calls