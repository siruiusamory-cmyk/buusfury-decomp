"""Retarget one 24-byte map-transition record in a PRIVATE ROM copy (MAP_WARP_FORMAT.md).

The record's destination is a two-byte `MapEntry` key at record `+0x11` (high) and `+0x12` (low),
which the engine scans the `MapEntry` table for (0x08008A0E/0x08008A14). Nothing else is written:
the region, the class word and the unresolved bytes stay retail.

    python tools/research/warp_patch.py --rom <copy> --record 0x295C3C --map 76 --out <copy>
    python tools/research/warp_patch.py --rom <copy> --record 0x295C3C --map 76 --out <copy> --check

The guard is loud: the two patched bytes must not lie inside any `RUNTIME_TARGETS.csv` row and not
inside the liveness witness (file 0x71734..0x71738), and the patched image must differ from its
source only inside those two bytes - one byte when the new key shares a byte with the retail one.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TARGETS = os.path.join(ROOT, "docs", "research", "RUNTIME_TARGETS.csv")
ME_TABLE = 0x08E2E0
ME_SIZE = 0x38
ME_COUNT = 452
KEY_OFFSET = 0x11
WITNESS = (0x71734, 0x71738)


def sha256(blob):
    return hashlib.sha256(blob).hexdigest().upper()


def map_key(rom, index):
    if not 0 <= index < ME_COUNT:
        raise SystemExit("map index %d is outside the MapEntry table's 0..%d"
                         % (index, ME_COUNT - 1))
    site = ME_TABLE + index * ME_SIZE
    return bytes(rom[site:site + 2])


def watched(path=TARGETS):
    with open(path, newline="") as handle:
        return [(int(row["start"], 16), int(row["end"], 16)) for row in csv.DictReader(handle)]


def guard(offsets, path=TARGETS):
    spans = watched(path) + [WITNESS]
    for offset in offsets:
        for start, end in spans:
            if start <= offset < end:
                raise SystemExit("patched byte 0x%06x lies inside watched span 0x%06x..0x%06x"
                                 % (offset, start, end))
    return ("patched bytes 0x%06x..0x%06x lie outside every watched row and the witness"
            % (offsets[0], offsets[-1]))

def apply(source, record, key):
    if len(key) != 2 or record < 0 or record + KEY_OFFSET + 2 > len(source):
        raise SystemExit("record or key outside the image")
    out = bytearray(source)
    out[record + KEY_OFFSET] = key[0]
    out[record + KEY_OFFSET + 1] = key[1]
    return bytes(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True)
    parser.add_argument("--record", required=True)
    parser.add_argument("--map", type=int, required=True, help="destination MapEntry index")
    parser.add_argument("--out", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    source = open(args.rom, "rb").read()
    record = int(args.record, 0)
    key = map_key(source, args.map)
    patched = apply(source, record, key)
    changed = [offset for offset in range(len(source)) if source[offset] != patched[offset]]
    line = guard([record + KEY_OFFSET + index for index in range(2)])
    if not changed:
        raise SystemExit("the record already carries the key %s" % key.hex())
    key_span = {record + KEY_OFFSET, record + KEY_OFFSET + 1}
    if not set(changed) <= key_span:
        raise SystemExit("the patch changed bytes outside the key span: %s"
                         % ["0x%06x" % offset for offset in changed[:4]])
    if not args.check:
        with open(args.out, "wb") as handle:
            handle.write(patched)
    report = {"source": os.path.abspath(args.rom), "source_sha256": sha256(source),
              "record": "0x%06x" % record, "destination_map": args.map,
              "key": key.hex(), "prior_key": bytes(source[record + KEY_OFFSET:
                                                          record + KEY_OFFSET + 2]).hex(),
              "changed_offsets": ["0x%06x" % offset for offset in changed],
              "patched_sha256": sha256(patched), "out": os.path.abspath(args.out),
              "guard": line}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
