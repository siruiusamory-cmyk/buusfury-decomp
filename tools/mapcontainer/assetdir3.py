"""Directory 3 at 0x3BB78C (53 x 20 B): the descriptor, its consumer, and the stream machine.

The table is 53 records of `{u32 array_base, u32 ramp_base, u32 0x0836D18C, u32 0x0836D540,
u16 value, u16 0}` at file `0x3BB78C`. The consumer is `0x0803EEE4`, called once per tick by
`0x0803EFD0` and re-armed from `record[+0x11]`. Decoded from the retail bytes instruction by
instruction (listing in the ticket's scratch), one CALL of it is:

    r1 = ++obj[1];  if r1 < obj[2] -> keep the stream pointer obj[0x14]
    else: obj[0x10] += 1; b = ramp[obj[0x10]]; if b == 0xFF: obj[0x10] = 0
          index = ramp[obj[0x10]]; obj[1] = 0
          block = record[+0] + 4*index; obj[0x14] = block + 1; obj[2] = block[0]
    then, from obj[0x14]: op = *p++; if op == 0: return
          slot = op & 0x0F, class = op >> 4
          class 0 -> one operand byte, stored to sub+0x59 AND sub+0x58
          class 1 -> sub+0x58 = sub+0x59 (the slot's last class-0 operand, which PERSISTS)
          class 2..15 -> sub+0x58 = payload[class - 2]   (the 14-byte class head)
          then the flag in sub+0x58: BITS 0,1,2 each take one operand byte into sub+0x5A..5C and
          BIT 3 takes two into sub+0x5D/0x5E
          repeat until the op byte is 0

`obj[2]` is therefore a CALL budget, not an entry count: a block serves `obj[2]` calls, and its
following calls continue the stream one byte at a time from where the last one stopped. That is
how the 291,135 B SCRIPT-BANK-002 could not explain are reached: not through a second index but
by the stream creeping past the blocks the pointer array names.

CORRECTED 2026-10-17 (SCRIPT-BANK-003): the flag bits are 0,1,2 and 3, not 7,6,5 and 4. The
routine tests them with `lsls rX,r2,#0x1f/#0x1e/#0x1d/#0x1c`, which shifts bit 0 to bit 31 - the
earlier decode read those shifts as a test of the HIGH bits and produced a grammar that could not
stay in phase. The class-0 operand also persists in sub+0x59 across calls (only sub+0x58 is
cleared, at the start of every call), which class 1 reads back.

MEASURED on the canonical image, and what each number rests on:

* the machine reaches 318,712 of the 320,076 payload bytes and every one of them gets exactly ONE
  role (0 addresses with two roles), so the roles partition the payload;
* against the BANK-READWATCH-001 run (session `bank-4`, 88,006 watch rows, 66,538
  distinct bank bytes) the role this walk assigns agrees with the role the runtime pc names for
  66,458 of 66,538 bytes (99.8798 %); the 80 that disagree are addresses read in two roles at
  different times (ramp[0] as ramp2 after a 0xFF reset and later as ramp1), and 0 runtime bytes
  are unmodelled. That correspondence is the calibration: the 12 runtime pcs are exactly the 12
  bank-reading loads in `0x0803EEE4`, each reported at its own address + 4;
* every READ run of SCRIPT-BANK-002 (81 of them) has its first byte reached by this walk;
* the null: the same walk over a byte-permuted payload classifies 61 of 320,076 bytes, because the
  permuted ramp bytes are no longer indices below the array's word count. Permuting only the
  stream bytes leaves coverage at ~100 % - any byte sequence is a legal opcode stream - so
  COVERAGE ALONE IS NOT EVIDENCE for the grammar; the runtime role agreement is.

Unexplained = bytes no call sequence of the machine reads. They are reported, never absorbed.

  python -m tools.mapcontainer.assetdir3 --rom baserom.gba [--csv OUT.csv]
        [--runs <scratch runs file>] [--hits rt001-hits.csv]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import struct
import sys

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
TABLE = 0x3BB78C
RECORD = 20
COUNT = 53
PAYLOAD = (0x36D540, 0x3BB78C)
ROWS = ((0x36D540, 0x3715C0), (0x3725C0, 0x3BB78C))
HEAD = (0x36D540, 14)
ROM_BASE = 0x08000000
FIXED = {8: 0x0836D18C, 12: 0x0836D540}
ISLAND = (0x3715C0, 0x3725C0)

QUIET = 1024
CAP = 60000

PC_ROLE = {0x0803EF06: "ramp", 0x0803EF14: "ramp", 0x0803EF18: "array", 0x0803EF20: "count",
           0x0803EF3E: "opcode", 0x0803EF5E: "cls0", 0x0803EF80: "head", 0x0803EF96: "bit0",
           0x0803EFA4: "bit1", 0x0803EFB2: "bit2", 0x0803EFC0: "bit3a", 0x0803EFCA: "bit3b"}

HEAD_BYTES, RAMP, ARRAY, COUNT_BYTE = "head", "ramp", "array", "count"
OPCODE, OPERAND, UNEXPLAINED = "opcode", "operand", "unexplained"
OPERANDS = ("cls0", "bit0", "bit1", "bit2", "bit3a", "bit3b")


def read_rom(path):
    data = open(path, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ROM_SHA256:
        raise SystemExit("ROM sha256 %s is not the canonical %s" % (digest, ROM_SHA256))
    return data


def u32(rom, at):
    return struct.unpack_from("<I", rom, at)[0]


def u16(rom, at):
    return struct.unpack_from("<H", rom, at)[0]


def file_of(address):
    return address - ROM_BASE


def operand_count(flag):
    return ((1 if flag & 0x01 else 0) + (1 if flag & 0x02 else 0)
            + (1 if flag & 0x04 else 0) + (2 if flag & 0x08 else 0))


def head_bytes(rom):
    return bytes(rom[HEAD[0]:HEAD[0] + HEAD[1]])


def descriptor(rom, table=TABLE, count=COUNT, payload=PAYLOAD):
    records = []
    for index in range(count):
        at = table + RECORD * index
        records.append({"index": index, "table": at,
                        "array_base": file_of(u32(rom, at)),
                        "ramp_base": file_of(u32(rom, at + 4)),
                        "fields": {offset: u32(rom, at + offset) for offset in FIXED},
                        "value": u16(rom, at + 0x10), "pad": u16(rom, at + 0x12)})
    for index, record in enumerate(records):
        following = (records[index + 1]["ramp_base"] if index + 1 < len(records) else payload[1])
        record["end"] = following
        record["words"] = (following - record["array_base"]) // 4
        record["addresses"] = [file_of(u32(rom, record["array_base"] + 4 * word))
                               for word in range(record["words"])]
        first = min([address for address in record["addresses"]
                     if record["ramp_base"] <= address < record["array_base"]] or
                    [record["array_base"]])
        record["ramp"] = rom[record["ramp_base"]:first]
    return records


def machine(rom, record, quiet=QUIET, cap=CAP, head=None, trace=False, payload=PAYLOAD):
    if head is None:
        head = head_bytes(rom)
    low, high = payload
    arr, ramp, words = record["array_base"], record["ramp_base"], record["words"]
    roles, entries, origin = {}, [], {}
    counter, count, budget, ptr = -1, 0, 1, 0
    carry = [0] * 16
    calls = last_new = 0
    block = 0
    stop = "saturated"

    def take(at, role):
        nonlocal last_new
        if not low <= at < high:
            return False
        if at in roles:
            return False
        roles[at] = role
        if trace:
            origin[at] = (record["index"], calls, block)
        last_new = calls
        return True

    def take_all(at, role, width):
        fresh = False
        for offset in range(width):
            fresh = take(at + offset, role) or fresh
        return fresh

    while calls < cap:
        calls += 1
        if calls - last_new > quiet:
            break
        count += 1
        if count >= budget:
            counter += 1
            at = ramp + counter
            if not low <= at < high:
                stop = "ramp read left the payload"
                break
            take(at, RAMP)
            if rom[at] == 0xFF:
                counter = 0
                at = ramp
            take(at, RAMP)
            index = rom[at]
            if index >= words:
                stop = "array index %d outside %d words" % (index, words)
                break
            word = arr + 4 * index
            if not low <= word < high:
                stop = "array word left the payload"
                break
            take_all(word, ARRAY, 4)
            block = file_of(u32(rom, word))
            if not low <= block < high:
                stop = "block pointer outside the payload"
                break
            count = 0
            take(block, COUNT_BYTE)
            budget = rom[block]
            ptr = block + 1
        while True:
            if not low <= ptr < high:
                stop = "stream left the payload"
                break
            start = ptr
            op = rom[ptr]
            fresh = take(ptr, OPCODE)
            ptr += 1
            if op == 0:
                if fresh:
                    entries.append((start, 1, None, None, None, b""))
                break
            slot, cls = op & 0x0F, op >> 4
            operands = b""
            if cls == 0:
                if not low <= ptr < high:
                    stop = "operand left the payload"
                    break
                carry[slot] = rom[ptr]
                take(ptr, "cls0")
                operands += bytes([rom[ptr]])
                ptr += 1
                flag = carry[slot]
            elif cls == 1:
                flag = carry[slot]
            else:
                take(low + cls - 2, HEAD_BYTES)
                flag = head[cls - 2]
            need = operand_count(flag)
            if ptr + need > high:
                stop = "operands left the payload"
                break
            cursor = ptr
            if flag & 0x01:
                take(cursor, "bit0")
                cursor += 1
            if flag & 0x02:
                take(cursor, "bit1")
                cursor += 1
            if flag & 0x04:
                take(cursor, "bit2")
                cursor += 1
            if flag & 0x08:
                take(cursor, "bit3a")
                take(cursor + 1, "bit3b")
                cursor += 2
            operands += bytes(rom[ptr:ptr + need])
            if fresh:
                entries.append((start, 1 + len(operands), cls, slot, flag, operands))
            ptr += need
        if stop != "saturated":
            break
    else:
        stop = "cap"
    return {"roles": roles, "entries": entries, "origin": origin, "calls": calls,
            "last": last_new, "stop": stop, "saturated": calls - last_new > quiet}


def walk(rom, records=None, quiet=QUIET, cap=CAP, trace=False, payload=PAYLOAD):
    if records is None:
        records = descriptor(rom, payload=payload)
    head = bytes(rom[payload[0]:payload[0] + HEAD[1]])
    roles, entries, stats, origin = {}, [], [], {}
    for record in records:
        out = machine(rom, record, quiet=quiet, cap=cap, head=head, trace=trace,
                      payload=payload)
        for at, role in out["roles"].items():
            roles.setdefault(at, role)
        if trace:
            for at, where in out["origin"].items():
                origin.setdefault(at, where)
        stats.append({"index": record["index"], **{k: out[k] for k in
                                                   ("calls", "last", "stop", "saturated")},
                      "bytes": len(out["roles"]),
                      "entries": len({entry[0] for entry in out["entries"]})})
        for entry in out["entries"]:
            entries.append((record["index"],) + entry)
    unique, seen = [], set()
    for entry in entries:
        if entry[1] in seen:
            continue
        seen.add(entry[1])
        unique.append(entry)
    return roles, unique, stats, origin


def classify(rom, roles, payload=PAYLOAD):
    kinds = [UNEXPLAINED] * (payload[1] - payload[0])
    for at, role in roles.items():
        if not payload[0] <= at < payload[1]:
            continue
        if role == RAMP:
            kinds[at - payload[0]] = RAMP
        elif role == ARRAY:
            kinds[at - payload[0]] = ARRAY
        elif role == COUNT_BYTE:
            kinds[at - payload[0]] = COUNT_BYTE
        elif role == HEAD_BYTES:
            kinds[at - payload[0]] = HEAD_BYTES
        elif role == OPCODE:
            kinds[at - payload[0]] = OPCODE
        elif role in OPERANDS:
            kinds[at - payload[0]] = OPERAND
    return kinds


def counts(kinds, payload, row):
    out = {}
    for at in range(row[0], row[1]):
        kind = kinds[at - payload[0]]
        out[kind] = out.get(kind, 0) + 1
    return out


def runs(kinds, payload, row, kind=UNEXPLAINED):
    out, start = [], None
    for at in range(row[0], row[1] + 1):
        here = at < row[1] and kinds[at - payload[0]] == kind
        if here and start is None:
            start = at
        elif not here and start is not None:
            out.append((start, at - start))
            start = None
    return out


def uniform(rom, runs_list):
    return sum(1 for address, length in runs_list if len(set(rom[address:address + length])) <= 2)


def packed_container(blob):
    if len(blob) < 8:
        return False
    kind, declared = struct.unpack_from("<II", blob, 0)
    return kind in (0, 1, 2) and 24 <= declared <= len(blob)


def decodes(rom, runs_list):
    hits = {"lz77": 0, "rle": 0, "webfoot": 0, "jcalg1": 0}

    def lz(src):
        if not src or src[0] != 0x10:
            return False
        out = bytearray()
        index = 1
        while index < len(src):
            flags = src[index]
            index += 1
            for bit in range(7, -1, -1):
                if index >= len(src):
                    return False
                if flags & (1 << bit):
                    if index + 1 >= len(src):
                        return False
                    count = ((src[index] >> 4) & 0xF) + 3
                    distance = (((src[index] & 0xF) << 8) | src[index + 1]) + 1
                    index += 2
                    for _ in range(count):
                        if distance > len(out):
                            return False
                        out.append(out[-distance])
                else:
                    out.append(src[index])
                    index += 1
        return bool(out)

    def rle(src):
        if not src or src[0] != 0x30:
            return False
        out = bytearray()
        index = 1
        while index < len(src):
            flag = src[index]
            index += 1
            if flag & 0x80:
                if index >= len(src):
                    return False
                out += bytes([src[index]]) * ((flag & 0x7F) + 3)
                index += 1
            else:
                count = (flag & 0x7F) + 1
                if index + count > len(src):
                    return False
                out += src[index:index + count]
                index += count
        return bool(out)

    for address, length in runs_list:
        source = rom[address:address + length]
        hits["lz77"] += 1 if lz(source) else 0
        hits["rle"] += 1 if rle(source) else 0
        hits["webfoot"] += 1 if packed_container(source) else 0
        hits["jcalg1"] += 1 if source[:4] == b"JCAL" else 0
    return hits


def null_coverage(rom, roles, payload=PAYLOAD, seed=1):
    import random

    def cover(image):
        roles, _entries, _stats, _origin = walk(bytes(image))
        return sum(1 for at in roles if payload[0] <= at < payload[1])

    real = sum(1 for at in roles if payload[0] <= at < payload[1])
    rng = random.Random(seed)
    shuffled = bytearray(rom[payload[0]:payload[1]])
    rng.shuffle(shuffled)
    full = bytearray(rom)
    full[payload[0]:payload[1]] = shuffled
    records = descriptor(rom)
    stream = bytearray(rom)
    for record in records:
        first = record["ramp_base"] + len(record["ramp"])
        body = bytearray(rom[first:record["array_base"]])
        rng.shuffle(body)
        stream[first:record["array_base"]] = body
    return real, cover(full), cover(stream)


def read_hits(path):
    roles, pcs, rows = {}, {}, 0
    with open(path, newline="", encoding="utf-8", errors="replace") as handle:
        handle.readline()
        for line in handle:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            try:
                pc, address = int(parts[0], 16), int(parts[1], 16)
            except ValueError:
                continue
            rows += 1
            if pc not in PC_ROLE:
                continue
            pcs[pc] = pcs.get(pc, 0) + 1
            roles[address - ROM_BASE] = PC_ROLE[pc]
    return roles, pcs, rows


def read_runs(path):
    out = []
    with open(path, newline="", encoding="utf-8") as handle:
        handle.readline()
        for line in handle:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                out.append((int(parts[1], 16), int(parts[2])))
    return out


def verify(rom, records, roles, stats, entries, payload=PAYLOAD):
    problems = []

    def note(text, at=None):
        problems.append(text if at is None else "%s at file 0x%06X" % (text, at))

    previous = 0
    for record in records:
        at = record["table"]
        for offset, value in FIXED.items():
            if record["fields"][offset] != value:
                note("[+%d] is 0x%08X, not the measured 0x%08X"
                     % (offset, record["fields"][offset], value), at)
        if record["pad"] != 0:
            note("[+0x12] is %d, not 0" % record["pad"], at)
        if not record["ramp_base"] < record["array_base"]:
            note("ramp_base is not below array_base", at)
        if record["ramp_base"] < previous:
            note("ramp_base is not past the previous record's array", at)
        if (record["end"] - record["array_base"]) % 4:
            note("the array does not end on the next ramp_base", record["array_base"])
        previous = record["array_base"]
        for word in range(record["words"]):
            address = record["addresses"][word]
            if not record["ramp_base"] <= address < record["array_base"]:
                note("array word %d points outside its own span" % word,
                     record["array_base"] + 4 * word)
        for byte in record["ramp"]:
            if byte != 0xFF and byte >= record["words"]:
                note("ramp byte %d is neither 0xFF nor below the %d words"
                     % (byte, record["words"]), record["ramp_base"])
    for stat in stats:
        if stat["stop"] == "cap":
            note("record %d hit the call cap, so its role set is not a fixpoint"
                 % stat["index"])
    head = bytes(rom[payload[0]:payload[0] + HEAD[1]])
    for _record, start, size, cls, slot, flag, operands in entries:
        if cls is None:
            if rom[start] != 0:
                note("a terminator entry is not a zero byte", start)
            continue
        if cls == 0 and operands[0] != flag:
            note("an entry's class-0 operand is not the flag it stores", start)
        if 1 < cls < 16 and flag != head[cls - 2]:
            note("an entry's class-%d flag is not head[%d]" % (cls, cls - 2), start)
        if len(operands) != (1 if cls == 0 else 0) + operand_count(flag):
            note("an entry carries %d operands where its flag takes %d"
                 % (len(operands), (1 if cls == 0 else 0) + operand_count(flag)), start)
        if rom[start:start + size] != bytes([(cls << 4) | slot]) + operands:
            note("the re-serialized entry is not the image's", start)
    return problems


def report(rom, records, roles, stats, kinds, entries, payload=PAYLOAD, runs_list=(),
           hits=None, origin=None, table_path=None):
    print("%-3s %-8s %-8s %6s %5s %4s %6s %7s %8s %10s"
          % ("#", "ramp", "array", "span", "ramp", "word", "blocks", "entries",
             "covered", "unexplained"))
    per_record_entries = {}
    for entry in entries:
        per_record_entries[entry[0]] = per_record_entries.get(entry[0], 0) + 1
    for record in records:
        tally = counts(kinds, payload, (record["ramp_base"], record["end"]))
        print("%-3d %06x %6x %6d %5d %4d %6d %7d %8d %10d"
              % (record["index"], record["ramp_base"], record["array_base"],
                 record["end"] - record["ramp_base"], len(record["ramp"]), record["words"],
                 len(record["addresses"]), per_record_entries.get(record["index"], 0),
                 sum(count for kind, count in tally.items() if kind != UNEXPLAINED),
                 tally.get(UNEXPLAINED, 0)))
    print("entries %d, of which terminators %d"
          % (len(entries), sum(1 for entry in entries if entry[3] is None)))
    row_totals = {}
    for row in ROWS:
        tally = counts(kinds, payload, row)
        row_totals[row] = tally
        print("row 0x%06x..0x%06x %6d B: head %d ramp %d array %d count %d opcode %d operand %d"
              " unexplained %d = %d"
              % (row[0], row[1], row[1] - row[0], tally.get(HEAD_BYTES, 0), tally.get(RAMP, 0),
                 tally.get(ARRAY, 0), tally.get(COUNT_BYTE, 0), tally.get(OPCODE, 0),
                 tally.get(OPERAND, 0), tally.get(UNEXPLAINED, 0), sum(tally.values())))
    total = sum(row[1] - row[0] for row in ROWS)
    took = total - sum(row_totals[row].get(UNEXPLAINED, 0) for row in ROWS)
    rest = total - took
    print("covered=%d unexplained=%d total=%d residue_pct=%.4f"
          % (took, rest, total, 100.0 * rest / total))
    island = sum(1 for at in range(*ISLAND) if roles.get(at) is not None)
    print("the Thumb island 0x%06x..0x%06x (out of scope) holds %d machine bytes"
          % (ISLAND[0], ISLAND[1], island))
    real, permuted, stream_only = null_coverage(rom, roles, payload)
    print("null coverage of the payload 0x%06x..0x%06x: real %d, byte-permuted %d,"
          " stream-bytes-only-permuted %d"
          % (payload[0], payload[1], real, permuted, stream_only))
    sizes = sorted(length for row in ROWS for _address, length in runs(kinds, payload, row))
    if sizes:
        print("unexplained runs min/median/max %d/%d/%d, padding-shaped %d"
              % (sizes[0], sizes[len(sizes) // 2], sizes[-1],
                 uniform(rom, [run for row in ROWS for run in runs(kinds, payload, row)])))
    if runs_list:
        read = set(hits[0]) if hits else set()
        tags = {}
        for start, size in runs_list:
            kinds_here = {kinds[at - payload[0]] for at in range(start, min(start + size, payload[1]))
                          if payload[0] <= at < payload[1]}
            got = [kind for kind in (OPCODE, OPERAND) if kind in kinds_here]
            if read:
                is_read = any(at in read for at in range(start, start + size))
                tag = ("READ+PARSED" if got else "READ+UNPARSED") if is_read else \
                      ("PARSED-ONLY" if got else "UNEXPLAINED")
            else:
                tag = "PARSED-ONLY" if got else "UNEXPLAINED"
            tags[tag] = tags.get(tag, 0) + 1
        print("SCRIPT-BANK-002's %d runs: %s" % (len(runs_list), dict(sorted(tags.items()))))
        table = []
        for start, size in runs_list:
            read = set(hits[0]) if hits else set()
            is_read = any(at in read for at in range(start, start + size))
            kinds_here = {kinds[at - payload[0]] for at in
                          range(start, min(start + size, payload[1]))
                          if payload[0] <= at < payload[1]}
            parsed = OPCODE in kinds_here or OPERAND in kinds_here
            where = origin.get(start)
            table.append((start, size, sum(1 for at in range(start, start + size) if at in read),
                          "READ+PARSED" if is_read and parsed else
                          "READ+UNPARSED" if is_read else
                          "PARSED-ONLY" if parsed else "UNEXPLAINED",
                          roles.get(start, "UNREACHED"),
                          where[0] if where else "", where[1] if where else "",
                          "0x%06x" % where[2] if where else ""))
        if table_path:
            with open(table_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["run_start", "bytes", "bytes_read", "class", "first_byte_role",
                                 "record", "call", "block"])
                writer.writerows(table)
        if hits:
            firsts = sum(1 for row in table if row[2] and row[4] == OPCODE)
            read_runs = sum(1 for row in table if row[2])
            print("reach path: %d of %d runtime-read runs have their first byte reached as an"
                  " opcode" % (firsts, read_runs))
            for row in table:
                if row[2] and row[4] != OPCODE:
                    print("  not an opcode: run 0x%06x %d B, first byte role %s (record %s,"
                          " call %s, block %s)" % (row[0], row[1], row[4], row[5], row[6], row[7]))
    if hits:
        runtime, pcs, rows = hits
        agree = sum(1 for at, role in runtime.items() if at in roles and roles[at] == role)
        unmodelled = sum(1 for at in runtime if at not in roles)
        print("runtime calibration: %d watch rows, %d bank bytes, %d pcs; role agreement"
              " %d/%d = %.4f %%; disagreements are bytes the machine reads in two roles;"
              " unmodelled %d"
              % (rows, len(runtime), len(pcs), agree, len(runtime),
                 100.0 * agree / max(len(runtime), 1), unmodelled))
    return took, rest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--csv")
    parser.add_argument("--runs")
    parser.add_argument("--hits")
    parser.add_argument("--reach")
    args = parser.parse_args(argv)
    rom = read_rom(args.rom)
    records = descriptor(rom)
    roles, entries, stats, origin = walk(rom, records, trace=True)
    kinds = classify(rom, roles)
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["index", "ramp_base", "array_base", "span", "ramp_length",
                             "array_words", "entries", "covered", "unexplained"])
            for record in records:
                tally = counts(kinds, PAYLOAD, (record["ramp_base"], record["end"]))
                writer.writerow([record["index"], "0x%06x" % record["ramp_base"],
                                 "0x%06x" % record["array_base"],
                                 record["end"] - record["ramp_base"], len(record["ramp"]),
                                 record["words"], 0,
                                 sum(count for kind, count in tally.items()
                                     if kind != UNEXPLAINED),
                                 tally.get(UNEXPLAINED, 0)])
    hits = read_hits(args.hits) if args.hits else None
    runs_list = read_runs(args.runs) if args.runs else []
    took, rest = report(rom, records, roles, stats, kinds, entries, runs_list=runs_list,
                        hits=hits, origin=origin, table_path=args.reach)
    problems = verify(rom, records, roles, stats, entries)
    for problem in problems[:20]:
        print("VERIFY FAIL: %s" % problem)
    print("invariants %s" % ("PASS" if not problems else "FAIL (%d)" % len(problems)))
    total = sum(row[1] - row[0] for row in ROWS)
    return 1 if problems or took + rest != total else 0


if __name__ == "__main__":
    sys.exit(main())
