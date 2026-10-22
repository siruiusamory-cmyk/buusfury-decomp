"""What the code does with a pointer into a range: field offsets, stride, and index use.

The census's `unknown-proven` rows are cited by `ldr Rd,[pc,#imm]` sites whose literal names the
range (T-143, `unknown_consumer_search`). That channel says a consumer exists; it does not say
whether the range's extents can be derived from it. This tool answers that second question at the
bytes: decode each loader window at an instruction boundary and report every access made through the
loaded pointer, or through a register derived from it by `adds Rd,Rb,#imm`, so a field map and a
stride come from the CODE and not from byte shapes (K-152, K-153).

An access whose address is not a constant is reported as `INDEXED`: `base + index` where the index
is a register holding no value this tool can follow. That is the one thing that decides promotability -
`base + stride*N` with `N` out of an object field is a LOWER BOUND, not an extent.

    python tools/research/loader_access_trace.py --rom baserom.gba --range 0x76CCE4 0x77AE68

Limits: one window of 0x80 bytes per site, ending at the first `bx lr` / `pop {...,pc}` / `ldm
...,{...,pc}`; a register loses its tracked value the moment anything else writes it (`ldr`, `movs`,
any call clobbers `r0`-`r3`), so a reported offset is only ever one the pointer really addressed at
that instruction; multi-word loads are one access with the register list's byte count; a pointer
passed to a callee is reported as a value with no access; a site whose own address lies inside the
range is flagged, because the halfword-offset loader channel reads data as instructions where the
image is not code (P-420).
"""

from __future__ import annotations

import argparse
import os
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs, CsError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unknown_consumer_search as search  # noqa: E402

ROM_BASE = 0x08000000
WINDOW = 0x80
WIDTHS = {"ldr": 4, "str": 4, "ldrh": 2, "strh": 2, "ldrsb": 1, "ldrsh": 2, "ldrb": 1, "strb": 1}
ACCESSES = tuple(WIDTHS)
READS_FIRST = ("str", "strb", "strh", "stm", "stmia", "stmdb", "push", "cmp", "cmn", "tst", "teq",
               "b", "bx", "cbz", "cbnz", "nop", "bkpt", "svc", "adr")
LISTS = ("pop",)
LDMS = ("ldm", "ldmia", "ldmdb")
CALLS = ("bl", "blx")
KEY = " = "


def disassembler():
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    md.skipdata = True
    return md


def site_trace(rom: bytes, site: int, start: int, end: int, md=None) -> tuple[list[str], list[str]]:
    md = disassembler() if md is None else md
    base = ROM_BASE
    regs: dict[str, int | None] = {}
    lines: list[str] = []
    accesses: list[str] = []
    for ins in md.disasm(rom[site:site + WINDOW], base + site):
        text = "%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str)
        try:
            operands = ins.operands
        except CsError:
            operands = ()
        if ins.mnemonic == "ldr" and len(operands) == 2 and operands[0].type == 1 \
                and operands[1].type == 3 and ins.reg_name(operands[1].mem.base) == "pc":
            target = ((ins.address + 4) & ~3) + operands[1].mem.disp
            value = int.from_bytes(rom[target - base:target - base + 4], "little")
            text += "  ; %08X %08X" % (target, value)
            regs[ins.reg_name(operands[0].reg)] = value
        elif ins.mnemonic in ACCESSES and len(operands) >= 2 and operands[1].type == 3:
            holder = ins.reg_name(operands[1].mem.base)
            if regs.get(holder) is not None and operands[1].mem.index:
                accesses.append("INDEXED %s [%s + reg]" % (ins.mnemonic, holder))
            elif regs.get(holder) is not None and start <= regs[holder] - base < end:
                accesses.append("%s %s +%#x%s%#x" % (ins.mnemonic, holder, operands[1].mem.disp,
                                                     KEY, regs[holder] - base
                                                     + operands[1].mem.disp))
            if ins.mnemonic.startswith("ldr"):
                regs.pop(ins.reg_name(operands[0].reg), None)
        elif ins.mnemonic in ("adds", "add") and len(operands) == 3 and operands[2].type == 2:
            dst, src = ins.reg_name(operands[0].reg), ins.reg_name(operands[1].reg)
            if regs.get(src) is not None:
                regs[dst] = regs[src] + operands[2].imm
        elif ins.mnemonic in ("adds", "add", "subs", "sub") and len(operands) == 2 \
                and operands[1].type == 2:
            dst = ins.reg_name(operands[0].reg)
            if regs.get(dst) is not None:
                delta = operands[1].imm
                regs[dst] = regs[dst] + (delta if ins.mnemonic in ("adds", "add") else -delta)
        elif ins.mnemonic in ("subs", "sub") and len(operands) == 3 and operands[2].type == 2:
            dst, src = ins.reg_name(operands[0].reg), ins.reg_name(operands[1].reg)
            if regs.get(src) is not None:
                regs[dst] = regs[src] - operands[2].imm
        elif ins.mnemonic in ("adds", "add") and len(operands) == 3 and operands[2].type == 1:
            dst = ins.reg_name(operands[0].reg)
            if regs.get(ins.reg_name(operands[1].reg)) is not None \
                    or regs.get(ins.reg_name(operands[2].reg)) is not None:
                regs[dst] = None
                accesses.append("INDEXED base + register (%s)" % ins.op_str)
        elif ins.mnemonic in LDMS and len(operands) >= 2 and operands[0].type == 1:
            holder = ins.reg_name(operands[0].reg)
            loaded = [operand for operand in operands[1:] if operand.type == 1]
            if regs.get(holder) is not None and start <= regs[holder] - base < end:
                accesses.append("%s %s +0x0 = %#x (%d bytes)"
                                % (ins.mnemonic, holder, regs[holder] - base, 4 * len(loaded)))
            for operand in loaded:
                regs.pop(ins.reg_name(operand.reg), None)
        elif ins.mnemonic in CALLS:
            for clobbered in ("r0", "r1", "r2", "r3", "r12", "lr"):
                regs.pop(clobbered, None)
        elif ins.mnemonic in LISTS:
            for operand in operands:
                if operand.type == 1:
                    regs.pop(ins.reg_name(operand.reg), None)
        elif operands and operands[0].type == 1 and ins.mnemonic not in READS_FIRST:
            regs.pop(ins.reg_name(operands[0].reg), None)
        lines.append(text)
        if ins.mnemonic == "bx" and ins.op_str == "lr":
            break
        if ins.mnemonic in ("pop", "ldm") and "pc" in ins.op_str:
            break
    return lines, accesses


def trace(rom: bytes, start: int, end: int, md=None) -> dict:
    md = disassembler() if md is None else md
    cited = search.loaders(rom, start, end)
    literals = []
    covered: set[int] = set()
    counts = {"sites": 0, "in_range_sites": 0, "field_sites": 0, "indexed_sites": 0,
              "pass_only_sites": 0}
    for literal, data in sorted(cited["hits"].items(), key=lambda item: -len(item[1]["sites"])):
        sites = []
        for site in data["sites"]:
            lines, accesses = site_trace(rom, site, start, end, md)
            counts["sites"] += 1
            counts["in_range_sites"] += start <= site < end
            if any(a.startswith("INDEXED") for a in accesses):
                counts["indexed_sites"] += 1
            elif any(KEY in a for a in accesses):
                counts["field_sites"] += 1
            else:
                counts["pass_only_sites"] += 1
            for access in accesses:
                if KEY not in access:
                    continue
                access, _, width_text = access.partition("(")
                where = int(access.split(KEY)[1], 16)
                if start <= where < end:
                    width = int(width_text.split()[0]) if width_text else WIDTHS[access.split()[0]]
                    covered.update(range(where, min(where + width, end)))
            sites.append({"site": site, "lines": lines, "accesses": accesses})
        literals.append({"literal": literal, "target": data["value"], "sites": sites})
    return {"start": start, "end": end, "loaders": cited["loaders"], "literals": literals,
            "counts": counts, "bytes": len(covered)}


def report(rom: bytes, start: int, end: int, verbose: bool = False) -> list[str]:
    measured = trace(rom, start, end)
    lines = ["range %#x..%#x  loaders=%d literals=%d" % (start, end, measured["loaders"],
                                                        len(measured["literals"]))]
    for entry in measured["literals"]:
        lines.append("\nliteral %#06x = %#010x  %d site(s)" % (entry["literal"],
                                                              entry["target"] + ROM_BASE,
                                                              len(entry["sites"])))
        for site in entry["sites"]:
            lines.append("  site %08X%s -> %s"
                         % (site["site"] + ROM_BASE,
                            " IN-RANGE" if start <= site["site"] < end else "",
                            "; ".join(site["accesses"]) or "(no tracked access)"))
            if verbose:
                lines += ["      " + line for line in site["lines"]]
    counts = measured["counts"]
    lines.append("\nsummary sites=%d in_range_sites=%d field_sites=%d indexed_sites=%d "
                 "pass_only_sites=%d" % (counts["sites"], counts["in_range_sites"],
                                         counts["field_sites"], counts["indexed_sites"],
                                         counts["pass_only_sites"]))
    lines.append("summary bytes_read_at_a_constant_offset=%d of %d (%.2f %%)"
                 % (measured["bytes"], end - start,
                    100.0 * measured["bytes"] / (end - start)))
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--range", nargs=2, action="append", metavar=("START", "END"),
                        required=True, type=lambda text: int(text, 16))
    parser.add_argument("--verbose", action="store_true", help="print every decoded instruction")
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    for start, end in args.range:
        for line in report(rom, start, end, args.verbose):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
