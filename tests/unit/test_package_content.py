"""The staged-package census, its positive controls, and the suffix parity.

A guard is only worth its lines if it catches the thing it names, so every screen
below is exercised by a staged file that must be caught and by a clean package that
must not be. The last test is the one that keeps the two forbidden-suffix lists
from drifting apart: a release protected by the weaker of two lists is protected by
nothing.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

from tools.quality import architecture, public_release
from tools.quality.package_content import LIMITATIONS, census, main

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: A machine path, assembled at run time on purpose. Written literally it would be
#: a finding in this test file itself, which the tree-wide screen reads.
MACHINE_PATH = "C:" + chr(92) + "Users" + chr(92) + "someone" + chr(92) + "rom.gba"
#: The same reasoning: a path naming a local checkout.
WORKTREE_PATH = "build/" + "log1-remake-" + "example" + "/dist/app.exe"


def _stage(tmp_path: Path) -> Path:
    """A package that would pass: one executable and one README."""
    package = tmp_path / "DragonByte-Z-release"
    package.mkdir()
    (package / "app.exe").write_bytes(b"MZ\x90\x00" + bytes(range(256)))
    (package / "README.txt").write_text(
        "DragonByte Z\n\nRun app.exe. You supply your own legally obtained ROM.\n",
        encoding="utf-8",
    )
    return package


def _codes(report: dict) -> set[str]:
    return {item["code"] for item in report["findings"]}


def test_a_clean_package_has_no_findings(tmp_path):
    report = census(_stage(tmp_path))
    assert report["findings"] == []
    assert report["files"] == 2
    assert report["unreadable"] == []
    assert report["binary_files"] == 1 and report["text_files"] == 1


def test_a_save_or_save_state_in_the_package_is_a_finding(tmp_path):
    package = _stage(tmp_path)
    for name in ("slot.sav", "state.ss1", "dump.dump"):
        (package / name).write_bytes(b"\x00" * 16)
    report = census(package)
    assert _codes(report) == {"forbidden-artifact"}
    assert len(report["findings"]) == 3


def test_a_rom_in_the_package_is_a_finding(tmp_path):
    package = _stage(tmp_path)
    (package / "derivative.gba").write_bytes(b"\x00" * 16)
    assert "forbidden-artifact" in _codes(census(package))


def test_a_machine_path_in_a_staged_text_file_is_a_finding(tmp_path):
    package = _stage(tmp_path)
    (package / "notes.txt").write_text(f"built from {MACHINE_PATH}\n", encoding="utf-8")
    report = census(package)
    assert "private-path-residue" in _codes(report)
    assert report["findings"][0]["line"] == 1


def test_a_local_worktree_name_in_a_staged_text_file_is_a_finding(tmp_path):
    package = _stage(tmp_path)
    (package / "build.log").write_text(f"staged {WORKTREE_PATH}\n", encoding="utf-8")
    assert "private-path-residue" in _codes(census(package))


def test_a_binary_file_is_counted_and_not_searched(tmp_path):
    package = _stage(tmp_path)
    (package / "payload.dat").write_bytes(bytes(range(256)) * 4)
    report = census(package)
    assert report["binary_files"] == 2
    assert report["findings"] == []


def test_a_declared_resource_that_is_missing_is_a_finding(tmp_path):
    package = _stage(tmp_path)
    report = census(package, required=("tools/webfoot/data/roms.yaml",))
    assert _codes(report) == {"required-resource-missing"}
    assert report["required"] == ["tools/webfoot/data/roms.yaml"]


def test_a_declared_resource_that_is_present_is_not_a_finding(tmp_path):
    package = _stage(tmp_path)
    report = census(package, required=("README.txt",))
    assert report["findings"] == []


def test_the_report_states_what_the_census_cannot_see(tmp_path):
    report = census(_stage(tmp_path))
    assert report["limitations"] == list(LIMITATIONS)
    assert any("compressed" in statement for statement in report["limitations"])


def test_the_entry_point_exits_zero_on_a_clean_package(tmp_path, capsys):
    assert main([str(_stage(tmp_path))]) == 0
    assert "0 finding(s)" in capsys.readouterr().out


def test_the_entry_point_exits_non_zero_on_a_finding(tmp_path, capsys):
    package = _stage(tmp_path)
    (package / "slot.sav").write_bytes(b"\x00")
    assert main([str(package)]) == 1
    assert "forbidden-artifact" in capsys.readouterr().out
    assert main([str(package), "--no-fail"]) == 0


def test_the_entry_point_writes_a_json_report(tmp_path):
    package = _stage(tmp_path)
    destination = tmp_path / "report.json"
    assert main([str(package), "--json", str(destination)]) == 0
    assert '"code_counts"' in destination.read_text(encoding="utf-8")
    # No machine path in the report: it is a document that may be kept.
    assert str(tmp_path) not in destination.read_text(encoding="utf-8")


def test_the_entry_point_refuses_something_that_is_not_a_directory(tmp_path, capsys):
    assert main([str(tmp_path / "not-there")]) == 2
    assert "is not a directory" in capsys.readouterr().err


def test_the_forbidden_suffix_lists_cannot_drift():
    """The static guard and the packaging-time probe refuse the same files."""
    script = (REPOSITORY_ROOT / "scripts" / "randomizer-release.ps1").read_text(
        encoding="utf-8"
    )
    block = re.search(
        r"RandomizerForbiddenExtensions\s*=\s*@\((.*?)\)", script, re.DOTALL
    )
    assert block is not None
    declared = set(re.findall(r"'([^']+)'", block.group(1)))
    assert declared == set(public_release.FORBIDDEN_SUFFIXES)
    # The census imports the release list rather than keeping a third one, and the
    # architecture list is the tracked-file rule: narrower is correct there, but a
    # suffix it refuses must never be one the release guard silently allows.
    assert set(architecture.NEVER_TRACKED_SUFFIXES) - set(
        public_release.FORBIDDEN_SUFFIXES
    ) == {".gbc", ".mss", ".raw"}
