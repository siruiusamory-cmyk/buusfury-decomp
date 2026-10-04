"""SPRITE-NEW-RUNTIME-001: one additional actor-sprite identity, above EOF.

This is the runtime experiment the sprite-new boundary ticket specified. It emits
a derivative ROM in which Buu's Fury can resolve and render a sprite identity the
retail image never contained, without replacing any existing sprite asset.

WHAT IS NEW, AND WHAT IS NOT
============================

Nothing canonical is retired. The retail registry at ROM ``0x086B6BDC``, all 297
character structures, and every existing animation, frame and graphics container
stay byte-identical. The derivative adds:

* a **298-entry registry** in freshly allocated space, whose first 297 entries are
  the canonical entries verbatim (no character structure moves, so no entry needs
  rewriting) plus entry 297 naming the new structure;
* the two literal-pool words that named the old registry, repointed to the new
  one. They are read from the published reference graph, not re-derived here;
* one **new character structure**, a verbatim clone of sprite 10's 0x54-byte
  header with both animation slots naming the new animation;
* one **new animation record**, two frames, all eight direction cells naming one
  new frame record;
* one **new frame record** and one **new kind-1 graphics container**;
* one placement's ``+0x10`` sprite id, changed from 10 to 307.

WHY THE SHAPE IS WHAT IT IS
===========================

**The registry cannot grow in place.** The word after entry 296 is a live IWRAM
pointer slot and the XP table follows it. The registry's entire inbound surface is
two Thumb literal-pool words (measured; see
``webfoot.graphics.CHARACTER_TABLE_REFERENCE_OFFSETS``), so growing it costs a
two-word patch.

**The new animation is laid out immediately before the new frame record.** An
animation's proven extent is ``4 + 16 * frame_count`` bytes and two further words
follow it in 987 of the 1,017 canonical objects, but no read site for them is
known and their values do not track the animation's own frames. Laying a frame
record straight after the pointer table reproduces the shape the other 30
canonical objects have, so the words are a frame header rather than an invented
trailer.

**Every direction cell names the same frame.** The compositor dereferences
``obj+0x54`` with no null test and the corpus has 0 null cells among 13,660, so a
null frame pointer is not an option. The Cui sheets are a single direction, so all
four slots point at one record. The sprite therefore renders identically from
every facing and does not turn or mirror, and no facing is named.

**The frame is 32x32 and the controlled actor already draws 32x32.** CRASH-ROOT-
CAUSE-001 measured a per-actor frame-composition budget and showed that growing a
frame past it corrupts the actor. The rule that sizes that buffer is NOT solved
here; this experiment avoids it by pointing a 32x32 sprite at an actor that
already renders 32x32 frames, so the budget is proven adequate by the retail
game's own behaviour.

COLOUR
======

The Cui sheets are fully opaque and use ``#FF00FF`` as a chroma key, which becomes
palette index 0. Every remaining colour is already exactly a 5-bit colour, so no
quantisation is performed: ``v = channel >> 3`` is exact and the displayed colour
is ``(v << 3) | (v >> 2)``. A colour that already exists in the global object
palette is reused; one that does not is written into a palette index that no
actor-sprite graphic and no portrait draws.

Run::

    python tools/research/sprite_new_runtime.py --rom <canonical> --out <derivative>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
_TOOLS = _HERE.parents[1]
for _entry in (str(_TOOLS), str(_HERE.parent), str(_REPO)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from webfoot.allocation import (Addressability, AllocationKind, AllocationRequest,
                                allocate)
from webfoot.binary import FileOffset
from webfoot.formats import map_placements as mp
from webfoot.formats import sprite_graphics as sg
from webfoot.graphics import load_actor_sprites
from webfoot.layout import AnchorId, OwnedRegion, RomRange
from webfoot.profile import RomProfileCatalog
from webfoot.rom import identify_rom
from webfoot.write import (ByteChange, GeneratedImage, apply_plan, emit_image,
                           plan_changes)

# --- the canonical image this experiment was measured against ---------------

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The actor-sprite registry: file offset, entry count, and the id of entry 0.
REGISTRY_FILE_OFFSET = 0x006B6BDC
REGISTRY_ENTRIES = 297
SPRITE_ID_FLOOR = 10

#: The identity this experiment adds. Entry 297 of the new registry, so the
#: engine's unchecked ``registry + 4 * (id - 10)`` lands on it.
NEW_SPRITE_ID = 307

#: The donor whose structure header is cloned, and whose 32x32 frames prove the
#: controlled actor's composition budget. Its header is copied verbatim because
#: the meaning of ``+0x10..+0x4F`` is unresolved; only the animation slots change.
DONOR_SPRITE_ID = 10
DONOR_STRUCTURE_FILE_OFFSET = 0x006A89D0
DONOR_STRUCTURE_SIZE = 0x5C             # 0x54-byte header + 2 animation pointers
DONOR_HEADER_SIZE = 0x54
ANIMATION_SLOT_COUNT = 2                # copied from the donor's +0x00

#: The controlled actor: map 19 placement 6, whose sprite id is the only word
#: changed. Placements 7 to 10 in the same map keep sprite 10, so the retail
#: sprite stays on screen as a control.
CONTROLLED_PLACEMENT_FILE_OFFSET = 0x072EF8
CONTROLLED_PLACEMENT_ID_FIELD = 0x10
CONTROLLED_PLACEMENT_LABEL = "map 19 placement 6"
CONTROLLED_PLACEMENT_ID_OLD = DONOR_SPRITE_ID

#: The party table. The actor a map-19 placement supplies does not exist on every
#: map - map 102, West City park, has zero placement records - and on such a map
#: the only actor is the player. The player's sprite id is not a placement field:
#: `0x08000158` resolves a party slot (argument < 10) by walking to a 24-byte
#: record in this table and reading its u16 at +0x0E, then feeding that back into
#: the same resolver. So the same identity can be attached to the player by
#: repointing that field instead of a placement's.
PARTY_TABLE_FILE_OFFSET = 0x006B82EC
PARTY_STRIDE = 24
PARTY_COUNT = 54
PARTY_SPRITE_ID_FIELD = 0x0E
PARTY_TABLE_LABEL = "player (party table)"
#: The record whose sprite id the engine resolved, filled in by the observer.
PARTY_PROBE_ADDRESS = 0x0801713C

#: The map's object array. TOOLKIT-024 proved the engine reads its COUNT from the
#: MapEntry field at +0x04 and its BASE from +0x14, and that the two upstream
#: names for those fields (`trigger_count_raw`, `scripts_pointer_raw`) are labels
#: rather than semantics. A NEW ACTOR means a new entry in this array, which on a
#: map whose slots are all occupied means re-emitting the array one element longer
#: and repointing the one field that names it.
MAP_ENTRY_STRIDE = 0x38
MAP_ENTRY_TABLE_ROM_OFFSET = 0x0008E2E0        # rom 0x0808E2E0, 452 records
MAP_OBJECT_COUNT_FIELD = 0x04
MAP_OBJECT_ARRAY_FIELD = 0x14
#: Map 102's own identity triple, used as a guard: the planner refuses if the
#: record it indexes is not the map it was measured against, so a wrong table
#: address cannot be read as a plausible-looking map.
NEW_ACTOR_MAP_EXPECTED = (1, 1, 3)

#: Where the new actor is authored. Map 102 is West City park: ten object slots,
#: all ten occupied, and not one placement-family actor. The placement is CLONED
#: from map 19 placement 6 rather than invented, so the flags, type selector and
#: behaviour descriptor are ones a retail 32x32 actor already runs with - which is
#: also what makes the frame-composition budget a known quantity instead of a
#: guess. Cloning the clone's own header and dropping its children keeps the new
#: record from pointing into another map's sub-objects.
#: Where the new actor is authored, in map pixels. Measured, not guessed: with
#: the actor at (320, 280) the observer reported its own screen position as
#: (231, -256), so the camera's top-left was (320-231, 280-(-256)) = (89, 536) and
#: the visible map region was x in [89, 329], y in [536, 696]. The actor was 256
#: pixels above the top edge. The player sits near the screen centre, so the save
#: spawns them around (209, 616); this position is just above and level with that.
NEW_ACTOR_MAP_INDEX = 102
#: One of map 102's three identical blue workers (sprite 69), file 0x078440.
NEW_ACTOR_CLONE_FILE_OFFSET = 0x00078440
NEW_ACTOR_SIBLING_FACTORY = 0x08017DA3
NEW_ACTOR_POSITION = (209, 580)

#: Map 102's own objects are the SIBLING family (factory 0x08017DA3), not
#: placements, and they are the park's NPCs. Cloning a placement - which is what
#: the first revision did - gives an actor that dispatches to a map-transition
#: script, and the runtime run showed exactly that: walking into it teleported the
#: player. The sibling layout is not the placement layout, so it is read on its
#: own offsets, all of which were measured from the ten records themselves:
#:
#:   +0x00 factory 0x08017DA3   +0x08 u32 position (low = x, high = y)
#:   +0x04 flags/data           +0x0C per-object data pointer
#:                              +0x10 SPRITE ID   +0x14 constant 1
#:                              +0x18 object pointer   +0x1C shared handler 0x0800A7A1
#:   record size 0x2C
#:
#: The sprite id was identified by rendering it: the ten records name sprites
#: 279, 36, 181, 261, 180, 294, 204, 69, 69 and 69, and those render as the park's
#: NPCs. The clone here is one of the three identical workers (sprite 69), so the
#: new NPC is a fourth one of a kind the map already builds three of, and the
#: original worker still stands beside it as the control.
NEW_ACTOR_SIBLING_POSITION_FIELD = 0x08
NEW_ACTOR_SIBLING_SPRITE_FIELD = 0x10
NEW_ACTOR_SIBLING_SIZE = 0x2C
NEW_ACTOR_RECORD_SIZE = 0x1C
ARRAY_OWNER = "sprite-new:object-array"
PLACEMENT_OWNER = "sprite-new:placement"

#: Palette and frame geometry, all measured from the donor's own records.
PALETTE_FILE_OFFSET = 0x0005652C
PALETTE_ENTRIES = 256
TRANSPARENT_INDEX = 0
CHROMA_KEY = (255, 0, 255)
FRAME_SIDE = 32
PIECE_X = -8
PIECE_Y = -24
#: shape 0 (square) and size 2 (32x32) in attribute 1, the 8bpp flag in
#: attribute 0, no flip. Copied from the donor's direction 0 piece.
PIECE_ATTRIBUTE = 0x80002000
ANIMATION_FRAME_COUNT = 2               # matches the donor's own animation
GRAPHICS_CONTAINER_KIND = sg.GRAPHICS_CONTAINER_KIND

#: The animations this identity carries, in slot order, as (sheet, slot). Slot 0
#: is the one the engine's own constructor selects, so the idle goes there; the
#: engine's state machine names neither, so the choice is recorded rather than
#: claimed.
CUI_SHEETS: tuple[tuple[str, int], ...] = (("stand", 0), ("walk", 1))

DOMAIN = "sprite_new_runtime"
METADATA_OWNER = "sprite-new:metadata"
GRAPHICS_OWNER = "sprite-new:graphics"


class SpriteNewError(ValueError):
    """An experiment input that cannot be honoured."""


# --- colour ------------------------------------------------------------------


def expand_channel(five: int) -> int:
    """The hardware's 5-to-8 bit expansion, the ONE decode this project uses."""
    return (five << 3) | (five >> 2)


def hardware_colour(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """The colour the hardware will display for one RGB888 source pixel.

    ``channel >> 3`` is exact for every Cui colour, including the zero-padded
    ``v << 3`` form a naive converter writes and the bit-replicated
    ``(v << 3) | (v >> 2)`` form the retail palette stores. Nothing is rounded.
    """
    return tuple(expand_channel(channel >> 3) for channel in rgb)


def read_cui_cell(sheet: Path, cell: int) -> list[tuple[int, int, int]]:
    """One 32x32 cell of a Cui sheet, row-major, as RGB triples."""
    from PIL import Image

    image = Image.open(sheet).convert("RGB")
    width, height = image.size
    if height != FRAME_SIDE or width % FRAME_SIDE:
        raise SpriteNewError(
            f"{sheet.name} is {width}x{height}; the measured Cui layout is one row "
            f"of {FRAME_SIDE}x{FRAME_SIDE} cells")
    columns = width // FRAME_SIDE
    if not 0 <= cell < columns:
        raise SpriteNewError(f"{sheet.name} has {columns} cells; {cell} is out of range")
    pixels = image.load()
    return [
        pixels[cell * FRAME_SIDE + x, y]
        for y in range(FRAME_SIDE)
        for x in range(FRAME_SIDE)
    ]


def cui_sheet_frames(sheet: Path) -> int:
    """How many FRAMES a Cui sheet holds: four direction cells per frame.

    CORRECTION to SPRITE-NEW-BOUNDARY-001, which recorded these sheets as a single
    direction. They are not. Each sheet is four direction cells per frame, in
    exactly the order the animation record stores them - slot ``d`` of frame ``f``
    lives at flat index ``f * 4 + d`` - so a sheet of ``4 * n`` cells is ``n``
    frames of four facings:

        block 4 cells = 1 frame, stand 8 = 2, hurt 12 = 3, walk 16 = 4,
        attack2 16 = 4

    Rendering the cells individually is what shows it: block's four cells are four
    different facings rather than four frames of one, and stand's eight are two
    frames of four. The first revision used a single cell for all four direction
    slots, which is why the runtime run showed a motionless stamp.
    """
    from PIL import Image

    width, height = Image.open(sheet).size
    if height != FRAME_SIDE or width % (FRAME_SIDE * sg.DIRECTION_COUNT):
        raise SpriteNewError(
            f"{sheet.name} is {width}x{height}; a Cui sheet must be a whole number "
            f"of four-cell frame groups")
    return (width // FRAME_SIDE) // sg.DIRECTION_COUNT


@dataclass(frozen=True, slots=True)
class PaletteAssignment:
    """The index every Cui colour takes, and the entries that had to be written."""

    indexed: bytes
    reused: int
    added: tuple[tuple[int, tuple[int, int, int]], ...]
    index_of_colour: dict

    @property
    def added_indices(self) -> tuple[int, ...]:
        return tuple(index for index, _ in self.added)


def assign_palette(palette_rgb, source_pixels, free_indices) -> PaletteAssignment:
    """Map Cui's RGB888 pixels onto object-palette indices.

    Index 0 is reserved for the chroma key, so black ARTWORK goes to the first
    non-zero entry that holds black rather than to the transparent index. A
    colour with no entry takes a free index, chosen as the free index whose
    current colour is nearest and then the lowest, so that if some undecoded
    consumer does draw it the visible change is as small as this experiment can
    make it.
    """
    by_colour: dict[tuple[int, int, int], int] = {}
    for index in range(1, PALETTE_ENTRIES):
        by_colour.setdefault(palette_rgb[index], index)

    remaining = sorted(set(free_indices))
    writes: list[tuple[int, tuple[int, int, int]]] = []
    index_of: dict[tuple[int, int, int], int] = {}
    out = bytearray()
    reused = 0
    for pixel in source_pixels:
        if pixel == CHROMA_KEY:
            out.append(TRANSPARENT_INDEX)
            continue
        display = hardware_colour(pixel)
        index = index_of.get(display)
        if index is None:
            index = by_colour.get(display)
            if index is not None:
                reused += 1
            else:
                if not remaining:
                    raise SpriteNewError(
                        f"no free object-palette entry for {display}; the "
                        "experiment will not quantise the artwork")
                index = min(
                    remaining,
                    key=lambda i: (
                        max(abs(palette_rgb[i][k] - display[k]) for k in range(3)),
                        i,
                    ),
                )
                remaining.remove(index)
                by_colour[display] = index
                writes.append((index, display))
            index_of[display] = index
        out.append(index)
    return PaletteAssignment(bytes(out), reused, tuple(sorted(writes)), index_of)


# --- record codecs -----------------------------------------------------------


def encode_registry(entries: list[int], new_entry_address: int) -> bytes:
    """The 297 canonical entries followed by the new identity's structure."""
    if len(entries) != REGISTRY_ENTRIES:
        raise SpriteNewError(f"registry has {len(entries)} entries, expected {REGISTRY_ENTRIES}")
    return struct.pack(f"<{REGISTRY_ENTRIES + 1}I", *entries, new_entry_address)


def encode_structure_many(donor_header: bytes,
                          animation_addresses) -> bytes:
    """The donor's 0x54-byte header with one pointer per animation slot.

    ``+0x00``'s low byte is the animation-array count: five engine sites read it
    with ``ldrb``, compare it against the index they want, load
    ``+0x54 + 4*index`` and null-test the element. So the header's count byte is
    REWRITTEN to match the array written here rather than inherited from a donor
    that carried a different number of slots - a count that disagrees with the
    array is a slot the engine will refuse to reach.
    """
    if len(donor_header) != DONOR_HEADER_SIZE:
        raise SpriteNewError(
            f"donor header is {len(donor_header)} bytes, expected {DONOR_HEADER_SIZE:#x}")
    count = len(animation_addresses)
    if not 1 <= count <= 23:
        raise SpriteNewError(
            f"{count} animation slots; the corpus carries 1..23 and the engine's "
            "accessors compare the count against small immediates")
    record = bytearray(donor_header)
    record[0] = count
    return bytes(record) + struct.pack(f"<{count}I", *animation_addresses)


def encode_structure(donor_header: bytes, animation_address: int) -> bytes:
    """The donor's 0x54-byte header with both animation slots repointed.

    The header is copied verbatim, including the four 16-byte blocks at
    ``+0x10..+0x4F`` whose meaning is unresolved, so the new identity inherits
    exactly the retail actor's per-direction data rather than an invented one.
    """
    if len(donor_header) != DONOR_HEADER_SIZE:
        raise SpriteNewError(
            f"donor header is {len(donor_header)} bytes, expected {DONOR_HEADER_SIZE:#x}")
    if donor_header[0] != ANIMATION_SLOT_COUNT:
        raise SpriteNewError(
            f"donor animation count is {donor_header[0]}, expected {ANIMATION_SLOT_COUNT}")
    return donor_header + struct.pack(f"<{ANIMATION_SLOT_COUNT}I", *[animation_address] * ANIMATION_SLOT_COUNT)


def encode_animation(frame_address: int) -> bytes:
    """Two frames, four direction cells each, every cell the same frame record."""
    cells = [frame_address] * (ANIMATION_FRAME_COUNT * sg.DIRECTION_COUNT)
    return struct.pack(f"<I{len(cells)}I", ANIMATION_FRAME_COUNT, *cells)


def encode_frame(container_address: int) -> bytes:
    """One 32x32 piece at the donor's own anchor, with the donor's attribute word."""
    box = struct.pack("<bbBB", PIECE_X, PIECE_Y, FRAME_SIDE, FRAME_SIDE)
    return (struct.pack("<I", 1) + box + box
            + struct.pack("<I", PIECE_ATTRIBUTE)
            + struct.pack("<I", container_address))


def encode_new_sibling(clone: bytes, sprite_id: int,
                       position: tuple[int, int]) -> bytes:
    """A new park-NPC record: the clone's whole shape, this identity, own spot.

    Everything but two fields is copied verbatim, including the per-object data
    pointer at ``+0x0C`` - which is what makes the new actor BEHAVE like the NPC
    it was cloned from, dialogue included, rather than merely wear its geometry.
    """
    if len(clone) != NEW_ACTOR_SIBLING_SIZE:
        raise SpriteNewError(
            f"the sibling clone is {len(clone)} bytes, expected "
            f"{NEW_ACTOR_SIBLING_SIZE:#x}")
    record = bytearray(clone)
    low, high = mp.encode_position(*position)
    struct.pack_into("<I", record, NEW_ACTOR_SIBLING_POSITION_FIELD,
                     (high << 16) | low)
    struct.pack_into("<I", record, NEW_ACTOR_SIBLING_SPRITE_FIELD, sprite_id)
    return bytes(record)


def encode_object_array(existing: list[int], new_pointer: int) -> bytes:
    """The map's object array, one element longer, every existing word verbatim."""
    return struct.pack(f"<{len(existing) + 1}I", *existing, new_pointer)


# --- planning ----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Experiment:
    """Everything the derivative contains, addresses included."""

    plan: object
    report: dict

    def output(self, base: bytes) -> bytes:
        return apply_plan(base, self.plan)


def _occupied(document, extra: tuple[OwnedRegion, ...]) -> tuple[OwnedRegion, ...]:
    """The reservation set every allocating domain shares, as graphics uses it."""
    occupied = [OwnedRegion(anchor.range, anchor.owner) for anchor in document.anchors]
    for reference in document.references:
        if not any(anchor.range.contains(reference.source) for anchor in document.anchors):
            occupied.append(
                OwnedRegion(reference.source_range, f"reference:{reference.target.value}")
            )
    occupied.extend(extra)
    return tuple(occupied)


def _free_palette_indices(sprites, identification, image: bytes) -> tuple[int, ...]:
    """Palette indices no actor-sprite graphic and no portrait draws.

    Deliberately conservative in the direction that matters: the union is taken
    over every decoded byte of both families, so a 4bpp graphic contributes both
    nibbles. That can only shrink the free list. The UI/HUD family is NOT included
    because it mixes background-palette full-screen images with OBJ graphics and
    its byte-union spans all 256 values, which would make the list empty; the
    runtime run's "no obvious graphics corruption" check is what covers the
    residual.
    """
    used: set[int] = set()
    for graphic in sprites.graphics():
        used.update(graphic.pixels)

    import logx_portrait_probe as portrait_probe
    from webfoot.formats import webfoot_lz

    for pointer in portrait_probe.portrait_pointers(image):
        container = webfoot_lz.unpack(image, pointer - 0x08000000)
        used.update(container.data)
    return tuple(i for i in range(1, PALETTE_ENTRIES) if i not in used)


def build_experiment(image: bytes, identification, sheet: Path, cell: int,
                     target: str = "placement") -> Experiment:
    """Plan the whole derivative against one verified canonical image."""
    sprites = load_actor_sprites(image, identification)
    profile = sprites.profile
    document = sprites.reference_document()

    # --- the registry must be published movable, or nothing here is justified
    registry_anchor = document.anchor(AnchorId(sprites.registry_identity))
    if registry_anchor.kind != "character_pointer_table":
        raise SpriteNewError(
            f"the registry anchor is kind {registry_anchor.kind!r}, not character_pointer_table")
    if registry_anchor.range.start.value != REGISTRY_FILE_OFFSET:
        raise SpriteNewError(
            f"the registry is not at 0x{REGISTRY_FILE_OFFSET:06X} in this image")
    if registry_anchor.range.size != REGISTRY_ENTRIES * 4:
        raise SpriteNewError("the registry extent is not 297 entries")
    if not registry_anchor.relocatable:
        raise SpriteNewError(
            "the registry is not published relocatable; its inbound surface is not "
            "fully expressed by the reference graph, so moving it is unjustified")
    registry_references = sprites.registry_references()
    if len(registry_references) != len(
        __import__("webfoot.graphics", fromlist=["x"]).CHARACTER_TABLE_REFERENCE_OFFSETS
    ):
        raise SpriteNewError(
            f"the registry has {len(registry_references)} published inbound words, "
            "which is not the measured set")

    entries = list(struct.unpack_from(
        f"<{REGISTRY_ENTRIES}I", image, REGISTRY_FILE_OFFSET))
    if entries[0] != 0x08000000 + DONOR_STRUCTURE_FILE_OFFSET:
        raise SpriteNewError("entry 0 is not the expected donor structure")
    donor_header = image[
        DONOR_STRUCTURE_FILE_OFFSET:DONOR_STRUCTURE_FILE_OFFSET + DONOR_HEADER_SIZE]

    # --- Cui, in palette indices: EVERY cell of every animation
    palette = sg.decode_palette(image, PALETTE_FILE_OFFSET)
    free_indices = _free_palette_indices(sprites, identification, image)

    graphic = sg.Graphic(offset=0, width=FRAME_SIDE, height=FRAME_SIDE,
                         colour_256=True, pixels=b"", packed_end=0)

    assigned = []
    for name, _slot in CUI_SHEETS:
        path = Path(sheet).parent / f"{name}.png"
        frames = cui_sheet_frames(path)
        cells = [
            assign_palette(palette.rgb, read_cui_cell(path, i), free_indices)
            for i in range(frames * sg.DIRECTION_COUNT)
        ]
        assigned.append((name, frames, cells))

    # Containers are 4-byte aligned in the canonical corpus and the decompressor
    # reads them as little-endian words, so each one is padded up to a word
    # boundary inside the single generated block rather than packed tight.
    container_parts: list[bytes] = []
    cell_offsets: list[tuple[int, int]] = []
    running = 0
    for _name, _frames, cells in assigned:
        for a in cells:
            payload = sg.encode_graphic_payload(
                graphic, a.indexed, kind=GRAPHICS_CONTAINER_KIND)
            cell_offsets.append((running, len(payload)))
            padded = payload + b"\xff" * ((-len(payload)) % 4)
            container_parts.append(padded)
            running += len(padded)
    container_payload = b"".join(container_parts)

    # Sizes first: every record names an address the allocator has not chosen yet,
    # so the block is laid out from its extents and filled afterwards.
    n_cells = sum(frames * sg.DIRECTION_COUNT for _n, frames, _c in assigned)
    animations_size = sum(4 + 16 * frames for _n, frames, _c in assigned)
    frames_size = n_cells * (8 + 12)
    structure_size = DONOR_HEADER_SIZE + 4 * len(assigned)
    META_TABLE = 0
    META_STRUCTURE = (REGISTRY_ENTRIES + 1) * 4
    META_ANIMATIONS = META_STRUCTURE + structure_size
    META_FRAMES = META_ANIMATIONS + animations_size
    META_SIZE = META_FRAMES + frames_size

    # --- allocations, all of them above EOF
    image_size = profile.generated_expansion.output_size
    requests = [
        AllocationRequest(
            AnchorId(GRAPHICS_OWNER), GRAPHICS_OWNER, len(container_payload), 4,
            kind=AllocationKind.GRAPHICS_CONTAINER,
            addressability=Addressability.EXPANDED_ONLY,
            evidence=(
                f"new {FRAME_SIDE}x{FRAME_SIDE} 8bpp Cui container, one identity's "
                "only payload; placed above EOF so this experiment exercises the "
                "new-identity write path rather than the shared canonical window")),
        AllocationRequest(
            AnchorId(METADATA_OWNER), METADATA_OWNER, META_SIZE, 4,
            kind=AllocationKind.SPRITE_IDENTITY_RECORD,
            evidence=(
                "one additional actor-sprite identity: the 298-entry registry plus "
                "its new character structure, animation record and frame record")),
    ]

    # A NEW ACTOR, for the run whose map has no free object slot. The map's own
    # object array is re-emitted one element longer and the new placement record
    # is authored beside it; both live above EOF and every existing array word
    # travels verbatim.
    new_actor = None
    if target == "new-actor":
        map_entry_at = (MAP_ENTRY_TABLE_ROM_OFFSET
                        + NEW_ACTOR_MAP_INDEX * MAP_ENTRY_STRIDE)
        zone, area, variation = (image[map_entry_at + 0x01],
                                 image[map_entry_at + 0x02],
                                 image[map_entry_at + 0x03])
        if (zone, area, variation) != NEW_ACTOR_MAP_EXPECTED:
            raise SpriteNewError(
                f"map {NEW_ACTOR_MAP_INDEX} is zone/area/variation "
                f"{zone}/{area}/{variation}, not {NEW_ACTOR_MAP_EXPECTED}; the map "
                "table this planner indexes is not the one it was measured against")
        count = image[map_entry_at + MAP_OBJECT_COUNT_FIELD]
        array_field = map_entry_at + MAP_OBJECT_ARRAY_FIELD
        array_addr = int.from_bytes(image[array_field:array_field + 4], "little")
        if not count or not 0x08000000 <= array_addr < 0x08000000 + len(image):
            raise SpriteNewError(
                f"map {NEW_ACTOR_MAP_INDEX} declares no readable object array "
                f"(count {count}, base 0x{array_addr:08X})")
        array_at = array_addr - 0x08000000
        existing = list(struct.unpack_from(f"<{count}I", image, array_at))
        for word in existing:
            if not 0x08000000 <= word < 0x08000000 + len(image):
                raise SpriteNewError(
                    f"the object array holds 0x{word:08X}, which is not a ROM pointer")
        clone = image[NEW_ACTOR_CLONE_FILE_OFFSET:
                      NEW_ACTOR_CLONE_FILE_OFFSET + NEW_ACTOR_SIBLING_SIZE]
        if len(clone) != NEW_ACTOR_SIBLING_SIZE:
            raise SpriteNewError("the sibling clone is short")
        factory = int.from_bytes(clone[0:4], "little")
        if factory != NEW_ACTOR_SIBLING_FACTORY:
            raise SpriteNewError(
                f"the clone at 0x{NEW_ACTOR_CLONE_FILE_OFFSET:06X} leads with "
                f"0x{factory:08X}, not the sibling factory "
                f"0x{NEW_ACTOR_SIBLING_FACTORY:08X}")
        clone_sprite = int.from_bytes(
            clone[NEW_ACTOR_SIBLING_SPRITE_FIELD:
                  NEW_ACTOR_SIBLING_SPRITE_FIELD + 4], "little")
        if not SPRITE_ID_FLOOR <= clone_sprite <= 306:
            raise SpriteNewError(
                f"the clone's +0x10 is {clone_sprite}, not a sprite id; the sibling "
                "layout this planner reads is not the one it was measured against")
        new_actor = {
            "map": NEW_ACTOR_MAP_INDEX,
            "map_entry_file_offset": map_entry_at,
            "zone_area_variation": [zone, area, variation],
            "array_field_file_offset": array_field,
            "array_old_file_offset": array_at,
            "array_old_rom_address": array_addr,
            "array_old_count": count,
            "array_existing_words": existing,
            "clone_file_offset": NEW_ACTOR_CLONE_FILE_OFFSET,
            "clone_bytes": clone,
            "clone_sprite": clone_sprite,
            "position": list(NEW_ACTOR_POSITION),
        }
        requests.append(AllocationRequest(
            AnchorId(ARRAY_OWNER), ARRAY_OWNER, 4 * (count + 1), 4,
            kind=AllocationKind.PLACEMENT_REFERENCE_ARRAY,
            addressability=Addressability.EXPANDED_ONLY,
            evidence=(
                f"map {NEW_ACTOR_MAP_INDEX}'s object array re-emitted one element "
                "longer so a genuinely new actor can be added; every existing word "
                "is copied verbatim and the array cannot grow in place because the "
                "next structure follows it")))
        requests.append(AllocationRequest(
            AnchorId(PLACEMENT_OWNER), PLACEMENT_OWNER, len(clone), 4,
            kind=AllocationKind.SPRITE_IDENTITY_RECORD,
            evidence=(
                "one new map placement record: the actor entity that carries the "
                "new identity, cloned whole from a retail 32x32 placement - flags, "
                "type selector, behaviour descriptor and children - so its shape is "
                "one the engine already builds")))

    allocations = allocate(profile, requests, occupied=_occupied(document, ()))
    by_owner = {allocation.request.owner: allocation for allocation in allocations}

    meta = by_owner[METADATA_OWNER]
    graphics = by_owner[GRAPHICS_OWNER]
    for allocation in allocations:
        if not allocation.is_expanded:
            raise SpriteNewError(
                f"{allocation.request.owner} landed inside the canonical image")

    meta_base = meta.range.start.value
    container_at = graphics.range.start.value
    container_addr = graphics.rom_address

    registry_addr = meta.rom_address
    graphics_addr = graphics.rom_address

    def rom(file_offset: int) -> int:
        return FileOffset(file_offset).to_gba_address(image_size).raw

    structure_at = meta_base + META_STRUCTURE
    structure_addr = rom(structure_at)

    block = bytearray([profile.generated_expansion.padding_byte]) * META_SIZE
    block[META_TABLE:META_TABLE + (REGISTRY_ENTRIES + 1) * 4] = encode_registry(
        entries, structure_addr)

    # Frames first: each cell gets its own 32x32 record naming that cell's own
    # container, in the order f * 4 + d the animation record stores them in.
    cell_index = 0
    frame_addresses: list[list[int]] = []
    for _name, frames, cells in assigned:
        per_sheet = []
        for _cell in cells:
            offset, _length = cell_offsets[cell_index]
            at = meta_base + META_FRAMES + 20 * cell_index
            payload = encode_frame(graphics_addr + offset)
            block[at - meta_base:at - meta_base + 20] = payload
            per_sheet.append(rom(at))
            cell_index += 1
        frame_addresses.append(per_sheet)

    # Then one animation per sheet, and the structure pointing at them.
    animation_addresses = []
    cursor = META_ANIMATIONS
    animation_rows = []
    for (name, frames, _cells), addresses in zip(assigned, frame_addresses):
        count = len(addresses)
        if count != frames * sg.DIRECTION_COUNT:
            raise SpriteNewError(f"{name}: {count} cells for {frames} frames")
        payload = struct.pack(f"<I{count}I", frames, *addresses)
        block[cursor:cursor + len(payload)] = payload
        animation_addresses.append(rom(meta_base + cursor))
        animation_rows.append({"sheet": name, "frame_count": frames,
                               "cells": count,
                               "rom_address": f"0x{rom(meta_base + cursor):08X}"})
        cursor += len(payload)

    block[META_STRUCTURE:META_STRUCTURE + structure_size] = encode_structure_many(
        donor_header, animation_addresses)
    structure_at = meta_base + META_STRUCTURE
    animation_at = meta_base + META_ANIMATIONS
    frame_at = meta_base + META_FRAMES
    animation_addr = animation_addresses[0] if animation_addresses else 0
    frame_addr = rom(frame_at)
    container_addr = graphics_addr

    # --- the writes
    changes = [
        ByteChange(meta_base, bytes([profile.generated_expansion.padding_byte]) * META_SIZE,
                   bytes(block), METADATA_OWNER,
                   "new sprite identity: registry, structure, animation and frame"),
        ByteChange(container_at,
                   bytes([profile.generated_expansion.padding_byte]) * len(container_payload),
                   container_payload, GRAPHICS_OWNER,
                   "new sprite identity: the Cui graphics container"),
    ]
    registry_rewrites = []
    for reference in registry_references:
        source = reference.source.value
        old = image[source:source + 4]
        if old != (REGISTRY_FILE_OFFSET + 0x08000000).to_bytes(4, "little"):
            raise SpriteNewError(
                f"the published registry reference at 0x{source:06X} does not hold "
                "the canonical registry address")
        new = FileOffset(registry_addr - 0x08000000).to_gba_address(image_size).raw
        encoded = new.to_bytes(4, "little")
        changes.append(ByteChange(
            source, old, encoded, METADATA_OWNER,
            f"registry relocation: the word at 0x{source:06X} repointed"))
        registry_rewrites.append({
            "file_offset": f"0x{source:06X}",
            "file_offset_int": source,
            "old_rom_address": f"0x{int.from_bytes(old, 'little'):08X}",
            "new_rom_address": f"0x{new:08X}",
        })

    if target == "placement":
        placement_field = CONTROLLED_PLACEMENT_FILE_OFFSET + CONTROLLED_PLACEMENT_ID_FIELD
        placement_old = image[placement_field:placement_field + 4]
        if placement_old != CONTROLLED_PLACEMENT_ID_OLD.to_bytes(4, "little"):
            raise SpriteNewError(
                f"the controlled actor at 0x{placement_field:06X} does not hold sprite id "
                f"{CONTROLLED_PLACEMENT_ID_OLD}")
        changes.append(ByteChange(
            placement_field, placement_old, NEW_SPRITE_ID.to_bytes(4, "little"),
            CONTROLLED_PLACEMENT_LABEL,
            f"controlled actor repointed from sprite {CONTROLLED_PLACEMENT_ID_OLD} to "
            f"the new identity {NEW_SPRITE_ID}"))
        controlled = {
            "mode": "placement",
            "label": CONTROLLED_PLACEMENT_LABEL,
            "file_offset": f"0x{CONTROLLED_PLACEMENT_FILE_OFFSET:06X}",
            "id_field": f"0x{CONTROLLED_PLACEMENT_ID_FIELD:02X}",
            "id_field_file_offset": f"0x{placement_field:06X}",
            "old_sprite_id": CONTROLLED_PLACEMENT_ID_OLD,
            "new_sprite_id": NEW_SPRITE_ID,
            "in_map_control": (
                "map 19 placements 7 to 10 keep sprite "
                f"{CONTROLLED_PLACEMENT_ID_OLD}"),
        }
    elif target == "player":
        # Every party record that currently names a real sprite id, so whichever
        # character the saved game has active resolves to the new identity. A
        # record whose +0x0E is zero or below the id floor is left alone: sprite
        # ids 0..9 route back into the party path and repointing one would be a
        # recursion, not a sprite.
        records = []
        for index in range(PARTY_COUNT):
            field = (PARTY_TABLE_FILE_OFFSET + index * PARTY_STRIDE
                     + PARTY_SPRITE_ID_FIELD)
            old = image[field:field + 2]
            old_id = int.from_bytes(old, "little")
            if not SPRITE_ID_FLOOR <= old_id <= 306:
                continue
            records.append((index, field, old_id))
        if not records:
            raise SpriteNewError("the party table names no real sprite id")
        for index, field, old_id in records:
            changes.append(ByteChange(
                field, image[field:field + 2], NEW_SPRITE_ID.to_bytes(2, "little"),
                PARTY_TABLE_LABEL,
                f"party record {index} repointed from sprite {old_id} to the new "
                f"identity {NEW_SPRITE_ID}"))
        controlled = {
            "mode": "player",
            "label": PARTY_TABLE_LABEL,
            "party_table_file_offset": f"0x{PARTY_TABLE_FILE_OFFSET:06X}",
            "sprite_id_field": f"0x{PARTY_SPRITE_ID_FIELD:02X}",
            "records_repointed": len(records),
            "records": [
                {"index": index, "file_offset": f"0x{field:06X}",
                 "old_sprite_id": old_id, "new_sprite_id": NEW_SPRITE_ID}
                for index, field, old_id in records
            ],
            "resolver_probe": f"0x{PARTY_PROBE_ADDRESS:08X}",
            "in_map_control": (
                "every other actor on the map keeps its own identity; only the "
                "party sprite-id field moves"),
        }
    elif target == "new-actor":
        # A genuinely new actor: the map's object array one element longer, and a
        # new placement record carrying the new identity. Every existing array word
        # is copied verbatim, so the ten actors map 102 already builds are
        # unchanged; the only canonical word that moves is the field naming the
        # array, and the old array bytes stay where they are.
        array_alloc = by_owner[ARRAY_OWNER]
        placement_alloc = by_owner[PLACEMENT_OWNER]
        placement_at = placement_alloc.range.start.value
        placement_addr = placement_alloc.rom_address
        array_at_new = array_alloc.range.start.value
        array_addr_new = array_alloc.rom_address

        placement_payload = encode_new_sibling(
            new_actor["clone_bytes"], NEW_SPRITE_ID, NEW_ACTOR_POSITION)
        array_payload = encode_object_array(
            new_actor["array_existing_words"], placement_addr)

        pad = profile.generated_expansion.padding_byte
        changes.append(ByteChange(
            placement_at, bytes([pad]) * len(placement_payload), placement_payload,
            PLACEMENT_OWNER,
            f"new actor for map {NEW_ACTOR_MAP_INDEX}: a childless placement record "
            f"carrying the new identity {NEW_SPRITE_ID}"))
        changes.append(ByteChange(
            array_at_new, bytes([pad]) * len(array_payload), array_payload,
            ARRAY_OWNER,
            f"map {NEW_ACTOR_MAP_INDEX} object array re-emitted with "
            f"{new_actor['array_old_count'] + 1} slots"))

        # The COUNT, which is what actually makes the extra slot visible. The
        # engine walks `MapEntry+0x04` (ldrb) indexing `MapEntry+0x14` by
        # `index * 4`, with no sentinel and no terminator, so an array that grew
        # without its count is an array the engine still reads at its old length.
        # Measured: without this write the new actor never constructs and the
        # placement constructor is never called at all.
        count_field = new_actor["map_entry_file_offset"] + MAP_OBJECT_COUNT_FIELD
        changes.append(ByteChange(
            count_field, image[count_field:count_field + 1],
            bytes([new_actor["array_old_count"] + 1]), ARRAY_OWNER,
            f"map {NEW_ACTOR_MAP_INDEX} object count "
            f"{new_actor['array_old_count']} -> {new_actor['array_old_count'] + 1}"))

        # Every word-aligned word in the image that names the old array, so the
        # repoint is a census rather than an assumption about which field owns it.
        needle = new_actor["array_old_rom_address"].to_bytes(4, "little")
        holders = [o for o in range(0, len(image) - 3, 4)
                   if image[o:o + 4] == needle]
        if not holders:
            raise SpriteNewError("nothing in the image names the old object array")
        array_rewrites = []
        for holder in holders:
            old = image[holder:holder + 4]
            encoded = FileOffset(array_addr_new - 0x08000000).to_gba_address(
                image_size).raw.to_bytes(4, "little")
            changes.append(ByteChange(
                holder, old, encoded, ARRAY_OWNER,
                f"object-array relocation: the word at 0x{holder:06X} repointed"))
            array_rewrites.append({
                "file_offset": f"0x{holder:06X}",
                "old_rom_address": f"0x{new_actor['array_old_rom_address']:08X}",
                "new_rom_address": f"0x{array_addr_new:08X}",
                "is_the_map_entry_field":
                    holder == new_actor["array_field_file_offset"],
            })

        controlled = {
            "mode": "new-actor",
            "label": f"new actor on map {NEW_ACTOR_MAP_INDEX}",
            "map_index": NEW_ACTOR_MAP_INDEX,
            "map_entry_file_offset": f"0x{new_actor['map_entry_file_offset']:06X}",
            "map_zone_area_variation": new_actor["zone_area_variation"],
            "array": {
                "old_file_offset": f"0x{new_actor['array_old_file_offset']:06X}",
                "old_rom_address": f"0x{new_actor['array_old_rom_address']:08X}",
                "old_count": new_actor["array_old_count"],
                "new_file_offset": f"0x{array_at_new:06X}",
                "new_rom_address": f"0x{array_addr_new:08X}",
                "new_count": new_actor["array_old_count"] + 1,
                "count_field_file_offset": (
                    f"0x{new_actor['map_entry_file_offset'] + MAP_OBJECT_COUNT_FIELD:06X}"),
                "count_field_old": new_actor["array_old_count"],
                "count_field_new": new_actor["array_old_count"] + 1,
                "existing_words_verbatim": True,
                "references_rewritten": array_rewrites,
            },
            "placement": {
                "file_offset": f"0x{placement_at:06X}",
                "rom_address": f"0x{placement_addr:08X}",
                "size": len(placement_payload),
                "cloned_from": f"0x{NEW_ACTOR_CLONE_FILE_OFFSET:06X}",
                "cloned_sprite_id": new_actor["clone_sprite"],
                "sprite_id": NEW_SPRITE_ID,
                "position": list(NEW_ACTOR_POSITION),
            },
            "what_changed_in_the_retail_image": (
                "one word per reference to the old object array; every existing "
                "array word, every existing object and every sprite is untouched"),
        }
    else:
        raise SpriteNewError(f"unknown target {target!r}")

    # Every palette entry the artwork needed, merged across all cells: a cell
    # that needs a colour another cell already took reuses the same index, so the
    # union is the whole set this identity requires.
    added: dict[int, tuple[int, int, int]] = {}
    reused_colours = set()
    for _name, _frames, cells in assigned:
        for a in cells:
            for index, colour in a.added:
                added[index] = colour
            reused_colours.update(a.index_of_colour)

    palette_writes = []
    for index in sorted(added):
        colour = added[index]
        offset = PALETTE_FILE_OFFSET + 2 * index
        old = image[offset:offset + 2]
        word = sg.pack_gba_colour(*colour)
        changes.append(ByteChange(
            offset, old, word.to_bytes(2, "little"), METADATA_OWNER,
            f"new object-palette entry {index} for the Cui colour {colour}"))
        palette_writes.append({
            "index": index,
            "file_offset": f"0x{offset:06X}",
            "old_word": f"0x{int.from_bytes(old, 'little'):04X}",
            "new_word": f"0x{word:04X}",
            "colour": list(colour),
            "old_colour": list(palette.rgb[index]),
        })

    generated_image = GeneratedImage(
        output_size=image_size,
        padding_byte=profile.generated_expansion.padding_byte,
        expansion_range=RomRange(FileOffset(len(image)), image_size - len(image)),
        expansion_evidence=profile.generated_expansion.evidence,
        allocated_spans=tuple(allocation.range for allocation in allocations),
    )
    # The container has no canonical source - it did not exist - so the range
    # recorded is the field that names it: the new piece's own ``+0x08`` word,
    # which lives in this same batch's metadata span. That is the case
    # `pointer_offset` documents for a span referenced only from a structure the
    # build itself materializes.
    container_pointer_field = frame_at + 8 + 8
    generated_allocations = [
        meta.generated_allocation_provenance(
            domain=DOMAIN, resource=METADATA_OWNER,
            pointer_offset=min(r.source.value for r in registry_references),
            source_range=registry_anchor.range),
        graphics.generated_allocation_provenance(
            domain=DOMAIN, resource=GRAPHICS_OWNER,
            pointer_offset=container_pointer_field,
            source_range=RomRange(FileOffset(container_pointer_field), 4)),
    ]
    if new_actor is not None:
        generated_allocations.append(
            by_owner[ARRAY_OWNER].generated_allocation_provenance(
                domain=DOMAIN, resource=ARRAY_OWNER,
                pointer_offset=new_actor["array_field_file_offset"],
                source_range=RomRange(
                    FileOffset(new_actor["array_old_file_offset"]),
                    4 * new_actor["array_old_count"])))
        generated_allocations.append(
            by_owner[PLACEMENT_OWNER].generated_allocation_provenance(
                domain=DOMAIN, resource=PLACEMENT_OWNER,
                pointer_offset=new_actor["array_field_file_offset"],
                source_range=RomRange(
                    FileOffset(new_actor["array_old_file_offset"]), 4)))
    generated_allocations = tuple(generated_allocations)
    plan = plan_changes(
        image, changes, profile_id=profile.id, base_sha256=profile.sha256,
        generated_image=generated_image,
        generated_allocations=generated_allocations)

    report = {
        "ticket": "SPRITE-NEW-RUNTIME-001",
        "base_sha256": profile.sha256,
        "new_sprite_id": NEW_SPRITE_ID,
        "registry": {
            "canonical_file_offset": f"0x{REGISTRY_FILE_OFFSET:06X}",
            "canonical_entries": REGISTRY_ENTRIES,
            "new_entries": REGISTRY_ENTRIES + 1,
            "new_file_offset": f"0x{registry_addr - 0x08000000:06X}",
            "new_rom_address": f"0x{registry_addr:08X}",
            "new_size": (REGISTRY_ENTRIES + 1) * 4,
            "references_rewritten": registry_rewrites,
            "dropped_entry_count": 0,
        },
        "allocations": [allocation.to_json() for allocation in allocations],
        "records": {
            "structure": {"file_offset": f"0x{structure_at:06X}",
                          "rom_address": f"0x{structure_addr:08X}",
                          "size": structure_size,
                          "cloned_from": f"0x{DONOR_STRUCTURE_FILE_OFFSET:06X}",
                          "animation_slots": len(assigned)},
            "animations": animation_rows,
            "frames": {"file_offset": f"0x{frame_at:06X}",
                       "rom_address": f"0x{frame_addr:08X}",
                       "count": n_cells,
                       "size": frames_size,
                       "per_cell": 8 + 12,
                       "order": "cell i of a sheet is frame_index * 4 + direction"},
            "container": {"file_offset": f"0x{container_at:06X}",
                          "rom_address": f"0x{container_addr:08X}",
                          "packed_size": len(container_payload),
                          "count": n_cells,
                          "kind": GRAPHICS_CONTAINER_KIND,
                          "declared_size": FRAME_SIDE * FRAME_SIDE,
                          "piece_attribute": f"0x{PIECE_ATTRIBUTE:08X}"},
        },
        "controlled_actor": controlled,
        "palette": {
            "transparent_index": TRANSPARENT_INDEX,
            "chroma_key": list(CHROMA_KEY),
            "colours": len(reused_colours),
            "entries_added_count": len(palette_writes),
            "entries_added": palette_writes,
            "quantised": False,
            "free_indices_considered": list(free_indices),
        },
        "cui": {"sheet": sheet.name, "cell": cell, "side": FRAME_SIDE},
    }
    return Experiment(plan=plan, report=report)


# --- verification ------------------------------------------------------------


def verify(image: bytes, report: dict) -> dict:
    """Re-read the emitted image and resolve the new identity the way the engine does.

    This is the strongest check available without an emulator: it walks the
    registry entry the ENGINE would compute, then the structure, the animation,
    the frame and the container, and decodes the pixels back.
    """
    image_size = len(image)
    registry_file = int(report["registry"]["new_file_offset"], 16)
    entry_offset = registry_file + 4 * (report["new_sprite_id"] - SPRITE_ID_FLOOR)
    structure_addr = int.from_bytes(image[entry_offset:entry_offset + 4], "little")
    structure_file = structure_addr - 0x08000000

    slots = image[structure_file]
    animations = [
        int.from_bytes(image[structure_file + 0x54 + 4 * i:
                             structure_file + 0x58 + 4 * i], "little")
        for i in range(slots)
    ]
    animation_file = animations[0] - 0x08000000
    frame_count = int.from_bytes(image[animation_file:animation_file + 4], "little")
    cells = [
        int.from_bytes(image[animation_file + 4 + 4 * i:
                             animation_file + 8 + 4 * i], "little")
        for i in range(frame_count * sg.DIRECTION_COUNT)
    ]
    unique_cells = sorted(set(cells))
    frame_file = cells[0] - 0x08000000
    piece_count = int.from_bytes(image[frame_file:frame_file + 4], "little")
    min_x, min_y, width, height = struct.unpack_from("<bbBB", image, frame_file + 4)
    piece = frame_file + 8
    px, py, d0, d1 = struct.unpack_from("<bbBB", image, piece)
    attribute = int.from_bytes(image[piece + 4:piece + 8], "little")
    container_addr = int.from_bytes(image[piece + 8:piece + 12], "little")

    decoded = sg.decode_graphic(image, container_addr - 0x08000000, d0, d1,
                                colour_256=bool(attribute & 0x2000))
    declared = int.from_bytes(
        image[container_addr - 0x08000000 + 4:container_addr - 0x08000000 + 8],
        "little")
    kind = int.from_bytes(
        image[container_addr - 0x08000000:container_addr - 0x08000000 + 4], "little")
    return {
        "registry_file_offset": f"0x{registry_file:06X}",
        "registry_new_entry_file_offset": f"0x{entry_offset:06X}",
        "structure_rom_address": f"0x{structure_addr:08X}",
        "structure_animation_slots": slots,
        "animation_rom_addresses": [f"0x{a:08X}" for a in animations],
        "animation_frame_count": frame_count,
        "animation_cells": len(cells),
        "distinct_cells": len(unique_cells),
        "all_cells_identical": len(unique_cells) == 1,
        "frame_rom_address": f"0x{cells[0]:08X}",
        "frame_piece_count": piece_count,
        "frame_box": [min_x, min_y, width, height],
        "piece": {"x": px, "y": py, "dim0": d0, "dim1": d1,
                  "attribute": f"0x{attribute:08X}",
                  "colour_256": bool(attribute & 0x2000),
                  "shape": (attribute >> 14) & 3,
                  "size": (attribute >> 30) & 3},
        "container_rom_address": f"0x{container_addr:08X}",
        "container_kind": kind,
        "container_declared_size": declared,
        "container_declared_matches_piece": declared == d0 * d1,
        "decoded_pixels": len(decoded.pixels),
        "distinct_indices": len(set(decoded.pixels)),
        "transparent_pixels": sum(1 for p in decoded.pixels if p == TRANSPARENT_INDEX),
        "image_size": image_size,
    }


# --- CLI ---------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True, help="the canonical image")
    parser.add_argument("--out", help="derivative image to write")
    parser.add_argument("--manifest", help="write the experiment report here")
    parser.add_argument(
        "--sheet", required=True,
        help="a Cui sheet PNG; the artwork is a private research input and is "
             "not tracked in this repository")
    parser.add_argument("--cell", type=int, default=0)
    parser.add_argument("--target", choices=("placement", "player", "new-actor"),
                        default="placement",
                        help="which actor carries the new identity")
    parser.add_argument("--verify", action="store_true",
                        help="re-read the emitted image and resolve the new identity")
    args = parser.parse_args(argv)

    catalog = RomProfileCatalog.load(str(_REPO / "config" / "roms.yaml"))
    rom_path = Path(args.rom)
    image = rom_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != CANONICAL_SHA256:
        print("refusing: the input is not the canonical image this experiment "
              "was measured against")
        return 2
    identification = identify_rom(rom_path, catalog)
    experiment = build_experiment(image, identification, Path(args.sheet), args.cell,
                                 target=args.target)

    if args.out:
        emit_image(rom_path, args.out, experiment.plan,
                   manifest_path=args.manifest)
    out_bytes = experiment.output(image)
    report = dict(experiment.report)
    report["output_sha256"] = hashlib.sha256(out_bytes).hexdigest()
    report["output_size"] = len(out_bytes)
    if args.verify:
        report["resolved"] = verify(out_bytes, report)
    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
