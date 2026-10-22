from __future__ import annotations

import argparse
import struct
import sys

THUMB_LDR_LITERAL = 0xF800
THUMB_LDR_BASE = 0x4800
ARM_LDR_LITERAL_MASK = 0x0F7F0000
ARM_LDR_LITERAL_PATTERN = 0x051F0000
ROM_BASE = 0x08000000
KNOWN_LITERAL_FILE_OFFSETS = (0x0008F8, 0x004210, 0x00545C, 0x008D10)
KNOWN_TABLE = 0x083BB78C


def thumb_sites(rom: bytes):
    out = []
    count = len(rom) // 2
    half = struct.unpack_from("<%dH" % count, rom, 0)
    for index, value in enumerate(half):
        if value & THUMB_LDR_LITERAL != THUMB_LDR_BASE:
            continue
        address = index * 2
        pc = (address + 4) & ~3
        out.append((ROM_BASE + address, ROM_BASE + pc + 4 * (value & 0xFF)))
    return out


def arm_sites(rom: bytes):
    out = []
    count = len(rom) // 4
    words = struct.unpack_from("<%dI" % count, rom, 0)
    for index, value in enumerate(words):
        if value & ARM_LDR_LITERAL_MASK != ARM_LDR_LITERAL_PATTERN:
            continue
        address = index * 4
        offset = value & 0xFFF
        if not value & (1 << 23):
            offset = -offset
        out.append((ROM_BASE + address, ROM_BASE + address + 8 + offset))
    return out


def scan(rom: bytes):
    return {"thumb": sorted(thumb_sites(rom)),
            "arm": sorted(arm_sites(rom))}


def into(sites, start: int, end: int):
    return [(site, target) for site, target in sites if start <= target < end]


def loads_into(rom: bytes, sites, start: int, end: int):
    out = []
    for kind in ("thumb", "arm"):
        for site, target in sites[kind]:
            offset = target - ROM_BASE
            if not 0 <= offset <= len(rom) - 4:
                continue
            value = struct.unpack_from("<I", rom, offset)[0]
            if start <= value < end:
                out.append((kind, site, target, value))
    return out


def report(rom, sites, start, end):
    denominator = ("%d Thumb + %d ARM ldr-literal sites (linear sweep at instruction origin; "
                   "reachability of an individual site is a separate question, P-090)"
                   % (len(sites["thumb"]), len(sites["arm"])))
    lines = ["range 0x%08X..0x%08X, %d B" % (start, end, end - start)]
    direct = into(sites["thumb"], start, end) + into(sites["arm"], start, end)
    lines.append("  computes an address inside the range: %d (inside a data range these are the "
                 "range's own bytes decoded as instructions, not references)" % len(direct))
    for site, target in direct[:12]:
        lines.append("      site 0x%08X -> 0x%08X" % (site, target))
    if len(direct) > 12:
        lines.append("      ... %d more" % (len(direct) - 12))
    refs = loads_into(rom, sites, start, end)
    lines.append("  loads a word that IS an address inside the range: %d" % len(refs))
    for kind, site, target, value in refs[:24]:
        lines.append("      %-5s site 0x%08X pool 0x%08X = 0x%08X" % (kind, site, target, value))
    if len(refs) > 24:
        lines.append("      ... %d more" % (len(refs) - 24))
    lines.append("  denominator: " + denominator)
    return lines


def self_check(rom: bytes) -> int:
    sites = scan(rom)
    assert sites["thumb"] and sites["arm"], "a matcher fired nowhere in a whole image"
    for kind in ("thumb", "arm"):
        site, target = sites[kind][0]
        assert into(sites[kind], target, target + 1) == [(site, target)], \
            "the %s matcher does not find the site it just decoded" % kind
    assert into(sites["thumb"], 0x08FFFF00, 0x08FFFF04) == [], \
        "a target outside the image reported a site"
    words = [struct.unpack_from("<I", rom, offset)[0] for offset in KNOWN_LITERAL_FILE_OFFSETS]
    assert words == [KNOWN_TABLE] * 4, "the known literal words moved: %s" % [hex(w) for w in words]
    found = loads_into(rom, sites, KNOWN_TABLE, KNOWN_TABLE + 1)
    assert len(found) >= 4, "the value route found %d of the 4 known sites" % len(found)
    assert {site for _, site, _, _ in found} >= {0x080008BC, 0x080041BA, 0x080053F8, 0x08008C86}, \
        "the value route missed a known site: %s" % sorted(hex(s) for _, s, _, _ in found)
    print("self-check: %d Thumb + %d ARM ldr-literal sites; the value route finds the 4 known "
          "sites naming 0x%08X" % (len(sites["thumb"]), len(sites["arm"]), KNOWN_TABLE))
    return 0


def as_address(value):
    return value + ROM_BASE if value < ROM_BASE else value


def parse_range(text):
    low, high = text.split(":")
    return as_address(int(low, 0)), as_address(int(high, 0))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--into", default="")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    if args.self_check:
        return self_check(rom)
    if not args.into:
        parser.error("--into START:END or --self-check")
    start, end = parse_range(args.into)
    print("\n".join(report(rom, scan(rom), start, end)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
