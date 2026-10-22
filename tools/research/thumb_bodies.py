"""Thumb bodies the transcribed slices carry as extracted data, and their conversion to Thumb source.

PATH-100-016 promoted data runs out of the transcribed slices into per-symbol retail INCBIN slices.
PATH-100-017 took the rows an ARM reference or a `BX pc` veneer proves are ARM. This module takes the
other half: a row that a Thumb-state control transfer ENTERS is Thumb code, whatever its bytes look
like. Decoding as ARM and reassembling byte-exact is not evidence of anything (P-488); the reference
is, and its state is the target's state (P-489).

The evidence rule, exactly (the ticket's rule 2):

  * a row address is an ENTRY when a Thumb-state control transfer in SOURCE code (a ledger row the
    tree carries as an instruction, decoded in the mode its own mapping symbol names) targets an
    address inside it: `B`/`B<cond>`/`BL`, or a `BX`/`BLX` whose register was loaded from a
    pc-relative word holding that address with bit 0 set (a Thumb function pointer);
  * from each entry, Thumb control flow is WALKED - fallthrough, in-row branch targets, `BL` return
    fallthrough - and stops at an unconditional exit: a `B` out of the row, a `BX`, or any
    instruction that loads `pc`;
  * only walked bytes are code; a pc-relative word the walk loads is a POOL word; every other byte
    stays INCBIN;
  * a walked target that lands in another row makes that row an entry transitively, which is the
    only way a `thumb` or `no-evidence` row converts.

    python tools/research/thumb_bodies.py census [--list]
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

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import arm_bodies  # noqa: E402
import arm_evidence  # noqa: E402

ROM_BASE = arm_bodies.ROM_BASE
ROM = arm_bodies.ROM
THUMB_BIT = 1
CENSUS_CSV = os.path.join(ROOT, "docs", "research", "ARM_BODIES.csv")
MANIFEST = os.path.join(ROOT, "build", "thumb_bodies", "manifest.json")
PC_RELATIVE = re.compile(r"\[pc, #(0x[0-9a-f]+|\d+)\]")
IMMEDIATE = re.compile(r"^#(0x[0-9a-f]+|\d+)$")
CONDITIONS = ("eq", "ne", "cs", "hs", "cc", "lo", "mi", "pl", "vs", "vc", "hi", "ls", "ge", "lt",
              "gt", "le")
SIZE4_ALLOWED = ("bl",)
NOT_V4T = frozenset(("cbz", "cbnz", "rev", "rev16", "revsh", "sxtb", "sxth", "uxtb", "uxth",
                     "bkpt", "nop", "cps", "cpsid", "cpsie", "it", "itt", "ite", "ittt", "itte",
                     "itet", "itee", "addw", "subw", "movw", "movt", "ldrd", "strd", "ldrex",
                     "strex", "dmb", "dsb", "isb", "tbb", "tbh", "udf", "setend"))
ENGINE = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

VERDICT_CONVERTED = "thumb-converted"
VERDICT_REFUSED = "thumb-refused"
VERDICT_NO_CODE = "thumb-not-code"
CENSUS_THUMB = os.path.join(ROOT, "docs", "research", "THUMB_BODIES.csv")
FIELDS = ("criterion", "evidence", "site", "file", "line", "token", "start", "end", "gba_start",
          "gba_end", "bytes", "arm_instructions", "pool_words", "verdict", "detail")
THUMB_FIELDS = ("entry_site", "walked_bytes", "pool_bytes", "left_incbin_bytes")


def frozen_rows():
    out = {}
    if not os.path.exists(CENSUS_CSV):
        return out
    for row in csv.DictReader(open(CENSUS_CSV, newline="")):
        out[(int(row["start"], 16), int(row["end"], 16))] = row
    return out


def rows():
    seen = set(frozen_rows())
    for _flags, row in arm_bodies.enumerated():
        seen.add((row[3], row[4]))
    return sorted(seen)


def today_rows():
    return sorted({(row[3], row[4]) for row in arm_bodies.incbin_rows()})


def refuse_overlap(spans):
    for before, after in zip(spans, spans[1:]):
        if before[1] > after[0]:
            raise SystemExit("INCBIN rows 0x%06x..0x%06x and 0x%06x..0x%06x overlap: the tree is "
                             "already converted, or its source is inconsistent"
                             % (before[0], before[1], after[0], after[1]))


class Rows:

    def __init__(self, spans):
        self.spans = spans
        self.starts = [start for start, _end in spans]

    def of(self, offset):
        index = bisect.bisect_right(self.starts, offset) - 1
        if index < 0:
            return None
        start, end = self.spans[index]
        return (start, end) if start <= offset < end else None


def decode(offset):
    got = list(ENGINE.disasm(ROM[offset:offset + 4], ROM_BASE + offset))
    if not got:
        return None
    instruction = got[0]
    if instruction.size == 4 and instruction.mnemonic not in SIZE4_ALLOWED:
        return None
    if instruction.mnemonic in NOT_V4T:
        return None
    return instruction.size, instruction.mnemonic, instruction.op_str


def direct_target(mnemonic, operands):
    if mnemonic == "b" or mnemonic == "bl" or \
            (mnemonic.startswith("b") and mnemonic[1:] in CONDITIONS):
        found = IMMEDIATE.match(operands)
        if found:
            return int(found.group(1), 0)
    return None


def loads_pc(mnemonic, operands):
    if mnemonic in ("bx", "blx"):
        return True
    head = operands.split(",")[0].strip()
    if mnemonic == "mov":
        return head == "pc"
    if mnemonic in ("ldm", "ldmia", "ldmfd", "pop"):
        return "pc" in operands
    if mnemonic.startswith(("ldr", "ldrb", "ldrh")):
        return head == "pc"
    return False


class Body:

    def __init__(self, row, kind):
        self.row = row
        self.kind = kind
        self.code = {}
        self.pool = set()
        self.outside_pool = set()
        self.targets = set()
        self.stops = []
        self.entries = []

    @property
    def walked(self):
        return sum(size for size, _m, _o in self.code.values())

    @property
    def pool_bytes(self):
        return len(self.pool) * 4

    @property
    def left(self):
        return (self.row[1] - self.row[0]) - self.walked - self.pool_bytes

    def code_bytes(self):
        out = set()
        for offset, (size, _m, _o) in self.code.items():
            out |= set(range(offset, offset + size))
        for offset in self.pool:
            out |= set(range(offset, offset + 4))
        return out


def walk(row, entries, kind="entry"):
    body = Body(row, kind)
    body.entries = list(entries)
    pending = [offset for offset, _k, _site, _tier in entries]
    seen = set()
    while pending:
        offset = pending.pop()
        while True:
            if offset in seen:
                break
            if not row[0] <= offset < row[1]:
                body.targets.add(ROM_BASE + offset)
                break
            seen.add(offset)
            got = decode(offset)
            if got is None:
                body.stops.append((offset, "not an ARMv4T Thumb instruction"))
                break
            size, mnemonic, operands = got
            if offset + size > row[1]:
                body.stops.append((offset, "the instruction crosses the row end"))
                target = direct_target(mnemonic, operands)
                if target is not None:
                    body.targets.add(target)
                break
            body.code[offset] = (size, mnemonic, operands)
            if mnemonic.startswith("ldr"):
                found = PC_RELATIVE.search(operands)
                if found:
                    literal = ((offset + ROM_BASE + 4) & ~3) + int(found.group(1), 0) - ROM_BASE
                    if row[0] <= literal and literal + 4 <= row[1]:
                        body.pool.add(literal)
                    else:
                        body.outside_pool.add(literal)
            target = direct_target(mnemonic, operands)
            if mnemonic == "b":
                if target is not None:
                    if row[0] <= target - ROM_BASE < row[1]:
                        pending.append(target - ROM_BASE)
                    else:
                        body.targets.add(target)
                break
            if loads_pc(mnemonic, operands):
                break
            if target is not None:
                if row[0] <= target - ROM_BASE < row[1]:
                    pending.append(target - ROM_BASE)
                else:
                    body.targets.add(target)
            offset += size
    covered = set()
    for at, (size, _m, _o) in body.code.items():
        covered |= set(range(at, at + size))
    body.pool = {at for at in body.pool if at not in covered}
    return body


def source_rows():
    states = arm_evidence.states()
    out = []
    for offset, length, _isa, insn in arm_bodies.ledger(os.path.join(arm_bodies.ROOT, "work",
                                                                     "ledger.csv")):
        if insn <= 0:
            continue
        out.append((offset, offset + length, arm_evidence.mode_of(states, offset + ROM_BASE),
                    insn))
    return out


def thumb_instructions(start, end):
    at = start
    while at + 2 <= end:
        got = decode(at)
        if got is None:
            at += 2
            continue
        yield at, got
        at += got[0]


def method_sites(blob, edges):
    out = []
    for base, stop in edges:
        for at in range(base, stop - 3, 4):
            target = base + struct.unpack_from("<i", blob, at)[0]
            if 0 <= target < len(blob) and target & THUMB_BIT:
                out.append((base, at, target & ~THUMB_BIT))
    return out


def method_entries(spans):
    import text_tables
    bases = sorted(text_tables.class_bases(ROM))
    tables = text_tables.table_rows(ROM)
    if not bases or not tables:
        return {}
    last = max(row[1] for row in tables)
    edges = [(base, bases[index + 1] if index + 1 < len(bases) else last)
             for index, base in enumerate(bases)]
    index = Rows(spans)
    out = {}
    for base, at, target in method_sites(ROM, edges):
        row = index.of(target)
        if row is None:
            continue
        site = "method table 0x%08x slot 0x%08x -> 0x%08x" % (ROM_BASE + base, ROM_BASE + at,
                                                              ROM_BASE + target)
        out.setdefault(row, []).append((target, "method", site, "method"))
    return out


def pointer_entries(spans):
    import pointer_rows
    index = Rows(spans)
    out = {}
    for start, end, _carrier, _line in pointer_rows.rows():
        for word in pointer_rows.grid(start, end - start):
            value = struct.unpack_from("<I", ROM, word)[0]
            target = value & ~1
            if not value & 1 or not ROM_BASE <= target < ROM_BASE + len(ROM):
                continue
            row = index.of(target - ROM_BASE)
            if row is None:
                continue
            xref = "pointer table word 0x%06X = 0x%08X" % (word, value)
            out.setdefault(row, []).append((target - ROM_BASE, "pointer", xref, "pointer"))
    return out


def returns(body):
    if not body.code:
        return False
    last = max(body.code)
    _size, mnemonic, operands = body.code[last]
    return (mnemonic == "bx" or (mnemonic == "pop" and "pc" in operands)
            or (mnemonic == "mov" and operands.startswith("pc"))
            or (mnemonic == "ldr" and operands.startswith("pc")))


def prologue_entries(spans):
    out = {}
    for start, end in spans:
        row = (start, end)
        for offset in range(start, end - 1, 2):
            if struct.unpack_from("<H", ROM, offset)[0] & 0xFF00 != 0xB500:
                continue
            body = walk(row, [(offset, "prologue", "PUSH {..,lr}", "shape")])
            if returns(body) and body.walked >= 4:
                out.setdefault(row, []).append(
                    (offset, "prologue",
                     "PUSH {..,lr} 0x%08x (walk %d B)" % (ROM_BASE + offset, body.walked), "shape"))
    return out


ENTRY_ADDRESS = re.compile(r"0x([0-9a-f]{7,8})")


def converted_entries(spans):
    index = Rows(spans)
    out = {}
    if not os.path.exists(CENSUS_THUMB):
        return out
    for entry in csv.DictReader(open(CENSUS_THUMB, newline="")):
        if entry["verdict"] != VERDICT_CONVERTED:
            continue
        start, end = int(entry["start"], 16), int(entry["end"], 16)
        found = [int(text, 16) - ROM_BASE for text in ENTRY_ADDRESS.findall(entry["entry_site"] or "")]
        inside = [value for value in found if start <= value < end]
        if not inside:
            continue
        body = walk((start, end), [(inside[-1], "converted", entry["entry_site"], "converted")])
        for target in body.targets:
            row = index.of(target - ROM_BASE)
            if row is None or row == (start, end):
                continue
            site = "Thumb 0x%08x (branch out of converted 0x%06x..0x%06x)" % (target, start, end)
            out.setdefault(row, []).append((target - ROM_BASE, "converted", site, "converted"))
    return out


def entries(spans=None, method=False, prologue=False, converted=False, pointer=False):
    index = Rows(rows() if spans is None else spans)
    found = {}
    for start, end, mode, insn in source_rows():
        if mode != "thumb":
            continue
        for offset, (size, mnemonic, operands) in thumb_instructions(start, end):
            target = direct_target(mnemonic, operands)
            kind = None
            site = "Thumb 0x%08x %s %s" % (ROM_BASE + offset, mnemonic, operands)
            if target is not None:
                kind = "branch"
            elif mnemonic == "ldr":
                literal = PC_RELATIVE.search(operands)
                if literal:
                    address = ((ROM_BASE + offset + 4) & ~3) + int(literal.group(1), 0)
                    value = struct.unpack_from("<I", ROM, address - ROM_BASE)[0]
                    if value & 1 and 0x08000000 <= value < 0x0A000000:
                        target, kind = value & ~1, "pointer"
            if kind is None or target is None:
                continue
            row = index.of(target - ROM_BASE)
            if row is None:
                continue
            tier = "tier1" if offset < start + insn else "tier2"
            found.setdefault(row, []).append(
                (target - ROM_BASE, kind,
                 site if kind == "branch" else "%s -> 0x%08x" % (site, target), tier))
    universe = spans if spans is not None else rows()
    for wanted, producer in ((method, method_entries), (converted, converted_entries),
                             (prologue, prologue_entries), (pointer, pointer_entries)):
        if not wanted:
            continue
        for row, sites in producer(universe).items():
            known = {offset for offset, _kind, _site, _tier in found.get(row, [])}
            found.setdefault(row, []).extend(site for site in sites if site[0] not in known)
    return found


def closure(spans=None, method=False, prologue=False, converted=False, pointer=False):
    spans = rows() if spans is None else spans
    refuse_overlap(spans)
    index = Rows(spans)
    seen = {}
    queue = []
    for row, found in sorted(entries(spans, method, prologue, converted, pointer).items()):
        queue.append(walk(row, found, "entry"))
    while queue:
        body = queue.pop(0)
        if body.row in seen:
            continue
        seen[body.row] = body
        for target in sorted(body.targets):
            other = index.of(target - ROM_BASE)
            if other is None or other in seen:
                continue
            site = "Thumb 0x%08x (walked from 0x%08x)" % (target, body.row[0] + ROM_BASE)
            queue.append(walk(other, [(target - ROM_BASE, "walk", site, "chain")], "transitive"))
    return seen


def tracked():
    if not os.path.exists(CENSUS_THUMB):
        return {}
    out = {}
    for row in csv.DictReader(open(CENSUS_THUMB, newline="")):
        if not row["verdict"]:
            continue
        out[(int(row["start"], 16), int(row["end"], 16))] = {
            "file": row["file"], "kind": row["walk_kind"], "entry_site": row["entry_site"],
            "walked_bytes": int(row["walked_bytes"]), "pool_bytes": int(row["pool_bytes"]),
            "verdict": row["verdict"], "detail": row["detail"]}
    return out


def cached():
    if not os.path.exists(MANIFEST):
        return {}
    return {(entry["start"], entry["end"]): entry
            for entry in json.load(open(MANIFEST))["rows"]}


def record():
    out = tracked()
    out.update(cached())
    return out


def row_state(row):
    manifest = cached()
    if row in manifest:
        entry = manifest[row]
        walked = entry["walked_bytes"] if "walked_bytes" in entry else 0
        pool = entry["pool_bytes"] if "pool_bytes" in entry else 0
        left = (row[1] - row[0]) - walked - pool
        return entry["entry_site"], walked, pool, left, entry["verdict"]
    return "", 0, 0, row[1] - row[0], ""


def site_tiers():
    out = {}
    for start, end, mode, insn in source_rows():
        if mode != "thumb":
            continue
        for offset, _got in thumb_instructions(start, end):
            out[offset] = "tier1" if offset < start + insn else "tier2"
    return out


def census(path=None, out=sys.stdout):
    path = path or CENSUS_THUMB
    frozen = frozen_rows()
    manifest = record()
    bodies = closure() if not manifest else {}
    tiers = site_tiers()
    fields = ("start", "end", "bytes", "file", "arm_verdict", "walk_kind", "entry_site",
              "entry_kind", "entry_tier", "walked_bytes", "pool_bytes", "left_incbin_bytes",
              "verdict", "detail")
    rows_out = []
    counts, byte_counts = {}, {}
    for start, end in sorted(set(frozen) | set(manifest)):
        row = (start, end)
        body = bodies.get(row)
        entry = manifest.get(row)
        if entry is not None:
            verdict, detail = entry["verdict"], entry["detail"]
            walked, pool = entry["walked_bytes"], entry["pool_bytes"]
            site = entry["entry_site"]
            kind = entry["kind"]
        elif body is not None:
            verdict = VERDICT_NO_CODE
            detail = "; ".join(sorted({why for _offset, why in body.stops})) or "no code walked"
            walked = pool = 0
            site = body.entries[0][2] if body.entries else ""
            kind = body.kind
        else:
            verdict, detail = "", ""
            walked = pool = 0
            site, kind = "", ""
        tier = ""
        site_offset = None
        found_site = re.match(r"Thumb 0x([0-9a-f]{8})", site)
        if found_site:
            site_offset = int(found_site.group(1), 16) - ROM_BASE
        if site_offset is not None:
            tier = tiers.get(site_offset, "")
        for _offset, _ekind, _esite, found in (body.entries if body else []):
            if found:
                tier = found
                break
        counts[verdict] = counts.get(verdict, 0) + 1
        byte_counts[verdict] = byte_counts.get(verdict, 0) + (end - start)
        rows_out.append(("0x%x" % start, "0x%x" % end, end - start,
                         frozen[row]["file"] if row in frozen else entry["file"],
                         frozen[row]["verdict"] if row in frozen else "", kind, site,
                         (body.entries[0][1] if body and body.entries else ""), tier, walked,
                         pool, (end - start) - walked - pool, verdict, detail))
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="ascii", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows_out)
    for verdict in sorted(counts):
        print("  %-18s %4d row(s) %7d B" % (verdict, counts[verdict], byte_counts[verdict]))
    print("wrote %s: %d row(s)" % (os.path.relpath(path, ROOT).replace(os.sep, "/"),
                                   len(rows_out)))
    return counts


def entry_report(out=sys.stdout):
    census_rows = []
    if os.path.exists(CENSUS_THUMB):
        with open(CENSUS_THUMB, newline="") as handle:
            census_rows = [row for row in csv.DictReader(handle) if row["verdict"]]
    if census_rows:
        rows = {}
        for row in census_rows:
            key = (int(row["start"], 16), int(row["end"], 16))
            rows[key] = [(key[0], row["entry_kind"], row["entry_site"], row["entry_tier"])]
        source = "the census, one site per row (the first)"
    else:
        rows = entries()
        source = "the walk, every site"
    at_start = {}
    inside = []
    for row in sorted(rows):
        starts = [entry for entry in rows[row] if entry[0] == row[0]]
        if starts:
            for value in {entry[3] for entry in starts}:
                at_start[value] = at_start.get(value, 0) + 1
        else:
            inside.append(row)
    b1 = sum(row[1] - row[0] for row in rows
             if any(e[0] == row[0] and e[3] == "tier1" for e in rows[row]))
    b2 = sum(row[1] - row[0] for row in rows
             if any(e[0] == row[0] and e[3] == "tier2" for e in rows[row]))
    bi = sum(row[1] - row[0] for row in inside)
    print("entries (%s): %d site(s) over %d row(s)"
          % (source, sum(len(v) for v in rows.values()), len(rows)))
    print("  at row start, tier1 : %4d row(s) %6d B" % (at_start.get("tier1", 0), b1))
    print("  at row start, tier2 : %4d row(s) %6d B" % (at_start.get("tier2", 0), b2))
    print("  inside the row only : %4d row(s) %6d B" % (len(inside), bi))
    for row in sorted(rows):
        for offset, kind, site, tier in rows[row]:
            where = "start" if offset == row[0] else "0x%06x" % offset
            print("  0x%06x..0x%06x %5d B  %-8s %-6s %-5s %s"
                  % (row[0], row[1], row[1] - row[0], where, kind, tier, site))
    return rows


def reentry(out=sys.stdout):
    spans = today_rows()
    found = entries(spans)
    census = frozen_rows()
    known = {row for row in census if census[row]["verdict"]}
    new = sorted(row for row in found if row not in known)
    print("today's INCBIN rows: %d; entries: %d site(s) over %d row(s)"
          % (len(spans), sum(len(value) for value in found.values()), len(found)))
    print("rows the census already acted on: %d; NEW: %d row(s) %d B"
          % (len(known), len(new), sum(row[1] - row[0] for row in new)))
    for row in new:
        for offset, _kind, site, tier in found[row]:
            print("  0x%06x..0x%06x %5d B  %-8s %-6s %s"
                  % (row[0], row[1], row[1] - row[0],
                     "start" if offset == row[0] else "0x%06x" % offset, tier, site))
    for row in new:
        if row in census:
            print("  (frozen verdict was empty: %s)" % census[row]["file"])
    return new


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("census", "list", "entries", "reentry"))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.mode == "reentry":
        reentry()
        return 0
    if args.mode == "entries":
        entry_report()
        return 0
    if args.mode == "list":
        bodies = closure()
        kinds = {}
        for body in bodies.values():
            kinds[body.kind] = kinds.get(body.kind, 0) + 1
        print("closure: %d row(s) %s, walked=%d pool=%d left=%d"
              % (len(bodies), kinds, sum(b.walked for b in bodies.values()),
                 sum(b.pool_bytes for b in bodies.values()), sum(b.left for b in bodies.values())))
        return 0
    census(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
