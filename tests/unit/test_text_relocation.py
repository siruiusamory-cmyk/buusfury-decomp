"""TOOLKIT-004 synthetic proof that longer text relocates correctly.

No ROM bytes appear here. The fixture is a miniature of the real topology,
because that topology is what makes the proof mean something:

    a string pool, exhaustively tiled, with a pointer table whose entries are
    the ONLY inbound references to the strings

The canonical Buu's Fury profile declares no verified free space, so canonical
growth is blocked and stays blocked. These tests prove the growth path itself on
a fixture that DOES declare free space, which is the only honest way to
demonstrate it without inventing a free region in a real game.

The reference class matters here in a way it does not for fixed-stride records:
a string's table slot is a `DECLARED_REFERENCE` because the pointer table's role
is verified, while a word elsewhere in the image that merely happens to equal a
string address is a `CANDIDATE_REFERENCE` and must block relocation until it is
resolved. The canonical ROM has exactly five such coincidences.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib

import pytest

from tools.webfoot.allocation import InsufficientSpaceError
from tools.webfoot.binary import FileOffset
from tools.webfoot.document import RomDocument
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.layout import (
    Anchor,
    AnchorId,
    LayoutError,
    Provenance,
    Reference,
    ReferenceClass as RC,
    ReferenceEncoding as RE,
    RomRange,
)
from tools.webfoot.profile import RomProfile
from tools.webfoot.relocation import (
    CandidateReferenceError,
    RelocationRequest,
    plan_relocation,
)
from tools.webfoot.write import apply_plan


#: Where the miniature pool and table live in the fixture image.
IMAGE_SIZE = 0x600
POOL = 0x100
TABLE = 0x180
FREE = 0x300
#: Sized to hold two of the longer payloads at once, so the multi-string batch
#: tests exercise allocation ordering rather than exhaustion.
FREE_SIZE = 0x200

#: The three strings the fixture pool holds, in table order. The middle one is
#: the relocation target: moving a string that is neither first nor last is
#: what proves the neighbours are left alone.
STRINGS = ("Start", "New Game", "Options")

STRING_IDS = tuple(AnchorId(f"text:{i:04d}") for i in range(len(STRINGS)))


def _build_image() -> tuple[bytearray, tuple[int, ...]]:
    """A synthetic image whose pool is exhaustively tiled, as the real one is."""
    image = bytearray(IMAGE_SIZE)
    # A plausible GBA header, so profile construction has something to check.
    image[0xA0:0xAC] = b"SYNTHETIC   "
    image[0xAC:0xB0] = b"TEST"
    image[0xB0:0xB2] = b"00"
    image[0xB2] = 0x96
    image[0xBD] = (-(sum(image[0xA0:0xBD]) + 0x19)) & 255

    offsets = []
    cursor = POOL
    for text in STRINGS:
        encoded = tt.encode_string(text)
        image[cursor : cursor + len(encoded)] = encoded
        offsets.append(cursor)
        cursor += len(encoded)

    for index, offset in enumerate(offsets):
        slot = TABLE + index * 4
        image[slot : slot + 4] = (offset + tt.GBA_ROM_BASE).to_bytes(4, "little")

    return image, tuple(offsets)


def _document(*, candidate_at: int | None = None) -> RomDocument:
    """The fixture as a `RomDocument`: one anchor per string, one ref each.

    `candidate_at` plants a word elsewhere in the image that equals the middle
    string's address and is declared `CANDIDATE_REFERENCE` - the shape of the
    five coincidental matches the canonical ROM actually contains.
    """
    image, offsets = _build_image()

    if candidate_at is not None:
        image[candidate_at : candidate_at + 4] = (
            offsets[1] + tt.GBA_ROM_BASE
        ).to_bytes(4, "little")

    profile = RomProfile.from_mapping(
        {
            "id": "synthetic-text-v1",
            "game": "synthetic",
            "region": "test",
            "revision": 0,
            "game_code": "TEST",
            "size": len(image),
            "sha256": hashlib.sha256(bytes(image)).hexdigest(),
            "free_regions": [
                {
                    "file_offset": FREE,
                    "size": FREE_SIZE,
                    "status": "CONFIRMED",
                    "evidence": "synthetic fixture construction; no game claim",
                }
            ],
        }
    )
    provenance = Provenance(
        profile.id, profile.sha256, "synthetic verified text layout contract"
    )

    anchors = tuple(
        Anchor(
            identity,
            RomRange(FileOffset(offset), len(tt.encode_string(text))),
            "text-string",
            f"owner:{identity.value}",
            2,
            True,
            provenance,
        )
        for identity, offset, text in zip(STRING_IDS, offsets, STRINGS)
    )

    references = [
        Reference(
            FileOffset(TABLE + index * 4),
            identity,
            0,
            RE.ABSOLUTE_ROM_U32_LE,
            RC.DECLARED_REFERENCE,
            provenance,
        )
        for index, identity in enumerate(STRING_IDS)
    ]
    if candidate_at is not None:
        references.append(
            Reference(
                FileOffset(candidate_at),
                STRING_IDS[1],
                0,
                RE.ABSOLUTE_ROM_U32_LE,
                RC.CANDIDATE_REFERENCE,
                provenance,
            )
        )

    return RomDocument.from_bytes(
        bytes(image), profile, anchors=anchors, references=tuple(references)
    )


LONGER = tt.encode_string("A Considerably Longer Replacement")


def _pointer(image: bytes, index: int) -> int:
    slot = TABLE + index * 4
    return int.from_bytes(image[slot : slot + 4], "little") - tt.GBA_ROM_BASE


# --- exit criterion 13: longer text relocates ----------------------------


def test_longer_text_is_allocated_from_declared_free_space():
    result = plan_relocation(
        _document(), [RelocationRequest(STRING_IDS[1], LONGER)]
    )
    allocation, = result.allocations
    assert allocation.request.anchor == STRING_IDS[1]
    assert FREE <= allocation.range.start.value
    assert allocation.range.end <= FREE + FREE_SIZE
    assert allocation.range.size == len(LONGER)
    assert "synthetic fixture" in allocation.free_region_evidence


def test_relocated_text_is_written_at_the_destination_and_decodes_back():
    document = _document()
    result = plan_relocation(document, [RelocationRequest(STRING_IDS[1], LONGER)])
    image = apply_plan(document.image, result.plan)

    destination = result.allocations[0].range.start.value
    text, end = tt.decode_string(image, destination)
    assert text == "A Considerably Longer Replacement"
    assert end - destination == len(LONGER)


# --- exit criterion 14: declared references are rewritten ----------------


def test_the_strings_table_slot_is_rewritten_to_the_new_address():
    """One word changes, because the table slot is the only inbound reference.

    That is the whole reason this subsystem is cheap to relocate, so it is
    asserted rather than assumed.
    """
    document = _document()
    result = plan_relocation(document, [RelocationRequest(STRING_IDS[1], LONGER)])
    image = apply_plan(document.image, result.plan)

    destination = result.allocations[0].range.start.value
    assert _pointer(image, 1) == destination


def test_untouched_strings_keep_their_pointers_and_their_bytes():
    document = _document()
    result = plan_relocation(document, [RelocationRequest(STRING_IDS[1], LONGER)])
    image = apply_plan(document.image, result.plan)

    for index in (0, 2):
        assert _pointer(image, index) == _pointer(document.image, index)
        offset = _pointer(image, index)
        assert tt.decode_string(image, offset)[0] == STRINGS[index]


def test_the_vacated_region_is_left_exactly_as_it_was():
    """TOOLKIT-003 does not reclaim old regions, and this ticket does not either.

    Asserted because a reader could reasonably expect the old bytes to be
    cleared; they are not, and a future reclamation ticket would change this
    test deliberately rather than discover the behaviour by accident.
    """
    document = _document()
    result = plan_relocation(document, [RelocationRequest(STRING_IDS[1], LONGER)])
    image = apply_plan(document.image, result.plan)

    old = document.anchor(STRING_IDS[1]).range
    assert image[old.start.value : old.end] == document.image[old.start.value : old.end]


# --- exit criterion 15: candidate references block relocation ------------


def test_a_candidate_reference_blocks_relocation_of_the_string_it_names():
    """The five coincidental pool-address matches in the canonical ROM are
    exactly this shape, and they must fail closed rather than be rewritten."""
    document = _document(candidate_at=0xF0)
    with pytest.raises(CandidateReferenceError, match="0x000000F0"):
        plan_relocation(document, [RelocationRequest(STRING_IDS[1], LONGER)])


def test_a_candidate_reference_does_not_block_an_unrelated_string():
    """Fail-closed must be targeted; blocking everything would be useless."""
    document = _document(candidate_at=0xF0)
    result = plan_relocation(document, [RelocationRequest(STRING_IDS[0], LONGER)])
    assert result.allocations[0].request.anchor == STRING_IDS[0]


# --- exit criterion 16: failure emits nothing ----------------------------


def test_insufficient_free_space_relocates_nothing_at_all():
    """Atomicity: a refused batch leaves no partially-moved string behind."""
    document = _document()
    oversized = b"\x41\x00" * (FREE_SIZE + 8) + b"\x00\x00"
    with pytest.raises(InsufficientSpaceError):
        plan_relocation(document, [RelocationRequest(STRING_IDS[1], oversized)])


def test_a_failed_batch_leaves_every_pointer_untouched():
    document = _document()
    oversized = b"\x41\x00" * (FREE_SIZE + 8) + b"\x00\x00"
    with pytest.raises(InsufficientSpaceError):
        plan_relocation(document, [RelocationRequest(STRING_IDS[1], oversized)])
    # The document is immutable, so this is really a check that no in-place
    # mutation crept into the failure path.
    for index in range(len(STRINGS)):
        assert tt.decode_string(document.image, _pointer(document.image, index))[0] == (
            STRINGS[index]
        )


def test_two_strings_relocate_together_deterministically():
    """Same batch, same inputs, same destinations - twice."""
    requests = [
        RelocationRequest(STRING_IDS[0], LONGER),
        RelocationRequest(STRING_IDS[2], LONGER),
    ]
    first = plan_relocation(_document(), requests)
    second = plan_relocation(_document(), requests)
    assert [a.range.to_json() for a in first.allocations] == [
        a.range.to_json() for a in second.allocations
    ]
    assert apply_plan(_document().image, first.plan) == apply_plan(
        _document().image, second.plan
    )


def test_batch_order_does_not_change_the_result():
    """Allocation sorts by identity, so the caller's order cannot leak in."""
    forward = plan_relocation(
        _document(),
        [
            RelocationRequest(STRING_IDS[0], LONGER),
            RelocationRequest(STRING_IDS[2], LONGER),
        ],
    )
    reverse = plan_relocation(
        _document(),
        [
            RelocationRequest(STRING_IDS[2], LONGER),
            RelocationRequest(STRING_IDS[0], LONGER),
        ],
    )
    assert [a.range.to_json() for a in forward.allocations] == [
        a.range.to_json() for a in reverse.allocations
    ]


def test_a_non_relocatable_string_is_refused():
    """The canonical profile declares `relocatable: false`; this is that rule."""
    document = _document()
    pinned = tuple(
        replace(anchor, relocatable=False) if anchor.identity == STRING_IDS[1] else anchor
        for anchor in document.anchors
    )
    document = RomDocument.from_bytes(
        document.image, document.profile, anchors=pinned, references=document.references
    )
    with pytest.raises(LayoutError, match="non-relocatable"):
        plan_relocation(document, [RelocationRequest(STRING_IDS[1], LONGER)])
