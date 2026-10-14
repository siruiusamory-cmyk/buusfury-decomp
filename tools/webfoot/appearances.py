
from __future__ import annotations

import struct
from dataclasses import dataclass, replace

# Bytes per record, as the engine's own left shift by four states it.
APPEARANCE_RECORD_SIZE = 0x10

# Measured by decoding every PC-relative literal load over the whole image and reading each pool word, then confirmed by a raw four-byte search at every byte offset.
APPEARANCE_TABLE_REFERENCE_OFFSETS: tuple[int, ...] = (
    0x00025310,
    0x000256B8,
    0x0002618C,
    0x00027474,
    0x000279D8,
)

# Each is the low byte of a Thumb compare immediate, so the count is patched in place rather than through a table.
APPEARANCE_COUNT_OFFSETS: tuple[int, ...] = (0x00024F92, 0x00027998, 0x000279CC)

APPEARANCE_CANONICAL_COUNT = 0xE8

# The encoding limit a Thumb compare immediate can state, and NOT the limit a build may use: that is the flag ceiling below.
APPEARANCE_COUNT_CEILING = 0xFF

APPEARANCE_FLAG_ARRAY_BYTES = 29

#: The block initializer at file offset 0x00004838 zeroes a WORD at `block+0xE4`
#: (`mov r1,#0xE4; mov r0,#0; str r0,[r1,r4]`), so that word is the engine's and
#: record indices 248 and above overwrite it. The byte at `block+0xE3` has no
#: established owner.
APPEARANCE_BLOCK_FIRST_OWNED_WORD = 0xE4

APPEARANCE_COUNT_FLAG_CEILING = APPEARANCE_CANONICAL_COUNT + 8

ROSTER_CANONICAL_COUNT = APPEARANCE_CANONICAL_COUNT

# The flag array's ceiling is the largest count that can be built at all, and the roster object is sized for exactly that so one layout serves every authored count.
ROSTER_SUPPORTED_COUNT = APPEARANCE_COUNT_FLAG_CEILING

ROSTER_CANONICAL_OBJECT_SIZE = 0x40 + 12 * ROSTER_CANONICAL_COUNT
ROSTER_OBJECT_SIZE = 0x40 + 12 * ROSTER_SUPPORTED_COUNT
ROSTER_CANONICAL_SECOND_COUNT = 0x14 + 4 * ROSTER_CANONICAL_COUNT
ROSTER_SECOND_COUNT = 0x14 + 4 * ROSTER_SUPPORTED_COUNT
ROSTER_CANONICAL_TAIL_A = 0x18 + 12 * ROSTER_CANONICAL_COUNT
ROSTER_TAIL_A = 0x18 + 12 * ROSTER_SUPPORTED_COUNT
ROSTER_CANONICAL_TAIL_B = ROSTER_CANONICAL_TAIL_A + 8
ROSTER_TAIL_B = ROSTER_TAIL_A + 8

@dataclass(frozen=True)
class RosterPatchSite:
    offset: int
    expected: bytes
    replacement: bytes
    role: str

    def check(self, image: bytes) -> None:
        found = image[self.offset:self.offset + len(self.expected)]
        if found != self.expected:
            raise AppearanceError(
                f"file 0x{self.offset:06X} is published as the roster {self.role}, "
                f"but it holds {found.hex() or 'nothing'} rather than the canonical "
                f"{self.expected.hex()}"
            )


# Eight groups, not five, because in three of them the compiler put other instructions between the move and its shift, and requiring the pair to be adjacent would leave three functions addressing the canonical tail.
def _roster_sites() -> tuple[RosterPatchSite, ...]:
    sites = [RosterPatchSite(0x00024F42, b"\x59", b"\x5c", "object size")]

    for offset in (0x00024F60, 0x00025112, 0x0002541C, 0x00025514):
        sites.append(RosterPatchSite(offset, b"\xed", b"\xf5",
                                     "display-list count offset"))

    for movs, shift, rd in ((0x00024FD6, 0x00024FD8, 0),
                            (0x0002502C, 0x0002502E, 0),
                            (0x00025106, 0x00025108, 1),
                            (0x00025638, 0x0002563A, 1)):
        sites.append(RosterPatchSite(movs, b"\x2b", b"\x59", "tail base A"))
        sites.append(RosterPatchSite(
            shift, ((6 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            ((5 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            "tail base A shift"))

    for movs, shift, rd in ((0x00024FE0, 0x00024FE2, 0),
                            (0x0002500E, 0x00025010, 0),
                            (0x0002505A, 0x00025066, 0),
                            (0x0002536E, 0x00025370, 1),
                            (0x0002541A, 0x00025420, 1),
                            (0x000254B0, 0x000254B4, 2),
                            (0x0002552C, 0x0002552E, 0),
                            (0x0002561E, 0x00025620, 1)):
        sites.append(RosterPatchSite(movs, b"\x0b", b"\x5b", "tail base B"))
        sites.append(RosterPatchSite(
            shift, ((8 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            ((5 << 6) | (rd << 3) | rd).to_bytes(2, "little"),
            "tail base B shift"))
    return tuple(sites)


ROSTER_PATCH_SITES: tuple[RosterPatchSite, ...] = _roster_sites()

# The record-index bound enforced by the engine's branch after each compare.
APPEARANCE_COUNT_OFFSET_WIDTH = 1

# Field offsets, whose widths are the ones the engine's own loads state: two halfword loads at +0x00 and +0x02 and three word loads at +0x04, +0x08 and +0x0C.
FIELD_TEXT_INDEX = 0x00
FIELD_DESCRIPTION_INDEX = 0x02
FIELD_SPRITE_ID = 0x04
FIELD_PORTRAIT_SLOT = 0x08
FIELD_STAT_INDEX = 0x0C

# The field is written rather than omitted, so an authored record is complete rather than truncated.
DEFAULT_PORTRAIT_SLOT = 0

# The value is negative, which the engine's own branch reads as no stat record, and it is corpus-legal rather than invented.
DEFAULT_STAT_INDEX = -1

EVIDENCE = "APPEARANCE-AUTHORING-GATE-001; docs/research/APPEARANCE_TABLE_GROWTH.md"


class AppearanceError(ValueError):
    """A refusal from this domain, in this domain's own terms."""


@dataclass(frozen=True, slots=True)
class AppearanceRecord:

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
    """Every record the profile declares, refusing a short or overrun table, because no count word or terminator is stored and the extent is the profile's declaration, not a number the image carries."""
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




def reference_document(profile, image: bytes):
    """A word that no longer holds the table address is a refusal rather than a repoint, and the anchor's relocatable flag comes from layout.relocation_eligible rather than being asserted."""
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


# Listed in layout.RELOCATION_ELIGIBLE_KINDS because the five-word inbound surface is a measured, closed census rather than a scan result.
APPEARANCE_TABLE_KIND = "appearance_record_table"


def name_vocabulary(image: bytes, profile) -> tuple[int, ...]:
    """No shipped surface creates a new text-table id, so these indices are the whole vocabulary an authored name may draw from, in first-use order."""
    seen: dict[int, None] = {}
    for record in read_records(image, profile):
        seen.setdefault(record.text_index, None)
    return tuple(seen)


def sprite_vocabulary(image: bytes, profile, *, extra: int | None = None
                      ) -> tuple[int, ...]:
    """A caller that holds an authored actor-sprite id passes it as extra rather than this function inventing one, and the canonical ids come first in ascending order."""
    ids = {record.sprite_id for record in read_records(image, profile)}
    if extra is not None:
        ids.add(extra)
    return tuple(sorted(ids))
