from __future__ import annotations

import argparse
import csv
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recomp"))
sys.path.insert(0, os.path.join(ROOT, "tools", "readability"))
sys.path.insert(0, HERE)

import export_inputs
import export_labels
import function_bounds
import gate
import name
import romfile

ROM_BASE = 0x08000000
ASM_INDEX = os.path.join("docs", "ASM_INDEX.csv")
LEDGER = os.path.join("work", "ledger.csv")
NAMING = os.path.join("docs", "NAMING_LEDGER.csv")
RECOMP = os.path.join("docs", "research", "RECOMP_NAMES.csv")
RETIRED = os.path.join("docs", "NAMING_RETIRED.csv")
HEADER = "address,kind,symbol,file"
INCLUDE = re.compile(r"^(\s*INCLUDE\s+)(\S+)(\s*)$")
SLICE = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted")
RUN = re.compile(r"_([0-9a-fA-F]{1,8})_([0-9a-fA-F]{1,8})\.bin$")
LINE_LABEL = re.compile(r"^\|([^|]+)\|\s*$")
EXPORT_LINE = re.compile(r"^(\s*EXPORT\s+)\|([^|]+)\|\s*$")
FUNCTION_FILE = re.compile(r"^asm/(?:sub|loc|dat|unk|g)_([0-9A-Fa-f]{8})\.s$")
WIDTHS = {"DCW": 2, "DCB": 1, "DCD": 4}
QUIET = ("EXPORT", "IMPORT", "INCLUDE", "AREA", "EQU", "GET", "PRESERVE8",
         "CODE16", "CODE32")
TOPS = ("buu.s", "rest_of_the_game.s")
BRANCHES = ("b", "bl", "beq", "bne", "bcs", "bcc", "bmi", "bpl", "bvs", "bvc", "bhi", "bls",
            "bge", "blt", "bgt", "ble", "bal", "cbz", "cbnz")


def read(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as handle:
        return handle.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def inside(root, relative):
    return os.path.join(root, *relative.split("/"))


def leaves(root=ROOT):
    order, seen = [], set()

    def expand(leaf):
        if leaf in seen:
            return
        seen.add(leaf)
        path = os.path.join(root, "asm", leaf)
        if not os.path.exists(path):
            order.append(leaf)
            return
        for line in read(path).split("\n"):
            found = INCLUDE.match(line)
            if found is not None:
                child = os.path.basename(found.group(2))
                if not child.endswith(".inc"):
                    expand(child)
        order.append(leaf)

    for top in TOPS:
        expand(top)
    return order


def include_site(root, leaf):
    for parent in TOPS:
        path = os.path.join(root, "asm", parent)
        for number, line in enumerate(read(path).split("\n"), 1):
            found = INCLUDE.match(line)
            if found is not None and os.path.basename(found.group(2)) == leaf:
                return parent, number
    return None


def section_start(root, leaf):
    site = include_site(root, leaf)
    if site is None:
        return False
    parent, number = site
    lines = read(os.path.join(root, "asm", parent)).split("\n")
    index = number - 2
    while index >= 0 and not lines[index].split(";")[0].strip():
        index -= 1
    return index < 0 or INCLUDE.match(lines[index]) is None


def mode_before(lines, number):
    mode = "thumb"
    for line in lines[:number]:
        state = line.split(";")[0].strip()
        if state.startswith("CODE32"):
            mode = "arm"
        elif state.startswith("CODE16"):
            mode = "thumb"
    return mode


def step(state, at, mode, rom):
    found = re.match(r"^(DCW|DCB|DCD)\s+(.+)$", state)
    if found is not None:
        return at + WIDTHS[found.group(1)] * len(found.group(2).split(",")), mode
    found = re.match(r"^SPACE\s+(\S+)$", state)
    if found is not None:
        return at + int(found.group(1), 0), mode
    found = SLICE.search(state)
    if found is not None:
        return ROM_BASE + int(found.group(2), 16), mode
    found = RUN.search(state)
    if found is not None:
        return ROM_BASE + int(found.group(2), 16), mode
    offset = at - ROM_BASE
    one = next(iter(function_bounds.ENGINES[mode].disasm(bytes(rom[offset:offset + 4]),
                                                        at, count=1)), None)
    if one is None:
        raise SystemExit("nothing decodes at 0x%08X in the %s state" % (at, mode))
    return at + one.size, mode


def cut(lines, rom, address, stop, known):
    anchor = None
    for number, line in enumerate(lines):
        found = LINE_LABEL.match(line.strip())
        if found is None:
            continue
        digits = function_bounds.ADDRESS_FORM.match(found.group(1))
        where = int(digits.group(1), 16) if digits is not None else known.get(found.group(1))
        if where is not None and where <= address:
            anchor = (number, where)
    if anchor is None:
        return None
    label, start, end, inner, slices = None, None, None, [], []
    at = anchor[1]
    mode = mode_before(lines, anchor[0])
    for number in range(anchor[0], len(lines)):
        state = lines[number].split(";")[0].strip()
        if at == stop:
            end = number
            break
        if not state:
            continue
        found = LINE_LABEL.match(state)
        if found is not None:
            digits = function_bounds.ADDRESS_FORM.match(found.group(1))
            where = int(digits.group(1), 16) if digits is not None else known.get(found.group(1))
            if where is not None:
                if where == address:
                    label = number
                elif address < where < stop:
                    inner.append((where, number, found.group(1)))
            continue
        if state.startswith(QUIET):
            continue
        if at > stop:
            return None
        if start is None and at == address:
            start = number
        before = at
        at, mode = step(state, at, mode, rom)
        if address <= before < stop and SLICE.search(state):
            slices.append((before, at, state))
    if end is None or start is None:
        return None
    return label, start, end, inner, slices


def halfwords(rom, address, stop):
    if (stop - address) % 2 or address % 2:
        raise SystemExit("the run 0x%08X..0x%08X is not halfword aligned" % (address, stop))
    return ["\tDCW      0x%04x" % int.from_bytes(rom[at - ROM_BASE:at - ROM_BASE + 2], "little")
            for at in range(address, stop, 2)]


def data_lines(rom, address, stop, inner, held, slices):
    out = list(held) if held else ["|dat_%08X|" % address]
    events = [(where, where, "|%s|" % text) for where, _number, text in inner]
    events += [(start, finish, "\t" + text) for start, finish, text in slices]
    at = address
    for start, finish, text in sorted(events):
        out += halfwords(rom, at, start)
        out.append(text)
        at = finish
    out += halfwords(rom, at, stop)
    return out


def entry_name(lines, end, symbol, stop):
    if symbol and function_bounds.ADDRESS_FORM.match(symbol) is None:
        return symbol
    found = LINE_LABEL.match(lines[end].strip()) if end < len(lines) else None
    if found is not None and function_bounds.ADDRESS_FORM.match(found.group(1)) is not None:
        if int(found.group(1)[-8:], 16) == stop:
            return found.group(1)
    return "sub_%08X" % stop


def first_byte(lines, label, start):
    head = lines[:label] if label is not None else lines[:start]
    return not any(line.split(";")[0].strip() and
                   not line.split(";")[0].strip().startswith(QUIET) for line in head)


def referenced(root, symbol):
    pattern = re.compile(r"\b%s\b" % re.escape(symbol), re.I)
    for folder in ("src", "include"):
        base = os.path.join(root, folder)
        if not os.path.isdir(base):
            continue
        for name in os.listdir(base):
            path = os.path.join(base, name)
            if os.path.isfile(path) and pattern.search(read(path)):
                return True
    return False


def references(root, old, data_label):
    for leaf in leaves(root):
        path = os.path.join(root, "asm", leaf)
        if not os.path.exists(path):
            continue
        lines = read(path).split("\n")
        changed = False
        for number, line in enumerate(lines):
            if EXPORT_LINE.match(line) is not None or LINE_LABEL.match(line.strip()):
                continue
            if "|%s|" % old in line:
                lines[number] = line.replace("|%s|" % old, "|%s|" % data_label)
                changed = True
        if changed:
            write(path, "\n".join(lines))


def index_rows(root=ROOT):
    return list(csv.DictReader(io.StringIO(read(inside(root, ASM_INDEX)))))


def index_text(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(HEADER.split(","))
    for row in sorted(rows, key=lambda item: int(item["address"], 16)):
        writer.writerow([row["address"], row["kind"], row["symbol"], row["file"]])
    return buffer.getvalue()


def ledger_shift(rows, pairs):
    out = [list(row) for row in rows]
    drop = set()
    for address, stop in sorted(pairs):
        start, ends = address - ROM_BASE, stop - ROM_BASE
        crossing = []
        for number, row in enumerate(out):
            if not start <= row[0] < ends:
                continue
            if row[0] + row[1] <= ends:
                drop.add(number)
                continue
            crossing.append(number)
        if len(crossing) > 1:
            raise SystemExit("two rows cross 0x%08X, so the prefix has no single owner" % stop)
        for number in crossing:
            row = out[number]
            row[1] -= ends - row[0]
            row[7] -= ends - row[0]
            row[0] = ends
            if row[1] <= 0 or row[7] < 0:
                raise SystemExit("the row at 0x%08X has nothing left after the prefix" % address)
    return [tuple(row) for number, row in enumerate(out) if number not in drop]


def retired_address(root, address, stop):
    path = inside(root, RETIRED)
    if not os.path.exists(path):
        return
    rows = list(csv.DictReader(io.StringIO(read(path))))
    changed = 0
    for row in rows:
        if int(row["address"], 16) == address:
            row["address"] = "0x%08X" % stop
            changed += 1
    if not changed:
        return
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write(path, buffer.getvalue())


def named_address(path, address, stop, symbol, upper):
    rows = list(csv.DictReader(io.StringIO(read(path))))
    fields = list(rows[0].keys())
    changed = 0
    for row in rows:
        if int(row["address"], 16) == address and symbol in (row.get("new"), row.get("name")):
            row["address"] = ("0x%08X" if upper else "0x%08x") % stop
            changed += 1
    if not changed:
        raise SystemExit("%s carries no row for 0x%08X" % (path, address))
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write(path, buffer.getvalue())


def renamed(root, path, target, rows, leaf, removed, address):
    if target == path:
        return path
    if os.path.exists(inside(root, target)):
        raise SystemExit("%s already exists" % target)
    for other in rows:
        if other["file"] == path and int(other["address"], 16) != address:
            other["file"] = target
    parent, number = include_site(root, leaf)
    parent_lines = read(os.path.join(root, "asm", parent)).split("\n")
    parent_lines[number - 1] = INCLUDE.sub(
        lambda one: one.group(1) + os.path.basename(target) + one.group(3),
        parent_lines[number - 1])
    write(os.path.join(root, "asm", parent), "\n".join(parent_lines))
    os.remove(inside(root, path))
    removed.append(path)
    return target


def relabel(root, path, head, body):
    write(inside(root, path), "\n".join(head + body))


def removed_from_index(root, removed):
    if not removed or not os.path.exists(os.path.join(root, ".git")):
        return
    subprocess.run(["git", "add", "--"] + removed, cwd=root, check=True)


def move(root, rom, pairs):
    order = leaves(root)
    rows = index_rows(root)
    known = function_bounds.lints.label_addresses()
    proven = proven_entries(root)
    ready, skipped = [], []
    for address, stop in sorted(pairs):
        stop = claimed(address, stop, proven)
        if address in proven:
            skipped.append((address, stop))
            continue
        row = next((item for item in rows if int(item["address"], 16) == address), None)
        if row is None:
            raise SystemExit("%s carries no row for 0x%08X" % (ASM_INDEX, address))
        text = read(inside(root, row["file"]))
        if row["symbol"] and referenced(root, row["symbol"]):
            skipped.append((address, stop))
            continue
        if cut(text.split("\n"), rom, address, stop, known) is None:
            skipped.append((address, stop))
            continue
        ready.append((address, stop))
    ledger = ledger_shift(gate.ledger_rows(inside(root, LEDGER)), ready)
    moves, removed = [], []
    for address, stop in ready:
        row = next(item for item in rows if int(item["address"], 16) == address)
        path = row["file"]
        leaf = os.path.basename(path)
        lines = read(inside(root, path)).split("\n")
        found_cut = cut(lines, rom, address, stop, known)
        if found_cut is None:
            skipped.append((address, stop))
            continue
        label, start, end, inner, slices = found_cut
        new = entry_name(lines, end, row["symbol"], stop)
        held = [lines[number].strip() for number in range(label, start)
                if LINE_LABEL.match(lines[number].strip())] if label is not None else []
        held = [line for line in held if LINE_LABEL.match(line).group(1) != new]
        body = data_lines(rom, address, stop, inner, held, slices)
        head = lines[:label] if label is not None else lines[:start]
        tail = lines[end:]
        insert = [] if tail and tail[0].strip() == "|%s|" % new else ["|%s|" % new]
        found = FUNCTION_FILE.match(path)
        target = "asm/%s.s" % new
        at = order.index(leaf) if leaf in order else None
        if at is None:
            raise SystemExit("%s is in no include list" % leaf)
        first = first_byte(lines, label, start)
        if first and not section_start(root, leaf):
            if at == 0:
                raise SystemExit("%s has no preceding file" % leaf)
            before = os.path.join(root, "asm", order[at - 1])
            if not os.path.exists(before):
                raise SystemExit("%s is generated, so it cannot carry the data run" % before)
            text = read(before)
            if "INCLUDE" in text:
                raise SystemExit("%s includes another file, so its end is not its extent" % before)
            write(before, text.rstrip("\n") + "\n" + "\n".join(body) + "\n")
            if found is not None:
                target = renamed(root, path, target, rows, leaf, removed, address)
            else:
                target = path
            relabel(root, target, head, insert + tail)
            order[at] = os.path.basename(target)
        elif found is not None and not first:
            write(inside(root, path), "\n".join(head + body))
            if os.path.exists(inside(root, target)):
                raise SystemExit("%s already exists" % target)
            relabel(root, target, [], insert + tail)
            order.insert(at + 1, os.path.basename(target))
            for other in rows:
                if other["file"] == path and int(other["address"], 16) >= stop:
                    other["file"] = target
            parent, number = include_site(root, leaf)
            parent_lines = read(os.path.join(root, "asm", parent)).split("\n")
            parent_lines.insert(number, "\tINCLUDE %s" % os.path.basename(target))
            write(os.path.join(root, "asm", parent), "\n".join(parent_lines))
        else:
            text = "\n".join(head + body + insert + tail)
            if found is not None:
                target = renamed(root, path, target, rows, leaf, removed, address)
                write(inside(root, target), text)
            else:
                target = path
                write(inside(root, path), text)
            order[at] = os.path.basename(target)
        row["address"] = "0x%08X" % stop
        row["symbol"] = new
        row["kind"] = "start"
        row["file"] = target
        if function_bounds.ADDRESS_FORM.match(new) is None:
            references(root, new, "dat_%08X" % address)
            named_address(os.path.join(root, NAMING), address, stop, new, True)
            named_address(os.path.join(root, RECOMP), address, stop, new, False)
        retired_address(root, address, stop)
        moves.append((address, stop, new, target, row["symbol"]))
    write(inside(root, ASM_INDEX), index_text(rows))
    gate.write_ledger(ledger, inside(root, LEDGER))
    removed_from_index(root, removed)
    return moves, skipped


def place_export(root, address, new):
    for leaf in leaves(root):
        path = os.path.join(root, "asm", leaf)
        if not os.path.exists(path):
            continue
        lines = read(path).split("\n")
        for number, line in enumerate(lines):
            found = EXPORT_LINE.match(line)
            if found is None:
                continue
            if found.group(2).lower() == new.lower():
                return
            digits = function_bounds.ADDRESS_FORM.match(found.group(2))
            if digits is None or int(digits.group(1), 16) != address:
                continue
            lines[number] = "%s|%s|" % (found.group(1), new)
            write(path, "\n".join(lines))
            return
    for leaf in leaves(root):
        path = os.path.join(root, "asm", leaf)
        if not os.path.exists(path):
            continue
        lines = read(path).split("\n")
        for number, line in enumerate(lines):
            if line.strip() == "|%s|" % new:
                lines.insert(number + 1, "\tEXPORT |%s|" % new)
                write(path, "\n".join(lines))
                return
    raise SystemExit("%s carries no label, so no export can name it" % new)


def pairs_from_allow(root=ROOT):
    rows = list(csv.DictReader(io.StringIO(read(inside(root, function_bounds.ALLOW)))))
    return [(int(row["address"], 16), int(row["entry"], 16))
            for row in rows if row["reason"] == "prefix"]


def proven_entries(root=ROOT):
    if not os.path.exists(inside(root, export_inputs.RUNTIME)):
        return set()
    return {address for address, _mode in export_inputs.runtime_labels(root)}


def claimed(address, stop, proven):
    inside = [entry for entry in proven if address < entry < stop]
    return min(inside) if inside else stop


def statement_at(root, rom, path, address):
    rows = [row for row in index_rows(root) if row["file"] == path]
    if not rows:
        raise SystemExit("%s is in no index row, so its start address is unknown" % path)
    at = min(int(row["address"], 16) for row in rows)
    lines = read(inside(root, path)).split("\n")
    mode = "thumb"
    for number, line in enumerate(lines):
        state = line.split(";")[0].strip()
        if state.startswith("CODE32"):
            mode = "arm"
            continue
        if state.startswith("CODE16"):
            mode = "thumb"
            continue
        if not state or state.startswith(QUIET) or LINE_LABEL.match(state):
            continue
        if at == address:
            return lines, number, mode
        at, mode = step(state, at, mode, rom)
        if at > address:
            return None
    return None


def reclaim_one(root, rom, start, entry, proven):
    if entry >= start:
        raise SystemExit("0x%08X does not stand before 0x%08X" % (entry, start))
    if entry not in proven:
        raise SystemExit("0x%08X is not a runtime-proven entry" % entry)
    rows = index_rows(root)
    found = [row for row in rows if int(row["address"], 16) == start]
    if len(found) != 1 or found[0]["symbol"] != "sub_%08X" % start:
        raise SystemExit("%s carries no single house row for 0x%08X" % (ASM_INDEX, start))
    row = found[0]
    path = row["file"]
    leaf = os.path.basename(path)
    if [other for other in rows if other["file"] == path and int(other["address"], 16) != start]:
        raise SystemExit("%s carries more than the one start in %s" % (ASM_INDEX, path))
    order = leaves(root)
    at = order.index(leaf) if leaf in order else None
    if at is None or at == 0:
        raise SystemExit("%s has no file before it whose tail can shrink" % leaf)
    before = "asm/%s" % order[at - 1]
    if "INCLUDE" in read(inside(root, before)):
        raise SystemExit("%s includes another file, so its end is not its extent" % before)
    walked = statement_at(root, rom, before, entry)
    if walked is None:
        raise SystemExit("%s carries no statement of its own at 0x%08X" % (before, entry))
    lines, number, mode = walked
    value = int.from_bytes(rom[entry - ROM_BASE:entry - ROM_BASE + 2], "little")
    carried = re.match(r"^DCW\s+0x([0-9a-fA-F]+)$", lines[number].strip())
    if carried is None or int(carried.group(1), 16) != value:
        raise SystemExit("%s does not carry 0x%08X as one DCW halfword" % (before, entry))
    one = next(iter(function_bounds.ENGINES[mode].disasm(
        bytes(rom[entry - ROM_BASE:entry - ROM_BASE + 4]), entry, count=1)), None)
    if one is None or one.size != 2 or one.mnemonic in BRANCHES:
        raise SystemExit("0x%08X does not decode to one plain halfword instruction" % entry)
    for leaf_name in leaves(root):
        other_path = inside(root, os.path.join("asm", leaf_name))
        if not os.path.exists(other_path):
            continue
        for line in read(other_path).split("\n"):
            if "|sub_%08X|" % start not in line:
                continue
            if leaf_name == leaf or EXPORT_LINE.match(line) is not None:
                continue
            raise SystemExit("%s names 0x%08X outside the file it starts" % (leaf_name, start))
    write(inside(root, before), "\n".join(lines[:number] + lines[number + 1:]))
    body = read(inside(root, path)).split("\n")
    label = "|sub_%08X|" % start
    if label not in [line.strip() for line in body]:
        raise SystemExit("%s carries no %s" % (path, label))
    number = [line.strip() for line in body].index(label)
    body[number] = "|sub_%08X|" % entry
    body.insert(number + 1, "\t%-9s%s" % (one.mnemonic.upper(), one.op_str))
    removed = []
    target = "asm/sub_%08X.s" % entry
    renamed(root, path, target, rows, leaf, removed, start)
    write(inside(root, target), "\n".join(body))
    row["address"] = "0x%08X" % entry
    row["symbol"] = "sub_%08X" % entry
    row["file"] = target
    write(inside(root, ASM_INDEX), index_text(rows))
    ledger = [list(item) for item in gate.ledger_rows(inside(root, LEDGER))]
    hit = [number for number, item in enumerate(ledger) if item[0] == start - ROM_BASE]
    if len(hit) != 1 or ledger[hit[0]][2] not in export_inputs.CODE:
        raise SystemExit("%s carries no single code row at 0x%08X" % (LEDGER, start))
    for other in ledger:
        if other[0] != start - ROM_BASE and entry - ROM_BASE <= other[0] < start - ROM_BASE:
            raise SystemExit("%s carries another row inside 0x%08X..0x%08X"
                             % (LEDGER, entry, start))
    ledger[hit[0]][0] = entry - ROM_BASE
    ledger[hit[0]][1] += start - entry
    ledger[hit[0]][7] += start - entry
    gate.write_ledger([tuple(item) for item in ledger], inside(root, LEDGER))
    removed_from_index(root, removed)
    return target


def reclaim(root, rom, pairs):
    proven = proven_entries(root)
    return [(reclaim_one(root, rom, start, entry, proven), start, entry)
            for start, entry in sorted(pairs)]


def regenerate(rom):
    found, flagged = function_bounds.save(rom)
    starts = set(found["starts"])
    rows = [row for row in index_rows() if int(row["address"], 16) in starts]
    write(inside(ROOT, ASM_INDEX), index_text(rows))
    tally = function_bounds.counts(found)
    export_inputs.main(["--write"])
    export_labels.main(["--write"])
    live, total, retired = name.sync_counts()
    return tally, flagged, live, total, retired


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Move a census start to its real entry and update every surface that names it.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--pair", action="append", default=[],
                        help="an address:entry pair to move instead of the permitted prefixes")
    parser.add_argument("--reclaim", action="append", default=[],
                        help="a start:entry pair whose row begins after the runtime-proven entry")
    args = parser.parse_args(argv)
    if not os.path.exists(args.rom):
        print("the move needs the retail image at %s" % args.rom)
        return 1
    rom = romfile.read_rom(args.rom, function_bounds.ROM_SHA256)
    reclaimed = [tuple(int(part, 16) for part in item.split(":")) for item in args.reclaim]
    if reclaimed:
        done = reclaim(ROOT, rom, reclaimed)
        for target, start, entry in done:
            place_export(ROOT, start, os.path.basename(target)[: -len(".s")])
        tally, flagged, live, total, retired = regenerate(rom)
        print("reclaimed=%d starts=%d flagged=%d live=%d total=%d retired=%d"
              % (len(done), tally["starts"], flagged, live, total, retired))
        for target, start, entry in done:
            print("0x%08X -> 0x%08X %s" % (start, entry, target))
        return 0
    pairs = [tuple(int(part, 16) for part in item.split(":")) for item in args.pair] \
        or pairs_from_allow()
    for address, stop in pairs:
        if stop <= address:
            raise SystemExit("0x%08X does not stand after 0x%08X" % (stop, address))
    moves, skipped = move(ROOT, rom, pairs)
    for address, _stop, _new, _path, _symbol in moves:
        place_export(ROOT, address, _new)
    tally, flagged, live, total, retired = regenerate(rom)
    print("moved=%d kept=%d starts=%d flagged=%d live=%d total=%d retired=%d"
          % (len(moves), len(skipped), tally["starts"], flagged, live, total, retired))
    for address, stop, new, path, _symbol in moves[:10]:
        print("0x%08X -> 0x%08X %s %s" % (address, stop, new, path))
    for address, stop in skipped:
        print("kept 0x%08X -> 0x%08X, an earlier move already carries the entry, or the prefix "
              "ends in a file the start does not begin" % (address, stop))
    return 0


if __name__ == "__main__":
    sys.exit(main())
