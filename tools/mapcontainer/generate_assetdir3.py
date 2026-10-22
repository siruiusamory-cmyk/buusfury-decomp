"""Emit the asset-directory-3 script bank (0x36D540..0x3715C0 and 0x3725C0..0x3BB78C) from its parse.

The two census rows stop being INCBIN slices of the retail image and become two generated files,
whose bytes the emitter RE-ENCODES from a structure `extract` recovered at build time:

    head       the 14 class flags at 0x36D540, indexed by `class - 2`
    ramp       a record's byte ramp; 0xFF resets the walk's counter, anything else is an array index
    count      a block's call budget, the first byte of the sub-block the array names
    entry      an opcode byte `(class << 4) | slot`, its flag, and its operands
    array      the u32 sub-block pointers at the end of a record's span
    raw        a byte no call sequence of the machine reads (reported, not absorbed)

`build` derives each entry's operand count from its flag (bits 0,1,2 one byte each, bit 3 two),
refuses an entry whose stored operands disagree, refuses a class-2..15 flag that is not its head
byte, and refuses an array word outside the payload - then compares the emitted bytes with the
image, so a perturbed store member cannot reach the assembler. The bytes come from the store, never
from the image (P-164).

MEASURED (SCRIPT-BANK-003, 2026-10-17): the walk reads 318,712 of the 320,076 payload bytes;
2 rows / 315,980 B is the census denominator, and 1,364 B of it is read by no call sequence.
Against the BANK-READWATCH-001 run every one of the 66,538 runtime-read bank bytes gets the role
the runtime pc names, and all 81 runtime-read runs of SCRIPT-BANK-002 have their first byte reached.

  extract  parse the rows, write the payload store
  build    re-encode both rows from the store into build/assetdir3/gen_<start>_<end>.bin
  verify   re-derive both rows from the image and check the carriers name the generated files \
  name     the token of one row
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import assetdir3  # noqa: E402
import payload_store  # noqa: E402

ROM_SHA256 = assetdir3.ROM_SHA256
ROWS = assetdir3.ROWS
PAYLOAD = assetdir3.PAYLOAD
BLOCK = "assetdir3"
OUT_DIR = os.path.join("build", BLOCK)
CARRIERS = (os.path.join("asm", "assetdir3_36d540.s"),
            os.path.join("asm", "assetdir3_3725c0.s"))

HEAD, RAMP, COUNT, ENTRY, ARRAY, RAW = 1, 2, 3, 4, 5, 6


class Refused(ValueError):
    pass


def resolve(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def read_rom(path):
    data = open(resolve(path), "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ROM_SHA256:
        raise SystemExit("ROM sha256 %s is not the canonical %s" % (digest, ROM_SHA256))
    return data


def name(start, end):
    return "gen_%x_%x.bin" % (start, end)


def token(start, end):
    return os.path.join("build", BLOCK, name(start, end)).replace(os.sep, "\\")


def segment(op, blob):
    if op in (HEAD, RAMP, RAW):
        return struct.pack("<BH", op, len(blob)) + blob
    if op in (COUNT,):
        return struct.pack("<BB", op, blob[0])
    if op == ARRAY:
        return struct.pack("<BH", op, len(blob) // 4) + blob
    if op == ENTRY:
        return struct.pack("<B", op) + blob
    raise Refused("unknown segment %d" % op)


def structure(rom, start, end, roles, entries, head):
    by_offset = {entry[1]: entry for entry in entries}
    out, at, pending = [], start, b""

    def flush():
        nonlocal pending
        if pending:
            out.append(segment(RAW, pending))
            pending = b""

    while at < end:
        role = roles.get(at)
        if role == assetdir3.HEAD_BYTES:
            flush()
            out.append(segment(HEAD, head))
            at += len(head)
            continue
        if role == assetdir3.RAMP:
            run = at
            while at < end and roles.get(at) == assetdir3.RAMP:
                at += 1
            flush()
            out.append(segment(RAMP, rom[run:at]))
            continue
        if role == assetdir3.ARRAY:
            run = at
            while at < end and roles.get(at) == assetdir3.ARRAY:
                at += 1
            flush()
            if run % 4 or (at - run) % 4:
                out.append(segment(RAW, rom[run:at]))
                continue
            values = b"".join(struct.pack("<I", assetdir3.u32(rom, word))
                              for word in range(run, at, 4))
            out.append(segment(ARRAY, values))
            continue
        if role == assetdir3.COUNT_BYTE:
            flush()
            out.append(segment(COUNT, rom[at:at + 1]))
            at += 1
            continue
        if role == assetdir3.OPCODE:
            entry = by_offset.get(at)
            if entry is None:
                raise Refused("0x%06X is an opcode with no entry" % at)
            _record, offset, size, cls, slot, flag, operands = entry
            if cls is None:
                flush()
                out.append(segment(ENTRY, b"\x00\x00\x00"))
                at += 1
                continue
            if offset + size > end:
                pending += rom[at:end]
                at = end
                continue
            flush()
            out.append(segment(ENTRY, struct.pack("<BBB", (cls << 4) | slot, flag,
                                                  len(operands)) + operands))
            at += size
            continue
        if role in assetdir3.OPERANDS:
            raise Refused("0x%06X is an operand no entry claims" % at)
        pending += rom[at:at + 1]
        at += 1
    flush()
    return b"".join(out)


def walked(rom):
    roles, entries, stats, origin = assetdir3.walk(rom, trace=True)
    return roles, entries, stats, origin


def extract(rom):
    roles, entries, stats, _origin = walked(rom)
    head = assetdir3.head_bytes(rom)
    members = {}
    for row in ROWS:
        members[row[0]] = structure(rom, row[0], row[1], roles, entries, head)
    return members


def segments(blob):
    at = 0
    while at < len(blob):
        op = blob[at]
        if op in (HEAD, RAMP, RAW):
            length = struct.unpack_from("<H", blob, at + 1)[0]
            yield op, blob[at + 3:at + 3 + length]
            at += 3 + length
        elif op == COUNT:
            yield op, blob[at + 1:at + 2]
            at += 2
        elif op == ARRAY:
            count = struct.unpack_from("<H", blob, at + 1)[0]
            yield op, blob[at + 3:at + 3 + 4 * count]
            at += 3 + 4 * count
        elif op == ENTRY:
            length = blob[at + 3]
            yield op, blob[at + 1:at + 4 + length]
            at += 4 + length
        else:
            raise Refused("segment %d at member offset 0x%06X" % (op, at))


def piece(op, body, head, cursor):
    if op in (HEAD, RAMP, RAW):
        if op == HEAD and len(body) != len(head):
            raise Refused("the head at 0x%06X is %d bytes" % (cursor, len(body)))
        return body
    if op == COUNT:
        return body
    if op == ARRAY:
        if len(body) % 4:
            raise Refused("the array at 0x%06X is not whole words" % cursor)
        for index in range(len(body) // 4):
            word = struct.unpack_from("<I", body, 4 * index)[0]
            if not PAYLOAD[0] <= word - 0x08000000 < PAYLOAD[1]:
                raise Refused("an array word names 0x%08X, outside the payload" % word)
        return body
    opcode, flag, length = struct.unpack_from("<BBB", body, 0)
    operands = body[3:]
    if len(operands) != length:
        raise Refused("the entry at 0x%06X is short of its own operands" % cursor)
    if opcode == 0:
        if operands:
            raise Refused("the terminator at 0x%06X carries operands" % cursor)
        return b"\x00"
    cls, slot = opcode >> 4, opcode & 0x0F
    need = (1 if cls == 0 else 0) + assetdir3.operand_count(flag)
    if len(operands) != need:
        raise Refused("the entry at 0x%06X stores %d operands, its flag takes %d"
                      % (cursor, len(operands), need))
    if cls == 0 and operands[0] != flag:
        raise Refused("the class-0 operand at 0x%06X is not its flag" % cursor)
    if 1 < cls < 16 and flag != head[cls - 2]:
        raise Refused("the class-%d flag at 0x%06X is not head[%d]" % (cls, cursor, cls - 2))
    return bytes([opcode]) + operands


def encode(members, rom, head, rows=ROWS):
    out = {}
    for start, blob in members.items():
        end = dict(rows)[start]
        cursor = start
        built = bytearray()
        for op, body in segments(blob):
            blob_bytes = piece(op, body, head, cursor)
            cursor += len(blob_bytes)
            if cursor > end:
                raise Refused("the segments of 0x%06X run past 0x%06X" % (start, end))
            built += blob_bytes
        if cursor != end:
            raise Refused("the segments of 0x%06X stop at 0x%06X of 0x%06X"
                          % (start, cursor, end))
        if bytes(built) != rom[start:end]:
            raise Refused("the re-encoded row 0x%06X..0x%06X is not the image's"
                          % (start, end))
        out[start] = bytes(built)
    return out


def cmd_extract(args):
    rom = read_rom(args.rom)
    members = extract(rom)
    os.makedirs(resolve(args.payloads), exist_ok=True)
    stamped = payload_store.write(payload_store.path(resolve(args.payloads)),
                                  sorted(members.items()))
    for start, blob in sorted(members.items()):
        print("row 0x%06x..0x%06x members=%d segments=%d bytes=%d"
              % (start, dict(ROWS)[start], 1, len(blob), dict(ROWS)[start] - start))
    print("wrote %s, %d bytes" % (payload_store.path(resolve(args.payloads)), stamped[0]))
    return 0


def report_block(out, written):
    print("sections=%d generated=%d retail=0 incbin_lines=%d containers=0 records=%d"
          % (len(out), len(out), len(out), len(out)))
    print("encode_cache_misses=%d trusted=1 total=0" % written)
    print("generated bytes=%d" % sum(len(blob) for blob in out.values()))


def already_emitted(out_dir, store_path):
    path = os.path.join(out_dir, "stamp.json")
    try:
        stamp = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if stamp.get("store") != payload_store.stamp(store_path):
        return None
    out = {}
    for key, (length, digest) in stamp.get("rows", {}).items():
        row = os.path.join(out_dir, name(int(key, 16), dict(ROWS)[int(key, 16)]))
        if not os.path.exists(row):
            return None
        blob = open(row, "rb").read()
        if len(blob) != length or hashlib.sha256(blob).hexdigest() != digest:
            return None
        out[int(key, 16)] = blob
    return out or None


def cmd_build(args):
    rom = read_rom(args.rom)
    store_path = payload_store.path(resolve(args.payloads))
    out_dir = resolve(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out = already_emitted(out_dir, store_path)
    if out is not None:
        print("manifest path: %s names the store's bytes" % os.path.join(out_dir, "stamp.json"))
        report_block(out, 0)
        return 0
    try:
        store = payload_store.read(store_path)
    except (OSError, ValueError) as exc:
        raise SystemExit("the payload store %s is unreadable: %s" % (store_path, exc))
    head = assetdir3.head_bytes(rom)
    out = encode(store, rom, head)
    written = 0
    stamp = {"store": payload_store.stamp(store_path), "rows": {}}
    for start, blob in sorted(out.items()):
        path = os.path.join(out_dir, name(start, dict(ROWS)[start]))
        old = open(path, "rb").read() if os.path.exists(path) else None
        if old != blob:
            with open(path, "wb") as handle:
                handle.write(blob)
            written += 1
        stamp["rows"]["0x%x" % start] = [len(blob), hashlib.sha256(blob).hexdigest()]
    with open(os.path.join(out_dir, "stamp.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(stamp, handle, sort_keys=True)
    report_block(out, written)
    return 0


def cmd_verify(args):
    rom = read_rom(args.rom)
    store_path = payload_store.path(resolve(args.payloads))
    store = payload_store.read(store_path)
    head = assetdir3.head_bytes(rom)
    problems = []
    fresh = extract(rom)
    if sorted(fresh) != sorted(store):
        problems.append("the store holds rows %s, the parse %s"
                        % (sorted(store), sorted(fresh)))
    else:
        for start in sorted(fresh):
            if store[start] != fresh[start]:
                problems.append("the store's row 0x%06X is not the parse's" % start)
    out = encode(store, rom, head)
    for start in sorted(out):
        path = os.path.join(resolve(args.out_dir), name(start, dict(ROWS)[start]))
        if not os.path.exists(path):
            problems.append("%s is missing" % path)
        elif open(path, "rb").read() != rom[start:dict(ROWS)[start]]:
            problems.append("%s is not the image's bytes" % path)
    for carrier in CARRIERS:
        text = open(resolve(carrier), encoding="utf-8", errors="replace").read()
        wanted = [line for line in text.split("\n") if ".extracted" in line]
        if wanted:
            problems.append("%s still INCBINs a retail slice" % carrier)
    for problem in problems:
        print("VERIFY FAIL: %s" % problem)
    print("rows=%d bytes=%d verify %s"
          % (len(out), sum(len(blob) for blob in out.values()),
             "PASS" if not problems else "FAIL (%d)" % len(problems)))
    return 1 if problems else 0


def cmd_name(args):
    for row in ROWS:
        print(token(*row))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for command, payloads in (("extract", True), ("build", True), ("verify", True)):
        step = sub.add_parser(command)
        step.add_argument("--rom", default="baserom.gba")
        step.add_argument("--payloads", default=os.path.join("assets", BLOCK))
        step.add_argument("--out-dir", default=OUT_DIR)
    sub.add_parser("name")
    args = parser.parse_args(argv)
    return {"extract": cmd_extract, "build": cmd_build, "verify": cmd_verify,
            "name": cmd_name}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
