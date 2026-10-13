"""Proven battery geometry, kept as data: one row per title, not one code path.

Two coordinate frames exist for the Buu's Fury word and the difference matters:

* the **buffer** frame is the game's own RAM image, where the checksum sits at
  buffer slot+``0x8A8`` (code: ``0x0800493C``..``0x08004942``);
* the **file** frame is what this machine holds. The medium stores each 8-byte
  block byte-reversed relative to the buffer, so the same word is the
  little-endian u32 at file ``slot+0x8AC``. A strict read of file ``slot+0x8A8``
  is zero in every populated Buu slot, which is why the wrong offset looks like
  an absent field.

:data:`GEOMETRIES` is a table because validity is per title: the family shares
the medium and the 8-byte-block reversal, not the slot layout. Each row names its
own evidence, so a number verified against real files and a number derived from
code are never confused. That table is also the seed of the family comparison
work, which is why it is data and not a branch.

Three facts are indexed apart, because they answer three questions:

* ``code_occupancy_bit`` - bit 0 of the decoded record's byte 1, which the game
  sets when it writes a slot record. It is set on an erased 0xFF slot too, so it
  is not validity;
* ``checksum_ok`` - the checksum comparison. For Buu's Fury and Legacy of Goku II
  this is the game's own gate; a slot that is not all 0xFF and fails it is
  CORRUPT;
* ``erased_all_ff`` - measured on this corpus, not code: an untouched slot is all
  ones.

Legacy of Goku is deliberately not computed. Its integrity field at ``slot+0x08``
is a rolling XOR key whose store and verify loops read no payload byte other than
the seed, so it cannot detect corruption, and no 512-byte save attributable to
that title exists in this corpus. It is ``checksum_ok = UNKNOWN`` with that
reason, never a pass.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

BUUS_FURY = "buus_fury"
LEGACY_OF_GOKU_II = "legacy_of_goku_ii"
LEGACY_OF_GOKU = "legacy_of_goku"

UNKNOWN = "UNKNOWN"
CORRUPT = "CORRUPT"

#: Checksum kinds, so a reader can tell a data checksum from a key that is not one.
ADLER32 = "adler32"
ROLLING_XOR_KEY = "rolling_xor_key"
NOT_COMPUTED = "not_computed"

HEADER_WORD = 0x12345678


@dataclass(frozen=True)
class Geometry:
    """One title's save layout. Data, so the family comparison can read it."""

    game: str
    medium_size: int
    slot_base: int
    slot_stride: int
    slot_count: int
    payload_len: int
    #: Buffer coordinates, relative to the slot, of the integrity word. The file
    #: frame is the same word byte-reversed, four bytes later for Buu's Fury.
    checksum_offset: int | None
    checksum_kind: str
    #: Whether the integrity word actually covers payload bytes.
    integrity_covers_payload: bool
    #: A stored value that means "this slot was never written". Zero is not a
    #: checksum any real payload produces, and it is what an unused LoGII slot
    #: holds.
    empty_checksum_value: int | None
    header_rule: str
    transform_scope: str
    evidence: str


GEOMETRIES: dict[str, Geometry] = {
    BUUS_FURY: Geometry(
        game=BUUS_FURY,
        medium_size=8192,
        slot_base=0x10,
        slot_stride=0x8B0,
        slot_count=3,
        payload_len=0x8A8,
        checksum_offset=0x8A8,
        checksum_kind=ADLER32,
        integrity_covers_payload=True,
        empty_checksum_value=None,
        header_rule="8-byte header at slot 0: checksum(first 4) + 0x12345678, written only on a"
                    " settings change",
        transform_scope="buus_fury_only",
        evidence="measured: slot 0 verified against four real saves; the 8-byte-block reversal and"
                 " the offset pair (buffer 0x8A8, file 0x8AC) are both verified",
    ),
    LEGACY_OF_GOKU_II: Geometry(
        game=LEGACY_OF_GOKU_II,
        medium_size=8192,
        slot_base=0x10,
        slot_stride=0x168,
        slot_count=3,
        payload_len=0x164,
        checksum_offset=0x164,
        checksum_kind=ADLER32,
        integrity_covers_payload=True,
        empty_checksum_value=0,
        header_rule="HYPOTHESIS: the word at image offset 0 is a settings header. Measured on the"
                    " two real saves here it is not adler32(first 4) and does not carry 0x12345678,"
                    " so no header is claimed",
        transform_scope="proven-by-file",
        evidence="slot 0 verified against three real saves, with perfect separation from the"
                 " raw-order model over 1460 files; stride 0x168 and count 3 are derived-from-code,"
                 " because only slot 0 carries a checksum in every real file held, and slots 1 and 2"
                 " hold a zero checksum over data that is not 0xFF",
    ),
    LEGACY_OF_GOKU: Geometry(
        game=LEGACY_OF_GOKU,
        medium_size=512,
        slot_base=0,
        slot_stride=0xAC,
        slot_count=2,
        payload_len=0xA0,
        checksum_offset=0x08,
        checksum_kind=ROLLING_XOR_KEY,
        integrity_covers_payload=False,
        empty_checksum_value=None,
        header_rule="the word at slot+0x08 is a rolling XOR key, not a data checksum",
        transform_scope="unknown",
        evidence="code-only: the store loop copies 167 payload bytes and the load loop 168, and the"
                 " key reads no payload byte other than the seed, so it cannot detect corruption;"
                 " no 512-byte save attributable to this title exists in the corpus",
    ),
}


def geometry_for(game: str) -> Geometry | None:
    return GEOMETRIES.get(game)


def geometry_by_size(size: int) -> Geometry | None:
    """The one geometry that claims this medium size, or None when ambiguous."""
    matches = [row for row in GEOMETRIES.values() if row.medium_size == size]
    return matches[0] if len(matches) == 1 else None


#: Filename tokens that name a title. A ROM's name is evidence about the save
#: that sits beside it, so it counts; they are checked before the medium size,
#: which two titles share.
NAME_TOKENS: tuple[tuple[str, str], ...] = (
    ("legacy of goku ii", LEGACY_OF_GOKU_II),
    ("legacy of goku 2", LEGACY_OF_GOKU_II),
    ("legacy of goku", LEGACY_OF_GOKU),
    ("buu's fury", BUUS_FURY),
    ("buus fury", BUUS_FURY),
)


def game_by_name(name: str) -> str | None:
    folded = name.lower()
    for token, game in NAME_TOKENS:
        if token in folded:
            return game
    return None


def game_by_checksum(image: bytes) -> str | None:
    """The title whose layout this image actually validates under.

    Two titles can share a medium size, and a save named `v3.sav` names neither.
    Trying each layout the size admits and keeping the one whose slot 0 passes is
    evidence from the file itself; a tie or no pass names nothing.
    """
    matches = [row for row in GEOMETRIES.values() if row.medium_size == len(image)]
    passed = [row.game for row in matches if _slot_at(image, row, 0).checksum_ok == "PASS"]
    return passed[0] if len(passed) == 1 else None


def deswizzle(data: bytes) -> bytes:
    """The buffer order of a run of medium bytes: reverse every 8-byte block."""
    whole = len(data) - len(data) % 8
    return b"".join(data[i:i + 8][::-1] for i in range(0, whole, 8)) + data[whole:]


def checksum(payload: bytes) -> int:
    """The integrity value the game stores, in the game's own arithmetic.

    Measured, not assumed: for Buu's Fury and Legacy of Goku II the stored word
    equals ``zlib.adler32`` of the de-swizzled payload. The earlier note's
    "adler32 mod 65521" is not what the image holds - that reduction gives a
    different number and fails every verified slot.
    """
    return zlib.adler32(payload)


def rolling_xor_key(payload: bytes) -> int:
    """Legacy of Goku's integrity word, computed the way its own code does.

    Code-only, and not a data checksum: the seed is payload byte 0 and the key is
    the XOR over 168 successive ``rol32(x, 3) + seed + 1`` values. It is computed
    so a real save can be compared against it, never used as validity.
    """
    seed = payload[0] if payload else 0
    value = 0
    key = 0
    for _ in range(168):
        value = ((value << 3) | (value >> 29)) & 0xFFFFFFFF
        value = (value + seed + 1) & 0xFFFFFFFF
        key ^= value
    return key


@dataclass(frozen=True)
class Slot:
    """One slot's facts, with no save content in it."""

    slot_index: int
    code_occupancy_bit: bool
    erased_all_ff: bool
    payload_len: int
    checksum_ok: str
    checksum_stored: int | None
    checksum_computed: int | None
    integrity_field_kind: str
    #: The settings header word is written only on a settings change, so it is
    #: absent from every file held, including the save the game itself wrote.
    header_written: bool
    transform_scope: str

    @property
    def occupied(self) -> bool:
        """A slot the game would keep."""
        return self.checksum_ok == "PASS"


def _slot_at(image: bytes, geometry: Geometry, index: int) -> Slot:
    """One slot, read from the file at its own offset.

    The slot's bytes are de-swizzled on their own, so every offset below is a
    slot offset and no image-level offset arithmetic can move them.
    """
    start = geometry.slot_base + index * geometry.slot_stride
    block = image[start:start + geometry.slot_stride]
    if len(block) < geometry.slot_stride:
        return Slot(index, False, False, max(len(block) - (geometry.checksum_offset or 0), 0),
                    UNKNOWN, None, None, geometry.checksum_kind, False, geometry.transform_scope)
    buffer_frame = deswizzle(block)
    payload = buffer_frame[:geometry.payload_len]
    erased = payload == b"\xff" * geometry.payload_len
    occupancy = bool(payload[1] & 0x01) if len(payload) > 1 else False
    stored = None
    if geometry.checksum_offset is not None and geometry.checksum_offset + 4 <= len(buffer_frame):
        stored = struct.unpack_from("<I", buffer_frame, geometry.checksum_offset)[0]
    computed: int | None = None
    if geometry.checksum_kind == ADLER32:
        computed = checksum(payload)
    elif geometry.checksum_kind == ROLLING_XOR_KEY:
        computed = rolling_xor_key(payload)
    if (
        erased
        or not geometry.integrity_covers_payload
        or (geometry.empty_checksum_value is not None and stored == geometry.empty_checksum_value)
    ):
        # An erased slot is not a save; an integrity field that cannot detect
        # corruption cannot validate one; and a layout's own "never written"
        # marker is not a failed save either. All three are UNKNOWN, never a pass.
        verdict = UNKNOWN
    elif stored == computed:
        verdict = "PASS"
    else:
        verdict = CORRUPT
    return Slot(index, occupancy, erased, geometry.payload_len, verdict, stored, computed,
                geometry.checksum_kind, _header_written(buffer_frame, geometry.payload_len),
                geometry.transform_scope)


def _header_written(buffer_frame: bytes, payload_len: int) -> bool:
    """Whether the settings header word sits where the layout says it would."""
    if payload_len + 4 > len(buffer_frame):
        return False
    return struct.unpack_from(">I", buffer_frame, payload_len)[0] == HEADER_WORD


def slots(image: bytes, game: str) -> list[Slot]:
    """Validity for every slot of one title's save image, in slot order."""
    geometry = geometry_for(game)
    if geometry is None:
        return []
    return [_slot_at(image, geometry, index) for index in range(geometry.slot_count)]
