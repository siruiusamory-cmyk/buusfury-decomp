from __future__ import annotations

import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "structured"))

import families  # noqa: E402

ROM_BASE = 0x08000000
ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
INTERPRETER = 0x08004038
TABLE = 0x080554C0
TABLE_LITERAL = 0x0800415C
END = 0x11
DOC_OUT = os.path.join(ROOT, "docs", "research", "OPCODE_STREAM_CENSUS.md")
FAMILY = "map_script_stream"
CACHE = "opcode"
LOOP = (
    (0x08004066, "0878", "ldrb r0,[r1]"),
    (0x08004068, "0131", "adds r1,#1"),
    (0x0800406A, "0191", "str r1,[sp,#4]"),
    (0x0800406C, "8000", "lsls r0,r0,#2"),
    (0x0800406E, "3a58", "ldr r2,[r7,r0]"),
    (0x08004070, "002a", "cmp r2,#0"),
    (0x08004072, "0cd1", "bne #0x800408e"),
    (0x0800405E, "3f4f", "ldr r7,[pc,#0xfc]"),
)
HANDLERS = {
    0x00: (0x08003C74, "byte", (
        (0x08003C76, "531c", "adds r3,r2,#1"),
        (0x08003C78, "0b60", "str r3,[r1]"),
        (0x08003C7C, "1378", "ldrb r3,[r2]"))),
    0x01: (0x08003C8A, "varint", (
        (0x08003C92, "2378", "ldrb r3,[r4]"),
        (0x08003C94, "0134", "adds r4,#1"),
        (0x08003CA0, "f5d4", "bmi #0x8003c8e"))),
    0x02: (0x08003CBE, "byte", (
        (0x08003CC2, "1a78", "ldrb r2,[r3]"),
        (0x08003CC4, "0133", "adds r3,#1"),
        (0x08003CC6, "0b60", "str r3,[r1]"))),
    0x03: (0x08003CD4, "byte", (
        (0x08003CD8, "1a78", "ldrb r2,[r3]"),
        (0x08003CDA, "0133", "adds r3,#1"),
        (0x08003CDC, "0b60", "str r3,[r1]"))),
    0x04: (0x08003CF6, "none", ((0x08003CF6, "0168", "ldr r1,[r0]"),)),
    0x05: (0x08003D16, "none", ((0x08003D16, "0168", "ldr r1,[r0]"),)),
    0x06: (0x08003D30, "none", ((0x08003D30, "0168", "ldr r1,[r0]"),)),
    0x07: (0x08003D3E, "none", ((0x08003D3E, "0168", "ldr r1,[r0]"),)),
    0x08: (0x08003D52, "none", ((0x08003D52, "0168", "ldr r1,[r0]"),)),
    0x09: (0x08003D66, "none", ((0x08003D66, "0168", "ldr r1,[r0]"),)),
    0x0A: (0x08003D7A, "none", ((0x08003D7C, "0168", "ldr r1,[r0]"),)),
    0x0B: (0x08003DAA, "none", ((0x08003DAA, "0168", "ldr r1,[r0]"),)),
    0x0C: (0x08003DC4, "none", ((0x08003DC4, "0168", "ldr r1,[r0]"),)),
    0x0D: (0x08003DDE, "none", ((0x08003DDE, "0168", "ldr r1,[r0]"),)),
    0x0E: (0x08003DF8, "none", ((0x08003DF8, "0168", "ldr r1,[r0]"),)),
    0x0F: (0x08003E12, "none", ((0x08003E12, "0168", "ldr r1,[r0]"),)),
    0x10: (0x08003E2C, "none", ((0x08003E2C, "0168", "ldr r1,[r0]"),)),
    0x12: (0x08003E46, "jump", (
        (0x08003E48, "0278", "ldrb r2,[r0]"),
        (0x08003E4A, "4378", "ldrb r3,[r0,#1]"),
        (0x08003E50, "8018", "adds r0,r0,r2"),
        (0x08003E52, "0860", "str r0,[r1]"))),
    0x13: (0x08003E56, "branch", (
        (0x08003E64, "0868", "ldr r0,[r1]"),
        (0x08003E68, "0278", "ldrb r2,[r0]"),
        (0x08003E6A, "4378", "ldrb r3,[r0,#1]"),
        (0x08003E70, "8018", "adds r0,r0,r2"),
        (0x08003E76, "0230", "adds r0,#2"))),
    0x14: (0x08003E7C, "none", ((0x08003E7C, "0168", "ldr r1,[r0]"),)),
    0x15: (0x08003E84, "byte", (
        (0x08003E8A, "1078", "ldrb r0,[r2]"),
        (0x08003E8C, "0132", "adds r2,#1"),
        (0x08003E8E, "0a60", "str r2,[r1]"))),
    0x16: (0x08003EB4, "byte", (
        (0x08003EBA, "1078", "ldrb r0,[r2]"),
        (0x08003EBC, "0132", "adds r2,#1"),
        (0x08003EBE, "0a60", "str r2,[r1]"))),
    0x17: (0x08003EE4, "byte", (
        (0x08003EEA, "1078", "ldrb r0,[r2]"),
        (0x08003EEC, "0132", "adds r2,#1"),
        (0x08003EEE, "0a60", "str r2,[r1]"))),
    0x18: (0x08003F10, "byte", (
        (0x08003F16, "1078", "ldrb r0,[r2]"),
        (0x08003F18, "0132", "adds r2,#1"),
        (0x08003F1A, "0a60", "str r2,[r1]"))),
    0x19: (0x08003F48, "byte", (
        (0x08003F4E, "1078", "ldrb r0,[r2]"),
        (0x08003F50, "0132", "adds r2,#1"),
        (0x08003F52, "0a60", "str r2,[r1]"))),
    0x1A: (0x08003F78, "byte", (
        (0x08003F7E, "1078", "ldrb r0,[r2]"),
        (0x08003F80, "0132", "adds r2,#1"),
        (0x08003F82, "0a60", "str r2,[r1]"))),
    0x1B: (0x08003FA4, "none", ((0x08003FA4, "0168", "ldr r1,[r0]"),)),
    0x1C: (0x08003FC0, "loop", (
        (0x08003FD0, "0868", "ldr r0,[r1]"),
        (0x08003FE0, "0278", "ldrb r2,[r0]"),
        (0x08003FE2, "4378", "ldrb r3,[r0,#1]"),
        (0x08003FE8, "801a", "subs r0,r0,r2"),
        (0x08003FD4, "0230", "adds r0,#2"))),
    0x1D: (0x08003FEE, "counted", (
        (0x08003FF2, "1578", "ldrb r5,[r2]"),
        (0x08003FFE, "2378", "ldrb r3,[r4]"),
        (0x08004028, "e6d1", "bne #0x8003ff8"))),
    0x1E: (0x08003D92, "none", ((0x08003D94, "0168", "ldr r1,[r0]"),)),
}
OPERANDS = {
    "byte": "one byte",
    "varint": "one 7-bit varint, bit 7 continues",
    "jump": "two bytes, signed target = operand + offset",
    "branch": "two bytes, then the next instruction or operand + offset",
    "loop": "two bytes, then the next instruction or operand - offset",
    "counted": "one count byte, then that many 7-bit varints",
    "none": "none",
}


def read_rom(path=None):
    path = path or os.path.join(ROOT, "baserom.gba")
    with open(path, "rb") as handle:
        rom = handle.read()
    if hashlib.sha256(rom).hexdigest() != ROM_SHA256:
        raise SystemExit("%s is not the canonical image" % path)
    return rom


def halfword(rom, address):
    return rom[address - ROM_BASE:address - ROM_BASE + 2].hex()


def pinned(rom):
    for address, word, _text in LOOP:
        found = halfword(rom, address)
        if found != word:
            raise SystemExit("0x%08X holds %s, not %s" % (address, found, word))
    literal = int.from_bytes(rom[TABLE_LITERAL - ROM_BASE:TABLE_LITERAL - ROM_BASE + 4], "little")
    if literal != TABLE:
        raise SystemExit("the table literal is 0x%08X, not 0x%08X" % (literal, TABLE))
    for opcode, (handler, _kind, quotes) in HANDLERS.items():
        found = int.from_bytes(rom[TABLE - ROM_BASE + 4 * opcode:TABLE - ROM_BASE + 4 * opcode + 4],
                               "little")
        if found != handler | 1:
            raise SystemExit("table entry 0x%02X is 0x%08X, not 0x%08X" % (opcode, found, handler | 1))
        for address, word, _text in quotes:
            if halfword(rom, address) != word:
                raise SystemExit("0x%08X holds %s, not %s" % (address, halfword(rom, address), word))
    end = int.from_bytes(rom[TABLE - ROM_BASE + 4 * END:TABLE - ROM_BASE + 4 * END + 4], "little")
    if end:
        raise SystemExit("table entry 0x%02X is 0x%08X, not the null the loop exits on" % (END, end))


def varint(rom, at, end):
    value = 0
    first = at
    while True:
        if at >= end:
            return None
        byte = rom[at]
        at += 1
        value = ((value << 7) | (byte & 0x7F)) & 0xFFFFFFFF
        if not byte & 0x80:
            break
    if at - first > 1 and not rom[first] & 0x7F:
        return None
    return value, at


def varint_bytes(value, count):
    out = bytearray()
    for shift in range(count - 1, -1, -1):
        group = (value >> (7 * shift)) & 0x7F
        out.append(group | (0x80 if shift else 0))
    return bytes(out)


def sizes(value):
    return max(1, (value.bit_length() + 6) // 7)


def decode(rom, start, end):
    instructions = {}
    ends = []
    bad = []
    work = [start]
    while work:
        at = work.pop()
        if at in instructions or at in ends:
            continue
        if not start <= at < end:
            bad.append((at, "outside"))
            continue
        opcode = rom[at]
        if opcode == END:
            instructions[at] = (END, 1, [])
            ends.append(at)
            continue
        if opcode not in HANDLERS:
            bad.append((at, "opcode 0x%02X" % opcode))
            continue
        kind = HANDLERS[opcode][1]
        cursor = at + 1
        if kind == "byte":
            if cursor + 1 > end:
                bad.append((at, "operand"))
                continue
            instructions[at] = (opcode, 2, [rom[cursor]])
            work.append(cursor + 1)
        elif kind == "varint":
            got = varint(rom, cursor, end)
            if got is None:
                bad.append((at, "varint"))
                continue
            value, stop = got
            instructions[at] = (opcode, stop - at, [value])
            work.append(stop)
        elif kind == "counted":
            if cursor + 1 > end:
                bad.append((at, "count"))
                continue
            count = rom[cursor]
            stop = cursor + 1
            values = []
            for _index in range(count):
                got = varint(rom, stop, end)
                if got is None:
                    bad.append((at, "varint"))
                    stop = None
                    break
                values.append(got[0])
                stop = got[1]
            if stop is None:
                continue
            instructions[at] = (opcode, stop - at, [count] + values)
            work.append(stop)
        elif kind in ("jump", "branch", "loop"):
            if cursor + 2 > end:
                bad.append((at, "operand"))
                continue
            offset = (rom[cursor] << 8) | rom[cursor + 1]
            if kind == "loop":
                target = cursor - offset
            else:
                target = cursor + offset
            instructions[at] = (opcode, 3, [target])
            if kind == "jump":
                work.append(target)
            else:
                work.append(at + 3)
                work.append(target)
        else:
            instructions[at] = (opcode, 1, [])
            work.append(cursor)
    cover = {}
    overlap = []
    for at, (opcode, size, operands) in instructions.items():
        for byte in range(at, at + size):
            if byte in cover:
                overlap.append((at, cover[byte]))
            cover[byte] = at
    if overlap:
        bad.extend(overlap)
    missing = [byte for byte in range(start, end) if byte not in cover]
    return {"start": start, "end": end, "instructions": instructions, "ends": sorted(ends),
            "bad": bad, "missing": missing}


def encode(decoded):
    out = bytearray()
    at = decoded["start"]
    for address in sorted(decoded["instructions"]):
        if address != at:
            raise SystemExit("instruction at 0x%06X does not follow 0x%06X" % (address, at))
        opcode, size, operands = decoded["instructions"][address]
        out.append(opcode)
        if opcode == END:
            at += size
            continue
        kind = HANDLERS[opcode][1]
        if kind == "byte":
            out += bytes(operands)
        elif kind == "varint":
            out += varint_bytes(operands[0], size - 1)
        elif kind == "counted":
            out.append(operands[0])
            for value in operands[1:]:
                out += varint_bytes(value, sizes(value))
        elif kind == "jump" or kind == "branch":
            offset = operands[0] - (address + 1)
            if not 0 <= offset <= 0xFFFF:
                raise SystemExit("target of 0x%06X is not forward" % address)
            out += bytes((offset >> 8, offset & 0xFF))
        elif kind == "loop":
            offset = (address + 1) - operands[0]
            if not 0 <= offset <= 0xFFFF:
                raise SystemExit("target of 0x%06X is not backward" % address)
            out += bytes((offset >> 8, offset & 0xFF))
        at += size
    if at != decoded["end"]:
        raise SystemExit("the instructions end at 0x%06X, not 0x%06X" % (at, decoded["end"]))
    return bytes(out)


def rows(rom):
    plan = families.plan(rom)
    targets = set()
    for _offset, entry in families.map_entries(rom):
        value = entry.fields[21]
        if ROM_BASE <= value < ROM_BASE + len(rom):
            targets.add(value - ROM_BASE)
    out = []
    for low, high in plan.gaps:
        bounds = sorted({low} | {target for target in targets if low <= target < high})
        for index, base in enumerate(bounds):
            if base in targets:
                out.append((base, bounds[index + 1] if index + 1 < len(bounds) else high))
    return out


def census(rom):
    out = []
    for start, end in rows(rom):
        decoded = decode(rom, start, end)
        clean = not decoded["bad"] and not decoded["missing"] and decoded["ends"]
        stop = decoded["end"] - start if clean else (
            decoded["missing"][0] - start if decoded["missing"] else 0)
        out.append({"start": start, "end": end, "bytes": end - start, "stream": stop,
                    "moved": clean, "decoded": decoded})
    return out


def totals(table):
    moved = [row for row in table if row["moved"]]
    stayed = [row for row in table if not row["moved"]]
    return {"rows": len(table), "bytes": sum(row["bytes"] for row in table),
            "moved_rows": len(moved), "moved_bytes": sum(row["bytes"] for row in moved),
            "stayed_rows": len(stayed), "stayed_bytes": sum(row["bytes"] for row in stayed)}


def doc_text(table):
    counts = totals(table)
    lines = []
    add = lines.append
    add("# The opcode streams the interpreter at `0x08004038` reads")
    add("")
    add("Generated by `tools/research/opcode_stream.py`. The interpreter reads one opcode byte, looks")
    add("it up in the table at `0x%08X`, whose null entry ends the stream, and passes the stream" % TABLE)
    add("cursor to that opcode's handler. Each handler below is the retail Thumb body the table entry")
    add("names; the quoted halfwords are the operand reads that fix the opcode's length.")
    add("")
    for address, word, text in LOOP:
        add("- `0x%08X` `%s` `%s`" % (address, word, text))
    add("- entry `0x%02X` of the table is null, so `0x%02X` is the only end opcode" % (END, END))
    add("")
    add("## The opcode table")
    add("")
    add("| opcode | handler | operands | quoted operand reads |")
    add("|---|---|---|---|")
    for opcode in sorted(HANDLERS):
        handler, kind, quotes = HANDLERS[opcode]
        proof = ", ".join("`0x%08X` `%s` `%s`" % quote for quote in quotes)
        add("| `0x%02X` | `0x%08X` | %s | %s |" % (opcode, handler, OPERANDS[kind], proof))
    add("| `0x%02X` | none | ends the stream | the table entry is null |" % END)
    add("")
    add("## The %d rows the `MapEntry` `+0x30` field names" % counts["rows"])
    add("")
    add("| row | bytes | stream | stop | status |")
    add("|---|---|---|---|---|")
    for row in table:
        add("| `0x%06X..0x%06X` | %d | %d | %d | %s |"
            % (row["start"], row["end"], row["bytes"], row["stream"], row["stream"],
               "moved" if row["moved"] else "raw"))
    add("")
    add("## Counts")
    add("")
    add("%d rows / %d B: %d rows / %d B are consumed by proven opcodes to the row's last byte and end"
        % (counts["rows"], counts["bytes"], counts["moved_rows"], counts["moved_bytes"]))
    add("on `0x%02X`; %d rows / %d B carry a stream that ends on `0x%02X` at the stop column, and their"
        % (END, counts["stayed_rows"], counts["stayed_bytes"], END))
    add("remaining bytes are not reached by the interpreter call the field makes, so they stay raw.")
    add("")
    add("    python tools\\research\\opcode_stream.py")
    add("    python tools\\research\\opcode_stream.py --check")
    add("")
    return "\n".join(lines) + "\n"


def output(section, out_dir=None):
    out_dir = out_dir or os.path.join(ROOT, "build", CACHE)
    return os.path.join(out_dir, "gen_%06x_%06x.bin" % (section["start"], section["end"]))


def build(rom, out_dir):
    table = census(rom)
    written = 0
    moved = 0
    for row in table:
        if not row["moved"]:
            continue
        blob = encode(row["decoded"])
        if blob != rom[row["start"]:row["end"]]:
            raise SystemExit("the stream at 0x%06X does not re-emit its bytes" % row["start"])
        path = output(row, out_dir)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path, "rb").read() != blob:
            with open(path, "wb") as handle:
                handle.write(blob)
            written += 1
        moved += len(blob)
    counts = totals(table)
    print("family %s rows=%d moved=%d moved_bytes=%d stayed=%d stayed_bytes=%d files=%d"
          % (FAMILY, counts["rows"], counts["moved_rows"], counts["moved_bytes"],
             counts["stayed_rows"], counts["stayed_bytes"], written))
    print("%s: %d section file(s) written, %d B" % (FAMILY, written, moved))
    return 0


def check(rom):
    pinned(rom)
    table = census(rom)
    counts = totals(table)
    if (counts["rows"], counts["bytes"], counts["moved_rows"], counts["moved_bytes"]) != \
            (132, 14857, 34, 1004):
        raise SystemExit("the census is %d rows / %d B, %d moved / %d B"
                         % (counts["rows"], counts["bytes"], counts["moved_rows"],
                            counts["moved_bytes"]))
    for row in table:
        if row["moved"]:
            blob = encode(row["decoded"])
            if blob != rom[row["start"]:row["end"]]:
                raise SystemExit("the stream at 0x%06X does not re-emit its bytes" % row["start"])
        elif row["stream"] >= row["bytes"]:
            raise SystemExit("the raw row at 0x%06X states no stop" % row["start"])
    with open(DOC_OUT, encoding="utf-8") as handle:
        if handle.read() != doc_text(table):
            raise SystemExit("%s is not the census this tool derives" % os.path.relpath(DOC_OUT, ROOT))
    print("CHECK: %d rows / %d B, %d moved / %d B, %d raw / %d B"
          % (counts["rows"], counts["bytes"], counts["moved_rows"], counts["moved_bytes"],
             counts["stayed_rows"], counts["stayed_bytes"]))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--out-dir", default=os.path.join(ROOT, "build", CACHE))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("command", nargs="?", default="census", choices=("census", "build"))
    args = parser.parse_args(argv)
    rom = read_rom(args.rom)
    if args.command == "build":
        return build(rom, os.path.abspath(args.out_dir))
    pinned(rom)
    table = census(rom)
    if args.check:
        return check(rom)
    counts = totals(table)
    print("rows %d bytes %d  moved %d rows %d B  raw %d rows %d B"
          % (counts["rows"], counts["bytes"], counts["moved_rows"], counts["moved_bytes"],
             counts["stayed_rows"], counts["stayed_bytes"]))
    with open(DOC_OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(doc_text(table))
    print("wrote %s" % os.path.relpath(DOC_OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
