"""SPRITE-NEW-AUTHORING-CORE-001: the sprite-identity planner, portably.

Everything here runs over synthetic bytes: a fabricated image holding a
297-entry character registry, one donor structure with a decodable animation and
frame, an object palette, a real reference document and a duck-typed stand-in for
the decoded sprite corpus. That split is deliberate. The canonical corpus walk
and the real container codec are ROM-derived and cannot be exercised portably, so
the proof against the canonical image lives in
`tests/integration/test_sprite_identity_rom.py`; what is decided HERE is what this
ticket adds - how a grown registry is laid out and repointed, where the allocator
puts the identity, how a direction-major sheet becomes frame-major engine slots,
which palette entries are written, and what is refused.

The stub is narrow on purpose. `plan_new_sprite_identity` consumes exactly four
members from the corpus object (`profile`, `palette_users()`,
`registry_identity` and `reference_document()`), so a fake supplying those four is
a faithful stand-in rather than a mock of internals, and the reference document it
returns is a real `RomDocument` built by the real validator.
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from tests.helpers import make_synthetic_rom, profile_for

from tools.webfoot import sprite_identity as sid
from tools.webfoot.allocation import InsufficientSpaceError
from tools.webfoot.binary import FileOffset
from tools.webfoot.document import RomDocument
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.layout import (Anchor, AnchorId, OwnedRegion, Provenance,
                                  Reference, ReferenceClass, ReferenceEncoding,
                                  RomRange, relocation_eligible)
from tools.webfoot.write import apply_plan, plan_changes

# --- the synthetic world -----------------------------------------------------

ROM_SIZE = 0x8000
ROM_BASE = 0x08000000
PROFILE_ID = "synthetic_exact"
EVIDENCE = "synthetic fixture for sprite-identity authoring"

#: The retail registry's own entry count, so "297 becomes 298" is asserted on a
#: table of the size the measurement was taken from.
REGISTRY_ENTRIES = 297
REGISTRY_OFFSET = 0x1000
PALETTE_OFFSET = 0x2000
BG_PALETTE_OFFSET = 0x2400
DONOR_STRUCTURE = 0x3000
DONOR_ANIMATION = 0x3100
DONOR_FRAME = 0x3200
#: The frame a donor-with-two-rects fixture points its second animation at.
DONOR_FRAME_2 = 0x3280
DONOR_CONTAINER = 0x3400
DONOR_SPRITE_ID = sid.SPRITE_ID_FLOOR
NEW_SPRITE_ID = sid.SPRITE_ID_FLOOR + REGISTRY_ENTRIES

#: The two published inbound words that name the registry. The retail pair is a
#: census of the canonical image, so a synthetic image states its own; what
#: matters here is that EVERY word the document publishes is repointed.
REGISTRY_WORDS = (0x0300, 0x0308)

#: One declared verified-free canonical region, deliberately large enough to hold
#: both spans this planner produces. Both must still land above canonical EOF,
#: which is what makes the addressability pin load-bearing rather than decorative.
FREE_OFFSET = 0x4000
FREE_SIZE = 0x0800
EXPANSION_SIZE = 0x10000

#: The donor's own frame geometry. Small so the fixtures stay cheap; every
#: authored frame copies these numbers rather than a constant in the planner.
CELL_SIDE = 8
PIECE_X = -4
PIECE_Y = -8
#: shape 0 (square), size 0 (8x8), 8bpp, no flip.
PIECE_ATTRIBUTES = 0x00002000


def _address(file_offset: int) -> bytes:
    return (ROM_BASE + file_offset).to_bytes(4, "little")


def _palette_word(index: int) -> int:
    """A distinct, valid 15-bit word per entry, so word identity is index identity.

    Entry ``i`` holds the word ``i``, which keeps artwork round-tripping exact:
    the display colour of entry ``i`` packs back to word ``i``.
    """
    return index


def _tables(entries: int = REGISTRY_ENTRIES) -> dict:
    return {
        "actor_sprites": {
            "character_table_address": ROM_BASE + REGISTRY_OFFSET,
            "character_count": entries,
            "animation_pointer_offset": 0,
            "object_palette_address": ROM_BASE + PALETTE_OFFSET,
            "bg_palette_address": ROM_BASE + BG_PALETTE_OFFSET,
            "evidence": EVIDENCE,
        }
    }


def _world(*, entries: int = REGISTRY_ENTRIES, donor_pieces: int = 1,
           colour_256: bool = True, free: bool = True, expansion: bool = True,
           relocatable: bool = True, palette_overrides=None, side: int = CELL_SIDE):
    """A 32 KiB synthetic image with a real registry, donor, palette and profile."""
    image = bytearray(make_synthetic_rom(size=ROM_SIZE))

    words = dict(palette_overrides or {})
    for index in range(sg.PALETTE_ENTRIES):
        struct.pack_into("<H", image, PALETTE_OFFSET + 2 * index,
                         words.get(index, _palette_word(index)))

    struct.pack_into(
        f"<{entries}I", image, REGISTRY_OFFSET,
        *[ROM_BASE + DONOR_STRUCTURE + index * 0x10 for index in range(entries)])
    for word in REGISTRY_WORDS:
        image[word:word + 4] = _address(REGISTRY_OFFSET)

    # The donor: a 0x54-byte header whose count byte is one, then one animation
    # pointer. Its header bytes are a deterministic pattern, so a clone that
    # changed one of them is visible in the output.
    header = bytearray(bytes(range(sid.STRUCTURE_HEADER_SIZE)))
    header[sid.STRUCTURE_COUNT_OFFSET] = 1
    image[DONOR_STRUCTURE:DONOR_STRUCTURE + sid.STRUCTURE_HEADER_SIZE] = header
    image[DONOR_STRUCTURE + sid.STRUCTURE_ANIMATION_TABLE_OFFSET:
          DONOR_STRUCTURE + sid.STRUCTURE_ANIMATION_TABLE_OFFSET + 4] = \
        _address(DONOR_ANIMATION)

    # One animation, one frame, four direction slots all naming that frame.
    struct.pack_into("<I", image, DONOR_ANIMATION, 1)
    for slot in range(sg.DIRECTION_COUNT):
        image[DONOR_ANIMATION + 4 + 4 * slot:DONOR_ANIMATION + 8 + 4 * slot] = \
            _address(DONOR_FRAME)

    attributes = PIECE_ATTRIBUTES if colour_256 else 0x00000000
    geometry = struct.pack("<bbBB", PIECE_X, PIECE_Y, side, side)
    frame = struct.pack("<I", donor_pieces) + geometry
    for piece_index in range(donor_pieces):
        frame += geometry + struct.pack(
            "<II", attributes, ROM_BASE + DONOR_CONTAINER + piece_index * 4)
    image[DONOR_FRAME:DONOR_FRAME + len(frame)] = frame

    image = bytes(image)
    overrides: dict = {"tables": _tables(entries)}
    if free:
        overrides["free_regions"] = [{
            "file_offset": FREE_OFFSET, "size": FREE_SIZE,
            "status": "CONFIRMED", "evidence": EVIDENCE,
        }]
    if expansion:
        overrides["generated_expansion"] = {
            "output_size": EXPANSION_SIZE, "padding_byte": 0xFF, "evidence": EVIDENCE,
        }
    profile = profile_for(image, **overrides)
    references = _references(profile)
    anchor = Anchor(AnchorId(_registry_identity()),
                    RomRange(FileOffset(REGISTRY_OFFSET), entries * 4),
                    "character_pointer_table", _registry_identity(), 4,
                    relocatable, _proof(profile))
    if relocatable:
        anchor = Anchor(anchor.identity, anchor.range, anchor.kind, anchor.owner,
                        anchor.alignment, relocation_eligible(anchor, references),
                        anchor.provenance)
    document = RomDocument.from_bytes(image, profile, anchors=(anchor,),
                                      references=references)
    return image, profile, document, references


def _registry_identity() -> str:
    return f"{PROFILE_ID}/character_table:0000"


def _proof(profile) -> Provenance:
    return Provenance(profile.id, profile.sha256, EVIDENCE)


def _references(profile) -> tuple[Reference, ...]:
    proof = _proof(profile)
    return tuple(
        Reference(FileOffset(word), AnchorId(_registry_identity()), 0,
                  ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                  ReferenceClass.CONFIRMED_REFERENCE, proof)
        for word in REGISTRY_WORDS
    )


class _StubSprites:
    """The four members `plan_new_sprite_identity` reads from the corpus."""

    def __init__(self, profile, document, drawn=()) -> None:
        self.profile = profile
        self._document = document
        self._drawn = dict(drawn)

    @property
    def registry_identity(self) -> str:
        return _registry_identity()

    def reference_document(self):
        return self._document

    def palette_users(self, index: int):
        return self._drawn.get(index, ())


def _sprites(world, **kwargs) -> _StubSprites:
    _image, profile, document, _references = world
    return _StubSprites(profile, document, **kwargs)


# --- sheets: a direction-major source, one palette entry per cell -------------


def _cell_colour(index: int) -> tuple[int, int, int]:
    """The display colour of palette entry ``index``."""
    return sg.expand_bgr555(_palette_word(index))


def _sheet(frames_per_direction: int = 1, *, side: int = CELL_SIDE,
           entries=None, transparent_cells=()) -> sid.SourceSheet:
    """A sheet whose cell ``c`` is solid palette entry ``c + 1``.

    Each cell being one flat index is what makes the direction-major to
    frame-major mapping checkable: the container a slot resolves to decodes to the
    entry that slot's own sheet cell was painted with.
    """
    pixels = bytearray()
    for cell in range(frames_per_direction * sg.DIRECTION_COUNT):
        if cell in transparent_cells:
            colour = sid.DEFAULT_TRANSPARENT_COLOUR
        else:
            colour = _cell_colour((entries or {}).get(cell, cell + 1))
        pixels += bytes(colour) * (side * side)
    return sid.SourceSheet(
        frames_per_direction=frames_per_direction, cell_width=side, cell_height=side,
        pixels=bytes(pixels))


def _solid_sheet(colour: tuple[int, int, int], *, side: int = CELL_SIDE):
    """A one-frame sheet painted entirely one colour, in every facing."""
    return sid.SourceSheet(
        frames_per_direction=1, cell_width=side, cell_height=side,
        pixels=bytes(colour) * (side * side * sg.DIRECTION_COUNT))


def _identity(*animations, sprite_id=NEW_SPRITE_ID, donor=DONOR_SPRITE_ID,
              free=()) -> sid.NewSpriteIdentity:
    return sid.NewSpriteIdentity(
        sprite_id=sprite_id, donor_sprite_id=donor,
        animations=tuple(animations), free_palette_entries=tuple(free))


def _animation(name="stand", **sheet_kwargs) -> sid.AnimationSource:
    return sid.AnimationSource(name=name, sheet=_sheet(**sheet_kwargs))


def _plan(world, identity, **kwargs):
    image = world[0]
    sprites = kwargs.pop("sprites", None) or _sprites(world)
    return sid.plan_new_sprite_identity(image, None, identity, sprites=sprites,
                                        **kwargs)


def _apply(world, materialization) -> bytes:
    """Plan and apply as the build does: one validation, one image."""
    image, profile, _document, _references = world
    generated = profile.generated_expansion.generated_image(
        len(image),
        tuple(a.allocated_range for a in materialization.generated_allocations))
    plan = plan_changes(
        image, materialization.changes, profile_id=profile.id,
        base_sha256=profile.sha256, relocations=materialization.relocations,
        generated_image=generated,
        generated_allocations=materialization.generated_allocations)
    return apply_plan(image, plan)


def _container_pixels(image: bytes, address: int, side: int = CELL_SIDE) -> bytes:
    return sg.decode_graphic(image, address - ROM_BASE, side, side,
                             colour_256=True).pixels


def _slots(image: bytes, materialization, animation_slot=0):
    """Resolve the identity out of the emitted image the way the engine would.

    Walks exactly the chain the sprite-id accessor walks - registry entry,
    structure, animation, frame, piece, container - and returns one
    ``(decoded pixels, container address)`` per engine direction slot.
    """
    authored = materialization.identity
    entry = (authored.registry_range.start.value
             + 4 * (authored.sprite_id - sid.SPRITE_ID_FLOOR))
    structure = int.from_bytes(image[entry:entry + 4], "little") - ROM_BASE
    slots = image[structure]
    assert slots == len(authored.animations)
    animations = [
        int.from_bytes(image[structure + sid.STRUCTURE_ANIMATION_TABLE_OFFSET + 4 * index:
                              structure + sid.STRUCTURE_ANIMATION_TABLE_OFFSET + 4 * index + 4],
                       "little") - ROM_BASE
        for index in range(slots)
    ]
    animation = animations[animation_slot]
    frame_count = int.from_bytes(image[animation:animation + 4], "little")
    container_word = sid.FRAME_HEADER_SIZE + sid.PIECE_GRAPHICS_OFFSET
    found = []
    for slot in range(frame_count * sg.DIRECTION_COUNT):
        pointer = int.from_bytes(image[animation + 4 + 4 * slot:
                                       animation + 8 + 4 * slot], "little")
        frame = pointer - ROM_BASE
        assert int.from_bytes(image[frame:frame + 4], "little") == 1
        container = int.from_bytes(
            image[frame + container_word:frame + container_word + 4], "little")
        found.append((_container_pixels(image, container), container))
    return found


# --- the canonical table grows by one entry ----------------------------------


def test_the_retail_sized_registry_grows_by_exactly_one_entry():
    world = _world()
    result = _plan(world, _identity(_animation()))
    authored = result.identity
    assert authored.registry_entries == REGISTRY_ENTRIES + 1

    output = _apply(world, result)
    start = authored.registry_range.start.value
    grown = output[start:start + (REGISTRY_ENTRIES + 1) * 4]
    assert len(grown) == 298 * 4
    assert struct.unpack_from("<I", grown, 297 * 4)[0] == \
        authored.structure_rom_address


def test_every_canonical_entry_survives_byte_identically():
    """No character structure moves, so no canonical entry is rewritten."""
    world = _world()
    image = world[0]
    result = _plan(world, _identity(_animation()))
    output = _apply(world, result)
    start = result.identity.registry_range.start.value
    canonical = image[REGISTRY_OFFSET:REGISTRY_OFFSET + REGISTRY_ENTRIES * 4]
    assert output[start:start + REGISTRY_ENTRIES * 4] == canonical
    # The canonical table's bytes are not retired, only stopped being named.
    assert output[REGISTRY_OFFSET:REGISTRY_OFFSET + REGISTRY_ENTRIES * 4] == canonical


def test_both_published_registry_words_are_repointed():
    world = _world()
    image = world[0]
    result = _plan(world, _identity(_animation()))
    output = _apply(world, result)
    moved = result.identity.registry_rom_address
    for word in REGISTRY_WORDS:
        assert int.from_bytes(image[word:word + 4], "little") == \
            ROM_BASE + REGISTRY_OFFSET
        assert int.from_bytes(output[word:word + 4], "little") == moved
    rewrites = result.relocations[0].references
    assert sorted(rewrite.reference.source.value for rewrite in rewrites) == \
        sorted(REGISTRY_WORDS)
    assert result.relocations[0].anchor == _registry_identity()


def test_the_only_canonical_bytes_written_are_the_words_and_the_palette():
    """Existing sprite data is untouched because nothing else is addressed."""
    world = _world()
    image = world[0]
    result = _plan(world, _identity(_animation()))
    canonical = sorted(change.offset for change in result.changes
                       if change.offset < len(image))
    expected = sorted(REGISTRY_WORDS + tuple(
        entry.file_offset for entry in result.identity.palette_entries))
    assert canonical == expected and result.identity.palette_entries == ()
    donor_extent = RomRange(FileOffset(DONOR_STRUCTURE), 0x58)
    for offset in canonical:
        assert not donor_extent.contains(FileOffset(offset))


def test_the_donor_structure_animation_and_frame_are_byte_identical():
    world = _world()
    image = world[0]
    result = _plan(world, _identity(_animation()))
    output = _apply(world, result)
    for offset, size in ((DONOR_STRUCTURE, 0x58), (DONOR_ANIMATION, 20),
                         (DONOR_FRAME, 20)):
        assert output[offset:offset + size] == image[offset:offset + size]


def test_the_new_identity_is_addressable_through_the_registry():
    world = _world()
    result = _plan(world, _identity(_animation()))
    output = _apply(world, result)
    slots = _slots(output, result)
    assert len(slots) == sg.DIRECTION_COUNT
    entry = (result.identity.registry_range.start.value
             + 4 * (NEW_SPRITE_ID - sid.SPRITE_ID_FLOOR))
    assert int.from_bytes(output[entry:entry + 4], "little") == \
        result.identity.structure_rom_address


def test_the_structure_clones_the_donor_header_and_states_its_own_count():
    world = _world()
    image = world[0]
    result = _plan(world, _identity(_animation(), _animation("walk")))
    output = _apply(world, result)
    start = result.identity.structure_range.start.value
    header = image[DONOR_STRUCTURE:DONOR_STRUCTURE + sid.STRUCTURE_HEADER_SIZE]
    cloned = output[start:start + sid.STRUCTURE_HEADER_SIZE]
    assert cloned[sid.STRUCTURE_COUNT_OFFSET] == 2
    assert cloned[1:] == header[1:]


# --- placement and determinism ----------------------------------------------


def test_both_spans_are_allocated_above_canonical_eof():
    """The declared canonical free region fits both, and neither may use it."""
    world = _world()
    image = world[0]
    result = _plan(world, _identity(_animation()))
    assert len(result.generated_allocations) == 2
    for allocation in result.generated_allocations:
        assert allocation.allocated_range.start.value >= len(image)
        assert allocation.expansion_evidence == EVIDENCE
    assert all(region.range.start.value >= len(image) for region in result.reserved)
    assert {region.range.size for region in result.reserved} == \
        {result.identity.containers_range.size,
         result.identity.registry_range.size + result.identity.structure_range.size
         + sum(a.animation_range.size for a in result.identity.animations)
         + sum(f.record_range.size
               for a in result.identity.animations for f in a.frames)}


def test_a_profile_without_declared_expansion_is_refused():
    world = _world(expansion=False)
    with pytest.raises(sid.SpriteIdentityError, match="no generated expansion"):
        _plan(world, _identity(_animation()))


def test_an_expansion_with_no_room_left_fails_closed():
    world = _world()
    image = world[0]
    reserved = (OwnedRegion(
        RomRange(FileOffset(len(image)), EXPANSION_SIZE - len(image)),
        "synthetic:reserved"),)
    with pytest.raises(InsufficientSpaceError):
        _plan(world, _identity(_animation()), reserved=reserved)


def test_identical_input_produces_identical_changes():
    world = _world()
    identity = _identity(_animation(), _animation("walk", frames_per_direction=4))
    first = _plan(world, identity)
    second = _plan(world, identity)
    assert first.changes == second.changes
    assert first.reserved == second.reserved
    assert first.relocations == second.relocations
    assert first.generated_allocations == second.generated_allocations
    assert first.identity.to_json() == second.identity.to_json()


def test_the_whole_plan_validates_and_applies_as_one_transaction():
    world = _world()
    result = _plan(world, _identity(_animation()))
    output = _apply(world, result)
    assert len(output) == EXPANSION_SIZE
    assert output[:len(world[0])] != world[0]


def test_generated_provenance_points_at_the_words_that_own_each_span():
    world = _world()
    result = _plan(world, _identity(_animation()))
    by_resource = {a.resource: a for a in result.generated_allocations}
    assert by_resource[sid.RECORDS_OWNER].pointer_offset == min(REGISTRY_WORDS)
    assert by_resource[sid.RECORDS_OWNER].source_range == result.relocations[0].old_range
    container_word = (result.identity.animations[0].frames[0].record_range.start.value
                      + sid.FRAME_HEADER_SIZE + sid.PIECE_GRAPHICS_OFFSET)
    assert by_resource[sid.GRAPHICS_OWNER].pointer_offset == container_word
    assert by_resource[sid.GRAPHICS_OWNER].owner == sid.GRAPHICS_OWNER


# --- the direction-major to frame-major mapping ------------------------------


def test_direction_major_cells_land_in_frame_major_engine_slots():
    """The one mapping: sheet cell ``d * frames + f`` is engine slot ``f * 4 + d``.

    Each cell is solid palette entry ``c + 1``, so the decoded container names the
    cell it came from. A sheet read straight through instead of through
    :meth:`SourceSheet.slot_cell_index` puts a different facing in every frame
    slot, which is what this asserts against.
    """
    frames = 4
    world = _world()
    result = _plan(world, _identity(_animation("walk", frames_per_direction=frames)))
    output = _apply(world, result)
    slots = _slots(output, result)
    assert len(slots) == frames * sg.DIRECTION_COUNT

    for frame_index in range(frames):
        for direction in range(sg.DIRECTION_COUNT):
            pixels, _container = slots[frame_index * sg.DIRECTION_COUNT + direction]
            sheet_cell = direction * frames + frame_index
            assert set(pixels) == {sheet_cell + 1}, (frame_index, direction)
    assert sorted({pixels[0] for pixels, _c in slots}) == list(range(1, frames * 4 + 1))
    assert len({container for _p, container in slots}) == frames * 4


def test_the_authored_records_name_the_cell_each_frame_was_built_from():
    frames = 2
    world = _world()
    result = _plan(world, _identity(_animation("stand", frames_per_direction=frames)))
    authored = result.identity.animations[0].frames
    assert [frame.slot for frame in authored] == list(range(frames * 4))
    for frame in authored:
        assert frame.sheet_cell == frame.direction * frames + frame.frame_index
        assert frame.frame_index == frame.slot // sg.DIRECTION_COUNT
        assert frame.direction == frame.slot % sg.DIRECTION_COUNT
        assert frame.sheet_name == "stand"
    assert len({frame.container_range.start.value for frame in authored}) == frames * 4


def test_two_animations_keep_their_own_order_and_frames():
    world = _world()
    result = _plan(world, _identity(_animation(),
                                    _animation("walk", frames_per_direction=2)))
    output = _apply(world, result)
    assert [animation.name for animation in result.identity.animations] == \
        ["stand", "walk"]
    assert [len(animation.frames) for animation in result.identity.animations] == \
        [4, 8]
    assert _slots(output, result)[0][0] == bytes([1]) * (CELL_SIDE * CELL_SIDE)
    walk = _slots(output, result, animation_slot=1)
    assert [pixels[0] for pixels, _container in walk] == [
        direction * 2 + frame + 1
        for frame in range(2)
        for direction in range(sg.DIRECTION_COUNT)
    ]


# --- colour ------------------------------------------------------------------


def _palette_words() -> set[int]:
    return {_palette_word(index) for index in range(sg.PALETTE_ENTRIES)}


def test_a_colour_the_palette_already_holds_writes_no_entry():
    world = _world()
    result = _plan(world, _identity(_animation()))
    assert result.identity.palette_entries == ()
    output = _apply(world, result)
    assert _slots(output, result)[0][0] == bytes([1]) * (CELL_SIDE * CELL_SIDE)


def test_a_new_colour_takes_a_requested_free_entry_and_writes_it():
    world = _world()
    green = (0, 255, 0)
    word = sg.pack_gba_colour(*green)
    assert word not in _palette_words()
    identity = _identity(
        sid.AnimationSource(name="stand", sheet=_solid_sheet(green)), free=(200, 201))
    result = _plan(world, identity)
    assert len(result.identity.palette_entries) == 1
    entry = result.identity.palette_entries[0]
    assert entry.index in (200, 201)
    assert entry.word == word
    assert entry.colour == sg.expand_bgr555(word)
    assert entry.previous_word == _palette_word(entry.index)
    assert entry.file_offset == PALETTE_OFFSET + 2 * entry.index
    output = _apply(world, result)
    assert _slots(output, result)[0][0] == \
        bytes([entry.index]) * (CELL_SIDE * CELL_SIDE)


def test_the_nearest_requested_entry_is_chosen_deterministically():
    world = _world()
    identity = _identity(
        sid.AnimationSource(name="stand", sheet=_solid_sheet((0, 255, 0))),
        free=(9, 200, 201))
    first = _plan(world, identity)
    second = _plan(world, identity)
    # Entries 200 and 201 are equidistant from the needed colour, so the lower
    # index wins and the choice cannot drift between runs.
    assert first.identity.palette_entries[0].index == 200
    assert second.identity.palette_entries[0].index == 200


def test_without_a_free_entry_a_new_colour_is_refused_rather_than_approximated():
    world = _world()
    identity = _identity(
        sid.AnimationSource(name="stand", sheet=_solid_sheet((0, 255, 0))))
    with pytest.raises(sid.SpriteIdentityError, match="will not substitute"):
        _plan(world, identity)


def test_an_entry_stored_with_bit_15_set_is_reused_rather_than_duplicated():
    """The stored word is the entry's low 15 bits, which is what its decode uses.

    One entry of the canonical object palette carries bit 15, and the write path
    can only produce 15-bit words, so a strict word comparison would fail to see a
    colour the palette already displays and would spend a free entry duplicating
    it.
    """
    world = _world(palette_overrides={5: 0xFFFF})
    white = sg.expand_bgr555(0x7FFF)
    assert white == (255, 255, 255)
    result = _plan(world, _identity(
        sid.AnimationSource(name="stand", sheet=_solid_sheet(white))))
    assert result.identity.palette_entries == ()
    output = _apply(world, result)
    assert _slots(output, result)[0][0] == bytes([5]) * (CELL_SIDE * CELL_SIDE)


def _two_colour_sheet(first: tuple[int, int, int], second: tuple[int, int, int]):
    """One sheet whose facing 0 is `first` and whose other facings are `second`.

    Both colours are needed, and the order they are met in is the order of the
    cells, which is what lets a test place the reuse and the write either way round.
    """
    pixels = bytearray()
    for cell in range(sg.DIRECTION_COUNT):
        colour = first if cell == 0 else second
        pixels += bytes(colour) * (CELL_SIDE * CELL_SIDE)
    return sid.SourceSheet(frames_per_direction=1, cell_width=CELL_SIDE,
                           cell_height=CELL_SIDE, pixels=bytes(pixels))


def _absent_word() -> int:
    """The lowest 15-bit word no entry of the fixture's default palette holds."""
    held = {_palette_word(index) & 0x7FFF for index in range(sg.PALETTE_ENTRIES)}
    return next(word for word in range(1, 0x8000) if word not in held)


def test_a_requested_entry_reused_for_its_own_colour_is_not_also_overwritten():
    """A free entry cannot be handed out in two different roles.

    Entry 5 holds a colour the artwork also uses. Reusing it for that colour must
    reserve it: a later colour written into it would repaint the pixels that just
    took it, and the plan would look successful while drawing the wrong colour.
    """
    world = _world(palette_overrides={5: _absent_word()})
    held = sg.expand_bgr555(_absent_word())
    novel = sg.expand_bgr555(0x7FFE)
    identity = _identity(
        sid.AnimationSource(name="stand", sheet=_two_colour_sheet(held, novel)),
        free=(5, 6))
    result = _plan(world, identity)
    assert [entry.index for entry in result.identity.palette_entries] == [6]
    output = _apply(world, result)
    emitted = sg.decode_palette(output, PALETTE_OFFSET)
    slots = _slots(output, result)
    first, second = slots[0][0][0], slots[1][0][0]
    assert emitted.raw[first] & 0x7FFF == _absent_word()
    assert emitted.raw[second] == result.identity.palette_entries[0].word
    assert emitted.raw[5] == _absent_word()


def test_a_requested_entry_overwritten_first_withdraws_its_old_colour():
    """The other order must be correct too: a written entry's old colour is gone."""
    world = _world(palette_overrides={5: _absent_word()})
    held = sg.expand_bgr555(_absent_word())
    novel = sg.expand_bgr555(0x7FFE)
    identity = _identity(
        sid.AnimationSource(name="stand", sheet=_two_colour_sheet(novel, held)),
        free=(5, 6))
    result = _plan(world, identity)
    output = _apply(world, result)
    emitted = sg.decode_palette(output, PALETTE_OFFSET)
    slots = _slots(output, result)
    first, second = slots[0][0][0], slots[1][0][0]
    assert first != second
    assert emitted.raw[first] == sg.pack_gba_colour(*novel)
    assert emitted.raw[second] & 0x7FFF == _absent_word()


def test_more_frames_than_the_sdk_can_read_back_are_refused():
    with pytest.raises(sid.SpriteIdentityError, match="could not be read back"):
        _sheet(sid.MAX_FRAMES_PER_ANIMATION + 1)


def test_a_donor_whose_piece_is_flipped_is_refused():
    world = _world()
    image, _profile, _document, _references = world
    flipped = bytearray(image)
    struct.pack_into("<I", flipped, DONOR_FRAME + 12,
                     PIECE_ATTRIBUTES | (0x1000 << 16))
    with pytest.raises(sid.SpriteIdentityError, match="flip bit"):
        _plan(_rebuilt_world(world, bytes(flipped)), _identity(_animation()))


def _rebuilt_world(world, image: bytes):
    """The same synthetic world over different image bytes, re-verified."""
    profile = profile_for(image, tables=_tables(), free_regions=[{
        "file_offset": FREE_OFFSET, "size": FREE_SIZE, "status": "CONFIRMED",
        "evidence": EVIDENCE,
    }], generated_expansion={
        "output_size": EXPANSION_SIZE, "padding_byte": 0xFF, "evidence": EVIDENCE,
    })
    references = _references(profile)
    anchor = Anchor(AnchorId(_registry_identity()),
                    RomRange(FileOffset(REGISTRY_OFFSET), REGISTRY_ENTRIES * 4),
                    "character_pointer_table", _registry_identity(), 4, True,
                    _proof(profile))
    document = RomDocument.from_bytes(image, profile, anchors=(anchor,),
                                      references=references)
    return image, profile, document, references


def test_a_preserved_entry_is_preferred_over_a_free_entry_showing_the_same_colour():
    """A shared colour must not spend the free entry the artwork still needs.

    Entry 7 is a preserved entry and entry 5 is requested as free; both show the
    colour the first cell uses. Reusing entry 5 would reserve it and leave the new
    colour with nowhere to go, so the preserved entry has to win and entry 5 has to
    stay available.
    """
    world = _world(palette_overrides={5: 0x0100, 7: 0x0100})
    held = sg.expand_bgr555(0x0100)
    novel = sg.expand_bgr555(0x7FFE)
    result = _plan(world, _identity(
        sid.AnimationSource(name="stand", sheet=_two_colour_sheet(held, novel)),
        free=(5,)))
    assert [entry.index for entry in result.identity.palette_entries] == [5]
    output = _apply(world, result)
    emitted = sg.decode_palette(output, PALETTE_OFFSET)
    slots = _slots(output, result)
    assert slots[0][0][0] == 7
    assert slots[1][0][0] == 5
    assert emitted.raw[7] == 0x0100
    assert emitted.raw[5] == sg.pack_gba_colour(*novel)


def test_a_written_entry_does_not_hide_a_preserved_entry_holding_its_old_colour():
    """The write order must not strand a colour another entry still shows."""
    world = _world(palette_overrides={5: 0x0100, 7: 0x0100})
    held = sg.expand_bgr555(0x0100)
    novel = sg.expand_bgr555(0x7FFE)
    result = _plan(world, _identity(
        sid.AnimationSource(name="stand", sheet=_two_colour_sheet(novel, held)),
        free=(5,)))
    assert [entry.index for entry in result.identity.palette_entries] == [5]
    output = _apply(world, result)
    emitted = sg.decode_palette(output, PALETTE_OFFSET)
    slots = _slots(output, result)
    assert emitted.raw[slots[0][0][0]] == sg.pack_gba_colour(*novel)
    assert slots[1][0][0] == 7
    assert emitted.raw[7] == 0x0100


def test_a_requested_entry_a_decoded_graphic_draws_is_refused():
    world = _world()
    sprites = _sprites(world, drawn={200: ("synthetic/graphic:0001",)})
    with pytest.raises(sid.SpriteIdentityError, match="draw it"):
        _plan(world, _identity(_animation(), free=(200,)), sprites=sprites)


def test_palette_users_is_consulted_for_every_requested_entry(monkeypatch):
    world = _world()
    seen: list[int] = []
    sprites = _sprites(world)

    def record(index):
        seen.append(index)
        return ()

    monkeypatch.setattr(sprites, "palette_users", record)
    _plan(world, _identity(_animation(), free=(7, 8)), sprites=sprites)
    assert seen == [7, 8]


def test_the_chroma_key_becomes_the_transparent_index():
    world = _world()
    result = _plan(world, _identity(_animation(transparent_cells=(0, 2))))
    output = _apply(world, result)
    slots = _slots(output, result)
    blank = bytes([sg.TRANSPARENT_INDEX]) * (CELL_SIDE * CELL_SIDE)
    assert slots[0][0] == blank
    assert slots[2][0] == blank
    assert slots[1][0] == bytes([2]) * (CELL_SIDE * CELL_SIDE)


def test_the_transparent_entry_is_never_written_or_reused():
    """Entry 0 is the hardware's transparency, so no artwork may name it."""
    world = _world()
    image = world[0]
    result = _plan(world, _identity(
        sid.AnimationSource(name="stand", sheet=_solid_sheet((0, 255, 0))), free=(1,)))
    assert result.identity.palette_entries[0].index == 1
    output = _apply(world, result)
    assert output[PALETTE_OFFSET:PALETTE_OFFSET + 2] == \
        image[PALETTE_OFFSET:PALETTE_OFFSET + 2]
    assert sg.TRANSPARENT_INDEX not in _slots(output, result)[0][0]


# --- what the API refuses ----------------------------------------------------


def test_a_sprite_id_that_is_not_the_appended_entry_is_refused():
    world = _world()
    with pytest.raises(sid.SpriteIdentityError, match="no other id is addressable"):
        _plan(world, _identity(_animation(), sprite_id=NEW_SPRITE_ID + 1))


def test_an_unknown_donor_is_refused_naming_the_supported_range():
    world = _world()
    with pytest.raises(sid.SpriteIdentityError, match="donor sprite id"):
        _plan(world, _identity(_animation(), donor=NEW_SPRITE_ID))


def test_a_multi_piece_donor_is_refused_rather_than_guessed():
    world = _world(donor_pieces=2)
    with pytest.raises(sid.SpriteIdentityError, match="one piece per frame"):
        _plan(world, _identity(_animation()))


def test_a_4bpp_donor_is_refused_rather_than_reinterpreted():
    world = _world(colour_256=False)
    with pytest.raises(sid.SpriteIdentityError, match="4bpp"):
        _plan(world, _identity(_animation()))


def test_a_sheet_at_another_size_than_the_donor_is_refused():
    world = _world()
    with pytest.raises(sid.SpriteIdentityError, match="one composition shape"):
        _plan(world, _identity(_animation(side=16)))


def test_a_sheet_smaller_than_the_donors_proven_frame_is_refused():
    """A smaller frame has no measured placement, so it is refused too."""
    world = _world(side=16)
    with pytest.raises(sid.SpriteIdentityError, match="one composition shape"):
        _plan(world, _identity(_animation(side=8)))


def test_the_measured_envelope_is_the_rect_the_authored_frames_use():
    """The guard's measurement and the emitted record agree, byte for byte."""
    world = _world(side=16)
    image = world[0]
    envelope = sid.measure_donor_envelope(image, DONOR_STRUCTURE, _frame_at(image))
    assert (envelope.width, envelope.height) == (16, 16)
    assert envelope.piece_count == 1 and envelope.pixels == 256

    # Every authored frame's header and piece carry that rect, and nothing else.
    result = _plan(world, _identity(_animation(side=16)))
    output = _apply(world, result)
    for animation in result.identity.animations:
        for frame in animation.frames:
            record = frame.record_range.start.value
            assert output[record + 6:record + 8] == bytes([envelope.width,
                                                           envelope.height])
            piece = record + sid.FRAME_HEADER_SIZE
            assert output[piece + 2:piece + 4] == bytes([envelope.width,
                                                         envelope.height])
            assert output[piece + 8:piece + 12] == \
                int(frame.container_range.start.to_gba_address(
                    frame.container_range.end).raw).to_bytes(4, "little")


def _frame_at(image: bytes):
    """The one frame decoder ``_donor`` hands the envelope measurement."""
    from tools.webfoot.binary import GbaRomAddress

    def frame_at(pointer: int, _what: str):
        return sg.decode_frame(image, GbaRomAddress(pointer).to_file_offset(len(image)))
    return frame_at


def test_a_valid_input_still_emits_the_donors_own_geometry():
    """The guard measures the donor; it does not restate the emitted record.

    This is determinism plus the record's own bytes, not a before/after diff
    against the previous code - the byte-level parity proof for an already-valid
    input is the ROM-gated Cui project case, which asserts the recorded runtime
    digest.
    """
    world = _world()
    result = _plan(world, _identity(_animation()))
    first = _apply(world, result)
    second = _apply(world, _plan(world, _identity(_animation())))
    assert first == second
    # And the record's own geometry is still the donor's, not a guarded restatement.
    record = result.identity.animations[0].frames[0].record_range.start.value
    assert first[record:record + 8] == struct.pack(
        "<Ibb", 1, PIECE_X, PIECE_Y) + bytes([CELL_SIDE, CELL_SIDE])
    assert first[record + 8:record + 12] == struct.pack("<bbBB", PIECE_X, PIECE_Y,
                                                        CELL_SIDE, CELL_SIDE)


def test_a_donor_whose_frames_disagree_about_their_rect_is_refused():
    """No single proven shape exists, so no authored geometry can be called one."""
    world = _world()
    image = bytearray(world[0])
    struct.pack_into("<I", image, DONOR_ANIMATION, 2)
    struct.pack_into(f"<{2 * sg.DIRECTION_COUNT}I", image, DONOR_ANIMATION + 4,
                     *([ROM_BASE + DONOR_FRAME] * sg.DIRECTION_COUNT
                       + [ROM_BASE + DONOR_FRAME_2] * sg.DIRECTION_COUNT))
    struct.pack_into("<I", image, DONOR_FRAME_2, 1)
    struct.pack_into("<bbBB", image, DONOR_FRAME_2 + 4, PIECE_X, PIECE_Y,
                     CELL_SIDE * 2, CELL_SIDE * 2)
    with pytest.raises(sid.SpriteIdentityError, match="several shapes"):
        _plan(_rebuilt_world(world, bytes(image)), _identity(_animation()))


def test_a_donor_whose_frame_box_contradicts_its_own_piece_is_refused():
    """The box the authored record copies must be the rect the donor draws."""
    world = _world()
    image = bytearray(world[0])
    struct.pack_into("<BB", image, DONOR_FRAME + 6, CELL_SIDE * 2, CELL_SIDE * 2)
    with pytest.raises(sid.SpriteIdentityError, match="disagrees with itself"):
        _plan(_rebuilt_world(world, bytes(image)), _identity(_animation()))


def test_a_donor_whose_frames_share_a_rect_but_not_an_anchor_is_refused():
    """One rect at two anchors is not one proven placement either.

    Both frames are 8x8 single pieces; the second sits one pixel higher, at
    ``PIECE_Y - 1``, in both its frame box and its piece record.
    """
    world = _world()
    image = bytearray(world[0])
    struct.pack_into("<I", image, DONOR_ANIMATION, 2)
    struct.pack_into(f"<{2 * sg.DIRECTION_COUNT}I", image, DONOR_ANIMATION + 4,
                     *([ROM_BASE + DONOR_FRAME] * sg.DIRECTION_COUNT
                       + [ROM_BASE + DONOR_FRAME_2] * sg.DIRECTION_COUNT))
    struct.pack_into("<I", image, DONOR_FRAME_2, 1)
    struct.pack_into("<bbBB", image, DONOR_FRAME_2 + 4, PIECE_X, PIECE_Y - 1,
                     CELL_SIDE, CELL_SIDE)
    struct.pack_into("<bbBB", image, DONOR_FRAME_2 + 8, PIECE_X, PIECE_Y - 1,
                     CELL_SIDE, CELL_SIDE)
    struct.pack_into("<II", image, DONOR_FRAME_2 + 12,
                     PIECE_ATTRIBUTES, ROM_BASE + DONOR_CONTAINER)
    with pytest.raises(sid.SpriteIdentityError, match="several anchors"):
        _plan(_rebuilt_world(world, bytes(image)), _identity(_animation()))


def test_a_donor_whose_animation_slot_is_null_is_skipped():
    """A null animation word is skipped rather than decoded or refused."""
    world = _world()
    image = bytearray(world[0])
    image[DONOR_STRUCTURE + sid.STRUCTURE_COUNT_OFFSET] = 2
    struct.pack_into("<I", image, DONOR_STRUCTURE + sid.STRUCTURE_ANIMATION_TABLE_OFFSET
                     + 4, 0)
    result = _plan(_rebuilt_world(world, bytes(image)), _identity(_animation()))
    assert result.identity.sprite_id == NEW_SPRITE_ID


def test_a_donor_that_names_no_decodable_frame_is_refused():
    """Every animation slot null: nothing is proven about the donor's frames."""
    world = _world()
    image = bytearray(world[0])
    struct.pack_into("<I", image, DONOR_STRUCTURE + sid.STRUCTURE_ANIMATION_TABLE_OFFSET,
                     0)
    with pytest.raises(sid.SpriteIdentityError, match="names no decodable frame"):
        _plan(_rebuilt_world(world, bytes(image)), _identity(_animation()))


def test_a_null_first_slot_is_refused_before_the_geometry_is_read():
    """The envelope skips a null slot, but the copied geometry still needs one.

    ``_donor`` reads slot 0 for the frame it copies, so a null slot 0 is refused
    by the file-offset check rather than silently authoring from a later slot.
    """
    world = _world()
    image = bytearray(world[0])
    image[DONOR_STRUCTURE + sid.STRUCTURE_COUNT_OFFSET] = 2
    struct.pack_into("<I", image, DONOR_STRUCTURE + sid.STRUCTURE_ANIMATION_TABLE_OFFSET,
                     0)
    struct.pack_into("<I", image, DONOR_STRUCTURE + sid.STRUCTURE_ANIMATION_TABLE_OFFSET
                     + 4, ROM_BASE + DONOR_ANIMATION)
    with pytest.raises(sid.SpriteIdentityError, match="not a file offset"):
        _plan(_rebuilt_world(world, bytes(image)), _identity(_animation()))


def test_an_unrelocatable_registry_is_refused():
    world = _world(relocatable=False)
    with pytest.raises(sid.SpriteIdentityError, match="not published relocatable"):
        _plan(world, _identity(_animation()))


def test_a_registry_word_that_no_longer_holds_the_table_is_refused():
    """A document built for one image cannot be used against another."""
    world = _world()
    sprites = _sprites(world)
    other = bytearray(world[0])
    other[REGISTRY_WORDS[1]:REGISTRY_WORDS[1] + 4] = b"\x00\x00\x00\x00"
    with pytest.raises(sid.SpriteIdentityError, match="does not hold the canonical"):
        sid.plan_new_sprite_identity(bytes(other), None, _identity(_animation()),
                                     sprites=sprites)


def test_a_registry_anchor_of_the_wrong_size_is_refused():
    world = _world()
    image, profile, _document, references = world
    anchor = Anchor(AnchorId(_registry_identity()),
                    RomRange(FileOffset(REGISTRY_OFFSET), 8),
                    "character_pointer_table", _registry_identity(), 4, True,
                    _proof(profile))
    document = RomDocument.from_bytes(image, profile, anchors=(anchor,),
                                      references=references)
    with pytest.raises(sid.SpriteIdentityError, match="the profile declares"):
        _plan((image, profile, document, references), _identity(_animation()))


def test_a_registry_anchor_of_another_kind_is_refused():
    world = _world()
    image, profile, _document, references = world
    anchor = Anchor(AnchorId(_registry_identity()),
                    RomRange(FileOffset(REGISTRY_OFFSET), REGISTRY_ENTRIES * 4),
                    "character_structure", _registry_identity(), 4, True,
                    _proof(profile))
    document = RomDocument.from_bytes(image, profile, anchors=(anchor,),
                                      references=references)
    with pytest.raises(sid.SpriteIdentityError, match="character_pointer_table"):
        _plan((image, profile, document, references), _identity(_animation()))


def test_a_donor_that_does_not_decode_is_refused():
    world = _world()
    image = bytearray(world[0])
    struct.pack_into("<I", image, DONOR_ANIMATION, 0)
    profile = profile_for(bytes(image), tables=_tables(), free_regions=[{
        "file_offset": FREE_OFFSET, "size": FREE_SIZE, "status": "CONFIRMED",
        "evidence": EVIDENCE,
    }], generated_expansion={
        "output_size": EXPANSION_SIZE, "padding_byte": 0xFF, "evidence": EVIDENCE,
    })
    references = _references(profile)
    anchor = Anchor(AnchorId(_registry_identity()),
                    RomRange(FileOffset(REGISTRY_OFFSET), REGISTRY_ENTRIES * 4),
                    "character_pointer_table", _registry_identity(), 4, True,
                    _proof(profile))
    document = RomDocument.from_bytes(bytes(image), profile, anchors=(anchor,),
                                      references=references)
    with pytest.raises(sid.SpriteIdentityError, match="does not decode"):
        _plan((bytes(image), profile, document, references), _identity(_animation()))


def test_too_many_animation_slots_are_refused_at_construction():
    sheet = _sheet()
    animations = tuple(
        sid.AnimationSource(name=f"slot{index}", sheet=sheet)
        for index in range(sid.MAX_ANIMATION_SLOTS + 1))
    with pytest.raises(sid.SpriteIdentityError, match="exceeds"):
        _identity(*animations)


def test_duplicate_animation_names_are_refused():
    with pytest.raises(sid.SpriteIdentityError, match="unique"):
        _identity(_animation("stand"), _animation("stand"))


def test_an_identity_with_no_animation_is_refused():
    with pytest.raises(sid.SpriteIdentityError, match="at least one"):
        sid.NewSpriteIdentity(sprite_id=NEW_SPRITE_ID,
                              donor_sprite_id=DONOR_SPRITE_ID, animations=())


@pytest.mark.parametrize("index", [0, 256, -1, "7"])
def test_a_free_entry_outside_the_palette_is_refused_at_construction(index):
    with pytest.raises(sid.SpriteIdentityError, match="free palette entry"):
        _identity(_animation(), free=(index,))


def test_a_repeated_free_entry_is_refused_at_construction():
    with pytest.raises(sid.SpriteIdentityError, match="repeat"):
        _identity(_animation(), free=(9, 9))


def test_a_sheet_whose_pixels_do_not_match_its_cells_is_refused():
    with pytest.raises(sid.SpriteIdentityError, match="RGB bytes"):
        sid.SourceSheet(frames_per_direction=1, cell_width=CELL_SIDE,
                        cell_height=CELL_SIDE, pixels=b"\x00" * 10)


def test_a_sheet_cell_index_outside_the_sheet_is_refused():
    sheet = _sheet()
    with pytest.raises(sid.SpriteIdentityError, match="outside"):
        sheet.slot_cell_index(1, 0)
    with pytest.raises(sid.SpriteIdentityError, match="outside"):
        sheet.slot_cell_index(0, sg.DIRECTION_COUNT)


def test_planning_something_that_is_not_an_identity_is_refused():
    world = _world()
    with pytest.raises(sid.SpriteIdentityError, match="NewSpriteIdentity"):
        _plan(world, "not an identity")


def test_a_profile_that_declares_no_actor_sprites_is_refused():
    world = _world()
    image, _profile, document, references = world
    stripped = profile_for(image, free_regions=[{
        "file_offset": FREE_OFFSET, "size": FREE_SIZE, "status": "CONFIRMED",
        "evidence": EVIDENCE,
    }], generated_expansion={
        "output_size": EXPANSION_SIZE, "padding_byte": 0xFF, "evidence": EVIDENCE,
    })
    sprites = _StubSprites(stripped, document)
    with pytest.raises(sid.SpriteIdentityError, match="declares no actor_sprites"):
        _plan((image, stripped, document, references), _identity(_animation()),
              sprites=sprites)


# --- the module's own public surface ----------------------------------------


def test_the_registry_anchor_kind_it_requires_is_relocation_eligible():
    from tools.webfoot.layout import RELOCATION_ELIGIBLE_KINDS
    assert "character_pointer_table" in RELOCATION_ELIGIBLE_KINDS
    assert isinstance(sid.SpriteIdentityError("x"), ValueError)


def test_no_module_constant_restates_a_retail_address():
    """The registry's length and address come from the profile, not a constant."""
    source = Path(sid.__file__).read_text(encoding="utf-8")
    for retail in ("0x6B6BDC", "0x006B6BDC", "0x072EF8", "0x006A89D0"):
        assert retail not in source
