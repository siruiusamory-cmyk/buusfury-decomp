"""WORKBENCH-001 critical-path test 4: the ROM-overwrite safety guard.

The guard is a module-level, Qt-free function so the #1 safety invariant can be
proven without constructing any widget. These tests are the fail-closed contract:
a generated file path equal to the source ROM is rejected; distinct file paths
are allowed; the SAME parent directory with a DIFFERENT filename is allowed.
"""

from pathlib import Path

from tools.webfoot.workbench.build_panel import is_safe_output_path, output_file_for


def test_identical_file_path_is_rejected(tmp_path):
    rom = tmp_path / "buus_fury.gba"
    rom.write_bytes(b"\x00")
    assert is_safe_output_path(rom, rom) is False


def test_distinct_file_paths_are_allowed(tmp_path):
    rom = tmp_path / "src" / "buus_fury.gba"
    out = tmp_path / "out" / "buus_fury_modified.gba"
    rom.parent.mkdir()
    rom.write_bytes(b"\x00")
    out.parent.mkdir()
    assert is_safe_output_path(out, rom) is True


def test_same_dir_different_filename_is_allowed(tmp_path):
    rom = tmp_path / "buus_fury.gba"
    rom.write_bytes(b"\x00")
    out = output_file_for(tmp_path, "buus_fury_usa_rev0")
    # Same parent directory as the source ROM, different filename -> allowed.
    assert out.parent == rom.parent
    assert is_safe_output_path(out, rom) is True


def test_output_file_convention():
    out = output_file_for(Path("/tmp/out"), "buus_fury_usa_rev0")
    assert out.name == "buus_fury_usa_rev0_modified.gba"
