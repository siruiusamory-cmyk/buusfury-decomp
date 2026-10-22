from __future__ import annotations

import argparse
import csv
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import assetdir  # noqa: E402
import assetdir2  # noqa: E402
import assetdirectory  # noqa: E402

ROM_BASE = 0x08000000
CODE_END = 0x46000
MUSIC_BASE = 0x3BB78C
MUSIC_STRIDE = 20
MUSIC_COUNT = 53
MUSIC_SAMPLES = 8
MUSIC_CALL = 0x0803F110
RECORD_CALL = 0x0803E378
OBJECT_POOL = 0x0803E7A8
OBJECT_POOL_VALUE = 0x087B6724
OBJECT_WORD = 0x087B6720
OBJECT_VALUE = 0x030038A4
SAMPLES_PATH = (
    (0x0803E536, 0x4B9C, "ldr r3, [pc, #0x270]"),
    (0x0803E53A, 0x3B04, "subs r3, #4"),
    (0x0803E53C, 0x681B, "ldr r3, [r3]"),
    (0x0803E540, 0x68DB, "ldr r3, [r3, #0xc]"),
    (0x0803E542, 0x689D, "ldr r5, [r3, #8]"),
    (0x0803E544, 0x0053, "lsls r3, r2, #1"),
    (0x0803E546, 0x189A, "adds r2, r3, r2"),
    (0x0803E548, 0x0092, "lsls r2, r2, #2"),
    (0x0803E54A, 0x18AA, "adds r2, r5, r2"),
    (0x0803E54C, 0x6282, "str r2, [r0, #0x28]"),
    (0x0803F11C, 0x60C1, "str r1, [r0, #0xc]"),
    (0x0803E0FA, 0x6A82, "ldr r2, [r0, #0x28]"),
)
DIRECTORIES = (assetdir, assetdir2)
TABLE_FIELDS = ("directory", "index", "record_offset", "block_offset", "byte_length",
                "data_ptr", "flags", "unit", "tied", "missing")

PINNED = (
    (0x080008BC, 0x4A0E, "ldr r2, [pc, #0x38]"),
    (0x080041BA, 0x4A15, "ldr r2, [pc, #0x54]"),
    (0x080053F8, 0x4A18, "ldr r2, [pc, #0x60]"),
    (0x08008C86, 0x4A22, "ldr r2, [pc, #0x88]"),
    (0x0800082A, 0x4931, "ldr r1, [pc, #0xc4]"),
    (0x0800082C, 0x0043, "lsls r3, r0, #1"),
    (0x0800082E, 0x1818, "adds r0, r3, r0"),
    (0x08000830, 0x0080, "lsls r0, r0, #2"),
    (0x08000832, 0x1841, "adds r1, r0, r1"),
    (0x0800083A, 0xF03D, "bl 0x0803E378"),
    (0x0803E0FC, 0x6813, "ldr r3, [r2]"),
    (0x0803E100, 0x88D3, "ldrh r3, [r2, #6]"),
    (0x0803E106, 0x8913, "ldrh r3, [r2, #8]"),
    (0x0803E10C, 0x8953, "ldrh r3, [r2, #0xa]"),
    (0x0803E110, 0x7912, "ldrb r2, [r2, #4]"),
    (0x0803E38E, 0x6281, "str r1, [r0, #0x28]"),
)


def halfword(rom: bytes, address: int) -> int:
    return struct.unpack_from("<H", rom, address - ROM_BASE)[0]


def word(rom: bytes, address: int) -> int:
    return struct.unpack_from("<I", rom, address - ROM_BASE)[0]


def bl_target(rom: bytes, address: int) -> int:
    first, second = struct.unpack_from("<HH", rom, address - ROM_BASE)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        raise ValueError("%#x is not a Thumb long branch" % address)
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    offset = (sign << 23) | ((1 - (j1 ^ sign)) << 22) | ((1 - (j2 ^ sign)) << 21)
    offset |= ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    if sign:
        offset -= 1 << 24
    return address + 4 + offset


def literal_sites(rom: bytes, address: int) -> list[int]:
    sites = []
    for offset in range(0, CODE_END, 2):
        value = struct.unpack_from("<H", rom, offset)[0]
        if value & 0xF800 != 0x4800:
            continue
        pool = ((offset + 4) & ~3) + (value & 0xFF) * 4
        if struct.unpack_from("<I", rom, pool)[0] == address:
            sites.append(ROM_BASE + offset)
    return sites


def calls(rom: bytes, site: int, target: int) -> list[int]:
    found = []
    for address in range(site, site + 0x24, 2):
        try:
            reached = bl_target(rom, address)
        except ValueError:
            continue
        if reached == target:
            found.append(address)
    return found


def reach(rom: bytes, base: int) -> list[int]:
    return [site for site in literal_sites(rom, ROM_BASE + base) if calls(rom, site, RECORD_CALL)]


def sample_bank(rom: bytes) -> bool:
    if word(rom, OBJECT_POOL) != OBJECT_POOL_VALUE or word(rom, OBJECT_WORD) != OBJECT_VALUE:
        return False
    return all(halfword(rom, address) == value for address, value, _text in SAMPLES_PATH)


def tied_run(rom: bytes, module) -> bool:
    if reach(rom, module.BASE):
        return True
    return (sample_bank(rom)
            and all(row["samples"] == ROM_BASE + module.BASE for row in music(rom)))


def music(rom: bytes) -> list[dict]:
    rows = []
    for index in range(MUSIC_COUNT):
        words = struct.unpack_from("<5I", rom, MUSIC_BASE + MUSIC_STRIDE * index)
        rows.append({"index": index, "offset": MUSIC_BASE + MUSIC_STRIDE * index,
                     "entries": words[0], "ramp": words[1], "samples": words[2],
                     "block": words[3], "count": words[4]})
    return rows


def names(rom: bytes, address: int) -> list[int]:
    pattern = struct.pack("<I", address)
    found, offset = [], rom.find(pattern)
    while offset >= 0:
        if offset % 4 == 0:
            found.append(offset)
        offset = rom.find(pattern, offset + 1)
    return found


def evidence(rom: bytes) -> list[tuple]:
    rows = [(address, text, halfword(rom, address) == value)
            for address, value, text in PINNED + SAMPLES_PATH]
    rows.append((0x080008BC, "four sites load 0x083bb78c and call 0x0803f110",
                 len([site for site in literal_sites(rom, MUSIC_BASE + ROM_BASE)
                      if calls(rom, site, MUSIC_CALL)]) == 4))
    rows.append((MUSIC_BASE + ROM_BASE, "all 53 music records name the 79-record table at +8",
                 all(row["samples"] == ROM_BASE + assetdir2.BASE for row in music(rom))))
    rows.append((OBJECT_POOL, "the +8 reader resolves the music object through 0x087b6720"
                 " and stores the indexed record at slot+0x28", sample_bank(rom)))
    return rows


def models(rom: bytes, module) -> list[dict]:
    rows = []
    for index, (offset, size) in enumerate(module.block_rows(rom)):
        record = module.fields(rom, module.BASE + assetdirectory.STRIDE * index,
                               assetdirectory.STRIDE)
        rows.append({"directory": module.DIRECTORY, "index": index,
                     "record_offset": module.BASE + assetdirectory.STRIDE * index,
                     "block_offset": offset, "byte_length": size,
                     "data_ptr": record["data_ptr"], "flags": record["flags"],
                     "unit": record["unit"],
                     "samples": assetdirectory.decode_stream(rom[offset:offset + size])})
    return rows


def survey(rom: bytes) -> list[dict]:
    rows = []
    for module in DIRECTORIES:
        tied = tied_run(rom, module)
        missing = ""
        if not tied:
            named = len([row for row in music(rom)
                         if row["samples"] == ROM_BASE + module.BASE])
            holds = names(rom, ROM_BASE + module.BASE)
            inside = len([site for site in holds
                          if MUSIC_BASE <= site < MUSIC_BASE + MUSIC_STRIDE * MUSIC_COUNT])
            missing = ("no literal site names %#010x and calls %#010x; %d of the %d music records "
                       "name it at +8; %d word(s) in the image hold it, %d inside the music table"
                       % (ROM_BASE + module.BASE, RECORD_CALL, named, MUSIC_COUNT, len(holds),
                          inside))
        for row in models(rom, module):
            row["tied"] = tied
            row["missing"] = missing
            rows.append(row)
    return rows


def verdicts(rom: bytes) -> list[tuple]:
    return [(module.DIRECTORY, tied_run(rom, module), module.TIED)
            for module in DIRECTORIES]


def total(rows: list[dict], tied: bool) -> tuple[int, int]:
    kept = [row for row in rows if row["tied"] == tied]
    return len(kept), sum(row["byte_length"] for row in kept)


def write_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="\n", encoding="ascii") as handle:
        writer = csv.DictWriter(handle, TABLE_FIELDS, restval="")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in TABLE_FIELDS})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--csv")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    rows = evidence(rom)
    for address, text, held in rows:
        print("evidence %08x %-58s %s" % (address, text, "PASS" if held else "FAIL"))
    for name, reached, declared in verdicts(rom):
        print("verdict  %-24s reached=%-5s declared=%s %s"
              % (name, reached, declared, "PASS" if reached == declared else "FAIL"))
    held = all(row[2] for row in rows) and all(reached == declared
                                               for _name, reached, declared in verdicts(rom))
    survey_rows = survey(rom)
    for module in DIRECTORIES:
        kept = [row for row in survey_rows if row["directory"] == module.DIRECTORY]
        tied, tied_bytes = total(kept, True)
        untied, untied_bytes = total(kept, False)
        print("%-26s %3d records %7d B tied %3d / %7d B untied %3d / %7d B"
              % (module.DIRECTORY, len(kept), sum(row["byte_length"] for row in kept),
                 tied, tied_bytes, untied, untied_bytes))
        for row in kept:
            if not row["tied"]:
                print("missing %-24s %s" % (module.DIRECTORY, row["missing"]))
                break
    tied, tied_bytes = total(survey_rows, True)
    untied, untied_bytes = total(survey_rows, False)
    print("tied %d records %d B; untied %d records %d B; total %d records %d B"
          % (tied, tied_bytes, untied, untied_bytes, len(survey_rows),
             tied_bytes + untied_bytes))
    if args.csv:
        write_csv(survey_rows, args.csv)
        print("wrote %s" % args.csv)
    return 0 if held else 1


if __name__ == "__main__":
    sys.exit(main())
