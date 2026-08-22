from __future__ import annotations

import socket
from pathlib import Path

import pytest

from tools.mgba_probe.runtime import ArmRequest
from tools.runtime.rom011_live_watch import (
    EXECUTABLE_LOAD_CENSUS,
    HumanWatchState,
    Rom011RspClient,
    SELECTED_CODE_LOADS,
    TargetInstance,
    WatchHit,
    build_first_access_watchpoint,
    build_read_watchpoints,
    instrumentation_fallback,
    parse_read_watch_stop,
    reproduction_matches,
)


X = 0x0203DE7C
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _target(*, epoch: int = 1, object_pointer: int = X) -> TargetInstance:
    return TargetInstance(
        load_epoch=epoch,
        map_entry_address=0x0808EB68,
        map_entry_index=39,
        selector=1,
        selected_value=0x08294968,
        descriptor=0x08294948,
        factory_raw=0x08007675,
        factory_fetch=0x08007674,
        object_pointer=object_pointer,
        registry_slot=0x03002A68,
        bounds=(592, 136, 601, 241),
    )


def _registers(*, pc: int = 0x08012340, lr: int = 0x08012001):
    values = [0] * 17
    values[14] = lr
    values[15] = pc
    values[16] = 0x20
    return tuple(values)


def _hit(*, pc: int, offset: int, epoch: int = 1) -> WatchHit:
    return WatchHit(
        stop_reply=f"T05rwatch:{X + offset:08x};",
        watched_address=X + offset,
        field="bounds_min_x",
        field_offset=offset,
        byte_offset=offset,
        object_pointer=X,
        load_epoch=epoch,
        pc=pc,
        lr=0x08010001,
        thumb=True,
        registers=_registers(pc=pc),
    )


def test_dynamic_x_watchpoint_ranges_cover_every_requested_byte_once():
    watchpoints = build_read_watchpoints(X)
    assert len(watchpoints) == 16
    assert {item.byte_offset for item in watchpoints} == {
        *range(0x04, 0x10),
        *range(0x14, 0x18),
    }
    assert all(item.packet().startswith("Z3,") for item in watchpoints)
    assert all(item.packet(remove=True).startswith("z3,") for item in watchpoints)
    with pytest.raises(ValueError, match="EWRAM"):
        build_read_watchpoints(0x0203DE7D)


def test_read_watch_stop_is_exact_and_rejects_wrong_object_or_stop_type():
    watchpoints = build_read_watchpoints(X)
    hit = parse_read_watch_stop(f"T05rwatch:{X + 0x0C:08x};", watchpoints)
    assert hit.field == "callback_reference"
    with pytest.raises(ValueError, match="outside"):
        parse_read_watch_stop("T05rwatch:0203debc;", watchpoints)
    with pytest.raises(ValueError, match="not an mGBA read"):
        parse_read_watch_stop(f"T05awatch:{X + 0x0C:08x};", watchpoints)


def test_rsp_client_allowlist_accepts_only_registered_watch_packets():
    left, right = socket.socketpair()
    try:
        client = Rom011RspClient(left)
        watchpoint = build_read_watchpoints(X)[0]
        packet = client.allow_watchpoint(watchpoint)
        assert packet == f"Z3,{X + 4:x},1"
        with pytest.raises(ValueError, match="not allowlisted"):
            client.command(f"Z3,{X + 5:x},1", timeout=0.01)
    finally:
        left.close()
        right.close()


def test_native_probe_control_uses_mgba_lowercase_hex(monkeypatch: pytest.MonkeyPatch):
    class CaptureSocket:
        def __init__(self):
            self.sent: list[bytes] = []

        def sendall(self, packet: bytes) -> None:
            self.sent.append(packet)

    capture = CaptureSocket()
    client = Rom011RspClient(capture)  # type: ignore[arg-type]
    monkeypatch.setattr(client, "_read_response", lambda timeout: "OK")
    request = ArmRequest(0xAB, X, 0xCD, 0x08294948)
    assert client.arm_native_probe(request) == "OK"
    payload = capture.sent[-1].split(b"$", 1)[1].split(b"#", 1)[0]
    assert payload.startswith(b"qLog1ProbeArm:ab,0203de7c,cd,08294948")
    assert b"DE7C" not in payload


def test_lifecycle_rejects_stale_hit():
    state = HumanWatchState()
    target = _target()
    state.arm(target)
    state.retire(target.object_pointer, target.load_epoch)
    with pytest.raises(ValueError, match="same-epoch"):
        state.accept_hit(
            f"T05rwatch:{X + 4:08x};",
            _registers(),
            build_read_watchpoints(X),
        )


def test_replacement_enforces_one_transition_maximum():
    state = HumanWatchState()
    state.arm(_target())
    state.arm(_target(epoch=2, object_pointer=0x0203DEBC))
    assert state.transition_count == 1
    with pytest.raises(ValueError, match="more than one"):
        state.arm(_target(epoch=3, object_pointer=0x0203DEFC))


def test_event_order_first_hit_stop_and_annotation_separation():
    state = HumanWatchState()
    target = _target()
    state.arm(target)
    hit = state.accept_hit(
        f"T05rwatch:{X + 0x14:08x};",
        _registers(),
        build_read_watchpoints(X),
    )
    assert hit.object_pointer == target.object_pointer
    assert state.events == ["armed", "first_hit"]
    assert state.human_annotation is None
    with pytest.raises(ValueError, match="already captured"):
        state.accept_hit(
            f"T05rwatch:{X + 0x14:08x};",
            _registers(),
            build_read_watchpoints(X),
        )
    state.annotate("Walking toward mansion door.")
    assert state.human_annotation == "Walking toward mansion door."
    assert hit.to_dict()["access_width"] is None


def test_no_hit_requires_live_instrumentation_and_cannot_follow_hit():
    empty = HumanWatchState()
    with pytest.raises(ValueError, match="valid armed"):
        empty.finish_no_hit()
    empty.arm(_target())
    empty.finish_no_hit()
    assert empty.events == ["armed", "no_hit"]

    captured = HumanWatchState()
    captured.arm(_target())
    captured.accept_hit(
        f"T05rwatch:{X + 4:08x};",
        _registers(),
        build_read_watchpoints(X),
    )
    with pytest.raises(ValueError, match="prevents no-hit"):
        captured.finish_no_hit()


def test_reproduction_requires_same_action_pc_and_field_offset():
    original = _hit(pc=0x08012784, offset=0x04)
    repeated = _hit(pc=0x08012784, offset=0x04, epoch=2)
    assert reproduction_matches(original, repeated, same_action=True)
    assert not reproduction_matches(original, repeated, same_action=False)
    assert not reproduction_matches(
        original, _hit(pc=0x0801279C, offset=0x04, epoch=2), same_action=True
    )


def test_unsupported_read_watchpoint_falls_back_to_targeted_code_breakpoints():
    assert instrumentation_fallback("OK") == "read_watchpoints"
    assert instrumentation_fallback("") == "targeted_code_breakpoints"
    assert instrumentation_fallback("E01") == "targeted_code_breakpoints"
    assert instrumentation_fallback(None) == "targeted_code_breakpoints"
    assert (
        instrumentation_fallback("OK", playable=False)
        == "targeted_code_breakpoints"
    )


def test_static_load_census_and_late_selected_code_stops_cover_requested_fields():
    assert {item.field_offset for item in EXECUTABLE_LOAD_CENSUS} == {
        0x00,
        0x04,
        0x06,
        0x08,
        0x0A,
        0x0C,
        0x14,
    }
    assert {item.pc for item in SELECTED_CODE_LOADS} == {
        0x080075CC,
        0x0801277A,
        0x08012828,
        0x080128AA,
    }
    assert len(SELECTED_CODE_LOADS) == 4
    assert all(
        item.field_offset in {0x00, 0x0C, 0x14}
        for item in SELECTED_CODE_LOADS
    )
    watchpoint = build_first_access_watchpoint(X)
    assert watchpoint.address == X + 4
    assert watchpoint.packet() == f"Z3,{X + 4:x},1"
    for routine in (0x080126D4, 0x080127AE, 0x08012846):
        loads = [
            item for item in EXECUTABLE_LOAD_CENSUS if item.routine_entry == routine
        ]
        first = min(loads, key=lambda item: item.pc)
        assert first.field_offset == 0x04


def test_code_load_hit_requires_exact_current_x_effective_address():
    candidate = next(
        item for item in EXECUTABLE_LOAD_CENSUS if item.pc == 0x08012748
    )
    registers = list(_registers(pc=candidate.pc))
    registers[candidate.base_register] = X + 4
    registers[candidate.index_register] = 0
    state = HumanWatchState()
    state.arm(_target())
    hit = state.accept_code_hit(
        "T05", registers, candidate, (592).to_bytes(2, "little", signed=True)
    )
    assert hit.effective_address == X + 4
    assert hit.value_signed == 592
    assert hit.to_dict()["access_width"] == 2

    wrong = list(registers)
    wrong[candidate.base_register] += 0x40
    fresh = HumanWatchState()
    fresh.arm(_target())
    with pytest.raises(ValueError, match="not current X"):
        fresh.accept_code_hit("T05", wrong, candidate, b"\x50\x02")


def test_human_readiness_lua_never_automates_input():
    lua = (
        PROJECT_ROOT / "tools/runtime/rom011_human_ready.lua"
    ).read_text(encoding="utf-8")
    injector = (
        PROJECT_ROOT / "tools/runtime/inject_mgba_lua.ps1"
    ).read_text(encoding="utf-8")
    assert "setKeys" not in lua
    assert "addKey" not in lua
    assert "clearKey" not in lua
    assert "rom011_human_ready.lua" in injector


def test_phase1_route_is_cancelled_before_armed_marker():
    route = (
        PROJECT_ROOT / "tools/runtime/rom009_clean_route.lua"
    ).read_text(encoding="utf-8")
    stop_setup = (
        PROJECT_ROOT / "tools/runtime/rom011_stop_setup.lua"
    ).read_text(encoding="utf-8")
    runner = (
        PROJECT_ROOT / "tools/runtime/rom011_live_watch.py"
    ).read_text(encoding="utf-8")
    assert "rom011_cancel_clean_route = stop_route" in route
    assert "emu:setKeys(0)" in route
    assert "rom011_cancel_clean_route()" in stop_setup
    assert "setKeys" not in stop_setup
    legacy_setup = runner.index("setup_stopped = (")
    legacy_marker = runner.index('_write_new_json(marker, armed)', legacy_setup)
    assert legacy_setup < legacy_marker
    native_arm = runner.index("request = ArmRequest(")
    native_marker = runner.index('_write_new_json(marker, armed)', native_arm)
    assert native_marker < legacy_setup
    native_setup = runner[native_arm:native_marker]
    assert "_inject_lua(" not in native_setup
    assert "installed_breakpoints - lifecycle_breakpoints" in native_setup
    assert "_remove_breakpoint(client, address)" in native_setup
    assert '"retired_discovery_breakpoints"' in native_setup
    assert '"active_lifecycle_breakpoints"' in native_setup
    assert runner.count("for address in sorted(discovery_breakpoints):") >= 2
    assert '"input_stopped": setup_stopped is not None' in runner
    assert "except subprocess.CalledProcessError as exc:" in runner


def test_live_runner_starts_with_supported_stop_query_and_marks_capture_ready():
    runner = (
        PROJECT_ROOT / "tools/runtime/rom011_live_watch.py"
    ).read_text(encoding="utf-8")
    assert 'client.command("qSupported")' not in runner
    assert 'initial_status = client.command("?")' in runner
    assert 'run_root / "capture-ready.json"' in runner


def test_idle_performance_benchmark_injects_no_input():
    benchmark = (
        PROJECT_ROOT / "tools/runtime/rom011_idle_benchmark.lua"
    ).read_text(encoding="utf-8")
    injector = (
        PROJECT_ROOT / "tools/runtime/inject_mgba_lua.ps1"
    ).read_text(encoding="utf-8")
    assert "setKeys" not in benchmark
    assert "addKey" not in benchmark
    assert "clearKey" not in benchmark
    assert "frame == 180" in benchmark
    assert "[string]$MarkerPath" in injector
    runner = (
        PROJECT_ROOT / "tools/runtime/rom011_live_watch.py"
    ).read_text(encoding="utf-8")
    assert "timeout=45" in runner
