"""Human-assisted exact-object read-watch support for ROM-011."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
from typing import Sequence

from tools.mgba_probe.runtime import (
    ArmRequest,
    ReadEvent,
    instrumented_environment,
    verify_instrumented_mgba,
)
from tools.runtime.evidence_bundle import write_run_bundle
from tools.runtime.rom006_gdb_probe import (
    EXPECTED_SHA256,
    EXPECTED_SIZE,
    RESOLVER_ENTRY_PC,
    RESOLVER_LOAD_PC,
    THUMB_STATE_BIT,
    _connect,
    _register_dict,
    _registers,
    effective_variation_source,
    rsp_packet,
)
from tools.runtime.rom007_factory_probe import (
    ACTIVE_MAP_POINTER_PACKET,
    ADAPTER_PC,
    adapter_entry_is_valid,
    decode_read_u32,
    map_entry_index_from_address,
    validate_registry_insertion,
)
from tools.runtime.rom008_object_trace import (
    FACTORY_RETURN_PC,
    FACTORY_VENEER_PC,
    MANAGER,
    POPULATION_PC,
    REMOVAL_COMMIT_PC,
    REMOVAL_PC,
    RESET_PC,
    LoadIdentity,
    private_working_paths,
    removal_count_commit_is_valid,
    removal_path_reaches_commit,
    reset_count_commit_is_valid,
    signed_halfwords,
    thumb_fetch_is_valid,
)
from tools.runtime.rom008_query_probe import (
    Rom008RspClient,
    _breakpoint,
    _read_bytes,
    _read_u32,
    _remove_breakpoint,
    sha256,
)
from tools.runtime.rom009_object_trace import DynamicExactObjectTracker
from tools.webfoot.analysis.variation_arrays import (
    census_variation_array_first_words,
)
from tools.webfoot.profile import RomProfileCatalog


OBJECT_SIZE = 0x18
EXPECTED_FACTORY_LR = 0x08012679
EXPECTED_RESOLVER_LR = 0x08008ABF
WATCH_STOP_RE = re.compile(r"^T05rwatch:([0-9A-Fa-f]{8});$")
WATCH_FIELDS = (
    ("bounds_min_x", 0x04, 2),
    ("bounds_min_y", 0x06, 2),
    ("bounds_max_x", 0x08, 2),
    ("bounds_max_y", 0x0A, 2),
    ("callback_reference", 0x0C, 4),
    ("retained_descriptor", 0x14, 4),
)
TARGETED_BREAKPOINT_REASON = (
    "16 simultaneous byte read-watchpoints ran below 1 FPS during human-live-11"
)
MIN_PLAYABLE_FPS = 30.0


@dataclass(frozen=True, slots=True)
class ReadWatchpoint:
    field: str
    field_offset: int
    field_width: int
    byte_offset: int
    address: int

    def packet(self, *, remove: bool = False) -> str:
        operation = "z" if remove else "Z"
        return f"{operation}3,{self.address:x},1"


@dataclass(frozen=True, slots=True)
class CodeLoadCandidate:
    pc: int
    routine_entry: int
    field: str
    field_offset: int
    access_width: int
    base_register: int
    immediate: int = 0
    index_register: int | None = None
    signed: bool = False
    instruction: str = ""
    selected: bool = False

    def effective_address(self, registers: Sequence[int]) -> int:
        if len(registers) != 17:
            raise ValueError("candidate hit lacks full ARM register set")
        address = registers[self.base_register] + self.immediate
        if self.index_register is not None:
            address += registers[self.index_register]
        return address

    def matches(self, registers: Sequence[int], object_pointer: int) -> bool:
        return self.effective_address(registers) == object_pointer + self.field_offset

    def to_dict(self) -> dict[str, object]:
        return {
            "pc": f"0x{self.pc:08X}",
            "routine_entry": f"0x{self.routine_entry:08X}",
            "field": self.field,
            "field_offset": self.field_offset,
            "access_width": self.access_width,
            "base_register": f"r{self.base_register}",
            "immediate": self.immediate,
            "index_register": (
                None if self.index_register is None else f"r{self.index_register}"
            ),
            "signed": self.signed,
            "instruction": self.instruction,
            "selected": self.selected,
        }


EXECUTABLE_LOAD_CENSUS = (
    CodeLoadCandidate(0x08012748, 0x080126D4, "bounds_min_x", 0x04, 2, 0, index_register=3, signed=True, instruction="ldrsh r2, [r0, r3]"),
    CodeLoadCandidate(0x08012756, 0x080126D4, "bounds_max_x", 0x08, 2, 0, index_register=3, signed=True, instruction="ldrsh r2, [r0, r3]"),
    CodeLoadCandidate(0x08012764, 0x080126D4, "bounds_min_y", 0x06, 2, 0, index_register=3, signed=True, instruction="ldrsh r2, [r0, r3]"),
    CodeLoadCandidate(0x08012772, 0x080126D4, "bounds_max_y", 0x0A, 2, 0, index_register=3, signed=True, instruction="ldrsh r0, [r0, r3]"),
    CodeLoadCandidate(0x0801277A, 0x080126D4, "callback_reference_after_bounds_match", 0x0C, 4, 1, immediate=12, instruction="ldr r0, [r1, #12]", selected=True),
    CodeLoadCandidate(0x08012792, 0x080126D4, "callback_reference", 0x0C, 4, 1, immediate=12, instruction="ldr r0, [r1, #12]"),
    CodeLoadCandidate(0x080127F6, 0x080127AE, "bounds_min_x", 0x04, 2, 1, index_register=3, signed=True, instruction="ldrsh r7, [r1, r3]"),
    CodeLoadCandidate(0x08012806, 0x080127AE, "bounds_max_x", 0x08, 2, 0, index_register=3, signed=True, instruction="ldrsh r7, [r0, r3]"),
    CodeLoadCandidate(0x08012814, 0x080127AE, "bounds_min_y", 0x06, 2, 0, index_register=3, signed=True, instruction="ldrsh r7, [r0, r3]"),
    CodeLoadCandidate(0x08012822, 0x080127AE, "bounds_max_y", 0x0A, 2, 0, index_register=3, signed=True, instruction="ldrsh r0, [r0, r3]"),
    CodeLoadCandidate(0x08012828, 0x080127AE, "callback_reference_after_bounds_match", 0x0C, 4, 1, immediate=12, instruction="ldr r0, [r1, #12]", selected=True),
    CodeLoadCandidate(0x08012866, 0x08012846, "bounds_min_x", 0x04, 2, 4, index_register=3, signed=True, instruction="ldrsh r0, [r4, r3]"),
    CodeLoadCandidate(0x0801286A, 0x08012846, "bounds_min_y", 0x06, 2, 4, index_register=3, signed=True, instruction="ldrsh r1, [r4, r3]"),
    CodeLoadCandidate(0x0801286E, 0x08012846, "bounds_max_x", 0x08, 2, 4, index_register=3, signed=True, instruction="ldrsh r2, [r4, r3]"),
    CodeLoadCandidate(0x08012872, 0x08012846, "bounds_max_y", 0x0A, 2, 4, index_register=3, signed=True, instruction="ldrsh r7, [r4, r3]"),
    CodeLoadCandidate(0x080128AA, 0x08012846, "dispatch_reference_after_bounds_match", 0x00, 4, 4, instruction="ldr r1, [r4, #0]", selected=True),
    CodeLoadCandidate(0x080075CC, 0x080075AC, "retained_descriptor", 0x14, 4, 6, immediate=20, instruction="ldr r4, [r6, #20]", selected=True),
)
SELECTED_CODE_LOADS = tuple(item for item in EXECUTABLE_LOAD_CENSUS if item.selected)
SELECTED_CODE_LOADS_BY_PC = {item.pc: item for item in SELECTED_CODE_LOADS}


@dataclass(frozen=True, slots=True)
class TargetInstance:
    load_epoch: int
    map_entry_address: int
    map_entry_index: int
    selector: int
    selected_value: int
    descriptor: int
    factory_raw: int
    factory_fetch: int
    object_pointer: int
    registry_slot: int
    bounds: tuple[int, int, int, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "load_epoch": self.load_epoch,
            "map_entry_address": f"0x{self.map_entry_address:08X}",
            "map_entry_index": self.map_entry_index,
            "selector": self.selector,
            "selected_value": f"0x{self.selected_value:08X}",
            "descriptor": f"0x{self.descriptor:08X}",
            "factory_raw": f"0x{self.factory_raw:08X}",
            "factory_fetch": f"0x{self.factory_fetch:08X}",
            "object": f"0x{self.object_pointer:08X}",
            "registry_slot": f"0x{self.registry_slot:08X}",
            "bounds": list(self.bounds),
        }


@dataclass(frozen=True, slots=True)
class WatchHit:
    stop_reply: str
    watched_address: int
    field: str
    field_offset: int
    byte_offset: int
    object_pointer: int
    load_epoch: int
    pc: int
    lr: int
    thumb: bool
    registers: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "stop_reply": self.stop_reply,
            "watched_address": f"0x{self.watched_address:08X}",
            "field": self.field,
            "field_offset": self.field_offset,
            "byte_offset": self.byte_offset,
            "object": f"0x{self.object_pointer:08X}",
            "load_epoch": self.load_epoch,
            "pc": f"0x{self.pc:08X}",
            "lr": f"0x{self.lr:08X}",
            "thumb": self.thumb,
            "read_write": "read",
            "access_width": None,
            "access_width_status": "UNKNOWN pending instruction-level decode",
            "registers": _register_dict(self.registers),
        }


@dataclass(frozen=True, slots=True)
class CodeHit:
    stop_reply: str
    field: str
    field_offset: int
    access_width: int
    object_pointer: int
    load_epoch: int
    pc: int
    lr: int
    thumb: bool
    value_raw: int
    value_signed: int | None
    effective_address: int
    instruction: str
    registers: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "stop_reply": self.stop_reply,
            "field": self.field,
            "field_offset": self.field_offset,
            "object": f"0x{self.object_pointer:08X}",
            "load_epoch": self.load_epoch,
            "pc": f"0x{self.pc:08X}",
            "lr": f"0x{self.lr:08X}",
            "thumb": self.thumb,
            "read_write": "read",
            "access_width": self.access_width,
            "effective_address": f"0x{self.effective_address:08X}",
            "value_raw": f"0x{self.value_raw:0{self.access_width * 2}X}",
            "value_signed": self.value_signed,
            "instruction": self.instruction,
            "registers": _register_dict(self.registers),
        }


@dataclass(frozen=True, slots=True)
class DevRangeHit:
    stop_reply: str
    watched_address: int
    field: str
    field_offset: int
    byte_offset: int
    access_width: int
    object_pointer: int
    load_epoch: int
    pc: int
    lr: int
    thumb: bool
    value_raw: int
    registers: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "stop_reply": self.stop_reply,
            "watched_address": f"0x{self.watched_address:08X}",
            "field": self.field,
            "field_offset": self.field_offset,
            "byte_offset": self.byte_offset,
            "object": f"0x{self.object_pointer:08X}",
            "load_epoch": self.load_epoch,
            "pc": f"0x{self.pc:08X}",
            "lr": f"0x{self.lr:08X}",
            "thumb": self.thumb,
            "read_write": "read",
            "access_width": self.access_width,
            "value_raw": f"0x{self.value_raw:0{self.access_width * 2}X}",
            "registers": _register_dict(self.registers),
        }


class HumanWatchState:
    """Fail-closed lifecycle, first-hit, no-hit, and annotation state."""

    def __init__(self) -> None:
        self.current: TargetInstance | None = None
        self.first_hit: WatchHit | CodeHit | DevRangeHit | ReadEvent | None = None
        self.human_annotation: str | None = None
        self.events: list[str] = []
        self.transition_count = 0
        self.last_armed_epoch = 0
        self.no_hit = False

    def arm(self, target: TargetInstance) -> None:
        if self.first_hit is not None or self.no_hit:
            raise ValueError("session already stopped")
        if self.last_armed_epoch:
            if target.load_epoch <= self.last_armed_epoch:
                raise ValueError("replacement target does not advance load epoch")
            self.transition_count += 1
            if self.transition_count > 1:
                raise ValueError("more than one map transition is outside ROM-011 scope")
        self.current = target
        self.last_armed_epoch = target.load_epoch
        self.events.append("armed")

    def retire(self, object_pointer: int, load_epoch: int) -> None:
        if self.current is None:
            raise ValueError("no current target to retire")
        if (
            self.current.object_pointer != object_pointer
            or self.current.load_epoch != load_epoch
        ):
            raise ValueError("retirement does not match current target identity")
        self.events.append("retired")
        self.current = None

    def accept_hit(
        self,
        response: str,
        registers: Sequence[int],
        watchpoints: Sequence[ReadWatchpoint],
    ) -> WatchHit:
        if self.first_hit is not None:
            raise ValueError("first meaningful hit already captured")
        if self.no_hit:
            raise ValueError("session already stopped as no-hit")
        if self.current is None:
            raise ValueError("watchpoint hit has no same-epoch target")
        watchpoint = parse_read_watch_stop(response, watchpoints)
        if not self.current.object_pointer <= watchpoint.address < (
            self.current.object_pointer + OBJECT_SIZE
        ):
            raise ValueError("watchpoint address does not belong to current object")
        if len(registers) != 17:
            raise ValueError("watchpoint hit lacks full ARM register set")
        hit = WatchHit(
            stop_reply=response,
            watched_address=watchpoint.address,
            field=watchpoint.field,
            field_offset=watchpoint.field_offset,
            byte_offset=watchpoint.byte_offset,
            object_pointer=self.current.object_pointer,
            load_epoch=self.current.load_epoch,
            pc=registers[15],
            lr=registers[14],
            thumb=bool(registers[16] & THUMB_STATE_BIT),
            registers=tuple(registers),
        )
        self.first_hit = hit
        self.events.append("first_hit")
        return hit

    def annotate(self, text: str) -> None:
        if self.first_hit is None:
            raise ValueError("human annotation requires captured executable evidence")
        if not text.strip():
            raise ValueError("human annotation must not be empty")
        self.human_annotation = text
        self.events.append("human_annotation")

    def accept_code_hit(
        self,
        response: str,
        registers: Sequence[int],
        candidate: CodeLoadCandidate,
        value_bytes: bytes,
    ) -> CodeHit:
        if self.first_hit is not None:
            raise ValueError("first meaningful hit already captured")
        if self.no_hit:
            raise ValueError("session already stopped as no-hit")
        if self.current is None:
            raise ValueError("code-load hit has no same-epoch target")
        if not candidate.matches(registers, self.current.object_pointer):
            raise ValueError("code-load hit effective address is not current X")
        if len(value_bytes) != candidate.access_width:
            raise ValueError("code-load hit value width mismatch")
        value_raw = int.from_bytes(value_bytes, "little", signed=False)
        value_signed = (
            int.from_bytes(value_bytes, "little", signed=True)
            if candidate.signed
            else None
        )
        hit = CodeHit(
            stop_reply=response,
            field=candidate.field,
            field_offset=candidate.field_offset,
            access_width=candidate.access_width,
            object_pointer=self.current.object_pointer,
            load_epoch=self.current.load_epoch,
            pc=registers[15],
            lr=registers[14],
            thumb=bool(registers[16] & THUMB_STATE_BIT),
            value_raw=value_raw,
            value_signed=value_signed,
            effective_address=candidate.effective_address(registers),
            instruction=candidate.instruction,
            registers=tuple(registers),
        )
        self.first_hit = hit
        self.events.append("first_hit")
        return hit

    def accept_dev_range_hit(
        self, response: str, payload: dict[str, object]
    ) -> DevRangeHit:
        if self.first_hit is not None:
            raise ValueError("first meaningful hit already captured")
        if self.no_hit:
            raise ValueError("session already stopped as no-hit")
        if self.current is None:
            raise ValueError("range hit has no same-epoch target")
        address = int(payload["address"])
        width = int(payload["width"])
        access_type = int(payload["access_type"])
        offset = address - self.current.object_pointer
        if access_type != 2:
            raise ValueError("development range callback was not a read")
        if width not in {1, 2, 4}:
            raise ValueError("development range callback width is unsupported")
        field_match = next(
            (
                (field, field_offset, field_width)
                for field, field_offset, field_width in WATCH_FIELDS
                if field_offset <= offset < field_offset + field_width
            ),
            None,
        )
        if field_match is None:
            raise ValueError("development range callback touched an excluded byte")
        field, field_offset, _ = field_match
        register_names = [f"r{index}" for index in range(13)] + [
            "sp",
            "lr",
            "pc",
            "cpsr",
        ]
        registers = tuple(int(payload[name]) & 0xFFFFFFFF for name in register_names)
        value_mask = (1 << (width * 8)) - 1
        hit = DevRangeHit(
            stop_reply=response,
            watched_address=address,
            field=field,
            field_offset=field_offset,
            byte_offset=offset,
            access_width=width,
            object_pointer=self.current.object_pointer,
            load_epoch=self.current.load_epoch,
            pc=registers[15],
            lr=registers[14],
            thumb=bool(registers[16] & THUMB_STATE_BIT),
            value_raw=int(payload["old_value"]) & value_mask,
            registers=registers,
        )
        self.first_hit = hit
        self.events.append("first_hit")
        return hit

    def accept_native_hit(self, hit: ReadEvent) -> ReadEvent:
        if self.first_hit is not None:
            raise ValueError("first meaningful hit already captured")
        if self.no_hit:
            raise ValueError("session already stopped as no-hit")
        if self.current is None:
            raise ValueError("native range hit has no same-epoch target")
        if (
            hit.target != self.current.object_pointer
            or hit.load_epoch != self.current.load_epoch
            or hit.descriptor != self.current.descriptor
            or hit.factory_raw != self.current.factory_raw
            or hit.factory_fetch != self.current.factory_fetch
        ):
            raise ValueError("native range hit does not match current X identity")
        self.first_hit = hit
        self.events.append("first_hit")
        return hit

    def finish_no_hit(self) -> None:
        if self.current is None:
            raise ValueError("no-hit requires valid armed instrumentation")
        if self.first_hit is not None:
            raise ValueError("captured hit prevents no-hit result")
        self.no_hit = True
        self.events.append("no_hit")


class Rom011RspClient(Rom008RspClient):
    """Narrowly permit exact read-watchpoint packets for dynamic X bytes."""

    def __init__(self, sock: socket.socket):
        super().__init__(sock)
        self._allowed_watch_packets: set[str] = set()

    def arm_native_probe(self, request: ArmRequest) -> str:
        payload = (
            f"qLog1ProbeArm:{request.sequence:x},{request.target:08x},"
            f"{request.load_epoch:x},{request.descriptor:08x},"
            f"{request.factory_raw:08x},{request.factory_fetch:08x},"
            f"{request.match_kind:x},"
            f"{request.profile_sha256}"
        )
        self.sock.sendall(rsp_packet(payload))
        return self._read_response(5.0)

    def disarm_native_probe(self, sequence: int) -> str:
        payload = f"qLog1ProbeDisarm:{sequence:x}"
        self.sock.sendall(rsp_packet(payload))
        return self._read_response(5.0)

    def native_probe_event(self) -> ReadEvent | None:
        self.sock.sendall(rsp_packet("qLog1ProbeEvent"))
        response = self._read_response(5.0)
        if not response:
            return None
        return ReadEvent.from_rsp(response)

    def acknowledge_native_probe_event(self, event_id: int) -> str:
        self.sock.sendall(rsp_packet(f"qLog1ProbeAck:{event_id:x}"))
        return self._read_response(5.0)

    def allow_watchpoint(
        self, watchpoint: ReadWatchpoint, *, remove: bool = False
    ) -> str:
        packet = watchpoint.packet(remove=remove)
        self._allowed_watch_packets.add(packet)
        return packet

    def command(self, payload: str, timeout: float = 5.0) -> str:
        if payload in self._allowed_watch_packets:
            self.sock.sendall(rsp_packet(payload))
            return self._read_response(timeout)
        return super().command(payload, timeout)


def build_read_watchpoints(object_pointer: int) -> tuple[ReadWatchpoint, ...]:
    if (
        isinstance(object_pointer, bool)
        or not isinstance(object_pointer, int)
        or object_pointer % 4
        or not 0x02000000 <= object_pointer
        or object_pointer + OBJECT_SIZE > 0x02040000
    ):
        raise ValueError("object pointer is not an aligned complete EWRAM object")
    watchpoints: list[ReadWatchpoint] = []
    for field, offset, width in WATCH_FIELDS:
        for byte_offset in range(offset, offset + width):
            watchpoints.append(
                ReadWatchpoint(
                    field=field,
                    field_offset=offset,
                    field_width=width,
                    byte_offset=byte_offset,
                    address=object_pointer + byte_offset,
                )
            )
    if len({item.address for item in watchpoints}) != 16:
        raise AssertionError("ROM-011 watchpoint construction is not byte-exact")
    return tuple(watchpoints)


def build_first_access_watchpoint(object_pointer: int) -> ReadWatchpoint:
    watchpoints = build_read_watchpoints(object_pointer)
    return next(item for item in watchpoints if item.byte_offset == 0x04)


def parse_read_watch_stop(
    response: str, watchpoints: Sequence[ReadWatchpoint]
) -> ReadWatchpoint:
    match = WATCH_STOP_RE.fullmatch(response)
    if match is None:
        raise ValueError("stop reply is not an mGBA read-watchpoint hit")
    address = int(match.group(1), 16)
    matches = [item for item in watchpoints if item.address == address]
    if len(matches) != 1:
        raise ValueError("read-watchpoint hit is outside the armed exact-X bytes")
    return matches[0]


def install_read_watchpoints(
    client: Rom011RspClient, watchpoints: Sequence[ReadWatchpoint]
) -> list[dict[str, str]]:
    installed: list[dict[str, str]] = []
    try:
        for watchpoint in watchpoints:
            packet = client.allow_watchpoint(watchpoint)
            response = client.command(packet)
            if response != "OK":
                raise RuntimeError(
                    f"read watchpoint rejected at 0x{watchpoint.address:08X}: {response!r}"
                )
            installed.append(
                {
                    "packet": packet,
                    "response": response,
                    "address": f"0x{watchpoint.address:08X}",
                    "field": watchpoint.field,
                }
            )
    except Exception:
        for watchpoint in watchpoints[: len(installed)]:
            packet = client.allow_watchpoint(watchpoint, remove=True)
            client.command(packet)
        raise
    return installed


def remove_read_watchpoints(
    client: Rom011RspClient, watchpoints: Sequence[ReadWatchpoint]
) -> None:
    for watchpoint in watchpoints:
        packet = client.allow_watchpoint(watchpoint, remove=True)
        if client.command(packet) != "OK":
            raise RuntimeError(
                f"read watchpoint removal rejected at 0x{watchpoint.address:08X}"
            )


def install_targeted_code_breakpoints(
    client: Rom011RspClient, installed_breakpoints: set[int]
) -> list[dict[str, object]]:
    installed: list[dict[str, object]] = []
    for candidate in SELECTED_CODE_LOADS:
        if candidate.pc not in installed_breakpoints:
            _breakpoint(client, candidate.pc)
            installed_breakpoints.add(candidate.pc)
        installed.append({**candidate.to_dict(), "response": "OK"})
    return installed


def instrumentation_fallback(
    response: str | None, *, playable: bool = True
) -> str:
    if response == "OK" and playable:
        return "read_watchpoints"
    return "targeted_code_breakpoints"


def reproduction_matches(
    original: WatchHit, repeated: WatchHit, *, same_action: bool
) -> bool:
    return (
        same_action
        and original.pc == repeated.pc
        and original.field_offset == repeated.field_offset
        and repeated.object_pointer != 0
        and repeated.load_epoch > 0
    )


def _write_new_json(path: Path, payload: dict[str, object]) -> None:
    if path.exists():
        raise FileExistsError(f"runtime output already exists: {path}")
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists():
        raise FileExistsError(f"temporary runtime output already exists: {temporary}")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _write_new_text(path: Path, text: str) -> None:
    if path.exists():
        raise FileExistsError(f"runtime output already exists: {path}")
    path.write_text(text, encoding="utf-8")


def _lua_path(path: Path) -> str:
    return json.dumps(path.resolve().as_posix())


def _dev_startup_wrapper(
    *,
    controller: Path,
    setup_script: Path,
    lua_ready_path: Path,
    arm_command_prefix: Path,
    setup_stopped_path: Path,
    range_ready_prefix: Path,
    benchmark_path: Path,
    hit_path: Path,
) -> str:
    values = {
        "setup_script": setup_script,
        "lua_ready_path": lua_ready_path,
        "arm_command_prefix": arm_command_prefix,
        "setup_stopped_path": setup_stopped_path,
        "range_ready_prefix": range_ready_prefix,
        "benchmark_path": benchmark_path,
        "hit_path": hit_path,
    }
    lines = ["rom011_dev = {"]
    lines.extend(f"    {key} = {_lua_path(value)}," for key, value in values.items())
    lines.extend(["}", f"dofile({_lua_path(controller)})", ""])
    return "\n".join(lines)


def _wait_for_marker(path: Path, process: subprocess.Popen[bytes], timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        exit_code = process.poll()
        if exit_code is not None:
            raise RuntimeError(
                f"mGBA exited with code {exit_code} before marker {path.name}"
            )
        time.sleep(0.05)
    raise TimeoutError(f"timed out waiting for marker {path.name}")


def _event(registers: Sequence[int]) -> dict[str, object]:
    return {
        "pc": f"0x{registers[15]:08X}",
        "lr": f"0x{registers[14]:08X}",
        "thumb": bool(registers[16] & THUMB_STATE_BIT),
        "registers": _register_dict(registers),
    }


def _accept_dev_range_result(
    *,
    state: HumanWatchState,
    response: str,
    hit_path: Path,
    client: Rom011RspClient,
) -> dict[str, object]:
    payload = json.loads(hit_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("development range hit is not a JSON object")
    hit = state.accept_dev_range_hit(response, payload)
    current = state.current
    if current is None:
        raise AssertionError("accepted development range hit lost current target")
    return {
        "result": "FIRST_HIT",
        "target": current.to_dict(),
        "hit": hit.to_dict(),
        "instrumentation_method": "development_lua_range_watchpoint",
        "object_snapshot": _read_bytes(
            client, current.object_pointer, OBJECT_SIZE
        ).hex(),
        "instruction_window_address": f"0x{max(0, hit.pc - 8):08X}",
        "instruction_window": _read_bytes(
            client, max(0, hit.pc - 8), 16
        ).hex(),
    }


def _accept_native_result(
    *,
    state: HumanWatchState,
    event: ReadEvent,
    client: Rom011RspClient,
) -> dict[str, object]:
    hit = state.accept_native_hit(event)
    current = state.current
    if current is None:
        raise AssertionError("accepted native range hit lost current target")
    return {
        "result": "FIRST_HIT",
        "target": current.to_dict(),
        "hit": hit.to_dict(),
        "instrumentation_method": "pinned_mgba_native_one_shot_range",
        "object_snapshot": _read_bytes(
            client, current.object_pointer, OBJECT_SIZE
        ).hex(),
        "instruction_window_address": f"0x{max(0, hit.instruction_pc - 8):08X}",
        "instruction_window": _read_bytes(
            client, max(0, hit.instruction_pc - 8), 16
        ).hex(),
    }


def _await_stop(
    client: Rom011RspClient,
    *,
    deadline: float,
    stop_request: Path,
    wake_path: Path | None = None,
) -> tuple[str, bool, bool]:
    running = False
    while time.monotonic() < deadline:
        if stop_request.exists():
            if running:
                client.sock.sendall(b"\x03")
                response = client._read_response(5.0)
            else:
                response = client.command("?")
            return response, True, False
        if wake_path is not None and wake_path.exists():
            if running:
                client.sock.sendall(b"\x03")
                response = client._read_response(5.0)
            else:
                response = client.command("?")
            return response, False, True
        try:
            if running:
                response = client._read_response(0.5)
            else:
                response = client.command("c", timeout=0.5)
            return response, False, False
        except socket.timeout:
            running = True
    raise TimeoutError("bounded human gameplay session timed out")


def _inject_lua(
    *,
    injector_path: Path,
    process_id: int,
    lua_path: Path,
    ready_path: Path,
    marker_path: Path | None = None,
) -> None:
    arguments = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(injector_path),
        "-TargetProcessId",
        str(process_id),
        "-LuaPath",
        str(lua_path),
        "-ReadyPath",
        str(ready_path),
    ]
    if marker_path is not None:
        arguments.extend(["-MarkerPath", str(marker_path)])
    try:
        subprocess.run(
            arguments,
            check=True,
            timeout=45,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        output = (exc.stderr or exc.stdout or str(exc)).strip()
        raise RuntimeError(f"Lua injector failed: {output}") from exc


def run_live_session(
    *,
    rom_path: Path,
    state_path: Path,
    save_path: Path,
    state_sha256: str,
    save_sha256: str,
    mgba_path: Path,
    profile_path: Path,
    run_root: Path,
    timeout_seconds: float,
    dev_lua_range: bool = False,
    native_probe: bool = True,
    manifest_path: Path | None = None,
) -> dict[str, object]:
    workspace_root = Path(__file__).resolve().parents[2]
    allowed_root = (workspace_root / "build" / "rom011").resolve()
    run_root = run_root.resolve()
    if run_root.parent != allowed_root or run_root.exists():
        raise ValueError("run root must be one new direct child of build/rom011")
    build_manifest: dict[str, object] | None = None
    if dev_lua_range:
        raise ValueError(
            "development Lua range has no recorded mGBA build identity, so it "
            "must not launch"
        )
    if manifest_path is None:
        raise ValueError("native probe requires an instrumented-build manifest")
    build_manifest = verify_instrumented_mgba(mgba_path, manifest_path)
    run_root.mkdir(parents=True)

    sources = (rom_path, state_path, save_path)
    before = {path: (path.stat(), sha256(path)) for path in sources}
    if (
        before[rom_path][0].st_size != EXPECTED_SIZE
        or before[rom_path][1] != EXPECTED_SHA256
    ):
        raise RuntimeError("verified ROM identity mismatch")
    if before[state_path][1].lower() != state_sha256.lower():
        raise RuntimeError("save-state identity mismatch")
    if before[save_path][1].lower() != save_sha256.lower():
        raise RuntimeError("save identity mismatch")

    census = census_variation_array_first_words(
        rom_path, RomProfileCatalog.load(profile_path)
    )
    by_index = {item.map_entry_index: item for item in census.observations}
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

    injector_path = workspace_root / "tools" / "runtime" / "inject_mgba_lua.ps1"
    setup_lua = workspace_root / "tools" / "runtime" / "rom009_clean_route.lua"
    stop_setup_lua = workspace_root / "tools" / "runtime" / "rom011_stop_setup.lua"
    idle_benchmark_lua = (
        workspace_root / "tools" / "runtime" / "rom011_idle_benchmark.lua"
    )
    dev_controller = workspace_root / "tools" / "runtime" / "rom011_dev_range.lua"
    lua_ready_path = run_root / "lua-ready.txt"
    dev_arm_command = run_root / "dev-arm-command.txt"
    dev_setup_stopped = run_root / "setup-stopped-1.txt"
    dev_range_ready = run_root / "dev-range-ready.txt"
    dev_benchmark = run_root / "idle-benchmark-complete.txt"
    dev_hit_path = run_root / "dev-range-hit.json"
    startup_wrapper: Path | None = None
    if dev_lua_range:
        startup_wrapper = run_root / "startup.lua"
        _write_new_text(
            startup_wrapper,
            _dev_startup_wrapper(
                controller=dev_controller,
                setup_script=setup_lua,
                lua_ready_path=lua_ready_path,
                arm_command_path=dev_arm_command,
                setup_stopped_path=dev_setup_stopped,
                range_ready_path=dev_range_ready,
                benchmark_path=dev_benchmark,
                hit_path=dev_hit_path,
            ),
        )

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
    ]
    if startup_wrapper is not None:
        process_arguments.extend(["--script", str(startup_wrapper)])
    process_arguments.append(str(rom_path))
    process_environment = (
        instrumented_environment(build_manifest)
        if build_manifest is not None
        else None
    )
    process = subprocess.Popen(process_arguments, env=process_environment)
    started = time.monotonic()
    deadline = started + timeout_seconds
    stop_request = run_root / "stop-request.json"
    tracker = DynamicExactObjectTracker()
    state = HumanWatchState()
    timeline: list[dict[str, object]] = []
    armed_targets: list[dict[str, object]] = []
    current_watchpoints: tuple[ReadWatchpoint, ...] = ()
    pending_armed: dict[str, object] | None = None
    pending_armed_marker: Path | None = None
    benchmark_complete: Path | None = None
    benchmark_started: float | None = None
    wrong_object_code_hits = {item.pc: 0 for item in SELECTED_CODE_LOADS}
    setup_stop_consumed = False
    accepted_entry: tuple[int, int] | None = None
    verified_load: LoadIdentity | None = None
    verified_adapter = False
    pending_factory = False
    lifecycle_breakpoints = {RESET_PC, REMOVAL_PC}
    discovery_breakpoints = {
        POPULATION_PC,
        RESOLVER_ENTRY_PC,
        RESOLVER_LOAD_PC,
        ADAPTER_PC,
    }
    installed_breakpoints = lifecycle_breakpoints | discovery_breakpoints
    session_error: Exception | None = None
    result: dict[str, object] | None = None
    try:
        benchmark_lua = dev_controller if dev_lua_range else idle_benchmark_lua
        if native_probe:
            pass
        elif dev_lua_range:
            _wait_for_marker(lua_ready_path, process, 15)
        else:
            _inject_lua(
                injector_path=injector_path,
                process_id=process.pid,
                lua_path=setup_lua,
                ready_path=lua_ready_path,
            )
        with _connect(time.monotonic() + 15) as sock:
            client = Rom011RspClient(sock)
            initial_status = client.command("?")
            for address in installed_breakpoints:
                _breakpoint(client, address)
            _write_new_json(
                run_root / "capture-ready.json",
                {
                    "gdb_initial_status": initial_status,
                    "breakpoints": [
                        f"0x{address:08X}" for address in sorted(installed_breakpoints)
                    ],
                    "frontend": str(mgba_path),
                    "process_id": process.pid,
                },
            )
            while time.monotonic() < deadline:
                wake_path = benchmark_complete
                if wake_path is None and dev_lua_range and armed_targets:
                    wake_path = dev_hit_path
                response, stop_requested, benchmark_ready = _await_stop(
                    client,
                    deadline=deadline,
                    stop_request=stop_request,
                    wake_path=wake_path,
                )
                if benchmark_ready:
                    if benchmark_complete is None:
                        result = _accept_dev_range_result(
                            state=state,
                            response=response,
                            hit_path=dev_hit_path,
                            client=client,
                        )
                        break
                    if (
                        pending_armed is None
                        or pending_armed_marker is None
                        or benchmark_complete is None
                        or benchmark_started is None
                    ):
                        raise AssertionError("benchmark woke without pending arm state")
                    frame_text = benchmark_complete.read_text(encoding="ascii")
                    if frame_text == "HIT" and dev_lua_range:
                        result = _accept_dev_range_result(
                            state=state,
                            response=response,
                            hit_path=dev_hit_path,
                            client=client,
                        )
                        break
                    if frame_text != "180":
                        raise RuntimeError("idle benchmark frame marker mismatch")
                    if dev_lua_range:
                        if not dev_range_ready.exists():
                            raise RuntimeError("development range ready marker missing")
                        if not dev_setup_stopped.exists():
                            raise RuntimeError("development setup-stop marker missing")
                    elapsed = time.monotonic() - benchmark_started
                    observed_fps = 180 / elapsed
                    if observed_fps < MIN_PLAYABLE_FPS:
                        raise RuntimeError(
                            f"instrumentation benchmark was not playable: "
                            f"{observed_fps:.3f} FPS"
                        )
                    pending_armed["performance_benchmark"] = {
                        "script": str(benchmark_lua),
                        "script_sha256": sha256(benchmark_lua),
                        "input_injected": False,
                        "frames": 180,
                        "elapsed_seconds": elapsed,
                        "observed_fps": observed_fps,
                        "minimum_playable_fps": MIN_PLAYABLE_FPS,
                        "wrong_object_breakpoint_hits": {
                            f"0x{pc:08X}": count
                            for pc, count in wrong_object_code_hits.items()
                        },
                    }
                    armed_targets.append(pending_armed)
                    _write_new_json(pending_armed_marker, pending_armed)
                    timeline.append(
                        {
                            "event": "armed",
                            **pending_armed["target"],
                            "observed_fps": observed_fps,
                        }
                    )
                    pending_armed = None
                    pending_armed_marker = None
                    benchmark_complete = None
                    benchmark_started = None
                    continue
                if stop_requested:
                    state.finish_no_hit()
                    result = {
                        "result": "E",
                        "reason": (
                            "bounded human sequence reported complete with no X read"
                        ),
                        "stop_reply": response,
                    }
                    break
                if WATCH_STOP_RE.fullmatch(response):
                    if native_probe:
                        native_event = client.native_probe_event()
                        if native_event is None:
                            raise RuntimeError(
                                "native watch stop arrived without captured event"
                            )
                        result = _accept_native_result(
                            state=state,
                            event=native_event,
                            client=client,
                        )
                        acknowledge = client.acknowledge_native_probe_event(
                            native_event.event_id
                        )
                        if acknowledge != "OK":
                            raise RuntimeError(
                                f"native event acknowledgement failed: {acknowledge}"
                            )
                        break
                    registers = _registers(client)
                    hit = state.accept_hit(
                        response, registers, current_watchpoints
                    )
                    current = state.current
                    if current is None:
                        raise AssertionError("accepted hit lost current target")
                    result = {
                        "result": "FIRST_HIT",
                        "target": current.to_dict(),
                        "hit": hit.to_dict(),
                        "instrumentation_method": "hybrid_first_access",
                        "object_snapshot": _read_bytes(
                            client, current.object_pointer, OBJECT_SIZE
                        ).hex(),
                        "instruction_window_address": (
                            f"0x{max(0, registers[15] - 8):08X}"
                        ),
                        "instruction_window": _read_bytes(
                            client, max(0, registers[15] - 8), 16
                        ).hex(),
                    }
                    break

                registers = _registers(client)
                pc = registers[15]
                code_candidate = SELECTED_CODE_LOADS_BY_PC.get(pc)
                if code_candidate is not None:
                    current = state.current
                    if current is None or not code_candidate.matches(
                        registers, current.object_pointer
                    ):
                        wrong_object_code_hits[code_candidate.pc] += 1
                        continue
                    value_bytes = _read_bytes(
                        client,
                        current.object_pointer + code_candidate.field_offset,
                        code_candidate.access_width,
                    )
                    hit = state.accept_code_hit(
                        response, registers, code_candidate, value_bytes
                    )
                    result = {
                        "result": "FIRST_HIT",
                        "target": current.to_dict(),
                        "hit": hit.to_dict(),
                        "instrumentation_method": "targeted_code_breakpoints",
                        "object_snapshot": _read_bytes(
                            client, current.object_pointer, OBJECT_SIZE
                        ).hex(),
                        "instruction_window_address": (
                            f"0x{max(0, registers[15] - 8):08X}"
                        ),
                        "instruction_window": _read_bytes(
                            client, max(0, registers[15] - 8), 16
                        ).hex(),
                    }
                    break
                if pc == RESET_PC:
                    if current_watchpoints:
                        remove_read_watchpoints(client, current_watchpoints)
                        current_watchpoints = ()
                    if state.current is not None:
                        if native_probe:
                            disarm_response = client.disarm_native_probe(
                                state.current.load_epoch
                            )
                            if disarm_response != "OK":
                                raise RuntimeError(
                                    "native range probe failed to disarm on reset: "
                                    f"{disarm_response}"
                                )
                            for address in sorted(discovery_breakpoints):
                                if address not in installed_breakpoints:
                                    _breakpoint(client, address)
                                    installed_breakpoints.add(address)
                        state.retire(
                            state.current.object_pointer, state.current.load_epoch
                        )
                    if not thumb_fetch_is_valid(pc, registers[16], RESET_PC):
                        raise RuntimeError(
                            "registry reset did not execute in Thumb state"
                        )
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
                        raise RuntimeError(
                            "registry reset left its verified store path"
                        )
                    if not reset_count_commit_is_valid(_read_u32(client, MANAGER)):
                        raise RuntimeError(
                            "registry reset did not commit zero count"
                        )
                    tracker.retire_reset()
                    verified_load = None
                    verified_adapter = False
                    timeline.append({"event": "reset", **_event(registers)})
                elif pc == RESOLVER_ENTRY_PC:
                    try:
                        index = map_entry_index_from_address(registers[0])
                    except ValueError:
                        continue
                    if (
                        registers[1] == 1
                        and registers[14] == EXPECTED_RESOLVER_LR
                        and bool(registers[16] & THUMB_STATE_BIT)
                    ):
                        accepted_entry = (registers[0], index)
                        verified_adapter = False
                elif pc == RESOLVER_LOAD_PC and accepted_entry is not None:
                    observation = by_index[accepted_entry[1]]
                    source = effective_variation_source(registers[0])
                    if (
                        registers[1] != 4
                        or source != observation.source_pointer_raw
                    ):
                        raise RuntimeError(
                            "resolver load disagrees with runtime MapEntry"
                        )
                    client.command("s")
                    after = _registers(client)
                    if (
                        after[15] != RESOLVER_LOAD_PC + 2
                        or after[0] != observation.first_word_raw
                    ):
                        raise RuntimeError(
                            "resolver value disagrees with static first word"
                        )
                    verified_load = LoadIdentity(
                        map_entry_address=accepted_entry[0],
                        map_entry_index=accepted_entry[1],
                        selector=1,
                        variation_source=source,
                        selected_value=after[0],
                    )
                elif pc == ADAPTER_PC and verified_load is not None:
                    if not adapter_entry_is_valid(
                        registers, verified_load.selected_value
                    ):
                        raise RuntimeError(
                            "adapter lost verified runtime-selected value"
                        )
                    verified_adapter = True
                elif pc == POPULATION_PC and registers[0] == MANAGER:
                    if verified_load is None or not verified_adapter:
                        raise RuntimeError(
                            "population reached without resolver/adapter identity"
                        )
                    load_epoch = tracker.begin_population(
                        registers[0], verified_load
                    )
                    verified_adapter = False
                    address = decode_read_u32(
                        client.command(ACTIVE_MAP_POINTER_PACKET)
                    )
                    index = map_entry_index_from_address(address)
                    observation = by_index[index]
                    if (
                        address != verified_load.map_entry_address
                        or index != verified_load.map_entry_index
                        or observation.source_pointer_raw
                        != verified_load.variation_source
                        or observation.first_word_raw
                        != verified_load.selected_value
                    ):
                        raise RuntimeError(
                            "active map disagrees with resolver load identity"
                        )
                    timeline.append(
                        {
                            "event": "population",
                            "load_epoch": load_epoch,
                            "map_entry": f"0x{address:08X}",
                            "map_index": index,
                            "selector": verified_load.selector,
                            "selected_value": (
                                f"0x{verified_load.selected_value:08X}"
                            ),
                        }
                    )
                    for address in (FACTORY_VENEER_PC, FACTORY_RETURN_PC):
                        if address not in installed_breakpoints:
                            _breakpoint(client, address)
                            installed_breakpoints.add(address)
                elif (
                    pc == FACTORY_VENEER_PC
                    and registers[14] == EXPECTED_FACTORY_LR
                ):
                    if registers[1] != tracker.factory.raw:
                        continue
                    if (
                        tracker.descriptor is not None
                        and registers[0] != tracker.descriptor
                    ):
                        continue
                    target = tracker.accept_factory(registers[0], registers[1])
                    _remove_breakpoint(client, FACTORY_VENEER_PC)
                    client.command("s")
                    after = _registers(client)
                    _breakpoint(client, FACTORY_VENEER_PC)
                    if (
                        after[15] != target.fetch_address
                        or not (after[16] & THUMB_STATE_BIT)
                    ):
                        raise RuntimeError("target factory fetch/state mismatch")
                    pending_factory = True
                    timeline.append(
                        {
                            "event": "factory",
                            "descriptor": f"0x{registers[0]:08X}",
                            "factory_raw": f"0x{target.raw:08X}",
                            "factory_fetch": f"0x{target.fetch_address:08X}",
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
                    if verified_load is None or tracker.descriptor is None:
                        raise AssertionError(
                            "live target lacks verified load/descriptor"
                        )
                    bounds = signed_halfwords(
                        _read_bytes(client, returned + 4, 8)
                    )
                    target_instance = TargetInstance(
                        load_epoch=identity.load_epoch,
                        map_entry_address=verified_load.map_entry_address,
                        map_entry_index=verified_load.map_entry_index,
                        selector=verified_load.selector,
                        selected_value=verified_load.selected_value,
                        descriptor=tracker.descriptor,
                        factory_raw=identity.factory.raw,
                        factory_fetch=identity.factory.fetch_address,
                        object_pointer=returned,
                        registry_slot=slot,
                        bounds=bounds,
                    )
                    state.arm(target_instance)
                    if native_probe:
                        request = ArmRequest(
                            sequence=identity.load_epoch,
                            target=returned,
                            load_epoch=identity.load_epoch,
                            descriptor=tracker.descriptor,
                            factory_raw=identity.factory.raw,
                            factory_fetch=identity.factory.fetch_address,
                        )
                        arm_response = client.arm_native_probe(request)
                        if arm_response != "OK":
                            raise RuntimeError(
                                f"native range probe rejected arm request: {arm_response}"
                            )
                        retired_breakpoints = sorted(
                            installed_breakpoints - lifecycle_breakpoints
                        )
                        for address in retired_breakpoints:
                            _remove_breakpoint(client, address)
                            installed_breakpoints.remove(address)
                        armed = {
                            "target": target_instance.to_dict(),
                            "instrumentation": {
                                "method": "pinned_mgba_native_one_shot_range",
                                "source_commit": "26b7884bc25a5933960f3cdcd98bac1ae14d42e2",
                                "control_sequence": request.sequence,
                                "control": "qLog1ProbeArm",
                                "event_transport": "qLog1ProbeEvent",
                                "ranges": ["X+0x04..X+0x0F", "X+0x14..X+0x17"],
                                "gdb_watchpoints": [],
                                "retired_discovery_breakpoints": [
                                    f"0x{address:08X}"
                                    for address in retired_breakpoints
                                ],
                                "active_lifecycle_breakpoints": [
                                    f"0x{address:08X}"
                                    for address in sorted(installed_breakpoints)
                                ],
                                "ui_automation": False,
                            },
                            "gdb_initial_status": initial_status,
                            "process_id": process.pid,
                        }
                        marker = (
                            run_root / "armed.json"
                            if not armed_targets
                            else run_root / f"rearmed-{len(armed_targets) + 1}.json"
                        )
                        armed_targets.append(armed)
                        _write_new_json(marker, armed)
                        timeline.append({"event": "armed", **target_instance.to_dict()})
                        pending_factory = False
                        continue
                    breakpoint_installation = install_targeted_code_breakpoints(
                        client, installed_breakpoints
                    )
                    setup_stopped: Path | None = None
                    if not setup_stop_consumed:
                        setup_stopped = (
                            run_root / f"setup-stopped-{identity.load_epoch}.txt"
                        )
                        _inject_lua(
                            injector_path=injector_path,
                            process_id=process.pid,
                            lua_path=stop_setup_lua,
                            ready_path=setup_stopped,
                        )
                        setup_stop_consumed = True
                    armed = {
                        "target": target_instance.to_dict(),
                        "instrumentation": {
                            "method": "targeted_code_breakpoints",
                            "fallback_reason": TARGETED_BREAKPOINT_REASON,
                            "rejected_method": {
                                "method": "16 byte read-watchpoints",
                                "run": "human-live-11",
                                "human_observation": "below 1 FPS",
                                "status": "unusable",
                            },
                            "rejected_code_set": {
                                "run": "human-live-12",
                                "breakpoints": [
                                    "0x080075CC",
                                    "0x08012748",
                                    "0x080127F6",
                                    "0x08012866",
                                ],
                                "180_frame_marker_completed": False,
                                "observed_seconds": 89,
                                "fps_upper_bound": 180 / 89,
                                "status": "unusable",
                            },
                            "rejected_hybrid_set": {
                                "run": "human-live-15",
                                "watchpoints": ["X+0x04"],
                                "breakpoints": ["0x080075CC"],
                                "180_frame_marker_completed": False,
                                "observed_seconds": 105,
                                "fps_upper_bound": 180 / 105,
                                "status": "unusable",
                            },
                            "static_load_census": [
                                item.to_dict() for item in EXECUTABLE_LOAD_CENSUS
                            ],
                            "coverage": (
                                "0x0801277A and 0x08012828 read X+0C only after "
                                "their routines load and accept X+04/+06/+08/+0A; "
                                "0x080128AA reads X+00 for dispatch only after its "
                                "routine loads and accepts those bounds; 0x080075CC "
                                "directly reads X+14"
                            ),
                            "selected_watchpoints": [],
                            "selected_breakpoints": breakpoint_installation,
                        },
                        "gdb_initial_status": initial_status,
                        "mgba_version": build_manifest.get("version_output"),
                        "process_id": process.pid,
                        "phase1_setup": {
                            "route": str(setup_lua),
                            "route_sha256": sha256(setup_lua),
                            "stop_script": str(stop_setup_lua),
                            "stop_script_sha256": sha256(stop_setup_lua),
                            "input_stopped": setup_stopped is not None,
                            "stop_marker": (
                                None if setup_stopped is None else str(setup_stopped)
                            ),
                        },
                    }
                    marker = (
                        run_root / "armed.json"
                        if not armed_targets
                        else run_root / f"rearmed-{len(armed_targets) + 1}.json"
                    )
                    if not armed_targets:
                        benchmark_complete = run_root / "idle-benchmark-complete.txt"
                        benchmark_ready_marker = run_root / "idle-benchmark-ready.txt"
                        _inject_lua(
                            injector_path=injector_path,
                            process_id=process.pid,
                            lua_path=benchmark_lua,
                            ready_path=benchmark_ready_marker,
                            marker_path=benchmark_complete,
                        )
                        benchmark_started = time.monotonic()
                        pending_armed = armed
                        pending_armed_marker = marker
                    else:
                        armed_targets.append(armed)
                        _write_new_json(marker, armed)
                        timeline.append(
                            {"event": "armed", **target_instance.to_dict()}
                        )
                    pending_factory = False
                elif pc == REMOVAL_PC and tracker.current is not None:
                    if (
                        registers[0] != MANAGER
                        or registers[1] != tracker.current.object_pointer
                    ):
                        continue
                    if current_watchpoints:
                        remove_read_watchpoints(client, current_watchpoints)
                        current_watchpoints = ()
                    if state.current is not None:
                        if native_probe:
                            disarm_response = client.disarm_native_probe(
                                state.current.load_epoch
                            )
                            if disarm_response != "OK":
                                raise RuntimeError(
                                    "native range probe failed to disarm stale X: "
                                    f"{disarm_response}"
                                )
                            for address in sorted(discovery_breakpoints):
                                if address not in installed_breakpoints:
                                    _breakpoint(client, address)
                                    installed_breakpoints.add(address)
                        state.retire(
                            state.current.object_pointer, state.current.load_epoch
                        )
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
                        raise RuntimeError(
                            "target removal did not reach bounded count commit"
                        )
                    client.command("s")
                    if not removal_count_commit_is_valid(
                        old_count, _read_u32(client, MANAGER)
                    ):
                        raise RuntimeError(
                            "registry removal count commit mismatch"
                        )
                    if not tracker.retire_removal(
                        manager=MANAGER, object_pointer=object_pointer
                    ):
                        raise RuntimeError(
                            "committed removal did not match current target"
                        )
                    timeline.append(
                        {
                            "event": "removal",
                            "object": f"0x{object_pointer:08X}",
                        }
                    )
            if result is None:
                raise TimeoutError("bounded human gameplay session timed out")
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
        raise RuntimeError(
            "ROM or source save artifact changed during runtime probe"
        ) from session_error
    if session_error is not None:
        failure = {
            "error": type(session_error).__name__,
            "detail": str(session_error),
            "timeline": timeline,
            "armed_targets": armed_targets,
            "source_artifacts": source_artifacts,
        }
        _write_new_json(run_root / "failed.json", failure)
        raise session_error
    if result is None:
        raise AssertionError("session ended without result or error")
    output = {
        **result,
        "timeline": timeline,
        "armed_targets": armed_targets,
        "state_events": state.events,
        "source_artifacts": source_artifacts,
    }
    _write_new_json(run_root / "result.json", output)
    write_run_bundle(
        run_root,
        tool="tools.runtime.rom011_live_watch",
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
            "armed_targets": len(armed_targets),
            "state_events": len(state.events),
        },
        artifacts={
            state_copy: "input-savestate",
            save_copy: "savegame",
            run_root / "capture-ready.json": "capture-ready",
        },
    )
    return output


def request_no_hit_stop(run_root: Path) -> Path:
    target = run_root.resolve() / "stop-request.json"
    if target.exists():
        raise FileExistsError("stop request already exists")
    target.write_text('{"bounded_sequence_complete": true}\n', encoding="utf-8")
    return target


def write_human_annotation(run_root: Path, text: str) -> Path:
    if not text.strip():
        raise ValueError("human annotation must not be empty")
    target = run_root.resolve() / "human-annotation.json"
    if target.exists():
        raise FileExistsError("human annotation already exists")
    target.write_text(
        json.dumps({"human_observation": text}, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("rom", type=Path)
    run.add_argument("state", type=Path)
    run.add_argument("save", type=Path)
    run.add_argument("--state-sha256", required=True)
    run.add_argument("--save-sha256", required=True)
    run.add_argument(
        "--mgba",
        type=Path,
        default=Path(r"C:\Program Files\mGBA\mGBA.exe"),
    )
    run.add_argument(
        "--profiles",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "config" / "roms.yaml",
    )
    run.add_argument("--run-root", type=Path, required=True)
    run.add_argument("--timeout", type=float, default=900.0)
    run.add_argument("--manifest", type=Path, required=True)
    stop = subparsers.add_parser("stop-no-hit")
    stop.add_argument("run_root", type=Path)
    annotate = subparsers.add_parser("annotate")
    annotate.add_argument("run_root", type=Path)
    annotate.add_argument("text")
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
            profile_path=args.profiles.resolve(),
            run_root=args.run_root,
            timeout_seconds=args.timeout,
            manifest_path=args.manifest.resolve(),
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "stop-no-hit":
        print(request_no_hit_stop(args.run_root))
        return 0
    if args.command == "annotate":
        print(write_human_annotation(args.run_root, args.text))
        return 0
    raise AssertionError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
