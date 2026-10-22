"""Convert the Thumb bodies PATH-100-018 proves are code into Thumb source.

`thumb_bodies.closure()` names the rows and their walked code, their pools and their exits. This
module writes the source for those, and proves every body byte-exact in between: each body is
assembled in `CODE16` at its own retail address and compared with the retail bytes, and an
instruction the assembler cannot reproduce byte-exactly is emitted as its exact `DCW` word (a `DCD`
for the four-byte `BL`) with the assembler's own reason in the comment instead.

Two things are deliberately NOT proved by the per-body assembly, and the gate's rebuild is what
proves them (P-493): a branch or `ADR` whose target is a label the body does not define. armasm
refuses a branch to an absolute symbol outside its area, so the PROBE emits those as their exact
retail word and the FINAL text spells them.

A row the walk leaves partly unconverted is spliced exactly as `fill_promote` splices a fill run:
the covering `INCBIN` line becomes pieces that tile it, each retail gap keeping its own
`baserom.gba_0x.._0x....extracted` name (and its own `incbin.bat` line in `rebuild.cmd`).

    python tools/research/thumb_body_convert.py            # prove the emitters, write nothing
    python tools/research/thumb_body_convert.py --write    # rewrite asm/*.s in place
"""
from __future__ import annotations

import argparse
import bisect
import csv
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import arm_body_convert  # noqa: E402
import thumb_bodies  # noqa: E402
from tools.research import bios_block_scan  # noqa: E402

ROM_BASE = thumb_bodies.ROM_BASE
ROM = thumb_bodies.ROM
DEV = os.path.join(ROOT, "build", "thumb_bodies")
MANIFEST = os.path.join(DEV, "manifest.json")
LESSONS = os.path.join(DEV, "lessons.json")
MAP = os.path.join(ROOT, "build", "buu.map")
TOKEN_LINE = re.compile(r"^(\s*)INCBIN\s+(baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)"
                        r"\.extracted)\s*$")
CALL_LINE = re.compile(r"^\s*call tools\\incbin\.bat baserom\.gba 0x([0-9a-fA-F]+) "
                       r"0x([0-9a-fA-F]+)\s*$")
LABEL_DEF = re.compile(r"^\s*\|[A-Za-z_][A-Za-z0-9_]*\|\s*$")
ADDRESSED = re.compile(r"(?:sub|loc|unk|gap|dat|arm|inc)_(?:0x)?([0-9A-Fa-f]{8})")
STRIPPABLE = frozenset(("add", "sub", "mov", "lsl", "lsr", "asr", "and", "orr", "eor", "bic",
                        "mvn", "mul", "rsb", "adc", "sbc", "ror", "neg", "tst", "teq", "cmp",
                        "cmn"))
DIRECTIVES = frozenset(("EQU", "AREA", "CODE16", "CODE32", "END", "EXPORT", "IMPORT", "INCLUDE",
                        "INCBIN", "SPACE", "DCB", "DCW", "DCD", "ALIGN", "GET", "GBLA", "SETA",
                        "WHILE", "WEND"))
BRANCHES = frozenset(("b", "bl"))


def is_branch(mnemonic):
    return mnemonic in BRANCHES or (mnemonic.startswith("b") and mnemonic[1:] in
                                    thumb_bodies.CONDITIONS)
SHAPES = {}


def shape_of(mnemonic, operands):
    return "%s %s" % (mnemonic, re.sub(r"#-?0x[0-9a-fA-F]+|#\d+", "#N", operands))


def load_lessons():
    if os.path.exists(LESSONS):
        SHAPES.update(json.load(open(LESSONS)))


def save_lessons():
    if not os.path.isdir(DEV):
        os.makedirs(DEV)
    json.dump(SHAPES, open(LESSONS, "w"), indent=1, sort_keys=True)


def with_bang(operands):
    if operands.endswith("!") or "{" not in operands:
        return operands
    return re.sub(r"^(r\d+)\s*,\s*(\{)", r"\1!, \2", operands)


def plain_candidates(mnemonic, operands):
    low = mnemonic.lower()
    parts = [part.strip() for part in operands.split(",")]
    if low == "movs" and len(parts) == 2 and parts[0].startswith("r") and parts[1].startswith("r"):
        return ["LSL %s, %s, #0" % (parts[0], parts[1])]
    if low == "muls" and len(parts) == 3:
        return ["MUL %s, %s" % (parts[0], parts[1]), "MUL %s, %s" % (parts[2], parts[1])]
    if low == "rsbs" and len(parts) == 3 and parts[2] == "#0":
        return ["NEG %s, %s" % (parts[0], parts[1])]
    if low in ("ldm", "ldmia", "ldmfd"):
        return ["LDMIA %s" % with_bang(operands), "LDM %s" % with_bang(operands)]
    if low in ("stm", "stmia", "stmfd"):
        return ["STMIA %s" % with_bang(operands), "STM %s" % with_bang(operands)]
    if low == "svc":
        return ["SWI %s" % operands.lstrip("#"), "SVC %s" % operands.lstrip("#")]
    if low in ("add", "adds") and len(parts) == 3 and parts[1] == "sp" and parts[0] == parts[2]:
        return ["ADD %s, sp" % parts[0]]
    if is_branch(low):
        return []
    base = low[:-1] if low.endswith("s") and low[:-1] in STRIPPABLE else low
    if base.upper() in DIRECTIVES:
        return []
    return ["%s %s" % (base.upper(), operands)]


def literal_of(mnemonic, operands, offset):
    target = thumb_bodies.direct_target(mnemonic, operands)
    if target is not None:
        return target
    if mnemonic == "adr":
        found = thumb_bodies.IMMEDIATE.match(operands.split(",")[-1].strip())
        return None if not found else ((offset + ROM_BASE + 4) & ~3) + int(found.group(1), 0)
    found = thumb_bodies.PC_RELATIVE.search(operands)
    if found:
        return ((offset + ROM_BASE + 4) & ~3) + int(found.group(1), 0)
    return None


def referenced(body):
    out = set()
    for offset, (_size, mnemonic, operands) in body.code.items():
        if is_branch(mnemonic) or mnemonic == "adr":
            target = literal_of(mnemonic, operands, offset)
            if target is not None:
                out.add(target)
    return out


def items_of(body):
    items = []
    seen = set()
    for offset, (size, mnemonic, operands) in body.code.items():
        value = struct.unpack_from("<I" if size == 4 else "<H", ROM, offset)[0]
        items.append((offset, size, mnemonic, operands, value))
        seen.add(offset)
    for offset in body.pool:
        if offset in seen:
            continue
        items.append((offset, 4, "dcd", "pool word the body loads",
                      struct.unpack_from("<I", ROM, offset)[0]))
    return sorted(items)


def full_items(body):
    items = [(offset, size, mnemonic, operands, value, False)
             for offset, size, mnemonic, operands, value in items_of(body)]
    out = []
    cursor = body.row[0]
    for item in items:
        out.extend(gap_items(cursor, item[0]))
        out.append(item)
        cursor = item[0] + item[1]
    out.extend(gap_items(cursor, body.row[1]))
    return out


def gap_items(start, end):
    out = []
    offset = start
    if offset % 2:
        out.append((offset, 1, "raw", "", ROM[offset], True))
        offset += 1
    while offset < end:
        if offset + 2 <= end:
            out.append((offset, 2, "raw", "", struct.unpack_from("<H", ROM, offset)[0], True))
            offset += 2
        else:
            out.append((offset, 1, "raw", "", ROM[offset], True))
            offset += 1
    return out


def word_lines(offset, size, value, comment=""):
    tail = ("\t; " + comment) if comment else ""
    if size == 1:
        return ["\tDCB     0x%02X%s" % (value, tail)]
    if size == 4 and offset % 4 == 0:
        return ["\tDCD     0x%08X%s" % (value, tail)]
    if size == 4:
        return ["\tDCW     0x%04X%s" % (value & 0xFFFF, tail),
                "\tDCW     0x%04X" % (value >> 16)]
    return ["\tDCW     0x%04X%s" % (value, tail)]


def sources_of():
    out, slices = {}, {}
    directory = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        rows = []
        for line in open(os.path.join(directory, name), errors="replace"):
            found = TOKEN_LINE.match(line.rstrip("\n"))
            if found:
                rows.append((int(found.group(3), 16), int(found.group(4), 16)))
        out[name] = rows
    for defined in label_maps()[2].values():
        for label in defined:
            found = re.match(r"\|inc_0x([0-9a-f]+)_0x([0-9a-f]+)\|$", label)
            if found:
                slices[(int(found.group(1), 16), int(found.group(2), 16))] = label
    return out, slices


def label_maps():
    includes, own, where = include_graph()
    units = {name: unit_of(name, includes) for name in own}
    out, names, addr_owner, name_owner = {}, {}, {}, {}
    for name, labels in own.items():
        unit = units[name]
        table = out.setdefault(unit, {})
        defined = names.setdefault(unit, set())
        owners = addr_owner.setdefault(unit, {})
        for address, label in labels.items():
            table.setdefault(address, label)
            owners.setdefault(address, name)
            defined.add(label)
        homes = name_owner.setdefault(unit, {})
        for label, home in where[name].items():
            homes.setdefault(label, home)
    return out, units, names, addr_owner, name_owner


EXEC_REGION = re.compile(r"Execution Region (\S+) \(Base: 0x([0-9a-f]+), Size: 0x([0-9a-f]+)")


def sections(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, errors="replace"):
        found = EXEC_REGION.search(line)
        if found:
            base = int(found.group(2), 16)
            out.append((base, base + int(found.group(3), 16), found.group(1)))
    return sorted(out)


class Sections:

    def __init__(self, regions):
        self.regions = regions
        self.bases = [base for base, _end, _name in regions]

    def of(self, address):
        index = bisect.bisect_right(self.bases, address) - 1
        if index < 0:
            return None
        base, end, name = self.regions[index]
        return name if address < end else None


def include_graph():
    includes, own, where = {}, {}, {}
    directory = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        found_includes, table, lines = [], {}, {}
        for line in open(os.path.join(directory, name), errors="replace"):
            found = re.match(r"^\s*INCLUDE\s+(\S+)", line)
            if found:
                found_includes.append(os.path.basename(found.group(1)))
                continue
            found = re.match(r"^\s*\|([A-Za-z_][A-Za-z0-9_]*)\|\s*$", line)
            if not found or found.group(1) in DIRECTIVES:
                continue
            digits = ADDRESSED.search(found.group(1))
            if digits:
                table.setdefault(int(digits.group(1), 16), "|%s|" % found.group(1))
                lines.setdefault("|%s|" % found.group(1), name)
                continue
            slice_label = re.fullmatch(r"inc_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)", found.group(1))
            if slice_label:
                table.setdefault(ROM_BASE + int(slice_label.group(1), 16),
                                 "|%s|" % found.group(1))
                lines.setdefault("|%s|" % found.group(1), name)
        includes[name] = found_includes
        own[name] = table
        where[name] = lines
    return includes, own, where


def unit_of(name, includes):
    for candidate, children in includes.items():
        if name in children:
            return unit_of(candidate, includes) if candidate != name else name
    return name


class Plan:

    def __init__(self, map_path=None, spans=None, method=False, prologue=False, converted=False,
                 pointer=False):
        self.sections = Sections(sections(map_path or MAP))
        self.bodies = thumb_bodies.closure(spans, method, prologue, converted, pointer)
        self.files, self.slices = sources_of()
        self.labels, self.unit, self.names, self.addr_owner, self.name_owner = label_maps()
        self.covered = {row: body.code_bytes() for row, body in self.bodies.items()}
        self.by_row = {}
        for name, rows in self.files.items():
            for start, end in rows:
                self.by_row[(start, end)] = name
        self.source_rows = {row: body for row, body in self.bodies.items()
                            if self.by_row.get(row) is None}
        self.bodies = {row: body for row, body in self.bodies.items()
                       if self.by_row.get(row) is not None}
        self.needed = set()
        for body in self.bodies.values():
            self.needed |= referenced(body)
        self.defs = self.plan_defs()

    def home(self, row):
        return self.by_row.get(row)

    def unit_of(self, row):
        return self.unit.get(self.home(row))

    def section_of(self, address):
        return self.sections.of(address)

    def plan_defs(self):
        out = {}
        self.def_owner = {}
        for row, body in self.bodies.items():
            unit = self.unit_of(row)
            if unit is None:
                continue
            table = out.setdefault(unit, {})
            for address in self.needed & {ROM_BASE + offset for offset in self.covered[row]}:
                if self.labels.get(unit, {}).get(address) is None:
                    table[address] = "|loc_%08X|" % address
                    self.def_owner[(unit, address)] = self.home(row)
        return out

    def name_for(self, unit, address):
        table = self.labels.get(unit, {})
        if address in table:
            return table[address], self.addr_owner.get(unit, {}).get(address), address
        if address in self.defs.get(unit, {}):
            return self.defs[unit][address], self.def_owner.get((unit, address)), address
        offset = address - ROM_BASE
        for (start, end), label in self.slices.items():
            if start <= offset < end and label in self.names.get(unit, set()):
                return ("%s + 0x%x" % (label, offset - start),
                        self.name_owner.get(unit, {}).get(label), ROM_BASE + start)
        return None, None, None


class Emitter:

    def __init__(self, plan):
        self.plan = plan
        self.bodies = {}
        self.variant = {}
        self.raw = {}
        self.bypass = {}
        self.items = {}
        self.sizes = {}
        self.where = {}

    def spell(self, row, unit, item, final):
        offset, size, mnemonic, operands, value, gap = item
        if gap:
            return word_lines(offset, size, value, "" if size == 2 else "retail byte")
        reason = self.raw.get(offset)
        if reason is not None:
            return word_lines(offset, size, value, reason)
        if mnemonic == "dcd":
            return word_lines(offset, 4, value, "pool word the body loads")
        target = literal_of(mnemonic, operands, offset) \
            if is_branch(mnemonic) or mnemonic == "adr" else None
        if mnemonic in ("bx", "blx"):
            return ["\t%-8s %s" % (mnemonic.upper(), operands)]
        if target is not None:
            label = None
            owner = None
            symbol = None
            if ROM_BASE + row[0] <= target < ROM_BASE + row[1]:
                label = self.plan.defs.get(unit, {}).get(target) or \
                    self.plan.labels.get(unit, {}).get(target)
                owner = self.plan.def_owner.get((unit, target)) or \
                    self.plan.addr_owner.get(unit, {}).get(target)
                symbol = target
            else:
                label, owner, symbol = self.plan.name_for(unit, target)
            if label is None:
                if size == 4 and 0x08000000 <= target < 0x0A000000:
                    return ["\t%-8s 0x%08X" % (mnemonic.upper(), target)]
                self.raw[offset] = "no label names 0x%08X" % target
                return word_lines(offset, size, value, "no label names 0x%08X" % target)
            if size == 2 and symbol is not None \
                    and self.plan.section_of(symbol) != self.plan.section_of(ROM_BASE + offset):
                self.raw[offset] = ("armasm A1253E: a 16-bit Thumb branch to %s, whose symbol "
                                    "0x%08X is in section %s, from section %s, cannot be relocated"
                                    % (label, symbol, self.plan.section_of(symbol),
                                       self.plan.section_of(ROM_BASE + offset)))
                return word_lines(offset, size, value, self.raw[offset])
            if offset in self.bypass[row] and not final:
                return word_lines(offset, size, value, "probe placeholder: %s %s" % (mnemonic,
                                                                                     label))
            head = "%s %s" % (mnemonic.upper(), label)
            if mnemonic == "adr":
                head = "ADR %s, %s" % (operands.split(",")[0].strip(), label)
            return ["\t%-8s %s" % tuple(head.split(" ", 1))]
        candidates = plain_candidates(mnemonic, operands)
        if not candidates:
            self.raw[offset] = "no assembler spelling for %s %s" % (mnemonic, operands)
            return word_lines(offset, size, value, "%s %s | no assembler spelling"
                              % (mnemonic, operands))
        shape = shape_of(mnemonic, operands)
        index = min(self.variant.get(shape, SHAPES.get(shape, 0)), len(candidates) - 1)
        return ["\t" + candidates[index]]

    def render(self, row, final):
        unit = self.plan.unit_of(row)
        out = []
        for item in self.items[row]:
            offset = item[0]
            label = self.plan.defs.get(unit, {}).get(ROM_BASE + offset)
            if label is not None:
                out.append((None, label))
            for line in self.spell(row, unit, item, final):
                out.append((offset, line))
        return out

    def pieces(self, row, final):
        unit = self.plan.unit_of(row)
        pieces = []
        start = end = None
        lines = []
        gap = False
        for item in self.items[row]:
            offset, size = item[0], item[1]
            is_gap = item[5]
            if start is None:
                start, end, lines, gap = offset, offset, [], is_gap
            elif is_gap != gap or offset != end:
                pieces.append(self.piece(start, end, lines, gap, row, unit))
                start, end, lines, gap = offset, offset, [], is_gap
            end = offset + size
            if is_gap:
                continue
            label = self.plan.defs.get(unit, {}).get(ROM_BASE + offset)
            if label is not None:
                lines.append(label)
            lines.extend(self.spell(row, unit, item, final))
        if start is not None:
            pieces.append(self.piece(start, end, lines, gap, row, unit))
        return pieces

    def piece(self, start, end, lines, gap, row, unit=None):
        if gap:
            address = ROM_BASE + start
            named = (self.plan.labels.get(unit, {}).get(address) is not None
                     or self.plan.defs.get(unit, {}).get(address) is not None)
            label = [] if named else ["|unk_%08X|" % address]
            return (start, end, label + ["INCBIN  %s" % gap_name(start, end)])
        if not lines:
            raise ValueError("empty emitted run 0x%06x..0x%06x in row 0x%06x"
                             % (start, end, row[0]))
        return (start, end, lines)

    def prove(self, row):
        self.items[row] = full_items(self.bodies[row])
        self.sizes[row] = {item[0]: item[1] for item in self.items[row]}
        self.bypass[row] = set()
        for item in self.items[row]:
            offset, _size, mnemonic, operands, _value, gap = item
            if gap or (not is_branch(mnemonic) and mnemonic != "adr"):
                continue
            target = literal_of(mnemonic, operands, offset)
            if target is not None and not (row[0] <= target - ROM_BASE < row[1]):
                self.bypass[row].add(offset)
        want = ROM[row[0]:row[1]]
        got, refusals = self.assemble(row)
        for _attempt in range(10):
            if got is not None and got[self.pad:self.pad + len(want)] == want:
                return True, None
            changed = False
            for number, message in refusals:
                offset = self.where.get(number - 3) if number - 3 in self.where else None
                if offset is not None and offset not in self.raw:
                    self.raw[offset] = "armasm %s" % message
                    changed = True
            if got is not None:
                for offset, size, mnemonic, operands, _value, gap in self.items[row]:
                    if gap or offset in self.raw:
                        continue
                    at = self.pad + offset - row[0]
                    if got[at:at + size] != ROM[offset:offset + size]:
                        candidates = plain_candidates(mnemonic, operands)
                        shape = shape_of(mnemonic, operands)
                        index = self.variant.get(shape, SHAPES.get(shape, 0)) + 1
                        if index < len(candidates):
                            self.variant[shape] = index
                            SHAPES[shape] = index
                        else:
                            self.raw[offset] = "the assembler does not reproduce this word"
                        changed = True
            if not changed:
                break
            got, refusals = self.assemble(row)
        reason = "the body does not reassemble byte-exact"
        if refusals:
            reason = "armasm %s" % refusals[0][1]
        return False, reason

    def assemble(self, row):
        pad = (ROM_BASE + row[0]) % 4
        rendered = self.render(row, False)
        lines = [line for _offset, line in rendered]
        self.where = {index + (1 if pad else 0): offset
                      for index, (offset, _line) in enumerate(rendered) if offset is not None}
        self.pad = pad
        return arm_body_convert.assemble(body_text(lines, pad), ROM_BASE + row[0] - pad, DEV)


def gap_name(start, end):
    return "baserom.gba_0x%x_0x%x.extracted" % (start, end)


def read_rows(path):
    with open(path, newline="") as handle:
        return sorted((int(row["start"], 16), int(row["end"], 16)) for row in csv.DictReader(handle))


def body_text(lines, pad=0):
    head = "\tAREA |thumb|, CODE, READONLY\n\tCODE16\n"
    if pad:
        head += "\tDCB     0x00\n" * (pad % 2) + "\tDCW     0x0000\n" * (pad // 2)
    return head + "\n".join(lines) + "\n\tEND\n"


def splice_all(plan, emitter, converted, write):
    by_file = {}
    for row in converted:
        name = plan.home(row)
        if name is not None:
            by_file.setdefault(name, []).append(row)
    gaps, spliced = [], {}
    for name, rows in sorted(by_file.items()):
        path = os.path.join(ROOT, "asm", name)
        text = open(path, newline="").read()
        for row in sorted(rows):
            pieces = emitter.pieces(row, True)
            for start, end, lines in pieces:
                if lines and any(line.startswith("INCBIN") for line in lines) \
                        and (start, end) != row:
                    gaps.append((start, end))
            text = bios_block_scan.replace_slice(text, row, pieces)
        spliced[name] = text
    if write:
        for name, text in sorted(spliced.items()):
            with open(os.path.join(ROOT, "asm", name), "w", newline="") as handle:
                handle.write(text)
    return gaps


def sync_rebuild(gaps, write):
    path = os.path.join(ROOT, "rebuild.cmd")
    lines = open(path, newline="").read().split("\n")
    named = set()
    for rows in sources_of()[0].values():
        named |= set(rows)
    kept, dropped, indexes = [], [], []
    for line in lines:
        found = CALL_LINE.match(line)
        if found and (int(found.group(1), 16), int(found.group(2), 16)) not in named:
            dropped.append(line)
            continue
        if found:
            indexes.append(len(kept))
        kept.append(line)
    if not indexes:
        raise ValueError("rebuild.cmd carries no incbin.bat call to append after")
    added = ["call tools\\incbin.bat baserom.gba 0x%x 0x%x" % (start, end)
             for start, end in sorted(set(gaps))]
    if write:
        kept[indexes[-1] + 1:indexes[-1] + 1] = added
        with open(path, "w", newline="") as handle:
            handle.write("\n".join(kept))
    return added, dropped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--skip-prove", action="store_true")
    parser.add_argument("--today", action="store_true",
                        help="row universe = the INCBIN lines the tree carries now (post-conversion "
                             "re-run; P-501)")
    parser.add_argument("--rows",
                        help="row universe = this CSV's start/end columns, instead of every INCBIN row")
    parser.add_argument("--method", action="store_true",
                        help="also enter the class-table method targets (thumb_bodies.method_entries)")
    parser.add_argument("--prologue", action="store_true",
                        help="also enter every PUSH {..,lr} shape whose walk ends in a return "
                             "(thumb_bodies.prologue_entries; weigh it against code_band's control)")
    parser.add_argument("--converted", action="store_true",
                        help="also enter the branch targets of the bodies the converter already wrote "
                             "(thumb_bodies.converted_entries)")
    parser.add_argument("--pointer", action="store_true",
                        help="also enter a pointer-tables word whose bit 0 is set "
                             "(thumb_bodies.pointer_entries): an indirect Thumb entry")
    args = parser.parse_args(argv)
    load_lessons()
    spans = None
    if args.rows:
        spans = read_rows(args.rows)
    elif args.today:
        spans = thumb_bodies.today_rows()
    plan = Plan(spans=spans, method=args.method, prologue=args.prologue,
                converted=args.converted, pointer=args.pointer)
    if not plan.sections.regions:
        raise SystemExit("%s carries no execution region: rebuild before converting, or pass a map"
                         % MAP)
    print("sections: %d, from %s" % (len(plan.sections.regions),
                                     os.path.relpath(MAP, ROOT).replace(os.sep, "/")))
    emitter = Emitter(plan)
    converted, refused, no_code = {}, {}, {}
    for row in sorted(plan.bodies):
        body = plan.bodies[row]
        emitter.bodies[row] = body
        if not body.code:
            no_code[row] = "; ".join(sorted({why for _offset, why in body.stops})) \
                or "the walk reached no instruction"
            continue
        ok, reason = emitter.prove(row)
        if ok:
            converted[row] = body
        else:
            refused[row] = reason
    walked = sum(plan.bodies[row].walked for row in converted)
    pool = sum(plan.bodies[row].pool_bytes for row in converted)
    print("rows %d: converted %d (%d walked B, %d pool B), assembler-refused %d, "
          "no-code %d, already-source %d"
          % (len(plan.bodies), len(converted), walked, pool, len(refused), len(no_code),
             len(plan.source_rows)))
    if not args.write:
        for row in sorted(refused):
            print("  REFUSED 0x%06x..0x%06x %s" % (row[0], row[1], refused[row]))
        for row in sorted(no_code):
            print("  NO-CODE 0x%06x..0x%06x %s" % (row[0], row[1], no_code[row]))
        return 0 if not (refused or no_code) else 1
    save_lessons()
    gaps = splice_all(plan, emitter, converted, args.write)
    body, dropped = sync_rebuild(gaps, args.write)
    rows = []
    for row in sorted(plan.bodies):
        found = plan.bodies[row]
        if row in converted:
            verdict, detail = thumb_bodies.VERDICT_CONVERTED, ""
        elif row in refused:
            verdict, detail = thumb_bodies.VERDICT_REFUSED, refused[row]
        else:
            verdict, detail = thumb_bodies.VERDICT_NO_CODE, no_code[row]
        runs = [[start, end] for start, end, lines in emitter.pieces(row, True)
                if not lines[0].startswith("INCBIN")] if row in converted else []
        rows.append({"start": row[0], "end": row[1], "file": plan.home(row), "kind": found.kind,
                     "entry_site": found.entries[0][2] if found.entries else "",
                     "walked_bytes": found.walked if row in converted else 0,
                     "pool_bytes": found.pool_bytes if row in converted else 0,
                     "runs": runs,
                     "verdict": verdict, "detail": detail})
    if not os.path.isdir(DEV):
        os.makedirs(DEV)
    json.dump({"rows": rows, "gaps": sorted(set(gaps))}, open(MANIFEST, "w"), indent=1)
    print("spliced %d file(s); %d new retail gap(s); rebuild.cmd gains %d incbin call(s) and drops "
          "%d stale one(s)"
          % (len({plan.home(row) for row in converted}), len(set(gaps)), len(body), len(dropped)))
    print("wrote %s" % os.path.relpath(MANIFEST, ROOT).replace(os.sep, "/"))
    thumb_bodies.census()
    return 0


if __name__ == "__main__":
    sys.exit(main())
