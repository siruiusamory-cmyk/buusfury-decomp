"""Cell-level sub-piece machinery and the pixel round-trip proof for a ported sprite.

Why this module exists: `cells_of` lived only in `build/split_frame_search.py`, which is untracked and
cannot run outside one worktree, while two tracked port tools imported it. The functions here are the
tracked home for the 8x8-cell model and for the proof that a sub-piece split loses no colour.

What it provides:
  * `cells_of(payload, size, step)` - the 8x8 cells of a frame and the source palette indices each uses;
  * `rects_for_bank(owned, size)` / `merge_rects(rects, size)` - greedy OBJ rectangle covers;
  * `pack_rect` / `unpack_rect` - the emitter's exact byte layout (per tile, per row, low then high
    nibble), and its inverse;
  * `verify_frame(frame, rects, banks)` - pack every rectangle, decode it back through the same bank's
    slot map, and compare with the source payload in SOURCE index space, also reporting pixel overlap
    between rectangles.

The comparison is deliberately source index -> packed byte -> source index. Comparing a mapped slot
against a raw source index can never agree and tests nothing, which is a recorded pitfall (P-086).
"""

from __future__ import annotations

from dataclasses import dataclass

CAPACITY = 15
SHAPES = [(64, 64), (64, 32), (32, 64), (32, 32), (32, 16), (16, 32), (16, 16),
          (32, 8), (8, 32), (16, 8), (8, 16), (8, 8)]

#: Every (width, height) an OBJ piece may take, from the emitter's SHAPE_SIZE table (three OBJ shapes x
#: four sizes, both orientations). Merging must refuse a rectangle outside this set: it would have no
#: shape/size encoding, and a merge that produced one used to reach the emitter as a KeyError.
VALID_RECT = frozenset({(8, 8), (16, 16), (32, 32), (64, 64),
                        (16, 8), (32, 8), (32, 16), (64, 32),
                        (8, 16), (8, 32), (16, 32), (32, 64)})


@dataclass(frozen=True)
class Cell:
    """One 8x8 cell of a frame: its pixel origin and the set of source indices it draws (0 excluded)."""

    x: int
    y: int
    colours: frozenset


def cells_of(payload: bytes, size: int = 64, step: int = 8) -> list[Cell]:
    """Every 8x8 cell of a size x size source frame, transparent (index 0) pixels excluded."""
    out = []
    for cell_y in range(0, size, step):
        for cell_x in range(0, size, step):
            colours = set()
            for row in range(step):
                for column in range(step):
                    value = payload[(cell_y + row) * size + cell_x + column]
                    if value:
                        colours.add(value)
            out.append(Cell(cell_x, cell_y, frozenset(colours)))
    return out


def rects_for_bank(owned, size):
    """Greedy cover of one bank's cells with the largest OBJ rectangles available: (n, [(x,y,w,h)])."""
    covered = set()
    rects = []
    for cell_y in range(0, size, 8):
        for cell_x in range(0, size, 8):
            if (cell_x, cell_y) not in owned or (cell_x, cell_y) in covered:
                continue
            best = None
            for width, height in SHAPES:
                if cell_x + width > size or cell_y + height > size:
                    continue
                block = {(x, y) for y in range(cell_y, cell_y + height, 8)
                         for x in range(cell_x, cell_x + width, 8)}
                if block <= owned and not (block & covered):
                    if best is None or len(block) > best[0]:
                        best = (len(block), block, width, height)
            if best is None:
                covered.add((cell_x, cell_y))
                rects.append((cell_x, cell_y, 8, 8))
                continue
            covered |= best[1]
            rects.append((cell_x, cell_y, best[2], best[3]))
    return len(rects), rects


def merge_rects(rects, size, max_tiles=16):
    """Merge same-bank neighbours into larger OBJ rectangles, so the reported count is not inflated.

    A merge is refused when the result is not a valid OBJ rectangle or would exceed 16 tiles. The
    validity check is load bearing: an earlier version merged (8,8)+(8,8) into a 64x16 rectangle, which
    no OBJ shape encodes, and it reached the emitter as a KeyError.
    """
    rects = list(rects)
    changed = True
    while changed:
        changed = False
        for i in range(len(rects)):
            x1, y1, w1, h1, bank1 = rects[i]
            for j in range(len(rects)):
                if i == j:
                    continue
                x2, y2, w2, h2, bank2 = rects[j]
                if bank1 != bank2:
                    continue
                if w1 == w2 and x1 == x2 and (y1 + h1 == y2 or y2 + h2 == y1):
                    merged = (x1, min(y1, y2), w1, h1 + h2, bank1)
                elif h1 == h2 and y1 == y2 and (x1 + w1 == x2 or x2 + w2 == x1):
                    merged = (min(x1, x2), y1, w1 + w2, h1, bank1)
                else:
                    continue
                if (merged[2], merged[3]) not in VALID_RECT:
                    continue
                if merged[2] > size or merged[3] > size or merged[2] * merged[3] // 64 > max_tiles:
                    continue
                rects = [r for k, r in enumerate(rects) if k not in (i, j)] + [merged]
                changed = True
                break
            if changed:
                break
    return rects


def pack_rect(payload, size, x, y, width, height, slots) -> bytes:
    """The emitter's exact layout: per tile, per row, low nibble then high nibble.

    Refuses a colour the bank does not hold rather than writing a wrong nibble, because a silent zero
    here is exactly the class of failure the round-trip check exists to catch.
    """
    slots = {**slots, 0: 0}
    out = bytearray()
    for tile_y in range(y, y + height, 8):
        for tile_x in range(x, x + width, 8):
            for row in range(8):
                for pair in range(0, 8, 2):
                    low_value = payload[(tile_y + row) * size + tile_x + pair]
                    high_value = payload[(tile_y + row) * size + tile_x + pair + 1]
                    for value in (low_value, high_value):
                        if value not in slots:
                            raise KeyError(f"colour 0x{value:02X} is not in this bank's slot map")
                    out.append((slots[low_value] & 0xF) | ((slots[high_value] & 0xF) << 4))
    return bytes(out)


def unpack_rect(packed, x, y, width, height, inverse) -> dict:
    """Decode a packed rectangle back to source indices: {(px, py): source index or -1}."""
    out = {}
    cursor = 0
    for tile_y in range(y, y + height, 8):
        for tile_x in range(x, x + width, 8):
            for row in range(8):
                for pair in range(0, 8, 2):
                    byte = packed[cursor]
                    cursor += 1
                    for column, value in ((pair, byte & 0xF), (pair + 1, (byte >> 4) & 0xF)):
                        out[(tile_x + column, tile_y + row)] = inverse.get(value, -1)
    return out


def slot_maps_for(banks) -> list[dict]:
    """One colour -> slot map per bank; slot 0 stays transparent, colours take slots from 1."""
    return [{value: slot for slot, value in enumerate(sorted(bank), start=1)} for bank in banks]


def inverse_maps_for(banks) -> list[dict]:
    maps = [{slot: value for value, slot in mapping.items()} for mapping in slot_maps_for(banks)]
    for mapping in maps:
        mapping[0] = 0
    return maps


def attribute_cells(cells, bank_colours):
    """Give each OCCUPIED cell a bank whose palette holds all of its colours: [(x, y, bank)] or None.

    A cell's colours must share a bank because the packed pixels of one rectangle all come from one
    palette. The first bank in order that holds them all wins, which keeps the piece count stable. A
    cell with no opaque pixel is skipped: nothing draws it, so it needs no bank.
    """
    out = []
    for cell in cells:
        if not cell.colours:
            continue
        for bank, colours in enumerate(bank_colours):
            if cell.colours <= colours:
                out.append((cell.x, cell.y, bank))
                break
        else:
            return None
    return out


def palette_for_bank(indices, source_palette) -> dict:
    """One bank: {colour: slot} with slots from 1, and the 16 halfwords the runtime writer copies.

    Slot 0 stays transparent. Colours are placed in sorted order so a rerun of the emitter reproduces
    the same bytes, which is what lets the appended palettes be verified byte for byte.
    """
    import struct

    slots = {}
    for slot, index in enumerate(sorted(indices), start=1):
        slots[index] = slot
    colours = [0] * 16
    for index, slot in slots.items():
        colours[slot] = struct.unpack_from("<H", source_palette, 2 * index)[0]
    return {"slots": slots, "colours": colours}


def build_frame(payload, size, cell_banks, palettes) -> list:
    """[(x, y, w, h, bank, packed bytes)] for one frame: each bank's cells covered with OBJ rectangles.

    `cell_banks` maps (x, y) to the bank that draws that cell, so a cell belongs to exactly one bank.
    """
    cells = cells_of(payload, size)
    owned = [set() for _ in palettes]
    for cell in cells:
        bank = cell_banks.get((cell.x, cell.y))
        if bank is not None:
            owned[bank].add((cell.x, cell.y))
    pieces = []
    for local_bank in range(len(palettes)):
        mapping = dict(palettes[local_bank]["slots"])
        mapping[0] = 0
        _, rects = rects_for_bank(owned[local_bank], size)
        rects = merge_rects([(x, y, w, h, local_bank) for x, y, w, h in rects], size)
        for x, y, width, height, _ in rects:
            packed = pack_rect(payload, size, x, y, width, height, mapping)
            pieces.append((x, y, width, height, local_bank, packed))
    return pieces


def verify_frame(frame, rects, banks) -> dict:
    """Pack, decode and compare one frame. `frame` carries `payload` and `size`.

    Returns {"opaque", "mismatch", "missed", "overlap", "pieces", "bytes", "gaps"}:

      * `opaque`   - opaque source pixels inside at least one rectangle;
      * `mismatch` - of those, pixels whose packed-then-decoded value is not the source index;
      * `missed`   - opaque source pixels NO rectangle covers, i.e. pixels the split would drop. This is
                     counted over the whole frame, because a test over rectangles alone cannot see a
                     pixel that no rectangle draws (the gap that made an earlier check vacuous);
      * `overlap`  - pixels drawn by more than one rectangle, which would let one erase another.

    The comparison is source index -> packed byte -> source index on purpose. Comparing a mapped slot
    against a raw source index can never agree and tests nothing (P-086).
    """
    payload = frame["payload"]
    size = frame["size"]
    slot_maps = slot_maps_for(banks)
    inverse_maps = inverse_maps_for(banks)
    seen = {}
    overlap = 0
    for x, y, width, height, bank in rects:
        for tile_y in range(y, y + height, 8):
            for tile_x in range(x, x + width, 8):
                for row in range(8):
                    for column in range(8):
                        key = (tile_x + column, tile_y + row)
                        if key in seen:
                            overlap += 1
                        seen[key] = bank
    mismatch = 0
    opaque = 0
    written = 0
    for x, y, width, height, bank in rects:
        packed = pack_rect(payload, size, x, y, width, height, slot_maps[bank])
        written += len(packed)
        decoded = unpack_rect(packed, x, y, width, height, inverse_maps[bank])
        for tile_y in range(y, y + height, 8):
            for tile_x in range(x, x + width, 8):
                for row in range(8):
                    for column in range(8):
                        px, py = tile_x + column, tile_y + row
                        source = payload[py * size + px]
                        if not source:
                            continue
                        opaque += 1
                        if decoded.get((px, py)) != source:
                            mismatch += 1
    gaps = [(x, y) for y in range(size) for x in range(size)
            if payload[y * size + x] and (x, y) not in seen]
    return {"opaque": opaque, "mismatch": mismatch, "missed": len(gaps), "gaps": gaps[:8],
            "overlap": overlap, "pieces": len(rects), "bytes": written}


def round_trip_check(frame, rects, banks) -> dict:
    """Same as verify_frame, named for the report line that quotes it."""
    return verify_frame(frame, rects, banks)
