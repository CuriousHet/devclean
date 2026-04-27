# tests/test_scanner.py
from pathlib import Path
import pytest

from devclean.scanner import scan, ScanResult
from devclean.exceptions import ScanError


# ── helpers ────────────────────────────────────────────────────────────────────

def make_structure(base: Path):
    """Build a fake repo tree under base."""
    (base / "project1" / "node_modules").mkdir(parents=True)
    (base / "project2" / "node_modules").mkdir(parents=True)
    (base / "project1" / "src").mkdir(parents=True)         
    (base / "project3" / "venv").mkdir(parents=True)


# ── tests ──────────────────────────────────────────────────────────────────────

def test_finds_matching_folders(tmp_path):
    make_structure(tmp_path)
    results = list(scan(tmp_path, ["node_modules"]))
    assert len(results) == 2
    assert all(r.name == "node_modules" for r in results)


def test_skips_non_matching_folders(tmp_path):
    make_structure(tmp_path)
    results = list(scan(tmp_path, ["node_modules"]))
    # src and venv should not appear
    names = [r.name for r in results]
    assert "src" not in names
    assert "venv" not in names


def test_finds_multiple_targets(tmp_path):
    make_structure(tmp_path)
    results = list(scan(tmp_path, ["node_modules", "venv"]))
    names = [r.name for r in results]
    assert names.count("node_modules") == 2
    assert names.count("venv") == 1


def test_result_has_correct_fields(tmp_path):
    (tmp_path / "my-app" / "node_modules").mkdir(parents=True)
    results = list(scan(tmp_path, ["node_modules"]))

    assert len(results) == 1
    r = results[0]
    assert r.name == "node_modules"
    assert r.path == tmp_path / "my-app" / "node_modules"
    assert r.parent == tmp_path / "my-app"


def test_raises_scan_error_if_path_missing():
    with pytest.raises(ScanError):
        list(scan(Path("/this/does/not/exist"), ["node_modules"]))


def test_raises_scan_error_if_path_is_file(tmp_path):
    fake_file = tmp_path / "not_a_dir.txt"
    fake_file.write_text("hello")
    with pytest.raises(ScanError):
        list(scan(fake_file, ["node_modules"]))


def test_empty_directory_yields_nothing(tmp_path):
    results = list(scan(tmp_path, ["node_modules"]))
    assert results == []


def test_returns_scan_result_instances(tmp_path):
    (tmp_path / "app" / "node_modules").mkdir(parents=True)
    results = list(scan(tmp_path, ["node_modules"]))
    assert all(isinstance(r, ScanResult) for r in results)