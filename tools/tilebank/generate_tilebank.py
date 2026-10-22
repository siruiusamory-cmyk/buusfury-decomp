"""Extract, emit and verify the 187-container tile-bank block at file 0x0945C0."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FORMATS = os.path.join(ROOT, "tools", "webfoot")
sys.path.insert(0, HERE)
sys.path.insert(0, FORMATS)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import encode_cache
import payload_store
import pngsheet
import romfile
import tilebank
import webfoot_lz

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000
KIND = 1
BANK_TABLE_FILE = 0x179764
BANK_COUNT = 187
BLOCK_START = 0x0945C0
BLOCK_LEN = 938404
COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")
MANIFEST_FIELDS = ("index", "table_entry_file_offset", "container_file_offset", "declared_size",
                   "stored_size", "payload_file", "payload_sha256", "stored_sha256")
PALETTE_FILE = 0x05632C
PALETTE_ENTRIES = 256
SHEET_NAME = "bank_%03d_%06x"
REFUSALS = "tilebank_refusals.csv"
REFUSAL_HEADER = ("index,container_file_offset,declared_size,reason\n")


def read_rom(path):
    return romfile.read_rom(path, ROM_SHA256)


def palette(rom):
    out = []
    for index in range(PALETTE_ENTRIES):
        value = struct.unpack_from("<H", rom, PALETTE_FILE + 2 * index)[0]
        out.append(tuple(((value >> shift) & 31) * 255 // 31 for shift in (0, 5, 10)))
    return out


def bank_table(rom):
    entries = []
    for index in range(BANK_COUNT):
        site = BANK_TABLE_FILE + 4 * index
        address = struct.unpack_from("<I", rom, site)[0]
        if not ROM_BASE <= address < ROM_BASE + len(rom):
            raise SystemExit("bank table entry %d holds %#010x, not a ROM address"
                             % (index, address))
        entries.append((index, site, address - ROM_BASE))
    return entries


def read_banks(rom, entries):
    banks = []
    for index, site, offset in entries:
        container = webfoot_lz.unpack(rom, offset, maximum_output=tilebank.MAX_PAYLOAD)
        if container.kind != KIND:
            raise SystemExit("bank %d is kind %d" % (index, container.kind))
        if container.declared_size % 64:
            raise SystemExit("bank %d declares %d, not a whole number of tiles"
                             % (index, container.declared_size))
        banks.append((index, site, offset, container))
    if [bank[2] for bank in banks] != sorted(bank[2] for bank in banks):
        raise SystemExit("the bank table is not in file order")
    if banks[0][2] != BLOCK_START:
        raise SystemExit("the block starts at %#x, not %#x" % (banks[0][2], BLOCK_START))
    gaps = {}
    for first, second in zip(banks, banks[1:]):
        gap = second[2] - (first[2] + first[3].packed_size)
        gaps[gap] = gaps.get(gap, 0) + 1
    if set(gaps) - {0, 4}:
        raise SystemExit("gaps between containers are %s bytes" % sorted(gaps))
    tail = BANK_TABLE_FILE - (banks[-1][2] + banks[-1][3].packed_size)
    union = sum(bank[3].packed_size for bank in banks)
    if union + sum(k * n for k, n in gaps.items()) + tail != BLOCK_LEN:
        raise SystemExit("containers and gaps do not tile the %d-byte block" % BLOCK_LEN)
    return banks


def compressor(exe, scratch):
    counter = itertools.count()

    def compress(payload):
        stem = os.path.join(scratch, "tilebank-%04d" % next(counter))
        with open(stem + ".in", "wb") as handle:
            handle.write(payload)
        proc = subprocess.run([exe, stem + ".in", stem + ".out"], capture_output=True)
        if proc.returncode != 0 or not os.path.exists(stem + ".out"):
            raise SystemExit("compress.exe exit %d: %s"
                             % (proc.returncode, proc.stderr.decode("utf-8", "replace").strip()))
        return open(stem + ".out", "rb").read()

    return compress


def read_manifest(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_manifest(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_payload(store, row):
    payload = store.get(int(row["container_file_offset"], 0))
    if payload is None or len(payload) != int(row["declared_size"]):
        raise SystemExit("payload %s is not a %s-byte member of the store"
                         % (row["payload_file"], row["declared_size"]))
    return payload


def sheet_stem(row):
    return SHEET_NAME % (int(row["index"]), int(row["container_file_offset"], 0))


def read_sheet(directory, row):
    path = os.path.join(directory, sheet_stem(row) + ".png")
    if not os.path.exists(path):
        raise SystemExit("%s is missing: the container has no editable sheet" % path)
    width, height, indices = pngsheet.read_indexed(path)[:3]
    tiles = int(row["declared_size"]) // pngsheet.TILE_BYTES
    if int(row["declared_size"]) % pngsheet.TILE_BYTES:
        raise SystemExit("bank %s declares %d, not a whole number of %d-byte tiles"
                         % (row["index"], int(row["declared_size"]), pngsheet.TILE_BYTES))
    return pngsheet.payload_of(indices, width, height, tiles)


def check_payload_digest(payload, row):
    digest = hashlib.sha256(payload).hexdigest()
    if digest != row["payload_sha256"]:
        raise SystemExit("payload %s is sha256 %s, not the manifest's %s"
                         % (row["payload_file"], digest, row["payload_sha256"]))


def scratch_dir(prefix):
    return tempfile.mkdtemp(prefix=prefix)


def cmd_extract(args):
    rom = read_rom(args.rom)
    colors = palette(rom)
    banks = read_banks(rom, bank_table(rom))
    os.makedirs(args.payloads, exist_ok=True)
    rows = []
    items = []
    for index, site, offset, container in banks:
        items.append((offset, container.data))
        rows.append({
            "index": index,
            "table_entry_file_offset": "0x%06x" % site,
            "container_file_offset": "0x%06x" % offset,
            "declared_size": container.declared_size,
            "stored_size": container.packed_size,
            "payload_file": "bank_%03d.bin" % index,
            "payload_sha256": hashlib.sha256(container.data).hexdigest(),
            "stored_sha256": hashlib.sha256(rom[offset:offset + container.packed_size]).hexdigest(),
        })
    write_manifest(args.manifest, rows)
    stamped = payload_store.write(payload_store.path(args.payloads), items)
    refused = write_sheets(args.payloads, rows, dict(items), colors)
    print("extracted %d payloads, union %d bytes, block %d bytes"
          % (len(rows), sum(bank[3].packed_size for bank in banks), BLOCK_LEN))
    print("wrote %s, %d bytes" % (payload_store.path(args.payloads), stamped[0]))
    print("sheets=%d refused=%d of %d containers, palette file 0x%06x"
          % (len(rows) - len(refused), len(refused), len(rows), PALETTE_FILE))
    print("REFUSED %s" % "; ".join("%s: %s" % (row["index"], reason) for row, reason in refused)
          if refused else "REFUSED none")
    return 1 if refused else 0


def refusal_reason(row, payload):
    if len(payload) != int(row["declared_size"]):
        return ("payload is %d bytes against a declared %s"
                % (len(payload), row["declared_size"]))
    if len(payload) % pngsheet.TILE_BYTES:
        return ("declared %s is not a whole number of %d-byte tiles"
                % (row["declared_size"], pngsheet.TILE_BYTES))
    return None


def write_sheets(directory, rows, payloads, colors):
    refused = []
    for row in rows:
        payload = payloads[int(row["container_file_offset"], 0)]
        reason = refusal_reason(row, payload)
        if reason is not None:
            refused.append((row, reason))
            continue
        tiles = len(payload) // pngsheet.TILE_BYTES
        width, height, indices = pngsheet.sheet_of(payload)
        stem = os.path.join(directory, sheet_stem(row))
        pngsheet.write_indexed(stem + ".png", width, height, indices, colors)
        with open(stem + ".json", "w", encoding="utf-8", newline="\n") as handle:
            json.dump({"index": int(row["index"]),
                       "container_file_offset": row["container_file_offset"],
                       "declared_size": int(row["declared_size"]),
                       "format": "%dx%d 8bpp tiles" % (pngsheet.TILE, pngsheet.TILE),
                       "tile_bytes": pngsheet.TILE_BYTES,
                       "tile_order": "linear: tile 0 at the sheet's top left, left to right",
                       "sheet_tiles_across": pngsheet.SHEET_TILES_ACROSS,
                       "tiles": tiles,
                       "palette": "ROM file 0x%06x, %d BGR555 entries, the BG palette bank,"
                                  " statically supported and runtime NOT MEASURED"
                                  % (PALETTE_FILE, PALETTE_ENTRIES)},
                      handle, indent=2, sort_keys=True)
            handle.write("\n")
    with open(os.path.join(directory, REFUSALS), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(REFUSAL_HEADER)
        for row, reason in refused:
            handle.write("%s,%s,%s,%s\n" % (row["index"], row["container_file_offset"],
                                            row["declared_size"], reason))
    return refused


def cmd_build(args):
    rows = read_manifest(args.manifest)
    if len(rows) != BANK_COUNT:
        raise SystemExit("the manifest holds %d rows, not %d" % (len(rows), BANK_COUNT))
    rows.sort(key=lambda row: int(row["container_file_offset"], 0))
    offsets = [int(row["container_file_offset"], 0) - BLOCK_START for row in rows]
    if offsets[0] != 0 or offsets[-1] >= BLOCK_LEN:
        raise SystemExit("the manifest's containers are not inside the block")
    banks = [tilebank.Bank(KIND, int(row["declared_size"]), read_sheet(args.payloads, row),
                           int(row["stored_size"])) for row in rows]
    scratch = scratch_dir("tilebank-")
    try:
        compress, cache, cache_close = encode_cache.cached_compress(
            compressor(COMPRESS, scratch), COMPRESS, encode_cache.default_cache_dir())
        block = tilebank.encode_block(banks, offsets, BLOCK_LEN, compress)
        cache_close()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if len(block) != BLOCK_LEN:
        raise SystemExit("emitted %d bytes, not %d" % (len(block), BLOCK_LEN))
    with open(args.out, "wb") as handle:
        handle.write(block)
    print("wrote %s: %d banks, %d bytes" % (args.out, len(banks), len(block)))
    print("encode_cache_misses=%d trusted=%d total=%d"
          % (cache["misses"], cache["trusted"], cache["total"]))
    return 0


def cmd_verify(args):
    rom = read_rom(args.rom)
    banks = read_banks(rom, bank_table(rom))
    rows = {int(row["index"]): row for row in read_manifest(args.manifest)}
    if sorted(rows) != sorted(bank[0] for bank in banks):
        raise SystemExit("the manifest does not name every bank")
    block = rom[BLOCK_START:BLOCK_START + BLOCK_LEN]
    store = payload_store.read(payload_store.path(args.payloads))
    scratch = scratch_dir("tilebank-")
    compress = compressor(COMPRESS, scratch)
    generated = bytearray(BLOCK_LEN)
    equal = 0
    try:
        for index, _, offset, container in banks:
            row = rows[index]
            if (int(row["container_file_offset"], 0) != offset
                    or int(row["declared_size"]) != container.declared_size
                    or int(row["stored_size"]) != container.packed_size):
                raise SystemExit("manifest row %d disagrees with the ROM" % index)
            if hashlib.sha256(rom[offset:offset + container.packed_size]).hexdigest() \
                    != row["stored_sha256"]:
                raise SystemExit("bank %d's stored bytes do not hash to the manifest's" % index)
            payload = read_payload(store, row)
            check_payload_digest(payload, row)
            bank = tilebank.Bank(container.kind, container.declared_size, payload,
                                 container.packed_size)
            blob = tilebank.encode(bank, compress)
            if len(blob) != container.packed_size:
                raise SystemExit("bank %d regenerated %d bytes against a stored %d"
                                 % (index, len(blob), container.packed_size))
            start = offset - BLOCK_START
            generated[start:start + len(blob)] = blob
            same = bytes(generated[start:start + len(blob)]) == block[start:start + len(blob)]
            equal += same
            print("bank %3d  file 0x%06x  declared %5d  stored %5d  generated %5d  %s"
                  % (index, offset, container.declared_size, container.packed_size, len(blob),
                     "EQUAL" if same else "DIFFER"))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    whole = bytes(generated) == block
    print("block 0x%06x..0x%06x %s" % (BLOCK_START, BLOCK_START + BLOCK_LEN,
                                       "byte-equal" if whole else "DIFFERS"))
    print("%d/%d byte-equal" % (equal, len(banks)))
    return 0 if whole and equal == len(banks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    extract = commands.add_parser("extract")
    extract.add_argument("--rom", required=True)
    extract.add_argument("--payloads", required=True)
    extract.add_argument("--manifest", required=True)
    extract.set_defaults(run=cmd_extract)
    build = commands.add_parser("build")
    build.add_argument("--payloads", required=True,
                       help="the directory holding the editable sheets (bank_NNN_XXXXXX.png)")
    build.add_argument("--manifest", required=True)
    build.add_argument("--out", required=True)
    build.set_defaults(run=cmd_build)
    verify = commands.add_parser("verify")
    verify.add_argument("--rom", required=True)
    verify.add_argument("--payloads", required=True)
    verify.add_argument("--manifest", required=True)
    verify.set_defaults(run=cmd_verify)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
