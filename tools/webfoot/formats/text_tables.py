"""Pure codec for the Buu's Fury UTF-16LE string pool and its pointer table.

Provenance
----------
The layout this module encodes is documented, with its evidence, in
`docs/research/TEXT_FORMAT.md`. It is this project's own work: the only upstream
with text tooling (`yoav74/BuusFuryToolkit`, pinned in `upstreams.lock`) records
a single address and finds strings by heuristic linguistic scanning, and knows
nothing of the pointer table that actually defines the extent. Its `.tbl`
character map is not used here and is not needed - the encoding is UTF-16LE, so
a unit decodes as a Unicode codepoint.

Evidence labels follow `docs/DEVELOPMENT.md`:

- ``CONFIRMED`` the encoding, the terminator, the control grammar, the pool and
  table extents, the exhaustive tiling, and the absence of aliasing. Each was
  established by reading the canonical ROM and each is re-asserted by a test.
- ``UNKNOWN``   what any ``0x0008`` operand *means*. The operand is preserved
  verbatim rather than named, because a guessed name in an authored file would
  later read as an extracted fact.

This module performs NO I/O. It maps bytes to text and back, so it carries no
ROM path, no profile check and no file access - `webfoot.rom` and
`webfoot.profile` own identity, `webfoot.write` owns emission, and
`webfoot.relocation` owns movement. That purity is load-bearing: it is what lets
the same codec keep working when the byte source is a decomp tree rather than a
ROM image.

Three design choices worth stating, because each has a cheaper wrong version:

1. **Identity is the table index, not the address.** A string's durable identity
   is its slot in the pointer table, because that is what the game's code
   actually uses to reach it - the reference topology shows access is by index,
   never by a direct pointer. An address is where a string happens to live right
   now and changes the moment anything moves.

2. **Every byte survives.** The decoded form is reversible for the whole pool,
   not for the strings we happen to understand. Unknown control operands become
   an escape that re-encodes to the same bytes, so `encode(decode(x)) == x` holds
   over all 82,874 pool bytes rather than over a sample.

3. **Validation is at encode time.** Assigning text does not check it; encoding
   does, and refuses rather than emitting something that would not decode back.
   That is the last point at which refusing is still free.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterator

# --- verified extents ----------------------------------------------------

#: CONFIRMED. File offset of the first string in the contiguous pool.
TEXT_POOL_START = 0x0005792C

#: CONFIRMED. File offset one past the pool's last byte (its final terminator).
TEXT_POOL_END = 0x0006BCE6

#: CONFIRMED. File offset of the pointer table's first entry.
TEXT_TABLE_START = 0x0006BCE8

#: CONFIRMED. Entries in the pointer table.
TEXT_ENTRY_COUNT = 1534

#: CONFIRMED. Bytes per pointer table entry: one little-endian GBA address.
TEXT_POINTER_SIZE = 4

#: GBA cartridge base. A file offset plus this is the address the game sees.
GBA_ROM_BASE = 0x08000000

#: CONFIRMED. The 16-bit unit that ends a string.
TERMINATOR = 0x0000

#: CONFIRMED. Prefix unit; always followed by exactly one operand unit.
CONTROL_PREFIX = 0x0008

#: CONFIRMED. Standalone unit meaning newline.
CONTROL_NEWLINE = 0x000A


class TextCodecError(ValueError):
    """Raised when bytes are not decodable text, or text is not encodable."""


# --- the reversible text representation ----------------------------------
#
# A decoded string is an ordinary Python `str`. Two things in the byte stream
# are not ordinary characters, and each gets a reversible spelling:
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
    """Decode the string starting at ``offset``.

    Returns the text and the file offset just past its terminator, so a caller
    can walk the pool without re-deriving lengths.
    """
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
    """Encode text back to its UTF-16LE byte form, terminator included.

    Refuses anything it could not have produced, so a project cannot author a
    string that decodes to something other than what was written.
    """
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


# --- the pointer table ---------------------------------------------------


@dataclass(frozen=True, slots=True)
class TextIdentity:
    """A string's durable identity: its slot in the pointer table.

    The index is identity because the game reaches a string *through* the table
    - the pool base has exactly one inbound reference in the whole image, and it
    is the table itself. An address, by contrast, is only where the bytes sit
    right now.

    Identity is shared across games: an index is an index whatever the encoding,
    which is why the project format and the write planner need no per-game
    variant. Only non-negativity is checked here. The upper bound belongs to the
    profile that declares the table's count, and `webfoot.text` enforces it at
    load time against that count - a bound baked in here would be one game's
    1,534 and would reject a second game's table for no reason.
    """

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
    """One enumerated string.

    ``offset`` and ``size`` are provenance describing where this string lives in
    the image right now; they are not part of the data model, and a project
    stores neither.
    """

    identity: TextIdentity
    text: str
    offset: int
    size: int

    @property
    def gba_address(self) -> int:
        return self.offset + GBA_ROM_BASE

    @property
    def pointer_offset(self) -> int:
        """File offset of this entry's slot in the pointer table."""
        return TEXT_TABLE_START + self.identity.index * TEXT_POINTER_SIZE


def read_pointer(data: bytes, index: int) -> int:
    """File offset the table's ``index`` entry points at."""
    slot = TEXT_TABLE_START + index * TEXT_POINTER_SIZE
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


def iter_text_entries(data: bytes) -> Iterator[TextEntry]:
    """Yield every string the pointer table enumerates, in table order.

    Table order is also address order in the canonical image, but the two are
    kept conceptually separate: order is a fact about the current layout, and
    identity is the index.
    """
    for index in range(TEXT_ENTRY_COUNT):
        offset = read_pointer(data, index)
        text, end = decode_string(data, offset)
        yield TextEntry(
            identity=TextIdentity(index),
            text=text,
            offset=offset,
            size=end - offset,
        )


def pool_is_exhaustively_tiled(data: bytes) -> bool:
    """True when the table's strings tile the pool with no gap or overlap.

    This is the structural invariant that makes a *complete* round trip provable
    rather than sampled: if every string ends exactly where the next begins, and
    the first starts at the pool base while the last ends at the pool end, then
    the enumeration accounts for every byte in the extent.
    """
    expected = TEXT_POOL_START
    for entry in iter_text_entries(data):
        if entry.offset != expected:
            return False
        expected = entry.offset + entry.size
    return expected == TEXT_POOL_END
