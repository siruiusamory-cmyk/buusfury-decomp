"""Bounded read-only mGBA probe for one exact ROM-008 runtime object.

The probe discovers the object from descriptor ``0x08294948`` and factory raw
target ``0x08007675`` in each run.  It then accepts spatial-query and callback
events only while that dynamically captured object remains live in the same
verified load epoch.  No ROM, register, or memory write packet is sent.
"""

from __future__ import annotations

import argparse
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
    THUMB_STATE_BIT,
    RESOLVER_ENTRY_PC,
    RESOLVER_LOAD_PC,
    _connect,
    _register_dict,
    _registers,
    effective_variation_source,
    rsp_packet,
)
from tools.runtime.rom007_factory_probe import (
    ACTIVE_MAP_POINTER_PACKET,
    ADAPTER_PC,
    Rom007RspClient,
    adapter_entry_is_valid,
    decode_read_u32,
    execution_target,
    map_entry_index_from_address,
    validate_registry_insertion,
)
from tools.runtime.rom008_object_trace import (
    EXPANDED_QUERY_ENTRY_PC,
    FACTORY_RETURN_PC,
    FACTORY_VENEER_PC,
    MANAGER,
    POINT_QUERY_ENTRY_PC,
    POPULATION_PC,
    REMOVAL_PC,
    REMOVAL_COMMIT_PC,
    RESET_PC,
    SECOND_QUERY_ENTRY_PC,
    SUPPORTED_CALLBACK_CALLS,
    ExactObjectTracker,
    LoadIdentity,
    private_working_paths,
    query_caller_from_lr,
    removal_count_commit_is_valid,
    removal_path_reaches_commit,
    reset_count_commit_is_valid,
    signed_halfwords,
    thumb_fetch_is_valid,
    validate_complete_timeline,
)
from tools.webfoot.analysis.variation_arrays import census_variation_array_first_words
from tools.webfoot.profile import RomProfileCatalog


EXPECTED_FACTORY_LR = 0x08012679
EXPECTED_RESOLVER_LR = 0x08008ABF
QUERY_ENTRY_PCS = (
    POINT_QUERY_ENTRY_PC,
    SECOND_QUERY_ENTRY_PC,
    EXPANDED_QUERY_ENTRY_PC,
)
KNOWN_QUERY_CALLERS = {
    POINT_QUERY_ENTRY_PC: {0x08006E4E, 0x08021DFE, 0x08021E06},
    SECOND_QUERY_ENTRY_PC: {0x08012AEC},
    EXPANDED_QUERY_ENTRY_PC: {0x08022142},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Rom008RspClient(Rom007RspClient):
    """Add exact, dynamically allowlisted read-only memory packets."""

    def __init__(self, sock: socket.socket):
        super().__init__(sock)
        self._allowed_reads: set[str] = set()

    def allow_read(self, address: int, length: int) -> str:
        if not 0 <= address <= 0xFFFFFFFF or not 1 <= length <= 0x100:
            raise ValueError("runtime read is outside bounded u32 address/length scope")
        if address + length > 0x1_0000_0000:
            raise ValueError("runtime read overflows address space")
        packet = f"m{address:x},{length:x}"
        self._allowed_reads.add(packet)
        return packet

    def command(self, payload: str, timeout: float = 5.0) -> str:
        if payload in self._allowed_reads:
            self.sock.sendall(rsp_packet(payload))
            return self._read_response(timeout)
        return super().command(payload, timeout)


def _breakpoint(client: Rom008RspClient, address: int) -> None:
    if client.command(f"Z0,{address:x},2") != "OK":
        raise RuntimeError(f"breakpoint rejected at 0x{address:08X}")


def _remove_breakpoint(client: Rom008RspClient, address: int) -> None:
    if client.command(f"z0,{address:x},2") != "OK":
        raise RuntimeError(f"breakpoint removal rejected at 0x{address:08X}")


def _read_bytes(client: Rom008RspClient, address: int, length: int) -> bytes:
    payload = client.command(client.allow_read(address, length))
    if len(payload) != length * 2:
        raise RuntimeError("runtime read returned an unexpected length")
    try:
        return bytes.fromhex(payload)
    except ValueError as exc:
        raise RuntimeError("runtime read returned non-hexadecimal data") from exc


def _read_u32(client: Rom008RspClient, address: int) -> int:
    return int.from_bytes(_read_bytes(client, address, 4), "little")


def _event(registers: Sequence[int]) -> dict[str, object]:
    return {
        "pc": f"0x{registers[15]:08X}",
        "lr": f"0x{registers[14]:08X}",
        "thumb": bool(registers[16] & THUMB_STATE_BIT),
        "registers": _register_dict(registers),
    }


def _step_to_callback(
    client: Rom008RspClient,
    *,
    call_pc: int,
    raw_target: int,
    return_pc: int,
    max_steps: int = 32,
) -> tuple[list[str], Sequence[int]]:
    target = execution_target(raw_target)
    _remove_breakpoint(client, call_pc)
    pcs: list[str] = []
    reached_target = False
    for _ in range(max_steps):
        client.command("s")
        registers = _registers(client)
        pcs.append(f"0x{registers[15]:08X}")
        if registers[15] == target.fetch_address:
            if bool(registers[16] & THUMB_STATE_BIT) != (target.state == "Thumb"):
                raise RuntimeError("callback fetch execution state disagrees with raw target")
            reached_target = True
        if registers[15] == return_pc:
            if not reached_target:
                raise RuntimeError("callback returned without reaching its raw target")
            _breakpoint(client, call_pc)
            return pcs, registers
    raise RuntimeError("callback exceeded bounded single-step budget")


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
    run_root = state_path.parent / f"rom008-{uuid.uuid4().hex}"
    state_copy, save_copy = private_working_paths(
        state_source=state_path,
        save_source=save_path,
        run_root=run_root,
        rom_name=rom_path.name,
    )
    state_copy.parent.mkdir(parents=True)
    save_copy.parent.mkdir(parents=True)
    state_root = run_root / "states"
    screenshot_root = run_root / "screenshots"
    state_root.mkdir()
    screenshot_root.mkdir()
    shutil.copy2(state_path, state_copy)
    shutil.copy2(save_path, save_copy)

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
            f"savegamePath={save_copy.parent}",
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
    tracker = ExactObjectTracker()
    timeline: list[dict[str, object]] = []
    query_entries: list[dict[str, object]] = []
    exact_query: dict[str, object] | None = None
    callbacks: list[dict[str, object]] = []
    accepted_entry: tuple[int, int] | None = None
    verified_load: LoadIdentity | None = None
    verified_adapter = False
    pending_factory = False
    pending_point_action = False
    installed = {
        RESET_PC,
        POPULATION_PC,
        REMOVAL_PC,
        RESOLVER_ENTRY_PC,
        RESOLVER_LOAD_PC,
        ADAPTER_PC,
    }
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
            client = Rom008RspClient(sock)
            client.command("?")
            for address in installed:
                _breakpoint(client, address)
            deadline = time.monotonic() + timeout_seconds
            for _ in range(96):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    client.command("c", timeout=min(5.0, remaining))
                except socket.timeout:
                    continue
                registers = _registers(client)
                pc = registers[15]
                if pc == RESET_PC:
                    if not thumb_fetch_is_valid(pc, registers[16], RESET_PC):
                        raise RuntimeError("registry reset did not execute in Thumb state")
                    _remove_breakpoint(client, RESET_PC)
                    reset_steps = []
                    for _ in range(3):
                        client.command("s")
                        reset_steps.append(_registers(client))
                    _breakpoint(client, RESET_PC)
                    if tuple(item[15] for item in reset_steps) != (
                        0x0804848A,
                        0x0804848C,
                        0x0804848E,
                    ):
                        raise RuntimeError("registry reset left its verified store path")
                    if not reset_count_commit_is_valid(_read_u32(client, MANAGER)):
                        raise RuntimeError("registry reset did not commit zero count")
                    tracker.retire_reset()
                    timeline.append({"event": "reset", **_event(registers)})
                    pending_point_action = False
                    verified_load = None
                    verified_adapter = False
                elif pc == RESOLVER_ENTRY_PC:
                    try:
                        index = map_entry_index_from_address(registers[0])
                    except ValueError:
                        continue
                    if (
                        index == 39
                        and registers[1] == 1
                        and registers[14] == EXPECTED_RESOLVER_LR
                        and bool(registers[16] & THUMB_STATE_BIT)
                    ):
                        accepted_entry = (registers[0], index)
                        verified_adapter = False
                elif pc == RESOLVER_LOAD_PC and accepted_entry is not None:
                    observation = by_index[accepted_entry[1]]
                    source = effective_variation_source(registers[0])
                    if registers[1] != 4 or source != observation.source_pointer_raw:
                        raise RuntimeError("resolver load disagrees with MapEntry 39")
                    client.command("s")
                    after = _registers(client)
                    if (
                        after[15] != RESOLVER_LOAD_PC + 2
                        or after[0] != observation.first_word_raw
                    ):
                        raise RuntimeError("resolver value disagrees with static first word")
                    verified_load = LoadIdentity(
                        map_entry_address=accepted_entry[0],
                        map_entry_index=accepted_entry[1],
                        selector=1,
                        variation_source=source,
                        selected_value=after[0],
                    )
                elif pc == ADAPTER_PC and verified_load is not None:
                    if not adapter_entry_is_valid(registers, verified_load.selected_value):
                        raise RuntimeError("adapter lost verified MapEntry-39 selected value")
                    verified_adapter = True
                elif pc == POPULATION_PC and registers[0] == MANAGER:
                    if verified_load is None or not verified_adapter:
                        raise RuntimeError("population reached without resolver/adapter load identity")
                    load_epoch = tracker.begin_population(registers[0], verified_load)
                    verified_adapter = False
                    address = decode_read_u32(client.command(ACTIVE_MAP_POINTER_PACKET))
                    index = map_entry_index_from_address(address)
                    observation = by_index[index]
                    if (
                        address != verified_load.map_entry_address
                        or index != verified_load.map_entry_index
                        or observation.source_pointer_raw != verified_load.variation_source
                        or observation.first_word_raw != verified_load.selected_value
                    ):
                        raise RuntimeError("active map disagrees with resolver load identity")
                    timeline.append(
                        {
                            "event": "population",
                            "load_epoch": load_epoch,
                            "map_entry": f"0x{address:08X}",
                            "map_index": index,
                            "variation_source": f"0x{observation.source_pointer_raw:08X}",
                            "first_word_raw": f"0x{observation.first_word_raw:08X}",
                            "count": registers[1],
                            "array": f"0x{registers[2]:08X}",
                        }
                    )
                    for address in (FACTORY_VENEER_PC, FACTORY_RETURN_PC):
                        if address not in installed:
                            _breakpoint(client, address)
                            installed.add(address)
                elif pc == FACTORY_VENEER_PC and registers[14] == EXPECTED_FACTORY_LR:
                    if registers[0] != tracker.descriptor or registers[1] != tracker.factory.raw:
                        continue
                    target = tracker.accept_factory(registers[0], registers[1])
                    _remove_breakpoint(client, FACTORY_VENEER_PC)
                    client.command("s")
                    after = _registers(client)
                    _breakpoint(client, FACTORY_VENEER_PC)
                    if after[15] != target.fetch_address or not (after[16] & THUMB_STATE_BIT):
                        raise RuntimeError("target factory fetch/state mismatch")
                    pending_factory = True
                    timeline.append(
                        {
                            "event": "factory",
                            "descriptor": f"0x{registers[0]:08X}",
                            "raw": f"0x{target.raw:08X}",
                            "fetch": f"0x{target.fetch_address:08X}",
                            "state": target.state,
                        }
                    )
                elif pc == FACTORY_RETURN_PC and pending_factory:
                    returned = registers[0]
                    manager = registers[5]
                    insertion_steps = []
                    _remove_breakpoint(client, FACTORY_RETURN_PC)
                    for _ in range(6):
                        client.command("s")
                        insertion_steps.append(_registers(client))
                    _breakpoint(client, FACTORY_RETURN_PC)
                    old_count, new_count, slot = validate_registry_insertion(
                        insertion_steps,
                        manager=manager,
                        returned_object=returned,
                    )
                    identity = tracker.commit_insertion(
                        manager=manager,
                        returned_object=returned,
                        old_count=old_count,
                        new_count=new_count,
                        slot=slot,
                    )
                    bounds = signed_halfwords(_read_bytes(client, returned + 4, 8))
                    timeline.append(
                        {
                            "event": "live",
                            "load_epoch": identity.load_epoch,
                            "object": f"0x{returned:08X}",
                            "slot": f"0x{slot:08X}",
                            "bounds": list(bounds),
                        }
                    )
                    for address in SUPPORTED_CALLBACK_CALLS:
                        if address not in installed:
                            _breakpoint(client, address)
                            installed.add(address)
                    for address in QUERY_ENTRY_PCS:
                        if address not in installed:
                            _breakpoint(client, address)
                            installed.add(address)
                    pending_factory = False
                elif pc == REMOVAL_PC and tracker.current is not None:
                    if registers[0] != MANAGER or registers[1] != tracker.current.object_pointer:
                        continue
                    if not thumb_fetch_is_valid(pc, registers[16], REMOVAL_PC):
                        raise RuntimeError("registry removal did not execute in Thumb state")
                    object_pointer = registers[1]
                    old_count = _read_u32(client, MANAGER)
                    _remove_breakpoint(client, REMOVAL_PC)
                    removal_pcs = []
                    for _ in range(128):
                        client.command("s")
                        stepped = _registers(client)
                        removal_pcs.append(stepped[15])
                        if stepped[15] == REMOVAL_COMMIT_PC:
                            break
                    _breakpoint(client, REMOVAL_PC)
                    if not removal_path_reaches_commit(removal_pcs):
                        raise RuntimeError("target removal did not reach its bounded count commit")
                    if not thumb_fetch_is_valid(
                        removal_pcs[-1], stepped[16], REMOVAL_COMMIT_PC
                    ):
                        raise RuntimeError("removal commit did not execute in Thumb state")
                    client.command("s")
                    after = _registers(client)
                    if after[15] != REMOVAL_COMMIT_PC + 2:
                        raise RuntimeError("registry removal left its verified count commit")
                    if not removal_count_commit_is_valid(
                        old_count, _read_u32(client, MANAGER)
                    ):
                        raise RuntimeError("registry removal count commit mismatch")
                    if not tracker.retire_removal(
                        manager=MANAGER, object_pointer=object_pointer
                    ):
                        raise RuntimeError("committed removal did not match current target")
                    timeline.append(
                        {
                            "event": "removal",
                            "object": f"0x{object_pointer:08X}",
                            "count": [old_count, old_count - 1],
                            **_event(after),
                        }
                    )
                    pending_point_action = False
                elif pc in QUERY_ENTRY_PCS:
                    if not thumb_fetch_is_valid(pc, registers[16], pc):
                        raise RuntimeError("query entry did not execute in Thumb state")
                    pending_point_action = False
                    caller = query_caller_from_lr(registers[14])
                    if caller not in KNOWN_QUERY_CALLERS[pc]:
                        raise RuntimeError(
                            f"query caller 0x{caller:08X} is not statically verified"
                        )
                    query_entries.append(
                        {
                            **_event(registers),
                            "caller": f"0x{caller:08X}",
                            "load_epoch": tracker.load_epoch,
                            "target_live": tracker.current is not None,
                        }
                    )
                elif pc in SUPPORTED_CALLBACK_CALLS and tracker.current is not None:
                    if not thumb_fetch_is_valid(pc, registers[16], pc):
                        raise RuntimeError("callback callsite did not execute in Thumb state")
                    raw_register, return_pc, label = SUPPORTED_CALLBACK_CALLS[pc]
                    if registers[1] != tracker.current.object_pointer:
                        continue
                    if pc == 0x08012784:
                        tracker.accept_aabb(registers[1])
                        query = signed_halfwords(_read_bytes(client, registers[13] + 4, 4))
                        exact_query = {
                            "path": "point",
                            "object": f"0x{registers[1]:08X}",
                            "query": list(query),
                            **_event(registers),
                        }
                    elif not pending_point_action:
                        raise RuntimeError("point action has no exact predicate invocation")
                    tracker.accept_callback(
                        tracker.current.object_pointer,
                        followup=(pc == 0x0801279C),
                    )
                    raw = registers[raw_register]
                    target = execution_target(raw)
                    step_pcs, returned = _step_to_callback(
                        client,
                        call_pc=pc,
                        raw_target=raw,
                        return_pc=return_pc,
                    )
                    captured_callback = {
                        "label": label,
                        "object": f"0x{tracker.current.object_pointer:08X}",
                        "raw": f"0x{target.raw:08X}",
                        "fetch": f"0x{target.fetch_address:08X}",
                        "state": target.state,
                        "arguments": _register_dict(registers),
                        "return": f"0x{returned[0]:08X}",
                        "step_pcs": step_pcs,
                    }
                    callbacks.append(captured_callback)
                    if label == "point_predicate" and returned[0] != 0:
                        pending_point_action = True
                    else:
                        pending_point_action = False
                        break
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

    source_artifacts: dict[str, object] = {}
    for path, (old_stat, old_hash) in before.items():
        current = path.stat()
        current_hash = sha256(path)
        source_artifacts[str(path)] = {
            "sha256": current_hash,
            "size": current.st_size,
            "mtime_ns": current.st_mtime_ns,
            "unchanged": (
                current_hash == old_hash
                and current.st_size == old_stat.st_size
                and current.st_mtime_ns == old_stat.st_mtime_ns
            ),
        }
    if not all(item["unchanged"] for item in source_artifacts.values()):
        raise RuntimeError("ROM or source save artifact changed during runtime probe") from probe_error
    if probe_error is not None:
        raise probe_error
    return {
        "timeline": timeline,
        "query_entries": query_entries,
        "exact_query": exact_query,
        "callbacks": callbacks,
        "complete": validate_complete_timeline(tracker.events),
        "source_artifacts": source_artifacts,
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
    parser.add_argument("--timeout", type=float, default=25.0)
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
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
