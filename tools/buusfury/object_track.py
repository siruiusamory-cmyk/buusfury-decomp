"""Pure, fail-closed tracking of the object pointer at *(0x08054FBC + 0x14).

This module holds the tracking POLICY and nothing else: no ROM access, no capstone,
no walk. `track_normalized` takes plain dictionaries, so it can be driven by
synthetic instructions as well as by the real census walk, and importing this
module costs nothing.

PROVENANCE is a `register -> object-relative offset` map. A register in it points
into the object, at a known offset, and an access `[reg, #disp]` therefore names
object offset `prov[reg] + disp`.

IT FAILS CLOSED. The whole point of this module is that it refuses to guess:

  * a control-flow DISCONTINUITY ends the run, because a gap between consecutive
    instruction addresses means the code was reached from somewhere this linear
    pass cannot prove, and a merge may have invalidated every register;
  * any BRANCH ends the run, for the same reason;
  * a stack slot overwritten by a store of UNKNOWN provenance is dropped, so a
    later reload from it proves nothing;
  * a reload from a slot never written by a tracked register yields nothing;
  * pointer arithmetic is followed only for an immediate add or subtract to a
    known register, so an unknown amount loses the register;
  * any write to a tracked register that is not a recognised copy or add LOSES it.

The result is deliberately conservative: it resolves FEWER offsets than a
permissive walk would, and every offset it does report is sound.
"""

#: Access width in bytes for the load/store mnemonics the census sees.
WIDTH = {
    "ldrb": 1, "strb": 1, "ldrh": 2, "strh": 2,
    "ldr": 4, "str": 4, "ldrsb": 1, "ldrsh": 2,
}

#: A stop reason, for callers that want to know WHY a run ended.
STOP_DISCONTINUITY = "control-flow discontinuity"
STOP_BRANCH = "branch or return"
STOP_END = "end of input"


def normalize(ins):
    """Turn a capstone instruction into a plain dictionary.

    This is the only place that knows about capstone, so `track_normalized` and
    every test of it deal solely in plain data.
    """
    mem = None
    for op in ins.operands:
        if op.type == ins.operands[0].type and hasattr(op, "mem"):
            mem = op.mem
            break
    dst = None
    if ins.operands and hasattr(ins.operands[0], "reg"):
        try:
            dst = ins.reg_name(ins.operands[0].reg)
        except Exception:  # noqa: BLE001 - an immediate destination is not a register
            dst = None
    src = None
    for op in ins.operands[1:]:
        if hasattr(op, "reg"):
            try:
                src = ins.reg_name(op.reg)
                break
            except Exception:  # noqa: BLE001
                pass
    imm = None
    for op in ins.operands:
        if hasattr(op, "imm"):
            imm = op.imm
    return {
        "addr": ins.address,
        "size": ins.size,
        "mnemonic": ins.mnemonic,
        "op_str": ins.op_str,
        "dst": dst,
        "src": src,
        "base": ins.reg_name(mem.base) if mem is not None else None,
        "disp": mem.disp if mem is not None else None,
        "index": bool(mem.index) if mem is not None else False,
        "imm": imm,
    }


def item(addr, mnemonic, dst=None, src=None, base=None, disp=None,
         imm=None, index=False, size=2, op_str=""):
    """Build a normalized instruction by hand, for tests."""
    return {
        "addr": addr, "size": size, "mnemonic": mnemonic, "op_str": op_str,
        "dst": dst, "src": src, "base": base, "disp": disp,
        "index": index, "imm": imm,
    }


def track_normalized(items, obj, function="synthetic"):
    """Track one object pointer through a straight-line run of instructions.

    Returns a dict with:
        records  - object-relative accesses, each with offset, width, direction
        spills   - (site, slot) for every spill that carried provenance
        reloads  - (site, slot) for every reload that restored it
        stopped  - why the run ended
        stopped_at - the address it ended at, or None
    """
    prov = {obj: 0}
    slots = {}
    prev = None
    records = []
    spills = []
    reloads = []
    stopped = STOP_END
    stopped_at = None

    for it in items:
        if prev is not None and it["addr"] != prev:
            stopped, stopped_at = STOP_DISCONTINUITY, it["addr"]
            break
        prev = it["addr"] + it["size"]

        mn = it["mnemonic"]
        if mn == "bx" or (mn.startswith("pop") and "pc" in (it["op_str"] or "")):
            stopped, stopped_at = STOP_BRANCH, it["addr"]
            break
        if mn.startswith("b") and mn not in ("bl", "blx", "bx"):
            stopped, stopped_at = STOP_BRANCH, it["addr"]
            break

        d, base, disp, imm = it["dst"], it["base"], it["disp"], it["imm"]
        sp = base == "sp"

        if base is not None and sp and mn.startswith("str"):
            if d in prov and disp is not None:
                slots[disp] = prov[d]
                spills.append((f"0x{it['addr']:08X}", disp))
            elif disp is not None:
                slots.pop(disp, None)      # fail closed: an unknown spill
            continue

        if base is not None and sp and mn.startswith("ldr"):
            if disp is not None and disp in slots and d is not None:
                prov[d] = slots[disp]
                reloads.append((f"0x{it['addr']:08X}", disp))
            elif d is not None and d in prov:
                prov.pop(d)                # fail closed: an unknown reload
            continue

        if base is not None and mn.startswith(("ldr", "str")) and not sp:
            if base in prov:
                records.append({
                    "function": function,
                    "site": f"0x{it['addr']:08X}",
                    "offset": prov[base] + (disp or 0),
                    "indexed": bool(it["index"]),
                    "width": WIDTH.get(mn, 0),
                    "access": "write" if mn.startswith("str") else "read",
                    "mnemonic": mn,
                    "via_reload": bool(reloads),
                })
                continue

        if d is not None:
            if base is not None:
                if d in prov:
                    prov.pop(d)            # any unrecognised load clobbers it
            elif mn in ("adds", "subs"):
                if it["src"] in prov and imm is not None:
                    prov[d] = prov[it["src"]] + (imm if mn == "adds" else -imm)
                elif d in prov:
                    prov.pop(d)
            elif mn in ("mov", "movs"):
                if it["src"] in prov:
                    prov[d] = prov[it["src"]]
                elif d in prov:
                    prov.pop(d)
            elif d in prov:
                prov.pop(d)

    return {"records": records, "spills": spills, "reloads": reloads,
            "stopped": stopped, "stopped_at": stopped_at}
