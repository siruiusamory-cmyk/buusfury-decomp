"""The offline evidence inspector: a bundle read with no emulator in the loop.

`tools/runtime/evidence_report.py` answers what a capture recorded without
relaunching anything: which ROM, which emulator and which build class, which
probe and with what arguments, which repository revision, what was observed, and
whether every referenced artifact still matches the digest the bundle recorded.

The controls here are what make that claim mean something:

1. every recorded field reaches the report;
2. an absent field is reported absent and never defaulted - that is the whole
   difference between an inspector and an assumption;
3. a vanished artifact and a tampered artifact are told apart, and the tampered
   one is reported with the digest actually measured;
4. a malformed, unsupported or incomplete bundle is refused with a non-zero
   exit whose message names the problem;
5. the module source contains no process-launch call, and a real report run
   leaves this machine's emulator process count unchanged.

The fixtures are synthetic throughout: fake paths, fake bytes, digests measured
from those bytes. No canonical ROM and no real emulator is touched.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.runtime import evidence_report

ROOT = Path(__file__).resolve().parents[2]

SCHEMA = "log1-runtime-evidence/1"

#: Every spelling that would put a process on this machine. The inspector must
#: contain none of them: it reads bytes and prints, nothing else.
LAUNCH_CALL_NAMES = (
    "Popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "os.system",
    "os.popen",
    "os.startfile",
    "asyncio.create_subprocess",
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _bundle(tmp_path: Path, **overrides: object) -> tuple[Path, dict[str, object]]:
    """One synthetic bundle whose every digest is measured from real bytes."""
    rom = tmp_path / "rom.gba"
    rom.write_bytes(b"synthetic rom bytes")
    emulator = tmp_path / "mGBA.exe"
    emulator.write_bytes(b"synthetic emulator bytes")
    capture = tmp_path / "capture.txt"
    capture.write_bytes(b"synthetic capture bytes")
    document: dict[str, object] = {
        "schema": SCHEMA,
        "run_id": "20261007-000000-synthetic",
        "created_utc": "2026-10-07T00:00:00Z",
        "repository": {"sha": "A" * 40, "dirty": False},
        "probe": {"tool": "synthetic probe", "arguments": {"rom": "rom.gba"}},
        "rom": {
            "path": str(rom),
            "sha256": _digest(rom),
            "bytes": rom.stat().st_size,
        },
        "emulator": {
            "path": str(emulator),
            "sha256": _digest(emulator),
            "build_class": "packaged-0.10.5-required",
            "label": "packaged mGBA 0.10.5 (win64)",
            "file_version": None,
            "instrumented": None,
        },
        "observations": {"frames": 12},
        "artifacts": [
            {
                "path": str(capture),
                "sha256": _digest(capture),
                "bytes": capture.stat().st_size,
                "role": "capture",
            }
        ],
    }
    document.update(overrides)
    target = tmp_path / "evidence.json"
    _write(target, document)
    return target, document


def _write(target: Path, document: object) -> None:
    target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _emulator_processes() -> int:
    """How many mGBA processes this machine has, read from the OS itself."""
    if os.name == "nt":
        listing = subprocess.run(
            ["tasklist", "/NH"], capture_output=True, text=True, check=False
        ).stdout
    else:
        listing = subprocess.run(
            ["ps", "-A", "-o", "comm="], capture_output=True, text=True, check=False
        ).stdout
    return sum("mgba" in line.lower() for line in listing.splitlines())


def test_the_report_reads_every_recorded_field(tmp_path: Path):
    bundle, document = _bundle(tmp_path)
    report = evidence_report.build_report(bundle)
    repository = document["repository"]
    probe = document["probe"]
    rom = document["rom"]
    emulator = document["emulator"]
    assert document["run_id"] in report
    assert repository["sha"] in report
    assert probe["tool"] in report
    assert rom["sha256"] in report
    assert str(rom["path"]) in report
    assert emulator["sha256"] in report
    assert emulator["build_class"] in report
    assert emulator["label"] in report
    assert "frames: 12" in report
    assert "role=capture" in report


def test_an_absent_field_is_reported_absent_and_never_defaulted(tmp_path: Path):
    """An absent label or version must not be filled in from anywhere."""
    bundle, document = _bundle(tmp_path)
    emulator = document["emulator"]
    assert isinstance(emulator, dict)
    emulator.pop("label")
    bundle.unlink()
    _write(bundle, document)

    report = evidence_report.build_report(bundle)

    assert "recorded label: absent" in report
    assert "recorded file_version: absent" in report
    assert "recorded instrumented: absent" in report
    assert "0.10.5" not in report.split("recorded build_class")[0]
    assert "0.11" not in report


def test_a_vanished_artifact_is_reported_absent(tmp_path: Path):
    bundle, document = _bundle(tmp_path)
    artifacts = document["artifacts"]
    assert isinstance(artifacts, list)
    Path(str(artifacts[0]["path"])).unlink()

    report = evidence_report.build_report(bundle)

    assert "file: absent" in report
    assert "DO NOT match" not in report


def test_a_tampered_artifact_names_the_digest_actually_measured(tmp_path: Path):
    bundle, document = _bundle(tmp_path)
    artifacts = document["artifacts"]
    assert isinstance(artifacts, list)
    captured = Path(str(artifacts[0]["path"]))
    recorded = str(artifacts[0]["sha256"])
    captured.write_bytes(b"different bytes now")

    report = evidence_report.build_report(bundle)

    observed = _digest(captured)
    assert observed != recorded
    assert "DO NOT match the recorded digest" in report
    assert observed.lower() in report.lower()


@pytest.mark.parametrize("shape", ("missing", "null"))
def test_an_unrecorded_digest_is_never_reported_as_a_mismatch(
    tmp_path: Path, shape: str
):
    """No recorded digest means unknown, in both spellings, in both directions.

    A bundle that carries the bytes but no digest has nothing to match and
    nothing to fail to match. Reporting either verdict would be a measurement
    the bundle does not support.
    """
    bundle, document = _bundle(tmp_path)
    entries = [document["rom"], document["emulator"], document["artifacts"][0]]
    for entry in entries:
        if shape == "missing":
            entry.pop("sha256")
        else:
            entry["sha256"] = None
    bundle.unlink()
    _write(bundle, document)

    report = evidence_report.build_report(bundle)

    assert report.count("digest not recorded") == 3
    assert "DO NOT match" not in report
    assert "bytes match the recorded digest" not in report
    for entry in entries:
        assert str(entry["path"]) in report


def test_an_unsupported_schema_is_refused_with_a_nonzero_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    bundle, _ = _bundle(tmp_path, schema="log1-runtime-evidence/2")

    exit_code = evidence_report.main([str(bundle)])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert "schema" in captured.err
    assert "log1-runtime-evidence/2" in captured.err


def test_a_malformed_bundle_is_refused_with_a_nonzero_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    bundle = tmp_path / "evidence.json"
    bundle.write_text("{ this is not json", encoding="utf-8")

    exit_code = evidence_report.main([str(bundle)])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert str(bundle) in captured.err


def test_a_missing_required_key_is_refused_and_named(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    bundle, document = _bundle(tmp_path)
    document.pop("rom")
    bundle.unlink()
    _write(bundle, document)

    exit_code = evidence_report.main([str(bundle)])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert "rom" in captured.err


def test_a_missing_bundle_file_is_refused_with_a_nonzero_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    absent = tmp_path / "not-there.json"

    exit_code = evidence_report.main([str(absent)])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert str(absent) in captured.err


def test_a_report_needs_exactly_one_bundle_path(capsys: pytest.CaptureFixture[str]):
    exit_code = evidence_report.main([])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert "usage" in captured.err


def test_the_inspector_source_contains_no_launch_call():
    source = (ROOT / "tools/runtime/evidence_report.py").read_text(encoding="utf-8")
    found = [name for name in LAUNCH_CALL_NAMES if name in source]
    assert not found, (
        f"the offline inspector contains process-launch spelling(s) {found}; it "
        "must read bytes and print, never start anything"
    )


def test_a_report_run_creates_no_emulator_process(tmp_path: Path):
    bundle, _ = _bundle(tmp_path)
    before = _emulator_processes()

    exit_code = evidence_report.main([str(bundle)])

    after = _emulator_processes()
    assert exit_code == 0
    assert after == before, (
        f"the emulator process count changed across a report run: {before} -> {after}"
    )


def test_the_module_entry_point_prints_the_report(tmp_path: Path):
    bundle, document = _bundle(tmp_path)

    result = subprocess.run(
        [sys.executable, "-m", "tools.runtime.evidence_report", str(bundle)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert document["run_id"] in result.stdout
    assert document["rom"]["sha256"] in result.stdout
