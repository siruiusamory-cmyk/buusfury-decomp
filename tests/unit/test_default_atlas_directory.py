"""WB-005: `_default_atlas_directory` must resolve next to the exe when frozen
(PyInstaller) and stay module-relative otherwise."""

from pathlib import Path

from tools.webfoot.cli import _default_atlas_directory


def test_non_frozen_is_module_relative(monkeypatch):
    monkeypatch.delattr("sys.frozen", raising=False)
    result = _default_atlas_directory()
    # Repo layout: <repo>/build/atlas, derived from the module path.
    assert result.parts[-2:] == ("build", "atlas")
    expected = Path(__import__("tools.webfoot.cli", fromlist=["__file__"]).__file__)
    assert result == expected.resolve().parents[2] / "build" / "atlas"


def test_frozen_is_next_to_exe(monkeypatch, tmp_path):
    exe = tmp_path / "DragonByte Z.exe"
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(exe), raising=False)
    result = _default_atlas_directory()
    assert result == tmp_path.resolve() / "build" / "atlas"
