"""Reusable, read-only primitives for mGBA GDB capture sessions.

This module preserves the response framing and bounded memory-read behavior
that produced the P-004 captures.  The command allowlist intentionally omits
all memory, register, and execution-state write packets.
"""

from __future__ import annotations

import re
import socket
import struct
import time
from collections.abc import Iterator

from tools.runtime.rom006_gdb_probe import decode_register_payload, rsp_packet


EWRAM_LO = 0x02000000
EWRAM_HI = 0x02040000
ROM_LO = 0x08000000
ROM_HI = 0x08800000
READ_CHUNK_SIZE = 192
CAPTURE_MAGIC = b"WFCAP001"
_RECORD_HEADER = struct.Struct("<III")
_ALLOWED_PACKET = re.compile(
    r"(?:\?|qSupported|g|c|[Zz](?:0|2),[0-9A-Fa-f]+,[0-9A-Fa-f]+|"
    r"m[0-9A-Fa-f]+,[0-9A-Fa-f]+)\Z"
)


def _unescape_rsp(payload: bytes) -> bytes:
    result = bytearray()
    index = 0
    while index < len(payload):
        if payload[index : index + 1] == b"}" and index + 1 < len(payload):
            result.append(payload[index + 1] ^ 0x20)
            index += 2
        else:
            result.append(payload[index])
            index += 1
    return bytes(result)


class CaptureRspClient:
    """Small RSP client restricted to read-only observation and execution control."""

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buffer = bytearray()

    @staticmethod
    def command_is_allowed(payload: str) -> bool:
        return _ALLOWED_PACKET.fullmatch(payload) is not None

    def read_response(self, timeout: float | None = None) -> str:
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            while self.buffer and self.buffer[0] in (ord("+"), ord("-")):
                del self.buffer[0]

            start = self.buffer.find(b"$")
            if start > 0:
                del self.buffer[:start]
                start = 0
            marker = self.buffer.find(b"#", start + 1) if start == 0 else -1
            if marker >= 0 and len(self.buffer) >= marker + 3:
                escaped = bytes(self.buffer[1:marker])
                checksum_text = bytes(self.buffer[marker + 1 : marker + 3])
                del self.buffer[: marker + 3]
                try:
                    claimed = int(checksum_text, 16)
                except ValueError:
                    claimed = -1
                payload = _unescape_rsp(escaped)
                if sum(payload) & 0xFF != claimed:
                    self.sock.sendall(b"-")
                    continue
                self.sock.sendall(b"+")
                return payload.decode("ascii", errors="replace")

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("RSP packet wait expired")
                self.sock.settimeout(min(remaining, 5.0))
            chunk = self.sock.recv(8192)
            if not chunk:
                raise ConnectionError("mGBA GDB connection closed")
            self.buffer.extend(chunk)

    def command(self, payload: str, timeout: float = 10.0) -> str:
        if not self.command_is_allowed(payload):
            raise ValueError(f"RSP command is not allowlisted: {payload!r}")
        self.sock.sendall(rsp_packet(payload))
        return self.read_response(timeout)

    def continue_execution(self) -> None:
        if not self.command_is_allowed("c"):
            raise AssertionError("continue packet unexpectedly disallowed")
        self.sock.sendall(rsp_packet("c"))

    def registers(self) -> tuple[int, ...]:
        return decode_register_payload(self.command("g"))

    def read_memory(self, address: int, length: int) -> bytes:
        if address < 0 or length < 0:
            raise ValueError("memory address and length must be non-negative")
        output = bytearray()
        while len(output) < length:
            request_length = min(READ_CHUNK_SIZE, length - len(output))
            payload = self.command(f"m{address + len(output):x},{request_length:x}")
            if payload.startswith("E"):
                raise RuntimeError(f"mGBA memory read failed: {payload}")
            try:
                data = bytes.fromhex(payload)
            except ValueError as exc:
                raise RuntimeError("mGBA memory reply was not hexadecimal") from exc
            if not data:
                raise RuntimeError("mGBA memory reply made no progress")
            output.extend(data[:request_length])
        return bytes(output)


def connect_capture_client(
    *, host: str = "127.0.0.1", port: int = 2345, timeout: float = 30.0
) -> CaptureRspClient:
    deadline = time.monotonic() + timeout
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            sock = socket.create_connection((host, port), timeout=1.0)
            sock.settimeout(10.0)
            return CaptureRspClient(sock)
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    raise TimeoutError(f"mGBA GDB port did not open: {last_error}")


def scan_aligned_ewram_pointers(data: bytes) -> tuple[tuple[int, int], ...]:
    """Return ``(offset, value)`` pairs for aligned EWRAM-shaped words."""
    pointers = []
    for offset in range(0, len(data) - 3, 4):
        value = int.from_bytes(data[offset : offset + 4], "little")
        if EWRAM_LO <= value < EWRAM_HI and value & 3 == 0:
            pointers.append((offset, value))
    return tuple(pointers)


def write_capture_record(stream, stop: int, address: int, data: bytes) -> None:
    stream.write(_RECORD_HEADER.pack(stop, address, len(data)))
    stream.write(data)


def iter_capture_records(blob: bytes) -> Iterator[tuple[int, int, bytes]]:
    """Decode records after an optional ``CAPTURE_MAGIC`` file header."""
    offset = len(CAPTURE_MAGIC) if blob.startswith(CAPTURE_MAGIC) else 0
    while offset < len(blob):
        if len(blob) - offset < _RECORD_HEADER.size:
            raise ValueError("truncated capture record header")
        stop, address, length = _RECORD_HEADER.unpack_from(blob, offset)
        offset += _RECORD_HEADER.size
        end = offset + length
        if end > len(blob):
            raise ValueError("truncated capture record payload")
        yield stop, address, blob[offset:end]
        offset = end
