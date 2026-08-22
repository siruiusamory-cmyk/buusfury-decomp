"""Fail-closed protocol and launch helpers for the ROM-011 native probe."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_COMMIT = "26b7884bc25a5933960f3cdcd98bac1ae14d42e2"
PROFILE_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
SCHEMA = "log1-mgba-read-probe-v1"
BUILD_SCHEMA = "log1-mgba-instrumented-build-v1"
FACTORY_RAW = 0x08007675
FACTORY_FETCH = 0x08007674
EWRAM_START = 0x02000000
EWRAM_END = 0x02040000
WATCH_RANGES = ((0x04, 0x10), (0x14, 0x18))
PATCH_PATH = Path(__file__).with_name("mgba-0.10.5-log1-read-probe.patch")


def _parse_hex(value: object, name: str) -> int:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{name} must be a 0x-prefixed hexadecimal string")
    try:
        parsed = int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} is not hexadecimal") from exc
    if not 0 <= parsed <= 0xFFFFFFFF:
        raise ValueError(f"{name} is outside uint32")
    return parsed


def _require_int(value: object, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def watched_ranges(target: int) -> tuple[tuple[int, int], ...]:
    if target < EWRAM_START or target > EWRAM_END - 0x18:
        raise ValueError("target X must leave both watched ranges inside EWRAM")
    return tuple((target + start, target + end) for start, end in WATCH_RANGES)


def overlap_for_read(target: int, address: int, width: int) -> tuple[int, int] | None:
    _require_int(address, "read address")
    _require_int(width, "read width", minimum=1)
    if width not in (1, 2, 4):
        raise ValueError("read width must be 1, 2, or 4 bytes")
    physical_address = address & ~(width - 1)
    end = physical_address + width
    for start, stop in watched_ranges(target):
        overlap_start = max(physical_address, start)
        overlap_end = min(end, stop)
        if overlap_start < overlap_end:
            return overlap_start, overlap_end
    return None


@dataclass(frozen=True, slots=True)
class ArmRequest:
    sequence: int
    target: int
    load_epoch: int
    descriptor: int
    factory_raw: int = FACTORY_RAW
    factory_fetch: int = FACTORY_FETCH
    profile_sha256: str = PROFILE_SHA256

    def __post_init__(self) -> None:
        _require_int(self.sequence, "sequence", minimum=1)
        watched_ranges(self.target)
        _require_int(self.load_epoch, "load epoch", minimum=1)
        _require_int(self.descriptor, "descriptor")
        if self.factory_raw != FACTORY_RAW or self.factory_fetch != FACTORY_FETCH:
            raise ValueError("factory identity does not match ROM-011 target")
        if self.profile_sha256 != PROFILE_SHA256:
            raise ValueError("ROM profile SHA-256 does not match trusted profile")

@dataclass(frozen=True, slots=True)
class ReadEvent:
    event_id: int
    control_sequence: int
    target: int
    load_epoch: int
    descriptor: int
    factory_raw: int
    factory_fetch: int
    address: int
    relative_offset: int
    access_width: int
    overlap_start: int
    overlap_end: int
    instruction_pc: int
    lr: int
    raw_r15: int
    cpsr: int
    registers: tuple[int, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ReadEvent":
        if data.get("schema") != SCHEMA:
            raise ValueError("native probe event schema mismatch")
        if data.get("profile_sha256") != PROFILE_SHA256:
            raise ValueError("native probe event ROM profile mismatch")
        registers_value = data.get("registers")
        if not isinstance(registers_value, list) or len(registers_value) != 16:
            raise ValueError("native probe event must contain r0-r15")
        registers = tuple(
            _parse_hex(value, f"register r{index}")
            for index, value in enumerate(registers_value)
        )
        event = cls(
            event_id=_require_int(data.get("event_id"), "event id", minimum=1),
            control_sequence=_require_int(
                data.get("control_sequence"), "control sequence", minimum=1
            ),
            target=_parse_hex(data.get("target"), "target"),
            load_epoch=_require_int(data.get("load_epoch"), "load epoch", minimum=1),
            descriptor=_parse_hex(data.get("descriptor"), "descriptor"),
            factory_raw=_parse_hex(data.get("factory_raw"), "factory raw"),
            factory_fetch=_parse_hex(data.get("factory_fetch"), "factory fetch"),
            address=_parse_hex(data.get("read_address"), "read address"),
            relative_offset=_require_int(
                data.get("relative_offset"), "relative offset"
            ),
            access_width=_require_int(
                data.get("access_width"), "access width", minimum=1
            ),
            overlap_start=_parse_hex(data.get("overlap_start"), "overlap start"),
            overlap_end=_parse_hex(
                data.get("overlap_end_exclusive"), "overlap end"
            ),
            instruction_pc=_parse_hex(data.get("instruction_pc"), "instruction PC"),
            lr=_parse_hex(data.get("lr"), "LR"),
            raw_r15=_parse_hex(data.get("raw_r15"), "raw r15"),
            cpsr=_parse_hex(data.get("cpsr"), "CPSR"),
            registers=registers,
        )
        event.validate()
        return event

    @classmethod
    def from_rsp(cls, payload: str) -> "ReadEvent":
        fields = payload.split(",")
        if len(fields) != 31 or fields[0] != "LOG1E1":
            raise ValueError("native probe RSP event shape mismatch")
        try:
            values = [int(field, 16) for field in fields[1:]]
        except ValueError as exc:
            raise ValueError("native probe RSP event contains non-hex data") from exc
        relative = values[8]
        if relative & 0x80000000:
            relative -= 0x100000000
        registers = tuple(values[14:30])
        event = cls(
            event_id=values[0],
            control_sequence=values[1],
            target=values[2],
            load_epoch=values[3],
            descriptor=values[4],
            factory_raw=values[5],
            factory_fetch=values[6],
            address=values[7],
            relative_offset=relative,
            access_width=values[9],
            overlap_start=values[10],
            overlap_end=values[11],
            instruction_pc=values[12],
            lr=registers[14],
            raw_r15=registers[15],
            cpsr=values[13],
            registers=registers,
        )
        event.validate()
        return event

    def validate(self) -> None:
        if self.factory_raw != FACTORY_RAW or self.factory_fetch != FACTORY_FETCH:
            raise ValueError("native probe event factory identity mismatch")
        watched_ranges(self.target)
        if self.relative_offset != self.address - self.target:
            raise ValueError("native probe event relative offset mismatch")
        overlap = overlap_for_read(self.target, self.address, self.access_width)
        if overlap != (self.overlap_start, self.overlap_end):
            raise ValueError("native probe event overlap mismatch")
        if self.registers[14] != self.lr or self.registers[15] != self.raw_r15:
            raise ValueError("native probe event register aliases mismatch")

    def to_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "control_sequence": self.control_sequence,
            "object": f"0x{self.target:08X}",
            "load_epoch": self.load_epoch,
            "descriptor": f"0x{self.descriptor:08X}",
            "factory_raw": f"0x{self.factory_raw:08X}",
            "factory_fetch": f"0x{self.factory_fetch:08X}",
            "read_address": f"0x{self.address:08X}",
            "relative_offset": self.relative_offset,
            "access_width": self.access_width,
            "overlap_start": f"0x{self.overlap_start:08X}",
            "overlap_end_exclusive": f"0x{self.overlap_end:08X}",
            "pc": f"0x{self.instruction_pc:08X}",
            "lr": f"0x{self.lr:08X}",
            "raw_r15": f"0x{self.raw_r15:08X}",
            "cpsr": f"0x{self.cpsr:08X}",
            "thumb": bool(self.cpsr & 0x20),
            "registers": {
                **{f"r{index}": f"0x{value:08X}" for index, value in enumerate(self.registers[:13])},
                "sp": f"0x{self.registers[13]:08X}",
                "lr": f"0x{self.registers[14]:08X}",
                "pc_raw": f"0x{self.registers[15]:08X}",
            },
        }


def parse_event(path: Path) -> ReadEvent:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("native probe event must be a JSON object")
    return ReadEvent.from_mapping(data)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def instrumented_environment(manifest: dict[str, Any]) -> dict[str, str]:
    runtime_value = manifest.get("runtime_bin")
    if not isinstance(runtime_value, str):
        raise ValueError("instrumented mGBA runtime path is missing")
    runtime_bin = Path(runtime_value)
    if not runtime_bin.is_absolute() or not runtime_bin.is_dir():
        raise ValueError("instrumented mGBA runtime path is invalid")
    for library in ("SDL2.dll", "libepoxy-0.dll"):
        if not (runtime_bin / library).is_file():
            raise ValueError(f"instrumented mGBA runtime is missing {library}")
    environment = os.environ.copy()
    environment["PATH"] = str(runtime_bin) + os.pathsep + environment.get("PATH", "")
    return environment


def verify_instrumented_mgba(executable: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("instrumented mGBA manifest must be an object")
    if manifest.get("schema") != BUILD_SCHEMA:
        raise ValueError("instrumented mGBA manifest schema mismatch")
    if manifest.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("instrumented mGBA source commit mismatch")
    expected_patch_hash = manifest.get("patch_sha256")
    if (
        not isinstance(expected_patch_hash, str)
        or sha256(PATCH_PATH) != expected_patch_hash
    ):
        raise ValueError("instrumented mGBA patch hash mismatch")
    expected_hash = manifest.get("executable_sha256")
    if not isinstance(expected_hash, str) or sha256(executable) != expected_hash:
        raise ValueError("instrumented mGBA executable hash mismatch")
    version = subprocess.run(
        [str(executable), "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
        env=instrumented_environment(manifest),
    ).stdout
    if "0.10.5" not in version or SOURCE_COMMIT[:8] not in version:
        raise ValueError("instrumented executable is not pinned mGBA 0.10.5")
    return manifest


def launcher_command(
    executable: Path,
    rom: Path,
    state: Path,
    *,
    gdb: bool = True,
) -> list[str]:
    command = [str(executable.resolve())]
    if gdb:
        command.append("--gdb")
    command.extend(["--savestate", str(state.resolve()), str(rom.resolve())])
    return command
