"""Attribute every `graphics` census row byte to exactly one measured cause, and assert the sums.

    python tools/research/residual_causes.py            # print the table
    python tools/research/residual_causes.py --check    # refuse unless the causes sum to the rows

GRAPHICS-RESIDUAL-002's instrument, restated after GRAPHICS-SPLICE-001 completed its one route. The
causes, in priority order per byte:

  dominant_record_unreached  the retail section starts with a DOMINANT layer record no root slot names
  container_the_scan_missed  the section decodes as a kind-1 container the packed scan's greedy walk
                           skipped
  address_dense            >= half of the section's 4-byte grid holds ROM addresses, no count field
  opaque                   no structural test fires

The two root-named families this table used to report as `root_named_table_staged` (926 x 24 B and
735 x 4 B, 25,164 B) are planned by the map emitter now, so they are no census row and the cause has
no byte left; `--check` refuses a cause that holds ROWS and claims no byte, which is what makes the
removal a measured step rather than a judgement - a cause with neither row nor byte is EXHAUSTED
(GRAPHICS-RESIDUAL-003 converted every row two of these four claims, so it prints 0 / 0). The sprite block is not classified here: its ten rows are per-animation
grids whose extent the code does not state (see docs/research/ROUTE_TO_100.md, the `graphics` route).

GRAPHICS-RESIDUAL-006: the map block's set (b) (62 rows / 31,808 B) is named by a child list's address
words - `naming` measures 57 rows named at their own start against 4 under the byte-permuted null - but
no code site reads the list, the index array or the row (`own_lists` is the only shape rule the bytes
pass), so the set has no format to convert and `--rows` prints its `reader` as `unproven`.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import os
import random
import struct
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))

CENSUS = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
MANIFEST = os.path.join(HERE, "..", "mapcontainer", "mapcontainer_manifest.csv")
CAUSES = ("dominant_record_unreached", "container_the_scan_missed", "address_dense", "opaque")

import mapcontainer
import webfoot_lz


def container_at(rom, start, end):
    if end - start < 8 or struct.unpack_from("<I", rom, start)[0] > 2:
        return None
    try:
        container = webfoot_lz.validate_retail_termination(
            rom, start, maximum_output=webfoot_lz.DEFAULT_MAX_OUTPUT)
    except webfoot_lz.ContainerError:
        return None
    return container if container.packed_end <= end else None


def classified(rom):
    import generate_mapcontainer as generator

    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    generator.set_block("map")
    _, sections, _ = generator.read_plan(rom, os.path.join(HERE, "..", "mapcontainer",
                                                           "mapcontainer_manifest.csv"))
    retail = sorted((section.start, section.end) for section in sections if section.kind == "retail")
    cause = {}
    for start, end in retail:
        if u32(start) == mapcontainer.DOMINANT:
            cause[start] = "dominant_record_unreached"
        elif container_at(rom, start, end) is not None:
            cause[start] = "container_the_scan_missed"
        else:
            addresses = words = 0
            for offset in range(start, end - 3, 4):
                words += 1
                addresses += 0x08000000 <= u32(offset) < 0x08000000 + len(rom)
            cause[start] = "address_dense" if words and 2 * addresses >= words else "opaque"
    return retail, cause


def nulls(rom, rows, cause_of):
    arrays = mapcontainer.root_arrays(rom)
    real = mapcontainer.root_slots(rom)
    permuted = bytearray(rom)
    for base, limit in arrays:
        blob = bytearray(rom[base:limit])
        random.Random(base).shuffle(blob)
        permuted[base:limit] = blob
    shuffled = mapcontainer.root_slots(bytes(permuted))

    retail, cause = classified(rom)
    starts = [start for start, _ in retail]
    holding = {retail[bisect.bisect_right(starts, start) - 1][0] for start, _ in rows}
    sections = [(start, end) for start, end in retail
                if cause[start] == "container_the_scan_missed"]
    with_rows = [(start, end) for start, end in sections if start in holding]
    decoded = set()
    for start, end in sections:
        copy = bytearray(rom)
        blob = bytearray(rom[start:end])
        random.Random(start).shuffle(blob)
        copy[start:end] = blob
        if container_at(bytes(copy), start, end) is not None:
            decoded.add(start)

    print("cause 1 variant-slot roots")
    print("  %-30s %6d %6d" % ("arrays walked", len(arrays), len(arrays)))
    real_slots, null_slots = (sum(len(s) for s in real), sum(len(s) for s in shuffled))
    real_roots, null_roots = (len({r for s in real for r in s}), len({r for s in shuffled for r in s}))
    real_two, null_two = (sum(1 for s in real if len(s) > 1), sum(1 for s in shuffled if len(s) > 1))
    print("  %-30s %6d %6d" % ("slots resolving", real_slots, null_slots))
    print("  %-30s %6d %6d" % ("distinct roots", real_roots, null_roots))
    print("  %-30s %6d %6d" % ("arrays holding two", real_two, null_two))
    print("  %-30s %6d %6d" % ("arrays whose own word survived the shuffle",
                               len(arrays), sum(1 for base, limit in arrays
                                                if bytes(permuted[base:limit]) == rom[base:limit])))
    print("cause 2 container_the_scan_missed")
    print("  %-30s %6d %6d" % ("sections decoding", len(sections), len(decoded)))
    print("  %-30s %6d %6d" % ("of which hold a census row", len(with_rows),
                               sum(1 for start, _ in with_rows if start in decoded)))
    print("  %-30s %6d %6d" % ("bytes in those rows", 
                               sum(1 for start, end in rows for offset in range(start, end)
                                   if cause_of(offset) == "container_the_scan_missed"), 0))
    plan = plan_of(rom)
    real_tail, null_tail = child_rows(rom, plan)
    print("family child-list row (this ticket)")
    print("  %-30s %6d %6d" % ("rows parsing to their own extent", real_tail[0], null_tail[0]))
    print("  %-30s %6d %6d" % ("bytes", real_tail[1], null_tail[1]))
    real_gap, null_gap = gap_null(rom)
    print("family child-list row, gap-level discovery (AMENDMENT A)")
    print("  %-30s %6d %6d" % ("rows", real_gap[0], null_gap[0]))
    print("  %-30s %6d %6d" % ("bytes", real_gap[1], null_gap[1]))
    labels = named(rom, rows, plan)
    real_naming, null_naming = naming(rom, [row for row in rows
                                            if "map-root-field" not in labels[row][0]], plan)
    print("family child-list naming of the set (b) rows (this ticket)")
    print("  %-30s %6d %6d" % ("rows named at their own start", real_naming[0], null_naming[0]))
    print("  %-30s %6d %6d" % ("address words landing in a row", real_naming[1], null_naming[1]))
    return {"slots": (real_slots, null_slots), "roots": (real_roots, null_roots),
            "two": (real_two, null_two), "sections": (len(sections), len(decoded)),
            "rows": (real_tail[0], null_tail[0]),
            "discovery": (real_gap[0], null_gap[0]),
            "naming": (real_naming[0], null_naming[0])}


def discovered(rom, span, claimed, gaps):
    permuted = bytearray(rom)
    for low, high in gaps:
        blob = bytearray(rom[low:high])
        random.Random(low).shuffle(blob)
        permuted[low:high] = blob
    rows = mapcontainer.mode_row_sites(bytes(permuted), span, claimed)
    return len(rows), sum(size for _, size in rows)


def gap_null(rom):
    import generate_mapcontainer as generator

    seen = []
    original = mapcontainer.mode_row_sites
    mapcontainer.mode_row_sites = lambda *arguments: (seen.append(arguments),
                                                      original(*arguments))[1]
    try:
        generator.set_block("map")
        _, _, plan = generator.read_plan(rom, MANIFEST)
    finally:
        mapcontainer.mode_row_sites = original
    _, span, claimed = seen[-1]
    gaps, cursor = [], span[0]
    for low, high in sorted((max(span[0], low), min(span[1], high)) for low, high in claimed):
        if low > cursor:
            gaps.append((cursor, low))
        cursor = max(cursor, high)
    if cursor < span[1]:
        gaps.append((cursor, span[1]))
    real = plan["all"][mapcontainer.MODE_ROW]
    return ((len(real), sum(size for _, size in real)), discovered(rom, span, claimed, gaps))


def plan_of(rom):
    import generate_mapcontainer as generator

    generator.set_block("map")
    return generator.read_plan(rom, MANIFEST)[2]


def lists_at(rom, offset, end):
    out, cursor = [], offset
    while cursor + 4 <= end:
        count, tag = rom[cursor], struct.unpack_from("<H", rom, cursor + 2)[0]
        if not 1 <= count <= mapcontainer.MODE_MAX_CHILDREN or tag not in mapcontainer.MODE_TAGS:
            break
        size = 4 + 4 * count
        pointers = [struct.unpack_from("<I", rom, cursor + 4 + 4 * index)[0]
                    for index in range(count)]
        if cursor + size > end or not all(mapcontainer.ROM_BASE <= pointer <
                                          mapcontainer.ROM_BASE + len(rom)
                                          for pointer in pointers):
            break
        out.append((cursor, count, pointers))
        cursor += size
    return out


def child_lists(rom, plan):
    return [(offset, count, pointers)
            for at, size in plan["all"][mapcontainer.MODE_ROW]
            for offset, count, pointers in lists_at(rom, at, at + size)]


def naming(rom, rows, plan=None):
    plan = plan or plan_of(rom)

    def measured(values):
        aligned, words = set(), 0
        for value in values:
            target = value - mapcontainer.ROM_BASE
            for start, end in rows:
                if start <= target < end:
                    words += 1
                    if target == start:
                        aligned.add(start)
                    break
        return len(aligned), words

    lists = child_lists(rom, plan)
    real = measured([pointer for _, _, pointers in lists for pointer in pointers])
    permuted = bytearray(rom)
    for offset, count, _ in lists:
        blob = bytearray(rom[offset + 4:offset + 4 + 4 * count])
        random.Random(offset).shuffle(blob)
        permuted[offset + 4:offset + 4 + 4 * count] = blob
    null = measured([struct.unpack_from("<I", permuted, offset + 4 + 4 * index)[0]
                     for offset, count, _ in lists for index in range(count)])
    return real, null


def own_lists(rom, rows):
    return {(start, end): len(lists_at(rom, start, end)) for start, end in rows}


def child_rows(rom, plan=None):
    claimed = (plan or plan_of(rom))["all"][mapcontainer.MODE_ROW]
    real = null = 0
    real_bytes = null_bytes = 0
    for at, size in claimed:
        parsed = mapcontainer.mode_row_fields(rom, at, at + size)
        if parsed is not None and parsed[1] == size:
            real += 1
            real_bytes += size
        permuted = bytearray(rom)
        body = bytearray(rom[at:at + size])
        random.Random(at).shuffle(body)
        permuted[at:at + size] = body
        parsed = mapcontainer.mode_row_fields(bytes(permuted), at, at + size)
        if parsed is not None and parsed[1] == size:
            null += 1
            null_bytes += size
    return (real, real_bytes), (null, null_bytes)


def measured(rom):
    import generate_mapcontainer as generator

    retail, cause = classified(rom)
    starts = [start for start, _ in retail]

    def cause_of(offset):
        section = bisect.bisect_right(starts, offset) - 1
        return cause[retail[section][0]]

    rows = [(int(row["start"], 16), int(row["end"], 16))
            for row in csv.DictReader(open(CENSUS, encoding="utf-8"))
            if row["class"] == "graphics"
            and int(row["start"], 16) >= generator.MAP.start
            and int(row["end"], 16) <= generator.MAP.end]
    return rows, cause_of


def named(rom, rows, plan=None):
    plan = plan or plan_of(rom)
    u32 = lambda at: struct.unpack_from("<I", rom, at)[0]
    inrom = lambda value: mapcontainer.ROM_BASE <= value < mapcontainer.ROM_BASE + len(rom)
    pointers = {}

    def citing(at, family):
        value = u32(at)
        if inrom(value):
            pointers.setdefault(value - mapcontainer.ROM_BASE, set()).add(family)

    for family, extents in plan["all"].items():
        for offset, size in extents:
            if size >= 4:
                for at in range(offset, offset + size - 3, 4):
                    citing(at, family)
    for root in mapcontainer.map_roots(rom):
        for at in range(root, root + 0x50 - 3, 4):
            citing(at, "map-root-field")
    from_row = {}
    for start, end in rows:
        for at in range(start, end - 3, 4):
            value = u32(at)
            if inrom(value):
                from_row.setdefault(value - mapcontainer.ROM_BASE, set()).add(start)
    out = {}
    for start, end in rows:
        cites = {family for family, extents in plan["all"].items()
                 for offset, size in extents if start <= offset < end}
        others = set()
        for target in range(start, end):
            cites |= pointers.get(target, set())
            others |= from_row.get(target, set())
        if others - {start}:
            cites.add("census_row")
        parsed = mapcontainer.mode_row_fields(rom, start, end)
        out[(start, end)] = ("+".join(sorted(cites)) or "none", parsed[1] if parsed else 0)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--nulls", action="store_true", help="the converted causes beside their null")
    parser.add_argument("--rows", help="write the per-row table to this CSV")
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    rows, cause_of = measured(rom)
    tally, by_row = Counter(), Counter()
    for start, end in rows:
        by_row[cause_of(start)] += 1
        for offset in range(start, end):
            tally[cause_of(offset)] += 1
    print("cause                      bytes   rows")
    for cause in CAUSES:
        print("  %-24s %6d %6d" % (cause, tally[cause], by_row[cause]))
    total = sum(end - start for start, end in rows)
    print("  %-24s %6d %6d" % ("total", sum(tally.values()), sum(by_row.values())))
    if args.nulls or args.check:
        measured_nulls = nulls(rom, rows, cause_of)
        for name, (real, null) in measured_nulls.items():
            if real <= null:
                raise SystemExit("the cause's %s reads %d against a byte-permuted null of %d, so the "
                                 "family does not beat its null" % (name, real, null))
        print("NULLS PASS: every converted cause beats its byte-permuted null")
    if args.check:
        for cause in CAUSES:
            if by_row[cause] and not tally[cause]:
                raise SystemExit("the cause %s has %d row(s) and no byte, so it is not measured"
                                 % (cause, by_row[cause]))
        if sum(tally.values()) != total or sum(by_row.values()) != len(rows):
            raise SystemExit("the causes sum to %d B / %d rows, the rows hold %d B / %d"
                             % (sum(tally.values()), sum(by_row.values()), total, len(rows)))
        print("CHECK PASS: %d rows / %d B attributed exactly once" % (len(rows), total))
    if args.rows:
        table = named(rom, rows)
        lists = own_lists(rom, rows)
        with open(args.rows, "w", encoding="utf-8", newline="") as handle:
            handle.write("start,end,bytes,cause,named_by,row_prefix,reader,lists\n")
            for start, end in rows:
                named_by, prefix = table[(start, end)]
                reader = "root_plus_0x10_data_only" if "map-root-field" in named_by else "unproven"
                handle.write("%08X,%08X,%d,%s,%s,%d,%s,%d\n"
                             % (start, end, end - start, cause_of(start), named_by, prefix,
                                reader, lists[(start, end)]))
        print("wrote %s (%d rows)" % (args.rows, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
