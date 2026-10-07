"""Human-assisted exact-family containment and callback capture for ROM-012."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import socket
import subprocess
import time
from typing import Sequence

from tools.mgba_probe.runtime import (
    ArmRequest,
    EWRAM_END,
    EWRAM_START,
    MATCH_ACCEPTED_X0C,
    ReadEvent,
    instrumented_environment,
    verify_instrumented_mgba,
)
from tools.runtime.evidence_bundle import write_run_bundle
from tools.runtime.rom006_gdb_probe import (
    EXPECTED_SHA256,
    EXPECTED_SIZE,
    THUMB_STATE_BIT,
    _connect,
    _register_dict,
    _registers,
)
from tools.runtime.rom007_factory_probe import (
    execution_target,
    map_entry_index_from_address,
)
from tools.runtime.rom008_object_trace import (
    MANAGER,
    TARGET_FACTORY_RAW,
    private_working_paths,
    signed_halfwords,
)
from tools.runtime.rom008_query_probe import (
    Rom008RspClient,
    _read_bytes,
    _read_u32,
    sha256,
)
from tools.runtime.rom011_live_watch import (
    WATCH_STOP_RE,
    Rom011RspClient,
    _await_stop,
    _write_new_json,
)


QUERY_MIN_X_PC = 0x08012748
ACCEPTED_PC = 0x08012778
FILTER_CALL_PC = 0x08012784
FILTER_RETURN_PC = 0x08012788
ACTION_CALL_PC = 0x0801279C
ACTION_RETURN_PC = 0x080127A0
OBJECT_SIZE = 0x18
ROM_START = 0x08000000
ROM_END = ROM_START + EXPECTED_SIZE
ACTIVE_MAP_POINTER = 0x03001980
EXPECTED_OBJECT_DISPATCH_BASE = 0x0804A09C


@dataclass(frozen=True, slots=True)
class FamilyObject:
    load_epoch: int
    map_entry_address: int
    map_entry_index: int
    descriptor: int
    object_pointer: int
    registry_slot: int
    bounds: tuple[int, int, int, int]
    callback_reference_raw: int = 0
    object_dispatch_base_raw: int = 0
    factory_raw: int = TARGET_FACTORY_RAW

    @property
    def object_index(self) -> int:
        return (self.registry_slot - MANAGER - 4) // 4

    def to_dict(self) -> dict[str, object]:
        return {
            "load_epoch": self.load_epoch,
            "map_entry_address": f"0x{self.map_entry_address:08X}",
            "map_entry_index": self.map_entry_index,
            "descriptor": f"0x{self.descriptor:08X}",
            "factory_raw": f"0x{self.factory_raw:08X}",
            "factory_fetch": f"0x{execution_target(self.factory_raw).fetch_address:08X}",
            "object": f"0x{self.object_pointer:08X}",
            "object_index": self.object_index,
            "registry_slot": f"0x{self.registry_slot:08X}",
            "bounds": list(self.bounds),
            "callback_reference_raw": f"0x{self.callback_reference_raw:08X}",
            "object_dispatch_base_raw": f"0x{self.object_dispatch_base_raw:08X}",
            "expected_object_dispatch_base": f"0x{EXPECTED_OBJECT_DISPATCH_BASE:08X}",
            "object_dispatch_matches_expected": (
                self.object_dispatch_base_raw == EXPECTED_OBJECT_DISPATCH_BASE
            ),
        }


@dataclass(frozen=True, slots=True)
class QuerySample:
    entity: int
    x: int
    y: int
    load_epoch: int
    object_pointer: int

    def to_dict(self) -> dict[str, object]:
        return {
            "entity": f"0x{self.entity:08X}",
            "x": self.x,
            "y": self.y,
            "load_epoch": self.load_epoch,
            "family_object": f"0x{self.object_pointer:08X}",
        }


@dataclass(frozen=True, slots=True)
class CallbackTrace:
    instruction_trace: tuple[str, ...]
    registers: tuple[int, ...]
    reached_target: bool
    returned_to_query: bool


def rectangle_delta(
    point: tuple[int, int], bounds: tuple[int, int, int, int]
) -> tuple[int, int]:
    """Return the shortest signed delta from a point into half-open bounds."""

    x, y = point
    x_min, y_min, x_max, y_max = bounds
    if x_min >= x_max or y_min >= y_max:
        raise ValueError("rectangle bounds must be non-empty and half-open")
    dx = x_min - x if x < x_min else (x_max - 1 - x if x >= x_max else 0)
    dy = y_min - y if y < y_min else (y_max - 1 - y if y >= y_max else 0)
    return dx, dy


def direction_for_delta(dx: int, dy: int) -> str:
    parts: list[str] = []
    if dy < 0:
        parts.append("north")
    elif dy > 0:
        parts.append("south")
    if dx < 0:
        parts.append("west")
    elif dx > 0:
        parts.append("east")
    return "-".join(parts) if parts else "already inside"


def choose_nearest_target(
    point: tuple[int, int], objects: Sequence[FamilyObject]
) -> tuple[FamilyObject, tuple[int, int]]:
    if not objects:
        raise ValueError("no live target-family objects were registered")
    ranked = [
        (abs(dx) + abs(dy), max(abs(dx), abs(dy)), item.object_index, item, (dx, dy))
        for item in objects
        for dx, dy in (rectangle_delta(point, item.bounds),)
    ]
    _, _, _, target, delta = min(ranked, key=lambda row: row[:3])
    return target, delta


def movement_is_consistent(direction: str, dx: int, dy: int) -> bool:
    direction = direction.lower()
    if direction == "east":
        return dx > 0 and abs(dx) >= abs(dy)
    if direction == "west":
        return dx < 0 and abs(dx) >= abs(dy)
    if direction == "north":
        return dy < 0 and abs(dy) >= abs(dx)
    if direction == "south":
        return dy > 0 and abs(dy) >= abs(dx)
    raise ValueError("direction must be north, south, east, or west")


def _read_s32(client: Rom008RspClient, address: int) -> int:
    return int.from_bytes(_read_bytes(client, address, 4), "little", signed=True)


def _query_sample(
    client: Rom008RspClient,
    registers: Sequence[int],
    *,
    load_epoch: int,
    object_pointer: int,
) -> QuerySample:
    # Verified Thumb flow: entry r1 is copied to callee-saved r5 at 0x080126DE,
    # then r5 supplies entity+0x1A0/+0x1A4 at 0x08012702..0x0801270A.
    entity = registers[5]
    return QuerySample(
        entity=entity,
        x=_read_s32(client, entity + 0x1A0) >> 8,
        y=_read_s32(client, entity + 0x1A4) >> 8,
        load_epoch=load_epoch,
        object_pointer=object_pointer,
    )


def _native_event_dict(event: ReadEvent) -> dict[str, object]:
    return {
        "event_id": event.event_id,
        "control_sequence": event.control_sequence,
        "target": f"0x{event.target:08X}",
        "load_epoch": event.load_epoch,
        "descriptor": f"0x{event.descriptor:08X}",
        "factory_raw": f"0x{event.factory_raw:08X}",
        "factory_fetch": f"0x{event.factory_fetch:08X}",
        "read_address": f"0x{event.address:08X}",
        "relative_offset": event.relative_offset,
        "access_width": event.access_width,
        "pc": f"0x{event.instruction_pc:08X}",
        "lr": f"0x{event.lr:08X}",
        "raw_r15": f"0x{event.raw_r15:08X}",
    }


def _family_object_for_min_x(
    registers: Sequence[int], objects: dict[int, FamilyObject]
) -> FamilyObject | None:
    address = (registers[0] + registers[3]) & 0xFFFFFFFF
    return next(
        (item for item in objects.values() if address == item.object_pointer + 4),
        None,
    )


def _valid_runtime_object_pointer(pointer: int) -> bool:
    return (
        pointer % 4 == 0
        and EWRAM_START <= pointer
        and pointer + OBJECT_SIZE <= EWRAM_END
    )


def _valid_descriptor_pointer(pointer: int) -> bool:
    return pointer % 4 == 0 and ROM_START <= pointer and pointer + 4 <= ROM_END


def _reconstruct_live_registry(
    client: Rom008RspClient,
    *,
    map_entry_address: int,
    load_epoch: int,
) -> tuple[list[dict[str, object]], list[FamilyObject]]:
    """Reconstruct target-family identity from the already-populated registry."""

    map_entry_index = map_entry_index_from_address(map_entry_address)
    count = _read_u32(client, MANAGER)
    if not 0 < count <= 0x400:
        raise RuntimeError("registry count exceeds bounded runtime scan")
    entries: list[dict[str, object]] = []
    matches: list[FamilyObject] = []
    for index in range(count):
        slot = MANAGER + 4 + index * 4
        pointer = _read_u32(client, slot)
        entry: dict[str, object] = {
            "index": index,
            "registry_slot": f"0x{slot:08X}",
            "object": f"0x{pointer:08X}",
            "object_pointer_valid": _valid_runtime_object_pointer(pointer),
        }
        if not _valid_runtime_object_pointer(pointer):
            entries.append(entry)
            continue
        descriptor = _read_u32(client, pointer + 0x14)
        entry["descriptor"] = f"0x{descriptor:08X}"
        entry["descriptor_pointer_valid"] = _valid_descriptor_pointer(descriptor)
        if not _valid_descriptor_pointer(descriptor):
            entries.append(entry)
            continue
        factory_raw = _read_u32(client, descriptor)
        entry["factory_raw"] = f"0x{factory_raw:08X}"
        entry["factory_matches_target"] = factory_raw == TARGET_FACTORY_RAW
        entries.append(entry)
        if factory_raw != TARGET_FACTORY_RAW:
            continue
        bounds = signed_halfwords(_read_bytes(client, pointer + 4, 8))
        if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
            raise RuntimeError("target-family object has empty runtime bounds")
        matches.append(
            FamilyObject(
                load_epoch=load_epoch,
                map_entry_address=map_entry_address,
                map_entry_index=map_entry_index,
                descriptor=descriptor,
                object_pointer=pointer,
                registry_slot=slot,
                bounds=bounds,
                callback_reference_raw=_read_u32(client, pointer + 0x0C),
                object_dispatch_base_raw=_read_u32(client, pointer),
                factory_raw=factory_raw,
            )
        )
    return entries, matches


def _validate_native_event(
    event: ReadEvent,
    *,
    target: FamilyObject,
    sequence: int,
    accepted: bool,
) -> None:
    expected_pc = 0x0801277A if accepted else QUERY_MIN_X_PC
    expected_offset = 0x0C if accepted else 4
    expected_width = 4 if accepted else 2
    expected_address = target.object_pointer + expected_offset
    if (
        event.control_sequence != sequence
        or event.target != target.object_pointer
        or event.load_epoch != target.load_epoch
        or event.descriptor != target.descriptor
        or event.factory_raw != target.factory_raw
        or event.factory_fetch != execution_target(target.factory_raw).fetch_address
        or event.instruction_pc != expected_pc
        or event.relative_offset != expected_offset
        or event.address != expected_address
        or event.access_width != expected_width
        or event.overlap_start != expected_address
        or event.overlap_end != expected_address + expected_width
    ):
        raise RuntimeError("native event lost reconstructed target identity")


def _arm_native(
    client: Rom011RspClient,
    *,
    target: FamilyObject,
    sequence: int,
    accepted: bool,
) -> None:
    response = client.arm_native_probe(
        ArmRequest(
            sequence=sequence,
            target=target.object_pointer,
            load_epoch=target.load_epoch,
            descriptor=target.descriptor,
            match_kind=MATCH_ACCEPTED_X0C if accepted else 0,
        )
    )
    if response != "OK":
        raise RuntimeError(f"native probe arm failed: {response}")


def _wait_native_event(
    client: Rom011RspClient,
    *,
    target: FamilyObject,
    sequence: int,
    accepted: bool,
    deadline: float,
    stop_request: Path,
) -> ReadEvent:
    response, stopped, _ = _await_stop(
        client,
        deadline=deadline,
        stop_request=stop_request,
    )
    if stopped:
        raise RuntimeError("bounded human sequence stopped")
    if not WATCH_STOP_RE.fullmatch(response):
        raise RuntimeError(f"expected native read stop, got {response}")
    event = client.native_probe_event()
    if event is None:
        raise RuntimeError("native stop has no event")
    _validate_native_event(
        event,
        target=target,
        sequence=sequence,
        accepted=accepted,
    )
    if client.acknowledge_native_probe_event(event.event_id) != "OK":
        raise RuntimeError("native event acknowledgement failed")
    return event


def _wait_for_post_load_registry(
    client: Rom011RspClient,
    *,
    load_epoch: int,
    deadline: float,
) -> tuple[
    int,
    int,
    list[dict[str, object]],
    list[FamilyObject],
    list[dict[str, object]],
]:
    """Resume without breakpoints until the command-line state is fully live."""

    attempts: list[dict[str, object]] = []
    while time.monotonic() < deadline:
        active_map = _read_u32(client, ACTIVE_MAP_POINTER)
        count = _read_u32(client, MANAGER)
        attempt: dict[str, object] = {
            "active_map_raw": f"0x{active_map:08X}",
            "registry_count_raw": count,
        }
        try:
            map_index = map_entry_index_from_address(active_map)
            entries, family = _reconstruct_live_registry(
                client,
                map_entry_address=active_map,
                load_epoch=load_epoch,
            )
        except (ValueError, RuntimeError) as exc:
            attempt["ready"] = False
            attempt["detail"] = str(exc)
            attempts.append(attempt)
        else:
            attempt["ready"] = bool(family)
            attempt["map_index"] = map_index
            attempt["family_count"] = len(family)
            attempts.append(attempt)
            if family:
                return active_map, map_index, entries, family, attempts

        try:
            response = client.command("c", timeout=0.25)
        except socket.timeout:
            client.sock.sendall(b"\x03")
            client._read_response(5.0)
        else:
            attempt["continue_response"] = response
    raise TimeoutError("post-transition state did not reach a populated live registry")


def _dispatch_snapshot(
    client: Rom008RspClient,
    registers: Sequence[int],
    *,
    slot_offset: int,
) -> dict[str, object]:
    receiver, object_pointer, entity, concrete_raw = registers[:4]
    dispatch_base = _read_u32(client, receiver)
    slot_raw = _read_u32(client, dispatch_base + slot_offset)
    expected_raw = (dispatch_base + slot_raw) & 0xFFFFFFFF
    if concrete_raw != expected_raw:
        raise RuntimeError("runtime callback target disagrees with relative vtable slot")
    target = execution_target(concrete_raw)
    return {
        "receiver": f"0x{receiver:08X}",
        "object": f"0x{object_pointer:08X}",
        "query_entity": f"0x{entity:08X}",
        "arguments": _register_dict(registers),
        "dispatch_base": f"0x{dispatch_base:08X}",
        "slot_offset": slot_offset,
        "slot_raw_relative": f"0x{slot_raw:08X}",
        "raw_code_pointer": f"0x{concrete_raw:08X}",
        "fetch_address": f"0x{target.fetch_address:08X}",
        "state": target.state,
    }


def _step_until_pc(
    client: Rom008RspClient, target_pc: int, *, max_steps: int
) -> tuple[list[str], Sequence[int]]:
    pcs: list[str] = []
    for _ in range(max_steps):
        client.command("s")
        registers = _registers(client)
        pcs.append(f"0x{registers[15]:08X}")
        if registers[15] == target_pc:
            return pcs, registers
    raise RuntimeError(f"bounded stepping did not reach 0x{target_pc:08X}")


def _trace_callback_without_breakpoint(
    client: Rom008RspClient,
    *,
    raw_target: int,
    return_pc: int,
    max_steps: int,
) -> CallbackTrace:
    target = execution_target(raw_target)
    pcs: list[str] = []
    reached_target = False
    last_registers: tuple[int, ...] | None = None
    for _ in range(max_steps):
        client.command("s")
        registers = tuple(_registers(client))
        last_registers = registers
        pcs.append(f"0x{registers[15]:08X}")
        if registers[15] == target.fetch_address:
            if bool(registers[16] & THUMB_STATE_BIT) != (target.state == "Thumb"):
                raise RuntimeError("callback execution state disagrees with raw target")
            reached_target = True
        if registers[15] == return_pc:
            if not reached_target:
                raise RuntimeError("callback returned without reaching its raw target")
            return CallbackTrace(tuple(pcs), registers, reached_target, True)
    if last_registers is None:
        raise AssertionError("positive callback trace budget produced no step")
    return CallbackTrace(tuple(pcs), last_registers, reached_target, False)


def _action_outcome(trace: CallbackTrace) -> tuple[str, str | None]:
    if not trace.reached_target:
        return "C", "bounded trace did not reach the concrete action target"
    if not trace.returned_to_query:
        return "B", "action executed; bounded trace did not return to the point query"
    return "B", None


def _source_status(
    before: dict[Path, tuple[object, str]],
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path, (old_stat, old_hash) in before.items():
        current = path.stat()
        current_hash = sha256(path)
        result[str(path)] = {
            "sha256": current_hash,
            "size": current.st_size,
            "mtime_ns": current.st_mtime_ns,
            "unchanged": (
                current_hash == old_hash
                and current.st_size == old_stat.st_size  # type: ignore[attr-defined]
                and current.st_mtime_ns == old_stat.st_mtime_ns  # type: ignore[attr-defined]
            ),
        }
    return result


def run_live_session(
    *,
    rom_path: Path,
    state_path: Path,
    save_path: Path,
    state_sha256: str,
    save_sha256: str,
    mgba_path: Path,
    manifest_path: Path,
    run_root: Path,
    timeout_seconds: float,
) -> dict[str, object]:
    workspace_root = Path(__file__).resolve().parents[2]
    allowed_root = (workspace_root / "build" / "rom012").resolve()
    run_root = run_root.resolve()
    if run_root.parent != allowed_root or run_root.exists():
        raise ValueError("run root must be one new direct child of build/rom012")
    build_manifest = verify_instrumented_mgba(mgba_path, manifest_path)
    run_root.mkdir(parents=True)

    sources = (rom_path, state_path, save_path)
    before = {path: (path.stat(), sha256(path)) for path in sources}
    if before[rom_path][0].st_size != EXPECTED_SIZE or before[rom_path][1] != EXPECTED_SHA256:
        raise RuntimeError("verified ROM identity mismatch")
    if before[state_path][1].lower() != state_sha256.lower():
        raise RuntimeError("save-state identity mismatch")
    if before[save_path][1].lower() != save_sha256.lower():
        raise RuntimeError("save identity mismatch")

    state_copy, save_copy = private_working_paths(
        state_source=state_path,
        save_source=save_path,
        run_root=run_root,
        rom_name=rom_path.name,
    )
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

    process_arguments = [
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
        str(rom_path),
    ]
    process = subprocess.Popen(
        process_arguments,
        env=instrumented_environment(build_manifest),
    )
    deadline = time.monotonic() + timeout_seconds
    stop_request = run_root / "stop-request.json"
    sample_request = run_root / "sample-request.json"
    observation_path = run_root / "human-observation.json"
    timeline: list[dict[str, object]] = []
    load_epoch = 1
    result: dict[str, object] | None = None
    session_error: Exception | None = None
    try:
        with _connect(time.monotonic() + 15) as sock:
            client = Rom011RspClient(sock)
            initial_status = client.command("?")
            (
                active_map,
                map_index,
                registry_entries,
                family,
                startup_attempts,
            ) = _wait_for_post_load_registry(
                client,
                load_epoch=load_epoch,
                deadline=min(deadline, time.monotonic() + 15.0),
            )
            query_probe_target = min(family, key=lambda item: item.object_index)
            _write_new_json(
                run_root / "capture-ready.json",
                {
                    "gdb_initial_status": initial_status,
                    "breakpoints": [],
                    "frontend": str(mgba_path),
                    "process_id": process.pid,
                    "source_state": {
                        "path": str(state_path),
                        "sha256": before[state_path][1],
                        "size": before[state_path][0].st_size,
                    },
                    "working_state": str(state_copy),
                    "active_map": f"0x{active_map:08X}",
                    "map_index": map_index,
                    "load_epoch": load_epoch,
                    "registry": f"0x{MANAGER:08X}",
                    "registry_entries": registry_entries,
                    "family_objects": [item.to_dict() for item in family],
                    "startup_attempts": startup_attempts,
                },
            )
            timeline.append(
                {
                    "event": "post_load_registry_reconstruction",
                    "load_epoch": load_epoch,
                    "map_entry": f"0x{active_map:08X}",
                    "map_index": map_index,
                    "family_count": len(family),
                }
            )

            sequence = 1
            _arm_native(
                client,
                target=query_probe_target,
                sequence=sequence,
                accepted=False,
            )
            first_event = _wait_native_event(
                client,
                target=query_probe_target,
                sequence=sequence,
                accepted=False,
                deadline=deadline,
                stop_request=stop_request,
            )
            first_sample = _query_sample(
                client,
                first_event.registers,
                load_epoch=load_epoch,
                object_pointer=query_probe_target.object_pointer,
            )
            selected, delta = choose_nearest_target(
                (first_sample.x, first_sample.y), family
            )
            selection = {
                "identity_chain": (
                    "live registry slot -> runtime object -> object+0x14 retained "
                    "descriptor -> descriptor+0 raw factory"
                ),
                "query": first_sample.to_dict(),
                "native_read_event": _native_event_dict(first_event),
                "active_map": f"0x{active_map:08X}",
                "map_index": map_index,
                "registry": f"0x{MANAGER:08X}",
                "load_epoch": load_epoch,
                "registry_entries": registry_entries,
                "family_objects": [item.to_dict() for item in family],
                "selected": selected.to_dict(),
                "navigation_delta": {"dx": delta[0], "dy": delta[1]},
                "direction": direction_for_delta(*delta),
                "active_breakpoints": [],
            }
            _write_new_json(run_root / "target-selection.json", selection)
            _write_new_json(
                run_root / "move-ready.json",
                {
                    "instruction": (
                        "confirm normal gameplay, move a short known cardinal "
                        "direction, then request a sample"
                    ),
                    **selection,
                },
            )

            response, stopped, woke = _await_stop(
                client,
                deadline=deadline,
                stop_request=stop_request,
                wake_path=sample_request,
            )
            if stopped or not woke:
                raise RuntimeError(f"movement sample was not requested: {response}")
            request = json.loads(sample_request.read_text(encoding="utf-8"))
            if request.get("direction") not in {"north", "south", "east", "west"}:
                raise RuntimeError("movement sample request has invalid direction")

            sequence += 1
            _arm_native(
                client,
                target=query_probe_target,
                sequence=sequence,
                accepted=False,
            )
            second_event = _wait_native_event(
                client,
                target=query_probe_target,
                sequence=sequence,
                accepted=False,
                deadline=deadline,
                stop_request=stop_request,
            )
            second_sample = _query_sample(
                client,
                second_event.registers,
                load_epoch=load_epoch,
                object_pointer=query_probe_target.object_pointer,
            )
            moved_x = second_sample.x - first_sample.x
            moved_y = second_sample.y - first_sample.y
            same_entity = second_sample.entity == first_sample.entity
            consistent = same_entity and movement_is_consistent(
                request["direction"], moved_x, moved_y
            )
            correlation = {
                "first": first_sample.to_dict(),
                "second": second_sample.to_dict(),
                "native_read_event": _native_event_dict(second_event),
                "reported_direction": request["direction"],
                "delta": {"dx": moved_x, "dy": moved_y},
                "same_entity_pointer": same_entity,
                "movement_consistent": consistent,
            }
            _write_new_json(run_root / "query-correlation.json", correlation)
            if not consistent:
                result = {
                    "result": "C",
                    "reason": "query entity did not track the reported player movement",
                    "query_correlation": correlation,
                }
            else:
                current_map = _read_u32(client, ACTIVE_MAP_POINTER)
                current_entries, current_family = _reconstruct_live_registry(
                    client,
                    map_entry_address=current_map,
                    load_epoch=load_epoch,
                )
                selected_now = next(
                    (
                        item
                        for item in current_family
                        if item.object_pointer == selected.object_pointer
                        and item.registry_slot == selected.registry_slot
                        and item.descriptor == selected.descriptor
                        and item.factory_raw == selected.factory_raw
                        and item.bounds == selected.bounds
                    ),
                    None,
                )
                if current_map != active_map or selected_now is None:
                    raise RuntimeError(
                        "active map or reconstructed target changed before arming"
                    )
                nav_delta = rectangle_delta(
                    (second_sample.x, second_sample.y), selected.bounds
                )
                sequence += 1
                _arm_native(
                    client,
                    target=selected,
                    sequence=sequence,
                    accepted=True,
                )
                _write_new_json(
                    run_root / "navigation-ready.json",
                    {
                        "query_correlation": correlation,
                        "current": second_sample.to_dict(),
                        "target": selected.to_dict(),
                        "navigation_delta": {"dx": nav_delta[0], "dy": nav_delta[1]},
                        "direction": direction_for_delta(*nav_delta),
                        "registry_entries_at_arm": current_entries,
                        "active_breakpoints": [],
                        "native_gate": "PC 0x0801277A AND X+0x0C overlap",
                        "instruction": "instrumentation is armed; take control of mGBA",
                    },
                )
                accepted_event = _wait_native_event(
                    client,
                    target=selected,
                    sequence=sequence,
                    accepted=True,
                    deadline=deadline,
                    stop_request=stop_request,
                )
                if accepted_event.registers[1] != selected.object_pointer:
                    raise RuntimeError(
                        "accepted X+0x0C load did not use selected object"
                    )
                hit_map = _read_u32(client, ACTIVE_MAP_POINTER)
                _, hit_family = _reconstruct_live_registry(
                    client,
                    map_entry_address=hit_map,
                    load_epoch=load_epoch,
                )
                exact_hit = next(
                    (
                        item
                        for item in hit_family
                        if item.object_pointer == selected.object_pointer
                        and item.registry_slot == selected.registry_slot
                        and item.descriptor == selected.descriptor
                        and item.factory_raw == selected.factory_raw
                        and item.bounds == selected.bounds
                    ),
                    None,
                )
                if hit_map != active_map or exact_hit is None:
                    raise RuntimeError(
                        "accepted event lost post-load registry identity chain"
                    )
                accepted_sample = _query_sample(
                    client,
                    accepted_event.registers,
                    load_epoch=load_epoch,
                    object_pointer=selected.object_pointer,
                )
                if rectangle_delta(
                    (accepted_sample.x, accepted_sample.y), selected.bounds
                ) != (0, 0):
                    raise RuntimeError(
                        "accepted path coordinates are outside captured bounds"
                    )
                accepted = {
                    "accepted_path_predecessor": f"0x{ACCEPTED_PC:08X}",
                    "captured_pc": "0x0801277A",
                    "native_read_event": _native_event_dict(accepted_event),
                    "query": accepted_sample.to_dict(),
                    "target": selected.to_dict(),
                    "registers": {
                        **{
                            f"r{i}": f"0x{x:08X}"
                            for i, x in enumerate(accepted_event.registers[:13])
                        },
                        "sp": f"0x{accepted_event.registers[13]:08X}",
                        "lr": f"0x{accepted_event.registers[14]:08X}",
                        "pc_raw": f"0x{accepted_event.registers[15]:08X}",
                    },
                    "object_snapshot": _read_bytes(
                        client, selected.object_pointer, OBJECT_SIZE
                    ).hex(),
                    "callback_reference_raw": (
                        f"0x{_read_u32(client, selected.object_pointer + 0x0C):08X}"
                    ),
                }
                _write_new_json(run_root / "accepted-captured.json", accepted)
                approach_trace, filter_regs = _step_until_pc(
                    client, FILTER_CALL_PC, max_steps=16
                )
                filter_data = _dispatch_snapshot(
                    client, filter_regs, slot_offset=8
                )
                filter_trace = _trace_callback_without_breakpoint(
                    client,
                    raw_target=filter_regs[3],
                    return_pc=FILTER_RETURN_PC,
                    max_steps=2048,
                )
                filter_data.update(
                    {
                        "approach_trace": approach_trace,
                        "instruction_trace": list(filter_trace.instruction_trace),
                        "reached_target": filter_trace.reached_target,
                        "returned_to_query": filter_trace.returned_to_query,
                        "return_value": (
                            filter_trace.registers[0]
                            if filter_trace.returned_to_query
                            else None
                        ),
                    }
                )
                _write_new_json(
                    run_root / "filter-captured.json",
                    {"accepted_containment": accepted, "filter": filter_data},
                )
                if not filter_trace.returned_to_query:
                    result = {
                        "result": "C",
                        "reason": "filter trace reached its bounded step limit",
                        "accepted_containment": accepted,
                        "filter": filter_data,
                        "action": None,
                    }
                elif filter_trace.registers[0] == 0:
                    result = {
                        "result": "A",
                        "accepted_containment": accepted,
                        "filter": filter_data,
                        "action": None,
                    }
                else:
                    action_approach, action_regs = _step_until_pc(
                        client, ACTION_CALL_PC, max_steps=16
                    )
                    action_data = _dispatch_snapshot(
                        client, action_regs, slot_offset=4
                    )
                    action_data["approach_trace"] = action_approach
                    _write_new_json(
                        run_root / "action-entered.json",
                        {
                            "accepted_containment": accepted,
                            "filter": filter_data,
                            "action": action_data,
                        },
                    )
                    action_trace = _trace_callback_without_breakpoint(
                        client,
                        raw_target=action_regs[3],
                        return_pc=ACTION_RETURN_PC,
                        max_steps=512,
                    )
                    action_data.update(
                        {
                            "instruction_trace": list(action_trace.instruction_trace),
                            "reached_target": action_trace.reached_target,
                            "returned_to_query": action_trace.returned_to_query,
                            "return_register_r0": (
                                action_trace.registers[0]
                                if action_trace.returned_to_query
                                else None
                            ),
                        }
                    )
                    action_result, action_reason = _action_outcome(action_trace)
                    result = {
                        "result": action_result,
                        "reason": action_reason,
                        "accepted_containment": accepted,
                        "filter": filter_data,
                        "action": action_data,
                    }
                    _write_new_json(run_root / "action-captured.json", result)
                    response, stopped, woke = _await_stop(
                        client,
                        deadline=deadline,
                        stop_request=stop_request,
                        wake_path=observation_path,
                    )
                    if stopped or not woke:
                        raise RuntimeError(
                            f"human observation was not supplied: {response}"
                        )
                    observation = json.loads(
                        observation_path.read_text(encoding="utf-8")
                    )
                    if not str(observation.get("human_observation", "")).strip():
                        raise RuntimeError("human observation is empty")
                    result["human_observation"] = observation["human_observation"]
    except Exception as exc:
        session_error = exc
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    source_artifacts = _source_status(before)
    if not all(item["unchanged"] for item in source_artifacts.values()):
        raise RuntimeError("ROM or source save artifact changed during runtime probe") from session_error
    if session_error is not None:
        failure = {
            "error": type(session_error).__name__,
            "detail": str(session_error),
            "timeline": timeline,
            "source_artifacts": source_artifacts,
        }
        _write_new_json(run_root / "failed.json", failure)
        raise session_error
    if result is None:
        raise AssertionError("session ended without result")
    output = {
        **result,
        "timeline": timeline,
        "source_artifacts": source_artifacts,
    }
    _write_new_json(run_root / "result.json", output)
    write_run_bundle(
        run_root,
        tool="tools.runtime.rom012_live_containment",
        arguments={
            "timeout_seconds": timeout_seconds,
            "manifest_path": str(manifest_path),
        },
        rom=rom_path,
        emulator=mgba_path,
        instrumented_manifest=manifest_path,
        observations={
            "result": output.get("result"),
            "timeline_events": len(timeline),
        },
        artifacts={
            state_copy: "input-savestate",
            save_copy: "savegame",
            run_root / "capture-ready.json": "capture-ready",
        },
    )
    return output


def request_sample(run_root: Path, direction: str) -> Path:
    if direction not in {"north", "south", "east", "west"}:
        raise ValueError("direction must be north, south, east, or west")
    target = run_root.resolve() / "sample-request.json"
    if target.exists():
        raise FileExistsError("sample request already exists")
    target.write_text(json.dumps({"direction": direction}, indent=2) + "\n", encoding="utf-8")
    return target


def write_human_observation(run_root: Path, text: str) -> Path:
    if not text.strip():
        raise ValueError("human observation must not be empty")
    target = run_root.resolve() / "human-observation.json"
    if target.exists():
        raise FileExistsError("human observation already exists")
    target.write_text(json.dumps({"human_observation": text}, indent=2) + "\n", encoding="utf-8")
    return target


def request_stop(run_root: Path) -> Path:
    target = run_root.resolve() / "stop-request.json"
    if target.exists():
        raise FileExistsError("stop request already exists")
    target.write_text('{"bounded_sequence_complete": true}\n', encoding="utf-8")
    return target


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("rom", type=Path)
    run.add_argument("state", type=Path)
    run.add_argument("save", type=Path)
    run.add_argument("--state-sha256", required=True)
    run.add_argument("--save-sha256", required=True)
    run.add_argument("--mgba", type=Path, required=True)
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--run-root", type=Path, required=True)
    run.add_argument("--timeout", type=float, default=900.0)
    sample = commands.add_parser("sample")
    sample.add_argument("run_root", type=Path)
    sample.add_argument("direction", choices=("north", "south", "east", "west"))
    annotate = commands.add_parser("annotate")
    annotate.add_argument("run_root", type=Path)
    annotate.add_argument("text")
    stop = commands.add_parser("stop")
    stop.add_argument("run_root", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "run":
        if args.timeout <= 0:
            raise SystemExit("--timeout must be positive")
        result = run_live_session(
            rom_path=args.rom.resolve(),
            state_path=args.state.resolve(),
            save_path=args.save.resolve(),
            state_sha256=args.state_sha256,
            save_sha256=args.save_sha256,
            mgba_path=args.mgba.resolve(),
            manifest_path=args.manifest.resolve(),
            run_root=args.run_root.resolve(),
            timeout_seconds=args.timeout,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "sample":
        print(request_sample(args.run_root, args.direction))
    elif args.command == "annotate":
        print(write_human_observation(args.run_root, args.text))
    else:
        print(request_stop(args.run_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
