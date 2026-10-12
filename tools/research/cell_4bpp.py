"""Convert indexed 8bpp art into 4bpp tiles that select an existing palette bank.

The destination is the GBA's 1-D OBJ tile layout: tiles in raster order, each tile eight rows of four bytes,
two pixels per byte, low nibble first. The source containers in The Legacy of Goku II are one byte per pixel in
ROW-MAJOR order, which is why this reorders rather than copying.

The palette bank is chosen PER PIECE from the banks the destination image already has, so no palette entry is
written anywhere and no other sprite's colours can change. Everything here is pure: bytes in, bytes out.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BANKS = 16
BANK_ENTRIES = 16
TILE = 8
TILE_BYTES = 32


def bank_colours(palette: bytes, bank: int) -> list[tuple[int, int, int]]:
    """The sixteen RGB colours of one bank, from a 256-entry BGR555 palette."""
    out = []
    for slot in range(BANK_ENTRIES):
        value = struct.unpack_from("<H", palette, 2 * (bank * BANK_ENTRIES + slot))[0]
        out.append((((value & 0x1F) * 255) // 31, (((value >> 5) & 0x1F) * 255) // 31,
                    (((value >> 10) & 0x1F) * 255) // 31))
    return out


def distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def map_to_bank(colours: dict[int, tuple[int, int, int]], bank: list[tuple[int, int, int]]) -> dict:
    """Map each source index to a local index 0..15 in this bank, and report the error.

    Index 0 is forced to local 0 because the hardware makes local 0 transparent in 4bpp, and the source's index
    0 is its transparent colour.
    """
    mapping = {0: 0}
    worst = 0
    total = 0
    for index, rgb in colours.items():
        if index == 0:
            continue
        slot = min(range(1, BANK_ENTRIES), key=lambda candidate: distance(rgb, bank[candidate]))
        mapping[index] = slot
        error = distance(rgb, bank[slot])
        worst = max(worst, error)
        total += error
    return {"mapping": mapping, "worst": worst, "total": total}


def choose_bank(pixels: bytes, palette: bytes, source_palette: bytes,
                candidate_banks: range | None = None) -> dict:
    """The bank whose entries fit this piece's colours best, with the mapping and its error."""
    indices = sorted(set(pixels))
    colours = {}
    for index in indices:
        value = struct.unpack_from("<H", source_palette, 2 * index)[0]
        colours[index] = (((value & 0x1F) * 255) // 31, (((value >> 5) & 0x1F) * 255) // 31,
                          (((value >> 10) & 0x1F) * 255) // 31)
    best = None
    for bank in (candidate_banks if candidate_banks is not None else range(BANKS)):
        result = map_to_bank(colours, bank_colours(palette, bank))
        score = (result["worst"], result["total"])
        if best is None or score < (best["worst"], best["total"]):
            best = {"bank": bank, **result, "score": score}
    if best is None:
        raise ValueError("no candidate bank")
    best["colours"] = len(colours)
    best["local_indices"] = len(set(best["mapping"].values()))
    return best


def pack_4bpp(pixels: bytes, width: int, height: int, mapping: dict[int, int]) -> bytes:
    """Row-major indexed pixels to the 1-D 4bpp tile layout, local indices, low nibble first."""
    if width % TILE or height % TILE:
        raise ValueError(f"{width}x{height} is not a whole number of 8x8 tiles")
    out = bytearray()
    for tile_y in range(0, height, TILE):
        for tile_x in range(0, width, TILE):
            for row in range(TILE):
                source = (tile_y + row) * width + tile_x
                line = pixels[source:source + TILE]
                for pair in range(0, TILE, 2):
                    low = mapping.get(line[pair], 0) & 0xF
                    high = mapping.get(line[pair + 1], 0) & 0xF
                    out.append(low | (high << 4))
    return bytes(out)


def pad_to(size: int, payload: bytes) -> bytes:
    """The engine copies width*height BYTES per piece regardless of depth, so the block is padded."""
    if len(payload) > size:
        raise ValueError(f"payload {len(payload)} exceeds the {size}-byte block the engine copies")
    return payload + bytes(size - len(payload))


def piece_bank_bits(bank: int) -> int:
    """The bank as it rides in the piece attribute word: bits 25..27, the attr1 affine-select field."""
    if not 0 <= bank < 8:
        raise ValueError(f"bank {bank} does not fit three bits")
    return bank << 25


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Report the banks a set of pieces needs")
    parser.add_argument("--log2", required=True)
    parser.add_argument("--palette", required=True, help="destination OBJ palette, GBA address or file offset")
    args = parser.parse_args()
    palette_address = int(args.palette, 0) if isinstance(args.palette, str) else args.palette

    from tools.research.build_friend_v4b_cell import read_log2_cell
    log2 = Path(args.log2).read_bytes()
    destination = Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - Buu's Fury (U).gba").read_bytes()
    offset = palette_address - 0x08000000
    palette = destination[offset:offset + 512]
    source_palette = log2[0x081DA6C8 - 0x08000000:0x081DA6C8 - 0x08000000 + 512]

    slots, payloads = read_log2_cell(log2)
    banks: dict[int, int] = {}
    for slot in slots:
        for record in slot:
            for piece in record if isinstance(record, list) else [record]:
                index = piece[5] if len(piece) > 5 else None
                if index is None or index >= len(payloads):
                    continue
                chosen = choose_bank(payloads[index], palette, source_palette)
                banks[chosen["bank"]] = banks.get(chosen["bank"], 0) + 1
                print(f"  {piece[2]}x{piece[3]} {chosen['colours']:>2} colours -> bank {chosen['bank']:>2}, "
                      f"{chosen['local_indices']:>2} local indices, worst {chosen['worst']:>6}")
    print(f"\nbanks used: {dict(sorted(banks.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
