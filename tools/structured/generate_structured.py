"""Extract, emit and verify the eight structured families of region A and region B.

Region A is the slice 0x071C90..0x0945C0 and region B is 0x179764..0x179A50; both stop
being INCBIN slices and become one generated file per contiguous run of family extents,
alternating with retail gaps written from the image.

  extract  walk the eight families, adjudicate the overlaps, write the payload store
  build    emit the generated runs from the store and the retail gaps from the image
  verify   re-derive every member from the image and check the source's INCBIN tokens
  ledger   append one row per generated run
  measure  print the measured plan and write nothing

MISS COUNT, which the gate reads as `encode_cache_misses=<n> trusted=1 total=<n>`: this
block has no encoder, so a MISS is a section file this run had to WRITE - the section
population is `total` (region A's 462 generated + 461 retail gaps, plus region B's one
generated file = 924). A warm no-op reports misses=0 total=924 and rewrites nothing; an
edit of one store member reports misses=1.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import families
import emitted  # noqa: E402
import gate  # noqa: E402
import payload_store

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
OUT_DIR = "build/structured"
MANIFEST_FIELDS = ("kind", "start", "end", "bytes", "family", "members", "whole_fragment")
MEMBER_FIELDS = ("store_key", "family", "start", "end", "bytes", "extent_start", "extent_end",
                 "whole_fragment", "blob_offset")


def resolve(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def read_rom(path):
    data = open(path, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ROM_SHA256:
        raise SystemExit("ROM sha256 %s is not the canonical %s" % (digest, ROM_SHA256))
    if len(data) != families.ROM_SIZE:
        raise SystemExit("ROM is %d bytes" % len(data))
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def section_output(section):
    if section[0] == "generated":
        return os.path.join(OUT_DIR, "gen_%x_%x.bin" % (section[1], section[2]))
    return "baserom.gba_0x%x_0x%x.extracted" % (section[1], section[2])


def planned_sections(built):
    region_a = [("generated", start, end) for start, end in built.runs
                if start < families.REGION_A[1]]
    region_b = [("generated", start, end) for start, end in built.runs
                if start >= families.REGION_A[1]]
    merged = []
    cursor = families.REGION_A[0]
    for section in region_a:
        if section[1] > cursor:
            merged.append(("retail", cursor, section[1]))
        merged.append(section)
        cursor = section[2]
    if cursor < families.REGION_A[1]:
        merged.append(("retail", cursor, families.REGION_A[1]))
    return merged + region_b


def member_payloads(rom, built):
    rows = families.record_extents(rom)
    full = {}
    out = {}
    for member in built.members:
        key = (member.family, member.extent_start, member.extent_end)
        if key not in full:
            full[key] = families.payload(rom, member.family, member.extent_start,
                                         member.extent_end, rows[member.family])
        blob = full[key]
        out[member.key] = (member.family, member.start, member.end,
                           blob[member.start - member.extent_start:
                                member.end - member.extent_start])
    return out


def run_of(built, key):
    for run in built.runs:
        if run[0] <= key < run[1]:
            return run
    raise SystemExit("member %#x is in no run" % key)


def cmd_extract(args):
    rom = read_rom(resolve(args.rom))
    built = families.assert_contract(rom)
    payloads = member_payloads(rom, built)
    os.makedirs(resolve(args.payloads), exist_ok=True)
    stamped = payload_store.write(payload_store.path(resolve(args.payloads)),
                                  [(key, blob) for key, (_, _, _, blob) in payloads.items()])
    per_family = {}
    for key, (family, start, end, blob) in payloads.items():
        count, total = per_family.get(family, (0, 0))
        per_family[family] = (count + 1, total + len(blob))
    for family in families.FAMILY_ORDER:
        count, total = per_family.get(family, (0, 0))
        print("family %-28s members=%3d bytes=%6d" % (family, count, total))
    print("members=%d bytes=%d extents=%d clipped=%d"
          % (len(payloads), sum(len(blob) for _, _, _, blob in payloads.values()),
             sum(len(rows) for rows in built.extents.values()),
             sum(built.clipped.values())))
    print("wrote %d members to %s, %d bytes"
          % (len(payloads), payload_store.path(resolve(args.payloads)), stamped[0]))
    return 0


def cmd_build(args):
    started = time.perf_counter()
    rom = read_rom(resolve(args.rom))
    read_done = time.perf_counter()
    built = families.assert_contract(rom)
    planned = time.perf_counter()
    out_dir = resolve(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    record_path = os.path.join(out_dir, "emitted.json")
    try:
        record = json.load(open(record_path))
    except (OSError, ValueError):
        record = {}
    contents = record.get("sections", {}) if isinstance(record, dict) else {}
    store_path = payload_store.path(resolve(args.payloads))
    try:
        store = payload_store.read(store_path)
    except (OSError, ValueError) as exc:
        raise SystemExit("the payload store %s is unreadable: %s" % (store_path, exc))

    plan = planned_sections(built)
    members = {}
    for member in built.members:
        members.setdefault(run_of(built, member.key), []).append(member)
    for run in members:
        members[run].sort(key=lambda member: member.start)
    blob_offsets = {}
    cursor = payload_store.HEADER.size + payload_store.ENTRY.size * len(store)
    for key in sorted(store):
        blob_offsets[key] = cursor
        cursor += len(store[key])
    planned_keys = {member.key for member in built.members}
    for key in store:
        if key not in planned_keys:
            raise SystemExit("the store holds a member at %#x that the plan does not" % key)
    loaded = time.perf_counter()
    misses = rewritten = skipped = 0
    for kind, start, end in plan:
        path = os.path.join(ROOT, section_output((kind, start, end)))
        if kind == "retail":
            blob = rom[start:end]
        else:
            run = members[(start, end)]
            if run[0].start != start or run[-1].end != end:
                raise SystemExit("run %#x is not tiled by its members" % start)
            for previous, following in zip(run, run[1:]):
                if previous.end != following.start:
                    raise SystemExit("run %#x has a hole before %#x"
                                     % (start, following.start))
            for member in run:
                if len(store.get(member.key, b"")) != member.end - member.start:
                    raise SystemExit("member %#x is not its %d kept bytes"
                                     % (member.key, member.end - member.start))
            blob = b"".join(store[member.key] for member in run)
            if len(blob) != end - start:
                raise SystemExit("run %#x is %d bytes against its %d"
                                 % (start, len(blob), end - start))
        entry = [len(blob), digest(blob)]
        known = contents.setdefault(path, [])
        if entry not in known:
            misses += 1
            known.append(entry)
        if os.path.exists(path) and os.path.getsize(path) == entry[0] \
                and digest(open(path, "rb").read()) == entry[1]:
            skipped += 1
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(blob)
            rewritten += 1
    emitted = time.perf_counter()
    with open(record_path, "w", newline="\n", encoding="utf-8") as handle:
        json.dump({"sections": contents}, handle)
    rows = []
    for kind, start, end in plan:
        run = members.get((start, end), [])
        rows.append({"kind": kind, "start": "0x%x" % start, "end": "0x%x" % end,
                     "bytes": end - start,
                     "family": "+".join(sorted({member.family for member in run})),
                     "members": len(run) if kind == "generated" else 0,
                     "whole_fragment": int(all(member.whole for member in run))
                     if kind == "generated" else ""})
    with open(os.path.join(out_dir, "manifest.csv"), "w", newline="\n",
              encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, MANIFEST_FIELDS, restval="")
        writer.writeheader()
        writer.writerows(rows)
    member_rows = [{"store_key": "0x%x" % member.key, "family": member.family,
                    "start": "0x%x" % member.start, "end": "0x%x" % member.end,
                    "bytes": member.end - member.start,
                    "extent_start": "0x%x" % member.extent_start,
                    "extent_end": "0x%x" % member.extent_end,
                    "whole_fragment": int(member.whole),
                    "blob_offset": "0x%x" % blob_offsets[member.key]}
                   for member in built.members]
    with open(os.path.join(out_dir, "members.csv"), "w", newline="\n",
              encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, MEMBER_FIELDS, restval="")
        writer.writeheader()
        writer.writerows(member_rows)
    lines = ["        INCBIN  %s" % section_output(section).replace("/", "\\")
             for section in plan]
    with open(os.path.join(out_dir, "incbin.txt"), "w", newline="\n", encoding="ascii") as handle:
        handle.write("\n".join(lines) + "\n")

    counts = {kind: sum(1 for section in plan if section[0] == kind)
              for kind in ("generated", "retail")}
    totals = {kind: sum(end - start for kind, start, end in plan if kind == section_kind)
              for kind, section_kind in (("generated", "generated"), ("retail", "retail"))}
    print("sections=%d generated=%d retail=%d incbin_lines=%d"
          % (len(plan), counts["generated"], counts["retail"], len(lines)))
    print("files rewritten=%d skipped=%d" % (rewritten, skipped))
    print("encode_cache_misses=%d trusted=1 total=%d" % (misses, len(plan)))
    print("phases: read %.2fs plan %.2fs payloads %.2fs encode+emit %.2fs total %.2fs"
          % (read_done - started, planned - read_done, loaded - planned, emitted - loaded,
             time.perf_counter() - started))
    print("generated bytes=%d retail bytes=%d total=%d"
          % (totals["generated"], totals["retail"],
             totals["generated"] + totals["retail"]))
    return 0


def cmd_verify(args):
    rom = read_rom(resolve(args.rom))
    built = families.assert_contract(rom)
    payloads = member_payloads(rom, built)
    store_path = payload_store.path(resolve(args.payloads))
    try:
        store = payload_store.read(store_path)
    except (OSError, ValueError) as exc:
        raise SystemExit("the payload store %s is unreadable: %s" % (store_path, exc))
    equal = 0
    failures = []
    per_family = {}
    for key in sorted(payloads):
        family, start, end, blob = payloads[key]
        count, total = per_family.get(family, (0, 0))
        same = store.get(key) == blob and blob == rom[start:end]
        per_family[family] = (count + same, total + 1)
        equal += same
        if not same:
            failures.append((family, key))
    for family in families.FAMILY_ORDER:
        count, total = per_family.get(family, (0, 0))
        print("member %-28s %3d/%3d byte-equal to the image" % (family, count, total))
    print("basis: every member is its extent's from_bytes -> to_bytes re-serialization,"
          " sliced to the kept fragment, compared with the image")
    if failures:
        print("VERIFY FAIL: %d members differ: %s"
              % (len(failures), [("%s %#x" % item) for item in failures[:8]]))
        return 1
    print("members %d/%d byte-equal and retail" % (equal, len(payloads)))

    text = emitted.source_text(ROOT, resolve(args.source))
    rows, problems = emitted.source_rows(ROOT, rom, text,
                                         (families.REGION_A[0], families.REGION_B[1]))
    if problems:
        print("VERIFY FAIL: %s" % problems[0])
        return 1
    planned = planned_sections(built)
    sections = 0
    for low, high in (families.REGION_A, families.REGION_B):
        inside = [row for row in rows if low <= row[0] and row[1] <= high]
        expected = [section for section in planned
                    if low <= section[1] and section[2] <= high]
        sections += len(expected)
        index = 0
        for kind, start, end in expected:
            pieces = []
            while index < len(inside) and inside[index][0] < end:
                row = inside[index]
                cursor = pieces[-1][1] if pieces else start
                if row[0] != cursor:
                    print("VERIFY FAIL: %s starts at %#x, not %#x"
                          % (emitted.row_name(row), row[0], cursor))
                    return 1
                pieces.append(row)
                index += 1
            if not pieces or pieces[-1][1] != end:
                print("VERIFY FAIL: the source rows do not reach %#x for the planned span "
                      "%#x..%#x" % (end, start, end))
                return 1
            if kind == "generated":
                named = [emitted.row_name(row) for row in pieces]
                if named != [section_output((kind, start, end)).replace("/", "\\")]:
                    print("VERIFY FAIL: the generated span %#x..%#x is not its own token %s"
                          % (start, end, named))
                    return 1
        if index != len(inside):
            print("VERIFY FAIL: %d source row(s) hold bytes past the last planned span"
                  % (len(inside) - index))
            return 1
    print("source rows=%d tile 0x%x..0x%x exactly and carry the retail bytes"
          % (sections, families.REGION_A[0], families.REGION_B[1]))
    print("ledger rows to append: %d" % len([s for s in planned if s[0] == "generated"]))
    return 0


def cmd_ledger(args):
    rom = read_rom(resolve(args.rom))
    built = families.assert_contract(rom)
    members = {}
    for member in built.members:
        members.setdefault(run_of(built, member.key), set()).add(member.family)
    written = total = 0
    with open(resolve(args.ledger), "a", newline="\n", encoding="utf-8") as handle:
        for start, end in built.runs:
            names = "+".join(sorted(members.get((start, end), set())))
            handle.write(gate.ledger_line((start, end - start, "data",
                                           "structured_run_%x_%s" % (start, names),
                                           "asm/rest_of_the_game.s", "generated", "byte-proven", 0)))
            written += 1
            total += end - start
    print("appended %d generated-run rows to %s for %d bytes"
          % (written, args.ledger, total))
    return 0


def cmd_measure(args):
    rom = read_rom(resolve(args.rom))
    built = families.assert_contract(rom)
    records = families.record_extents(rom)
    round_trip = families.round_trip(rom)
    print("region A 0x%x..0x%x region B 0x%x..0x%x"
          % (families.REGION_A + families.REGION_B))
    print("%-28s %6s %8s %8s %8s %6s %6s %s"
          % ("family", "extents", "bytes", "clipped", "records", "whole", "broken",
             "round trip"))
    for family in families.FAMILY_ORDER:
        rows = built.extents[family]
        low, high = families.REGION[family]
        inside = sum(1 for offset, length in records[family]
                     if low <= offset and offset + length <= high)
        records_ok, records_total, bytes_ok, bytes_total = round_trip[family]
        print("%-28s %6d %8d %8d %8d %6d %6d %d/%d rec %d/%d B"
              % (family, len(rows), sum(end - start for start, end in rows),
                 built.clipped[family], inside, built.whole_fragments[family],
                 built.non_whole_fragments[family], records_ok, records_total, bytes_ok,
                 bytes_total))
    region_a = [run for run in built.runs if run[0] < families.REGION_A[1]]
    region_b = [run for run in built.runs if run[0] >= families.REGION_A[1]]
    print("region A: runs=%d gaps=%d files=%d generated=%d retail=%d"
          % (len(region_a), len(built.gaps), len(region_a) + len(built.gaps),
             sum(end - start for start, end in region_a),
             sum(end - start for start, end in built.gaps)))
    print("region B: runs=%d gaps=%d files=%d generated=%d retail=%d"
          % (len(region_b), 0, len(region_b), sum(end - start for start, end in region_b), 0))
    print("union components=%d promoted bytes=%d"
          % (built.union_components, sum(end - start for start, end in built.runs)))
    sites = families.overlap_sites(rom)
    print("overlap sites=%d pairwise bytes=%d clipped bytes=%d"
          % (len(sites), sum(high - low for low, high, *_ in sites),
             sum(built.clipped.values())))
    for low, high, loser, owner, loser_bytes, owner_bytes in sites[:10]:
        print("  0x%06x..0x%06x %4d B loser=%-26s (%4d B) owner=%-26s (%5d B)"
              % (low, high, high - low, loser, loser_bytes, owner, owner_bytes))
    return 0


def set_defaults(parser):
    for name in ("extract", "build", "verify", "ledger", "measure"):
        sub = parser.add_parser(name)
        sub.add_argument("--rom", required=True)
        if name in ("extract", "build", "verify"):
            sub.add_argument("--payloads", required=True)
        if name == "build":
            sub.add_argument("--out-dir", required=True)
        if name == "verify":
            sub.add_argument("--source", required=True)
        if name == "ledger":
            sub.add_argument("--ledger", required=True)
        sub.set_defaults(run=globals()["cmd_" + name])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    set_defaults(parser.add_subparsers(dest="command", required=True))
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
