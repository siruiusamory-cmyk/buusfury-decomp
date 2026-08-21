"""Stable fail-closed outcome taxonomy for ROM-010 runtime orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import socket
import subprocess
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ProbeStatus:
    code: str
    phase: str
    infrastructure: str
    research: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _status(
    code: str,
    phase: str,
    infrastructure: str,
    research: str,
    detail: str,
) -> ProbeStatus:
    return ProbeStatus(code, phase, infrastructure, research, detail)


def classify_probe_exception(
    error: BaseException, *, mgba_path: Path | None = None
) -> ProbeStatus:
    """Classify only demonstrated exception paths; unknown errors stay unknown."""

    message = str(error)
    if isinstance(error, FileNotFoundError):
        missing = Path(error.filename).resolve() if error.filename else None
        expected = mgba_path.resolve() if mgba_path is not None else None
        if missing is not None and expected is not None and missing == expected:
            return _status(
                "mgba_absent",
                "emulator_launch",
                "failed",
                "not_started",
                message,
            )
        return _status(
            "runtime_input_absent",
            "input_verification",
            "failed",
            "not_started",
            message,
        )
    if isinstance(error, subprocess.TimeoutExpired):
        return _status(
            "lua_injection_timeout",
            "lua_initialization",
            "failed",
            "not_started",
            message,
        )
    if isinstance(error, subprocess.CalledProcessError):
        output = "\n".join(part for part in (error.stdout, error.stderr) if part)
        if "mGBA window did not appear" in output or "loaded Buu's Fury ROM" in output:
            code = "wrong_mgba_process"
        elif "Lua script did not report ready" in output:
            code = "lua_loading_failed"
        else:
            code = "lua_injection_failed"
        return _status(code, "lua_initialization", "failed", "not_started", output)
    if isinstance(error, TimeoutError) and "mGBA GDB port did not open" in message:
        return _status(
            "debugger_connection_timeout",
            "debugger_attach",
            "failed",
            "not_started",
            message,
        )
    if isinstance(error, socket.timeout):
        return _status(
            "debugger_response_timeout",
            "debugger_operation",
            "failed",
            "not_started",
            message,
        )
    exact_runtime_errors = {
        "TCP port 2345 already in use": (
            "debugger_port_occupied",
            "debugger_preflight",
        ),
        "verified ROM identity mismatch": ("wrong_rom", "input_verification"),
        "save-state identity mismatch": (
            "wrong_runtime_state",
            "input_verification",
        ),
        "save identity mismatch": ("wrong_runtime_save", "input_verification"),
    }
    if message in exact_runtime_errors:
        code, phase = exact_runtime_errors[message]
        return _status(code, phase, "failed", "not_started", message)
    if message.startswith("breakpoint rejected at "):
        return _status(
            "breakpoint_installation_failed",
            "breakpoint_installation",
            "failed",
            "not_started",
            message,
        )
    if "does not match current target identity" in message:
        return _status(
            "wrong_target_rejected",
            "target_attribution",
            "succeeded",
            "rejected",
            message,
        )
    if "no live target object exists in this load epoch" in message:
        return _status(
            "stale_object_rejected",
            "target_attribution",
            "succeeded",
            "rejected",
            message,
        )
    return _status(
        "unknown_probe_failure",
        "unknown",
        "failed",
        "unknown",
        message,
    )


def classify_probe_result(result: Mapping[str, object]) -> ProbeStatus:
    """Separate successful infrastructure from the bounded research result."""

    orchestration = result.get("orchestration")
    if not isinstance(orchestration, Mapping):
        raise ValueError("probe result lacks orchestration stages")
    required = (
        "inputs_verified",
        "emulator_launched",
        "lua_ready",
        "debugger_attached",
        "breakpoints_installed",
    )
    missing = [name for name in required if orchestration.get(name) is not True]
    if missing:
        raise ValueError(f"probe result has incomplete infrastructure stages: {missing}")

    complete = result.get("complete")
    callbacks = result.get("callbacks")
    exact_query = result.get("exact_query")
    rejecting_guard = result.get("rejecting_guard")
    if complete is True:
        if not isinstance(callbacks, list) or not callbacks or not exact_query:
            raise ValueError("complete probe lacks exact query/callback evidence")
        return _status(
            "exact_callback_captured",
            "research",
            "succeeded",
            "A",
            "Exact same-epoch target callback captured.",
        )
    if complete is not False:
        raise ValueError("probe completion flag is not boolean")
    if isinstance(rejecting_guard, Mapping) and rejecting_guard.get("rejects") is True:
        return _status(
            "first_entry_guard_identified",
            "research",
            "succeeded",
            "C",
            "First rejecting guard captured for current target.",
        )
    if exact_query:
        return _status(
            "exact_aabb_callback_filtered",
            "research",
            "succeeded",
            "B",
            "Exact target reached AABB processing without callback completion.",
        )
    if orchestration.get("runtime_load_verified") is not True:
        return _status(
            "runtime_state_not_verified",
            "state_load",
            "succeeded",
            "inconclusive",
            "Debugger path worked, but no trusted runtime load was verified.",
        )
    if orchestration.get("target_live") is not True:
        return _status(
            "target_not_observed",
            "target_attribution",
            "succeeded",
            "inconclusive",
            "Runtime load verified, but target factory/object was not observed.",
        )
    return _status(
        "research_failure_no_aabb_or_guard",
        "research",
        "succeeded",
        "inconclusive",
        "Exact target became live; no AABB, callback, or rejecting guard executed.",
    )


def probe_exit_code(status: ProbeStatus) -> int:
    if status.infrastructure != "succeeded":
        return 3
    if status.research in {"A", "B", "C"}:
        return 0
    return 2


def write_probe_output(
    path: Path, payload: Mapping[str, object], *, workspace_root: Path
) -> Path:
    output_root = (workspace_root.resolve() / "build" / "rom010").resolve()
    target = path.resolve()
    if target.parent != output_root or target.suffix.lower() != ".json":
        raise ValueError("probe output must be a direct JSON child of build/rom010")
    if target.exists():
        raise FileExistsError(f"probe output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    if temporary.exists():
        raise FileExistsError(f"temporary probe output already exists: {temporary}")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    return target
