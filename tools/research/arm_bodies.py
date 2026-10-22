"""ARM bodies the transcribed slices carry as extracted data, and their conversion to ARM source.

PATH-100-016 promoted data runs out of the transcribed slices into per-symbol retail INCBIN
slices. Some of those runs are not data at all: a Thumb file reaches an ARM function through a
four-byte veneer (`BX pc` then `LSL r0,r0,#0`), and the ARM body that follows was spelled as an
`INCBIN` of the bytes. The bytes are code, so the classification is wrong and the ARM body is
transcribed back as source.

Two criteria name the rows:

  (a) the row's ROM range overlaps an instruction row of the PRE-SPLIT ledger
      (`19b4e44^:work/ledger.csv`), i.e. the bytes were transcribed as source before PATH-100-016
      and are extracted data after it;
  (b) the four bytes before the row's own start are the Thumb veneer `78 47 00 00`, so the row's
      start is the ARM body's entry and is word aligned.

Every row of the union is then classified from its own bytes, with capstone and with the
assembler: whole ARM instructions that reassemble byte-exact are CONVERTED; bytes that assemble
under `CODE16` (Thumb) are out of this ticket's scope and stay INCBIN; anything else stays INCBIN
with the reason. The byte proof is the gate's DIGEST MATCH plus a per-row scratch assembly.

    python tools/research/arm_bodies.py census
    python tools/research/arm_bodies.py convert [--write]
    python tools/research/arm_bodies.py check
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import subprocess
import sys

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate  # noqa: E402
ROM_BASE = 0x08000000
VENEER = b"\x78\x47\x00\x00"
SLICE = re.compile(r"INCBIN\s+(baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted)")
TOKEN = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted")
LABEL_DEF = re.compile(r"^\s*\|([A-Za-z_][A-Za-z0-9_]*)\|\s*$")
PRE_LEDGER = os.path.join(ROOT, "build", "ledger-pre.csv")
CENSUS_CSV = os.path.join(ROOT, "docs", "research", "ARM_BODIES.csv")
MANIFEST = os.path.join(ROOT, "build", "arm_bodies", "manifest.json")

ROM = open(os.path.join(ROOT, "baserom.gba"), "rb").read()


def ledger(path):
    return [(row[0], row[1], row[2], row[7]) for row in gate.ledger_rows(path)]


def instruction_bytes(rows):
    out = set()
    for offset, _length, _isa, insn in rows:
        out |= set(range(offset, offset + insn))
    return out


def incbin_rows():
    rows = []
    directory = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        for number, line in enumerate(open(os.path.join(directory, name), errors="replace"), 1):
            found = SLICE.search(line)
            if found:
                rows.append((name, number, found.group(1), int(found.group(2), 16),
                             int(found.group(3), 16)))
    return rows


def converted_rows():
    if not os.path.exists(MANIFEST):
        return []
    data = json.load(open(MANIFEST))
    return [(entry["file"], entry["line"],
             "baserom.gba_0x%x_0x%x.extracted" % (entry["start"], entry["end"]),
             entry["start"], entry["end"])
            for entry in sorted(data["converted"], key=lambda item: (item["file"], item["line"]))]


def criteria_of(start, end, pre):
    flags = ""
    if set(range(start, end)) & pre:
        flags += "a"
    if start >= 8 and ROM[start - 4:start] == VENEER:
        flags += "b"
    return flags


def enumerated():
    pre = instruction_bytes(ledger(PRE_LEDGER))
    out, seen = [], set()
    for row in converted_rows() + incbin_rows():
        if (row[0], row[3], row[4]) in seen:
            continue
        seen.add((row[0], row[3], row[4]))
        flags = criteria_of(row[3], row[4], pre)
        if flags:
            out.append((flags, row))
    return sorted(out, key=lambda item: (item[1][0], item[1][3]))


def symbols():
    path = os.path.join(ROOT, "build", "output", "symbols.json")
    if not os.path.exists(path):
        return {}
    data = json.load(open(path))
    out = {}
    for symbol in data["symbols"]:
        out[int(symbol["address"], 16)] = symbol["name"].strip("|")
    return out


def existing_labels():
    out = {}
    directory = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        for line in open(os.path.join(directory, name), errors="replace"):
            found = LABEL_DEF.match(line)
            if not found:
                continue
            label = found.group(1)
            digits = re.fullmatch(r"(?:sub|loc|unk|gap)_([0-9A-Fa-f]{8})", label)
            if digits:
                out.setdefault(int(digits.group(1), 16) - ROM_BASE, "|%s|" % label)
    return out


def arm_decode(start, end):
    engine = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    instructions, gaps = [], []
    at = start
    for ins in engine.disasm(ROM[start:end], ROM_BASE + start):
        offset = ins.address - ROM_BASE
        if offset > at:
            gaps.append((at, offset))
        instructions.append((offset, ins.size, ins.mnemonic, ins.op_str, ins.bytes))
        at = offset + ins.size
    if at < end:
        gaps.append((at, end))
    return instructions, gaps


def thumb_decodes(start, end):
    engine = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    at = start
    for ins in engine.disasm(ROM[start:end], ROM_BASE + start):
        if ins.address - ROM_BASE != at:
            return False
        at += ins.size
    return at == end and (end - start) % 2 == 0


def pool_words(start, end, gaps):
    loaded = set()
    engine = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    for offset, size, mnemonic, operands, _raw in arm_decode(start, end)[0]:
        if mnemonic not in ("ldr", "ldrbt", "ldrt"):
            continue
        found = re.search(r"\[pc, #(0x[0-9a-f]+|\d+)\]", operands)
        if found:
            loaded.add((offset + 8 + int(found.group(1), 0)) & ~3)
    words = {}
    for low, high in gaps:
        for offset in range(low, high, 4):
            if 0 <= offset < len(ROM) - 3 and offset in loaded:
                words[offset] = struct.unpack_from("<I", ROM, offset)[0]
    return words


def classify(flags, row, reassembles=None):
    start, end = row[3], row[4]
    if (end - start) % 4:
        return "stays-incbin", "length %d is not a multiple of 4" % (end - start)
    instructions, gaps = arm_decode(start, end)
    if not instructions:
        return "stays-incbin", "no ARM instruction decodes at the row's start"
    loaded = pool_words(start, end, gaps)
    leftover = [g for g in gaps if any(o not in loaded for o in range(g[0], g[1], 4))]
    if leftover:
        if thumb_decodes(start, end):
            return "thumb", "the whole range decodes as Thumb instructions"
        return "stays-incbin", ("undecodable ARM bytes at 0x%06x..0x%06x that the body does not "
                                "load" % leftover[0])
    if reassembles is None:
        return "arm-decode", "%d whole ARM instruction(s), %d pool word(s)" % (
            len(instructions) - len(loaded), len(loaded))
    if not reassembles:
        return "ambiguous", ("capstone decodes %d whole ARM instruction(s) that the assembler "
                             "does not reproduce byte-exactly"
                             % (len(instructions) - len(loaded)))
    return "arm", "%d ARM instruction(s), %d pool word(s)" % (
        len(instructions) - len(loaded), len(loaded))


def print_ledger():
    for flags, row in enumerated():
        start, end = row[3], row[4]
        instructions, gaps = arm_decode(start, end)
        loaded = pool_words(start, end, gaps)
        verdict, detail = classify(flags, row)
        print("%s %-20s:%-6d %-46s 0x%06x..0x%06x 0x%08x..0x%08x %5d B  "
              "insn=%-4d pool=%-2d %-14s %s"
              % (flags, row[0], row[1], row[2], start, end, ROM_BASE + start, ROM_BASE + end,
                 end - start, len(instructions) - len(loaded), len(loaded), verdict, detail))


def census(path=CENSUS_CSV):
    import arm_evidence
    references = arm_evidence.load() if os.path.exists(arm_evidence.OUT) else None
    converted = {(entry["file"], entry["start"], entry["end"])
                 for entry in json.load(open(MANIFEST))["converted"]} if os.path.exists(MANIFEST) \
        else set()
    rows = enumerated()
    counts, byte_counts, crit_counts = {}, {}, {}
    lines = ["criterion,evidence,site,file,line,token,start,end,gba_start,gba_end,bytes,"
             "arm_instructions,pool_words,verdict,detail"]
    for flags, row in rows:
        start, end = row[3], row[4]
        instructions, gaps = arm_decode(start, end)
        loaded = pool_words(start, end, gaps)
        evidence, site = arm_evidence.evidence_for(row, references)
        if (row[0], start, end) in converted:
            verdict, detail = "arm", "converted byte-exact"
        elif evidence in ("veneer", "arm-xref"):
            verdict, detail = "arm-refused", "ARM-state evidence, no byte-exact reassembly"
        elif evidence == "thumb-xref":
            verdict, detail = "thumb-xref", "only Thumb references reach it: " + site
        elif thumb_decodes(start, end):
            verdict, detail = "thumb", "the whole range decodes as Thumb instructions"
        else:
            verdict, detail = "no-evidence", "no ARM-state reference and no veneer"
        counts[verdict] = counts.get(verdict, 0) + 1
        byte_counts[verdict] = byte_counts.get(verdict, 0) + (end - start)
        crit_counts[flags] = crit_counts.get(flags, 0) + 1
        lines.append("%s,%s,%s,%s,%d,%s,0x%x,0x%x,0x%08x,0x%08x,%d,%d,%d,%s,%s"
                     % (flags, evidence, site, row[0], row[1], row[2], start, end,
                        ROM_BASE + start, ROM_BASE + end, end - start,
                        len(instructions) - len(loaded), len(loaded), verdict, detail))
    open(path, "w", encoding="ascii", newline="\n").write("\n".join(lines) + "\n")
    print("criterion counts: %s" % crit_counts)
    print("union: %d row(s), %d B" % (len(rows), sum(r[4] - r[3] for _, r in rows)))
    for verdict in sorted(counts):
        print("  %-12s %4d row(s)  %7d B" % (verdict, counts[verdict], byte_counts[verdict]))
    print("wrote %s" % os.path.relpath(path, ROOT).replace(os.sep, "/"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("census", "list", "convert", "check"))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=CENSUS_CSV)
    args = parser.parse_args(argv)
    if args.mode == "census":
        census(args.out)
    elif args.mode == "list":
        print_ledger()
    elif args.mode == "convert":
        import arm_body_convert
        return arm_body_convert.main(args.write)
    elif args.mode == "check":
        import arm_body_convert
        return arm_body_convert.check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
