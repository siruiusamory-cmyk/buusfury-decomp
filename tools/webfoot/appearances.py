"""The verified character appearance-definition table and its reference graph.

APPEARANCE-AUTHORING-GATE-001. The engine addresses a fixed 232-record,
`0x10`-stride table whose only bound is three compiled `cmp rN,#0xE8` loop
bounds. There is no count word and no terminator, and the byte immediately after
the extent already begins a literal-named structure, so the table can neither be
grown in place nor told how long it is from its own bytes.

What this module owns is the table's identity and its VERIFIED inbound surface:

* the profile declares the table (address, count, stride), so an extent is a
  project fact rather than a literal in a consuming module;
* the five literal-pool words that name it are published as
  `CONFIRMED_REFERENCE` / `ABSOLUTE_ROM_U32_LE`, each re-checked against the
  image before it is published, so a build can refuse rather than repoint a word
  that no longer names the table;
* the three compiled count bounds are named here as the code offsets they are.

The census behind the constants below is
`docs/research/APPEARANCE_TABLE_GROWTH.md`. They are a census result for one
image, which is why every consumer re-checks the bytes it is about to change.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, replace

#: Bytes per record, as the engine's own `index << 4` states it.
APPEARANCE_RECORD_SIZE = 0x10

#: File offsets of the five literal-pool words that hold the table address.
#: Measured by decoding every PC-relative literal load over the whole image and
#: reading each pool word, then confirmed by a raw four-byte search at every byte
#: offset: exactly these five words equal the canonical address.
APPEARANCE_TABLE_REFERENCE_OFFSETS: tuple[int, ...] = (
    0x00025310,
    0x000256B8,
    0x0002618C,
    0x00027474,
    0x000279D8,
)

#: File offsets of the three `cmp rN,#0xE8` halfwords that bound the record
#: index. Each is the low byte of a Thumb `cmp` immediate, so the count is
#: patched in place rather than through a table.
APPEARANCE_COUNT_OFFSETS: tuple[int, ...] = (0x00024F92, 0x00027998, 0x000279CC)

#: The canonical count's own encoding in those halfwords.
APPEARANCE_CANONICAL_COUNT = 0xE8

#: The largest count a Thumb `cmp rN,#imm8` can state. Beyond this the bound
#: would need code widening, so a build refuses instead. This is the ENCODING
#: limit and it is NOT the limit a build may use: see the flag array below.
APPEARANCE_COUNT_CEILING = 0xFF

#: The engine keeps one "seen" bit per record in the block it holds at
#: `[reader+8]`. The bit for record `i` is bit `i & 7` of the byte at
#: `block + 0xC5 + (i >> 3)`, so the 232 canonical records fill bytes
#: `block+0xC5` through `block+0xE1` exactly: 29 bytes, 232 bits.
APPEARANCE_FLAG_ARRAY_BYTES = 29

#: The block initializer at file offset 0x00004838 zeroes a WORD at `block+0xE4`
#: (`mov r1,#0xE4; mov r0,#0; str r0,[r1,r4]`), so that word is the engine's and
#: record indices 248 and above overwrite it. The byte at `block+0xE3` has no
#: established owner.
APPEARANCE_BLOCK_FIRST_OWNED_WORD = 0xE4

#: The largest count a build may state, from the flag array rather than from the
#: encoding. Record indices at or above the canonical count write past the array:
#: index 232 writes `block+0xE2`, and eight appended records all land in that one
#: byte. Index 240 would write `block+0xE3`, which has no established owner, and
#: index 248 would overwrite the word the initializer zeroes at `block+0xE4`. So
#: eight is the largest number of appended records whose flag storage is confined
#: to the single byte immediately after the array. INFERRED, not confirmed: no
#: writer to `block+0xE2` was found, which is the same evidence that leaves
#: `block+0xE3` unestablished, so this bound rests on the initializer zeroing a
#: WORD at `block+0xE4` and on nothing else. Confirming it means showing that
#: neither byte is read by any consumer of the block.
APPEARANCE_COUNT_FLAG_CEILING = APPEARANCE_CANONICAL_COUNT + 8

#: The roster object the engine builds from the seen-flag array, and the one
#: structure whose compiled offsets have to move when the count grows. It is
#: heap-allocated (the builder's single caller passes a null argument) and its
#: layout is `0x40 + 12 * count`: `+0x14` holds `4 * count` bytes of index
#: entries, then the display-list count, then `8 * count` bytes of display
#: entries, then a `0x28`-byte tail.
ROSTER_CANONICAL_COUNT = APPEARANCE_CANONICAL_COUNT

#: The count this build relocates the roster object for. Eight records is what
#: the flag array admits, so 240 is the largest count that can be built at all,
#: and sizing every build for it needs no per-count encoding: the additions all
#: land inside one `movs`/`lsls` pair whatever the authored count is.
#: The flag array's ceiling IS the largest buildable count, so the roster is sized
#: for exactly that.
ROSTER_SUPPORTED_COUNT = APPEARANCE_COUNT_FLAG_CEILING

#: The canonical object size and the supported one, with the three offsets that
#: follow from them.
ROSTER_CANONICAL_OBJECT_SIZE = 0x40 + 12 * ROSTER_CANONICAL_COUNT
ROSTER_OBJECT_SIZE = 0x40 + 12 * ROSTER_SUPPORTED_COUNT
ROSTER_CANONICAL_SECOND_COUNT = 0x14 + 4 * ROSTER_CANONICAL_COUNT
ROSTER_SECOND_COUNT = 0x14 + 4 * ROSTER_SUPPORTED_COUNT
ROSTER_CANONICAL_TAIL_A = 0x18 + 12 * ROSTER_CANONICAL_COUNT
ROSTER_TAIL_A = 0x18 + 12 * ROSTER_SUPPORTED_COUNT
ROSTER_CANONICAL_TAIL_B = ROSTER_CANONICAL_TAIL_A + 8
ROSTER_TAIL_B = ROSTER_TAIL_A + 8

#: One compiled statement of the roster layout that has to change with the count.
#: `expected` is what the canonical image holds, checked before anything is
#: written, and `replacement` is what states the grown offset.
@dataclass(frozen=True)
class RosterPatchSite:
    offset: int
    expected: bytes
    replacement: bytes
    role: str

    def check(self, image: bytes) -> None:
        found = image[self.offset:self.offset + len(self.expected)]
        if found != self.expected:
            raise AppearanceFormatError(
                f"file 0x{self.offset:06X} is published as the roster {self.role}, "
                f"but it holds {found.hex() or 'nothing'} rather than the canonical "
                f"{self.expected.hex()}"
            )


def _roster_sites() -> tuple[RosterPatchSite, ...]:
    """The twenty-three halfwords and immediate bytes the roster layout lives in.

    Four groups, each an idiom the engine already uses: the object size, the
    display-list count's offset, and the two tail bases. The tail bases are
    `movs` plus `lsls` pairs, so both halves are stated.
    """
    sites = [RosterPatchSite(0x00024F42, b"\x59", b"\x5c", "object size")]

    # The display-list count's offset: 0xED << 2 becomes 0xF5 << 2.
    for offset in (0x00024F60, 0x00025112, 0x0002541C, 0x00025514):
        sites.append(RosterPatchSite(offset, b"\xed", b"\xf5",
                                     "display-list count offset"))

    # The first tail base: 0x2B << 6 becomes 0x59 << 5, same object address.
    for movs, shift, rd in ((0x00024FD6, 0x00024FD8, 0),
                            (0x0002502C, 0x0002502E, 0),
                            (0x00025106, 0x00025108, 1),
                            (0x00025638, 0x0002563A, 1)):
        sites.append(RosterPatchSite(movs, b"\x2b", b"\x59", "tail base A"))
        sites.append(RosterPatchSite(
            shift, ((6 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            ((5 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            "tail base A shift"))

    # The second tail base: 0x0B << 8 becomes 0x5B << 5, same object address.
    for movs, shift, rd in ((0x00024FE0, 0x00024FE2, 0),
                            (0x0002500E, 0x00025010, 0),
                            (0x0002536E, 0x00025370, 1),
                            (0x0002552C, 0x0002552E, 0),
                            (0x0002561E, 0x00025620, 1)):
        sites.append(RosterPatchSite(movs, b"\x0b", b"\x5b", "tail base B"))
        sites.append(RosterPatchSite(
            shift, ((8 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            ((5 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            "tail base B shift"))
    return tuple(sites)


#: Every compiled statement of the roster layout, in file-offset order.
ROSTER_PATCH_SITES: tuple[RosterPatchSite, ...] = _roster_sites()

#: The record-index bound enforced by the engine's `blt` after each `cmp`.
APPEARANCE_COUNT_OFFSET_WIDTH = 1

#: Field offsets. Names are positions, and the widths are the widths the
#: engine's own loads state: two halfword loads at `+0x00`/`+0x02` and three
#: word loads at `+0x04`/`+0x08`/`+0x0C`.
FIELD_TEXT_INDEX = 0x00
FIELD_DESCRIPTION_INDEX = 0x02
FIELD_SPRITE_ID = 0x04
FIELD_PORTRAIT_SLOT = 0x08
FIELD_STAT_INDEX = 0x0C

#: The one value of `+0x08` this write path authors: 98 of the 232 canonical
#: records carry it, and every non-zero value names one of the 155 portrait
#: slots, which no shipped surface authors. The field is written, not omitted,
#: so the new record is a complete record rather than a truncated one.
DEFAULT_PORTRAIT_SLOT = 0

#: The one value of `+0x0C` this write path authors. It is negative, which the
#: engine's own `blt` reads as "no stat record"; 88 of the 232 canonical records
#: carry a negative index, so the value is corpus-legal rather than invented.
DEFAULT_STAT_INDEX = -1

#: What every anchor and reference this domain publishes cites as its ground.
EVIDENCE = "APPEARANCE-AUTHORING-GATE-001; docs/research/APPEARANCE_TABLE_GROWTH.md"


class AppearanceError(ValueError):
    """A refusal from this domain, in this domain's own terms."""


@dataclass(frozen=True, slots=True)
class AppearanceRecord:
    """One 16-byte appearance definition, in field order."""

    text_index: int
    description_index: int
    sprite_id: int
    portrait_slot: int
    stat_index: int

    def __post_init__(self) -> None:
        _require_u16(self.text_index, "text index")
        _require_u16(self.description_index, "description index")
        if type(self.sprite_id) is not int or not 0 <= self.sprite_id < 2**32:
            raise AppearanceError(
                f"sprite id {self.sprite_id!r} is not an unsigned 32-bit value"
            )
        if type(self.portrait_slot) is not int or not 0 <= self.portrait_slot < 2**32:
            raise AppearanceError(
                f"portrait slot {self.portrait_slot!r} is not an unsigned 32-bit value"
            )
        if type(self.stat_index) is not int or not -(2**31) <= self.stat_index < 2**31:
            raise AppearanceError(
                f"stat index {self.stat_index!r} is not a signed 32-bit value"
            )

    def encode(self) -> bytes:
        return struct.pack(
            "<HHIIi", self.text_index, self.description_index, self.sprite_id,
            self.portrait_slot, self.stat_index,
        )


def _require_u16(value: object, what: str) -> None:
    if type(value) is not int or not 0 <= value < 2**16:
        raise AppearanceError(f"{what} {value!r} is not an unsigned 16-bit value")


# --- the declared table ------------------------------------------------------


def table_identity(profile) -> str:
    """The published anchor identity of the appearance-definition table."""
    return f"{profile.id}/appearance_table:0000"


def declared(profile):
    """The profile's declaration of the table, or a refusal naming the profile."""
    layout = getattr(profile, "appearances", None)
    if layout is None:
        raise AppearanceError(
            f"profile {profile.id!r} declares no appearance table; the "
            "appearance-definition domain is unavailable for this ROM"
        )
    return layout


def table_offset(profile, image_size: int) -> int:
    """The table's file offset, from the profile's own declaration."""
    return declared(profile).address.to_file_offset(image_size)


def record_count(profile) -> int:
    """The canonical record count the profile declares."""
    return declared(profile).count


def read_records(image: bytes, profile) -> tuple[AppearanceRecord, ...]:
    """Every record the profile declares, refusing a short or overrun table."""
    layout = declared(profile)
    if layout.record_size != APPEARANCE_RECORD_SIZE:
        raise AppearanceError(
            f"profile {profile.id!r} declares a {layout.record_size}-byte appearance "
            f"record; this codec reads {APPEARANCE_RECORD_SIZE}-byte records"
        )
    offset = table_offset(profile, len(image))
    span = layout.count * layout.record_size
    if offset + span > len(image):
        raise AppearanceError(
            f"the declared appearance table runs past the image: {layout.count} "
            f"records at file 0x{offset:06X} need {span} bytes"
        )
    return tuple(
        AppearanceRecord(*struct.unpack_from(
            "<HHIIi", image, offset + index * APPEARANCE_RECORD_SIZE))
        for index in range(layout.count)
    )


def canonical_table(image: bytes, profile) -> bytes:
    """The table's canonical bytes, as the profile declares them."""
    offset = table_offset(profile, len(image))
    return image[offset:offset + record_count(profile) * APPEARANCE_RECORD_SIZE]


# --- the published reference graph -------------------------------------------


def reference_document(profile, image: bytes):
    """The table's anchor and its five verified inbound words.

    The words are `CONFIRMED_REFERENCE` because each was measured twice: the
    consuming instruction was decoded and the pool word it loads was read, and
    the value is re-checked against this image here. A word that no longer holds
    the table address is a refusal rather than a repoint, because the constant is
    a census result for one image and not a guarantee about another.

    The anchor's `relocatable` flag is decided by the shared contract
    (`layout.relocation_eligible`), not asserted: a kind whose inbound surface a
    ticket has not proven the graph expresses stays fixed.
    """
    from .binary import FileOffset
    from .document import RomDocument
    from .layout import (Anchor, AnchorId, Provenance, Reference, ReferenceClass,
                         ReferenceEncoding, RomRange, relocation_eligible)

    layout = declared(profile)
    offset = table_offset(profile, len(image))
    span = layout.count * layout.record_size
    expected = layout.address.raw.to_bytes(4, "little")
    provenance = Provenance(profile.id, profile.sha256, EVIDENCE)

    anchors = [Anchor(
        AnchorId(table_identity(profile)),
        RomRange(FileOffset(offset), span),
        APPEARANCE_TABLE_KIND,
        table_identity(profile),
        layout.record_size,
        False,
        provenance,
    )]
    references = []
    for source in APPEARANCE_TABLE_REFERENCE_OFFSETS:
        if image[source:source + 4] != expected:
            raise AppearanceError(
                f"file 0x{source:06X} is published as a reference to the "
                f"appearance table at 0x{layout.address.raw:08X}, but the image "
                "holds something else there"
            )
        references.append(Reference(
            FileOffset(source),
            AnchorId(table_identity(profile)),
            0,
            ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
            ReferenceClass.CONFIRMED_REFERENCE,
            provenance,
        ))
    anchors = [replace(anchor, relocatable=relocation_eligible(anchor, references))
               for anchor in anchors]
    return RomDocument.from_bytes(image, profile,
                                  anchors=tuple(anchors),
                                  references=tuple(references))


#: The anchor kind this domain publishes. Listed in
#: `layout.RELOCATION_ELIGIBLE_KINDS`, because the five-word inbound surface
#: above is a measured, closed census rather than a scan result.
APPEARANCE_TABLE_KIND = "appearance_record_table"


def name_vocabulary(image: bytes, profile) -> tuple[int, ...]:
    """The distinct text indices the canonical records use, in first-use order.

    This is the vocabulary an authored definition may draw its on-screen name
    from, because creating a new text-table id is not shipped. Ordering by first
    use rather than numerically keeps the retail order a reader recognises.
    """
    seen: dict[int, None] = {}
    for record in read_records(image, profile):
        seen.setdefault(record.text_index, None)
    return tuple(seen)


def sprite_vocabulary(image: bytes, profile, *, extra: int | None = None
                      ) -> tuple[int, ...]:
    """The sprite ids the canonical records select, ascending.

    The engine's accessor also accepts the id an authored actor-sprite identity
    takes, which is not in any canonical record, so a caller that has one passes
    it as ``extra`` rather than this function inventing it.
    """
    ids = {record.sprite_id for record in read_records(image, profile)}
    if extra is not None:
        ids.add(extra)
    return tuple(sorted(ids))
