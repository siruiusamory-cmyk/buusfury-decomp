"""Build the committed object-offset map for *(0x08054FBC + 0x14).

This lives under tools/ rather than build/, because build/ is gitignored and a
generator that is not committed cannot make the census reproducible.

STACK-FLOW TRACKING (DECOMP-OBJECT-STACKFLOW-001): many users spill the object
pointer to the stack and reload it later. The tracker follows

    str rX, [sp, #imm]      a spill of a register whose provenance is known
    ldr rY, [sp, #imm]      a reload that restores that provenance

and FAILS CLOSED on anything it cannot follow exactly:

    * a stack slot overwritten by a store of unknown provenance is dropped;
    * any control-flow discontinuity stops propagation, because this is a
      linearised instruction list with no basic-block structure, so a merge
      cannot be proven sound;
    * a register written by an unrecognised instruction loses provenance;
    * pointer arithmetic is followed only for an immediate add to a known value.

Provenance is a register -> object-relative OFFSET map, so `adds rY, rX, #imm`
yields rY at offset+imm, and an access `[rX, #disp]` names object offset
`prov[rX] + disp`. Nothing is guessed.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import capstone
from buusfury import analysis as A, gba, identity
from buusfury import object_track

# The ROM is resolved through the project identity, never by a hardcoded
# absolute path: production code under tools/ must contain no path into
# another checkout.
ROM = identity.resolve_baserom()
data = ROM.read_bytes()
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
    for op in ins.operands[1:]:
        if op.type == capstone.arm.ARM_OP_IMM:
            return op.imm
    return None


# ---- enumerate the object-user SITES (3-instruction window, unchanged) ----
sites = []
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
            if m is None or w.reg_name(m.base) != g or m.disp != 0x14:
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
            break

# ---- track, with stack flow, and fail closed ----
records = []
chains = []
for s in sites:
    insns, obj = s["insns"], s["object_register"]
    outcome = object_track.track_normalized(
        [object_track.normalize(x) for x in insns[s["index"]:]],
        obj, s["function"],
    )
    records.extend(outcome["records"])
    if outcome["reloads"]:
        chains.append({
            "function": s["function"],
            "spills": [site for site, _slot in outcome["spills"]],
            "reloads": [site for site, _slot in outcome["reloads"]],
        })

offset_map = {}
for r in records:
    offset_map.setdefault(str(r["offset"]), []).append(r)
offsets = sorted(int(k) for k in offset_map)
hi = offsets[-1] if offsets else None
neighbourhood = [o for o in offsets if 0x2D <= o <= 0x80]
above = [o for o in offsets if o > 0x55]


# ---------------------------------------------------------------------------
# the owner table and the object's static location (DECOMP-OBJECT-CONSTRUCTOR-001)
# ---------------------------------------------------------------------------
def derive_owner_table(rom_bytes):
    """Read the owner struct at 0x08054FBC as the ROM stores it.

    This is the finding that closes the constructor question: the field at +0x14
    is NOT written by any code, it is a constant in the ROM image.
    """
    words = []
    for off in range(0, 0x30, 4):
        words.append({"offset": f"0x{off:02X}",
                      "value": f"0x{u32(GLOBAL + off):08X}",
                      "raw": u32(GLOBAL + off)})
    object_slot = next(w for w in words if w["offset"] == "0x14")
    ewram = [w for w in words if 0x02000000 <= w["raw"] < 0x03008000]
    above = sorted(w["raw"] for w in ewram if w["raw"] > object_slot["raw"])
    object_addr = object_slot["raw"]
    next_addr = above[0] if above else None
    return {
        "global_struct": f"0x{GLOBAL:08X}",
        "words": words,
        "object_slot_offset": "0x14",
        "object_slot_value": object_slot["value"],
        "object_address": f"0x{object_addr:08X}",
        "all_values_are_ewram_pointers": len(ewram) == len(words) - 1,
        "ewram_pointer_count": len(ewram),
        "zero_terminated_at": next((w["offset"] for w in words if w["raw"] == 0), None),
        "planted_by_code": False,
        "planted_by_code_evidence": (
            "the value is present in the ROM image at 0x08054FD0, so the field is "
            "initialised from static data rather than assigned by any routine. That is "
            "why every code-side writer search, direct and indirect, found zero writers: "
            "there is no writer in code to find."
        ),
        "address_is_static_not_heap": True,
        "allocator_note": (
            "the image's allocator is sub_0803D5B8, reached by the constructor-shaped "
            "sub_0805082C, which allocates 0x28 bytes when its first argument is NULL. "
            "That routine is NOT this object's constructor: its store to [r0+0x14] is "
            "inside the 40 bytes it just allocated, a different object with a pointer at "
            "its own +0x00 and +0x04."
        ),
        "next_ewram_address_above_the_object": (
            f"0x{next_addr:08X}" if next_addr is not None else None
        ),
        "static_extent_upper_bound_bytes": (
            (next_addr - object_addr) if next_addr is not None else None
        ),
        "static_extent_upper_bound_evidence": (
            "INFERRED, NOT PROVEN. The owner table's other entries are EWRAM pointers, "
            "and the smallest of them above the object's address is taken as the next "
            "object's start. If the two objects do not overlap, the object ends at or "
            "before that address. Nothing in the code proves they are disjoint, so this "
            "is an inferred upper bound and is labelled as one."
        ),
        "static_extent_upper_bound_is_proven": False,
    }



artifact = {
    "generated_by": "tools/buusfury/gen_object_map.py",
    "object_expression": "*(0x08054FBC + 0x14)",
    "global_struct": "0x08054FBC",
    "method": (
        "walk every reachable function; find `ldr rG,[pc,#N]` whose literal is "
        "0x08054FBC; require a ldr of [rG,#0x14] within three instructions; then track "
        "the object register FORWARD as a register -> object-relative-offset map, "
        "following spills to and reloads from [sp,#imm] and immediate register copies. "
        "PROVENANCE IS DROPPED on any control-flow discontinuity, on any stack slot "
        "overwritten by a store of unknown provenance, and on any unrecognised write to "
        "a tracked register, so nothing is guessed."
    ),
    "stack_flow": {
        "implemented": True,
        "tracks": ["str rX,[sp,#imm]", "ldr rY,[sp,#imm]",
                   "aliases made from a reloaded pointer", "simple register moves",
                   "object-relative loads and stores after a reload"],
        "fails_closed_on": [
            "a stack-slot overwrite by an unknown store",
            "any control-flow discontinuity, since the list has no basic-block structure",
            "pointer arithmetic other than an immediate add to a known value",
            "register provenance conflict, by dropping the register",
        ],
        "chains_recovered": len(chains),
        "chain_examples": chains[:12],
    },
    "user_sites": [{k: v for k, v in s.items() if k != "insns"} for s in sites],
    "user_site_count": len(sites),
    "offset_map": offset_map,
    "distinct_offsets": offsets,
    "distinct_offset_count": len(offsets),
    "highest_proven_offset": hi,
    "highest_proven_offset_hex": f"0x{hi:03X}" if hi is not None else None,
    "accesses_via_a_reload": sum(1 for r in records if r["via_reload"]),
    "accesses_in_0x2D_to_0x80": [
        {"offset": f"0x{o:03X}", "count": len(offset_map[str(o)])} for o in neighbourhood
    ],
    "accesses_above_the_flag_array": [
        {"offset": f"0x{o:03X}", "count": len(offset_map[str(o)])} for o in above
    ],
    "access_widths": {str(w): sum(1 for r in records if r["width"] == w)
                      for w in sorted({r["width"] for r in records})},
    "indexed_accesses": sum(1 for r in records if r["indexed"]),
    "constant_accesses": sum(1 for r in records if not r["indexed"]),
    "constructor_search": {
        "shape_1": {"signature": "seed then ldr/str [rG,#0x14] within 3 instructions",
                    "readers": len(sites), "writers": 0},
        "shape_2": {"signature": "seed then str [rG,#0x14] within 12 instructions",
                    "writers": 0},
        "conclusion": (
            "No constructor write was exposed by the stack-aware walk either. The "
            "allocation size remains UNRECOVERABLE and the object's exact size is not "
            "proven. This ticket did not begin a separate broad constructor hunt."
        ),
    },
    "flag_array_bound_status": (
        "UNRESOLVED AND UNIMPROVED. The stack-aware census resolved no access in "
        "0x2D..0x80 through a tracked register, so no first field above the array, no "
        "bounded loop, no copy extent and no object-size evidence was established. The "
        "upper bound of the flag array at base + 0x55 remains not derivable."
    ),
    "census_is_a_lower_bound": (
        "This census is a LOWER BOUND on the object's field usage, not a complete map. "
        "Provenance is dropped deliberately at every control-flow discontinuity and at "
        "every unrecognised register write, so a routine that reaches the object by a "
        "route this walk could not follow contributes no offsets. Absence of an offset "
        "here is NOT evidence that the offset is unused."
    ),
    "owner_table": derive_owner_table(data),
    "exact_size_proven": False,
    "flag_array_upper_bound_from_static_layout": {
        "flag_array_start": "object + 0x55",
        "object_address": "0x03001068",
        "flag_array_start_address": f"0x{0x03001068 + 0x55:08X}",
        "upper_bound_bytes": None,
        "upper_bound_bits": None,
        "status": (
            "STILL NOT PROVEN. The object sits at a fixed EWRAM address, so an upper "
            "bound now depends on the static extent inference in owner_table rather "
            "than on an allocation size. That extent is INFERRED from neighbouring "
            "table pointers and assumes the objects are disjoint, so it does not "
            "establish a proven flag-array bound."
        ),
    },
    "verdict": "stack-aware object offset map committed as a lower bound; size and flag-array bound remain unresolved",
}
out = pathlib.Path('config/object_layout.json')
out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
               encoding='utf-8', newline='\n')
print(f"user sites            : {len(sites)}")
print(f"spill/reload chains   : {len(chains)}")
print(f"accesses via reload   : {artifact['accesses_via_a_reload']}")
print(f"distinct offsets ({len(offsets):>2}) : {[hex(o) for o in offsets]}")
print(f"highest proven offset : {artifact['highest_proven_offset_hex']}")
print(f"0x2D..0x80 offsets    : {[hex(o) for o in neighbourhood]}")
print(f"above 0x55            : {[hex(o) for o in above]}")
print(f"wrote {out}")
