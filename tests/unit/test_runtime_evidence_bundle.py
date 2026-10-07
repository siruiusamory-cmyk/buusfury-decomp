"""Determinism, refusal and measurement tests for the runtime evidence bundle.

Everything here is synthetic: fake paths, fake digests, a synthetic ROM-sized
byte string. No emulator process is launched and no capture is read.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

from tools.runtime import evidence_bundle as bundle


def _emulator() -> dict[str, object]:
    return {
        "path": "C:/synthetic/mGBA.exe",
        "sha256": "A" * 64,
        "build_class": "packaged-0.10.5-required",
        "label": "synthetic packaged build",
        "file_version": None,
        "instrumented": None,
    }


def _document() -> dict[str, object]:
    return {
        "schema": bundle.SCHEMA,
        "run_id": "probe-00000000000000000000000000000000",
        "created_utc": "2026-10-07T00:00:00Z",
        "repository": {"sha": None, "dirty": False},
        "probe": {
            "tool": "tools.runtime.rom008_query_probe",
            "arguments": {"timeout_seconds": 25.0},
        },
        "rom": {"path": "C:/synthetic/game.gba", "sha256": "B" * 64, "bytes": 8388608},
        "emulator": _emulator(),
        "observations": {"stops": 3},
        "artifacts": [
            {
                "path": "states/input.ss1",
                "sha256": "C" * 64,
                "bytes": 4,
                "role": "savestate",
            }
        ],
    }


def test_schema_constant_is_the_frozen_version() -> None:
    assert bundle.SCHEMA == "log1-runtime-evidence/1"
    assert bundle.EVIDENCE_FILENAME == "evidence.json"


def test_round_trip_is_byte_identical(tmp_path: Path) -> None:
    first = bundle.write_bundle(tmp_path / "a" / "evidence.json", _document())
    second = bundle.write_bundle(tmp_path / "b" / "evidence.json", _document())
    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes() == bundle.serialize_bundle(_document()).encode("utf-8")


def test_serialization_is_exactly_the_frozen_form() -> None:
    text = bundle.serialize_bundle(_document())
    assert text == json.dumps(_document(), sort_keys=True, indent=2) + "\n"
    assert text.startswith('{\n  "artifacts"')
    assert text.endswith("}\n")


def test_unsupported_schema_is_refused() -> None:
    document = _document()
    document["schema"] = "log1-runtime-evidence/2"
    with pytest.raises(ValueError, match="schema"):
        bundle.validate_bundle(document)


def test_missing_required_key_is_refused_by_name() -> None:
    document = _document()
    del document["rom"]
    with pytest.raises(ValueError, match="rom"):
        bundle.validate_bundle(document)


def test_unknown_extra_top_level_key_is_accepted() -> None:
    document = _document()
    document["future_extension"] = {"anything": [1]}
    accepted = bundle.validate_bundle(document)
    assert accepted["future_extension"] == {"anything": [1]}
    assert set(accepted) - set(document) == set()


def test_unsupported_emulator_build_class_is_refused() -> None:
    document = _document()
    document["emulator"]["build_class"] = "asserted-by-caller"
    with pytest.raises(ValueError, match="build_class"):
        bundle.validate_bundle(document)


def test_write_never_emits_a_byte_order_mark(tmp_path: Path) -> None:
    written = bundle.write_bundle(tmp_path / "evidence.json", _document())
    raw = written.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert raw.startswith(b"{")
    assert b"\r\n" not in raw


def test_read_bundle_refuses_a_missing_key(tmp_path: Path) -> None:
    document = _document()
    del document["emulator"]
    path = tmp_path / "evidence.json"
    path.write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValueError, match="emulator"):
        bundle.read_bundle(path)


def test_emulator_identity_refuses_an_unmeasured_path(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not found"):
        bundle.emulator_identity(tmp_path / "not-mGBA.exe")


def test_build_bundle_measures_rom_artifact_and_timestamp(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(bundle, "emulator_identity", lambda *a, **k: _emulator())
    rom = tmp_path / "game.gba"
    rom.write_bytes(b"synthetic-rom")
    state = tmp_path / "input.ss1"
    state.write_bytes(b"synthetic-state")

    built = bundle.build_bundle(
        run_id="probe-1",
        repository={"sha": None, "dirty": False},
        probe={"tool": "synthetic", "arguments": {"max_stops": 2}},
        rom=rom,
        emulator=tmp_path / "mGBA.exe",
        observations={"stops": 0},
        artifacts={state: "savestate"},
    )

    assert built["rom"] == {
        "path": str(rom),
        "sha256": hashlib.sha256(b"synthetic-rom").hexdigest(),
        "bytes": len(b"synthetic-rom"),
    }
    assert built["artifacts"] == [
        {
            "path": str(state),
            "sha256": hashlib.sha256(b"synthetic-state").hexdigest(),
            "bytes": len(b"synthetic-state"),
            "role": "savestate",
        }
    ]
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(built["created_utc"])
    )
    assert built["schema"] == bundle.SCHEMA
    assert built["repository"] == {"sha": None, "dirty": False}


#: The three packaged-build probes that own a run directory of their own.
STANDARD_PROBES = (
    "tools/runtime/rom006_gdb_probe.py",
    "tools/runtime/rom007_factory_probe.py",
    "tools/runtime/rom008_query_probe.py",
)

#: The instrumented-build probes and the performance gate, same one call each.
INSTRUMENTED_PROBES = (
    "tools/mgba_probe/benchmark.py",
    "tools/runtime/rom011_live_watch.py",
    "tools/runtime/rom012_live_containment.py",
)

ROOT = Path(__file__).resolve().parents[2]


def test_write_run_bundle_names_the_run_directory_and_skips_missing_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(bundle, "emulator_identity", lambda *a, **k: _emulator())
    monkeypatch.setattr(
        bundle, "repository_identity", lambda root: {"sha": None, "dirty": False}
    )
    run_root = tmp_path / "probe-abc"
    run_root.mkdir()
    rom = tmp_path / "game.gba"
    rom.write_bytes(b"synthetic-rom")
    state = run_root / "input.ss1"
    state.write_bytes(b"synthetic-state")

    written = bundle.write_run_bundle(
        run_root,
        tool="tools.runtime.synthetic",
        arguments={"max_stops": 2},
        rom=rom,
        emulator=tmp_path / "mGBA.exe",
        observations={"stops": 1},
        artifacts={state: "input-savestate", run_root / "never-written.sav": "savegame"},
    )

    assert written == run_root / "evidence.json"
    document = json.loads(written.read_text(encoding="utf-8"))
    assert document["run_id"] == "probe-abc"
    assert document["probe"] == {
        "tool": "tools.runtime.synthetic",
        "arguments": {"max_stops": 2},
    }
    assert document["observations"] == {"stops": 1}
    assert [item["role"] for item in document["artifacts"]] == ["input-savestate"]
    assert document["artifacts"][0]["path"] == str(state)


def test_each_standard_probe_emits_one_bundle_through_the_one_module() -> None:
    for relative in STANDARD_PROBES:
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert (
            "from tools.runtime.evidence_bundle import write_run_bundle" in source
        ), relative
        assert source.count("write_run_bundle(") == 1, relative


def test_rom009_and_the_rom010_flow_inherit_rom008_coverage() -> None:
    import tools.runtime.rom008_query_probe as rom008
    import tools.runtime.rom009_callback_probe as rom009

    assert rom009.run_probe is rom008.run_probe
    assert "write_run_bundle" not in (
        ROOT / "tools/runtime/rom009_callback_probe.py"
    ).read_text(encoding="utf-8")


def test_instrumented_paths_emit_one_bundle_with_the_manifest_attached() -> None:
    for relative in INSTRUMENTED_PROBES:
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert (
            "from tools.runtime.evidence_bundle import write_run_bundle" in source
        ), relative
        assert source.count("write_run_bundle(") == 1, relative
        assert "instrumented_manifest=manifest_path" in source, relative

    benchmark = (ROOT / "tools/mgba_probe/benchmark.py").read_text(encoding="utf-8")
    assert '"stock_control"' in benchmark, (
        "the gate's stock control belongs in observations, not as the bundle's "
        "emulator: the emulator under test is the instrumented build"
    )


#: The run's own primary output, which the bundle must never gate.
PRIMARY_WRITE = {
    "tools/mgba_probe/benchmark.py": "report_path.write_text(",
    "tools/runtime/rom011_live_watch.py": '_write_new_json(run_root / "result.json", output)',
    "tools/runtime/rom012_live_containment.py": '_write_new_json(run_root / "result.json", output)',
}


def test_the_bundle_never_gates_the_runs_own_output() -> None:
    for relative, anchor in PRIMARY_WRITE.items():
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert source.index(anchor) < source.index("write_run_bundle("), (
            f"{relative}: the bundle is written before the run's own output, so a "
            "bundle failure would cost a completed capture its primary record"
        )


def test_instrumented_emulator_identity_carries_the_attested_manifest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    manifest_path = tmp_path / "log1-probe-build.json"
    manifest_path.write_text("{}", encoding="utf-8")
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"synthetic-emulator")
    monkeypatch.setattr(
        bundle,
        "verify_instrumented_mgba",
        lambda *a, **k: {
            "source_commit": "26b7884bc25a5933960f3cdcd98bac1ae14d42e2",
            "patch_sha256": "8ee9d92dd1d69fda96f7c31bc8b10e17d6aa7195b56ab103e56cb5f8d9583346",
            "executable_sha256": "0698a84715adcd8fd34dc45837c01ef2c52e7eefd5ad19b6def72f8c8d791641",
            "version_output": "synthetic instrumented 0.10.5",
        },
    )

    measured = bundle.emulator_identity(
        executable, instrumented_manifest=manifest_path
    )

    assert measured["build_class"] == "instrumented-required"
    assert measured["sha256"] == (
        "0698a84715adcd8fd34dc45837c01ef2c52e7eefd5ad19b6def72f8c8d791641"
    )
    assert measured["label"] == "synthetic instrumented 0.10.5"
    assert measured["instrumented"] == {
        "manifest_path": str(manifest_path),
        "source_commit": "26b7884bc25a5933960f3cdcd98bac1ae14d42e2",
        "patch_sha256": "8ee9d92dd1d69fda96f7c31bc8b10e17d6aa7195b56ab103e56cb5f8d9583346",
    }


def test_unknown_repository_block_validates_and_round_trips(tmp_path: Path) -> None:
    document = _document()
    document["repository"] = {"sha": None, "dirty": None}

    first = bundle.write_bundle(tmp_path / "a" / "evidence.json", document)
    second = bundle.write_bundle(tmp_path / "b" / "evidence.json", document)

    assert first.read_bytes() == second.read_bytes()
    assert json.loads(first.read_text(encoding="utf-8"))["repository"] == {
        "sha": None,
        "dirty": None,
    }
    assert bundle.validate_bundle(document)["repository"] == {
        "sha": None,
        "dirty": None,
    }


def test_repository_identity_reports_unknown_when_git_cannot_answer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def refuse(*arguments: object) -> str:
        raise subprocess.CalledProcessError(128, ["git"])

    monkeypatch.setattr(bundle, "_git", refuse)

    assert bundle.repository_identity(tmp_path) == {"sha": None, "dirty": None}


def test_repository_identity_measures_a_commit_and_dirty_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def answer(*arguments: object) -> str:
        return "a" * 40 if arguments[-1] == "HEAD" else " M tools/x.py"

    monkeypatch.setattr(bundle, "_git", answer)

    assert bundle.repository_identity(tmp_path) == {"sha": "a" * 40, "dirty": True}
