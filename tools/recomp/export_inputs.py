from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
from bisect import bisect_right

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate

ROM = os.path.join(ROOT, "baserom.gba")
SHA1 = os.path.join(ROOT, "baserom.sha1")
OUT = os.path.join(ROOT, "docs", "research", "RECOMP_INPUTS.toml")
RUNTIME = os.path.join("docs", "research", "RUNTIME_LABELS.csv")
CRT0 = os.path.join("asm", "crt0.s")
IWRAM = os.path.join("asm", "iwram.s")
HEADER = os.path.join("asm", "rom_header.s")
ENTRY_PC = 0x08000000
CODE = ("thumb", "arm")
LABEL = re.compile(r"^EXPORT\s+\|(sub_[0-9a-fA-F]{8})\|$")
NAMED = re.compile(r"^EXPORT\s+\|([^|]+)\|$")
NAMES = os.path.join("docs", "NAMING_LEDGER.csv")
CENSUS = os.path.join("docs", "research", "FUNCTION_BOUNDS.csv")
DCD = re.compile(r"^(\w+)\s+DCD\s+0x([0-9a-fA-F]+)$")
SPACE = re.compile(r"^SPACE\s+0x([0-9a-fA-F]+)$")
COUNT_SHIFT = re.compile(r"^movs\s+r1,\s*r1,\s+lsr\s+#2$", re.I)
CONTROL = re.compile(r"^orr\s+r1,\s*r1,\s+#0x84,\s*8$", re.I)
BRANCH = re.compile(r"^B\s+Init$", re.I)
VENEER = bytes.fromhex("7847c04604f01fe5")
STEP_LIMIT = 4000
NULL_BLOCK = 0x10000
THUMB_UNDEFINED = ((0x4780, 0x47FF), (0xB100, 0xB3FF), (0xB600, 0xBBFF),
                   (0xBE00, 0xBFFF), (0xDE00, 0xDEFF), (0xE800, 0xEFFF))


def code_rows(root=ROOT):
    path = os.path.join(root, "work", "ledger.csv")
    rows = [(off, length, isa) for off, length, isa, _region, _source, _kind, _evidence, _insn
            in gate.ledger_rows(path) if isa in CODE]
    rows.sort()
    for before, after in zip(rows, rows[1:]):
        if before[0] + before[1] > after[0]:
            raise SystemExit("%s holds two overlapping code rows at 0x%x and 0x%x"
                             % (path, before[0], after[0]))
    return rows


def promoted(root=ROOT):
    path = os.path.join(root, *NAMES.split("/"))
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as handle:
        return {(row["new"]): int(row["address"], 16) - ENTRY_PC
                for row in csv.DictReader(handle) if row.get("new") and row.get("address")}


def labels(root=ROOT):
    out = {}
    folder = os.path.join(root, "asm")
    named = promoted(root)
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".s"):
            continue
        state = None
        for line in open(os.path.join(folder, name), encoding="ascii", errors="replace"):
            text = line.strip()
            if text.startswith("CODE16"):
                state = "thumb"
                continue
            if text.startswith("CODE32"):
                state = "arm"
                continue
            found = LABEL.match(text)
            if found:
                out[int(found.group(1)[-8:], 16) - ENTRY_PC] = (found.group(1), state)
                continue
            found = NAMED.match(text)
            if found and found.group(1) in named:
                out[named[found.group(1)]] = (found.group(1), state)
    return out


def mode_of(offset, rows, starts, names):
    index = bisect_right(starts, offset) - 1
    if index >= 0:
        start, length, mode = rows[index]
        if start <= offset < start + length:
            return mode
    return names[offset][1] or ""


def functions(rows, names):
    return [(off, length, mode, names[off][0] if off in names else "")
            for off, length, mode in rows]


def entries(rows, names):
    starts = {row[0] for row in rows}
    order = [row[0] for row in rows]
    return [(off, mode_of(off, rows, order, names)) for off in sorted(names)
            if off not in starts]


def census_entries(root=ROOT):
    path = os.path.join(root, *CENSUS.split("/"))
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        return sorted((int(row["address"], 16) - ENTRY_PC, row["kind"])
                      for row in csv.DictReader(handle))


def runtime_labels(root=ROOT):
    out = []
    for line in open(os.path.join(root, RUNTIME), encoding="ascii"):
        text = line.strip()
        if text and not text.startswith("address"):
            addr, mode = text.split(",")
            out.append((int(addr, 16), mode))
    return out


def runtime_entries(bounds, copy, labels):
    return [(addr, mode) for addr, mode in labels
            if bounds.get(addr - ENTRY_PC, copy.get(addr)) == mode]


def veneer_rows(rom):
    return [(position, 8, "thumb") for position in range(0, len(rom) - 8, 2)
            if rom[position:position + 8] == VENEER]


def copy_bounds(rom, copy_rows):
    out = {}
    for runtime_start, source_start, size in copy_rows:
        found, _starts = walk(rom, [(source_start - ENTRY_PC, size, "arm")])
        for off, mode in found.items():
            out[runtime_start + off - (source_start - ENTRY_PC)] = mode
    return out


def copies(root=ROOT):
    values = {}
    shifts = controls = 0
    for line in open(os.path.join(root, CRT0), encoding="ascii", errors="replace"):
        text = line.strip()
        found = DCD.match(text)
        if found:
            values[found.group(1)] = int(found.group(2), 16)
        shifts += 1 if COUNT_SHIFT.match(text) else 0
        controls += 1 if CONTROL.match(text) else 0
    blocks = []
    for line in open(os.path.join(root, IWRAM), encoding="ascii", errors="replace"):
        found = SPACE.match(line.strip())
        if found:
            blocks.append(int(found.group(1), 16))
    if shifts < 1 or controls < 1:
        raise SystemExit("%s does not carry the DMA copy whose size this tool reads" % CRT0)
    size = (values["hardware_conf_4"] >> 2) * 4
    if size != blocks[0]:
        raise SystemExit("%s copies 0x%x B to 0x%08X but %s reserves 0x%x B there"
                         % (CRT0, size, values["hardware_conf_3"], IWRAM, blocks[0]))
    if sum(blocks) != 0x8000:
        raise SystemExit("%s blocks total 0x%x B, not the 0x8000 B of IWRAM"
                         % (IWRAM, sum(blocks)))
    return [(values["hardware_conf_3"], values["hardware_conf_2"], size)], blocks


def entry_address(root=ROOT):
    for line in open(os.path.join(root, HEADER), encoding="ascii", errors="replace"):
        if BRANCH.match(line.strip()):
            return ENTRY_PC
    raise SystemExit("%s carries no reset branch, so the entry pc is not derivable" % HEADER)


def identity(path=ROM, sha1_path=SHA1):
    if not os.path.exists(path):
        raise SystemExit("no image at %s, so the identity block cannot be derived" % path)
    data = open(path, "rb").read()
    digest = hashlib.sha1(data).hexdigest()
    expected = open(sha1_path, encoding="ascii").read().strip()
    if digest != expected:
        raise SystemExit("%s has sha1 %s, not the %s of %s"
                         % (path, digest, expected, sha1_path))
    return digest, hashlib.md5(data).hexdigest()


def halfwords(rom, at, count):
    return [half_word(rom, at + 2 * index) for index in range(count)]


def half_word(rom, at):
    return rom[at] | rom[at + 1] << 8


def word_at(rom, at):
    return int.from_bytes(rom[at:at + 4], "little")


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def thumb_size(rom, at):
    if at + 2 > len(rom):
        return None
    half = half_word(rom, at)
    if half >= 0xF000:
        if half >= 0xF800 or at + 4 > len(rom):
            return None
        return 4 if half_word(rom, at + 2) >= 0xF800 else None
    for low, high in THUMB_UNDEFINED:
        if low <= half <= high:
            return None
    return 2


def thumb_branch(at, half):
    return at + 4 + signed(half & 0x7FF, 11) * 2


def thumb_condition(at, half):
    return at + 4 + signed(half & 0xFF, 8) * 2


def thumb_call(rom, at):
    high = half_word(rom, at)
    low = half_word(rom, at + 2)
    return at + 4 + signed(((high & 0x7FF) << 11) | (low & 0x7FF), 22) * 2


def arm_branch(at, word):
    return at + 8 + signed(word & 0xFFFFFF, 24) * 4


def flow(rom, at, mode, bounds=None):
    queue = [(at, mode)]
    seen = set()
    returned = False
    branches = 0
    end = at
    steps = 0
    while queue and steps < STEP_LIMIT:
        at, mode = queue.pop()
        if (at, mode) in seen:
            continue
        seen.add((at, mode))
        done = False
        while not done and steps < STEP_LIMIT:
            steps += 1
            if not 0 <= at < len(rom) or (bounds is not None and bounds.get(at) != mode):
                return False, 0, None
            if mode == "thumb":
                size = thumb_size(rom, at)
                if size is None:
                    return False, 0, None
                half = half_word(rom, at)
                end = max(end, at + size)
                if size == 4:
                    at += 4
                elif (half & 0xFF80) == 0x4700:
                    returned = returned or half == 0x4770
                    done = True
                elif (half & 0xFF00) == 0xBD00:
                    returned = True
                    done = True
                elif (half & 0xFF00) == 0xDF00:
                    done = True
                elif (half & 0xF800) == 0xE000:
                    queue.append((thumb_branch(at, half), "thumb"))
                    done = True
                elif (half & 0xF000) == 0xD000:
                    branches += 1
                    queue.append((thumb_condition(at, half), "thumb"))
                    at += 2
                else:
                    at += 2
            else:
                if at + 4 > len(rom):
                    return False, 0, None
                word = word_at(rom, at)
                end = max(end, at + 4)
                if word >> 28 == 0x0F:
                    return False, 0, None
                if word in (0xE12FFF1E, 0xE1A0F00E) or (word & 0x0FFF8000) == 0x08BD8000:
                    returned = True
                    done = True
                elif (word & 0x0FFFFFF0) == 0x012FFF10:
                    done = True
                elif (word & 0x0F000000) == 0x0B000000:
                    done = True
                elif (word & 0x0F000000) == 0x0A000000:
                    queue.append((arm_branch(at, word), "arm"))
                    if word >> 28 == 0x0E:
                        returned = True
                        done = True
                    else:
                        branches += 1
                        at += 4
                else:
                    at += 4
        if not done and steps >= STEP_LIMIT:
            return False, 0, None
    return returned, branches, end


def covered(addr, mode, funcs, copy_rows):
    for start, length, row_mode in funcs:
        if ENTRY_PC + start <= addr < ENTRY_PC + start + length and row_mode == mode:
            return True
    return any(runtime <= addr < runtime + size for runtime, _source, size in copy_rows)


def covering(rom, entries, rows, copy_rows):
    funcs = [(off, length, mode) for off, length, mode in rows]
    extra = []
    for addr, mode in entries:
        if covered(addr, mode, funcs, copy_rows):
            continue
        if mode not in CODE:
            continue
        off = addr - ENTRY_PC
        end = extent(rom, off, mode)
        if end is None:
            continue
        ahead = [start for start, _length, _mode in funcs if start > off]
        stop = min(end, min(ahead)) if ahead else end
        if stop <= off:
            continue
        extra.append((off, stop - off, mode))
        funcs.append((off, stop - off, mode))
    return extra


def walk(rom, rows):
    engines = {"thumb": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB),
               "arm": capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)}
    bounds = {}
    starts = []
    held = {off for off, _length, _mode in rows}
    for off, length, mode in rows:
        pending = [(off, mode)]
        while pending:
            position, mode = pending.pop()
            step = 2 if mode == "thumb" else 4
            engine = engines[mode]
            previous = ""
            while position < off + length:
                placed = False
                for insn in engine.disasm(rom[position:off + length], ENTRY_PC + position):
                    bounds[position] = mode
                    if position > off and insn.mnemonic == "push" and "lr" in insn.op_str \
                            and previous in ("return", "padding"):
                        starts.append((position, mode))
                    returned = (insn.mnemonic == "bx" and insn.op_str == "lr") or \
                               (insn.mnemonic == "pop" and "pc" in insn.op_str)
                    previous = "padding" if insn.bytes == b"\x00\x00" else \
                               ("return" if returned else "")
                    switched = mode == "thumb" and insn.mnemonic == "bx" and insn.op_str == "pc"
                    placed = True
                    position = insn.address - ENTRY_PC + insn.size
                    if switched:
                        pending.append(((insn.address - ENTRY_PC + 4) & ~3, "arm"))
                    break
                if not placed:
                    bounds[position] = mode
                    previous = "padding" if rom[position:position + 2] == b"\x00\x00" else ""
                    position += step
            if position == off + length and position not in held \
                    and previous in ("return", "padding"):
                starts.append((position, mode))
    return bounds, starts


def probe(rom, bounds, at, mode):
    returned, branches, _end = flow(rom, at, mode, bounds)
    return returned, branches


def extent(rom, at, mode):
    returned, _branches, end = flow(rom, at, mode)
    return end if returned else None


def call_targets(rom, rows):
    out = set()
    for off, length, mode in rows:
        at = off
        end = off + length
        while at < end:
            if mode == "thumb":
                size = thumb_size(rom, at)
                if size is None:
                    at += 2
                    continue
                if size == 4:
                    out.add(thumb_call(rom, at))
                at += size
            else:
                if at + 4 <= end and word_at(rom, at) & 0x0F000000 == 0x0B000000:
                    out.add(arm_branch(at, word_at(rom, at)))
                at += 4
    return out


def table_targets(rom, rows, tables, copy_rows):
    out = set()
    for low, stride, count in tables:
        for index in range(count):
            at = low + stride * index
            out.add(at + int.from_bytes(rom[at:at + 4], "little", signed=True))
    out.update(addr - ENTRY_PC for addr, _mode in copy_entries(rom, rows, copy_rows))
    return out


def address_taken(rom, bounds, rows, tables, copy_rows):
    words = 0
    raw = {}
    for at in range(0, len(rom) - 3, 4):
        value = word_at(rom, at)
        if value & 0xFF000000 != 0x08000000:
            continue
        if value & 1:
            target, mode = (value & ~1) - ENTRY_PC, "thumb"
        elif value & 3 == 0:
            target, mode = value - ENTRY_PC, "arm"
        else:
            continue
        if bounds.get(target) != mode:
            continue
        raw[target] = mode
        words += 1
    calls = call_targets(rom, rows)
    proven = table_targets(rom, rows, tables, copy_rows)
    accepted = {}
    for target, mode in raw.items():
        returned, branches = probe(rom, bounds, target, mode)
        if not returned:
            continue
        if branches == 0 and target not in calls and target not in proven:
            continue
        accepted[target] = mode
    return words, raw, accepted


def permuted(rom):
    out = bytearray(rom)
    for base in range(0, len(out), NULL_BLOCK):
        block = bytes(rom[base:base + NULL_BLOCK])
        pairs = [block[index:index + 2] for index in range(0, len(block) - 1, 2)]
        out[base:base + len(block)] = b"".join(reversed(pairs))
    return bytes(out)


def measure(rom, rows, tables, copy_rows):
    bounds, _starts = walk(rom, rows)
    words, raw, accepted = address_taken(rom, bounds, rows, tables, copy_rows)
    shuffled = permuted(rom)
    null_words, null_raw, null_accepted = address_taken(
        shuffled, bounds, rows, jump_tables(shuffled), copy_rows)
    return {"aligned": len(rom) // 4, "candidate_words": words, "candidates": len(raw),
            "accepted": len(accepted), "null_candidate_words": null_words,
            "null_candidates": len(null_raw), "null_accepted": len(null_accepted)}


def jump_tables(rom):
    tables = []
    for position in range(0, len(rom) - 10, 2):
        if not (0x48 <= rom[position + 1] <= 0x4f and rom[position + 3] == 0x44
                and rom[position + 2] & 0x78 == 0x78):
            continue
        half = halfwords(rom, position, 5)
        if not (0x4800 <= half[0] <= 0x4fff and half[1] & 0xff78 == 0x4478):
            continue
        if not (0x4800 <= half[2] <= 0x4fff and half[3] & 0xff78 == 0x4478):
            continue
        if not (0x4280 <= half[4] <= 0x42ff or 0x4500 <= half[4] <= 0x45ff):
            continue
        loop = halfwords(rom, position + 10, 7)
        if not any(one & 0xf800 in (0x3000, 0x3800) and one & 0xff == 4 for one in loop):
            continue
        seeded = [int.from_bytes(rom[((position + 4 * (index + 1)) & ~3) + (half[2 * index] & 0xff) * 4:][:4],
                                 "little") for index in (0, 1)]
        start = seeded[0] + position + 6
        end = seeded[1] + position + 10
        low, high = min(start, end), max(start, end)
        count = (high - low) // 4
        if count < 1 or low < 0 or high > len(rom):
            continue
        targets = [low + 4 * index
                   + int.from_bytes(rom[low + 4 * index:low + 4 * index + 4], "little", signed=True)
                   for index in range(count)]
        if any(target % 2 == 0 or not 0 < target < len(rom) for target in targets):
            continue
        tables.append((low, 4, count))
    return sorted(tables)


def copy_entries(rom, rows, copy_rows):
    found = set()
    extents = {off: length for off, length, mode in rows}
    for runtime, source, size in copy_rows:
        code_size = extents.get(source - ENTRY_PC, 0)
        for position in range(0, len(rom) - 12, 2):
            if rom[position] == 0x78 and rom[position + 1] == 0x47 \
                    and rom[position:position + 8] == VENEER:
                target = int.from_bytes(rom[position + 8:position + 12], "little")
                if runtime <= target < runtime + size:
                    found.add((target, "arm"))
        for off, length, mode in rows:
            for position in range(off + ((4 - off % 4) % 4), off + length - 3, 4):
                target = int.from_bytes(rom[position:position + 4], "little")
                if runtime <= target < runtime + code_size:
                    found.add((target, "arm"))
    return sorted(found)


def extra_entries(rom, rows, tables, copy_rows, starts):
    out = [(ENTRY_PC + off, mode) for off, mode in starts]
    for low, stride, count in tables:
        for index in range(count):
            off = low + stride * index
            target = off + int.from_bytes(rom[off:off + 4], "little", signed=True)
            out.append((ENTRY_PC + target - 1, "thumb"))
    out.extend(copy_entries(rom, rows, copy_rows))
    return out


def render(root=ROOT, rom=ROM):
    rows = code_rows(root)
    names = labels(root)
    copy_rows, blocks = copies(root)
    sha1, md5 = identity(rom, os.path.join(root, "baserom.sha1"))
    image = open(rom, "rb").read()
    tables = jump_tables(image)
    bounds, starts = walk(image, rows + veneer_rows(image))
    row_starts = {ENTRY_PC + off for off, _length, _mode in rows}
    order = [row[0] for row in rows]
    found = [(ENTRY_PC + off, mode) for off, mode in entries(rows, names)]
    found += [(ENTRY_PC + off, mode_of(off, rows, order, names))
              for off, _kind in census_entries(root) if off not in names]
    found = [row for row in found if row[1] in CODE]
    found += extra_entries(image, rows, tables, copy_rows, starts)
    _words, _raw, accepted = address_taken(image, bounds, rows, tables, copy_rows)
    found += [(ENTRY_PC + target, mode) for target, mode in accepted.items()]
    runtime = runtime_entries(bounds, copy_bounds(image, copy_rows), runtime_labels(root))
    found += runtime
    runtime_set = set(runtime)
    extra = covering(image, sorted(found), rows, copy_rows)
    funcs = functions(rows, names) + [(off, length, mode, "") for off, length, mode in extra]
    funcs.sort()
    row_starts |= {ENTRY_PC + off for off, _length, _mode, _name in funcs}
    spans = [(off, length, mode) for off, length, mode, _name in funcs]
    ents = []
    seen = set()
    for addr, mode in sorted(found):
        if addr in row_starts or addr in seen:
            continue
        if (addr, mode) not in runtime_set and not covered(addr, mode, spans, copy_rows):
            continue
        seen.add(addr)
        ents.append((addr, mode))
    lines = ["[counts]",
             "functions = %d" % len(funcs),
             "code_bytes = %d" % sum(row[1] for row in funcs),
             "entries = %d" % len(ents),
             "jump_tables = %d" % len(tables),
             "code_copies = %d" % len(copy_rows),
             "iwram_bytes = %d" % sum(blocks),
             "",
             "[identity]",
             'sha1 = "%s"' % sha1,
             'md5 = "%s"' % md5,
             "",
             "[program]",
             "entry_pc = 0x%08x" % entry_address(root),
             ""]
    for runtime_start, source_start, size in copy_rows:
        lines += ["[[code_copy]]",
                  "runtime_start = 0x%08x" % runtime_start,
                  "source_start = 0x%08x" % source_start,
                  "size = 0x%x" % size,
                  ""]
    for addr, stride, count in tables:
        lines += ["[[jump_table]]",
                  "addr = 0x%08x" % (ENTRY_PC + addr),
                  "stride = %d" % stride,
                  "count = %d" % count,
                  'format = "entry-relative"',
                  'entries_mode = "thumb"',
                  ""]
    for off, length, mode, name in funcs:
        lines += ["[[code]]",
                  "addr = 0x%08x" % (ENTRY_PC + off),
                  'mode = "%s"' % mode,
                  "size = %d" % length]
        if name:
            lines.append('name = "%s"' % name)
        lines.append("")
    for addr, mode in ents:
        lines += ["[[entry]]",
                  "addr = 0x%08x" % addr,
                  'mode = "%s"' % mode]
        if (addr, mode) in runtime_set:
            lines.append('class = "runtime"')
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--measure", action="store_true")
    args = parser.parse_args(argv)
    if args.measure:
        image = open(ROM, "rb").read()
        rows = code_rows()
        copy_rows, _blocks = copies()
        found = measure(image, rows, jump_tables(image), copy_rows)
        print("aligned words = %d" % found["aligned"])
        print("candidate words = %d (%.4f %%)" % (
            found["candidate_words"], 100.0 * found["candidate_words"] / found["aligned"]))
        print("distinct candidates = %d" % found["candidates"])
        print("accepted = %d (%.4f %% of distinct candidates)" % (
            found["accepted"], 100.0 * found["accepted"] / found["candidates"]))
        print("null candidate words = %d, null accepted = %d" % (
            found["null_candidate_words"], found["null_accepted"]))
        print("null share of accepted = %.4f %%" % (
            100.0 * found["null_accepted"] / found["accepted"]))
        return 0
    text = render()
    for line in text.splitlines()[1:7]:
        print(line)
    if args.check:
        with open(OUT, encoding="ascii", newline="") as handle:
            if handle.read() != text:
                raise SystemExit("%s is not the export this tree derives"
                                 % os.path.relpath(OUT, ROOT))
        print("CHECK: the export matches the tree")
        return 0
    if args.write:
        with open(OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
        print("wrote %s (%d B)" % (os.path.relpath(OUT, ROOT), len(text)))
        return 0
    print("dry run: pass --write or --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
