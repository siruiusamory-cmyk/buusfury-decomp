"""Prove that one pixel of one tile-bank PNG drives exactly the image bytes it claims to.

  python tools\\tilebank\\png_perturb.py --png assets\\tilebank\\bank_000_0945c0.png \\
      --offset 1234 --to 90

The prediction is computed from the retail bytes, not from the build: the container's stored
extent is re-encoded from the edited payload through the same compressor the build uses, and the
predicted image differences are the differing runs inside that extent. A build that read the
payload store instead of the sheet would print the same canonical digest and no difference, so a
prediction that MISSES is the finding (P-164). The PNG is written back byte-for-byte at the end,
and the restore must return the canonical digest.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gate"))

import gate
import generate_tilebank as generator
import pngsheet
import tilebank

ASSETS = os.path.join(generator.ROOT, "assets", "tilebank")
EDIT = os.path.join(generator.ROOT, "build", "png-perturb-edit.gba")


def row_for(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    for row in generator.read_manifest(os.path.join(HERE, "tilebank_manifest.csv")):
        if generator.sheet_stem(row) == stem:
            return row
    raise SystemExit("%s names no manifest row" % path)


def pixel_of(offset, across=pngsheet.SHEET_TILES_ACROSS):
    tile, inside = divmod(offset, pngsheet.TILE_BYTES)
    row, column = divmod(inside, pngsheet.TILE)
    return (tile % across) * pngsheet.TILE + column, (tile // across) * pngsheet.TILE + row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--png", required=True)
    parser.add_argument("--offset", type=int, required=True, help="payload byte, 0-based")
    parser.add_argument("--to", type=int, required=True, help="the new palette index")
    args = parser.parse_args()

    row = row_for(args.png)
    declared = int(row["declared_size"])
    if not 0 <= args.offset < declared:
        raise SystemExit("offset %d is outside the bank's %d bytes" % (args.offset, declared))
    if not 0 <= args.to <= 255:
        raise SystemExit("--to %d is not a palette index" % args.to)

    before_png = open(args.png, "rb").read()
    width, height, indices, palette = pngsheet.read_indexed(args.png)
    payload = pngsheet.payload_of(indices, width, height, declared // pngsheet.TILE_BYTES)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != row["payload_sha256"]:
        raise SystemExit("the sheet is already edited: payload sha256 %s, the manifest's %s"
                         % (digest, row["payload_sha256"]))
    edited = bytearray(payload)
    if edited[args.offset] == args.to:
        raise SystemExit("byte %d is already %d" % (args.offset, args.to))
    edited[args.offset] = args.to

    container = int(row["container_file_offset"], 0)
    stored = int(row["stored_size"])
    retail = open(gate.RETAIL, "rb").read()
    scratch = tempfile.mkdtemp(prefix="png-perturb-")
    try:
        compress = generator.compressor(generator.COMPRESS, scratch)
        blob = tilebank.encode(tilebank.Bank(generator.KIND, declared, bytes(edited), stored),
                               compress)
    except tilebank.TileBankError as error:
        shutil.rmtree(scratch, ignore_errors=True)
        raise SystemExit("the edited payload does not fit the container's %d stored bytes: %s"
                         % (stored, error))
    wants = sorted((container + off, retail[container + off:container + off + length],
                    blob[off:off + length])
                   for off, length in runs_of(retail[container:container + stored], blob))
    print("bank %s file %s: payload byte %d %d -> %d, container 0x%06x..0x%06x"
          % (row["index"], row["container_file_offset"], args.offset,
             payload[args.offset], args.to, container, container + stored))
    for offset, before, after in wants:
        print("predicted: 0x%06x %s -> %s" % (offset, before.hex(" "), after.hex(" ")))

    x, y = pixel_of(args.offset)
    indices[y * width + x] = args.to
    pngsheet.write_indexed(args.png, width, height, indices, palette)

    try:
        if gate.rebuild() != 0:
            return 1
        after_image = open(gate.IMAGE, "rb").read()
        if hashlib.sha256(after_image).hexdigest() == gate.CANONICAL_SHA256:
            print("FAIL the edit did not reach the image")
            return 1
        shutil.copyfile(gate.IMAGE, EDIT)
        runs = gate.diff_runs(retail, after_image, limit=len(wants) + 5)
        got = sorted((offset, before, after) for offset, _length, before, after in runs)
        ok = got == wants
        for offset, before, after in wants:
            hit = [g for g in got if g[0] == offset]
            print("%s 0x%06x (payload byte %d = sheet pixel %d,%d)"
                  % ("found" if hit else "MISSING", offset, args.offset, x, y))
        print("PERTURBATION %s (%d differing run(s), %d predicted)"
              % ("PASS" if ok else "FAIL", len(runs), len(wants)))
    finally:
        open(args.png, "wb").write(before_png)
        print("restored %s" % os.path.relpath(args.png, generator.ROOT))
    if gate.rebuild() != 0:
        return 1
    final = hashlib.sha256(open(gate.IMAGE, "rb").read()).hexdigest()
    print("restored sha256=%s" % final)
    print("RESTORE %s" % ("PASS" if final == gate.CANONICAL_SHA256 else "FAIL"))
    print("the edited image is kept at %s for `python tools\\gate\\gate.py --compare baserom.gba"
          " build\\png-perturb-edit.gba`" % os.path.relpath(EDIT, generator.ROOT))
    return 0 if ok and final == gate.CANONICAL_SHA256 else 1


def runs_of(before, after):
    out = []
    index = 0
    while index < min(len(before), len(after)):
        if before[index] != after[index]:
            start = index
            while index < min(len(before), len(after)) and before[index] != after[index]:
                index += 1
            out.append((start, index - start))
        else:
            index += 1
    return out


if __name__ == "__main__":
    raise SystemExit(main())
