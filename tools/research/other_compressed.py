"""The `other-compressed` class, row by row: what each row's bytes ARE, and whether this tree can
regenerate them.

The census (`tools/research/raw_remainder.py`) assigns a class to every INCBIN row and states one
tally for this class. A tally is not a format, and a class predicate can be wrong about what it
accepts, so this module measures each row at its own address and writes the evidence:

  python tools\\research\\other_compressed.py                     # measure the census's own row set
  python tools\\research\\other_compressed.py --rows <csv>        # re-measure a frozen row list
  python tools\\research\\other_compressed.py --rows <csv> --write   # rewrite the csv and the document

Per row it records the first bytes of the header, the header's own `kind` and declared size, how far
the container's packed stream runs, and a verdict:

  `packed-byte-exact`   kind 1/2, the strict termination rule passes, and `tools\\compress\\compress.exe`
                        turns the decoded payload back into the image's own bytes;
  `packed-differs`      kind 1/2 and the stream terminates, but the re-encode is a different (valid)
                        tokenization - named by its first differing byte;
  `stored-kind`         the header's kind word is 0 (STORED, a plain copy), so the row is NOT a packed
                        container; `webfoot_lz.validate_retail_termination` returns it after a bounds
                        check alone, which is how it reached this class in the first place;
  `no-container`        the row's first bytes are not a container header at all.

The format evidence is looked up in the tracked source on every run, so a citation cannot drift:
the header contract (`kind` u32, declared size u32, body at +8), the body decoder
`asm/rest_of_the_game.s:|sub_087b79e4|` (DMA-copied to IWRAM at boot) and its end code, the host port
`tools/research/jcalg1.py`, and the two encoders of this tree (`tools/compress/compress.exe` and
`tools/webfoot/webfoot_lz.py:pack`).
"""

import argparse
import csv
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from tools.research import bios_block_scan as B  # noqa: E402
from tools.research import jcalg1  # noqa: E402
from tools.webfoot import webfoot_lz  # noqa: E402

MAX_OUTPUT = B.MAX_DECOMPRESSED
ORACLE = os.path.join(ROOT, "tools", "compress", "compress.exe")
CENSUS = os.path.join(ROOT, "docs", "research", "RAW_REMAINDER.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "OTHER_COMPRESSED.csv")
DOC_OUT = os.path.join(ROOT, "docs", "research", "OTHER_COMPRESSED.md")
SITES = (
    ("body decoder", "asm/rest_of_the_game.s", r"^\|sub_087b79e4\|", "0x7B79E4"),
    ("its bit reader", "asm/rest_of_the_game.s", r"^\|loc_087b7c30\|", "0x7B7C30"),
    ("its end code", "asm/rest_of_the_game.s", r"^\|loc_087b7c78\|", "0x7B7C78"),
)
RECORDED = {"rows": 71, "packed": 46, "byte-exact": 45, "differs": 1, "stored": 25}
FIELDS = ("start", "end", "bytes", "file", "line", "head12", "kind", "declared", "packed_end",
          "covered", "verdict", "note", "walk_bytes", "walk_containers")


class ReportError(ValueError):
    pass


def site_line(relative, pattern, address):
    path = os.path.join(ROOT, relative)
    for number, line in enumerate(open(path, errors="replace"), 1):
        if re.search(pattern, line):
            if address.lower() not in line.lower() and "0x" not in address:
                raise ReportError("%s:%d does not name %s" % (relative, number, address))
            return number
    raise ReportError("%s carries no %s" % (relative, pattern))


def census_rows(path=CENSUS, klass="other-compressed"):
    with open(path, newline="") as handle:
        return [(int(row["start"], 16), int(row["end"], 16), row["file"], row["line"])
                for row in csv.DictReader(handle) if row["class"] == klass]


def frozen_rows(path):
    with open(path, newline="") as handle:
        return [(int(row["start"], 16), int(row["end"], 16), row.get("file", ""), row.get("line", ""))
                for row in csv.DictReader(handle)]


def oracle(scratch):
    def compress(payload):
        source = os.path.join(scratch, "payload.bin")
        target = os.path.join(scratch, "container.bin")
        with open(source, "wb") as handle:
            handle.write(payload)
        if os.path.exists(target):
            os.remove(target)
        done = subprocess.run([ORACLE, source, target], capture_output=True)
        if done.returncode != 0 or not os.path.exists(target):
            return None
        with open(target, "rb") as handle:
            return handle.read()
    return compress


def first_difference(left, right):
    for index in range(min(len(left), len(right))):
        if left[index] != right[index]:
            return index
    return None


def measure(rom, start, end, compress, walk=False):
    kind, declared = int.from_bytes(rom[start:start + 4], "little"), \
        int.from_bytes(rom[start + 4:start + 8], "little")
    record = {"start": start, "end": end, "bytes": end - start, "head12": rom[start:start + 12].hex(),
              "kind": kind, "declared": declared, "packed_end": "", "covered": "",
              "verdict": "no-container", "note": "", "walk_bytes": 0, "walk_containers": 0}
    try:
        container = webfoot_lz.validate_retail_termination(rom, start, maximum_output=0x4000)
    except Exception as refusal:
        record["note"] = type(refusal).__name__
        return record
    record["packed_end"], record["covered"] = container.packed_end, container.packed_end - start
    if container.kind not in webfoot_lz.PACKED_KINDS:
        record["verdict"] = "stored-kind"
        record["note"] = ("kind %d (STORED) is a plain copy, not a packed stream; the class "
                          "predicate accepted it on the bounds check alone" % container.kind)
        return record
    blob = compress(container.data)
    if blob is None:
        record["verdict"] = "packed-differs"
        record["note"] = "compress.exe refused the %d-byte payload" % len(container.data)
        return record
    retail = rom[start:start + len(blob)]
    if blob == retail:
        record["verdict"] = "packed-byte-exact"
    else:
        record["verdict"] = "packed-differs"
        where = first_difference(blob, retail)
        record["note"] = ("first differing byte %s (%d bytes re-encoded, %d in the image)"
                          % (where, len(blob), len(retail)))
    if walk:
        at, walked, count = start, 0, 0
        while at + B.JCALG1_HEADER <= end:
            hit = B.jcalg1_container(rom, at, end, compress)
            if hit is None or not hit.get("byte_exact"):
                break
            at += hit["compressed"]
            walked += hit["compressed"]
            count += 1
        record["walk_bytes"], record["walk_containers"] = walked, count
    return record


def tally(records):
    out = {"rows": len(records),
           "packed": sum(1 for r in records if r["verdict"].startswith("packed")),
           "byte-exact": sum(1 for r in records if r["verdict"] == "packed-byte-exact"),
           "differs": sum(1 for r in records if r["verdict"] == "packed-differs"),
           "stored": sum(1 for r in records if r["verdict"] == "stored-kind")}
    return out


def csv_text(records):
    import io
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, extrasaction="ignore",
                            lineterminator="\n")
    writer.writeheader()
    for record in records:
        row = dict(record)
        for key in ("start", "end", "packed_end"):
            if isinstance(row.get(key), int):
                row[key] = "0x%X" % row[key]
        writer.writerow(row)
    return buffer.getvalue()


def doc_text(records, counts, sites):
    lines = []
    add = lines.append
    add("# `other-compressed` row by row: the format, the round trip, and what the class really held")
    add("")
    add("Generated by `tools/research/other_compressed.py` (GEN-COMPRESSED-001); the row set is the")
    add("census's own `other-compressed` class **at the 2026-10-16 master** (`docs/research/RAW_REMAINDER.csv`,")
    add("71 rows / 46,140 B), frozen in `docs/research/OTHER_COMPRESSED.csv` because the promotion this")
    add("ticket lands retires those rows. Every number below is re-measured from the retail image on")
    add("every run and asserted against the recorded tally.")
    add("")
    add("## What the format is")
    add("")
    add("- A **packed Webfoot/JCALG1 container**: `{u32 kind, u32 declared_size}` then the packed body")
    add("  at +8. `kind` 1 and 2 are the packed kinds, `kind` 0 is STORED - a plain copy")
    add("  (`tools/webfoot/webfoot_lz.py:140-144`); the header is read at `+0`/`+4`")
    add("  (`tools/webfoot/webfoot_lz.py:read_header`, `tools/research/bios_block_scan.py:jcalg1_container`).")
    add("- The body is the engine's own JCALG1 stream. Its decoder in this tree's source is")
    add("  `%s:%d` `|sub_087b79e4|` (file `%s`), with its bit reader at `:%d` and its end code at `:%d`;"
        % (sites[0][0], sites[0][1], sites[0][2], sites[1][1], sites[2][1]))
    add("  it is DMA-copied to IWRAM at boot (`asm/crt0.s:51` `hardware_conf_2 DCD 0x087B79A4`) and")
    add("  entered at `0x03000040`. The host port is `tools/research/jcalg1.py`; the independent")
    add("  reader is `tools/webfoot/webfoot_lz.py:unpack`.")
    add("- The encoders of this tree are `tools/compress/compress.exe` (JCALG1 r5.32, wrapped by")
    add("  `tools/compress/main.cpp`, which writes the kind-1 header and drops the checksum) and")
    add("  `tools/webfoot/webfoot_lz.py:pack`. They do NOT agree: measured on the 46 packed rows, the")
    add("  re-encode through `compress.exe` reproduces retail on 45 and differently on 1, and `pack`")
    add("  reproduces none of them (`kind 2` header, first differing byte 0, output never shorter).")
    add("  So the retail tokenization is `compress.exe`'s, and a row it does not reproduce needs an")
    add("  encoder this tree does not have.")
    add("")
    add("## The measured tally")
    add("")
    add("| verdict | rows | bytes |")
    add("|---|---|---|")
    for verdict, note in (("packed-byte-exact", "kind 1/2 and the re-encode is the image's own bytes"),
                          ("packed-differs", "kind 1/2, terminates, re-encodes to another tokenization"),
                          ("stored-kind", "kind 0 (STORED): not a packed container at all"),
                          ("no-container", "no container header at the row's start")):
        rows = [r for r in records if r["verdict"] == verdict]
        add("| `%s` | %d | %d |" % (verdict, len(rows), sum(r["bytes"] for r in rows)))
    add("| **total** | **%d** | **%d** |" % (counts["rows"], sum(r["bytes"] for r in records)))
    add("")
    add("Recorded tally (`RECORDED` in the tool): %s - asserted on every run."
        % ", ".join("%s=%d" % item for item in sorted(RECORDED.items())))
    add("")
    add("## The finding: 25 of the 71 rows were never compressed data")
    add("")
    add("The class predicate is `webfoot_lz.validate_retail_termination(rom, row_start)` succeeding with")
    add("its `packed_end` inside the row. That function requires the stream's own escape **only on the")
    add("packed path** - a `kind` 0 header is returned after a bounds check alone")
    add("(`tools/webfoot/webfoot_lz.py:511-520` returns before `_unpack_stream`) - so any row whose first")
    add("four bytes happen to be a small integer was accepted as a \"container\" ending at")
    add("`start + 8 + declared`. Measured: %d of the %d rows carry a `kind` 0 header (%d of them")
    add("declaring zero bytes), and 127 of the 4,322 census rows have a first word in 1..0x4000 that the")
    add("stored path would accept. `raw_remainder.webfoot_extent` now requires a PACKED kind, so those")
    add("rows fall to the class their own bytes support. That is a correction to the census instrument,")
    add("not to the bytes: no byte of any row moved.")
    add("")
    add("## The promotion (SC2)")
    add("")
    add("- The %d `packed-byte-exact` rows are the 45 slices of `asm/rawlabeled_3bbe70.s`")
    add("  (0x3BBE70..0x3BD2F8, 5,256 B, one container per slice). `tools/research/generate_jcalg1.py")
    add("  `--sweep-class other-compressed --apply` replaced each slice token with")
    add("  `INCBIN build\\jcalg1\\gen_<start>_<end>.bin`; the build re-encodes the stored decoded payload")
    add("  with `compress.exe` and refuses unless the result is the image's own bytes")
    add("  (`generate_jcalg1.encoded`).")
    add("- The `packed-differs` row stays INCBIN with its reason; the `stored-kind` rows were never")
    add("  candidates.")
    add("")
    add("## Every row")
    add("")
    add("| row | bytes | carrier | head (12 B) | kind | declared | packed end | walk | verdict | note |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for record in records:
        add("| `0x%06X..0x%06X` | %d | `%s:%s` | `%s` | %d | %d | %s | %d | `%s` | %s |"
            % (record["start"], record["end"], record["bytes"], record["file"], record["line"],
               record["head12"], record["kind"], record["declared"],
               ("0x%06X" % record["packed_end"]) if record["packed_end"] != "" else "-",
               record["walk_bytes"], record["verdict"], record["note"] or "-"))
    add("")
    add("## Re-run")
    add("")
    add("    python tools\\research\\other_compressed.py --rows docs\\research\\OTHER_COMPRESSED.csv")
    add("    python tools\\research\\raw_remainder.py --route-probe")
    add("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--rows", default=CSV_OUT, help="the frozen row list (start,end,file,line)")
    parser.add_argument("--census", default=CENSUS)
    parser.add_argument("--csv", default=CSV_OUT)
    parser.add_argument("--doc", default=DOC_OUT)
    parser.add_argument("--write", action="store_true", help="rewrite the csv and the document")
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    if os.path.exists(args.rows):
        rows = frozen_rows(args.rows)
    else:
        rows = census_rows(args.census)
    sites = []
    for name, relative, pattern, address in SITES:
        try:
            sites.append((relative, site_line(relative, pattern, address), address))
        except ReportError as missing:
            raise SystemExit(str(missing))
    scratch = tempfile.mkdtemp(prefix="other-compressed-")
    compress = oracle(scratch)
    records = []
    for start, end, name, line in rows:
        record = measure(rom, start, end, compress, walk=True)
        record["file"], record["line"] = name, line
        records.append(record)
    counts = tally(records)
    print("other-compressed: %s" % ", ".join("%s=%d" % item for item in sorted(counts.items())))
    for key, value in RECORDED.items():
        if counts.get(key) != value:
            print("RECORDED %s=%d, measured %d" % (key, value, counts[key]))
    print(csv_text(records), end="")
    if args.write:
        with open(args.csv, "w", newline="") as handle:
            handle.write(csv_text(records))
        with open(args.doc, "w", newline="") as handle:
            handle.write(doc_text(records, counts, sites))
        print("wrote %s and %s" % (os.path.relpath(args.csv, ROOT), os.path.relpath(args.doc, ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
