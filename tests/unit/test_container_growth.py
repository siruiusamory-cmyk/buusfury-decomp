"""DRAGONBYTE-Z-CONTAINER-GROWTH-001: one growth-capable container operation.

The proof is not that a build succeeds. A grown container has to DECODE to the
payload that was authored, every dislodged reference has to be rewritten and
named in the provenance, the plan has to stay one plan, and a second build with
identical inputs has to be byte-identical.

Unlike `test_graphics_authoring.py`, whose corpus stand-in returns a fixed length
so it can test planning arithmetic, this module runs the REAL codec: the payload
is packed by `webfoot_lz.pack` through `sprite_graphics.encode_graphic_payload`,
and the relocated bytes are decoded again through `sprite_graphics.decode_graphic`,
which cross-checks the container's declared size against the piece's extents before
it returns a byte. Nothing here asserts a stub's constant length.
"""

from __future__ import annotations

import hashlib

import pytest

from tests.helpers import make_synthetic_rom, profile_for

from tools.webfoot import graphics_authoring as ga
from tools.webfoot.allocation import (AllocationKind, DEFAULT_ADDRESSABILITY)
from tools.webfoot.binary import FileOffset
from tools.webfoot.document import RomDocument
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.graphics import (CharacterIdentity, Graphic as DomainGraphic,
                                    GraphicIdentity)
from tools.webfoot.layout import (Anchor, AnchorId, Provenance, Reference,
                                  ReferenceClass, ReferenceEncoding, RomRange)
from tools.webfoot.project.model import PixelOverride
from tools.webfoot.relocation import RelocationRequest, plan_relocation
from tools.webfoot.write import plan_changes

ROM_SIZE = 0x4000
ROM_BASE = 0x08000000
PROFILE_ID = "synthetic_container_growth"
CONTAINER_A = 0x0800
CONTAINER_B = 0x0900
PIECE_A = 0x1000
PIECE_B = 0x1100
#: Deliberately smaller than the grown payload, so the growth has to leave the
#: canonical image rather than take verified-free bytes that happen to fit.
FREE_OFFSET = 0x2000
FREE_SIZE = 24
EVIDENCE = "synthetic container-growth fixture"

KIND = sg.GRAPHICS_CONTAINER_KIND
#: 16x16, because a 4bpp 8x8 payload cannot outgrow its own container: the
#: packer's worst case for 64 pixels is 48 bytes and the codec header is 8. The
#: codec takes one index per pixel and swizzles two of them into each tile byte.
WIDTH = HEIGHT = 16
PIXEL_BYTES = WIDTH * HEIGHT


def _ramp_pixels() -> bytes:
    """The graphic the container originally holds."""
    return bytes((index * 7) & 15 for index in range(64))


def _grown_pixels() -> bytes:
    """Pixels whose packed form is larger than the container it replaces."""
    return bytes((index * 73 + (index >> 2) * 29 + (index * index >> 5)) & 15
                 for index in range(PIXEL_BYTES))


def _pack(pixels: bytes, width: int, height: int) -> bytes:
    graphic = sg.Graphic(offset=CONTAINER_A, width=width, height=height,
                         colour_256=False, pixels=pixels, packed_end=CONTAINER_A)
    return sg.encode_graphic_payload(graphic, pixels, kind=KIND)


def _decode(image: bytes, start: int, width: int, height: int) -> bytes:
    """Decode the container at ``start`` and return its linear pixels.

    `sprite_graphics.decode_graphic` is the retail read path, and it cross-checks
    the container's declared size against the piece's extents before returning
    anything, so a decode that succeeds is a structural verification rather than a
    plausible-looking result.
    """
    return sg.decode_graphic(image, start, width, height, colour_256=False).pixels


def _identity(index: int) -> str:
    return f"{PROFILE_ID}/graphic:{index:04d}"


def _world():
    """A 16 KiB image holding two real containers and one confirmed consumer."""
    original = _pack(_ramp_pixels(), 8, 8)
    image = bytearray(make_synthetic_rom(size=ROM_SIZE))
    image[CONTAINER_A:CONTAINER_A + len(original)] = original
    other = bytearray(original)
    other[5] ^= 0x01
    image[CONTAINER_B:CONTAINER_B + len(other)] = other
    for piece, target in ((PIECE_A, CONTAINER_A), (PIECE_B, CONTAINER_B)):
        image[piece:piece + 4] = (ROM_BASE + target).to_bytes(4, "little")
    image = bytes(image)
    profile = profile_for(
        image,
        free_regions=[{"file_offset": FREE_OFFSET, "size": FREE_SIZE,
                       "status": "CONFIRMED", "evidence": EVIDENCE}],
        generated_expansion={"output_size": 0x8000, "padding_byte": 0xFF,
                             "evidence": EVIDENCE},
    )
    anchor = Anchor(AnchorId(_identity(0)), RomRange(FileOffset(CONTAINER_A), len(original)),
                    "graphics_container", _identity(0), 4, True,
                    Provenance(profile.id, profile.sha256, EVIDENCE))
    reference = Reference(FileOffset(PIECE_A), anchor.identity, 0,
                          ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                          ReferenceClass.CONFIRMED_REFERENCE, anchor.provenance)
    document = RomDocument.from_bytes(image, profile, anchors=(anchor,),
                                      references=(reference,))
    return image, profile, document, original


def _grown() -> bytes:
    return _pack(_grown_pixels(), WIDTH, HEIGHT)


def _request(payload: bytes, *, authorize: bool = True) -> RelocationRequest:
    return RelocationRequest(
        AnchorId(_identity(0)), payload,
        addressability=DEFAULT_ADDRESSABILITY[AllocationKind.GRAPHICS_CONTAINER],
        generated=("test", _identity(0), PIECE_A) if authorize else None)


def _materialize(image: bytes, plan) -> bytes:
    """The grown image with the plan applied, which is what a build publishes."""
    grown = bytearray(plan.generated_image.materialize(image))
    for change in plan.changes:
        grown[change.offset:change.end] = change.new
    return bytes(grown)


def test_the_fixture_actually_grows():
    """Prove the instrument before believing any negative below."""
    assert len(_grown()) > len(_pack(_ramp_pixels(), 8, 8))


# --- the refusal that was removed, and the one that replaced it --------------


def test_a_growth_request_without_an_expansion_authorization_is_refused():
    """The one refusal the generalisation keeps, and why it is kept.

    `plan_relocation` accepts a payload of any size now. What it still refuses is
    an above-EOF placement the caller did not authorize, because no provenance
    record could then explain the address those bytes were written at.
    """
    _, _, document, _ = _world()
    with pytest.raises(Exception, match="names no generated allocation authorization"):
        plan_relocation(document, [_request(_grown(), authorize=False)])


# --- the proof: a grown container decodes byte-identically -------------------


def test_a_grown_container_decodes_byte_identically_from_above_the_canonical_image():
    """The decode is the proof, not the plan's own arithmetic."""
    image, profile, document, original = _world()
    payload = _grown()
    result = plan_relocation(document, [_request(payload)])
    allocation = result.allocations[0]
    assert allocation.is_expanded, "the payload must leave the canonical image"
    assert allocation.range.start.value >= profile.size

    start = allocation.range.start.value
    output = _materialize(image, result.plan)
    assert len(output) == profile.generated_expansion.output_size
    assert output[start:start + len(payload)] == payload
    assert _decode(output, start, WIDTH, HEIGHT) == _grown_pixels(), \
        "the grown container decodes to the authored payload"
    # The container is its own object at the destination, not a tail of whatever
    # the allocator placed before it: its header is the first thing there.
    assert webfoot_lz.read_header(output, start) == (KIND, 
        sg.tile_byte_count(WIDTH, HEIGHT, colour_256=False))
    # The extent it left behind is untouched, so an undiscovered reference still
    # points at the art it always pointed at.
    assert output[CONTAINER_A:CONTAINER_A + len(original)] == \
        image[CONTAINER_A:CONTAINER_A + len(original)]


def test_every_dislodged_reference_is_rewritten_and_named_in_the_provenance():
    image, _, document, _ = _world()
    payload = _grown()
    result = plan_relocation(document, [_request(payload)])
    start = result.allocations[0].range.start.value
    output = _materialize(image, result.plan)

    assert output[PIECE_A:PIECE_A + 4] == (ROM_BASE + start).to_bytes(4, "little")
    relocation = result.plan.relocations[0]
    assert relocation.anchor == _identity(0)
    assert relocation.old_range == RomRange(FileOffset(CONTAINER_A), 24)
    assert relocation.new_range == result.allocations[0].range
    assert [r.new_source_file_offset for r in relocation.references] == [PIECE_A]
    assert [r.old_target_file_offset for r in relocation.references] == [CONTAINER_A]
    assert [r.new_target_file_offset for r in relocation.references] == [start]
    assert [r.reference.classification.value
            for r in relocation.references] == ["CONFIRMED_REFERENCE"]
    # Named, not merely rewritten: the manifest a reader sees says so too.
    documented = result.to_json()["manifest"]
    rewritten = documented["relocations"][0]["references_rewritten"][0]
    assert rewritten["source_file_offset"] == PIECE_A
    assert rewritten["new_target_file_offset"] == start
    assert documented["generated_allocations"][0]["owner"] == _identity(0)
    assert documented["generated_allocations"][0]["pointer_offset"] == PIECE_A
    # The unrelated container's own reference is untouched.
    assert output[PIECE_B:PIECE_B + 4] == image[PIECE_B:PIECE_B + 4]


# --- one plan, and one output -------------------------------------------------


def test_the_plan_is_one_plan_for_the_build():
    """The growth compiles into the single write plan, not a plan of its own."""
    image, _, document, _ = _world()
    result = plan_relocation(document, [_request(_grown())])
    assert len(result.plan.relocations) == 1
    assert len(result.plan.generated_allocations) == 1
    # Replaying the batch through the public plan entry point reproduces the same
    # plan rather than a second planning pass with its own answer.
    replay = plan_changes(image, result.plan.changes,
                          profile_id=result.plan.base_profile_id,
                          base_sha256=result.plan.base_sha256,
                          relocations=result.plan.relocations,
                          generated_image=result.plan.generated_image,
                          generated_allocations=result.plan.generated_allocations)
    assert replay.changes == result.plan.changes
    assert replay.relocations == result.plan.relocations


def test_a_second_build_with_identical_inputs_is_byte_identical():
    image, _, document, _ = _world()
    first = plan_relocation(document, [_request(_grown())])
    second = plan_relocation(document, [_request(_grown())])
    assert first.to_json() == second.to_json()
    assert _materialize(image, first.plan) == _materialize(image, second.plan)
    assert hashlib.sha256(_materialize(image, first.plan)).hexdigest() == \
        hashlib.sha256(_materialize(image, second.plan)).hexdigest()


# --- the graphics domain routes its growth through that one operation --------


def _graphic(packed_size: int) -> DomainGraphic:
    return DomainGraphic(
        identity=GraphicIdentity(PROFILE_ID, 0), file_offset=CONTAINER_A,
        width=8, height=8, colour_256=False, pixels=_ramp_pixels(),
        packed_size=packed_size, consumers=(),
        characters=(CharacterIdentity(PROFILE_ID, 0),))


class _StubSprites:
    """The four members `plan_graphic_overrides` reads, with the REAL encoder."""

    def __init__(self, profile, document, payload: bytes) -> None:
        self.profile = profile
        self._document = document
        self._payload = payload
        self._graphics = (_graphic(len(_pack(_ramp_pixels(), 8, 8))),)

    def graphics(self):
        return self._graphics

    def encode_pixels(self, identity, pixels: bytes) -> bytes:
        return self._payload

    def reference_document(self):
        return self._document


def test_the_graphics_domain_plans_its_growth_through_the_shared_operation():
    image, profile, document, _ = _world()
    payload = _grown()
    sprites = _StubSprites(profile, document, payload)
    override = PixelOverride(identity=_identity(0),
                             file="graphics/assets/graphic_0000.png",
                             pixels=_grown_pixels(), width=WIDTH, height=HEIGHT,
                             colour_256=False)
    result = ga.plan_graphic_overrides(image, None, {_identity(0): override},
                                       sprites=sprites)
    assert len(result.relocations) == 1
    assert len(result.generated_allocations) == 1
    assert result.relocations[0].anchor == _identity(0)
    assert result.relocations[0].new_range.size == len(payload)
    assert result.generated_allocations[0].domain == ga.DOMAIN

    generated = profile.generated_expansion.generated_image(
        profile.size, tuple(a.allocated_range for a in result.generated_allocations))
    plan = plan_changes(image, result.changes, profile_id=profile.id,
                        base_sha256=profile.sha256, relocations=result.relocations,
                        generated_image=generated,
                        generated_allocations=result.generated_allocations)
    output = _materialize(image, plan)
    start = result.relocations[0].new_range.start.value
    assert _decode(output, start, WIDTH, HEIGHT) == _grown_pixels()
    assert output[PIECE_A:PIECE_A + 4] == (ROM_BASE + start).to_bytes(4, "little")
    assert output[CONTAINER_A:CONTAINER_A + 24] == image[CONTAINER_A:CONTAINER_A + 24]
