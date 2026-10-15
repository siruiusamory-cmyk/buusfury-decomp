from pathlib import Path
import subprocess

import pytest

from tools.runtime.rom008_object_trace import MANAGER, TARGET_FACTORY_RAW, LoadIdentity
from tools.runtime.rom009_object_trace import DynamicExactObjectTracker
from tools.runtime.rom010_probe_status import (
    classify_probe_exception,
    classify_probe_result,
    probe_exit_code,
    write_probe_output,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _result(**overrides):
    result = {
        "orchestration": {
            "inputs_verified": True,
            "emulator_launched": True,
            "lua_ready": True,
            "debugger_attached": True,
            "breakpoints_installed": True,
            "runtime_load_verified": True,
            "target_live": True,
        },
        "complete": False,
        "callbacks": [],
        "exact_query": None,
        "rejecting_guard": None,
    }
    result.update(overrides)
    return result


def _load() -> LoadIdentity:
    return LoadIdentity(0x0808E2E0, 0, 1, 0x08070000, 0x08200000)


def _live_tracker() -> DynamicExactObjectTracker:
    tracker = DynamicExactObjectTracker()
    tracker.begin_population(MANAGER, _load())
    tracker.accept_factory(0x08290000, TARGET_FACTORY_RAW)
    tracker.commit_insertion(
        manager=MANAGER,
        returned_object=0x0203DE7C,
        old_count=0,
        new_count=1,
        slot=0x03002A68,
    )
    return tracker


def test_process_and_connection_failures_have_distinct_codes(tmp_path: Path):
    mgba = tmp_path / "mGBA.exe"
    absent = FileNotFoundError(2, "not found", str(mgba))
    assert classify_probe_exception(absent, mgba_path=mgba).code == "mgba_absent"
    assert (
        classify_probe_exception(RuntimeError("TCP port 2345 already in use")).code
        == "debugger_port_occupied"
    )
    assert (
        classify_probe_exception(TimeoutError("mGBA GDB port did not open: refused")).code
        == "debugger_connection_timeout"
    )


def test_lua_timeout_wrong_process_and_breakpoint_failure_are_distinct():
    timeout = subprocess.TimeoutExpired(["powershell.exe"], 30)
    assert classify_probe_exception(timeout).code == "lua_injection_timeout"
    wrong_process = subprocess.CalledProcessError(
        1,
        ["powershell.exe"],
        stderr="mGBA did not report the loaded Buu's Fury ROM",
    )
    assert classify_probe_exception(wrong_process).code == "wrong_mgba_process"
    assert (
        classify_probe_exception(RuntimeError("breakpoint rejected at 0x080126D4")).code
        == "breakpoint_installation_failed"
    )


def test_successful_attach_is_separate_from_research_failure():
    status = classify_probe_result(_result())
    assert status.infrastructure == "succeeded"
    assert status.research == "inconclusive"
    assert status.code == "research_failure_no_aabb_or_guard"
    assert probe_exit_code(status) == 2


def test_state_load_failure_is_machine_detected_after_attach():
    result = _result()
    result["orchestration"]["runtime_load_verified"] = False
    result["orchestration"]["target_live"] = False
    status = classify_probe_result(result)
    assert status.infrastructure == "succeeded"
    assert status.code == "runtime_state_not_verified"


def test_wrong_target_and_stale_object_rejections_are_classified():
    tracker = _live_tracker()
    with pytest.raises(ValueError) as wrong:
        tracker.accept_aabb(0x0203DEBC)
    assert classify_probe_exception(wrong.value).code == "wrong_target_rejected"

    tracker.begin_population(MANAGER, _load())
    with pytest.raises(ValueError) as stale:
        tracker.accept_aabb(0x0203DE7C)
    assert classify_probe_exception(stale.value).code == "stale_object_rejected"


def test_exact_callback_success_and_filtered_paths_are_distinct():
    captured = classify_probe_result(
        _result(complete=True, exact_query={"object": "0x0203DE7C"}, callbacks=[{}])
    )
    assert captured.research == "A"
    assert captured.code == "exact_callback_captured"
    assert probe_exit_code(captured) == 0

    filtered = classify_probe_result(
        _result(exact_query={"object": "0x0203DE7C"})
    )
    assert filtered.research == "B"
    assert filtered.code == "exact_aabb_callback_filtered"
    assert probe_exit_code(filtered) == 0

    rejected = classify_probe_result(_result(rejecting_guard={"rejects": True}))
    assert rejected.research == "C"
    assert rejected.code == "first_entry_guard_identified"
    assert probe_exit_code(rejected) == 0


def test_incomplete_or_self_inconsistent_result_fails_closed():
    result = _result()
    result["orchestration"]["debugger_attached"] = False
    with pytest.raises(ValueError, match="incomplete infrastructure"):
        classify_probe_result(result)
    with pytest.raises(ValueError, match="lacks exact query/callback"):
        classify_probe_result(_result(complete=True, callbacks=[]))
    assert probe_exit_code(classify_probe_exception(RuntimeError("unexpected"))) == 3


def test_lua_ready_marker_is_bounded_and_ignored():
    injector = (PROJECT_ROOT / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8"
    )
    probe = (PROJECT_ROOT / "tools/runtime/rom008_query_probe.py").read_text(
        encoding="utf-8"
    )
    assert "ReadyPath must remain beneath ignored build directory" in injector
    assert "Lua script did not report ready" in injector
    assert "$attempt -lt 100" in injector
    assert 'str(run_root / "lua-ready.txt")' in probe
    assert "ReadyPath already exists" in injector
    invoke_helper = (
        PROJECT_ROOT / "tools/runtime/invoke_mgba_run.ps1"
    ).read_text(encoding="utf-8")
    assert "$run.GetCurrentPattern" not in injector
    assert "InvokePattern]::Pattern" in invoke_helper
    assert "Start-Process" in injector
    assert "-WindowStyle Hidden" in injector
    assert "Stop-Process -Id $invokeProcess.Id" in injector
    assert "$desktop.FindAll($Scope, $condition)" in injector
    assert "if (-not $scripting)" in injector


def test_probe_output_is_atomic_and_limited_to_ignored_build(tmp_path: Path):
    workspace = tmp_path / "workspace"
    output = workspace / "build/rom010/result.json"
    assert write_probe_output(output, {"complete": False}, workspace_root=workspace) == output
    assert output.read_text(encoding="utf-8") == '{\n  "complete": false\n}\n'
    assert not (output.parent / ".result.json.tmp").exists()
    with pytest.raises(FileExistsError, match="already exists"):
        write_probe_output(output, {"complete": False}, workspace_root=workspace)
    with pytest.raises(ValueError, match="direct JSON child"):
        write_probe_output(
            workspace / "docs/result.json",
            {"complete": False},
            workspace_root=workspace,
        )
    with pytest.raises(ValueError, match="direct JSON child"):
        write_probe_output(
            workspace / "build/rom010/private.sav",
            {"complete": False},
            workspace_root=workspace,
        )
    with pytest.raises(ValueError, match="direct JSON child"):
        write_probe_output(
            workspace / "build/rom010/nested/result.json",
            {"complete": False},
            workspace_root=workspace,
        )
