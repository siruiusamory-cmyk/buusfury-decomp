"""Toolchain discovery, and the JCALG1 front-end build's known failure mode.

Portable: nothing here requires any tool to actually be installed. The tests
assert that discovery reports absence honestly rather than inventing a path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from buusfury import toolchain


def test_manifest_declares_the_ads_tools():
    manifest = toolchain.load_manifest()
    ids = {t["id"] for t in manifest["tools"]}
    for expected in ("armasm", "armcpp", "armlink", "fromelf", "tcc", "tcpp"):
        assert expected in ids


def test_manifest_declares_the_asset_and_harness_tools():
    manifest = toolchain.load_manifest()
    ids = {t["id"] for t in manifest["tools"]}
    for expected in ("grit", "cmake", "msvc-x86", "python"):
        assert expected in ids


def test_ads12_redistribution_is_recorded_as_prohibited():
    manifest = toolchain.load_manifest()
    assert "PROHIBITED" in manifest["redistribution_policy"]["ads12"]


def test_every_ads_tool_blocks_full_reproduction():
    manifest = toolchain.load_manifest()
    for entry in manifest["tools"]:
        if entry["family"] == "ads12" and entry["id"] in (
            "armasm",
            "armcpp",
            "armlink",
            "fromelf",
        ):
            assert entry["blocks_full_reproduction"] is True


def test_doctor_returns_a_row_for_every_declared_tool():
    statuses = toolchain.doctor(probe_versions=False)
    manifest = toolchain.load_manifest()
    assert {s.id for s in statuses} == {t["id"] for t in manifest["tools"]}


def test_doctor_does_not_invent_paths():
    """A tool is either found, or its path is None. No placeholder strings."""
    for status in toolchain.doctor(probe_versions=False):
        if not status.available:
            assert status.path is None


def test_ads_root_is_none_when_unset_and_not_a_directory(monkeypatch, tmp_path):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    assert toolchain.ads_root() is None
    assert toolchain.ads_root(tmp_path / "does-not-exist") is None


def test_ads_root_accepts_a_real_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("ADS12_ROOT", str(tmp_path))
    assert toolchain.ads_root() == tmp_path


def test_ads_tool_is_found_under_the_root_bin_directory(monkeypatch, tmp_path):
    """A staged fake ADS proves the ADS12_ROOT lookup order actually works."""
    bindir = tmp_path / "Bin"
    bindir.mkdir()
    fake = bindir / "armasm.exe"
    fake.write_bytes(b"MZ")
    monkeypatch.delenv("PATH", raising=False)
    assert toolchain._ads_executable("armasm", tmp_path) == fake


def test_ads_tool_is_absent_when_neither_root_nor_path_has_it(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path))
    assert toolchain._ads_executable("armasm", tmp_path) is None


def test_require_raises_with_the_purpose_when_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("ADS12_ROOT", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(toolchain.ToolchainError) as excinfo:
        toolchain.require("armasm", toolchain.doctor(probe_versions=False))
    assert "ADS12_ROOT" in str(excinfo.value)


def test_build_compress_exe_explains_what_is_missing(tmp_path):
    """Without a fetched reference checkout, say so - do not fail obscurely."""
    from buusfury import assets

    with pytest.raises(assets.AssetError) as excinfo:
        assets.build_compress_exe(tmp_path, tmp_path / "out")
    assert "fetch-reference" in str(excinfo.value)


def test_find_cmake_with_vs_generator_returns_a_path_or_none():
    result = toolchain.find_cmake_with_vs_generator()
    assert result is None or isinstance(result, Path)
