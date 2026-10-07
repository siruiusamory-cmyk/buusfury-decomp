"""Read-only mGBA GDB probe for ROM-006 runtime evidence.

The client deliberately allowlists only capability/status, register-read,
hardware-breakpoint, continue, and single-step packets. It never sends a ROM,
RAM, or register write packet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import time
from typing import Sequence
import uuid

from tools.runtime.evidence_bundle import write_run_bundle
from tools.runtime.mgba_identity import (
    DEFAULT_PACKAGED_MGBA,
    PACKAGED_0_10_5,
    require_mgba_build,
)
from tools.webfoot.analysis.variation_arrays import (
    VariationArrayFirstWordObservation,
    census_variation_array_first_words,
)
from tools.webfoot.profile import RomProfileCatalog


EXPECTED_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
EXPECTED_SIZE = 8_388_608
MAP_ENTRY_BASE = 0x0808E2E0
MAP_ENTRY_SIZE = 0x38
MAP_ENTRY_COUNT = 452
RESOLVER_ENTRY_PC = 0x080089CC
RESOLVER_LOAD_PC = 0x080089D4
REGISTRY_ADAPTER_PC = 0x08009670
REGISTER_COUNT = 17
THUMB_STATE_BIT = 0x20


def rsp_packet(payload: str) -> bytes:
    encoded = payload.encode("ascii")
    checksum = sum(encoded) & 0xFF
    return b"$" + encoded + b"#" + f"{checksum:02x}".encode("ascii")


def decode_register_payload(payload: str) -> tuple[int, ...]:
    expected_length = REGISTER_COUNT * 8
    if len(payload) != expected_length:
        raise ValueError(
            f"register payload must contain {expected_length} hex characters"
        )
    try:
        raw = bytes.fromhex(payload)
    except ValueError as exc:
        raise ValueError("register payload is not hexadecimal") from exc
    return tuple(
        int.from_bytes(raw[offset : offset + 4], "little")
        for offset in range(0, len(raw), 4)
    )


def effective_variation_source(r0_at_load: int) -> int:
    if not 0 <= r0_at_load <= 0xFFFFFFFF:
        raise ValueError("r0 must be an unsigned 32-bit value")
    return (r0_at_load + 0x3C) & 0xFFFFFFFF


def selector_from_scaled_r1(scaled_r1: int) -> int:
    if not 0 <= scaled_r1 <= 0xFFFFFFFF:
        raise ValueError("r1 must be an unsigned 32-bit value")
    if scaled_r1 & 3:
        raise ValueError("scaled selector must be divisible by four")
    return scaled_r1 >> 2


def map_entry_address(index: int) -> int:
    if (
        isinstance(index, bool)
        or not isinstance(index, int)
        or not 0 <= index < MAP_ENTRY_COUNT
    ):
        raise ValueError(f"MapEntry index must be in [0, {MAP_ENTRY_COUNT})")
    return MAP_ENTRY_BASE + index * MAP_ENTRY_SIZE


def level3_capture_is_valid(
    *,
    entry_registers: Sequence[int] | None,
    load_registers: Sequence[int],
    after_registers: Sequence[int],
    expected_entry_address: int,
    expected_source: int,
    expected_first_word: int,
) -> bool:
    if entry_registers is None:
        return False
    return (
        len(entry_registers) == REGISTER_COUNT
        and len(load_registers) == REGISTER_COUNT
        and len(after_registers) == REGISTER_COUNT
        and entry_registers[15] == RESOLVER_ENTRY_PC
        and entry_registers[0] == expected_entry_address
        and entry_registers[1] == 1
        and bool(entry_registers[16] & THUMB_STATE_BIT)
        and load_registers[15] == RESOLVER_LOAD_PC
        and load_registers[1] == 4
        and effective_variation_source(load_registers[0]) == expected_source
        and bool(load_registers[16] & THUMB_STATE_BIT)
        and after_registers[15] == RESOLVER_LOAD_PC + 2
        and after_registers[0] == expected_first_word
        and bool(after_registers[16] & THUMB_STATE_BIT)
    )


class RspClient:
    """Minimal response parser and command allowlist for mGBA's GDB stub."""

    _ALLOWED_EXACT = frozenset({"?", "qSupported", "g", "s", "c"})
    _ALLOWED_PREFIXES = ("Z0,", "z0,")

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buffer = bytearray()

    @classmethod
    def command_is_allowed(cls, payload: str) -> bool:
        return payload in cls._ALLOWED_EXACT or payload.startswith(
            cls._ALLOWED_PREFIXES
        )

    def _read_response(self, timeout: float) -> str:
        self.sock.settimeout(timeout)
        while True:
            while self.buffer and self.buffer[0] in (ord("+"), ord("-")):
                del self.buffer[0]
            start = self.buffer.find(b"$")
            if start >= 0:
                marker = self.buffer.find(b"#", start + 1)
                if marker >= 0 and len(self.buffer) >= marker + 3:
                    payload = bytes(self.buffer[start + 1 : marker])
                    checksum = int(bytes(self.buffer[marker + 1 : marker + 3]), 16)
                    del self.buffer[: marker + 3]
                    if sum(payload) & 0xFF != checksum:
                        self.sock.sendall(b"-")
                        continue
                    self.sock.sendall(b"+")
                    return payload.decode("ascii")
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("mGBA GDB connection closed")
            self.buffer.extend(chunk)

    def command(self, payload: str, timeout: float = 5.0) -> str:
        if not self.command_is_allowed(payload):
            raise ValueError(f"RSP command is not allowlisted: {payload!r}")
        self.sock.sendall(rsp_packet(payload))
        return self._read_response(timeout)


def _registers(client: RspClient) -> tuple[int, ...]:
    return decode_register_payload(client.command("g"))


def _register_dict(registers: Sequence[int]) -> dict[str, str]:
    return {
        **{f"r{index}": f"0x{registers[index]:08X}" for index in range(16)},
        "cpsr": f"0x{registers[16]:08X}",
    }


def _connect(deadline: float) -> socket.socket:
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            return socket.create_connection(("127.0.0.1", 2345), timeout=1.0)
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    raise TimeoutError(f"mGBA GDB port did not open: {last_error}")


def _predicted(
    observation: VariationArrayFirstWordObservation,
) -> dict[str, int | str]:
    return {
        "map_entry_index": observation.map_entry_index,
        "map_entry_address": f"0x{map_entry_address(observation.map_entry_index):08X}",
        "variation_source": f"0x{observation.source_pointer_raw:08X}",
        "first_word_raw": f"0x{observation.first_word_raw:08X}",
    }


def run_probe(
    *,
    rom_path: Path,
    state_path: Path,
    mgba_path: Path,
    profile_path: Path,
    timeout_seconds: float,
    max_stops: int,
    trace_registry: bool,
) -> dict[str, object]:
    mgba_path = require_mgba_build(mgba_path, PACKAGED_0_10_5)
    before = rom_path.stat()
    before_hash = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    if before.st_size != EXPECTED_SIZE or before_hash != EXPECTED_SHA256:
        raise RuntimeError("verified ROM identity mismatch before runtime probe")
    if not state_path.is_file():
        raise RuntimeError(f"bootstrap state missing: {state_path}")

    census = census_variation_array_first_words(
        rom_path, RomProfileCatalog.load(profile_path)
    )
    by_source = {
        item.source_pointer_raw: item for item in census.observations
    }

    port_probe = socket.socket()
    try:
        if port_probe.connect_ex(("127.0.0.1", 2345)) == 0:
            raise RuntimeError("TCP port 2345 already in use")
    finally:
        port_probe.close()

    breakpoints = [RESOLVER_ENTRY_PC, RESOLVER_LOAD_PC]
    if trace_registry:
        breakpoints.append(REGISTRY_ADAPTER_PC)
    probe_root = state_path.parent / f"probe-{uuid.uuid4().hex}"
    save_root = probe_root / "save"
    save_root.mkdir(parents=True)
    process = subprocess.Popen(
        [
            str(mgba_path),
            "--gdb",
            "--savestate",
            str(state_path),
            "-C",
            f"savegamePath={save_root}",
            "-C",
            "mute=1",
            str(rom_path),
        ]
    )
    started = time.monotonic()
    events: list[dict[str, object]] = []
    latest_entry: dict[str, object] | None = None
    latest_entry_registers: tuple[int, ...] | None = None
    selected_capture: dict[str, object] | None = None
    registry_capture: dict[str, object] | None = None
    try:
        with _connect(started + 15) as sock:
            client = RspClient(sock)
            events.append(
                {
                    "setup": {
                        "supported": client.command("qSupported"),
                        "initial_stop": client.command("?"),
                        "breakpoints": {
                            f"0x{pc:08X}": client.command(f"Z0,{pc:x},2")
                            for pc in breakpoints
                        },
                    }
                }
            )

            for stop_number in range(1, max_stops + 1):
                remaining = timeout_seconds - (time.monotonic() - started)
                if remaining <= 0:
                    break
                try:
                    reason = client.command("c", timeout=min(10.0, remaining))
                except socket.timeout:
                    continue
                registers = _registers(client)
                pc = registers[15]
                event: dict[str, object] = {
                    "stop": stop_number,
                    "reason": reason,
                    "pc": f"0x{pc:08X}",
                    "registers": _register_dict(registers),
                    "thumb": bool(registers[16] & THUMB_STATE_BIT),
                }

                if pc == RESOLVER_ENTRY_PC:
                    latest_entry_registers = registers
                    latest_entry = {
                        "map_entry_address": f"0x{registers[0]:08X}",
                        "selector": registers[1],
                        "lr": f"0x{registers[14]:08X}",
                    }
                    event["resolver_entry"] = latest_entry
                elif pc == RESOLVER_LOAD_PC:
                    source = effective_variation_source(registers[0])
                    observation = by_source.get(source)
                    event["scaled_selector_r1"] = registers[1]
                    event["selector"] = selector_from_scaled_r1(registers[1])
                    event["effective_source"] = f"0x{source:08X}"
                    event["latest_resolver_entry"] = latest_entry
                    if observation:
                        event["predicted"] = _predicted(observation)
                    step_reason = client.command("s", timeout=5.0)
                    after = _registers(client)
                    event["after_load"] = {
                        "reason": step_reason,
                        "registers": _register_dict(after),
                        "observed_r0": f"0x{after[0]:08X}",
                    }
                    if registers[1] == 4 and observation:
                        event["observed_equals_expected"] = (
                            after[0] == observation.first_word_raw
                        )
                        event["level3_valid"] = level3_capture_is_valid(
                            entry_registers=latest_entry_registers,
                            load_registers=registers,
                            after_registers=after,
                            expected_entry_address=map_entry_address(
                                observation.map_entry_index
                            ),
                            expected_source=observation.source_pointer_raw,
                            expected_first_word=observation.first_word_raw,
                        )
                        if event["level3_valid"]:
                            selected_capture = event
                elif pc == REGISTRY_ADAPTER_PC:
                    steps: list[dict[str, object]] = []
                    for _ in range(4):
                        reason_after_step = client.command("s", timeout=5.0)
                        after = _registers(client)
                        steps.append(
                            {
                                "reason": reason_after_step,
                                "pc": f"0x{after[15]:08X}",
                                "registers": _register_dict(after),
                            }
                        )
                    event["adapter_steps"] = steps
                    registry_capture = event
                events.append(event)
                if selected_capture and (registry_capture or not trace_registry):
                    break
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    after = rom_path.stat()
    after_hash = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    unchanged = (
        before_hash == after_hash
        and before.st_size == after.st_size
        and before.st_mtime_ns == after.st_mtime_ns
    )
    write_run_bundle(
        probe_root,
        tool="tools.runtime.rom006_gdb_probe",
        arguments={
            "timeout_seconds": timeout_seconds,
            "max_stops": max_stops,
            "trace_registry": trace_registry,
        },
        rom=rom_path,
        emulator=mgba_path,
        observations={
            "level3_valid": bool(
                isinstance(selected_capture, dict)
                and selected_capture.get("level3_valid") is True
            ),
            "registry_capture": registry_capture is not None,
            "rom_unchanged": unchanged,
        },
        artifacts={
            state_path: "input-savestate",
            save_root / rom_path.with_suffix(".sav").name: "savegame",
        },
    )
    return {
        "rom": str(rom_path),
        "state": str(state_path),
        "state_sha256": hashlib.sha256(state_path.read_bytes()).hexdigest(),
        "sha256_before": before_hash,
        "sha256_after": after_hash,
        "size_before": before.st_size,
        "size_after": after.st_size,
        "mtime_ns_before": before.st_mtime_ns,
        "mtime_ns_after": after.st_mtime_ns,
        "rom_unchanged": unchanged,
        "selected_capture": selected_capture,
        "registry_capture": registry_capture,
        "events": events,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("state", type=Path)
    parser.add_argument(
        "--mgba",
        type=Path,
        default=DEFAULT_PACKAGED_MGBA,
    )
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "config" / "roms.yaml",
    )
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--max-stops", type=int, default=32)
    parser.add_argument("--trace-registry", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    if args.max_stops <= 0:
        raise SystemExit("--max-stops must be positive")
    result = run_probe(
        rom_path=args.rom.resolve(),
        state_path=args.state.resolve(),
        mgba_path=args.mgba.resolve(),
        profile_path=args.profiles.resolve(),
        timeout_seconds=args.timeout,
        max_stops=args.max_stops,
        trace_registry=args.trace_registry,
    )
    print(json.dumps(result, indent=2))
    capture = result["selected_capture"]
    valid = (
        result["rom_unchanged"]
        and isinstance(capture, dict)
        and capture.get("level3_valid") is True
    )
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
