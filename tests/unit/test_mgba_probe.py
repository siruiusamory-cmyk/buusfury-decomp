from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.mgba_probe.benchmark import analyze_vcount_samples, reanalyze_gate_report
from tools.mgba_probe.runtime import (
    FACTORY_FETCH,
    FACTORY_RAW,
    PROFILE_SHA256,
    ArmRequest,
    instrumented_environment,
    launcher_command,
    overlap_for_read,
    parse_event,
    watched_ranges,
    verify_instrumented_mgba,
)


X = 0x0203DE7C


def _event(**overrides: object) -> dict[str, object]:
    registers = ["0x00000000"] * 16
    registers[14] = "0x08012001"
    registers[15] = "0x0801274C"
    value: dict[str, object] = {
        "schema": "log1-mgba-read-probe-v1",
        "profile_sha256": PROFILE_SHA256,
        "event_id": 1,
        "control_sequence": 4,
        "target": f"0x{X:08X}",
        "load_epoch": 3,
        "descriptor": "0x08294948",
        "factory_raw": f"0x{FACTORY_RAW:08X}",
        "factory_fetch": f"0x{FACTORY_FETCH:08X}",
        "read_address": f"0x{X + 4:08X}",
        "relative_offset": 4,
        "access_width": 2,
        "overlap_start": f"0x{X + 4:08X}",
        "overlap_end_exclusive": f"0x{X + 6:08X}",
        "instruction_pc": "0x08012748",
        "lr": registers[14],
        "raw_r15": registers[15],
        "cpsr": "0x00000020",
        "registers": registers,
    }
    value.update(overrides)
    return value


def test_dynamic_ranges_and_overlap_preserve_original_width():
    assert watched_ranges(X) == ((X + 4, X + 0x10), (X + 0x14, X + 0x18))
    assert overlap_for_read(X, X + 2, 4) is None
    assert overlap_for_read(X, X + 5, 4) == (X + 4, X + 8)
    assert overlap_for_read(X, X + 3, 2) is None
    assert overlap_for_read(X, X + 5, 2) == (X + 4, X + 6)
    assert overlap_for_read(X, X + 0x10, 4) is None
    with pytest.raises(ValueError, match="1, 2, or 4"):
        overlap_for_read(X, X + 4, 3)


def test_vcount_benchmark_counts_scanline_wraps():
    samples = [(index * 0.01, (100 + index * 136) % 228) for index in range(301)]
    result = analyze_vcount_samples(samples)
    assert result["fps"] == pytest.approx(59.649, rel=0.001)


def test_vcount_benchmark_ignores_same_tick_samples():
    samples = [(index * 0.01, (100 + index * 136) % 228) for index in range(301)]
    samples.insert(1, samples[0])
    result = analyze_vcount_samples(samples)
    assert result["fps"] == pytest.approx(59.649, rel=0.001)


def test_vcount_benchmark_rejects_ambiguous_sampling():
    with pytest.raises(RuntimeError, match="unambiguous"):
        analyze_vcount_samples([(0.02 * index, index % 228) for index in range(200)])


def test_performance_report_reanalysis_uses_raw_samples(tmp_path: Path):
    report = {
        "schema": "log1-mgba-performance-gate-v1",
        "results": [{"case": name} for name in ("stock", "instrumented-disarmed", "instrumented-armed")],
    }
    (tmp_path / "performance-gate.json").write_text(json.dumps(report), encoding="utf-8")
    samples = [(index * 0.01, (100 + index * 136) % 228) for index in range(301)]
    for name in ("stock", "instrumented-disarmed", "instrumented-armed"):
        case = tmp_path / name
        case.mkdir()
        (case / "vcount-samples.json").write_text(json.dumps(samples), encoding="utf-8")
    updated = reanalyze_gate_report(tmp_path)
    assert updated["analysis_revision"] == "direct-vcount-wrap-v2"
    assert updated["acceptance"]["automated_near_realtime_observation_passed"] is True
    assert updated["acceptance"]["complete"] is False
    assert updated["quantitative_throughput_ratio_valid"] is False


def test_wrong_or_out_of_range_x_is_rejected():
    with pytest.raises(ValueError, match="EWRAM"):
        watched_ranges(0x03000000)
    with pytest.raises(ValueError, match="factory"):
        ArmRequest(1, X, 1, 0x08294948, factory_raw=0x08007677)


def test_event_parser_preserves_width_registers_and_identity(tmp_path: Path):
    path = tmp_path / "event.json"
    path.write_text(json.dumps(_event()), encoding="utf-8")
    event = parse_event(path)
    assert event.address == X + 4
    assert event.access_width == 2
    assert event.instruction_pc == 0x08012748
    assert event.lr == 0x08012001
    assert event.registers[14] == event.lr


def test_rsp_event_parser_preserves_fixed_first_hit_state():
    mapping = _event()
    registers = mapping["registers"]
    assert isinstance(registers, list)
    fields = [
        "LOG1E1",
        "0000000000000001",
        "0000000000000004",
        f"{X:08X}",
        "00000003",
        "08294948",
        f"{FACTORY_RAW:08X}",
        f"{FACTORY_FETCH:08X}",
        f"{X + 4:08X}",
        "00000004",
        "00000002",
        f"{X + 4:08X}",
        f"{X + 6:08X}",
        "08012748",
        "00000020",
        *(str(value)[2:] for value in registers),
    ]
    from tools.mgba_probe.runtime import ReadEvent

    event = ReadEvent.from_rsp(",".join(fields))
    assert event.event_id == 1
    assert event.instruction_pc == 0x08012748
    assert event.access_width == 2


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"target": "0x0203DEBC"}, "relative offset"),
        ({"load_epoch": 0}, "load epoch"),
        ({"factory_raw": "0x08007677"}, "factory identity"),
        ({"access_width": 1, "overlap_end_exclusive": f"0x{X + 6:08X}"}, "overlap"),
        ({"registers": ["0x00000000"] * 15}, "r0-r15"),
    ],
)
def test_event_parser_fails_closed(override: dict[str, object], message: str, tmp_path: Path):
    path = tmp_path / "event.json"
    path.write_text(json.dumps(_event(**override)), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        parse_event(path)


def test_launcher_is_command_driven_and_loads_state(tmp_path: Path):
    command = launcher_command(
        tmp_path / "mgba-sdl.exe",
        tmp_path / "game.gba",
        tmp_path / "clean.ss1",
    )
    assert "--gdb" in command
    assert "--savestate" in command
    assert "--log1-probe-control" not in command
    assert "--log1-probe-event" not in command
    assert all("Scripting" not in item for item in command)


def test_instrumented_build_verification_is_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"instrumented")
    runtime_bin = tmp_path / "runtime"
    runtime_bin.mkdir()
    (runtime_bin / "SDL2.dll").write_bytes(b"")
    (runtime_bin / "libepoxy-0.dll").write_bytes(b"")
    from tools.mgba_probe import runtime

    manifest = {
        "schema": runtime.BUILD_SCHEMA,
        "source_commit": runtime.SOURCE_COMMIT,
        "patch_sha256": runtime.sha256(runtime.PATCH_PATH),
        "executable_sha256": runtime.sha256(executable),
        "runtime_bin": str(runtime_bin),
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(
        runtime.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout=f"mGBA 0.10.5 ({runtime.SOURCE_COMMIT})"
        ),
    )
    assert verify_instrumented_mgba(executable, manifest_path) == manifest
    assert str(runtime_bin) in instrumented_environment(manifest)["PATH"]

    manifest["source_commit"] = "0" * 40
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="source commit"):
        verify_instrumented_mgba(executable, manifest_path)

    manifest["source_commit"] = runtime.SOURCE_COMMIT
    manifest["patch_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="patch hash"):
        verify_instrumented_mgba(executable, manifest_path)
