"""Recompute the character-window OAM inventory from a strip-probe run.

The observer writes one oam_<event>_<frame>.txt per snapshot containing all 128
raw OAM entries. This reads those raw words and computes the tile coverage
independently, so the inventory in the closure report does not rest on the
observer's own formatting or on a rule the observer happened to apply.

THE ADDRESSING RULE, MEASURED (run renderpath-02, canonical image, savestate
npc-front.ss1): the text object's four strip slots are 178, 242, 370 and 498,
and the four sprites that display them are a 32x64 and three 64x64 256-colour
objects. Their allocations are contiguous in 32-byte units -- 178 + 64 = 242,
242 + 128 = 370, 370 + 128 = 498, 498 + 128 = 626, where 626 is the next,
unrelated 16x16 256-colour scene sprite -- and the engine's own per-frame blit
computes 0x06010000 + slot*32 (decompiled at 0x0800ADA0; measured at
0x0800B586). So the OAM tile field is an index of 32-byte units even for an
8bpp object, and an 8bpp 8x8 cell occupies two of them, laid out consecutively.

DISPCNT bit 6 selects 1D object character mapping; bit 6 of 0x1F40 is set, so
the 1D branch is the live one. Both branches are implemented anyway.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

DISPCNT_OBJ_1D = 0x0040
OBJ_TILES = 0x06010000
WINDOW_LO, WINDOW_HI = 0x06014360, 0x06014EC0

SHAPE = {0: "square", 1: "wide", 2: "tall"}
DIMS = {
    0: {0: (8, 8), 1: (16, 16), 2: (32, 32), 3: (64, 64)},
    1: {0: (16, 8), 1: (32, 8), 2: (32, 16), 3: (64, 32)},
    2: {0: (8, 16), 1: (8, 32), 2: (16, 32), 3: (32, 64)},
}
ENTRY = re.compile(r"^\s*(\d+)\s+(0x[0-9A-Fa-f]{4})\s+(0x[0-9A-Fa-f]{4})\s+(0x[0-9A-Fa-f]{4})\s*$")


def coverage(a0: int, a1: int, a2: int, one_d: bool):
    if a0 & 0x0200:
        return None
    shape, size = (a0 >> 14) & 3, (a1 >> 14) & 3
    if shape not in DIMS:
        return None
    w, h = DIMS[shape][size]
    eight = bool(a0 & 0x2000)
    units = 2 if eight else 1
    cells = (w // 8) * (h // 8)
    base = a2 & 0x3FF
    if one_d:
        lo = OBJ_TILES + base * 32
        hi = lo + cells * units * 32 - 1
    else:
        positions = [
            base + (cx * units) + (cy * 32) for cy in range(h // 8) for cx in range(w // 8)
        ]
        lo = OBJ_TILES + min(positions) * 32
        hi = OBJ_TILES + (max(positions) + units) * 32 - 1
    return {
        "w": w,
        "h": h,
        "eight": eight,
        "lo": lo,
        "hi": hi,
        "x": a1 & 0x1FF,
        "y": a0 & 0xFF,
        "tile": base,
        "affine": (a0 >> 8) & 1,
        "pal": (a2 >> 12) & 0xF,
        "pri": (a2 >> 10) & 3,
        "shape": SHAPE[shape],
        "size": size,
    }


def parse(path: Path):
    frame = event = dispcnt = None
    entries: dict[int, tuple[int, int, int]] = {}
    for line in path.read_text(encoding="ascii", errors="replace").splitlines():
        if line.startswith("frame "):
            parts = line.split()
            frame, event = int(parts[1]), parts[3]
            dispcnt = int(parts[5], 16)
            break
    in_raw = False
    for line in path.read_text(encoding="ascii", errors="replace").splitlines():
        if line.startswith("--- all 128 raw entries"):
            in_raw = True
            continue
        if in_raw:
            match = ENTRY.match(line)
            if match:
                index = int(match.group(1))
                entries[index] = tuple(int(match.group(n), 16) for n in (2, 3, 4))
    return frame, event, dispcnt, entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--quiet", action="store_true", help="only the summary lines")
    args = parser.parse_args()

    snapshots = 0
    covers: dict[int, int] = {}
    positions: dict[int, set] = {}
    for path in sorted(args.run_dir.glob("oam_*.txt")):
        frame, event, dispcnt, entries = parse(path)
        if dispcnt is None or not entries:
            continue
        snapshots += 1
        one_d = bool(dispcnt & DISPCNT_OBJ_1D)
        covered = []
        for index in sorted(entries):
            span = coverage(*entries[index], one_d)
            if span and span["lo"] < WINDOW_HI and span["hi"] >= WINDOW_LO:
                covered.append((index, span))
                covers[index] = covers.get(index, 0) + 1
                positions.setdefault(index, set()).add(
                    (span["tile"], span["x"], span["y"], span["shape"], span["size"],
                     span["eight"], span["affine"], span["pri"], span["lo"], span["hi"])
                )
        if not args.quiet:
            rendered = ", ".join(
                f"{i}:t{s['tile']}({s['shape']}{s['size']} "
                f"{'8bpp' if s['eight'] else '4bpp'} xy={s['x']},{s['y']} pri={s['pri']})"
                for i, s in covered
            )
            print(f"f={frame:5d} {event:7s} enabled={sum(1 for e in entries.values() if e[0] and not e[0] & 0x0200):3d}"
                  f" covering={len(covered)} [{rendered}]")

    print()
    print(f"snapshots                 : {snapshots}")
    print(f"distinct OAM indices seen covering the window: {len(covers)}")
    for index in sorted(covers):
        variants = positions[index]
        stable = "STABLE" if len(variants) == 1 else f"{len(variants)} DISTINCT STATES"
        sample = next(iter(variants))
        print(f"  index {index:3d}: seen {covers[index]:3d}/{snapshots}  {stable}"
              f"  tile={sample[0]} xy={sample[1]},{sample[2]}"
              f" {sample[3]}{sample[4]} {'8bpp' if sample[5] else '4bpp'}"
              f" affine={sample[6]} pri={sample[7]} bytes={sample[8]:#010x}..{sample[9]:#010x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
