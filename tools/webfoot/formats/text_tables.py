
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterator

from ..binary import GBA_ROM_BASE as _GBA_ROM_BASE


TEXT_POINTER_SIZE = 4

GBA_ROM_BASE = _GBA_ROM_BASE

TERMINATOR = 0x0000

CONTROL_PREFIX = 0x0008

CONTROL_NEWLINE = 0x000A


class TextCodecError(ValueError):
    """Raised when bytes are not decodable text, or text is not encodable."""


#
#     0x0008 <operand>   ->  "{08:XX}"    operand as two uppercase hex digits
#     0x000A             ->  "\n"         a real newline, because it is one
#
# A literal "{" in the text is escaped as "{{", so the escape syntax cannot be
# forged by ROM content. That matters: without it, a string that legitimately
# contained "{08:02}" would decode to something that re-encodes as a control
# code, and the round trip would silently corrupt it. The pool contains no "{"
# today, but the codec must be correct for text a modder authors, not only for
# text that already exists.

_CONTROL_RE = re.compile(r"\{08:([0-9A-Fa-f]{2})\}")


def decode_string(data: bytes, offset: int) -> tuple[str, int]:
    text: list[str] = []
    position = offset
    while True:
        if position + 2 > len(data):
            raise TextCodecError(
                f"unterminated string starting at {offset:#010x}"
            )
        unit = int.from_bytes(data[position : position + 2], "little")
        position += 2
        if unit == TERMINATOR:
            return "".join(text), position
        if unit == CONTROL_PREFIX:
            if position + 2 > len(data):
                raise TextCodecError(
                    f"control prefix at {position - 2:#010x} has no operand"
                )
            operand = int.from_bytes(data[position : position + 2], "little")
            position += 2
            if operand > 0xFF:
                raise TextCodecError(
                    f"control operand {operand:#06x} at {position - 2:#010x} "
                    "exceeds one byte and has no reversible spelling"
                )
            text.append(f"{{08:{operand:02X}}}")
            continue
        if unit == CONTROL_NEWLINE:
            text.append("\n")
            continue
        character = chr(unit)
        # "{" is the escape introducer, so ROM content carrying one must be
        # doubled or the round trip would reinterpret it as an escape.
        text.append("{{" if character == "{" else character)


def encode_string(text: str) -> bytes:
    out = bytearray()
    position = 0
    length = len(text)
    while position < length:
        character = text[position]
        if character == "{":
            if text.startswith("{{", position):
                out += b"\x7b\x00"
                position += 2
                continue
            match = _CONTROL_RE.match(text, position)
            if match is None:
                raise TextCodecError(
                    f"malformed control token at index {position}: expected "
                    '"{08:XX}" with two hex digits, or "{{" for a literal brace'
                )
            out += CONTROL_PREFIX.to_bytes(2, "little")
            out += int(match.group(1), 16).to_bytes(2, "little")
            position = match.end()
            continue
        if character == "\n":
            out += CONTROL_NEWLINE.to_bytes(2, "little")
            position += 1
            continue
        codepoint = ord(character)
        if codepoint > 0xFFFF:
            raise TextCodecError(
                f"character {character!r} at index {position} is outside the "
                "basic multilingual plane and has no UTF-16LE unit"
            )
        if codepoint == TERMINATOR:
            raise TextCodecError(
                f"embedded NUL at index {position} would terminate the string"
            )
        if codepoint == CONTROL_PREFIX or codepoint == CONTROL_NEWLINE:
            # Unreachable for 0x0A (handled above); 0x08 as a literal character
            # would re-decode as a control prefix, so it is refused rather than
            # written out and silently reinterpreted.
            raise TextCodecError(
                f"control unit {codepoint:#06x} at index {position} cannot be "
                "written as a literal character"
            )
        out += codepoint.to_bytes(2, "little")
        position += 1
    out += TERMINATOR.to_bytes(2, "little")
    return bytes(out)


def encoded_size(text: str) -> int:
    """Bytes ``text`` occupies once encoded, terminator included."""
    return len(encode_string(text))




@dataclass(frozen=True, slots=True)
class TextIdentity:

    index: int

    def __post_init__(self) -> None:
        if type(self.index) is not int or self.index < 0:
            raise TextCodecError(
                f"text index must be a non-negative integer, got {self.index!r}"
            )

    @property
    def key(self) -> str:
        """Stable, sortable, human-typable. Fixed width so string sort == index sort."""
        return f"text:{self.index:04d}"

    def __str__(self) -> str:
        return self.key


@dataclass(frozen=True, slots=True)
class TextEntry:

    identity: TextIdentity
    text: str
    offset: int
    size: int

    @property
    def gba_address(self) -> int:
        return self.offset + GBA_ROM_BASE


def read_pointer(data: bytes, index: int, table_start: int) -> int:
    slot = table_start + index * TEXT_POINTER_SIZE
    if slot + TEXT_POINTER_SIZE > len(data):
        raise TextCodecError(f"pointer table entry {index} is out of bounds")
    address = int.from_bytes(data[slot : slot + TEXT_POINTER_SIZE], "little")
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
    return (offset + GBA_ROM_BASE).to_bytes(TEXT_POINTER_SIZE, "little")


def iter_text_entries(
    data: bytes, *, table_start: int, count: int
) -> Iterator[TextEntry]:
    for index in range(count):
        offset = read_pointer(data, index, table_start)
        text, end = decode_string(data, offset)
        yield TextEntry(
            identity=TextIdentity(index),
            text=text,
            offset=offset,
            size=end - offset,
        )


def pool_is_exhaustively_tiled(
    data: bytes, *, table_start: int, count: int, pool_start: int, pool_end: int
) -> bool:
    expected = pool_start
    for entry in iter_text_entries(data, table_start=table_start, count=count):
        if entry.offset != expected:
            return False
        expected = entry.offset + entry.size
    return expected == pool_end
