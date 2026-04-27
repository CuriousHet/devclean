from pathlib import Path
import pytest

from devclean.cleaner import clean, CleanResult, get_size
from devclean.scanner import scan

def test_dry_run_does_not_delete(tmp_path):
    (tmp_path / "node_modules").mkdir()
    results = list(scan(tmp_path, ["node_modules"]))
    clean_result = clean(results[0], dry_run=True)

    assert clean_result.path.exists()
    assert clean_result.deleted == False


def test_real_clean_deletes_folder(tmp_path):
    (tmp_path / "node_modules").mkdir()
    results = list(scan(tmp_path, ["node_modules"]))
    clean_result = clean(results[0], dry_run=False)

    assert not clean_result.path.exists()
    assert clean_result.deleted == True


def test_size_greater_than_zero(tmp_path):
    folder = tmp_path / "node_modules"
    folder.mkdir()
    (folder / "package.js").write_bytes(b"x" * (1024 * 1024)) 

    results = list(scan(tmp_path, ["node_modules"]))
    clean_result = clean(results[0], dry_run=True)

    assert clean_result.size_mb == pytest.approx(1.0, abs=0.01)


def test_size_empty_folder(tmp_path):
    (tmp_path / "node_modules").mkdir()
    results = list(scan(tmp_path, ["node_modules"]))
    clean_result = clean(results[0], dry_run=True)

    assert clean_result.size_mb == 0.0


def test_clean_already_deleted_folder(tmp_path):
    folder = tmp_path / "node_modules"
    folder.mkdir()
    results = list(scan(tmp_path, ["node_modules"]))
    r = results[0]

    clean(r, dry_run=False)        # delete for real
    assert not folder.exists()

    clean_result = clean(r, dry_run=False)   # clean again — should not crash
    assert clean_result.deleted == False
    assert clean_result.size_mb == 0.0


def test_clean_returns_clean_result_instance(tmp_path):
    (tmp_path / "node_modules").mkdir()
    results = list(scan(tmp_path, ["node_modules"]))
    clean_result = clean(results[0], dry_run=True)

    assert isinstance(clean_result, CleanResult)


def test_get_size_empty_folder(tmp_path):
    folder = tmp_path / "empty"
    folder.mkdir()

    assert get_size(folder) == 0.0


def test_get_size_with_known_content(tmp_path):
    folder = tmp_path / "node_modules"
    folder.mkdir()
    (folder / "a.js").write_bytes(b"x" * (1024 * 1024))   # 1 MB
    (folder / "b.js").write_bytes(b"x" * (1024 * 1024))   # 1 MB

    assert get_size(folder) == pytest.approx(2.0, abs=0.01)