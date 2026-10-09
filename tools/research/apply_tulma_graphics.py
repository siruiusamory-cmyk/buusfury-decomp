"""Apply FRIEND-V3-TULMA-GRAPHICS-001: retail Bulma's own graphics, redrawn as Tulma.

WHY A RESEARCH WRITER AND NOT THE PROJECT BUILD. `webfoot build` refuses any base that
is not an exactly-verified canonical image, and the image this ticket must extend is a
10,133,410-byte derivative. The project's generated-image policy models
canonical-plus-expansion-to-16-MiB, which is not that image either. So this writer
follows the friend chain's own precedent (`apply_friend_v3_text_edits.py`): an explicit
`--base` with an exact `--expect-sha256`, writing a NEW image and never the source. The
codec is not reimplemented - container kind, decode, swizzle, re-encode and the retail
termination check all come from `tools.webfoot.formats.sprite_graphics`.

TARGET IDENTITY, AND THE TRAP THIS AVOIDS. In the foundation the only appearance record
whose label reads `Bulma` is record 22, which is retail CHI-CHI. Retail BULMA is record
20, labelled `Tulma` there. Nothing here keys on a label: the target is the
sprite-definition registry entry for sprite id 41 and portrait slot 17, and both are
address-identical in the canonical image and in the foundation (measured: every frame,
piece, attribute and container of sprite 41 is byte-identical between the two).

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

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.webfoot.formats import rgb_png  # noqa: E402
from tools.webfoot.formats import sprite_graphics as sg  # noqa: E402
from tools.webfoot.formats import webfoot_lz as wl  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

#: config/roms.yaml actor_sprites.character_table_address.
REGISTRY_TABLE_ADDRESS = 0x086B6BDC
#: The run index of sprite id 41: ids run 10..306, so index = id - 10.
BULMA_CHARACTER_INDEX = 31
BULMA_SPRITE_ID = 41
#: config/roms.yaml actor_sprites.object_palette_address.
OBJECT_PALETTE_ADDRESS = 0x0805652C
#: A structure's animation-pointer array, count-bounded, begins at +0x54
#: (PROJECT_STATE.md "Sprite definitions and animations").
ANIMATION_ARRAY_OFFSET = 0x54
#: The three populated slots of sprite 41, and the sheet that fills each. Slot 1 is walk
#: by frame count alone (4 per facing); stand against arms-up is the raised silhouette.
#: Slots 2..11 are null and carry no art.
SHEET_SLOTS = ((0, "stand.png", 2), (1, "walk.png", 4), (12, "arms_up.png", 2))
#: The portrait pointer array (accessor 0x08011F20) and retail Bulma's own slot.
PORTRAIT_ARRAY_ADDRESS = 0x086F393C
BULMA_PORTRAIT_SLOT = 17
PORTRAIT_SIDE = 64
#: Every donor frame is one 16x32 piece at anchor (0,-24), and 16x32 is also exactly the
#: composition size the structure declares (+0x02 = 0x200). A piece's stored dim_0/dim_1
#: are pixel extents, not tile counts (the engine halves dim_0 to centre an OBJ).
FRAME_WIDTH, FRAME_HEIGHT = 16, 32
FRAME_ANCHOR = (0, -24)
COMPOSITION_SIZE = 0x200
#: The supplied sheets are one row of 32x32 cells and the art sits in x 8..23 of each, so
#: this window recovers the donor frame with no pixel dropped.
CELL_SIDE = 32
CELL_CROP_X = 8
#: The planner's chroma key for a hole (docs/project-format.md).
CHROMA_KEY = (255, 0, 255)


class TulmaGraphicsError(ValueError):
    """Raised when a guard refuses rather than writing an unproven byte."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_offset(address: int, size: int) -> int:
    """A GBA ROM address as a file offset, through the window the SDK uses."""
    offset = address - 0x08000000
    if not 0 <= offset < size:
        raise TulmaGraphicsError(f"address {address:#010x} is outside a {size}-byte image")
    return offset


def read_u32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise TulmaGraphicsError(f"word at {offset:#x} runs past the image")
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
        raise TulmaGraphicsError(
            f"colour {colour} is not in the object palette; this writer adds no entry, so "
            "the art must use colours the image already carries"
        )
    if len(candidates) == 1:
        return candidates[0]
    visible = [index for index in candidates if index != sg.TRANSPARENT_INDEX]
    if len(visible) != 1:
        raise TulmaGraphicsError(
            f"colour {colour} is carried by indices {candidates} and no single visible "
            "index chooses between them"
        )
    return visible[0]


def raster_from_png(
    path: Path, table: dict[tuple[int, int, int], tuple[int, ...]],
    width: int, height: int, *, cell: int | None = None,
) -> bytes:
    """One PNG, or one cropped cell of a sheet, as linear palette indices, row major."""
    pixels, png_width, png_height, alpha = rgb_png.decode_truecolour(path.read_bytes())
    if alpha is not None and any(value != 255 for value in alpha):
        raise TulmaGraphicsError(
            f"{path.name} has a partly transparent pixel; a sprite pixel is one palette "
            "index, so this writer takes the chroma key as the hole rather than alpha"
        )
    if cell is None:
        if (png_width, png_height) != (width, height):
            raise TulmaGraphicsError(
                f"{path.name} is {png_width}x{png_height}; expected {width}x{height}"
            )
        left = 0
    else:
        if png_height != CELL_SIDE or png_width % CELL_SIDE:
            raise TulmaGraphicsError(
                f"{path.name} is {png_width}x{png_height}; expected one row of "
                f"{CELL_SIDE}x{CELL_SIDE} cells"
            )
        if not 0 <= cell < png_width // CELL_SIDE:
            raise TulmaGraphicsError(f"{path.name} has no cell {cell}")
        left = cell * CELL_SIDE + CELL_CROP_X
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


def donor_cells(data: bytes, assets: Path) -> list[Cell]:
    """Walk sprite 41's populated slots and build the raster for every cell.

    Every structural fact the write depends on is asserted, not assumed: the composition
    size, the populated slots, the frame count against the sheet's own cell count, one
    piece per frame, the 16x32 rect at anchor (0,-24), the 8bpp attribute bit and the
    direction-major cell order.
    """
    size = len(data)
    table = file_offset(REGISTRY_TABLE_ADDRESS, size)
    structure = file_offset(read_u32(data, table + 4 * BULMA_CHARACTER_INDEX), size)
    composition = read_u32(data, structure) >> 16
    if composition != COMPOSITION_SIZE:
        raise TulmaGraphicsError(
            f"sprite {BULMA_SPRITE_ID} declares composition size {composition:#x}; this "
            f"write is proven only for the {COMPOSITION_SIZE:#x} one 16x32 frame needs"
        )
    palette = palette_indices(data, file_offset(OBJECT_PALETTE_ADDRESS, size))

    cells: list[Cell] = []
    for slot, sheet, frames_per_facing in SHEET_SLOTS:
        pointer = read_u32(data, structure + ANIMATION_ARRAY_OFFSET + 4 * slot)
        if pointer == 0:
            raise TulmaGraphicsError(f"sprite {BULMA_SPRITE_ID} slot {slot} is null")
        animation = sg.decode_animation(data, file_offset(pointer, size))
        if animation.frame_count != frames_per_facing:
            raise TulmaGraphicsError(
                f"slot {slot} holds {animation.frame_count} frames per facing but "
                f"{sheet} supplies {frames_per_facing}"
            )
        path = assets / sheet
        for frame in range(animation.frame_count):
            for direction in range(sg.DIRECTION_COUNT):
                cells.append(_cell(data, palette, path, size, animation, slot, sheet,
                                   frames_per_facing, frame, direction))
    return cells


def _cell(data, palette, path, size, animation, slot, sheet, frames_per_facing,
          frame, direction) -> Cell:
    frame_offset = file_offset(animation.pointer_for(frame, direction), size)
    record = sg.decode_frame(data, frame_offset)
    if record.piece_count != 1:
        raise TulmaGraphicsError(
            f"slot {slot} frame {frame} direction {direction} holds "
            f"{record.piece_count} pieces; this write is proven only for the donor's "
            "single-piece frames"
        )
    piece = record.pieces[0]
    if piece.stored_dimensions != (FRAME_WIDTH, FRAME_HEIGHT):
        raise TulmaGraphicsError(
            f"slot {slot} frame {frame} direction {direction} stores "
            f"{piece.stored_dimensions} pixels; expected the donor's "
            f"{(FRAME_WIDTH, FRAME_HEIGHT)}"
        )
    if record.header_bounds != (*FRAME_ANCHOR, FRAME_WIDTH, FRAME_HEIGHT):
        raise TulmaGraphicsError(
            f"slot {slot} frame {frame} direction {direction} is bounded "
            f"{record.header_bounds}; expected the donor's "
            f"{(*FRAME_ANCHOR, FRAME_WIDTH, FRAME_HEIGHT)}"
        )
    if not piece.colour_256:
        raise TulmaGraphicsError(
            f"slot {slot} frame {frame} direction {direction} is not 8bpp"
        )
    graphic_offset = file_offset(piece.graphics_pointer, size)
    raster = raster_from_png(path, palette, FRAME_WIDTH, FRAME_HEIGHT,
                             cell=direction * frames_per_facing + frame)
    # Retail renders direction 3 by flipping the direction-2 container, so the art a
    # flipped piece requires is the mirror of the cell the artist drew for that facing.
    if piece.horizontal_flip:
        raster = mirror(raster, FRAME_WIDTH, FRAME_HEIGHT)
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
            raise TulmaGraphicsError(
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
                raise TulmaGraphicsError(
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
    reference_words: tuple[int, ...],
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
        raise TulmaGraphicsError(
            f"the portrait container at {offset:#x} declares {container.declared_size} "
            f"bytes but the supplied raster is {len(raster)}"
        )
    payload = wl.pack(raster, kind=kind)
    try:
        wl.validate_retail_termination(payload)
    except wl.ContainerError as exc:
        raise TulmaGraphicsError(
            f"the re-encoded portrait does not satisfy the retail termination contract: {exc}"
        ) from exc
    _place(data, plan, offset, payload, owner, reference_words, {
        "container_offset": offset,
        "container_address": f"0x{offset + 0x08000000:08X}",
        "format": "linear-raster",
        "width": PORTRAIT_SIDE,
        "height": PORTRAIT_SIDE,
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
            raise TulmaGraphicsError(
                f"the base does not hold what this plan expects at {write.offset:#x}"
            )
        spans.append((write.offset, write.end))
    spans.sort()
    for (_, first_end), (second_start, _) in zip(spans, spans[1:]):
        if second_start < first_end:
            raise TulmaGraphicsError(f"overlapping writes at {second_start:#x}")
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
        raise TulmaGraphicsError(
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


def verify_reopen(out: bytes, assets: Path, expected: dict[int, bytes]) -> dict:
    """Reopen the written image and require every frame cell to reach the intended art.

    The diff-confinement check above only proves WHERE bytes changed. This one proves the
    image the engine will read is the image intended: each frame cell is walked again from
    the output, and the set of containers the cells name must be exactly the set this write
    placed. A container that moved while one of its pieces stayed behind shows up here as a
    missing container named by the output - which is the retail-art-reversion failure mode
    a single-reference rewrite would produce.
    """
    named: dict[int, bytes] = {}
    for cell in donor_cells(out, assets):
        named.setdefault(cell.graphic_offset, cell.raster)
    if set(named) != set(expected):
        missing = sorted(hex(x) for x in set(expected) - set(named))
        extra = sorted(hex(x) for x in set(named) - set(expected))
        raise TulmaGraphicsError(
            f"the written image names {len(named)} sprite containers but this write placed "
            f"{len(expected)}; missing {missing}, unexpected {extra}"
        )
    for offset, raster in expected.items():
        decoded = sg.decode_graphic(out, offset, FRAME_WIDTH, FRAME_HEIGHT, colour_256=True)
        if decoded.pixels != raster:
            raise TulmaGraphicsError(
                f"the container at {offset:#x} does not decode to the art this write placed"
            )
    return {"sprite_containers_reopened": len(named)}


def _write_staged(path: Path, data: bytes) -> None:
    """Write through a sibling temporary file, then rename, so a reader never sees a partial.

    The precedent is `apply_friend_v3_text_edits.py`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".",
                                     suffix=".partial", delete=False) as handle:
        staged = Path(handle.name)
        try:
            handle.write(data)
        except BaseException:
            handle.close()
            staged.unlink(missing_ok=True)
            raise
    staged.replace(path)


def run(base_path: Path, expect_sha256: str, assets: Path, out_path: Path,
        report_path: Path) -> dict:
    # First and total, before anything is read for writing: a source is an input on every path
    # and an output on none, and a hard link of the canonical image is the same file.
    ensure_not_source_alias(base_path, out_path)
    ensure_not_source_alias(base_path, report_path)
    ensure_not_source_alias(out_path, report_path)
    data = base_path.read_bytes()
    digest = sha256(data)
    if digest != expect_sha256.lower():
        raise TulmaGraphicsError(
            f"{base_path} is {digest}, not the base this write was proven against "
            f"({expect_sha256.lower()})"
        )

    plan = Plan()
    placed: dict[int, bytes] = {}
    for target in containers(donor_cells(data, assets)).values():
        plan_container(data, plan, target.offset, FRAME_WIDTH, FRAME_HEIGHT, target.raster,
                       owner=f"sprite:{BULMA_SPRITE_ID}", reference_words=target.references)
        record = plan.records[-1]
        placed[record.get("new_offset", record["container_offset"])] = target.raster

    size = len(data)
    portrait_word = file_offset(PORTRAIT_ARRAY_ADDRESS, size) + 4 * BULMA_PORTRAIT_SLOT
    portrait_offset = file_offset(read_u32(data, portrait_word), size)
    palette = palette_indices(data, file_offset(OBJECT_PALETTE_ADDRESS, size))
    portrait_raster = raster_from_png(assets / "portrait.png", palette, PORTRAIT_SIDE,
                                      PORTRAIT_SIDE)
    plan_portrait(
        data, plan, portrait_offset, portrait_raster,
        owner=f"appearance:{BULMA_CHARACTER_INDEX}/portrait:{BULMA_PORTRAIT_SLOT}",
        reference_words=(portrait_word,),
    )
    portrait_record = plan.records[-1]

    out = apply(data, plan)
    reopen = verify_reopen(out, assets, placed)
    portrait_now = portrait_record.get("new_offset", portrait_record["container_offset"])
    # This compares the raw payload, so no swizzle step sits between the art and the check.
    # It establishes that the payload written IS the raster this writer holds; it does NOT
    # establish that a linear raster is the right format, because pack-then-unpack agrees
    # with whatever format the writer assumed. The format is checked against retail data in
    # tests/integration/test_tulma_graphics_rom.py, which is the only place it can be.
    if wl.unpack(out, portrait_now).data != portrait_raster:
        raise TulmaGraphicsError("the portrait container does not hold the art placed")
    reopen["portrait_container_offset"] = portrait_now
    report = {
        "ticket": "FRIEND-V3-TULMA-GRAPHICS-001",
        "base_path": str(base_path),
        "base_sha256": digest,
        "base_size": len(data),
        "output_path": str(out_path),
        "output_sha256": sha256(out),
        "output_size": len(out),
        "palette_changed": False,
        "target": {
            "sprite_id": BULMA_SPRITE_ID,
            "character_index": BULMA_CHARACTER_INDEX,
            "portrait_slot": BULMA_PORTRAIT_SLOT,
            "slots": [{"slot": slot, "sheet": sheet, "frames_per_facing": frames}
                      for slot, sheet, frames in SHEET_SLOTS],
        },
        "assets": {name: sha256((assets / name).read_bytes())
                   for name in ("stand.png", "walk.png", "arms_up.png", "portrait.png")},
        "containers_written": len(plan.records),
        "containers": plan.records,
        "diff": verify(data, out, plan),
        "reopen": reopen,
    }
    _write_staged(out_path, out)
    _write_staged(report_path,
                  (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    if sha256(base_path.read_bytes()) != digest:
        raise TulmaGraphicsError("the base image changed during the build")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = run(args.base, args.expect_sha256, args.assets, args.out, args.report)
    except (TulmaGraphicsError, WriteError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(f"output  {report['output_sha256']}  {report['output_size']} bytes")
    print(f"wrote   {report['containers_written']} containers")
    print(f"diff    {report['diff']['changed_bytes_inside_declared_spans']} inside, "
          f"{report['diff']['changed_bytes_outside']} outside")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
