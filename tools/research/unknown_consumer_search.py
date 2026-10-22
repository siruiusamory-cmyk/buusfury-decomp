"""Widened consumer search for a range the census still calls `unknown-proven`.

The census's recorded denominator for these ranges is a search that found no consumer. This tool
runs the channels that search did not cover, and it refuses to read a hit count without a matched
null: a word can name a range by coincidence, and only a literal a second instruction also loads
is a literal pool rather than an accident.

Channels, each measured at the bytes:

  shape     the range's word classes: zero, small, ROM pointer, IWRAM pointer, odd code pointer.
  direct    every word-aligned word in the image whose value names an address inside the range,
            split into words inside the range and words outside it.
  loaders   every Thumb-1 `ldr Rd,[pc,#imm8]` whose literal names the range. A REAL literal-pool
            literal is loaded by more than one instruction; a coincidence is a singleton, so the
            report gives the loaders-per-literal distribution and the same distribution over
            same-size control windows.
  indirect  a literal names a table somewhere else in the image, and a word inside that table
            names the range.

    python tools/research/unknown_consumer_search.py --rom baserom.gba --range 0x75A738 0x76CCD4
"""

from __future__ import annotations

import argparse
import struct
import sys

ROM_BASE = 0x08000000
ROM_END = 0x0A000000
IWRAM = (0x03000000, 0x03008000)
CONTROL_STRIDE = 0x300000
CONTROL_COUNT = 12
TABLE_WINDOW = 0x100


def halfwords(rom: bytes) -> tuple[int, ...]:
    return struct.unpack_from("<%dH" % (len(rom) // 2), rom, 0)


def words(rom: bytes) -> tuple[int, ...]:
    return struct.unpack_from("<%dI" % (len(rom) // 4), rom, 0)


def shape(rom: bytes, start: int, end: int) -> dict:
    counts = {"words": 0, "zero": 0, "small": 0, "rom": 0, "iwram": 0, "odd_code": 0, "other": 0}
    for offset in range(start, end - 3, 4):
        value = struct.unpack_from("<I", rom, offset)[0]
        counts["words"] += 1
        if value == 0:
            counts["zero"] += 1
        elif value < 0x10000:
            counts["small"] += 1
        elif ROM_BASE <= value < ROM_END:
            counts["rom"] += 1
            counts["odd_code"] += value & 1
        elif IWRAM[0] <= value < IWRAM[1]:
            counts["iwram"] += 1
        else:
            counts["other"] += 1
    return counts


def direct(rom: bytes, start: int, end: int) -> dict:
    low, high = start + ROM_BASE, end + ROM_BASE
    inside = outside = 0
    sites = []
    for index, value in enumerate(words(rom)):
        if low <= value <= high:
            site = index * 4
            if start <= site < end:
                inside += 1
            else:
                outside += 1
                sites.append((site, value - ROM_BASE))
    return {"inside": inside, "outside": outside, "sites": sites}


def loader_targets(rom: bytes) -> dict[int, tuple[int, ...]]:
    half = halfwords(rom)
    out: dict[int, list[int]] = {}
    for index, value in enumerate(half):
        if value & 0xF800 != 0x4800:
            continue
        address = index * 2
        literal = ((address + 4) & ~3) + (value & 0xFF) * 4
        if literal + 4 > len(rom) or literal % 4:
            continue
        out.setdefault(literal, []).append(address)
    return {literal: tuple(sites) for literal, sites in out.items()}


def loaders(rom: bytes, start: int, end: int, targets: dict = None) -> dict:
    targets = loader_targets(rom) if targets is None else targets
    low, high = start + ROM_BASE, end + ROM_BASE
    table = words(rom)
    hits = {}
    for literal, sites in targets.items():
        value = table[literal // 4]
        if low <= value <= high:
            hits[literal] = {"value": value - ROM_BASE, "sites": sites}
    sizes = [len(hit["sites"]) for hit in hits.values()]
    return {"loaders": sum(sizes), "literals": len(hits), "hits": hits,
            "multi": sum(1 for size in sizes if size > 1),
            "largest": max(sizes, default=0),
            "distribution": {size: sizes.count(size) for size in sorted(set(sizes))}}


def control_loaders(rom: bytes, size: int, targets: dict = None,
                    stride: int = CONTROL_STRIDE, count: int = CONTROL_COUNT) -> list[dict]:
    targets = loader_targets(rom) if targets is None else targets
    table = words(rom)
    out = []
    for index in range(1, count + 1):
        start = (stride * index) % (len(rom) - size)
        low, high = start + ROM_BASE, start + size + ROM_BASE
        sizes = [len(sites) for literal, sites in targets.items()
                 if low <= table[literal // 4] <= high]
        out.append({"start": start, "loaders": sum(sizes), "literals": len(sizes),
                    "multi": sum(1 for s in sizes if s > 1), "largest": max(sizes, default=0)})
    return out


def indirect(rom: bytes, start: int, end: int, targets: dict = None,
             window: int = TABLE_WINDOW) -> dict:
    targets = loader_targets(rom) if targets is None else targets
    low, high = start + ROM_BASE, end + ROM_BASE
    table = words(rom)
    out: dict[int, list] = {}
    for literal in targets:
        value = table[literal // 4]
        if not (ROM_BASE <= value < ROM_BASE + len(rom)):
            continue
        base = value - ROM_BASE
        if base % 4:
            continue
        for step in range(min(window, len(rom) - base) // 4):
            entry = table[base // 4 + step]
            if low <= entry <= high:
                out.setdefault(base, []).append((literal, base + 4 * step, entry - ROM_BASE))
    return out


def report(rom: bytes, start: int, end: int) -> list[str]:
    targets = loader_targets(rom)
    size = end - start
    lines = ["range 0x%06X..0x%06X (%d B)" % (start, end, size)]
    counts = shape(rom, start, end)
    lines.append("  shape   words=%d zero=%d small=%d rom=%d odd_code=%d iwram=%d other=%d"
                 % (counts["words"], counts["zero"], counts["small"], counts["rom"],
                    counts["odd_code"], counts["iwram"], counts["other"]))
    hit = direct(rom, start, end)
    lines.append("  direct  words naming it: inside=%d outside=%d" % (hit["inside"],
                                                                      hit["outside"]))
    found = loaders(rom, start, end, targets)
    lines.append("  loaders loaders=%d literals=%d multi=%d largest=%d distribution=%s"
                 % (found["loaders"], found["literals"], found["multi"], found["largest"],
                    found["distribution"]))
    controls = control_loaders(rom, size, targets)
    lines.append("  null    over %d same-size controls: loaders=%s multi=%s largest=%s"
                 % (len(controls), [row["loaders"] for row in controls],
                    [row["multi"] for row in controls], [row["largest"] for row in controls]))
    for literal, data in sorted(found["hits"].items(), key=lambda item: -len(item[1]["sites"])):
        lines.append("    literal 0x%06X = 0x%08X  loaders %s"
                     % (literal, data["value"] + ROM_BASE,
                        " ".join("0x%08X" % (site + ROM_BASE) for site in data["sites"])))
    tables = indirect(rom, start, end, targets)
    lines.append("  indirect tables naming it: %d" % len(tables))
    for base, entries in sorted(tables.items(), key=lambda item: -len(item[1]))[:10]:
        lines.append("    table 0x%06X: %d entries, first %d"
                     % (base, len(entries), len(entries)))
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--range", nargs=2, action="append", metavar=("START", "END"),
                        required=True, type=lambda text: int(text, 16))
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    for start, end in args.range:
        for line in report(rom, start, end):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
