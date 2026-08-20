"""Bounded read-only mGBA probe for one ROM-007 map-object factory.

The probe accepts private save artifacts at runtime but never copies them into
tracked paths. Its GDB client allowlists register reads, one exact active-map
pointer read, hardware breakpoints, continue, and single-step packets. It never
sends a memory or register write packet.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import time
from typing import Sequence
import uuid

from tools.runtime.rom006_gdb_probe import (
    EXPECTED_SHA256,
    EXPECTED_SIZE,
    MAP_ENTRY_BASE,
    MAP_ENTRY_COUNT,
    MAP_ENTRY_SIZE,
    RESOLVER_ENTRY_PC,
    RESOLVER_LOAD_PC,
    RspClient,
    THUMB_STATE_BIT,
    _connect,
    _register_dict,
    _registers,
    effective_variation_source,
)
from tools.webfoot.analysis.variation_arrays import census_variation_array_first_words
from tools.webfoot.profile import RomProfileCatalog


ACTIVE_MAP_POINTER_PACKET = "m3001980,4"
CALLSITE_PC = 0x08008AC2
ADAPTER_PC = 0x08009670
MANAGER_PC = 0x08012664
DESCRIPTOR_PC = 0x08012672
FACTORY_CALL_PC = 0x08012674
FACTORY_VENEER_PC = 0x08046AA2
FACTORY_RETURN_PC = 0x08012678
SPATIAL_CALLBACK_PC = 0x08012784
EXPECTED_RESOLVER_LR = 0x08008ABF
EXPECTED_ADAPTER_LR = 0x08008AC7
EXPECTED_FACTORY_LR = 0x08012679


@dataclass(frozen=True, slots=True)
class ExecutionTarget:
    raw: int
    state: str
    fetch_address: int


@dataclass(frozen=True, slots=True)
class FactoryCapture:
    descriptor: int
    target: ExecutionTarget
    returned_object: int
    registry_slot: int
    old_count: int
    new_count: int


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def map_entry_index_from_address(address: int) -> int:
    if isinstance(address, bool) or not isinstance(address, int):
        raise ValueError("MapEntry address must be an integer")
    offset = address - MAP_ENTRY_BASE
    if offset < 0 or offset >= MAP_ENTRY_COUNT * MAP_ENTRY_SIZE:
        raise ValueError("MapEntry address is outside the canonical table")
    if offset % MAP_ENTRY_SIZE:
        raise ValueError("MapEntry address is not record-aligned")
    return offset // MAP_ENTRY_SIZE


def execution_target(raw: int) -> ExecutionTarget:
    if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= 0xFFFFFFFF:
        raise ValueError("execution target must be a raw 32-bit value")
    return ExecutionTarget(
        raw=raw,
        state="Thumb" if raw & 1 else "ARM",
        fetch_address=raw & ~1 if raw & 1 else raw,
    )


def decode_read_u32(payload: str) -> int:
    if len(payload) != 8:
        raise ValueError("u32 memory response must contain eight hex characters")
    try:
        raw = bytes.fromhex(payload)
    except ValueError as exc:
        raise ValueError("u32 memory response is not hexadecimal") from exc
    return int.from_bytes(raw, "little")


def registry_slot(manager: int, old_count: int) -> int:
    if not 0 <= manager <= 0xFFFFFFFF or not 0 <= old_count <= 0xFFFFFFFF:
        raise ValueError("registry inputs must be unsigned 32-bit values")
    result = manager + 4 + old_count * 4
    if result > 0xFFFFFFFF:
        raise ValueError("registry slot calculation overflowed")
    return result


def factory_capture_is_valid(
    capture: FactoryCapture,
    *,
    expected_descriptor: int,
    expected_raw_target: int,
    expected_object: int,
    manager: int,
    old_count: int,
) -> bool:
    return (
        capture.descriptor == expected_descriptor
        and capture.target == execution_target(expected_raw_target)
        and capture.returned_object == expected_object
        and 0x02000000 <= capture.returned_object < 0x02040000
        and capture.registry_slot == registry_slot(manager, old_count)
        and capture.old_count == old_count
        and capture.new_count == old_count + 1
    )


def validate_registry_insertion(
    steps: Sequence[Sequence[int]], *, manager: int, returned_object: int
) -> tuple[int, int, int]:
    expected_pcs = (0x0801267A, 0x0801267C, 0x0801267E, 0x08012680, 0x08012682, 0x08012684)
    if any(len(item) < 17 for item in steps):
        raise ValueError("registry insertion register capture is incomplete")
    if len(steps) != len(expected_pcs) or tuple(item[15] for item in steps) != expected_pcs:
        raise ValueError("registry insertion did not follow the expected instruction sequence")
    old_count = steps[0][1]
    new_count = steps[1][2]
    slot = steps[3][1] + 4
    if new_count != old_count + 1:
        raise ValueError("registry count did not increment by one")
    if slot != registry_slot(manager, old_count):
        raise ValueError("registry slot disagrees with manager and old count")
    if any(item[0] != returned_object or item[5] != manager for item in steps):
        raise ValueError("registry insertion lost returned object or manager provenance")
    return old_count, new_count, slot


def adapter_entry_is_valid(registers: Sequence[int], expected_selected: int) -> bool:
    return (
        len(registers) >= 17
        and registers[15] == ADAPTER_PC
        and registers[14] == EXPECTED_ADAPTER_LR
        and registers[1] == expected_selected
        and bool(registers[16] & THUMB_STATE_BIT)
    )


def adapter_steps_are_valid(steps: Sequence[Sequence[int]]) -> bool:
    expected_pcs = (0x08009672, 0x08009674, 0x08009676, 0x08009678, 0x0800967A)
    return (
        len(steps) == len(expected_pcs)
        and all(len(item) >= 17 for item in steps)
        and tuple(item[15] for item in steps) == expected_pcs
        and all(bool(item[16] & THUMB_STATE_BIT) for item in steps)
    )


def manager_entry_is_valid(
    registers: Sequence[int], *, manager: int, count: int, array_base: int
) -> bool:
    return (
        len(registers) >= 17
        and registers[15] == MANAGER_PC
        and registers[0] == manager
        and registers[1] == count
        and registers[2] == array_base
        and bool(registers[16] & THUMB_STATE_BIT)
    )


def population_is_complete(expected_count: int | None, captures: Sequence[FactoryCapture]) -> bool:
    return expected_count is not None and expected_count > 0 and len(captures) == expected_count


class Rom007RspClient(RspClient):
    @classmethod
    def command_is_allowed(cls, payload: str) -> bool:
        return payload == ACTIVE_MAP_POINTER_PACKET or super().command_is_allowed(payload)


def _thumb(registers: Sequence[int]) -> bool:
    return bool(registers[16] & THUMB_STATE_BIT)


def _event(registers: Sequence[int]) -> dict[str, object]:
    return {
        "pc": f"0x{registers[15]:08X}",
        "thumb": _thumb(registers),
        "registers": _register_dict(registers),
    }


def _format_target(target: ExecutionTarget) -> dict[str, object]:
    return {
        "raw": f"0x{target.raw:08X}",
        "state": target.state,
        "fetch_address": f"0x{target.fetch_address:08X}",
    }


def run_probe(
    *,
    rom_path: Path,
    state_path: Path,
    save_path: Path,
    state_sha256: str,
    save_sha256: str,
    lua_path: Path,
    injector_path: Path,
    mgba_path: Path,
    profile_path: Path,
    timeout_seconds: float,
) -> dict[str, object]:
    sources = (rom_path, state_path, save_path)
    before = {path: (path.stat(), sha256(path)) for path in sources}
    if before[rom_path][0].st_size != EXPECTED_SIZE or before[rom_path][1] != EXPECTED_SHA256:
        raise RuntimeError("verified ROM identity mismatch")
    if before[state_path][1].lower() != state_sha256.lower():
        raise RuntimeError("save-state identity mismatch")
    if before[save_path][1].lower() != save_sha256.lower():
        raise RuntimeError("save identity mismatch")

    census = census_variation_array_first_words(
        rom_path, RomProfileCatalog.load(profile_path)
    )
    by_index = {item.map_entry_index: item for item in census.observations}
    run_root = state_path.parent / f"probe-{uuid.uuid4().hex}"
    save_root = run_root / "save"
    state_root = run_root / "states"
    screenshot_root = run_root / "screenshots"
    for path in (save_root, state_root, screenshot_root):
        path.mkdir(parents=True)
    state_copy = run_root / "input.ss1"
    shutil.copy2(state_path, state_copy)
    shutil.copy2(save_path, save_root / rom_path.with_suffix(".sav").name)

    port_probe = socket.socket()
    try:
        if port_probe.connect_ex(("127.0.0.1", 2345)) == 0:
            raise RuntimeError("TCP port 2345 already in use")
    finally:
        port_probe.close()

    process = subprocess.Popen(
        [
            str(mgba_path),
            "--gdb",
            "--savestate",
            str(state_copy),
            "-C",
            f"savegamePath={save_root}",
            "-C",
            f"savestatePath={state_root}",
            "-C",
            f"screenshotPath={screenshot_root}",
            "-C",
            "mute=1",
            "-C",
            "audioSync=0",
            "-C",
            "videoSync=0",
            str(rom_path),
        ]
    )
    started = time.monotonic()
    starting_map: dict[str, object] | None = None
    active_map: dict[str, object] | None = None
    adapter: dict[str, object] | None = None
    manager: dict[str, object] | None = None
    pending_target: tuple[int, ExecutionTarget] | None = None
    factories: list[FactoryCapture] = []
    spatial_calls: list[dict[str, object]] = []
    stop_trace: list[str] = []
    initial_breakpoints = (
        RESOLVER_ENTRY_PC,
        RESOLVER_LOAD_PC,
        CALLSITE_PC,
        ADAPTER_PC,
    )
    factory_breakpoints = (
        MANAGER_PC,
        DESCRIPTOR_PC,
        FACTORY_CALL_PC,
        FACTORY_VENEER_PC,
        FACTORY_RETURN_PC,
    )
    installed_breakpoints = set(initial_breakpoints)
    probe_error: Exception | None = None
    try:
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(injector_path),
                "-TargetProcessId",
                str(process.pid),
                "-LuaPath",
                str(lua_path),
            ],
            check=True,
            timeout=30,
        )
        with _connect(started + 15) as sock:
            client = Rom007RspClient(sock)
            client.command("?")
            starting_address = decode_read_u32(client.command(ACTIVE_MAP_POINTER_PACKET))
            starting_index = map_entry_index_from_address(starting_address)
            starting_observation = by_index[starting_index]
            starting_map = {
                "address": f"0x{starting_address:08X}",
                "index": starting_index,
                "variation_source": f"0x{starting_observation.source_pointer_raw:08X}",
                "first_word_raw": f"0x{starting_observation.first_word_raw:08X}",
            }
            for address in initial_breakpoints:
                if client.command(f"Z0,{address:x},2") != "OK":
                    raise RuntimeError(f"breakpoint rejected at 0x{address:08X}")

            accepted_entry: tuple[int, int] | None = None
            expected_factory_count: int | None = None
            for _ in range(64):
                remaining = timeout_seconds - (time.monotonic() - started)
                if remaining <= 0:
                    break
                try:
                    client.command("c", timeout=min(10.0, remaining))
                except socket.timeout:
                    continue
                registers = _registers(client)
                pc = registers[15]
                stop_trace.append(f"0x{pc:08X}/lr=0x{registers[14]:08X}")
                if pc == RESOLVER_ENTRY_PC:
                    try:
                        index = map_entry_index_from_address(registers[0])
                    except ValueError:
                        continue
                    if (
                        registers[14] == EXPECTED_RESOLVER_LR
                        and registers[1] == 1
                        and _thumb(registers)
                    ):
                        accepted_entry = (registers[0], index)
                elif pc == RESOLVER_LOAD_PC and accepted_entry is not None:
                    observation = by_index[accepted_entry[1]]
                    source = effective_variation_source(registers[0])
                    if registers[1] != 4 or source != observation.source_pointer_raw:
                        raise RuntimeError("resolver load disagrees with accepted MapEntry")
                    client.command("s")
                    after = _registers(client)
                    if after[15] != RESOLVER_LOAD_PC + 2 or after[0] != observation.first_word_raw:
                        raise RuntimeError("runtime-selected value disagrees with static census")
                    active_map = {
                        "entry": f"0x{accepted_entry[0]:08X}",
                        "index": accepted_entry[1],
                        "selector": 1,
                        "variation_source": f"0x{source:08X}",
                        "first_word_raw": f"0x{after[0]:08X}",
                        "registers_at_load": _register_dict(registers),
                    }
                elif pc == ADAPTER_PC and active_map is not None:
                    incoming = registers[1]
                    if not adapter_entry_is_valid(
                        registers, int(active_map["first_word_raw"], 16)
                    ):
                        raise RuntimeError(
                            "adapter PC/LR/state/input disagrees with selected first_word_raw"
                        )
                    steps = []
                    for _ in range(5):
                        client.command("s")
                        steps.append(_registers(client))
                    if not adapter_steps_are_valid(steps):
                        raise RuntimeError("adapter stepping left expected Thumb instruction path")
                    expected_factory_count = steps[3][1]
                    if not 1 <= expected_factory_count <= 8:
                        raise RuntimeError("factory count exceeds bounded ROM-007 probe scope")
                    adapter = {
                        "entry": _event(registers),
                        "selected_value": f"0x{incoming:08X}",
                        "field_40_raw": f"0x{steps[3][1]:08X}",
                        "field_44_raw": f"0x{steps[3][2]:08X}",
                        "manager": f"0x{steps[4][0]:08X}",
                    }
                    for address in factory_breakpoints:
                        if client.command(f"Z0,{address:x},2") != "OK":
                            raise RuntimeError(
                                f"factory breakpoint rejected at 0x{address:08X}"
                            )
                        installed_breakpoints.add(address)
                elif pc == MANAGER_PC:
                    if adapter is None:
                        raise RuntimeError("manager reached without adapter provenance")
                    if not manager_entry_is_valid(
                        registers,
                        manager=int(adapter["manager"], 16),
                        count=int(adapter["field_40_raw"], 16),
                        array_base=int(adapter["field_44_raw"], 16),
                    ):
                        raise RuntimeError("manager arguments disagree with adapter capture")
                    manager = _event(registers)
                elif pc == FACTORY_VENEER_PC and registers[14] == EXPECTED_FACTORY_LR:
                    target = execution_target(registers[1])
                    descriptor = registers[0]
                    client.command("s")
                    after = _registers(client)
                    if after[15] != target.fetch_address or _thumb(after) != (target.state == "Thumb"):
                        raise RuntimeError("indirect branch target/state mismatch")
                    pending_target = (descriptor, target)
                elif pc == FACTORY_RETURN_PC and pending_target is not None:
                    returned = registers[0]
                    captured_manager = registers[5]
                    if adapter is None or captured_manager != int(adapter["manager"], 16):
                        raise RuntimeError("factory return lost adapter manager provenance")
                    insertion_steps = []
                    for _ in range(6):
                        client.command("s")
                        insertion_steps.append(_registers(client))
                    try:
                        old_count, new_count, slot = validate_registry_insertion(
                            insertion_steps,
                            manager=captured_manager,
                            returned_object=returned,
                        )
                    except ValueError as exc:
                        raise RuntimeError(str(exc)) from exc
                    if old_count != len(factories):
                        raise RuntimeError("registry old count disagrees with captured iteration count")
                    capture = FactoryCapture(
                        descriptor=pending_target[0],
                        target=pending_target[1],
                        returned_object=returned,
                        registry_slot=slot,
                        old_count=old_count,
                        new_count=new_count,
                    )
                    if not factory_capture_is_valid(
                        capture,
                        expected_descriptor=pending_target[0],
                        expected_raw_target=pending_target[1].raw,
                        expected_object=returned,
                        manager=captured_manager,
                        old_count=old_count,
                    ):
                        raise RuntimeError("factory capture failed provenance validation")
                    factories.append(capture)
                    pending_target = None
                    if expected_factory_count is not None and len(factories) == expected_factory_count:
                        for address in installed_breakpoints:
                            client.command(f"z0,{address:x},2")
                        client.command(f"Z0,{SPATIAL_CALLBACK_PC:x},2")
                elif pc == SPATIAL_CALLBACK_PC and factories:
                    target = execution_target(registers[3])
                    candidate = {
                        "entry": _event(registers),
                        "object": f"0x{registers[1]:08X}",
                        "callback": _format_target(target),
                        "matches_captured_factory_object": registers[1]
                        in {item.returned_object for item in factories},
                    }
                    client.command(f"z0,{SPATIAL_CALLBACK_PC:x},2")
                    step_states = []
                    at_target = None
                    for _ in range(4):
                        client.command("s")
                        stepped = _registers(client)
                        step_states.append(f"0x{stepped[15]:08X}")
                        if stepped[15] == target.fetch_address:
                            at_target = stepped
                            break
                    candidate["step_pcs_to_callback"] = step_states
                    if at_target is None:
                        observed = step_states[-1] if step_states else "<none>"
                        raise RuntimeError(
                            "spatial callback branch target mismatch: "
                            f"raw=0x{target.raw:08X}, expected=0x{target.fetch_address:08X}, "
                            f"observed={observed}"
                        )
                    client.command("s")
                    after_first = _registers(client)
                    candidate["r0_after_first_callback_instruction"] = f"0x{after_first[0]:08X}"
                    spatial_calls.append(candidate)
                    if candidate["matches_captured_factory_object"] or len(spatial_calls) >= 8:
                        break
            if not population_is_complete(expected_factory_count, factories):
                raise RuntimeError(
                    "factory population was incomplete within bounded probe; stops="
                    + ",".join(stop_trace)
                )
    except Exception as exc:
        probe_error = exc
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    unchanged: dict[str, object] = {}
    for path, (old_stat, old_hash) in before.items():
        current = path.stat()
        current_hash = sha256(path)
        unchanged[str(path)] = {
            "sha256": current_hash,
            "size": current.st_size,
            "mtime_ns": current.st_mtime_ns,
            "unchanged": (
                current_hash == old_hash
                and current.st_size == old_stat.st_size
                and current.st_mtime_ns == old_stat.st_mtime_ns
            ),
        }
    if not all(item["unchanged"] for item in unchanged.values()):
        raise RuntimeError("ROM or source save artifact changed during runtime probe") from probe_error
    if probe_error is not None:
        raise probe_error
    return {
        "starting_map": starting_map,
        "active_map": active_map,
        "adapter": adapter,
        "manager": manager,
        "factories": [
            {
                "descriptor": f"0x{item.descriptor:08X}",
                "target": _format_target(item.target),
                "returned_object": f"0x{item.returned_object:08X}",
                "registry_slot": f"0x{item.registry_slot:08X}",
                "old_count": item.old_count,
                "new_count": item.new_count,
            }
            for item in factories
        ],
        "distinct_factory_targets": len({item.target.raw for item in factories}),
        "expected_factory_count": expected_factory_count,
        "spatial_calls": spatial_calls,
        "source_artifacts": unchanged,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("state", type=Path)
    parser.add_argument("save", type=Path)
    parser.add_argument("--state-sha256", required=True)
    parser.add_argument("--save-sha256", required=True)
    parser.add_argument("--lua", type=Path, required=True)
    parser.add_argument("--injector", type=Path, required=True)
    parser.add_argument("--mgba", type=Path, default=Path(r"C:\Program Files\mGBA\mGBA.exe"))
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "config" / "roms.yaml",
    )
    parser.add_argument("--timeout", type=float, default=45.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    result = run_probe(
        rom_path=args.rom.resolve(),
        state_path=args.state.resolve(),
        save_path=args.save.resolve(),
        state_sha256=args.state_sha256,
        save_sha256=args.save_sha256,
        lua_path=args.lua.resolve(),
        injector_path=args.injector.resolve(),
        mgba_path=args.mgba.resolve(),
        profile_path=args.profiles.resolve(),
        timeout_seconds=args.timeout,
    )
    print(json.dumps(result, indent=2))
    valid = (
        result["active_map"] is not None
        and result["adapter"] is not None
        and len(result["factories"]) == result["expected_factory_count"]
        and all(item["unchanged"] for item in result["source_artifacts"].values())
    )
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
