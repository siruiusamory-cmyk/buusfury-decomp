"""FRIEND-V3-TULMA-GRAPHICS-001: the writer against a real image, end to end.

The supplied artwork is private and must not enter the repository, so this test derives its
own sheets from the image. It first walks the donor to learn which (slot, frame, direction)
cells name which container and which of them are drawn flipped, then draws ONE pattern per
container and gives every cell that names it that pattern - which is what the real artist
did, and what makes the shared-container guard meaningful. Every pattern is built from three
colours the image's own object palette already holds, so no palette entry is invented.

That exercises the whole path a real import takes - the donor walk, the direction-major cell
order, the flip handling for the shared direction-2/3 container, the palette lookup, the
in-place against append decision, every reference rewrite and the reopen check - without
carrying a pixel of anyone's art.

The canonical image is used because sprite 41's structures and containers are byte-identical
in it and in the friend image this ticket extends (measured separately).

What must hold after the write:
  * the base image is unchanged and the object palette is byte-identical, because this
    writer changes indices and never colours;
  * every frame cell of sprite 41 decodes to the pattern its own container was drawn with,
    in all four directions including the flipped one;
  * every word naming a moved container was rewritten, so no facing keeps the old art - the
    failure mode a single-reference rewrite produces;
  * sprite 66, retail Chi-Chi, the character the foundation labels `Bulma`, is untouched.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.export.png import encode_rgba
from tools.research import apply_tulma_graphics as tg
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz as wl

CANONICAL_SHA1 = "f1c4b07554d2a3b1ad2f325307051e775ce68087"
#: Retail Chi-Chi's sprite id: the character the foundation displays as "Bulma".
CHICHI_CHARACTER_INDEX = 66 - 10


def _rom_path() -> str:
    for candidate in sorted(glob.glob(os.path.join("roms", "*.gba"))):
        if hashlib.sha1(Path(candidate).read_bytes()).hexdigest() == CANONICAL_SHA1:
            return candidate
    pytest.skip("canonical Buu's Fury ROM not present locally")


def _offset(image: bytes, address: int) -> int:
    return tg.file_offset(address, len(image))


def _palette_colour(image: bytes, index: int) -> tuple[int, int, int]:
    base = _offset(image, tg.OBJECT_PALETTE_ADDRESS)
    word = image[base + 2 * index] | (image[base + 2 * index + 1] << 8)
    return sg.expand_bgr555(word)


def _three_indices(image: bytes) -> list[int]:
    """Three indices with distinct 5-bit colours, so a pattern reads back unambiguously."""
    seen: dict[tuple[int, int, int], int] = {}
    for index in range(1, 256):
        seen.setdefault(tuple(c >> 3 for c in _palette_colour(image, index)), index)
    assert len(seen) >= 3
    return list(seen.values())[:3]


def _donor(image: bytes) -> dict[tuple[int, int, int], tuple[int, bool]]:
    """(slot, frame, direction) -> (container ROM address, drawn flipped)."""
    table = _offset(image, tg.REGISTRY_TABLE_ADDRESS)
    structure = _offset(image, tg.read_u32(image, table + 4 * tg.BULMA_CHARACTER_INDEX))
    out: dict[tuple[int, int, int], tuple[int, bool]] = {}
    for slot, _sheet, frames_per_facing in tg.SHEET_SLOTS:
        pointer = tg.read_u32(image, structure + tg.ANIMATION_ARRAY_OFFSET + 4 * slot)
        assert pointer != 0
        animation = sg.decode_animation(image, _offset(image, pointer))
        assert animation.frame_count == frames_per_facing
        for frame in range(animation.frame_count):
            for direction in range(sg.DIRECTION_COUNT):
                record = sg.decode_frame(
                    image, _offset(image, animation.pointer_for(frame, direction)))
                assert record.piece_count == 1
                piece = record.pieces[0]
                out[(slot, frame, direction)] = (piece.graphics_pointer,
                                                 piece.horizontal_flip)
    return out


def _pattern(indices: list[int], seed: int) -> bytes:
    return bytes(indices[(x + y + seed) % 3]
                 for y in range(tg.FRAME_HEIGHT) for x in range(tg.FRAME_WIDTH))


def _cell_image(image: bytes, indices: list[int], raster: bytes, flipped: bool):
    """One 32x32 cell: the 16x32 art in the x 8..23 window, chroma key in the margins."""
    colours = {index: _palette_colour(image, index) for index in indices}
    rows = [[colours[raster[y * tg.FRAME_WIDTH + x]] for x in range(tg.FRAME_WIDTH)]
            for y in range(tg.FRAME_HEIGHT)]
    if flipped:
        rows = [list(reversed(row)) for row in rows]
    out: list[tuple[int, int, int]] = []
    for row in rows:
        out.extend([tg.CHROMA_KEY] * 8 + row + [tg.CHROMA_KEY] * 8)
    assert len(out) == 32 * 32
    return out


def _sheet_png(cells: list[list[tuple[int, int, int]]]) -> bytes:
    """One row of 32x32 cells as a row-major PNG buffer, which is what a sheet is."""
    flat = [pixel for y in range(32) for cell in cells for pixel in cell[y * 32:(y + 1) * 32]]
    return encode_rgba(32 * len(cells), 32,
                       bytes(c for pixel in flat for c in (*pixel, 255)))


def _build(image: bytes, directory: Path):
    """Write the four assets. Returns {container address: the index raster it must hold}."""
    indices = _three_indices(image)
    donor = _donor(image)
    seeded = {address: _pattern(indices, position * 5)
              for position, address in enumerate(sorted({v[0] for v in donor.values()}))}
    for slot, sheet, frames_per_facing in tg.SHEET_SLOTS:
        cells = []
        for direction in range(sg.DIRECTION_COUNT):
            for frame in range(frames_per_facing):
                address, flipped = donor[(slot, frame, direction)]
                cells.append(_cell_image(image, indices, seeded[address], flipped))
        (directory / sheet).write_bytes(_sheet_png(cells))
    portrait = [[_palette_colour(image, indices[(x + y) % 3]) for x in range(64)]
                for y in range(64)]
    (directory / "portrait.png").write_bytes(
        encode_rgba(64, 64, bytes(c for row in portrait for pixel in row for c in (*pixel, 255))))
    return seeded


def _sprite_containers(image: bytes, character_index: int) -> set[int]:
    table = _offset(image, tg.REGISTRY_TABLE_ADDRESS)
    structure = _offset(image, tg.read_u32(image, table + 4 * character_index))
    found: set[int] = set()
    for slot in range(23):
        pointer = tg.read_u32(image, structure + tg.ANIMATION_ARRAY_OFFSET + 4 * slot)
        # A slot may be null, and in this corpus a slot may also hold a word that is not a
        # ROM pointer at all; neither names an animation record.
        if not 0x08000000 <= pointer < 0x0A000000:
            continue
        animation = sg.decode_animation(image, _offset(image, pointer))
        for frame in range(animation.frame_count):
            for direction in range(sg.DIRECTION_COUNT):
                record = sg.decode_frame(
                    image, _offset(image, animation.pointer_for(frame, direction)))
                found.update(piece.graphics_pointer for piece in record.pieces)
    return found


def _coherence(pixels: bytes, side: int) -> float:
    """Mean absolute difference between horizontally adjacent pixels. Lower is smoother."""
    total = 0
    count = 0
    for y in range(side):
        row = pixels[y * side:(y + 1) * side]
        for x in range(side - 1):
            total += abs(row[x] - row[x + 1])
            count += 1
    return total / count


def _portrait_offsets(image: bytes, limit: int) -> list[int]:
    """File offsets of portrait slots holding a full-size raster, in slot order."""
    array = _offset(image, tg.PORTRAIT_ARRAY_ADDRESS)
    found: list[int] = []
    for slot in range(64):
        word = array + 4 * slot
        if word + 4 > len(image):
            break
        pointer = tg.read_u32(image, word)
        if not 0x08000000 <= pointer < 0x08000000 + len(image):
            continue
        offset = _offset(image, pointer)
        if wl.unpack(image, offset).declared_size != tg.PORTRAIT_SIDE * tg.PORTRAIT_SIDE:
            continue
        found.append(offset)
        if len(found) >= limit:
            break
    return found


def test_a_portrait_payload_is_linear_and_a_sprite_payload_is_tiled():
    """The format claim, measured against retail art and not against the writer's encoder.

    A pack-then-unpack check passes on whichever format the writer assumed, so it cannot
    settle this; that is why the same retail bytes are read BOTH ways here. A portrait is a
    smooth image, so the linear reading must be far more coherent than reading the same bytes
    as 8x8 swizzled tiles, and a sprite payload must show the reverse. This is the only place
    the format can be settled, because only the retail image carries art whose shape is known.
    """
    rom = _rom_path()
    image = Path(rom).read_bytes()
    side = tg.PORTRAIT_SIDE

    portraits = _portrait_offsets(image, 6)
    assert portraits, "no portrait slot holds a full-size raster in this image"
    for offset in portraits:
        payload = wl.unpack(image, offset).data
        linear = _coherence(bytes(payload), side)
        tiled = _coherence(sg.decode_graphic(image, offset, side, side,
                                             colour_256=True).pixels, side)
        assert linear < tiled, (
            f"the portrait at {offset:#x} reads more coherently as tiles "
            f"({tiled:.2f} against {linear:.2f} linear), so it is not a linear raster"
        )

    donor = _donor(image)
    sprite_offset = _offset(image, donor[(tg.SHEET_SLOTS[0][0], 0, 0)][0])
    sprite_payload = wl.unpack(image, sprite_offset).data
    sprite_linear = _coherence(_linear_reading(sprite_payload, tg.FRAME_WIDTH, tg.FRAME_HEIGHT),
                               tg.FRAME_WIDTH)
    sprite_tiled = _coherence(sg.decode_graphic(image, sprite_offset, tg.FRAME_WIDTH,
                                                tg.FRAME_HEIGHT, colour_256=True).pixels,
                              tg.FRAME_WIDTH)
    assert sprite_tiled < sprite_linear, (
        "a sprite container reads more coherently as a linear raster, so it is not tiles"
    )


def _linear_reading(payload: bytes, width: int, height: int) -> bytes:
    """The same bytes read as a plain row-major raster, for comparison with the tile reading."""
    needed = width * height
    assert len(payload) >= needed, "payload is smaller than the raster it would be read as"
    return bytes(payload[:needed])


def test_the_writer_rewrites_every_facing_and_leaves_chi_chi_alone(tmp_path):
    rom = _rom_path()
    base = Path(rom).read_bytes()
    digest = hashlib.sha256(base).hexdigest()
    assets = tmp_path / "assets"
    assets.mkdir()
    seeded = _build(base, assets)
    donor = _donor(base)
    out = tmp_path / "candidate.gba"

    report = tg.run(Path(rom), digest, assets, out, tmp_path / "report.json")
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == digest

    candidate = out.read_bytes()
    assert report["output_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["palette_changed"] is False
    assert report["diff"]["changed_bytes_outside"] == 0
    palette = _offset(base, tg.OBJECT_PALETTE_ADDRESS)
    assert base[palette:palette + 512] == candidate[palette:palette + 512]

    # Every frame cell of the target decodes to the pattern its container was drawn with.
    cells = tg.donor_cells(candidate, assets)
    assert len(cells) == 32, "three populated slots, 2 + 4 + 2 frames, four facings each"
    expected = tg.containers(cells)
    for cell in cells:
        address = donor[(cell.slot, cell.frame, cell.direction)][0]
        decoded = sg.decode_graphic(candidate, cell.graphic_offset, tg.FRAME_WIDTH,
                                    tg.FRAME_HEIGHT, colour_256=True)
        assert decoded.pixels == seeded[address]
        assert decoded.pixels == expected[cell.graphic_offset].raster
    assert len(expected) == len(seeded)

    # Every word naming a container holds that container's placed address, so no facing can
    # keep pointing at the old payload.
    for record in report["containers"]:
        placed = record.get("new_offset", record["container_offset"])
        for word in record["reference_word_offsets"]:
            assert tg.read_u32(candidate, word) == placed + 0x08000000
    shared = [r for r in report["containers"] if len(r["reference_word_offsets"]) > 1]
    assert shared, "the donor shares containers between facings, so this must be exercised"

    # Chi-Chi: every container its frames reach is byte-identical to the base.
    containers = _sprite_containers(base, CHICHI_CHARACTER_INDEX)
    assert containers
    for address in containers:
        offset = _offset(base, address)
        end = sg.decode_graphic(base, offset, tg.FRAME_WIDTH, tg.FRAME_HEIGHT,
                                colour_256=True).packed_end
        assert base[offset:end] == candidate[offset:end]


def test_a_facing_that_is_not_the_mirror_of_its_pair_is_refused(tmp_path):
    """The guard that stops one shared container being given two different arts."""
    rom = _rom_path()
    base = Path(rom).read_bytes()
    assets = tmp_path / "assets"
    assets.mkdir()
    seeded = _build(base, assets)
    donor = _donor(base)
    indices = _three_indices(base)
    for slot, sheet, frames_per_facing in tg.SHEET_SLOTS:
        cells = []
        for direction in range(sg.DIRECTION_COUNT):
            for frame in range(frames_per_facing):
                address, flipped = donor[(slot, frame, direction)]
                # Draw the flipped facing unflipped: the pair now disagrees.
                cells.append(_cell_image(base, indices, seeded[address], False))
        (assets / sheet).write_bytes(_sheet_png(cells))
    with pytest.raises(tg.TulmaGraphicsError, match="disagrees"):
        tg.run(Path(rom), hashlib.sha256(base).hexdigest(), assets,
               tmp_path / "candidate.gba", tmp_path / "report.json")
