from __future__ import annotations

import json
import os
import sys

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "symbols"))

import arm_bodies  # noqa: E402
import generate_symbols  # noqa: E402

ROM_BASE = arm_bodies.ROM_BASE
THUMB = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
ARM = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)


def states():
    path = os.path.join(ROOT, "build", "buu.map")
    if not os.path.exists(path):
        raise SystemExit("build/buu.map is missing: rebuild before gathering evidence")
    return generate_symbols.read_map(path)[1]


def mode_of(map_states, address):
    return "arm" if generate_symbols.state_at(map_states, address) == "$a" else "thumb"


def instruction_ranges():
    map_states = states()
    out = []
    for offset, _length, _isa, insn in arm_bodies.ledger(os.path.join(arm_bodies.ROOT, "work",
                                                                     "ledger.csv")):
        if insn <= 0:
            continue
        mode = mode_of(map_states, offset + ROM_BASE)
        out.append((offset, offset + insn, mode))
    return out


def references(spans, wanted):
    found = {}
    for start, end, state in spans:
        engine = ARM if state == "arm" else THUMB
        for instruction in engine.disasm(arm_bodies.ROM[start:end], ROM_BASE + start):
            mnemonic = instruction.mnemonic
            if not mnemonic.startswith("b"):
                continue
            operands = instruction.op_str
            if not (operands.startswith("#") or operands.startswith("0x")):
                continue
            target = int(operands.lstrip("#"), 0)
            if target not in wanted:
                continue
            found.setdefault(target, []).append((state, instruction.address, mnemonic, operands))
    return found


OUT = os.path.join(ROOT, "build", "arm_evidence.json")


def load():
    if not os.path.exists(OUT):
        raise SystemExit("%s is missing: run arm_evidence.py first" % OUT)
    return {int(key, 16): value for key, value in json.load(open(OUT)).items()}


def evidence_for(row, references=None):
    start = row[3] + arm_bodies.ROM_BASE
    if row[3] >= 8 and arm_bodies.ROM[row[3] - 4:row[3]] == arm_bodies.VENEER:
        return "veneer", ""
    entries = (references or {}).get(start, [])
    arm = [entry for entry in entries if entry[0] == "arm"]
    if arm:
        return "arm-xref", "ARM 0x%08x %s %s" % (arm[0][1], arm[0][2], arm[0][3])
    if entries:
        return "thumb-xref", "Thumb 0x%08x %s %s" % (entries[0][1], entries[0][2], entries[0][3])
    return "none", ""


def main(argv=None):
    rows = arm_bodies.enumerated()
    wanted = {row[3] + ROM_BASE for _flags, row in rows}
    converted = {"%08x" % (row[3] + ROM_BASE) for row in arm_bodies.converted_rows()}
    found = references(instruction_ranges(), wanted)
    counts = {}
    for flags, row in rows:
        kinds = {entry[0] for entry in found.get(row[3] + ROM_BASE, [])}
        verdict = "both" if len(kinds) > 1 else (kinds.pop() if kinds else "none")
        counts[verdict] = counts.get(verdict, 0) + 1
    print("rows reached by: %s" % counts)
    for target in sorted(found):
        kind, site, mnemonic, operands = found[target][0]
        print("  0x%08x <- 0x%08x %s %s %s%s" % (target, site, kind, mnemonic, operands,
                                                 "  [converted]"
                                                 if "%08x" % target in converted else ""))
    with open(OUT, "w") as handle:
        json.dump({"%08x" % target: entries for target, entries in found.items()}, handle, indent=1)
    print("wrote %s" % os.path.relpath(OUT, ROOT).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
