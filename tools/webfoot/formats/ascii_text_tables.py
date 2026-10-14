
from __future__ import annotations

import re

from ..binary import GBA_ROM_BASE
from .text_tables import TextCodecError, TEXT_POINTER_SIZE

TERMINATOR = 0x00

POINTER_SIZE = TEXT_POINTER_SIZE

NEWLINE = 0x0A

_ESCAPE_RE = re.compile(r"\{([0-9A-Fa-f]{2})\}")


def decode_string(data: bytes, offset: int) -> tuple[str, int]:
    text: list[str] = []
    position = offset
    while True:
        if position >= len(data):
            raise TextCodecError(f"unterminated string starting at {offset:#010x}")
        byte = data[position]
        position += 1
        if byte == TERMINATOR:
            return "".join(text), position
        if byte == NEWLINE:
            text.append("\n")
            continue
        if byte == 0x7B:
            text.append("{{")
            continue
        if 0x20 <= byte < 0x7F:
            text.append(chr(byte))
            continue
        text.append(f"{{{byte:02X}}}")


def encode_string(text: str) -> bytes:
    out = bytearray()
    position = 0
    length = len(text)
    while position < length:
        character = text[position]
        if character == "{":
            if text.startswith("{{", position):
                out.append(0x7B)
                position += 2
                continue
            match = _ESCAPE_RE.match(text, position)
            if match is None:
                raise TextCodecError(
                    f"malformed escape at index {position}: expected "
                    '"{XX}" with two hex digits, or "{{" for a literal brace'
                )
            byte = int(match.group(1), 16)
            if byte == TERMINATOR:
                raise TextCodecError(
                    f"escape at index {position} encodes the terminator and "
                    "would end the string early"
                )
            if 0x20 <= byte < 0x7F or byte == NEWLINE:
                raise TextCodecError(
                    f"escape at index {position} encodes {byte:#04x}, which has "
                    "a literal spelling and would not decode back to this escape"
                )
            out.append(byte)
            position = match.end()
            continue
        if character == "\n":
            out.append(NEWLINE)
            position += 1
            continue
        codepoint = ord(character)
        if not 0x20 <= codepoint < 0x7F:
            raise TextCodecError(
                f"character {character!r} at index {position} is not printable "
                "ASCII and has no byte in this encoding"
            )
        out.append(codepoint)
        position += 1
    out.append(TERMINATOR)
    return bytes(out)


def encoded_size(text: str) -> int:
    """Bytes ``text`` occupies once encoded, terminator included."""
    return len(encode_string(text))




def read_pointer(data: bytes, table_start: int, index: int) -> int:
    slot = table_start + index * POINTER_SIZE
    if slot + POINTER_SIZE > len(data):
        raise TextCodecError(f"pointer table entry {index} is out of bounds")
    address = int.from_bytes(data[slot : slot + POINTER_SIZE], "little")
    if not GBA_ROM_BASE <= address < GBA_ROM_BASE + len(data):
        raise TextCodecError(
            f"pointer table entry {index} holds {address:#010x}, which is not "
            "a GBA ROM address"
        )
    return address - GBA_ROM_BASE


def encode_pointer(offset: int) -> bytes:
    """Encode a file offset as the table's little-endian GBA address form."""
    if type(offset) is not int or offset < 0:
        raise TextCodecError(f"pointer target must be a file offset, got {offset!r}")
    return (offset + GBA_ROM_BASE).to_bytes(POINTER_SIZE, "little")


def pool_is_exhaustively_tiled(
    data: bytes,
    pool_start: int,
    pool_end: int,
) -> bool:
    position = pool_start
    while position < pool_end:
        try:
            _, end = decode_string(data, position)
        except TextCodecError:
            return False
        if end > pool_end:
            return False
        position = end
    return position == pool_end
