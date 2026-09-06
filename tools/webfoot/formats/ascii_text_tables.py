"""Pure codec for an ASCII, NUL-terminated string pool and its pointer table.

Provenance
----------
The layout this module encodes is documented, with its evidence, in
`docs/research/LOGII_TEXT_FORMAT.md`. It was established by reading the
canonical Legacy of Goku II image directly. The pinned Arefu upstream reaches
the same table through its `MapNameTableOffset` config field but ships no offset
for it and no codec; nothing here is copied from it.

Evidence labels follow `docs/DEVELOPMENT.md`:

- ``CONFIRMED`` the encoding, the terminator, the table and pool extents, the
  exhaustive tiling, and the presence of shared targets. Each was established by
  reading the canonical ROM and each is re-asserted by a test.
- ``UNKNOWN``   what any ``%``-introduced token is substituted with at runtime.
  The bytes are preserved verbatim and never interpreted, so a format specifier
  survives a round trip without this module claiming to know its argument.

Why this is a separate codec from `text_tables`
-----------------------------------------------
Buu's Fury text is UTF-16LE with a 16-bit control grammar; this is 8-bit ASCII
with none. Sharing one codec would mean a unit width parameter threaded through
every function plus a control grammar that is present for one game and absent
for the other - more branching than the two modules cost, and the branches would
sit in the hot path of both games rather than being decided once at load. The
*shared* parts are real and are shared: identity, project format, extraction,
the write planner, and the build path are all common, which is what TOOLKIT-005
set out to prove. The byte-level reader is where the games genuinely differ.

Two properties of this table that the UTF-16LE one does not have, and which any
caller must respect:

1. **Pointers alias, and are not strictly ascending.** 260 slots resolve to 246
   distinct targets: 9 strings are shared by 14 extra slots - "Golden Cap." and
   "Scouter Part" among them. Buu's pool has no aliasing and its codec may
   assume ascending order; this one may not. Enumeration is therefore by walking
   the *pool*, with each string's slot looked up afterwards, so coverage of the
   extent is proved directly rather than inferred from table order.

2. **Editing a shared string changes every slot that reads it.** That is a
   property of the data, not a defect, but it means an edit applies to a target
   rather than to an index.

This module performs NO I/O. It maps bytes to text and back, so it carries no
ROM path, no profile check and no file access - `webfoot.rom` and
`webfoot.profile` own identity, `webfoot.write` owns emission. That purity is
what lets the same codec keep working when the byte source is a decomp tree.
"""

from __future__ import annotations

import re

from .text_tables import TextCodecError

#: GBA cartridge base. A file offset plus this is the address the game sees.
GBA_ROM_BASE = 0x08000000

#: CONFIRMED. The byte that ends a string.
TERMINATOR = 0x00

#: CONFIRMED. Bytes per pointer table entry: one little-endian GBA address.
POINTER_SIZE = 4

#: CONFIRMED. The only non-printable byte the pool contains, and it is a real
#: newline inside a label rather than a control code with an operand.
NEWLINE = 0x0A

#: The escape spelling for a byte with no printable ASCII character. Present so
#: the representation stays reversible for bytes a future revision might carry;
#: the canonical pool needs it for none of its 5,184 bytes.
_ESCAPE_RE = re.compile(r"\{([0-9A-Fa-f]{2})\}")


def decode_string(data: bytes, offset: int) -> tuple[str, int]:
    """Decode the string starting at ``offset``.

    Returns the text and the file offset just past its terminator, so a caller
    can walk the pool without re-deriving lengths.

    A literal "{" is doubled, exactly as in the UTF-16LE codec and for the same
    reason: without it a string that legitimately contained "{0A}" would decode
    to something that re-encodes as a different byte.
    """
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
        if byte == 0x7B:  # "{"
            text.append("{{")
            continue
        if 0x20 <= byte < 0x7F:
            text.append(chr(byte))
            continue
        text.append(f"{{{byte:02X}}}")


def encode_string(text: str) -> bytes:
    """Encode text back to its ASCII byte form, terminator included.

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


# --- the pointer table ---------------------------------------------------


def read_pointer(data: bytes, table_start: int, index: int) -> int:
    """File offset the table's ``index`` entry points at.

    Unlike the UTF-16LE reader, ``table_start`` is a parameter rather than a
    module constant: this codec is selected by a profile and must not carry one
    game's address.
    """
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
    """True when NUL-terminated strings tile the pool exactly.

    Every string must end where the next begins, and the last must end exactly
    at the pool end, so the walk accounts for every byte in the extent with
    nothing left over and nothing read past it.
    """
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
