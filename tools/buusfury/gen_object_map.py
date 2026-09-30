"""Build the committed object-offset map for *(0x08054FBC + 0x14).

This lives under tools/ rather than build/, because build/ is gitignored and a
generator that is not committed cannot make the census reproducible."""
import json, pathlib, sys
sys.path.insert(0, r"C:\Dev\buusfury-decomp\tools")
import capstone
from buusfury import analysis as A, gba

data = pathlib.Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - Buu's Fury (U).gba").read_bytes()
BASE = gba.ROM_BASE
GLOBAL = 0x08054FBC

def u32(a):
    return int.from_bytes(data[a - BASE:a - BASE + 4], "little")

def chain(entry, limit=0x600):
    seen, out, bl, pending = {}, [], [], [entry]
    while pending:
        a = pending.pop()
        if a in seen or not gba.in_cartridge(a):
            continue
        for ins in A.MD_THUMB.disasm(data[a - BASE:a - BASE + limit], a):
            if ins.address in seen:
                break
            seen[ins.address] = ins.size
            out.append(ins)
            mn, ops = ins.mnemonic, ins.op_str
            imm = ins.operands[0].imm & 0xFFFFFFFF if (ins.operands and ins.operands[0].type == capstone.arm.ARM_OP_IMM) else None
            if mn in ("bl", "blx") and imm is not None:
                bl.append((ins.address, imm & ~1)); continue
            if mn == "b" and imm is not None:
                pending.append(imm); break
            if mn.startswith(("bne","beq","bcc","bcs","bmi","bpl","bvs","bvc","bhi","bls","bge","blt","bgt","ble")) and imm is not None:
                pending.append(imm); continue
            if mn == "bx" or (mn.startswith("pop") and "pc" in ops) or (mn.startswith("ldr") and ops.startswith("pc")):
                break
    out.sort(key=lambda i: i.address)
    return out, bl

seeds = {a & ~1 for a, _i, _w in A.EXTERNAL_CODE_SEEDS}
for tbl, n in ((0x080554C0, 31), (0x08055098, 266), (0x08055508, 13)):
    for i in range(n):
        v = u32(tbl + i * 4)
        if gba.in_cartridge(v) and v > 0x08000100:
            seeds.add(v & ~1)
funcs, done = {}, set()
for _ in range(4):
    new = 0
    for s in sorted(seeds):
        if s in done:
            continue
        done.add(s)
        out, bl = chain(s)
        if out:
            funcs[s] = out
        for _site, tgt in bl:
            if tgt not in seeds and gba.in_cartridge(tgt):
                seeds.add(tgt); new += 1
    if not new:
        break

def dst(ins):
    if ins.operands and ins.operands[0].type == capstone.arm.ARM_OP_REG:
        return ins.reg_name(ins.operands[0].reg)
    return None

def memop(ins):
    for op in ins.operands:
        if op.type == capstone.arm.ARM_OP_MEM:
            return op.mem
    return None

def imm_of(ins):
    if ins.operands and ins.operands[-1].type == capstone.arm.ARM_OP_IMM:
        return ins.operands[-1].imm
    return None

WIDTH = {"ldrb": 1, "strb": 1, "ldrh": 2, "strh": 2, "ldr": 4, "str": 4,
         "ldrsb": 1, "ldrsh": 2}
POINTER_LIKE_MIN = 0x02000000

# ---- enumerate the object-user SITES (3-instruction window, as before) ----
sites = []
writers = []
for entry, insns in funcs.items():
    for i, x in enumerate(insns):
        if not x.mnemonic.startswith("ldr"):
            continue
        slot = A._literal_slot(x, "thumb")
        if slot is None or u32(slot) != GLOBAL:
            continue
        g = dst(x)
        if g is None:
            continue
        for w in insns[i + 1:i + 4]:
            m = memop(w)
            if m is None or w.reg_name(m.base) != g:
                continue
            if m.disp != 0x14:
                continue
            if w.mnemonic.startswith("ldr"):
                obj = dst(w)
                if obj is not None:
                    sites.append({"function": f"0x{entry:08X}",
                                  "seed": f"0x{x.address:08X}",
                                  "deref": f"0x{w.address:08X}",
                                  "object_register": obj,
                                  "index": insns.index(w) + 1,
                                  "insns": insns})
            else:
                writers.append({"function": f"0x{entry:08X}",
                                "seed": f"0x{x.address:08X}",
                                "store": f"0x{w.address:08X}"})
            break

# ---- track each site's object register and collect accesses ----
records = []
for s in sites:
    insns, obj = s["insns"], s["object_register"]
    derived = {obj}
    for x in insns[s["index"]:]:
        d = dst(x)
        m = memop(x)
        if m is not None and x.reg_name(m.base) in derived and x.mnemonic.startswith(("ldr", "str")):
            records.append({
                "function": s["function"], "site": f"0x{x.address:08X}",
                "offset": m.disp, "indexed": bool(m.index),
                "width": WIDTH.get(x.mnemonic, 0),
                "access": "write" if x.mnemonic.startswith("str") else "read",
                "mnemonic": x.mnemonic,
            })
        if d is not None:
            srcs = [x.reg_name(o.reg) for o in x.operands[1:] if o.type == capstone.arm.ARM_OP_REG]
            if any(a in derived for a in srcs) and x.mnemonic in ("adds", "mov", "movs", "subs", "lsrs", "lsls"):
                derived.add(d)

offset_map = {}
for r in records:
    offset_map.setdefault(str(r["offset"]), []).append(r)

# ---- constructor search: SECOND shape, the global base held in a register ----
wide_writers = []
for entry, insns in funcs.items():
    for i, x in enumerate(insns):
        if not x.mnemonic.startswith("ldr"):
            continue
        slot = A._literal_slot(x, "thumb")
        if slot is None or u32(slot) != GLOBAL:
            continue
        g = dst(x)
        if g is None:
            continue
        for y in insns[i + 1:i + 13]:
            m = memop(y)
            if (y.mnemonic.startswith("str") and m is not None
                    and y.reg_name(m.base) == g and m.disp == 0x14):
                wide_writers.append(f"0x{y.address:08X}")

offsets = sorted(int(k) for k in offset_map)
hi = offsets[-1] if offsets else None
neighbourhood = [o for o in offsets if 0x40 <= o <= 0x80]

artifact = {
    "generated_by": "tools/buusfury/gen_object_map.py",
    "object_expression": "*(0x08054FBC + 0x14)",
    "global_struct": "0x08054FBC",
    "method": (
        "walk every reachable function; find `ldr rG,[pc,#N]` whose literal is "
        "0x08054FBC; require a ldr of [rG,#0x14] within three instructions; then track "
        "the register the object lands in FORWARD through simple copies and adds, and "
        "record every ldr/str whose base is in that derived set"
    ),
    "user_sites": [{k: v for k, v in s.items() if k != "insns"} for s in sites],
    "user_site_count": len(sites),
    "offset_map": offset_map,
    "distinct_offsets": offsets,
    "highest_proven_offset": hi,
    "highest_proven_offset_hex": f"0x{hi:03X}" if hi is not None else None,
    "accesses_in_the_flag_neighbourhood_0x40_to_0x80": [
        {"offset": f"0x{o:03X}", "count": len(offset_map[str(o)])} for o in neighbourhood
    ],
    "access_widths": {str(w): sum(1 for r in records if r["width"] == w)
                      for w in sorted({r["width"] for r in records})},
    "indexed_accesses": sum(1 for r in records if r["indexed"]),
    "constant_accesses": sum(1 for r in records if not r["indexed"]),
    "constructor_search": {
        "shape_1": {
            "signature": "ldr rG,[pc,#N] (literal 0x08054FBC) then ldr/str [rG,#0x14] within 3 instructions",
            "readers": len(sites),
            "writers": len(writers),
        },
        "shape_2": {
            "signature": "ldr rG,[pc,#N] (literal 0x08054FBC) then str [rG,#0x14] within 12 instructions, i.e. the global base held in a register",
            "writers": len(wide_writers),
            "sites": wide_writers[:20],
        },
        "conclusion": (
            "BOTH SHAPES FOUND ZERO WRITERS, so no constructor or allocation size was "
            "reached by either. The object pointer is never stored by any code path "
            "matching a global-literal load followed by a store to +0x14 within 12 "
            "instructions. The allocation SIZE REMAINS UNRECOVERABLE, and the object may "
            "be built through a thunk, a call return, or a path where the global base is "
            "obtained another way."
        ),
    },
    "flag_array_bound_status": (
        "UNRESOLVED AND UNIMPROVED. The census found no access in +0x40..+0x80 at all "
        "through the tracked register, so no first-field-after-the-array, no bounded "
        "loop and no copy extent was established. The upper bound of the flag array at "
        "base + 0x55 remains not derivable."
    ),
    "census_is_a_lower_bound": (
        "This census is a LOWER BOUND on the object's field usage, not a complete map. "
        "Registers are tracked only through simple copies and adds, so a routine that "
        "reaches the object by another route, or that reloads it into a register this "
        "walk did not derive, contributes no offsets. Absence of an offset here is NOT "
        "evidence that the offset is unused."
    ),
    "exact_size_proven": False,
    "verdict": "object offset map committed as a lower bound; size and flag-array bound remain unresolved",
}
out = pathlib.Path('config/object_layout.json')
out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
               encoding='utf-8', newline='\n')
print(f"user sites            : {len(sites)}")
print(f"site-level writers    : {len(writers)}")
print(f"wide-shape writers    : {len(wide_writers)}")
print(f"distinct offsets      : {[hex(o) for o in offsets]}")
print(f"highest proven offset : {artifact['highest_proven_offset_hex']}")
print(f"0x40..0x80 offsets    : {[hex(o) for o in neighbourhood]}")
print(f"wrote {out}")
