from __future__ import annotations

import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def conftest_module():
    spec = importlib.util.spec_from_file_location("_root_conftest", os.path.join(ROOT, "conftest.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_missing_temp_base_is_created_and_a_file_there_fails_loudly(tmp_path, monkeypatch):
    module = conftest_module()
    missing = tmp_path / "gone" / "pytest-root"
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(missing))
    module.pytest_configure(None)
    assert missing.is_dir()
    occupied = tmp_path / "occupied"
    occupied.write_text("x", encoding="ascii")
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(occupied))
    with pytest.raises(FileExistsError):
        module.pytest_configure(None)
