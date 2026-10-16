"""Swap a character's actor sprites, or a dialogue portrait, in a friend image.

WHAT THIS IS. The reusable engine behind the friend chain's graphics swap. Give it a base
image, one PNG per populated animation slot, and optionally a PNG for a portrait slot, and it
produces a NEW image and never writes the source. `tools/webfoot/character_swap.py` is the
invocable front end, driven by a JSON spec. The ticket that first needed this was
FRIEND-V3-TULMA-GRAPHICS-001, which is why one donor's geometry is named as a default.

TWO PAYLOAD FORMATS, AND WHY THE DIFFERENCE COST A RUNTIME SESSION. An actor-sprite container
holds swizzled 8x8 tiles. A dialogue portrait container holds a LINEAR raster. Decode
(unswizzle) then re-encode (swizzle) round trips byte-exactly, so a writer that treats a
portrait as tiles passes its own decode-then-compare check while putting noise on the screen.
That is why `plan_portrait` packs straight and compares the raw payload, and why the format is
settled against retail art in the integration tests rather than against this module's encoder,
which cannot see an assumption it shares.

TARGET IDENTITY, AND THE TRAP THIS AVOIDS. In the foundation the only appearance record whose
label reads `Bulma` is record 22, which is retail CHI-CHI. Retail BULMA is record 20, labelled
`Tulma` there. Nothing here keys on a label: a target is a sprite id and a portrait slot, and a
sprite's run index in the registry is its id minus ten. For the donor this was measured on,
both are address-identical in the canonical image and in the foundation.

WHAT IS WRITTEN, AND WHY SO LITTLE. Each supplied sheet is retail Bulma's own art
recoloured: cropped to the 16-wide window at x=8 of each 32x32 cell it reproduces the
donor frame's silhouette exactly (union equals intersection on all 32 frames), and every
colour it uses is already carried by the object palette at the hardware 5-bit resolution.
So the write is pixels only. No frame, piece, animation, anchor, composition size or
palette entry changes; a container's bytes move only when the re-encoded payload does not
fit the extent it already occupies. The palette is left byte-identical on purpose: it is
shared with every other actor and every portrait, and
`docs/research/GRAPHICS_PIXEL_OVERRIDE.md` records that an override changes indices,
never the palette.

PLACEMENT RULE. A re-encoded payload is written in place when it fits the container's
measured packed extent; otherwise it is appended above the end of the image and the one
word that names it is rewritten - the piece's `+0x08` for a sprite container, the array
slot for a portrait. An appended payload leaves the bytes it replaces untouched, so a
reference this writer did not discover still reaches intact art. An in-place payload
overwrites the region it occupied, which is why `verify` confines the diff to the spans
this report attributes to a named owner.

WHY NOT `write.plan_changes`. It requires every change to lie inside the base image, so it
cannot express an append, and its generated-image path is canonical-plus-16-MiB. The
guards that matter are kept here: a stale-base check per change, a non-overlap check, and
a post-write assertion that the output differs from the base only inside spans this
report attributes to a named owner.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

from tools.webfoot.formats import rgb_png
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz as wl

#: A structure's animation-pointer array, count-bounded, begins at +0x54
#: (PROJECT_STATE.md "Sprite definitions and animations").
ANIMATION_ARRAY_OFFSET = 0x54
#: Sprite ids run 10..306, so a structure's run index in the registry is id - 10.
SPRITE_ID_BASE = 10
#: The planner's chroma key for a hole (docs/project-format.md).
CHROMA_KEY = (255, 0, 255)

#: PINMAP-04. The profile every read here defaults to, and the three names that
#: carry it. The addresses themselves are the profile's declaration: no target
#: address is spelled in this module, and the planner's own reads take their
#: addresses from the layout object they are handed, never from these names.
_CANONICAL_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: The compat names remain importable because `tools/research/apply_tulma_graphics.py`
#: re-exports them and two modules that import that one at collection time read them.
#: They are resolved on access rather than at import so a packaged profile this module
#: cannot read fails at the reader that asked for an address, not at collection for
#: every module that merely imports this one.
_DERIVED_LAYOUT_NAMES = ("REGISTRY_TABLE_ADDRESS", "OBJECT_PALETTE_ADDRESS",
                         "PORTRAIT_ARRAY_ADDRESS")


def _packaged_layout():
    """The packaged profile's actor-sprite layout, through the capability gate.

    The same shape `map_render.canonical_profile` uses, one capability over: the
    profile is the packaged catalog's entry and not a second copy of it. The import
    is inside the call because `capability` imports `profile`.
    """
    from .capability import Capability, packaged_contract
    layout = packaged_contract(
        _CANONICAL_PROFILE_ID, Capability.ACTOR_SPRITES
    ).actor_sprites
    if layout is None:
        raise SpriteSwapError(
            f"packaged profile {_CANONICAL_PROFILE_ID!r} declares no actor_sprites "
            "layout, so no default target address exists"
        )
    return layout


def __getattr__(name: str) -> int:
    if name in _DERIVED_LAYOUT_NAMES:
        layout = _packaged_layout()
        return {
            "REGISTRY_TABLE_ADDRESS": layout.character_table_address,
            "OBJECT_PALETTE_ADDRESS": layout.object_palette_address,
            "PORTRAIT_ARRAY_ADDRESS": layout.portrait_table_address,
        }[name].raw
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class SpriteGeometry(NamedTuple):
    """The frame rectangle a donor's containers are proven at.

    Every structural fact a write depends on is asserted against this rather than assumed,
    so a donor with a different frame shape is refused instead of written wrongly.
    """

    frame_width: int
    frame_height: int
    cell_side: int
    crop_x: int
    frame_anchor: tuple[int, int]
    composition_size: int


class SheetSlot(NamedTuple):
    """One populated animation slot, the sheet that fills it, and its frames per facing."""

    slot: int
    sheet: str
    frames_per_facing: int


#: Every donor measured so far is one 16x32 piece at anchor (0,-24), and 16x32 is exactly
#: the composition size the structure declares (+0x02 = 0x200). A piece's stored dim_0/dim_1
#: are pixel extents, not tile counts (the engine halves dim_0 to centre an OBJ).
DONOR_GEOMETRY = SpriteGeometry(frame_width=16, frame_height=32, cell_side=32, crop_x=8,
                                frame_anchor=(0, -24), composition_size=0x200)


class SpriteSwap(NamedTuple):
    """Which character to redraw, from which sheets, at which geometry."""

    sprite_id: int
    slots: tuple[SheetSlot, ...]
    geometry: SpriteGeometry = DONOR_GEOMETRY

    @property
    def character_index(self) -> int:
        return self.sprite_id - SPRITE_ID_BASE


class PortraitSwap(NamedTuple):
    """Which portrait slot to redraw, from which PNG, at which side."""

    slot: int
    png: str
    side: int = 64


class SpriteSwapError(ValueError):
    """Raised when a guard refuses rather than writing an unproven byte."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_offset(address: int, size: int) -> int:
    """A GBA ROM address as a file offset, through the window the SDK uses."""
    offset = address - 0x08000000
    if not 0 <= offset < size:
        raise SpriteSwapError(f"address {address:#010x} is outside a {size}-byte image")
    return offset


def read_u32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise SpriteSwapError(f"word at {offset:#x} runs past the image")
    return int.from_bytes(data[offset:offset + 4], "little")


# --- palette --------------------------------------------------------------------------


def palette_indices(
    data: bytes, palette_offset: int
) -> dict[tuple[int, int, int], tuple[int, ...]]:
    """5-bit colour -> the palette indices that carry it, in index order.

    Compared at 5-bit resolution because that is the hardware's own: the sheets state a
    colour as ``v << 3`` and the ROM states it as ``(v << 3) | (v >> 2)``, and both are
    the same BGR555 word.
    """
    table: dict[tuple[int, int, int], list[int]] = {}
    for index in range(sg.PALETTE_ENTRIES):
        word = data[palette_offset + 2 * index] | (data[palette_offset + 2 * index + 1] << 8)
        table.setdefault(((word & 31), (word >> 5) & 31, (word >> 10) & 31), []).append(index)
    return {key: tuple(value) for key, value in table.items()}


def index_for_colour(
    colour: tuple[int, int, int], table: dict[tuple[int, int, int], tuple[int, ...]]
) -> int:
    """The palette index a supplied colour means, refusing any colour not already there.

    The chroma key is a hole. A colour carried by several indices resolves to the lowest
    index that is not the transparent key: only ``(0,0,0)`` is ambiguous in this palette
    (indices 0 and 1), and index 0 is the hardware's transparent index, so black means
    index 1. Any other ambiguity is refused rather than guessed.
    """
    if colour == CHROMA_KEY:
        return sg.TRANSPARENT_INDEX
    candidates = table.get((colour[0] >> 3, colour[1] >> 3, colour[2] >> 3))
    if not candidates:
        raise SpriteSwapError(
            f"colour {colour} is not in the object palette; this writer adds no entry, so "
            "the art must use colours the image already carries"
        )
    if len(candidates) == 1:
        return candidates[0]
    visible = [index for index in candidates if index != sg.TRANSPARENT_INDEX]
    if len(visible) != 1:
        raise SpriteSwapError(
            f"colour {colour} is carried by indices {candidates} and no single visible "
            "index chooses between them"
        )
    return visible[0]


def raster_from_png(
    path: Path, table: dict[tuple[int, int, int], tuple[int, ...]],
    width: int, height: int, *, cell: int | None = None,
    geometry: SpriteGeometry = DONOR_GEOMETRY,
) -> bytes:
    """One PNG, or one cropped cell of a sheet, as linear palette indices, row major."""
    pixels, png_width, png_height, alpha = rgb_png.decode_truecolour(path.read_bytes())
    if alpha is not None and any(value != 255 for value in alpha):
        raise SpriteSwapError(
            f"{path.name} has a partly transparent pixel; a sprite pixel is one palette "
            "index, so this engine takes the chroma key as the hole rather than alpha"
        )
    if cell is None:
        if (png_width, png_height) != (width, height):
            raise SpriteSwapError(
                f"{path.name} is {png_width}x{png_height}; expected {width}x{height}"
            )
        left = 0
    else:
        side = geometry.cell_side
        if png_height != side or png_width % side:
            raise SpriteSwapError(
                f"{path.name} is {png_width}x{png_height}; expected one row of "
                f"{side}x{side} cells"
            )
        if not 0 <= cell < png_width // side:
            raise SpriteSwapError(f"{path.name} has no cell {cell}")
        left = cell * side + geometry.crop_x
    out = bytearray()
    for y in range(height):
        for x in range(width):
            at = (y * png_width + left + x) * 3
            out.append(index_for_colour(
                (pixels[at], pixels[at + 1], pixels[at + 2]), table))
    return bytes(out)


def mirror(raster: bytes, width: int, height: int) -> bytes:
    return bytes(raster[y * width + (width - 1 - x)]
                 for y in range(height) for x in range(width))


# --- the donor walk -------------------------------------------------------------------


@dataclass(frozen=True)
class Cell:
    """One animation cell: the container it names and the raster that must fill it."""

    slot: int
    frame: int
    direction: int
    graphic_offset: int
    piece_offset: int
    raster: bytes


def donor_cells(data: bytes, assets: Path, spec: SpriteSwap, *,
                layout=None) -> list[Cell]:
    """Walk a sprite's populated slots and build the raster for every cell.

    Every structural fact the write depends on is asserted, not assumed: the composition
    size, the populated slots, the frame count against the sheet's own cell count, one
    piece per frame, the frame rect at its anchor, the 8bpp attribute bit and the
    direction-major cell order.

    ``layout`` is the actor-sprite layout this walk reads its addresses from - the
    character registry, the object palette and the animation pointer offset. It
    defaults to the packaged profile's layout and is never cached here, so a caller
    holding another image's profile drives every read from that one.
    """
    if layout is None:
        layout = _packaged_layout()
    size = len(data)
    geometry = spec.geometry
    table = file_offset(layout.character_table_address.raw, size)
    structure = file_offset(read_u32(data, table + 4 * spec.character_index), size)
    composition = read_u32(data, structure) >> 16
    if composition != geometry.composition_size:
        raise SpriteSwapError(
            f"sprite {spec.sprite_id} declares composition size {composition:#x}; this "
            f"write is proven only for the {geometry.composition_size:#x} one "
            f"{geometry.frame_width}x{geometry.frame_height} frame needs"
        )
    palette = palette_indices(data, file_offset(layout.object_palette_address.raw, size))

    cells: list[Cell] = []
    for slot, sheet, frames_per_facing in spec.slots:
        pointer = read_u32(data, structure + layout.animation_pointer_offset + 4 * slot)
        if pointer == 0:
            raise SpriteSwapError(f"sprite {spec.sprite_id} slot {slot} is null")
        animation = sg.decode_animation(data, file_offset(pointer, size))
        if animation.frame_count != frames_per_facing:
            raise SpriteSwapError(
                f"slot {slot} holds {animation.frame_count} frames per facing but "
                f"{sheet} supplies {frames_per_facing}"
            )
        path = assets / sheet
        for frame in range(animation.frame_count):
            for direction in range(sg.DIRECTION_COUNT):
                cells.append(_cell(data, palette, path, size, animation, slot, sheet,
                                   frames_per_facing, frame, direction, geometry))
    return cells


def _cell(data, palette, path, size, animation, slot, sheet, frames_per_facing,
          frame, direction, geometry: SpriteGeometry) -> Cell:
    frame_offset = file_offset(animation.pointer_for(frame, direction), size)
    record = sg.decode_frame(data, frame_offset)
    rect = (geometry.frame_width, geometry.frame_height)
    if record.piece_count != 1:
        raise SpriteSwapError(
            f"slot {slot} frame {frame} direction {direction} holds "
            f"{record.piece_count} pieces; this write is proven only for the donor's "
            "single-piece frames"
        )
    piece = record.pieces[0]
    if piece.stored_dimensions != rect:
        raise SpriteSwapError(
            f"slot {slot} frame {frame} direction {direction} stores "
            f"{piece.stored_dimensions} pixels; expected the donor's {rect}"
        )
    if record.header_bounds != (*geometry.frame_anchor, *rect):
        raise SpriteSwapError(
            f"slot {slot} frame {frame} direction {direction} is bounded "
            f"{record.header_bounds}; expected the donor's "
            f"{(*geometry.frame_anchor, *rect)}"
        )
    if not piece.colour_256:
        raise SpriteSwapError(
            f"slot {slot} frame {frame} direction {direction} is not 8bpp"
        )
    graphic_offset = file_offset(piece.graphics_pointer, size)
    raster = raster_from_png(path, palette, *rect,
                             cell=direction * frames_per_facing + frame, geometry=geometry)
    # Retail renders direction 3 by flipping the direction-2 container, so the art a
    # flipped piece requires is the mirror of the cell the artist drew for that facing.
    if piece.horizontal_flip:
        raster = mirror(raster, *rect)
    return Cell(slot=slot, frame=frame, direction=direction, graphic_offset=graphic_offset,
                piece_offset=piece.offset + sg.PIECE_GRAPHICS, raster=raster)


@dataclass(frozen=True)
class Target:
    """One container, the art it must hold, and EVERY word that names it.

    More than one piece can name one container - retail renders direction 3 by naming
    the direction-2 container under a horizontal flip - so a payload that moves must
    carry every one of those words with it. Repointing only the first is the failure this
    type exists to prevent: the second facing would keep drawing the original art.
    """

    offset: int
    raster: bytes
    references: tuple[int, ...]


def containers(cells: list[Cell]) -> dict[int, Target]:
    """One target per distinct container, refusing a container two cells disagree on.

    A container several slots name must render the same art in all of them, so the rasters
    reaching it are required to agree. That is what makes the supplied sheets' own sharing
    assumptions checkable instead of trusted.
    """
    rasters: dict[int, bytes] = {}
    references: dict[int, list[int]] = {}
    for cell in cells:
        existing = rasters.get(cell.graphic_offset)
        if existing is None:
            rasters[cell.graphic_offset] = cell.raster
        elif existing != cell.raster:
            raise SpriteSwapError(
                f"container at {cell.graphic_offset:#x} is named by slot {cell.slot} frame "
                f"{cell.frame} direction {cell.direction} with art that disagrees with the "
                "cell already assigned to it"
            )
        references.setdefault(cell.graphic_offset, []).append(cell.piece_offset)
    return {offset: Target(offset, rasters[offset], tuple(references[offset]))
            for offset in sorted(rasters)}


# --- the plan -------------------------------------------------------------------------


@dataclass
class Write:
    """One contiguous overwrite, with the bytes it replaces for the stale-base check."""

    offset: int
    old: bytes
    new: bytes
    owner: str
    reason: str

    @property
    def end(self) -> int:
        return self.offset + len(self.new)


@dataclass
class Plan:
    writes: list[Write] = field(default_factory=list)
    records: list[dict] = field(default_factory=list)
    placed: list[int] = field(default_factory=list)


def _place(
    data: bytes, plan: Plan, offset: int, payload: bytes, owner: str,
    reference_words: tuple[int, ...], record: dict,
) -> None:
    """Put an encoded payload where it belongs, in place or appended.

    A payload that fits the extent the container already occupies is written there; one that
    does not is appended above the end of the image, and every word that names the container
    is rewritten in the same batch after each word is confirmed to be the one this write
    read. Repointing only some of those words is how a facing keeps the old art.
    """
    if len(payload) <= record["original_packed_size"]:
        plan.writes.append(Write(offset, data[offset:offset + len(payload)], payload, owner,
                                 "in-place graphics payload overwrite"))
        record["placement"] = "in-place"
        record["spans"] = [[offset, len(payload)]]
    else:
        for word in reference_words:
            if read_u32(data, word) != offset + 0x08000000:
                raise SpriteSwapError(
                    f"the word at {word:#x} names {read_u32(data, word):#010x}, not the "
                    f"container at {offset:#x}; refusing to repoint a word this write did "
                    "not read"
                )
        align_base = max([len(data)] + plan.placed)
        start = (align_base + 3) & ~3
        padding = start - align_base
        plan.placed.append(start + len(payload))
        plan.writes.append(Write(start, b"", payload, owner, "appended graphics payload"))
        spans = [[align_base, padding + len(payload)]]
        for word in reference_words:
            plan.writes.append(Write(word, data[word:word + 4],
                                     (start + 0x08000000).to_bytes(4, "little"), owner,
                                     "reference rewrite to the appended payload"))
            spans.append([word, 4])
        record["placement"] = "appended"
        record["new_offset"] = start
        record["new_address"] = f"0x{start + 0x08000000:08X}"
        record["padding_bytes"] = padding
        # The alignment run between the old end of image and the payload belongs to this
        # payload, so the diff-confinement check can attribute every changed byte.
        record["spans"] = spans
    plan.records.append(record)


def plan_container(
    data: bytes, plan: Plan, offset: int, width: int, height: int, raster: bytes,
    owner: str, reference_words: tuple[int, ...],
) -> None:
    """Encode one actor-sprite container, which the engine reads as swizzled 8x8 tiles."""
    kind = sg.graphics_container_kind(data, offset)
    graphic = sg.decode_graphic(data, offset, width, height, colour_256=True)
    payload = sg.encode_graphic_payload(graphic, raster, kind=kind)
    _place(data, plan, offset, payload, owner, reference_words, {
        "container_offset": offset,
        "container_address": f"0x{offset + 0x08000000:08X}",
        "format": "swizzled-tiles",
        "width": width,
        "height": height,
        "original_packed_size": graphic.packed_size,
        "encoded_size": len(payload),
        "owner": owner,
        "reference_word_offsets": list(reference_words),
    })


def plan_portrait(
    data: bytes, plan: Plan, offset: int, raster: bytes, owner: str,
    reference_words: tuple[int, ...], side: int = 64,
) -> None:
    """Encode the portrait container, whose payload is a LINEAR raster and not tiles.

    This cost a runtime session, so it is stated as evidence rather than as a choice.
    Rendering the retail container's own payload as a linear 64x64 raster reproduces the
    retail portrait; reading that same payload as swizzled 8x8 tiles produces noise. The
    portrait therefore packs straight.

    The trap is that the sprite encoder agrees with itself on the wrong model: decode
    (unswizzle) then re-encode (swizzle) round trips byte-exactly, so a writer that treated
    the portrait as tiles passed its own decode-then-compare check while putting noise on
    the screen. A format check that shares the writer's assumption cannot catch that.
    """
    kind = sg.graphics_container_kind(data, offset)
    container = wl.unpack(data, offset)
    if container.declared_size != len(raster):
        raise SpriteSwapError(
            f"the portrait container at {offset:#x} declares {container.declared_size} "
            f"bytes but the supplied raster is {len(raster)}"
        )
    payload = wl.pack(raster, kind=kind)
    try:
        wl.validate_retail_termination(payload)
    except wl.ContainerError as exc:
        raise SpriteSwapError(
            f"the re-encoded portrait does not satisfy the retail termination contract: {exc}"
        ) from exc
    _place(data, plan, offset, payload, owner, reference_words, {
        "container_offset": offset,
        "container_address": f"0x{offset + 0x08000000:08X}",
        "format": "linear-raster",
        "width": side,
        "height": side,
        "original_packed_size": container.packed_size,
        "encoded_size": len(payload),
        "owner": owner,
        "reference_word_offsets": list(reference_words),
    })


def apply(data: bytes, plan: Plan) -> bytes:
    """Apply the plan, refusing a stale base and any overlap before writing a byte."""
    spans = []
    for write in plan.writes:
        if write.old and data[write.offset:write.offset + len(write.old)] != write.old:
            raise SpriteSwapError(
                f"the base does not hold what this plan expects at {write.offset:#x}"
            )
        spans.append((write.offset, write.end))
    spans.sort()
    for (_, first_end), (second_start, _) in zip(spans, spans[1:]):
        if second_start < first_end:
            raise SpriteSwapError(f"overlapping writes at {second_start:#x}")
    out = bytearray(data)
    for write in plan.writes:
        if write.end > len(out):
            out.extend(b"\xff" * (write.end - len(out)))
        out[write.offset:write.end] = write.new
    return bytes(out)


def verify(base: bytes, out: bytes, plan: Plan) -> dict:
    """Every changed byte must belong to a span the report attributes to an owner."""
    owned = bytearray(len(out))
    for record in plan.records:
        for start, length in record["spans"]:
            for i in range(start, start + length):
                owned[i] = 1
    inside = outside = 0
    first_outside = None
    for i in range(len(out)):
        old = base[i] if i < len(base) else None
        if out[i] != old:
            if owned[i]:
                inside += 1
            elif first_outside is None:
                outside += 1
                first_outside = i
            else:
                outside += 1
    if outside:
        raise SpriteSwapError(
            f"{outside} changed bytes fall outside every declared span; first at "
            f"{first_outside:#x}"
        )
    return {
        "changed_bytes_inside_declared_spans": inside,
        "changed_bytes_outside": outside,
        "base_size": len(base),
        "output_size": len(out),
        "appended_bytes": len(out) - len(base),
    }


# --- the run --------------------------------------------------------------------------


def verify_reopen(out: bytes, assets: Path, expected: dict[int, bytes],
                  spec: SpriteSwap, *, layout=None) -> dict:
    """Reopen the written image and require every frame cell to reach the intended art.

    The diff-confinement check above only proves WHERE bytes changed. This one proves the
    image the engine will read is the image intended: each frame cell is walked again from
    the output, and the set of containers the cells name must be exactly the set this write
    placed. A container that moved while one of its pieces stayed behind shows up here as a
    missing container named by the output - which is the retail-art-reversion failure mode
    a single-reference rewrite would produce.

    ``layout`` is handed to the re-walk unchanged, so the reopened read resolves from the
    same layout the write did.
    """
    named: dict[int, bytes] = {}
    for cell in donor_cells(out, assets, spec, layout=layout):
        named.setdefault(cell.graphic_offset, cell.raster)
    if set(named) != set(expected):
        missing = sorted(hex(x) for x in set(expected) - set(named))
        extra = sorted(hex(x) for x in set(named) - set(expected))
        raise SpriteSwapError(
            f"the written image names {len(named)} sprite containers but this write placed "
            f"{len(expected)}; missing {missing}, unexpected {extra}"
        )
    rect = (spec.geometry.frame_width, spec.geometry.frame_height)
    for offset, raster in expected.items():
        decoded = sg.decode_graphic(out, offset, *rect, colour_256=True)
        if decoded.pixels != raster:
            raise SpriteSwapError(
                f"the container at {offset:#x} does not decode to the art this write placed"
            )
    return {"sprite_containers_reopened": len(named)}


def swap(data: bytes, assets: Path, *, sprites: tuple[SpriteSwap, ...] = (),
         portraits: tuple[PortraitSwap, ...] = (), layout=None) -> tuple[bytes, dict]:
    """One pass over the image: rewrite every named sprite's containers and every portrait.

    Pure: it takes bytes and returns bytes, so the caller owns the file system and can apply
    the source-alias rule and the staged write once for the whole run. The palette is not
    touched, which the report states as a measurement rather than a promise, because every
    changed byte must fall inside a span this report attributes to a named owner.

    ``layout`` is the actor-sprite layout every target address comes from - the character
    registry, the object palette and the portrait pointer array. It defaults to the packaged
    profile's layout, and a layout that declares no portrait array refuses a portrait swap
    by name instead of falling back to any address.
    """
    if not sprites and not portraits:
        raise SpriteSwapError("no operation was given, so there is nothing to write")
    if layout is None:
        layout = _packaged_layout()

    plan = Plan()
    per_sprite: list[tuple[SpriteSwap, dict[int, bytes]]] = []
    for spec in sprites:
        placed: dict[int, bytes] = {}
        for target in containers(
                donor_cells(data, assets, spec, layout=layout)).values():
            geometry = spec.geometry
            plan_container(data, plan, target.offset, geometry.frame_width,
                           geometry.frame_height, target.raster,
                           owner=f"sprite:{spec.sprite_id}", reference_words=target.references)
            record = plan.records[-1]
            placed[record.get("new_offset", record["container_offset"])] = target.raster
        per_sprite.append((spec, placed))

    size = len(data)
    palette = palette_indices(data, file_offset(layout.object_palette_address.raw, size))
    portrait_records = []
    for spec in portraits:
        if layout.portrait_table_address is None:
            raise SpriteSwapError(
                f"a portrait swap needs {_CANONICAL_PROFILE_ID}'s portrait_table_address "
                "and this profile declares none; there is no fallback address"
            )
        word = file_offset(layout.portrait_table_address.raw, size) + 4 * spec.slot
        offset = file_offset(read_u32(data, word), size)
        declared = wl.unpack(data, offset).declared_size
        if declared != spec.side * spec.side:
            raise SpriteSwapError(
                f"portrait slot {spec.slot} declares {declared} bytes but a "
                f"{spec.side}x{spec.side} raster needs {spec.side * spec.side}"
            )
        raster = raster_from_png(assets / spec.png, palette, spec.side, spec.side)
        plan_portrait(data, plan, offset, raster, owner=f"portrait:{spec.slot}",
                      reference_words=(word,), side=spec.side)
        portrait_records.append((spec, plan.records[-1], raster))

    out = apply(data, plan)
    reopen: dict[str, object] = {}
    for spec, placed in per_sprite:
        reopen[f"sprite:{spec.sprite_id}"] = verify_reopen(
            out, assets, placed, spec, layout=layout)
    written_portraits = []
    for spec, record, raster in portrait_records:
        now = record.get("new_offset", record["container_offset"])
        # This compares the raw payload, so no swizzle step sits between the art and the check.
        # It establishes that the payload written IS the raster held; it does NOT establish
        # that a linear raster is the right format, because pack-then-unpack agrees with
        # whatever format the engine assumed. Only retail art can settle that, which the
        # integration tests do.
        if wl.unpack(out, now).data != raster:
            raise SpriteSwapError(
                f"the portrait container at {now:#x} does not hold the art placed"
            )
        written_portraits.append({"slot": spec.slot, "side": spec.side,
                                  "container_offset": record["container_offset"],
                                  "written_offset": now})
    reopen["portraits"] = written_portraits

    return out, {
        "palette_changed": False,
        "sprites": [{"sprite_id": spec.sprite_id, "character_index": spec.character_index,
                     "slots": [{"slot": slot, "sheet": sheet, "frames_per_facing": frames}
                               for slot, sheet, frames in spec.slots]}
                    for spec in sprites],
        "portraits": [{"slot": spec.slot, "png": spec.png, "side": spec.side}
                      for spec in portraits],
        "assets": {name: sha256((assets / name).read_bytes())
                   for name in sorted({slot.sheet for spec in sprites for slot in spec.slots}
                                      | {spec.png for spec in portraits})},
        "containers_written": len(plan.records),
        "containers": plan.records,
        "diff": verify(data, out, plan),
        "reopen": reopen,
    }
