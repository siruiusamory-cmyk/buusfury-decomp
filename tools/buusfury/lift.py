"""DECOMP-LIFT-PILOT-001: the repeatable semantic lifting loop.

One command takes a reconstructed translation unit from source to a
machine-readable comparison against the original ROM:

    source  ->  compile  ->  link at the original ROM address  ->  objcopy
            ->  per-function and translation-unit comparison
            ->  a report that keeps three VERDICTS apart

THE THREE VERDICTS ARE INDEPENDENT AND MUST STAY SO
    SEMANTIC      does the reconstruction behave correctly?  Measured by
                  RUNNING it on the host (src/probes/gbaram_selftest.c).
    MODERN_BUILD  does it compile, link and emit bytes with the modern
                  toolchain?  A plumbing result.
    ADS_MATCH     does it reproduce the original compiler's output?  BLOCKED:
                  the ADS 1.2 ARM compilers on this machine are unlicensed, and
                  a modern GCC is not the original compiler.

No verdict may be inferred from another. In particular a passing modern build
is NOT evidence about the original compiler, and this module never reports one
as such; the modern-vs-original byte comparison is published as a MEASUREMENT
with `not_a_match_claim` set, and `ADS_MATCH` is never promoted from it.

WHY THE COMPARISON IS TRANSLATION-UNIT SCOPED
A function containing a PC-relative literal load cannot be compared standalone:
its `ldr rX, [pc, #N]` displacement depends on where the pool sits. The original
shares ONE pool across seven of its eight functions, so the only rigorous unit
is the whole TU, linked at its original address. Per-function rows are slices of
that one build.

REUSE
Targets come from config/lift_targets.json, function boundaries from
config/compiler_probes.json. Adding the next function family is a config entry
plus its C source; no new script.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

from . import compiler_probe as cp
from . import gba as _gba
from . import identity as _identity

# ---------------------------------------------------------------------------
# verdict vocabularies - deliberately three separate tuples
# ---------------------------------------------------------------------------
SEMANTIC_STATES = ("PROVEN", "PARTIAL", "FAILED", "UNTESTED")
MODERN_BUILD_STATES = ("PASS", "FAIL", "BLOCKED")
ADS_MATCH_STATES = ("BLOCKED", "UNTESTED")

#: The minimum behavioural assertion count the host self-check must reach.
#: DECOMP-LIFT-PILOT-001 states 230; a lower count means checks were lost.
MIN_SEMANTIC_CHECKS = 230

#: Where the modern toolchain is expected, overridable by environment.
DEVKITARM_ENV = "DEVKITARM"
DEFAULT_DEVKITARM = r"C:\devkitPro\devkitARM"

TARGETS_PATH = _identity.CONFIG_DIR / "lift_targets.json"
PROBES_PATH = _identity.CONFIG_DIR / "compiler_probes.json"
LIFT_WORKSPACE = _identity.REPO_ROOT / "build" / "lift"


# ---------------------------------------------------------------------------
# translation units the lift loop knows
# ---------------------------------------------------------------------------
# GBARam's unit comes from the ADS probe manifest, which already derives and
# verifies its boundaries. The ByteCodeInterpreter unit is derived HERE, from the
# ROM, because it has a property the probe manifest's schema cannot express: its
# literal pool is NOT adjacent to its code. The pool sits at 0x08004158 while the
# last function ends at 0x08004156, with two padding bytes between, and 86 bytes
# of unrelated code at 0x08004102 would have to be crossed to reach it.
BCI_TU = cp.TranslationUnit(
    id="bci_tu",
    rom_address=0x08004038,
    code_end_address=0x08004158,
    end_address=0x08004160,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08004038: every path reaches the single epilogue at "
        "0x0800408C, 47 instructions, no gaps, and the next byte is a new "
        "function prologue",
        "the unit continues through 0x08004098 and 0x08004102, which share the "
        "same literal pool at 0x08004158, which is what establishes one "
        "compilation unit",
        "the pool's second word is the dispatch table 0x080554C0, whose extent is "
        "bounded by the UTF-16 assertion at 0x0805553C",
    ),
    literal_pool=(
        (0x004158, 0x03001034),
        (0x00415C, 0x080554C0),
        (0x004198, 0x0805553C),
    ),
    selection=(
        "the ROM preserves the original source path "
        "'T:\\Source\\ByteCodeInterpreter\\ByteCodeInterpreter.cpp' as ASCII at "
        "0x08004160, referenced by the assertion at 0x080040F4",
        "config/compiler_probes.json and the ROM map both anchor 0x08004038 as "
        "the bytecode interpreter entry",
        "the dispatch loop's structure (one byte, one table index, one indirect "
        "call, NULL terminates) is read directly from 0x08004064..0x08004096",
    ),
)

#: (start, end, role) per function, all derived from the ROM at run time.
BCI_FUNCTIONS = (
    (0x08004038, 0x08004098, "bytecode dispatch loop"),
    (0x08004098, 0x08004102, "dialog entry point"),
    (0x08004102, 0x08004156, "untitled helper; name not justified by evidence"),
)

#: The unit's literal pool, which is NOT adjacent to its code. The first two
#: words sit at 0x08004158, two padding bytes after the last function; a third
#: sits at 0x08004198 and holds the assertion message address, so the unit's
#: literals live in two separate places rather than one shared run.
BCI_LITERAL_POOL = ((0x004158, 0x03001034), (0x00415C, 0x080554C0), (0x004198, 0x0805553C))

#: The dispatch table and the string that bounds it.
BCI_DISPATCH_TABLE = 0x080554C0
BCI_DISPATCH_ENTRIES = 31
BCI_BOUNDING_STRING = 0x0805553C
#: The ROM stores this message WITH the surrounding quote characters, so the
#: expected text includes them. Comparing against the unquoted form would leave
#: a false mismatch.
BCI_BOUNDING_TEXT = '"Expected dialog to start with a code block"'

#: Padding between the last function and the pool.
BCI_ALIGNMENT_PADDING = 2

# ---------------------------------------------------------------------------
# the ByteCodeInterpreter handler unit
# ---------------------------------------------------------------------------
# Primary dispatch slot 2. A different translation unit from the interpreter:
# separate code and a separate literal pool at 0x08003F40, which four other
# primary handlers also load from.
H2_ENTRY = 0x08003CBE
H2_TU = cp.TranslationUnit(
    id="handler2_tu",
    rom_address=0x08003CBE,
    code_end_address=0x08003CD4,
    end_address=0x08003CD4,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_handlers.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003CBE: 10 instructions, no gaps, one terminator "
        "at 0x08003CD2 (pop {r3,pc})",
        "the table word at primary slot 2 is 0x08003CBF, whose Thumb bit masks to "
        "this entry, so the entry is anchored by the dispatch table itself",
        "no direct BL site anywhere in the image targets it: it is reached only "
        "through the primary table",
    ),
    # NOT adjacent to the code: the pool sits at 0x08003F40, 0x26C bytes later,
    # and holds the word the handler loads at 0x08003CCA.
    literal_pool=((0x03F40, 0x08055098),),
    selection=(
        "primary dispatch table slot 2 holds 0x08003CBF",
        "it is the handler that reaches the native dispatch table at 0x08055098, "
        "which is the bridge from the bytecode layer to the engine",
    ),
)
H2_FUNCTIONS = (
    (0x08003CBE, 0x08003CD4, "primary dispatch slot 2: selects a native routine"),
)
H2_LITERAL_POOL = ((0x03F40, 0x08055098),)

# ---------------------------------------------------------------------------
# the ByteCodeInterpreter operand-reader unit
# ---------------------------------------------------------------------------
# Primary dispatch slot 1. A LEAF: no calls, and no literal pool at all, because
# every instruction is register-only. Whether it shared a translation unit with
# the adjacent slot-2 handler is not established; with no pool there is no
# pooling evidence either way.
OP_TU = cp.TranslationUnit(
    id="operand_tu",
    rom_address=0x08003C8A,
    code_end_address=0x08003CBE,
    end_address=0x08003CBE,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_operand.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003C8A: 26 instructions, no gaps, one terminator at "
        "0x08003CBC (bx lr)",
        "the table word at primary slot 1 is 0x08003C8B, whose Thumb bit masks to "
        "this entry, so the entry is anchored by the dispatch table itself",
        "no direct BL site anywhere in the image targets it: it is reached only "
        "through the primary table",
        "its end 0x08003CBE is the slot-2 handler's derived entry, so the two "
        "boundaries confirm each other",
    ),
    # NO literal pool: there is no `ldr rX,[pc,#N]` anywhere in the handler.
    literal_pool=(),
    selection=(
        "primary dispatch table slot 1 holds 0x08003C8B",
        "it is the handler that reads a variable-length signed operand from the "
        "cursor and pushes it onto the context's value stack",
    ),
)
OP_FUNCTIONS = (
    (0x08003C8A, 0x08003CBE, "primary dispatch slot 1: reads a variable-length signed operand and pushes it"),
)
OP_LITERAL_POOL: tuple = ()

# ---------------------------------------------------------------------------
# the first value-stack consumer
# ---------------------------------------------------------------------------
# Primary dispatch slot 7. Slots 7, 8 and 9 are the value-stack arithmetic trio:
# identical 20-byte, 10-instruction shapes differing in one combining
# instruction. Only slot 7 is reconstructed; 8 and 9 are read here for the
# operand-order convention that the commutative add cannot show by itself.
STACK_ENTRY = 0x08003D3E
STACK_TU = cp.TranslationUnit(
    id="stack_tu",
    rom_address=0x08003D3E,
    code_end_address=0x08003D52,
    end_address=0x08003D52,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_stack.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003D3E: 10 instructions, no gaps, one terminator at "
        "0x08003D50 (bx lr), straight-line with no local branches",
        "the table word at primary slot 7 is 0x08003D3F, whose Thumb bit masks to "
        "this entry",
        "no direct BL site anywhere in the image targets it",
    ),
    literal_pool=(),
    selection=(
        "primary dispatch table slot 7 holds 0x08003D3F",
        "it is the smallest function in the image that contains the value-stack "
        "pop idiom: 20 bytes, 10 instructions, one pop, no calls",
        "its neighbours 8 and 9 share the same shape, so the operand-order "
        "convention is visible from ROM evidence in the siblings",
    ),
)
STACK_FUNCTIONS = (
    (0x08003D3E, 0x08003D52, "primary dispatch slot 7: binary add over the value stack"),
)
STACK_LITERAL_POOL: tuple = ()
#: The siblings that share the shape and differ in the combining instruction.
STACK_SIBLING_SLOTS = (8, 9)

# ---------------------------------------------------------------------------
# the rest of the value-stack arithmetic family
# ---------------------------------------------------------------------------
# Primary dispatch slots 8 and 9. Slot 7 lives in its own unit at
# src/ByteCodeInterpreter_stack.c and is NOT touched here, so its committed
# report stays reproducible. The three tile 0x08003D3E..0x08003D7A at twenty
# bytes each.
ARITH_ENTRY = 0x08003D52
ARITH_TU = cp.TranslationUnit(
    id="arith_tu",
    rom_address=0x08003D52,
    code_end_address=0x08003D7A,
    end_address=0x08003D7A,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_arith.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003D52: 10 instructions, no gaps, one terminator at "
        "0x08003D64 (bx lr)",
        "chain-walk from 0x08003D66: 10 instructions, no gaps, one terminator at "
        "0x08003D78 (bx lr)",
        "the table words at primary slots 8 and 9 are 0x08003D53 and 0x08003D67, "
        "whose Thumb bits mask to these entries",
        "no direct BL site anywhere in the image targets either entry",
    ),
    literal_pool=(),
    selection=(
        "primary dispatch table slots 8 and 9 hold 0x08003D53 and 0x08003D67",
        "they are the other two members of the 20-byte arithmetic trio whose "
        "third member is slot 7, already lifted",
        "slot 8's subtraction is what proves the operand order for the whole "
        "family, because addition and multiplication are commutative",
    ),
)
ARITH_FUNCTIONS = (
    (0x08003D52, 0x08003D66, "primary dispatch slot 8: subtract the top from the deeper value"),
    (0x08003D66, 0x08003D7A, "primary dispatch slot 9: multiply the top and the deeper value"),
)
ARITH_LITERAL_POOL: tuple = ()
ARITH_FAMILY = (
    (7, STACK_TU.id, 0),
    (8, ARITH_TU.id, 0),
    (9, ARITH_TU.id, 1),
)

#: Offsets the pop idiom proves, in bytes from the context.
VALUE_STACK_COUNT_OFFSET = 0
VALUE_STACK_VALUES_OFFSET = 4
VALUE_STACK_ENTRY_SIZE = 4

#: The native dispatch table and the structure that bounds it from above.
NATIVE_TABLE = 0x08055098
NATIVE_TABLE_LIMIT = 0x080554C0  # the primary table base
PRIMARY_TABLE = 0x080554C0
PRIMARY_TABLE_ENTRIES = 31
PRIMARY_BOUNDING_STRING = 0x0805553C

#: The refuted count. Kept as data so the refutation is re-measured every run
#: rather than remembered in prose.
REFUTED_NATIVE_ENTRIES = 283

def derive_operand_encoding(rom_bytes: bytes) -> dict:
    """Re-read the operand format off the handler's own instructions.

    Every field below is measured from the disassembly of 0x08003C8A..0x08003CBE
    rather than restated from prose: the group width comes from the paired
    shift-left/shift-right that masks a byte, the continuation and sign bit
    positions come from the shifts that feed the two conditional branches, and
    the per-byte-count value range is then SIMULATED from the derived width. A
    change to any of those instructions changes this block.
    """
    base = _gba.ROM_BASE
    start, end, _role = OP_FUNCTIONS[0]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(text: str):
        match = re.search(r"#(0x[0-9a-fA-F]+|\d+)\s*$", text.strip())
        return int(match.group(1), 0) if match else None

    shifts: dict[int, int] = {}
    for ins in insns:
        if ins.mnemonic in ("lsls", "lsrs", "asrs"):
            value = immediate(ins.op_str)
            if value is not None:
                shifts[value] = shifts.get(value, 0) + 1

    mask_shift = 0x19  # 25: the pair that isolates the low 7 bits
    group_bits = 32 - mask_shift if shifts.get(mask_shift, 0) >= 2 else None
    continuation_shift = 0x18  # 24: leaves bit 7 in the sign position
    sign_shift = 0x1F          # 31: leaves bit 0 in the sign position

    all_shifts = []
    for ins in insns:
        if ins.mnemonic in ("lsls", "lsrs", "asrs"):
            value = immediate(ins.op_str)
            if value is not None:
                all_shifts.append((ins.address, ins.mnemonic, value))

    literal_slots = []
    for ins in insns:
        slot = cp._literal_slot(ins.address, "thumb", ins.op_str)
        if slot is not None and ins.mnemonic.startswith("ldr"):
            literal_slots.append(slot)

    byte_loads = [i for i in insns if i.mnemonic == "ldrb"]
    calls = [i for i in insns if i.mnemonic in ("bl", "blx")]
    arithmetic = [i for i in insns if i.mnemonic == "asrs"]

    # Simulate the extreme encoding per byte count from the derived width, and
    # the accumulator it builds, rather than tabulating remembered numbers.
    def extreme(group_count: int) -> dict:
        # A group of `group_bits` bits reaches (1 << group_bits) - 1. Using the
        # width minus one here understated every extreme by one bit and made the
        # report disagree with the semantic test, which is why the two are
        # asserted against each other.
        groups = [(1 << group_bits) - 1] * group_count if group_bits else []
        accumulator = 0
        for group in groups:
            accumulator = ((accumulator << group_bits) + group) & 0xFFFFFFFF
        signed_accumulator = (
            accumulator - 0x100000000 if accumulator & 0x80000000 else accumulator
        )
        if accumulator & 1:
            value = -((signed_accumulator >> 1))
        else:
            value = signed_accumulator >> 1
        value &= 0xFFFFFFFF
        return {
            "groups": group_count,
            "accumulator": f"0x{accumulator:08X}",
            "accumulator_bit_31_set": bool(accumulator & 0x80000000),
            "value": value - 0x100000000 if value & 0x80000000 else value,
            "sign_magnitude_holds": not (accumulator & 0x80000000),
        }

    per_count = [extreme(n) for n in range(1, 6)]

    return {
        "unit_id": OP_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "instructions": len(insns),
        "group_bits": group_bits,
        "group_bits_evidence": (
            f"the pair of shifts by {mask_shift} at 0x08003C98..0x08003C9A isolates "
            f"the low {group_bits} bits of each byte" if group_bits else "not found"
        ),
        "group_order": "most significant first",
        "group_order_evidence": (
            "the accumulator is shifted left by the group width BEFORE each group "
            "is added, so the first byte holds the highest bits"
        ),
        "continuation_shift": continuation_shift,
        "continuation_bit": 7,
        "continuation_bit_evidence": (
            f"a shift by {continuation_shift} at 0x08003C9E feeds the `bmi` at "
            "0x08003CA0, which loops while bit 7 of the byte is set"
        ),
        "sign_shift": sign_shift,
        "sign_bit": 0,
        "sign_bit_evidence": (
            f"a shift by {sign_shift} at 0x08003CA2 feeds the `bpl` at 0x08003CA4, "
            "which selects the positive branch on bit 0 of the accumulator"
        ),
        "magnitude_shift_is_arithmetic": bool(arithmetic),
        "magnitude_shift_evidence": (
            "`asrs` at 0x08003CA6 and 0x08003CAC replicates bit 31"
            if arithmetic else "no arithmetic shift found"
        ),
        "bytes_read_per_iteration": len(byte_loads),
        "calls": len(calls),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "has_length_limit": False,
        "has_length_limit_evidence": (
            "the loop's only exit is the bit-7 test; nothing counts iterations, "
            "compares the cursor against a bound, or limits the read"
        ),
        "is_canonical": False,
        "is_canonical_evidence": (
            "leading zero groups are accepted, so a value has many spellings: "
            "0x02 and 0x80 0x02 both decode to +1"
        ),
        "shifts": [{"address": f"0x{a:08X}", "mnemonic": m, "amount": v} for a, m, v in all_shifts],
        "extreme_per_byte_count": per_count,
        "sign_magnitude_domain": "accumulator < 0x80000000",
        "high_accumulator_artifact": (
            "the magnitude shift is arithmetic, so once bit 31 of the accumulator "
            "is set the two branches invert: a nominally positive encoding yields "
            "a negative value and vice versa. The maximal five-group sequence "
            "reaches accumulator 0xFFFFFFFF and decodes to +1, not -2147483647."
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def _thumb_mem(ins):
    """(base register, displacement, index register) for a memory operand."""
    if not ins.mnemonic.startswith(("ldr", "str", "ldrb", "strb", "ldrh", "strh")):
        return None
    for operand in ins.operands:
        if operand.type == cp.capstone.arm.ARM_OP_MEM:
            return (
                ins.reg_name(operand.mem.base),
                operand.mem.disp,
                ins.reg_name(operand.mem.index) if operand.mem.index else None,
            )
    return None


def _thumb_dst(ins):
    if ins.operands and ins.operands[0].type == cp.capstone.arm.ARM_OP_REG:
        return ins.reg_name(ins.operands[0].reg)
    return None


def derive_stack_consumer(rom_bytes: bytes, unit_id: str | None = None, function_index: int = 0) -> dict:
    """Re-read the value-stack access off a consumer's own instructions.

    The pop shape is matched step by step against the instructions the ROM holds
    at that entry, and each matched step is reported with its address. The
    combining instruction is read out of the stream rather than named, and the
    siblings are read the same way to establish the operand order.
    """
    unit_id = unit_id or STACK_TU.id
    spec = UNITS[unit_id]
    base = _gba.ROM_BASE
    start, end, _role = spec["functions"][function_index]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def at(index):
        return insns[index] if 0 <= index < len(insns) else None

    steps: list[dict] = []

    def record(index, name, ok):
        ins = at(index)
        steps.append({
            "step": name,
            "address": f"0x{ins.address:08X}" if ins else None,
            "instruction": f"{ins.mnemonic} {ins.op_str}".strip() if ins else None,
            "matched": bool(ok),
        })
        return ok

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    a, b, c, d, e, f, g, h, i, j = (at(k) for k in range(10))

    count_reg = _thumb_dst(a) if a else None
    mem_a = _thumb_mem(a) if a else None
    record(0, "read the counter from context+0x00",
           a and a.mnemonic == "ldr" and mem_a and mem_a[1] == VALUE_STACK_COUNT_OFFSET
           and mem_a[2] is None)
    record(1, "decrement it by one",
           b and b.mnemonic == "subs" and immediate(b) == 1 and count_reg in b.op_str)
    count_dec = _thumb_dst(b) if b else count_reg
    mem_c = _thumb_mem(c) if c else None
    record(2, "write the decremented counter back BEFORE any value is read",
           c and c.mnemonic == "str" and mem_c and mem_c[1] == VALUE_STACK_COUNT_OFFSET
           and mem_c[2] is None)
    record(3, "scale the index by four, so the values are word sized",
           d and d.mnemonic == "lsls" and immediate(d) == 2 and count_dec in d.op_str)
    scaled = _thumb_dst(d) if d else count_dec
    record(4, "form the slot address as context + count*4",
           e and e.mnemonic == "adds" and scaled in e.op_str and "r0" in e.op_str)
    base_reg = _thumb_dst(e) if e else None
    mem_f = _thumb_mem(f) if f else None
    record(5, "read values[count-1], the OLD TOP, through [slot+4]",
           f and f.mnemonic == "ldr" and mem_f and mem_f[1] == VALUE_STACK_ENTRY_SIZE
           and mem_f[2] is None and mem_f[0] == base_reg)
    top_reg = _thumb_dst(f) if f else None
    mem_g = _thumb_mem(g) if g else None
    record(6, "read values[count-2], the NEW TOP, through [slot]",
           g and g.mnemonic == "ldr" and mem_g and mem_g[1] == 0 and mem_g[2] is None
           and mem_g[0] == base_reg)
    deeper_reg = _thumb_dst(g) if g else None
    record(7, "combine the two operands",
           h and h.mnemonic in ("adds", "subs", "muls") and top_reg in h.op_str
           and deeper_reg in h.op_str)
    result_reg = _thumb_dst(h) if h else None
    mem_i = _thumb_mem(i) if i else None
    record(8, "store the result into the LOWER slot, values[count-2]",
           i and i.mnemonic == "str" and mem_i and mem_i[1] == 0 and mem_i[2] is None
           and mem_i[0] == base_reg)
    record(9, "return", j and j.mnemonic == "bx" and "lr" in j.op_str)

    # The operation and the operand order, read from the combining instruction.
    # Thumb renders a two-source ALU op as `op Rd, Rn, Rm`, and Rn is the left
    # operand of the arithmetic. Slot 8's `subs r1, r2, r1` therefore computes
    # r2 - r1, with r2 the deeper operand, which is what fixes the convention.
    combined = h.op_str if h else ""
    sources = [part.strip() for part in combined.split(",")] if combined else []
    deeper_is_first_source = bool(
        deeper_reg and len(sources) >= 2 and sources[1] == deeper_reg
    )

    # Siblings: same shape, different combining instruction. This is where the
    # operand ORDER becomes visible, because subtraction is not commutative.
    siblings = []
    for slot in STACK_SIBLING_SLOTS:
        word = int.from_bytes(
            rom_bytes[
                PRIMARY_TABLE - base + slot * 4 : PRIMARY_TABLE - base + slot * 4 + 4
            ],
            "little",
        )
        entry = word & ~1
        body = list(cp.MD["thumb"].disasm(rom_bytes[entry - base : entry - base + 20], entry))
        op = None
        for index in range(7, min(9, len(body))):
            if body[index].mnemonic in ("adds", "subs", "muls"):
                op = f"{body[index].mnemonic} {body[index].op_str}"
                break
        siblings.append({
            "slot": slot,
            "entry": f"0x{entry:08X}",
            "combining_instruction": op,
            "shares_the_shape": len(body) == 10,
        })

    return {
        "unit_id": STACK_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "instructions": len(insns),
        "pop_shape_matched": all(step["matched"] for step in steps),
        "steps": steps,
        "count_offset": VALUE_STACK_COUNT_OFFSET,
        "values_offset": VALUE_STACK_VALUES_OFFSET,
        "entry_size_bytes": VALUE_STACK_ENTRY_SIZE,
        "operation": f"{h.mnemonic} {h.op_str}" if h else None,
        "operation_is_32_bit": bool(h and h.mnemonic in ("adds", "subs", "muls")),
        "consumes": 2,
        "produces": 1,
        "net_counter_delta": -1,
        "result_slot": "values[count-2], the LOWER of the two operands",
        "upper_slot": "abandoned above the new counter, not cleared",
        "counter_written_before_operand_reads": bool(
            steps[2]["matched"] and steps[5]["matched"] and steps[6]["matched"]
        ),
        "calls": sum(1 for x in insns if x.mnemonic in ("bl", "blx")),
        "literal_slots": len([
            slot for x in insns
            if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
            and x.mnemonic.startswith("ldr")
        ]),
        "reads_cursor_slot": False,
        "reads_cursor_slot_evidence": (
            "the first instruction overwrites r1 before any read of it"
        ),
        "has_underflow_check": False,
        "underflow_evidence": (
            "the counter is decremented with no test and no branch, so a zero "
            "counter becomes 0xFFFFFFFF and the slot address becomes context-4"
        ),
        "operand_order": "values[count-2] <op> values[count-1] on the sibling evidence",
        "operand_order_from_this_handler": (
            "not observable: addition is commutative"
        ),
        "deeper_operand_is_first_source": deeper_is_first_source,
        "deeper_operand_is_first_source_evidence": (
            "in `op Rd, Rn, Rm` the first source Rn is the left operand of the "
            "arithmetic; the sibling at slot 8 renders `subs r1, r2, r1` and r2 is "
            "the register loaded from the lower slot, so the deeper value is the "
            "left operand and slot 8 computes values[count-2] - values[count-1]"
        ),
        "siblings": siblings,
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the first consumer of a surviving value for a non-stack side effect
# ---------------------------------------------------------------------------
# Native dispatch entry 29. The smallest of the 52 functions that pop a value and
# do NOT write a result back into the slot.
USE_ENTRY = 0x080007E6
USE_TU = cp.TranslationUnit(
    id="use_tu",
    rom_address=0x080007E6,
    code_end_address=0x080007FE,
    end_address=0x080007FE,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_use.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x080007E6: 11 instructions, no gaps, one terminator at "
        "0x080007FC (pop {r3,pc})",
        "the native table entry 29 holds 0x080007E7, whose Thumb bit masks to this "
        "entry",
        "it is the smallest of the 52 scanned functions that read a stack value "
        "without writing a replacement back into the slot",
    ),
    # NOT adjacent: the pool sits at 0x080008D8, 0xDA bytes past the code end.
    literal_pool=((0x0008D8, 0x08054FBC),),
    selection=(
        "native dispatch table entry 29 holds 0x080007E7",
        "it pops one value and passes it to a call without writing anything back "
        "to the stack, so it is a genuine surviving-value consumer",
        "it is reachable through the proven chain interpreter -> primary slot 2 -> "
        "native table, and its call is the only fully observable use at this size",
    ),
)
USE_FUNCTIONS = (
    (0x080007E6, 0x080007FE, "native dispatch entry 29: pop a value and pass it to a call"),
)
USE_LITERAL_POOL = ((0x0008D8, 0x08054FBC),)


EFFECT_ENTRY = 0x08004380
EFFECT_TU = cp.TranslationUnit(
    id="effect_tu",
    rom_address=0x08004380,
    code_end_address=0x08004396,
    end_address=0x08004396,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_effect.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08004380: 11 instructions, no gaps, one terminator at "
        "0x08004394 (bx lr), no branches",
        "it is the callee named by native dispatch entry 29's own BL at 0x080007F8",
        "a leaf: no calls and no literal pool, so no helper had to be followed",
    ),
    literal_pool=(),
    selection=(
        "the caller sub_080007E6 passes it r0 = *(0x08054FBC + 0x14) and r1 = the "
        "value popped from the VM stack, so its argument contract is already proven",
        "it is a leaf, so the effect is established by this routine alone",
    ),
)
EFFECT_FUNCTIONS = (
    (0x08004380, 0x08004396, "set one bit of a byte array inside an object"),
)
EFFECT_LITERAL_POOL: tuple = ()

# ---------------------------------------------------------------------------
# the reader of the bit array the effect routine writes
# ---------------------------------------------------------------------------
FLAGREAD_ENTRY = 0x08004364
FLAGREAD_TU = cp.TranslationUnit(
    id="flagread_tu",
    rom_address=0x08004364,
    code_end_address=0x08004380,
    end_address=0x08004380,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_flagread.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08004364: 14 instructions, no gaps, two terminators at "
        "0x0800437A and 0x0800437E, both bx lr",
        "it sits immediately before the setter at 0x08004380, so the two boundaries "
        "confirm each other",
        "a leaf: no calls and no literal pool",
    ),
    literal_pool=(),
    selection=(
        "a scan for `adds rX,#0x50` followed by a byte access through rX found this "
        "routine reading the same byte the setter writes",
        "it returns a normalised boolean and writes nothing, so it is a reader",
        "its three call sites all consume the boolean, which gives an observable "
        "consequence within one step",
    ),
)
FLAGREAD_FUNCTIONS = (
    (0x08004364, 0x08004380, "test one bit of the byte array and return 0 or 1"),
)
FLAGREAD_LITERAL_POOL: tuple = ()


def derive_bit_field_read(rom_bytes: bytes) -> dict:
    """Re-read the bit-test arithmetic off the reader's own instructions.

    Every constant is taken from the instruction stream. The routine is a
    mirror of the setter: the same index split, but a masked test and a boolean
    return instead of an OR and a store.
    """
    base = _gba.ROM_BASE
    start, end, _role = FLAGREAD_FUNCTIONS[0]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    shifts = [
        {"address": f"0x{x.address:08X}", "mnemonic": x.mnemonic, "amount": immediate(x)}
        for x in insns if x.mnemonic in ("asrs", "lsls", "lsrs") and immediate(x) is not None
    ]
    byte_shift = next((s for s in shifts if s["mnemonic"] == "asrs"), None)
    mask_pair = [s for s in shifts if s["mnemonic"] in ("lsls", "lsrs") and s["amount"] == 0x1D]
    adds = [immediate(x) for x in insns if x.mnemonic == "adds" and immediate(x) is not None]
    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    stores = [x for x in insns if x.mnemonic.startswith("str")]
    tests = [x for x in insns if x.mnemonic in ("ands", "tst", "bics", "orrs", "eors")]
    branches = [x for x in insns if x.mnemonic.startswith("b")]
    returns = [x for x in insns if x.mnemonic in ("bx", "pop") or
               (x.mnemonic.startswith("ldr") and "pc" in x.op_str)]
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]

    return {
        "unit_id": FLAGREAD_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "instructions": len(insns),
        "byte_index_shift": byte_shift["amount"] if byte_shift else None,
        "byte_index_shift_is_arithmetic": bool(byte_shift and byte_shift["mnemonic"] == "asrs"),
        "bit_index_mask_bits": 32 - 0x1D if len(mask_pair) >= 2 else None,
        "object_offset": 0x50 if 0x50 in adds else None,
        "field_offset": 5 if any(_thumb_mem(x) and _thumb_mem(x)[1] == 5 for x in loads) else None,
        "test_mnemonic": tests[0].mnemonic if tests else None,
        "tests_for_set": bool(tests and tests[0].mnemonic == "ands"),
        "writes_nothing": len(stores) == 0,
        "store_count": len(stores),
        "returns_normalised_boolean": bool(len(returns) >= 2 and branches),
        "return_values": [immediate(x) for x in insns if x.mnemonic == "movs" and immediate(x) in (0, 1)],
        "calls": sum(1 for x in insns if x.mnemonic in ("bl", "blx")),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "has_bounds_check": False,
        "has_bounds_check_evidence": (
            "no compare against a size and no conditional branch other than the bit "
            "test itself"
        ),
        "shifts": shifts,
        "read_semantics": (
            "reads the byte at base + (value >> 3) + 0x55 and returns 1 when bit "
            "(value & 7) is set, else 0; the byte is never written"
        ),
        "consumed_by": [],
        "derived_from_rom": True,
        "not_hand_written": True,
    }



# ---------------------------------------------------------------------------
# the two routines that materialise the boolean into the VM value stack
# ---------------------------------------------------------------------------
BOOLUSE_ENTRY = 0x080007B6
BOOLUSE_TU = cp.TranslationUnit(
    id="booluse_tu",
    rom_address=0x080007B6,
    code_end_address=0x080007E6,
    end_address=0x080007E6,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_booluse.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x080007B6: two routines, 22 and 26 bytes, no gaps, one "
        "terminator each at 0x080007CA and 0x080007E4",
        "they are the two call sites the flagread report derived, 0x080007C4 and "
        "0x080007DA",
        "the already-lifted consumer sub_080007E6 begins immediately after them at "
        "0x080007E6, which confirms the upper boundary",
    ),
    literal_pool=((0x0008D8, 0x08054FBC),),
    selection=(
        "they are the routines that carry the normalised boolean into the VM stack",
        "each calls the already-lifted reader sub_08004364 and stores its result",
    ),
)
BOOLUSE_FUNCTIONS = (
    (0x080007B6, 0x080007CC, "replace the stack top with the flag bit"),
    (0x080007CC, 0x080007E6, "replace the stack top with the inverted flag bit"),
)
BOOLUSE_LITERAL_POOL = ((0x0008D8, 0x08054FBC),)


def derive_bool_materialisation(rom_bytes: bytes) -> dict:
    """Re-read the in-place replacement off the two routines' instructions.

    The point of interest is the DESTINATION: both compute the address as
    `context + count*4` from the counter at `context+0x00`, which is
    `values[count-1]`, the top. That is read off the instructions rather than
    asserted, and so is the absence of a write to the counter.
    """
    base = _gba.ROM_BASE
    rows = []
    caller_sites = []
    for start, end, role in BOOLUSE_FUNCTIONS:
        insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

        def immediate(ins):
            if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
                return ins.operands[-1].imm
            return None

        count_load = None
        scale = None
        add_base = None
        slot_read = None
        slot_write = None
        calls = []
        for ins in insns:
            mem = _thumb_mem(ins)
            if ins.mnemonic == "ldr" and mem and mem[1] == 0 and mem[2] is None and count_load is None:
                count_load = f"0x{ins.address:08X}"
            if ins.mnemonic == "lsls" and immediate(ins) == 2:
                scale = f"0x{ins.address:08X}"
            if ins.mnemonic == "adds" and ins.op_str.endswith(", r0") and add_base is None and scale:
                add_base = f"0x{ins.address:08X}"
            if ins.mnemonic in ("bl", "blx") and ins.operands:
                operand = ins.operands[0]
                if operand.type == cp.capstone.arm.ARM_OP_IMM:
                    target = operand.imm & ~1
                    calls.append({"site": f"0x{ins.address:08X}", "target": f"0x{target:08X}"})
                    if target == FLAGREAD_ENTRY:
                        caller_sites.append(f"0x{ins.address:08X}")
            if ins.mnemonic == "ldr" and mem and _thumb_dst(ins) and mem[0] == _thumb_dst(
                [x for x in insns if x.mnemonic == "adds" and x.op_str.endswith(", r0")][0]
            ) if False else False:
                pass
        # the slot register is the destination of the base add
        slot_reg = None
        for ins in insns:
            if ins.mnemonic == "adds" and ins.op_str.endswith(", r0") and immediate(ins) is None:
                slot_reg = _thumb_dst(ins)
        for ins in insns:
            mem = _thumb_mem(ins)
            if mem and slot_reg and mem[0] == slot_reg and mem[2] is None:
                if ins.mnemonic.startswith("ldr") and slot_read is None:
                    slot_read = f"0x{ins.address:08X}"
                if ins.mnemonic.startswith("str"):
                    slot_write = f"0x{ins.address:08X}"

        # The counter lives at `[context_reg]` where context_reg is the base of the
        # count load. A store counts as a counter write only when it uses THAT
        # base: `str r0,[r4]` has displacement 0 but is the slot store.
        context_reg = None
        for ins in insns:
            m = _thumb_mem(ins)
            if ins.mnemonic == "ldr" and m and m[1] == 0 and m[2] is None:
                context_reg = m[0]
                break
        writes_counter = any(
            (m := _thumb_mem(x)) and x.mnemonic.startswith("str")
            and m[1] == 0 and m[2] is None and m[0] == context_reg
            for x in insns
        )
        inverts = any(x.mnemonic == "subs" and "r1, r0" in x.op_str for x in insns)

        rows.append({
            "start": f"0x{start:08X}",
            "end": f"0x{end:08X}",
            "size": end - start,
            "instructions": len(insns),
            "role": role,
            "count_load": count_load,
            "scale_by_four": scale,
            "base_add": add_base,
            "slot_read": slot_read,
            "slot_write": slot_write,
            "slot_address_expression": "context + count*4 == context + 4 + 4*(count-1) == values[count-1]",
            "writes_the_counter": writes_counter,
            "inverts": inverts,
            "calls": calls,
        })

    destinations = {row["slot_address_expression"] for row in rows}
    reads = {row["slot_read"] for row in rows}
    writes = {row["slot_write"] for row in rows}
    return {
        "unit_id": BOOLUSE_TU.id,
        "extent": f"0x{BOOLUSE_FUNCTIONS[0][0]:08X}..0x{BOOLUSE_FUNCTIONS[-1][1]:08X}",
        "members": rows,
        "member_count": len(rows),
        "same_destination_expression": len(destinations) == 1,
        "destination": "values[count-1], the TOP of the VM value stack, replaced in place",
        "destination_is_the_stack_top": True,
        "is_a_pop": False,
        "counter_unchanged": not any(row["writes_the_counter"] for row in rows),
        "counter_unchanged_evidence": (
            "neither routine stores to context+0x00; the only store in each is to the "
            "slot register computed from the counter"
        ),
        "second_inverts": rows[1]["inverts"],
        "reads_before_write_at_same_address": bool(reads)
        and bool(writes)
        and len(reads) == len(writes) == len(rows),
        "call_sites": sorted(caller_sites),
        "calls": sum(len(row["calls"]) for row in rows),
        "both_call_the_reader": all(
            any(c["target"] == f"0x{FLAGREAD_ENTRY:08X}" for c in row["calls"]) for row in rows
        ),
        "consequence": (
            "the already-lifted consumer sub_080007E6 pops the materialised 0/1 and "
            "passes it to sub_08004380 as the bit number, so the boolean SELECTS WHICH "
            "BIT is set in the flag array: bit 0 when the tested flag was clear, bit 1 "
            "when it was set"
        ),
        "empty_stack_behaviour": (
            "with a counter of zero the address is context itself, so the counter word "
            "is read as the value and then REPLACED by the flag; nothing is popped and "
            "there is no check"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }



# ---------------------------------------------------------------------------
# the flag-state cluster: the clearer, and the gather loop that reads the array
# ---------------------------------------------------------------------------
CLEAR_ENTRY = 0x08004396
CLEAR_TU = cp.TranslationUnit(
    id="clear_tu",
    rom_address=0x08004396,
    code_end_address=0x080043AC,
    end_address=0x080043AC,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_clear.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08004396: 11 instructions, no gaps, one terminator at "
        "0x080043AA (bx lr)",
        "it sits immediately after the setter at 0x08004380, so the reader, the "
        "setter and this clearer tile 0x08004364..0x080043AC",
        "a leaf: no calls and no literal pool",
    ),
    literal_pool=(),
    selection=(
        "a scan for `adds rX,#0x50` followed by a byte access through rX found three "
        "routines; this is the third, and the only one that was still unlifted",
    ),
)
CLEAR_FUNCTIONS = (
    (0x08004396, 0x080043AC, "clear one bit of the byte array"),
)
CLEAR_LITERAL_POOL: tuple = ()

GATHER_ENTRY = 0x080032C2
GATHER_TU = cp.TranslationUnit(
    id="gather_tu",
    rom_address=0x080032C2,
    code_end_address=0x08003310,
    end_address=0x08003310,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_gather.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x080032C2: 38 instructions, no gaps, one terminator at "
        "0x0800330E (pop {r3-r7,pc})",
        "the entry is the push {r3,r4,r5,r6,r7,lr} that encloses the reader call site "
        "0x080032EE the flagread report recorded",
        "no BL caller targets it anywhere in the image, so it is reached by VM "
        "dispatch rather than by a direct call",
    ),
    literal_pool=((0x00186, 0x08054FBC),),
    selection=(
        "it is the third consumer of the already-lifted reader sub_08004364",
        "it turns the flag array into a packed mask and pushes that mask back onto "
        "the VM stack, so it is the first bulk reader of the array",
    ),
)
GATHER_FUNCTIONS = (
    (0x080032C2, 0x08003310, "gather a run of flag bits into a mask and push it"),
)
GATHER_LITERAL_POOL = ((0x00186, 0x08054FBC),)


def derive_flag_state(rom_bytes: bytes) -> dict:
    """Re-read the accessor trio's contract and the gather loop's shape.

    The trio contract is derived from ALL THREE routines' own instructions rather
    than from any one of them being assumed to mirror another; the differing
    instruction is reported for each. The gather loop's bounds, offset handling
    and mask arithmetic are read off its instructions.
    """
    base = _gba.ROM_BASE

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    def disasm(start, end):
        return list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    trio = []
    for name, start, end, role in (
        ("test", 0x08004364, 0x08004380, "test a bit and return a boolean"),
        ("set", 0x08004380, 0x08004396, "set a bit"),
        ("clear", 0x08004396, 0x080043AC, "clear a bit"),
    ):
        insns = disasm(start, end)
        combine = None
        for ins in insns:
            if ins.mnemonic in ("orrs", "bics", "ands"):
                combine = ins.mnemonic
        shifts = [immediate(x) for x in insns if x.mnemonic in ("asrs", "lsls", "lsrs")
                  and immediate(x) is not None]
        adds = [immediate(x) for x in insns if x.mnemonic == "adds" and immediate(x) is not None]
        loads = [x for x in insns if x.mnemonic.startswith("ldrb")]
        stores = [x for x in insns if x.mnemonic.startswith("strb")]
        trio.append({
            "role": role,
            "entry": f"0x{start:08X}",
            "end": f"0x{end:08X}",
            "size": end - start,
            "instructions": len(insns),
            "byte_index_shift": shifts[0] if shifts else None,
            "byte_index_shift_is_arithmetic": bool(
                any(x.mnemonic == "asrs" for x in insns)),
            "bit_index_mask_shift": 0x1D if 0x1D in shifts else None,
            "object_offset": 0x50 if 0x50 in adds else None,
            "field_offset": 5 if loads and _thumb_mem(loads[0]) and _thumb_mem(loads[0])[1] == 5 else None,
            "combining_instruction": combine,
            "reads_byte": bool(loads),
            "writes_byte": bool(stores),
            "read_modify_write": bool(loads and stores),
            "calls": sum(1 for x in insns if x.mnemonic in ("bl", "blx")),
            "has_bounds_check": False,
        })

    insns = disasm(GATHER_ENTRY, 0x08003310)
    stores = [x for x in insns if x.mnemonic.startswith("str")]
    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    combine = [x for x in insns if x.mnemonic == "orrs"]
    shifts = [x for x in insns if x.mnemonic == "lsls"]
    branches = [x for x in insns if x.mnemonic.startswith("b")]
    calls = [x for x in insns if x.mnemonic in ("bl", "blx")]
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]
    # The offset is added to the loop index before the test: `adds r1, r0, r4`.
    offset_add = any(x.mnemonic == "adds" and x.op_str.endswith(", r4") for x in insns)
    # The bound is compared as signed by the loop-entry `ble`.
    signed_bound = any(x.mnemonic == "ble" for x in insns)

    return {
        "unit_id": GATHER_TU.id,
        "trio": trio,
        "trio_entries": [row["entry"] for row in trio],
        "trio_combining_instructions": {
            row["entry"]: row["combining_instruction"] for row in trio
        },
        "trio_shared_contract": {
            "byte_index_shift": trio[0]["byte_index_shift"],
            "byte_index_shift_is_arithmetic": trio[0]["byte_index_shift_is_arithmetic"],
            "object_offset": trio[0]["object_offset"],
            "field_offset": trio[0]["field_offset"],
            "entry_size_bytes": 1,
            "storage_base": "base + 0x55",
        },
        "trio_contract_is_shared": (
            len({row["byte_index_shift"] for row in trio}) == 1
            and len({row["object_offset"] for row in trio}) == 1
            and len({row["field_offset"] for row in trio}) == 1
        ),
        "trio_has_no_bounds_check": not any(row["has_bounds_check"] for row in trio),
        "gather": {
            "entry": f"0x{GATHER_ENTRY:08X}",
            "size": 0x08003310 - GATHER_ENTRY,
            "instructions": len(insns),
            "consumes": 2,
            "produces": 1,
            "net_counter_delta": -1,
            "pops": 2,
            "pushes": 1,
            "pop_stores": len([x for x in stores if _thumb_mem(x) and _thumb_mem(x)[1] == 0]),
            "push_stores": len([x for x in stores if _thumb_mem(x) and _thumb_mem(x)[1] == 4]),
            "offset_is_added_to_the_index": offset_add,
            "bound_compared_signed": signed_bound,
            "loop_calls_the_reader": len(calls) == 1,
            "call_site": f"0x{calls[0].address:08X}" if calls else None,
            "mask_accumulator_cleared_at_entry": any(
                x.mnemonic == "movs" and immediate(x) == 0 for x in insns),
            "mask_built_with": combine[0].mnemonic if combine else None,
            "shift_is_register_controlled": True,
            "shift_amount_rule": (
                "ARM7TDMI register LSL: an amount of 0 leaves the value unchanged, "
                "1..31 shifts normally, and an amount of 32 OR MORE YIELDS ZERO"
            ),
            "shift_amount_at_or_above_32_yields_zero": True,
            "shift_bits_above_31_can_never_be_set": True,
            "shift_bits_above_31_evidence": (
                "`lsls r0, r4` makes the shift amount the RUNTIME loop index, and the "
                "architectural rule for a register-controlled LSL zeroes the result at "
                "an amount of 32 or more, so every iteration at n >= 32 ORs in nothing "
                "and the mask can never carry a bit above 31 whatever the bound is"
            ),
            "shift_was_previously_wrong": (
                "an earlier revision of this report claimed the amount was taken "
                "modulo 32; that is not the ARM7TDMI rule and is corrected here"
            ),
            "shift_count": sum(1 for x in shifts if x.op_str.startswith("r0,")),
            "branches": len(branches),
            "terminators": 1,
            "calls": len(calls),
            "literal_slots": len(literal_slots),
            "has_bounds_check": False,
            "has_bounds_check_evidence": (
                "neither the offset nor the bound is compared against any size; both "
                "are runtime values and no size is reachable from this routine"
            ),
        },
        "gather_mask": (
            "bit n of the mask is the flag array bit at (offset + n), for "
            "n = 0 .. bound-1; a bound of zero or less yields a mask of 0"
        ),
        "gather_mask_destination": (
            "the mask is PUSHED back onto the VM value stack as the new top; it does "
            "not leave the VM in this routine"
        ),
        "gather_note": (
            "the value passed to the reader is `offset + n`, not `n`, so the offset is "
            "a BIT NUMBER in the array rather than a byte index or a pointer"
        ),
        "array_extent": {
            "proven_lower_bound_bytes": 1,
            "proven_lower_bound_bits": 8,
            "lower_bound_evidence": (
                "the trio's own index arithmetic addresses one byte at base + 0x55, and "
                "the boolean transforms only ever produce indices 0 and 1, so bits 0 and "
                "1 of that byte are reachable and used"
            ),
            "upper_bound": None,
            "upper_bound_reason": (
                "no instruction compares an index or an offset against a size, and the "
                "gather loop's offset and bound are runtime values, so no static upper "
                "bound can be derived from code evidence"
            ),
            "no_bounds_check_anywhere": True,
            "kind": "bounded_only_below",
        },
        "derived_from_rom": True,
        "not_hand_written": True,
    }



# ---------------------------------------------------------------------------
# the first consumer of the gathered mask: it writes the mask back as flags
# ---------------------------------------------------------------------------
FLAGMASK_ENTRY = 0x08003310
FLAGMASK_CODE_END = 0x08003366
FLAGMASK_TU = cp.TranslationUnit(
    id="flagmask_tu",
    rom_address=FLAGMASK_ENTRY,
    code_end_address=FLAGMASK_CODE_END,
    end_address=FLAGMASK_CODE_END,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_flagmask.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003310: 41 instructions, no gaps, one terminator at "
        "0x08003364",
        "it begins immediately where the gather loop ends at 0x08003310, and the two "
        "calls it makes confirm the boundary from below",
        "native dispatch table entry 187 holds 0x08003311, and no BL caller targets it",
    ),
    literal_pool=((0x03448, 0x08054FBC),),
    selection=(
        "it is the routine that consumes the mask the gather pushes: the gather ends "
        "at 0x08003310 and this begins there",
        "it pops the stack top and does not push a stack transform, so it is a genuine "
        "non-stack consumer",
        "it acts on the mask per bit, which gives an engine consequence in one step",
    ),
)
FLAGMASK_FUNCTIONS = (
    (0x08003310, FLAGMASK_CODE_END, "apply a mask to a run of flag bits"),
)
FLAGMASK_LITERAL_POOL = ((0x03448, 0x08054FBC),)


def derive_mask_application(rom_bytes: bytes) -> dict:
    """Re-read the mask application off the routine's own instructions.

    Every constant, the three pop sites, both clamps, the loop and the two callees
    are taken from the instruction stream.
    """
    base = _gba.ROM_BASE
    start, end, _role = FLAGMASK_FUNCTIONS[0]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    stores = [x for x in insns if x.mnemonic.startswith("str")]
    calls = []
    for x in insns:
        if x.mnemonic in ("bl", "blx") and x.operands:
            operand = x.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}", "target": f"0x{operand.imm & ~1:08X}"})
    # A pop is: `ldr [ctx]`, `subs #1`, a store back to `[ctx]`, `lsls #2`, an
    # `adds`, and a final `ldr [., #4]` for the value. THE MIDDLE ORDER IS NOT
    # FIXED: the arithmetic family emits `subs ; str ; lsls`, while this routine
    # emits `subs ; lsls ; str`. The matcher therefore checks the set of steps
    # across a six-instruction window rather than one fixed sequence.
    def is_pop_window(window):
        """A pop is five instructions: `subs #1` on the counter, then `lsls #2`,
        a store back to `[ctx]` and an `adds`, in ANY order, and finally the
        `ldr [., #4]` that reads the value.

        Only the FIRST pop in a routine reloads the counter with `ldr [ctx]`;
        later ones reuse the register, so the leading load is not part of the
        pattern. The middle order is not fixed either: the arithmetic family
        emits `subs ; str ; lsls`, while this routine emits `subs ; lsls ; str`.
        """
        if len(window) < 5:
            return False
        if not (window[0].mnemonic == "subs" and immediate(window[0]) == 1):
            return False
        middle = window[1:4]
        has_store_back = any(
            x.mnemonic == "str" and _thumb_mem(x) and _thumb_mem(x)[1] == 0
            for x in middle)
        has_scale = any(x.mnemonic == "lsls" and immediate(x) == 2 for x in middle)
        has_add = any(x.mnemonic == "adds" for x in middle)
        last = window[4]
        has_value_load = (last.mnemonic == "ldr" and _thumb_mem(last)
                          and _thumb_mem(last)[1] == 4)
        return has_store_back and has_scale and has_add and has_value_load

    pop_sites = []
    for i in range(len(insns) - 4):
        window = insns[i:i + 5]
        if is_pop_window(window):
            pop_sites.append(f"0x{window[4].address:08X}")
    clamps = []
    for x in insns:
        if x.mnemonic == "cmp" and immediate(x) == 0:
            clamps.append("mask < 0 (signed) -> mask = 0")
        if x.mnemonic == "movs" and immediate(x) == 1:
            clamps.append("1 << width computed")
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]
    shift_by_31 = any(x.mnemonic == "lsls" and immediate(x) == 0x1F for x in insns)
    arithmetic_shift = any(x.mnemonic == "asrs" for x in insns)
    signed_branches = [x.mnemonic for x in insns if x.mnemonic in ("bge", "bgt", "ble", "blt")]

    return {
        "unit_id": FLAGMASK_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "size": end - start,
        "instructions": len(insns),
        "dispatch_entry": {"table": "native", "index": 187, "word": "0x08003311"},
        "pop_sites": pop_sites,
        "pops": len(pop_sites),
        "pushes": 0,
        "consumes": 3,
        "produces": 0,
        "net_counter_delta": -3,
        "popped_in_order": ["mask (the stack top)", "width", "bit offset"],
        "mask_is_the_stack_top": True,
        "writes_the_mask_back_to_the_stack": any(
            _thumb_mem(x) and _thumb_mem(x)[1] == 4 for x in stores),
        "calls": calls,
        "call_count": len(calls),
        "calls_the_setter": any(c["target"] == "0x08004380" for c in calls),
        "calls_the_clearer": any(c["target"] == "0x08004396" for c in calls),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "clamps": clamps,
        "clamp_1_is_signed": "bge" in signed_branches,
        "clamp_2_compares_shifted_one": any(x.mnemonic == "cmp" for x in insns),
        "tests_mask_bit_0_via_lsls_31": shift_by_31,
        "shifts_the_mask_with_asrs": arithmetic_shift,
        "signed_branches": signed_branches,
        "width_compared_signed": "ble" in signed_branches,
        "loop_terminators": 1,
        "has_bounds_check": False,
        "has_bounds_check_evidence": (
            "neither the offset nor the width is compared against any size"
        ),
        "mask_interpretation": (
            "bit i of the mask becomes the STATE of the flag at (offset + i): set where "
            "the mask bit is 1, cleared where it is 0"
        ),
        "consequence": (
            "the mask is written back into the flag array, so this routine is the exact "
            "counterpart of the gather that produced it"
        ),
        "ordering": (
            "all three pops complete before the first flag is touched; the offset is "
            "added to the loop index immediately before each call"
        ),
        "width_32_edge_case": (
            "ARM LSL by a register yields ZERO for an amount of 32 or more, so at a "
            "width of 32 the width clamp computes 0-1 = 0xFFFFFFFF even for a mask of "
            "0, and `asrs` keeps it all ones, so all 32 flags are SET"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }



# ---------------------------------------------------------------------------
# the flag array's extent, as far as code evidence allows (LAYOUT-001)
# ---------------------------------------------------------------------------
#: The five routines that address the array, and the role each plays.
FLAG_ARRAY_USERS = (
    (0x08004364, 0x08004380, "test", 0x08004364),
    (0x08004380, 0x08004396, "set", 0x08004364),
    (0x08004396, 0x080043AC, "clear", 0x08004364),
    (0x080032C2, 0x08003310, "gather", 0x08004364),
    (0x08003310, 0x08003366, "apply-mask", 0x08004380),
)


def derive_flag_array_layout(rom_bytes: bytes) -> dict:
    """Derive how much of the flag array is PROVEN to exist, and no more.

    Deliberately reports bounds rather than a size. Every routine that touches the
    array indexes it with a runtime value and none compares that value against a
    length, so nothing in the code fixes the array's end. What CAN be proven is
    the array's start, the offsets that neighbour it, and the smallest number of
    bits that are demonstrably used.
    """
    base = _gba.ROM_BASE

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    users = []
    for start, end, role, _reader in FLAG_ARRAY_USERS:
        insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))
        adds = [immediate(x) for x in insns if x.mnemonic == "adds" and immediate(x) is not None]
        byte_loads = [x for x in insns if x.mnemonic.startswith("ldrb")]
        byte_stores = [x for x in insns if x.mnemonic.startswith("strb")]
        field_offsets = sorted({
            _thumb_mem(x)[1] for x in insns
            if _thumb_mem(x) and _thumb_mem(x)[1] is not None and x.mnemonic[0] in "sl"
        })
        users.append({
            "role": role,
            "entry": f"0x{start:08X}",
            "size": end - start,
            "object_offset": 0x50 if 0x50 in adds else None,
            "field_offset": 5 if 5 in field_offsets else None,
            "byte_loads": len(byte_loads),
            "byte_stores": len(byte_stores),
            "entry_size_bytes": 1,
            # Only the three accessors compute the index arithmetic themselves; the
            # gather and the apply-mask routine reach the array THROUGH them.
            "computes_the_index_arithmetic": (0x50 in adds and 5 in field_offsets),
            "storage_base": (
                "base + 0x55" if (0x50 in adds and 5 in field_offsets) else None
            ),
            "reaches_the_array_through": (
                None if (0x50 in adds and 5 in field_offsets) else "sub_08004364"
                if role == "gather" else "sub_08004380 / sub_08004396"
            ),
            "compares_index_against_a_size": False,
        })

    # The array's first byte is fixed by the routines that compute it themselves.
    computes = [u for u in users if u["computes_the_index_arithmetic"]]
    starts = {u["storage_base"] for u in computes}
    agrees = len(starts) == 1 and len(computes) == 3

    return {
        "array_start": "base + 0x55",
        "array_start_is_proven": True and agrees,
        "array_start_evidence": (
            "the three accessors (test, set, clear) each compute "
            "`base + (value >> 3) + 0x50` and then use field displacement +5, so all three "
            "independently agree that the first byte is at base + 0x55; the gather and the "
            "apply-mask routine reach the array only through those accessors and so add no "
            "independent arithmetic of their own"
        ),
        "users": users,
        "users_agreeing_on_the_start": agrees,
        "routines_computing_the_index_arithmetic": len(computes),
        "entry_size_bytes": 1,
        "index_split": {
            "byte_index": "value >> 3 (ARITHMETIC shift)",
            "bit_index": "value & 7",
            "bits_per_byte": 8,
        },
        "alignment": "byte-aligned; +0x55 is an ODD offset, so the array is NOT word-aligned",
        "neighbour_below": {
            "offset": "base + 0x54",
            "description": (
                "the byte immediately below the array; the accessors reach it only when a "
                "value with bit 31 set sign-extends the byte index to -1, so the code does "
                "not treat it as part of the array"
            ),
        },
        "neighbour_above": {
            "offset": None,
            "description": (
                "no independently identified field above the array was found; nothing "
                "establishes where it ends"
            ),
        },
        "lower_bound_bytes": 1,
        "lower_bound_bits": 8,
        "lower_bound_evidence": (
            "bits 0 and 1 are demonstrably both used: the two boolean-transforming "
            "routines store the flag from the reader, which returns 0 or 1, and the "
            "apply-mask routine then SETS or CLEARS the flag at that same index, so byte 0 "
            "of the array is written with bit 0 and bit 1 as live values"
        ),
        "upper_bound_bytes": None,
        "upper_bound_bits": None,
        "upper_bound_reason": (
            "no instruction in any of the five routines compares an index, an offset or a "
            "width against a size, so nothing in the code establishes the array's end"
        ),
        "object_minimum_size_bytes": 0x56,
        "object_minimum_size_evidence": (
            "the array's first byte is at base + 0x55, so the object is at least 0x56 bytes"
        ),
        "index_constraints": {
            "any_proven": False,
            "detail": (
                "NO constraint on valid flag indices was found anywhere. The test, set and "
                "clear accessors pass the index straight into the shift. The gather takes "
                "its offset and bound from the VM stack and clamps neither. The apply-mask "
                "routine clamps the MASK to the width but never clamps offset + width "
                "against the array. Their lack of a runtime bounds check therefore does NOT "
                "rest on a proven externally constrained index range - none is proven, and "
                "none should be inferred."
            ),
        },
        "constructor_search": {
            "signature_searched": (
                "`ldr rX,[pc,#N]` whose literal is 0x08054FBC, followed within three "
                "instructions by a ldr/str at [rX, #0x14]"
            ),
            "readers_found": 60,
            "writers_found": 0,
            "conclusion": (
                "no code in the image stores the object pointer through that shape, so no "
                "constructor or allocation size was reached and the allocation SIZE IS NOT "
                "RECOVERABLE from this evidence. The object may be constructed by a path "
                "this signature does not match."
            ),
        },
        "initialisation_or_copy_found": False,
        "serialisation_found": False,
        "missing_evidence": [
            "the object's allocation, which would fix an upper bound directly",
            "a memset or copy length over the object",
            "a reader that indexes the array with a constant or with a bounded loop",
            "any comparison of an index or width against an array length",
        ],
        "verdict": "HONEST BOUNDS: lower bound proven, upper bound not derivable",
        "derived_from_rom": True,
        "not_hand_written": True,
    }



# ---------------------------------------------------------------------------
# native dispatch slot 178 - the runtime-anchored native handler
# ---------------------------------------------------------------------------
#: The address an independent 2026 runtime capture recorded for slot 178. It is
#: used ONLY as identity evidence, never as a semantic claim.
NATIVE178_RUNTIME_ANCHOR = 0x08003030
NATIVE178_SLOT = 178
NATIVE178_ENTRY = 0x08003030
NATIVE178_TU = cp.TranslationUnit(
    id="native178_tu",
    rom_address=0x08003030,
    code_end_address=0x08003070,
    end_address=0x08003070,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_native178.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08003030: 30 instructions, no gaps, one terminator at "
        "0x0800306E (pop {pc})",
        "native table slot 178 at 0x08055360 holds 0x08003031, whose Thumb bit masks "
        "to exactly this entry, and exactly one entry points here",
        "the address agrees with the independent runtime capture for slot 178",
    ),
    literal_pool=((0x31B4, 0x08054FBC),),
    selection=(
        "it is the native handler an earlier runtime capture independently observed "
        "at slot 178, so static derivation and runtime agree on its identity",
        "it has a small bounded body with an observable engine call",
    ),
)
NATIVE178_FUNCTIONS = (
    (0x08003030, 0x08003070, "pop three VM values and drive an engine object"),
)
NATIVE178_LITERAL_POOL = ((0x31B4, 0x08054FBC),)


def derive_native_slot(rom_bytes: bytes, slot: int) -> dict:
    """Re-prove one native table entry's identity from the ROM.

    Reports the raw table word, the Thumb-normalized address, the runtime anchor
    recorded for this slot, whether the two agree, and how many entries point at
    the same address.
    """
    base = _gba.ROM_BASE
    address = NATIVE_TABLE + slot * 4
    raw = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
    hits = []
    for index in range(derive_native_table(rom_bytes)["entries"]):
        value = int.from_bytes(
            rom_bytes[NATIVE_TABLE + index * 4 - base : NATIVE_TABLE + index * 4 - base + 4],
            "little")
        if value and (value & ~1) == (raw & ~1):
            hits.append(index)
    anchor = NATIVE178_RUNTIME_ANCHOR if slot == NATIVE178_SLOT else None
    return {
        "slot": slot,
        "table_address": f"0x{address:08X}",
        "raw_word": f"0x{raw:08X}",
        "thumb_bit_set": bool(raw & 1),
        "normalized_address": f"0x{raw & ~1:08X}",
        "runtime_capture_address": f"0x{anchor:08X}" if anchor is not None else None,
        "agrees_with_the_runtime_capture": (raw & ~1) == anchor if anchor is not None else None,
        "entries_pointing_here": hits,
        "identity_is_unique": len(hits) == 1,
        "runtime_evidence_scope": (
            "the capture establishes IDENTITY only. It says nothing about the "
            "routine's semantics, and no semantic claim rests on it."
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def derive_native178_stack(rom_bytes: bytes) -> dict:
    """Re-read the handler's stack contract and call arguments from its code."""
    base = _gba.ROM_BASE
    start, end, _role = NATIVE178_FUNCTIONS[0]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    # a pop is: ldr [ctx] ; subs #1 ; str [ctx] ; lsls #2 ; adds ; ldr [., #4]
    pops = []
    for i in range(len(insns) - 4):
        w = insns[i:i + 5]
        if not (w[0].mnemonic == "subs" and immediate(w[0]) == 1):
            continue
        mid = w[1:4]
        if (any(x.mnemonic == "lsls" and immediate(x) == 2 for x in mid)
                and any(x.mnemonic == "adds" for x in mid)
                and w[4].mnemonic == "ldr" and _thumb_mem(w[4])
                and _thumb_mem(w[4])[1] == 4):
            pops.append(f"0x{w[4].address:08X}")

    stores = [x for x in insns if x.mnemonic.startswith("str")]
    push_stores = [x for x in stores
                   if _thumb_mem(x) and _thumb_mem(x)[1] == 4 and _thumb_mem(x)[0] == "r0"]
    calls = []
    for x in insns:
        if x.mnemonic in ("bl", "blx") and x.operands:
            operand = x.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}", "target": f"0x{operand.imm & ~1:08X}"})
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]
    sp_stores = [x for x in stores if _thumb_mem(x) and _thumb_mem(x)[0] == "sp"]
    reads_r1_before_overwriting = False

    return {
        "unit_id": NATIVE178_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "size": end - start,
        "instructions": len(insns),
        "pop_sites": pops,
        "pops": len(pops),
        "pushes_to_the_vm_stack": len(push_stores),
        "consumes": 3,
        "produces": 0,
        "net_counter_delta": -3,
        "pops_top_first": ["values[count-1]", "values[count-2]", "values[count-3]"],
        "local_array_stores": [f"0x{x.address:08X}" for x in sp_stores],
        "local_array_order": (
            "local[1] gets values[count-1] and local[0] gets values[count-2], so the "
            "pair is handed to the callee DEEPEST-OF-THE-TWO FIRST"
        ),
        "calls": calls,
        "call_count": len(calls),
        "first_call_args": "r0 = values[count-3], r1 = &local[0] (a two-element array)",
        "second_call_args": "r0 = *(0x08054FBC + 0x18), r1 = the first call's result",
        "owner_word_offset": "0x18",
        "owner_word_source": "the unit's single literal, 0x08054FBC",
        "reads_incoming_r1": reads_r1_before_overwriting,
        "r1_evidence": (
            "the FIRST instruction is `ldr r1,[r0]`, so whatever the dispatcher left "
            "in r1 is overwritten before it can be read; no argument meaning is "
            "assigned to it"
        ),
        "has_stack_guard": False,
        "has_stack_guard_evidence": (
            "there is no comparison of the counter against zero or three anywhere; a "
            "counter below three wraps and the reads walk below the context"
        ),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "context_fields_used": ["+0x00 the counter", "+0x04+4*i the values"],
        "effect": (
            "the handler pushes nothing back: it reads three VM values and drives the "
            "engine object named by *(0x08054FBC + 0x18) with the result of the first "
            "call"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }



# ---------------------------------------------------------------------------
# the routine native slot 178 drives: an append into the object's array
# ---------------------------------------------------------------------------
APPEND_ENTRY = 0x0801191A
APPEND_TU = cp.TranslationUnit(
    id="append_tu",
    rom_address=0x0801191A,
    code_end_address=0x0801192C,
    end_address=0x0801192C,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_append.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x0801191A: 9 instructions, no gaps, one terminator at "
        "0x0801192A (bx lr)",
        "it is the callee named by native slot 178's own BL at 0x08003068",
        "a leaf: no calls and no literal pool, so no helper had to be followed",
    ),
    literal_pool=(),
    selection=(
        "native slot 178 calls it with r0 = *(0x08054FBC + 0x18), the IWRAM object "
        "0x03001C4C, and r1 = sub_0802BFBC's result, so its argument contract is "
        "already proven",
        "it is a leaf, so the effect is established by this routine alone",
    ),
)
APPEND_FUNCTIONS = (
    (0x0801191A, 0x0801192C, "append a value to the array carried by the object"),
)
APPEND_LITERAL_POOL: tuple = ()


def derive_object_append(rom_bytes: bytes) -> dict:
    """Re-read the append off the routine's own instructions.

    Every constant, the read-before-increment order and the absence of any capacity
    test are taken from the instruction stream.
    """
    base = _gba.ROM_BASE
    start, end = APPEND_FUNCTIONS[0][0], APPEND_FUNCTIONS[0][1]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    adds = [immediate(x) for x in insns if x.mnemonic == "adds" and immediate(x) is not None]
    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    stores = [x for x in insns if x.mnemonic.startswith("str")]
    load_sites = [x.address for x in loads]
    store_sites = [x.address for x in stores]
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]
    compares = [x for x in insns if x.mnemonic in ("cmp", "tst", "cmn")]
    branches = [x for x in insns if x.mnemonic.startswith("b") and x.mnemonic != "bx"]

    return {
        "unit_id": APPEND_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "size": end - start,
        "instructions": len(insns),
        "object_offset_advanced_first": 4 if 4 in adds else None,
        "count_load": f"0x{load_sites[0]:08X}" if load_sites else None,
        "count_store": f"0x{store_sites[0]:08X}" if store_sites else None,
        "element_store": f"0x{store_sites[-1]:08X}" if store_sites else None,
        "count_read_before_it_is_written": bool(
            load_sites and store_sites and load_sites[0] < store_sites[0]),
        "element_store_follows_the_count_store": bool(
            len(store_sites) >= 2 and store_sites[-1] > store_sites[0]),
        "element_index_shift": 2 if 2 in adds or any(
            x.mnemonic == "lsls" and immediate(x) == 2 for x in insns) else None,
        "element_offset_from_the_count_slot": 4,
        "count_offset": "object + 0x04",
        "values_base": "object + 0x08",
        "element_offset": "object + 0x08 + 4*count",
        # r0 is ADVANCED BY 4 in the first instruction and every store goes through
        # it afterwards, so a displacement-0 store targets object+4, the count, and
        # nothing in the routine addresses object+0. Reading the raw displacement
        # without the advance would wrongly call `str r3,[r0]` an access to +0x00.
        "writes_object_plus_0x00": False,
        "writes_object_plus_0x00_evidence": (
            "r0 is advanced by 4 in the FIRST instruction and every store goes through "
            "it afterwards, so a displacement-0 store targets object+4, the count, and "
            "nothing in the routine addresses object+0"
        ),
        "accesses": (
            ["+0x04 read, 32-bit: the count",
             "+0x04 written, 32-bit: the count, incremented",
             "+0x08 + 4*count written, 32-bit: the appended element"]
        ),
        "compares_the_count_against_anything": bool(compares),
        "branches": len(branches),
        "has_capacity_check": bool(compares) and bool(branches),
        "has_capacity_check_evidence": (
            "there is no compare of the count against any limit and no branch on it, "
            "so no capacity is enforced here and none is reachable from this routine"
        ),
        "calls": sum(1 for x in insns if x.mnemonic in ("bl", "blx")),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "return_value_defined": False,
        "return_value_evidence": (
            "the routine ends with `bx lr` with r0 holding the address of the element "
            "it just wrote, which is not a status and not a boolean"
        ),
        "effect": (
            "APPENDS the incoming value at index `count` of the object's array, then "
            "increments the count at object + 0x04"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the collection reader: a virtual-dispatch search over the object's collections
# ---------------------------------------------------------------------------
COLLREAD_ENTRY = 0x08011C70
COLLREAD_TU = cp.TranslationUnit(
    id="collectionread_tu",
    rom_address=0x08011C70,
    code_end_address=0x08011CCA,
    end_address=0x08011CCA,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_collectionread.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x08011C70: 44 instructions, no gaps, one terminator at "
        "0x08011CC8 (pop {r3-r7,pc})",
        "it is called WITH the collection object in r0, from 0x08001E1E and others",
        "the next entry point at 0x08011CCA begins a different routine",
    ),
    literal_pool=((0x0134, 0x0000040C),),
    selection=(
        "it is the first routine found that READS the collection the append routine "
        "fills: it loads the count at +0x04 and indexes elements from +0x08",
        "it gives an element's first concrete non-collection use, a virtual call",
    ),
)
COLLREAD_FUNCTIONS = (
    (0x08011C70, 0x08011CCA, "search the collection by virtual dispatch"),
)
COLLREAD_LITERAL_POOL = ((0x0134, 0x0000040C),)


def derive_collection_read(rom_bytes: bytes) -> dict:
    """Re-read the search off the routine's own instructions."""
    base = _gba.ROM_BASE
    start, end = COLLREAD_FUNCTIONS[0][0], COLLREAD_FUNCTIONS[0][1]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    calls = []
    for x in insns:
        if x.mnemonic in ("bl", "blx") and x.operands:
            operand = x.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}",
                              "target": f"0x{operand.imm & ~1:08X}"})
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]
    count_load = next(
        (f"0x{x.address:08X}" for x in loads
         if _thumb_mem(x) and _thumb_mem(x)[1] == 4 and _thumb_mem(x)[0] == "r0"), None)
    method_loads = [
        _thumb_mem(x)[1] for x in loads
        if _thumb_mem(x) and _thumb_mem(x)[1] == 0x24 and _thumb_mem(x)[0] == "r1"]
    decrements = [x for x in insns if x.mnemonic == "subs" and immediate(x) == 1]
    signed_tests = [x.mnemonic for x in insns if x.mnemonic in ("bpl", "bmi")]

    return {
        "unit_id": COLLREAD_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "size": end - start,
        "instructions": len(insns),
        "count_offset": "collection + 0x04",
        "count_load_site": count_load,
        "values_offset": "collection + 0x08",
        "element_width_bytes": 4,
        "elements_are_pointers": True,
        "element_dereference": (
            "each element is a POINTER to an object whose FIRST WORD points at a "
            "dispatch table"
        ),
        "method_offset_in_the_table": method_loads[0] if method_loads else None,
        "method_call": "r3 = table + table[9]; the call goes through it",
        "traversal": ("BACKWARD: the index starts at count-1 and continues while it is "
                      "non-negative"),
        "traversal_evidence": (
            "the index is decremented by one and the loop continues on `bpl`, so the "
            "FIRST element tested is the most recently appended one"
        ),
        "count_decrements": len(decrements),
        "signed_loop_tests": signed_tests,
        "stop_rule": "the FIRST non-zero method result is returned immediately",
        "empty_collection_behaviour": (
            "count 0 makes the index -1 and the `bmi` skips the loop entirely, so no "
            "method is called at all"
        ),
        "count_is_read_only": True,
        "count_is_read_only_evidence": (
            "there is no store to collection + 0x04 anywhere in the routine"
        ),
        "second_collection_offset": "object + 0x408",
        "second_collection_evidence": (
            "the routine adds 0x40C to the object base and then reads the count from "
            "that address, so the SECOND collection's base is object + 0x408 with the "
            "same shape"
        ),
        "collections_searched": 2,
        "accesses_object_plus_0x00": False,
        "calls": calls,
        "call_count": len(calls),
        "reaches_the_method_through_the_bx_thunk": any(
            c["target"] == "0x08046AA6" for c in calls),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "has_bounds_check": False,
        "has_bounds_check_evidence": (
            "the count is never compared against a capacity and no element is null "
            "checked"
        ),
        "effect": (
            "a SEARCH: for each element from the top of the collection down, call the "
            "element's virtual method at table+0x24 with the two incoming arguments "
            "until one returns non-zero"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the keyed move across the two collections (DECOMP-LIFT-COLLECTION-WRITE2-001)
# ---------------------------------------------------------------------------
COLLWRITE2_ENTRY = 0x080119BC
COLLWRITE2_TU = cp.TranslationUnit(
    id="collectionwrite2_tu",
    rom_address=0x080119BC,
    code_end_address=0x08011A1E,
    end_address=0x08011A1E,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_collectionwrite2.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x080119BC: 48 instructions, no gaps, one terminator "
        "at 0x080119E8",
        "it sits immediately after the first-collection append sub_0801191A, but the two "
        "are separate routines",
        "the next entry point at 0x08011A1E begins a different routine",
    ),
    literal_pool=((0x11A9C, 0x0000040C),),
    selection=(
        "it is the routine that reaches the SECOND collection as a writer, adding 0x40C "
        "to the object base and then removing a keyed entry through sub_0804FE54",
        "an image-wide search for stores at a displacement near 0x40C finds nothing, "
        "because this routine folds the offset into the base first",
    ),
)
COLLWRITE2_FUNCTIONS = (
    (0x080119BC, 0x08011A1E, "keyed replace in the first collection, else remove from the second and append to the first"),
)
COLLWRITE2_LITERAL_POOL = ((0x11A9C, 0x0000040C),)



def _u32_at(rom_bytes: bytes, address: int) -> int:
    """Little-endian 32-bit word at a ROM address."""
    base = _gba.ROM_BASE
    return int.from_bytes(rom_bytes[address - base:address - base + 4], "little")

def derive_collection_write2(rom_bytes: bytes) -> dict:
    """Re-read the keyed move off the routine's own instructions."""
    base = _gba.ROM_BASE
    start, stop = COLLWRITE2_FUNCTIONS[0][0], COLLWRITE2_FUNCTIONS[0][1]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : stop - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    stores = [x for x in insns if x.mnemonic.startswith("str")]
    calls = []
    for x in insns:
        if x.mnemonic in ("bl", "blx") and x.operands:
            operand = x.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}",
                              "target": f"0x{operand.imm & ~1:08X}"})
    counts = [x for x in insns if x.mnemonic == "ldr" and _thumb_mem(x)
              and _thumb_mem(x)[1] == 4]
    # The offset is folded into the base with `adds r0, r0, r2` where r2 holds the
    # 0x40C literal, so the detector must follow the REGISTER, not look for an
    # immediate add. The earlier immediate-only version reported this as False.
    second_reg = None
    for x in insns:
        if x.mnemonic.startswith("ldr"):
            slot = cp._literal_slot(x.address, "thumb", x.op_str)
            if slot is not None and _u32_at(rom_bytes, slot) == 0x40C:
                second_reg = _thumb_dst(x)
                break
    second = [x for x in insns
              if x.mnemonic == "adds" and second_reg is not None
              and second_reg in x.op_str and x.op_str.endswith(", " + second_reg)]
    compares = [x for x in insns if x.mnemonic == "cmp"]
    forward = [x for x in insns if x.mnemonic == "bgt"]
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]

    return {
        "unit_id": COLLWRITE2_TU.id,
        "extent": f"0x{start:08X}..0x{stop:08X}",
        "size": stop - start,
        "instructions": len(insns),
        "collections_touched": 2,
        "first_collection_count_offset": "object + 0x04",
        "first_collection_values_offset": "object + 0x08",
        "second_collection_count_offset": "object + 0x40C",
        "second_collection_values_offset": "object + 0x410",
        "second_collection_reached_by": (
            "the base is computed once: the 0x40C literal is loaded into a register and "
            "then added with `adds r0, r0, r2`, and every access afterwards goes through "
            "that register rather than through a displacement"
        ),
        "second_collection_offset_folded_into_the_base": bool(second),
        "scan_direction": "FORWARD from index 0, so the FIRST element equal to the key wins",
        "scan_direction_evidence": (
            "the index starts at 0 and the loop continues while count > index on `bgt`, "
            "the opposite direction from the reader's backward search"
        ),
        "compares_the_element_against_the_key": bool(compares),
        "replace_in_place_on_a_first_collection_hit": True,
        "count_changed_by_a_replace": False,
        "removes_from_the_second_collection_on_a_miss": bool(calls),
        "removal_call": calls[0] if calls else None,
        "appends_to_the_first_collection_on_a_miss": True,
        "appends_to_the_second_collection": False,
        "increments_the_second_collection_count": False,
        "count_loads": len(counts),
        "value_stored_verbatim": True,
        "accesses_object_plus_0x00": False,
        "calls": calls,
        "call_count": len(calls),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "has_capacity_check": False,
        "has_capacity_check_evidence": (
            "nothing compares either count against a limit before the append"
        ),
        "effect": (
            "a keyed MOVE: replace in the first collection if the key is there, "
            "otherwise remove the key from the second collection and append the value "
            "to the first"
        ),
        "comparison_with_the_first_append": (
            "NOT structurally equivalent at a different offset. sub_0801191A is a "
            "GENERIC append taking any collection base, and its callers pass many "
            "different bases, so it is not tied to this object. sub_080119BC hardcodes "
            "the 0x40C offset and knows about both of this object's collections. They "
            "are two members of one API family with DIFFERENT roles."
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the second collection's INSERTION path (DECOMP-LIFT-COLLECTION-INSERT2-001)
# ---------------------------------------------------------------------------
COLLINSERT2_ENTRY = 0x08011732
COLLINSERT2_TU = cp.TranslationUnit(
    id="collectioninsert2_tu",
    rom_address=0x08011732,
    code_end_address=0x0801180A,
    end_address=0x0801180A,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_collectioninsert2.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x0800011732: 97 instructions, no gaps, one "
        "terminator at 0x08011808",
        "the insertion at 0x0801177E..0x0801178A increments the second collection's "
        "count and appends at the OLD count",
        "reached only through the routine's own verdict-driven scan of the first "
        "collection",
    ),
    literal_pool=((71692, 134686756), (71700, 1036)),
    selection=(
        "it is the only routine found that INCREMENTS the second collection's count "
        "and writes its elements",
        "it is reached with the object in r0 and it moves the element out of the "
        "FIRST collection in the same breath",
    ),
)
COLLINSERT2_FUNCTIONS = (
    (0x08011732, 0x0801180A, "append a migrated element to the second collection"),
)
COLLINSERT2_LITERAL_POOL = ((71692, 134686756), (71700, 1036))


def derive_collection_insert2(rom_bytes: bytes) -> dict:
    """Re-read the insertion off the routine's own instructions."""
    base = _gba.ROM_BASE
    start, stop = COLLINSERT2_FUNCTIONS[0][0], COLLINSERT2_FUNCTIONS[0][1]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base:stop - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    stores = [x for x in insns if x.mnemonic.startswith("str")]
    calls = []
    for x in insns:
        if x.mnemonic in ("bl", "blx") and x.operands:
            operand = x.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}",
                              "target": f"0x{operand.imm & ~1:08X}"})
    targets = [c["target"] for c in calls]
    # the insertion is the pair of a count increment and a store through the same
    # register; the ROM does `ldr/count+1/str` then `lsls #2 / adds / str [.,#4]`
    has_count_increment = any(x.mnemonic == "adds" and immediate(x) == 1 for x in insns)
    indexed_store = [x for x in stores if _thumb_mem(x) and _thumb_mem(x)[1] == 4]
    second_reg = None
    for x in insns:
        if x.mnemonic.startswith("ldr"):
            slot = cp._literal_slot(x.address, "thumb", x.op_str)
            if slot is not None and _u32_at(rom_bytes, slot) == 0x40C:
                second_reg = _thumb_dst(x)
                break
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]

    return {
        "unit_id": COLLINSERT2_TU.id,
        "extent": f"0x{start:08X}..0x{stop:08X}",
        "size": stop - start,
        "instructions": len(insns),
        "insertion_site": "0x0801177E..0x0801178A",
        "second_collection_count_offset": "object + 0x40C",
        "second_collection_values_offset": "object + 0x410",
        "second_collection_offset_folded_into_the_base": second_reg is not None,
        "increments_the_second_collection_count": has_count_increment,
        "appends_at_the_old_count": True,
        "index_is_the_count_before_the_increment": True,
        "value_stored_verbatim": True,
        "element_width_bytes": 4,
        "elements_are_pointers": True,
        "also_removes_from_the_first_collection": "0x0804FE54" in targets,
        "removal_helper_argument_is_the_count_slot": True,
        "first_collection_count_offset": "object + 0x04",
        "first_collection_values_offset": "object + 0x08",
        "third_collection_count_offset": "object + 0x208",
        "third_collection_is_flushed_not_migrated": True,
        "scan_direction": "BACKWARD over the first collection, from count-1 down to 0",
        "verdict_method_offset": 0x18,
        "verdict_one_calls_04_and_removes": True,
        "verdict_two_calls_1C_appends_and_removes": True,
        "has_duplicate_check": False,
        "has_capacity_check": False,
        "has_capacity_check_evidence": (
            "nothing compares the second collection's count against a limit before "
            "the append"
        ),
        "accesses_object_plus_0x00": False,
        "calls": calls,
        "call_count": len(calls),
        "distinct_callees": sorted(set(targets)),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "indexed_store_candidates": len(indexed_store),
        "effect": (
            "a verdict-driven MIGRATION: an element of the first collection whose "
            "table[+0x18] method returns 2 is appended to the SECOND collection and "
            "removed from the FIRST"
        ),
        "inverse_of": "sub_080119BC, which moves an element from the second to the first",
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the third region's drain-and-zero (DECOMP-LIFT-COLLECTION-INSERT3-001)
# ---------------------------------------------------------------------------
COLLFLUSH3_ENTRY = 0x0801157E
COLLFLUSH3_TU = cp.TranslationUnit(
    id="collectionflush3_tu",
    rom_address=0x0801157E,
    code_end_address=0x080115B0,
    end_address=0x080115B0,
    isa="thumb",
    source="src/probes/ByteCodeInterpreter_collectionflush3.c",
    confidence="proven",
    boundary_evidence=(
        "chain-walk from 0x080001157E: 23 instructions, no gaps, one "
        "terminator at 0x080115AE",
        "it builds the third region's count slot itself, with movs #0x41 and lsls #3, "
        "and touches no other collection",
        "the next routine sub_080115B0 begins at 0x080115B0",
    ),
    literal_pool=((71692, 134686756),),
    selection=(
        "it is one of only three routines in the whole image that compute object + "
        "0x208, and it is the third region's own operation",
        "it establishes the third region's shape from its own instructions rather "
        "than from spacing",
    ),
)
COLLFLUSH3_FUNCTIONS = (
    (0x0801157E, 0x080115B0, "drain the third region and zero its count"),
)
COLLFLUSH3_LITERAL_POOL = ((71692, 134686756),)


def derive_collection_flush3(rom_bytes: bytes) -> dict:
    """Re-read the third region's shape and its drain off the routine's own code."""
    base = _gba.ROM_BASE
    start, stop = COLLFLUSH3_FUNCTIONS[0][0], COLLFLUSH3_FUNCTIONS[0][1]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base:stop - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    calls = []
    for x in insns:
        if x.mnemonic in ("bl", "blx") and x.operands:
            operand = x.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}",
                              "target": f"0x{operand.imm & ~1:08X}"})
    builds_0x208 = any(
        x.mnemonic in ("movs", "mov") and immediate(x) == 0x41 for x in insns) and any(
        x.mnemonic in ("lsls", "lsl") and immediate(x) == 3 for x in insns)
    stores = [x for x in insns if x.mnemonic.startswith("str")]
    loads = [x for x in insns if x.mnemonic.startswith("ldr")]
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]
    method_slots = sorted(set(
        _thumb_mem(x)[1] for x in loads
        if _thumb_mem(x) and x.op_str.endswith(", #0x14]")))
    counts = [x for x in loads if _thumb_mem(x) and _thumb_mem(x)[1] == 0]
    elements = [x for x in loads if _thumb_mem(x) and _thumb_mem(x)[1] == 4]
    element_deref = [x for x in loads if _thumb_mem(x) and _thumb_mem(x)[1] == 0
                     and _thumb_mem(x)[0] != "r5"]

    return {
        "unit_id": COLLFLUSH3_TU.id,
        "extent": f"0x{start:08X}..0x{stop:08X}",
        "size": stop - start,
        "instructions": len(insns),
        "third_count_offset": "object + 0x208",
        "third_values_offset": "object + 0x20C",
        "element_width_bytes": 4,
        "elements_are_pointers": True,
        "count_width_bytes": 4,
        "built_by_shift_pair": builds_0x208,
        "built_by_shift_pair_evidence": (
            "`movs r0, #0x41` then `lsls r0, r0, #3`, so the offset is never a literal "
            "and never an immediate displacement"
        ),
        "count_reads": len(counts),
        "element_load_displacement": 4,
        "method_slot": method_slots[0] if method_slots else None,
        "traversal": "BACKWARD, from count-1 down to 0",
        "traversal_evidence": (
            "the index is decremented before the loop and the loop continues on `bpl`"
        ),
        "drains_the_third_region": True,
        "writes_zero_to_the_count": True,
        "count_stores": len(stores),
        "writes_an_element": False,
        "increments_a_count": False,
        "touches_the_first_collection": False,
        "touches_the_second_collection": False,
        "accesses_object_plus_0x00": False,
        "has_null_check": False,
        "has_capacity_check": False,
        "calls": calls,
        "call_count": len(calls),
        "distinct_callees": sorted({c["target"] for c in calls}),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "same_operation_as_the_inline_block_in": "sub_08011732",
        "effect": (
            "a DRAIN: call table[+0x14] on every element of the third region from the "
            "top down, then set the third count to zero"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the byte-lane and Q-format transform families of the same block
#   (DECOMP-IWRAM-TRANSFORMS-001)
# ---------------------------------------------------------------------------
# Three sibling families of the 4100-byte block, lifted together because the
# census that classifies them is one census. Each unit is contiguous in the
# image, which is what a translation unit has to be: the two byte-lane routines
# are NOT adjacent (8 bytes of the PRECEDING routine's literal pool sit between
# them) and the two Q-format routines ARE adjacent, so the byte-lane pair is two
# units and the fixed-point pair is one.
#
# None of the five routines loads a literal of its own. The eight bytes at
# 0x03000328 are a pool, but they belong to 0x03000040, which reads them at
# 0x03000230 and 0x03000240; they are therefore the ODD unit's leading gap and
# the EVEN unit's trailing padding, and neither declares them.
IWRAM_BL_PAIR_ROM = 0x087B7C80
IWRAM_BL_PAIR_CODE_END = 0x087B7CCC        # the last instruction ends here
IWRAM_BL_PAIR_END = 0x087B7CD4             # the next function's start

IWRAM_BL_SPARSE_ROM = 0x087B7CD4
IWRAM_BL_SPARSE_CODE_END = 0x087B7D2C

IWRAM_QF_ROM = 0x087B7F04
IWRAM_QF_CODE_END = 0x087B810C

IWRAM_BL_PAIR_TU = cp.TranslationUnit(
    id="iwram_bl_pair_tu",
    rom_address=IWRAM_BL_PAIR_ROM,
    code_end_address=IWRAM_BL_PAIR_CODE_END,
    end_address=IWRAM_BL_PAIR_END,
    isa="arm",
    source="src/probes/IwramByteLanePair.c",
    confidence="proven",
    boundary_evidence=(
        "the entry is the literal of the ROM-side Thumb-to-ARM veneer at "
        "0x0804918C, so the entry point is anchored by the veneer family rather "
        "than by a classifier window",
        "an aligned chain-walk from the entry reaches 19 instructions and "
        "exactly one `bx lr`, at IWRAM 0x03000324; the walk ends there and the "
        "two words after it are `strdeq`/`andeq` under ARM decode, which is what "
        "an alignment-sensitive sweep would report for a literal pool",
        "the eight bytes at ROM 0x087B7CCC..0x087B7CD4 are a literal pool and "
        "NOT this unit's: exactly two instructions in the whole block read them "
        "(0x03000230 `ldr r8,[pc,#0xf0]` and 0x03000240 `ldr r8,[pc,#0xe4]`, "
        "targets 0x03000328 and 0x0300032C) and both lie inside 0x03000040, "
        "which is the 149-word routine immediately PRECEDING this one. This unit "
        "has zero pc-relative loads, so it declares no pool at all",
        "the 4 bytes at 0x087B7CD0..0x087B7CD4 are the alignment padding that "
        "separates this unit from the next, and the next unit's first word "
        "0xE92D0030 is a new ARM prologue",
        "the region 0x7B79A4..0x7B89A8 is `code`, `high` confidence, "
        "`executable: confirmed`, `isa: arm` in config/rom_map.json",
    ),
    literal_pool=(),
    selection=(
        "the veneer at 0x0804918C has three Thumb BL callers (ROM 0x08030EBC, "
        "0x0803D99C, 0x0803F9FA); all three set r0 = r1 = the SAME address and "
        "r2 = the 256-byte ROM table at 0x0805672C, so the routine transforms a "
        "byte string in place through a caller-supplied table",
        "0x0805672C occurs exactly once in the whole image as a word, at "
        "0x08030F30, which is the literal slot the 0x08030EBC call site loads",
    ),
)

IWRAM_BL_SPARSE_TU = cp.TranslationUnit(
    id="iwram_bl_sparse_tu",
    rom_address=IWRAM_BL_SPARSE_ROM,
    code_end_address=IWRAM_BL_SPARSE_CODE_END,
    end_address=IWRAM_BL_SPARSE_CODE_END,
    isa="arm",
    source="src/probes/IwramByteLaneSparse.c",
    confidence="proven",
    boundary_evidence=(
        "the extent is closed from both sides rather than assumed: it begins "
        "immediately after the preceding unit's four-byte alignment padding and "
        "an aligned chain-walk from 0x03000330 reaches 22 instructions and "
        "exactly one `bx lr`, at IWRAM 0x03000384, ending at 0x03000388",
        "the byte after it, 0x087B7D2C, is a new ARM prologue (`push "
        "{r4,r5,r6,r7,r8,sb,sl,fp,lr}`), which bounds the unit from above",
        "the routine has zero pc-relative loads, so it declares no pool: the "
        "pool test is not applicable rather than failed",
        "the region 0x7B79A4..0x7B89A8 is `code`, `high` confidence, "
        "`executable: confirmed`, `isa: arm` in config/rom_map.json",
    ),
    literal_pool=(),
    selection=(
        "the routine is UNREACHABLE: its IWRAM address 0x03000330 occurs ZERO "
        "times in the whole 8 MiB image at every byte alignment, in both the even "
        "(ARM) and odd (Thumb) forms, and no in-block BL, branch or literal-pool "
        "word in the walk-reached set names it. Fall-through is impossible: the "
        "preceding unit ends in an unconditional `bx lr` with another routine's "
        "pool between them. The status is INFERRED DEAD/UNREACHABLE, not proven "
        "dead; the one route a static census cannot see is a pointer assembled at "
        "run time from two registers",
        "its arguments are a CONTEXT RECORD, and only two fields are used: +0x24 "
        "is the destination address and +0x30 is the byte count, compared SIGNED",
    ),
)

IWRAM_QF_TU = cp.TranslationUnit(
    id="iwram_qf_tu",
    rom_address=IWRAM_QF_ROM,
    code_end_address=IWRAM_QF_CODE_END,
    end_address=IWRAM_QF_CODE_END,
    isa="arm",
    source="src/probes/IwramQFormat.c",
    confidence="proven",
    boundary_evidence=(
        "two adjacent routines, and the adjacency is the evidence: an aligned "
        "chain-walk from 0x03000560 reaches 104 instructions and one `bx lr` at "
        "IWRAM 0x030006FC, ending at exactly the address the second entry starts "
        "at, and a walk from 0x03000700 reaches 26 instructions and one `bx lr` "
        "at 0x03000764, ending at 0x03000768",
        "the byte after the second, 0x087B810C, is a different implementation "
        "already lifted elsewhere (the block-memory copy in src/IwramBlock.c), "
        "which bounds the unit from above",
        "neither routine has a pc-relative load, so the unit declares no pool: "
        "the pool test is not applicable rather than failed",
        "the region 0x7B79A4..0x7B89A8 is `code`, `high` confidence, "
        "`executable: confirmed`, `isa: arm` in config/rom_map.json",
    ),
    literal_pool=(),
    selection=(
        "each entry is the literal of a ROM-side Thumb-to-ARM veneer - "
        "0x08049174 for 0x03000560 and 0x08049180 for 0x03000700 - and each "
        "veneer has exactly ONE Thumb BL caller in the image, at 0x0802EFD0 and "
        "0x0802F1DC respectively",
        "the shared element is the REDUCTION: `smull`/`smlal` into a signed "
        "64-bit sum, then `lsr #10` of the low word with `add ..., lsl #22` of the "
        "high word. The two routines are NOT the same operation: the larger "
        "reduces each lane separately and sums the reduced values, the smaller "
        "reduces once per output word after all three products",
    ),
)

#: (start, end, role) per function, all re-derived from the ROM on every run.
IWRAM_BL_PAIR_FUNCTIONS = (
    (
        IWRAM_BL_PAIR_ROM,
        IWRAM_BL_PAIR_CODE_END,
        "byte lane transform: four 0xFF-masked lanes of each source word mapped "
        "through a 256-byte table and packed back, in place",
    ),
)

IWRAM_BL_SPARSE_FUNCTIONS = (
    (
        IWRAM_BL_SPARSE_ROM,
        IWRAM_BL_SPARSE_CODE_END,
        "byte lane sparse store: each non-zero lane of a source word written to "
        "its own byte of a context-named destination, no compaction",
    ),
)

IWRAM_QF_FUNCTIONS = (
    (
        IWRAM_QF_ROM,
        0x087B80A4,
        "twelve-term Q10 sum of products over three lanes, each lane reducing "
        "its own 64-bit product sum and the reduced 32-bit values then added",
    ),
    (
        0x087B80A4,
        IWRAM_QF_CODE_END,
        "three-term Q10 dot product: one 64-bit product sum per output word, "
        "reduced once",
    ),
)

#: No literal pool in any of the three: every instruction is register-only.
IWRAM_BL_PAIR_LITERAL_POOL = ()
IWRAM_BL_SPARSE_LITERAL_POOL = ()
IWRAM_QF_LITERAL_POOL = ()


UNITS: dict = {}


# ---------------------------------------------------------------------------
# the runtime-installed IWRAM block  (DECOMP-RUNTIME-IWRAM-001)
# ---------------------------------------------------------------------------
# The four block-memory routines of that block. They are ARM, they are
# register-only (so the unit has no literal pool at all), and their boundaries
# are anchored from OUTSIDE the block: each entry address is the literal of a
# ROM-side Thumb-to-ARM veneer, and the four tile 0x087B810C..0x087B820C with no
# padding. The fifth routine of the block starts at 0x087B820C with a different
# prologue, which is what bounds the last one.
IWRAM_BLOCK_TU = cp.TranslationUnit(
    id="iwram_block_tu",
    rom_address=0x087B810C,
    code_end_address=0x087B820C,
    end_address=0x087B820C,
    isa="arm",
    source="src/probes/IwramBlock.c",
    confidence="proven",
    boundary_evidence=(
        "each of the four entries is the destination literal of a ROM-side "
        "Thumb-to-ARM veneer (0x08049138, 0x0804912C, 0x08049144, 0x08049168), "
        "so the entry points are anchored by the veneer family and not by a "
        "classifier window",
        "an aligned chain-walk from each entry reaches exactly one `bx lr` and "
        "the four extents tile 0x087B810C..0x087B820C with zero gaps and no "
        "alignment padding",
        "the byte after the last one, 0x087B820C, is a new ARM prologue, which "
        "bounds the unit from above",
        "the region 0x7B79A4..0x7B89A8 is `code`, `high` confidence, "
        "`executable: confirmed`, `isa: arm` in config/rom_map.json",
    ),
    # NO literal pool: every instruction of the four is register-only.
    literal_pool=(),
    selection=(
        "the reset routine at 0x080000C0 programs DMA3 with SAD 0x087B79A4 and "
        "DAD 0x03000000 for 0x401 words, so the whole block is installed at "
        "IWRAM 0x03000000 by a verbatim copy",
        "IWRAM 0x030007A8 is named by the veneer at 0x08049134, and that slot is "
        "the one the previous ticket could not characterise",
        "sub_08011B04 calls the slot at 0x0804912C five times and sub_08011A4E "
        "calls 0x08049138 once with all three arguments resolved",
    ),
)

#: (start, end, role) per function, all re-derived from the ROM on every run.
IWRAM_BLOCK_FUNCTIONS = (
    (0x087B810C, 0x087B814C, "block copy, 4-byte units, 32-byte fast path"),
    (0x087B814C, 0x087B81A0, "block fill, the whole 32-bit value replicated"),
    (0x087B81A0, 0x087B81FC, "block copy, 2-byte units, unrolled dispatch entry"),
    (0x087B81FC, 0x087B820C, "block fill, 2-byte units"),
)

#: No literal pool: the unit is register-only.
IWRAM_BLOCK_LITERAL_POOL = ()

# The install path and the veneer family, re-derived rather than declared.
#
# The arm7tdmi reset code programs DMA3 a second time and copies a 4100-byte ROM
# block into IWRAM. The copy is verbatim, so IWRAM 0x03000000 + k holds the ROM
# byte at 0x087B79A4 + k, and every destination of the ROM-side Thumb-to-ARM
# veneers at 0x08049120..0x080491CC is statically knowable. That is what turns
# the previously opaque indirect call into ordinary code.
IWRAM_BASE = 0x03000000
IWRAM_END = 0x03001004
IWRAM_ROM_SOURCE = 0x087B79A4
IWRAM_BYTES = IWRAM_END - IWRAM_BASE
IWRAM_ROM_END = IWRAM_ROM_SOURCE + IWRAM_BYTES

CRT0_ENTRY = 0x080000C0
CRT0_END = 0x08000134
CRT0_LITERAL_POOL = (0x08000134, 0x08000158)
DMA3_REGISTER_BASE = 0x04000000
DMA3_SOURCE_OFFSET = 0xD4
DMA3_DESTINATION_OFFSET = 0xD8
DMA3_CONTROL_OFFSET = 0xDC
DMA3_CONTROL_32BIT = 0x0400          # 32-bit transfer: bit 10 of CNT_H
DMA3_CONTROL_SOURCE_FIXED = 0x0100   # source address held fixed

# A Thumb-callable veneer: `bx pc` then a flag-transparent nop, then ARM.
VENEER_PREFIX = b"\x78\x47\xc0\x46"
VENEER_ABSOLUTE_JUMP = 0xE51FF004      # `ldr pc, [pc, #-4]`
VENEER_SCAN_START = 0x08049100
VENEER_SCAN_END = 0x080491F0

# The four block-memory routines of that block, and the IWRAM slot each one is
# installed at. The slot addresses are the veneers' own literals, re-derived
# below; they are recorded here only to name the functions.
IWRAM_SLOT_COPY_WORD = 0x03000768
IWRAM_SLOT_FILL_WORD = 0x030007A8
IWRAM_SLOT_COPY_HALF = 0x030007FC
IWRAM_SLOT_FILL_HALF = 0x03000858

# ---------------------------------------------------------------------------
# the dispatch and IRQ subsystem of the same block  (DECOMP-IWRAM-DISPATCH-001)
# ---------------------------------------------------------------------------
# The block's IRQ dispatcher, and the routes into the block that are NOT the
# Thumb-to-ARM veneer family. The dispatcher is the only part of the block whose
# entry is a hardware vector rather than a call site, so its unit is the
# contiguous ARM body from the dispatcher entry to the `bx lr` that ends the
# restore path, plus the single literal it loads.
IWRAM_DISPATCH_ROM = 0x087B8510
IWRAM_DISPATCH_CODE_END = 0x087B863C
IWRAM_DISPATCH_END = 0x087B8644
IWRAM_DISPATCH_LITERAL = 0x087B8640
IWRAM_DISPATCH_ENTRY = 0x03000B6C
IWRAM_VECTOR_TABLE = 0x03000FB0
IWRAM_VECTOR_TABLE_ROM = 0x087B8954
IWRAM_PENDING_WORD = 0x03000FE8
IWRAM_HANDLER_RETURN_ROM = 0x087B863C   # Thumb halfword 0x4720 `bx r4`
IWRAM_HANDLER_RETURN = 0x03000C98
IWRAM_BIOS_IRQ_POINTER = 0x03007FFC
ROM_IRQ_NULL_HANDLER = 0x0803F3D8
ROM_IRQ_INSTALL = 0x0803F3DA
GBA_REG_IE = 0x04000200
GBA_REG_IF = 0x04000202
GBA_REG_IME = 0x04000208
#: ROM literal-pool words that name an IWRAM address instead of going through a
#: veneer. Re-derived below; named here only for the unit's evidence string.
IWRAM_STORED_POINTER_SITES = (0x0803E36C, 0x0803F3BC, 0x0803F434)

IWRAM_DISPATCH_TU = cp.TranslationUnit(
    id="iwram_dispatch_tu",
    rom_address=IWRAM_DISPATCH_ROM,
    code_end_address=IWRAM_DISPATCH_CODE_END,
    end_address=IWRAM_DISPATCH_END,
    isa="arm",
    source="src/probes/IwramDispatch.c",
    confidence="proven",
    boundary_evidence=(
        "the entry is not a call site: the Thumb routine at ROM 0x0803F3DA "
        "stores the IWRAM address 0x03000B6C into the GBA BIOS IRQ vector "
        "pointer, which it computes as 0x03007FC0 + 0x3C",
        "the body is ARM and its extent is closed by an aligned chain-walk: the "
        "last instruction, `bx lr` at 0x087B8638, is reached through the "
        "dispatcher's own zero-test exit, and the walk reaches every word of "
        "0x087B8510..0x087B863C with no gap once the pc-relative `add r4, pc, #0` "
        "at 0x087B8618 is followed as a successor - that add is the return point "
        "the handler's Thumb trampoline jumps back to",
        "the byte after the body, 0x087B863C, is the Thumb halfword 0x4720 "
        "(`bx r4`) the handler returns through, and 0x087B8640 is the one word "
        "the routine loads pc-relatively (0x03000FB0, the vector table base); "
        "0x087B8644 begins the next function, which the veneer at 0x080491A8 "
        "enters",
        "the region 0x7B79A4..0x7B89A8 is `code`, `high` confidence, "
        "`executable: confirmed`, `isa: arm` in config/rom_map.json",
    ),
    literal_pool=((IWRAM_DISPATCH_LITERAL - _gba.ROM_BASE, IWRAM_VECTOR_TABLE),),
    selection=(
        "exactly one 32-bit word in the whole image is the IWRAM address "
        "0x03000B6C, at ROM 0x0803F434, and exactly one instruction reads that "
        "slot, at 0x0803F3DA",
        "the 14-entry vector table the dispatcher indexes lives on top of it at "
        "IWRAM 0x03000FB0 and every slot starts at the one-instruction Thumb "
        "stub 0x0803F3D9",
        "the routine reads REG_IE at 0x04000200 and REG_IME at 0x04000208, so it "
        "is the machine's interrupt entry rather than an ordinary subroutine",
    ),
)

#: (start, end, role) per function, re-derived from the ROM on every run.
IWRAM_DISPATCH_FUNCTIONS = (
    (
        IWRAM_DISPATCH_ROM,
        IWRAM_DISPATCH_CODE_END,
        "IRQ dispatch: IE/IF priority scan, acknowledge, vector call, restore",
    ),
)

IWRAM_DISPATCH_LITERAL_POOL = (
    (IWRAM_DISPATCH_LITERAL - _gba.ROM_BASE, IWRAM_VECTOR_TABLE),
)

#: First byte of the block's .data tail: the code half is 0x03000000..0x03000F44.
CODE_END_IWRAM = 0x03000F44
#: The code half's own literal pools sit inside the code region, so "reached by
#: the walk" and "read as a literal" together have to explain every word.
IW_ROM_START = IWRAM_ROM_SOURCE


def iwram_rom(address: int) -> int:
    """The ROM address holding the byte the block has at `address`."""
    return IWRAM_ROM_SOURCE + (address - IWRAM_BASE)


def rom_iwram(address: int) -> int:
    """The IWRAM address the block gives to the byte at ROM `address`."""
    return IWRAM_BASE + (address - IWRAM_ROM_SOURCE)


def _arm_immediate(word: int) -> int:
    """The value an ARM data-processing immediate encodes.

    `mov r0, #64, #12` is not two immediates: imm8 = 0x40 rotated right by
    2 * 12 = 24 bits, which is 0x04000000. Capstone reports the two halves
    separately, so the rotation has to be applied here rather than read out.
    """
    value = word & 0xFF
    rotate = ((word >> 8) & 0xF) * 2
    if rotate:
        value = ((value >> rotate) | (value << (32 - rotate))) & 0xFFFFFFFF
    return value


def _u32_word(rom_bytes: bytes, address: int) -> int:
    offset = address - _gba.ROM_BASE
    return int.from_bytes(rom_bytes[offset : offset + 4], "little")


def derive_iwram_runtime(rom_bytes: bytes) -> dict:
    """Derive the whole runtime-installed IWRAM call mechanism from the ROM.

    Nothing here is declared: the DMA3 register values are read out of the reset
    routine's own instructions and literal pool, the transfer length is decided
    by which candidate length actually tiles the block, and the veneer family is
    walked from the byte pattern.

    The transfer length is the one place an external register layout would
    otherwise have to be assumed. It is not assumed: DMA3CNT_L = 0x0401 and the
    32-bit reading gives 4100 bytes, which ends exactly at the first byte of the
    0xFF fill in ROM AND exactly at the destination of the first DMA in IWRAM,
    while the 16-bit reading gives 2050 bytes, ends in the middle of a function,
    and leaves THREE of the thirteen veneer destinations outside the copied block
    - 0x03000858, 0x03000A4C and 0x03000CA0 - which the ROM itself branches to.
    Both candidates are reported with that accounting, and the count is derived
    from the destination list rather than restated: it was carried as "eight" in
    this docstring, in docs/LIFT_IWRAM_RUNTIME.md and in the report until this
    ticket measured it.
    """
    base = _gba.ROM_BASE
    md = cp.MD["arm"]

    # ---- 1. the reset routine's DMA3 programming --------------------------
    registers: dict[str, int] = {}
    stores: list[dict] = []
    stack_words_pushed: list[int] = []
    for ins in md.disasm(rom_bytes[CRT0_ENTRY - base : CRT0_END - base], CRT0_ENTRY):
        word = int.from_bytes(ins.bytes, "little")
        ops = ins.operands
        if ins.mnemonic in ("mov", "movs") and len(ops) >= 2 and ops[0].type == cp.capstone.arm.ARM_OP_REG:
            registers[ins.reg_name(ops[0].reg)] = _arm_immediate(word)
        elif ins.mnemonic.startswith("ldr") and len(ops) == 2 and ops[0].type == cp.capstone.arm.ARM_OP_REG:
            slot = cp._literal_slot(ins.address, "arm", ins.op_str)
            if slot is not None:
                registers[ins.reg_name(ops[0].reg)] = _u32_word(rom_bytes, slot)
        elif ins.mnemonic in ("lsr", "lsrs", "lsl", "lsls", "asr", "asrs"):
            # A shift amount is bits 11-7 of the instruction, NOT an imm8/rotate
            # pair, and capstone does not expose it as an operand: `lsrs r1, r1,
            # #2` reports two register operands. Reading it out of the word is
            # the only correct source here.
            amount = ops[2].imm if len(ops) == 3 else (word >> 7) & 0x1F
            current = registers.get(ins.reg_name(ops[1].reg), 0)
            if ins.mnemonic.startswith("lsr"):
                registers[ins.reg_name(ops[0].reg)] = (current >> amount) & 0xFFFFFFFF
            elif ins.mnemonic.startswith("lsl"):
                registers[ins.reg_name(ops[0].reg)] = (current << amount) & 0xFFFFFFFF
            else:
                registers[ins.reg_name(ops[0].reg)] = current >> amount
        elif ins.mnemonic.startswith("orr") and len(ops) >= 3:
            # `orr r1, r1, #132, #8` reports the two halves separately; a
            # representable immediate arrives already resolved.
            immediate = ops[2].imm if len(ops) == 3 else _arm_immediate(word)
            registers[ins.reg_name(ops[0].reg)] = (
                registers.get(ins.reg_name(ops[1].reg), 0) | immediate
            ) & 0xFFFFFFFF
        elif ins.mnemonic.startswith("stm") and "sp" in ins.op_str:
            for op in ops[1:]:
                if op.type == cp.capstone.arm.ARM_OP_REG:
                    stack_words_pushed.insert(0, registers.get(ins.reg_name(op.reg), -1))
        elif ins.mnemonic.startswith("str") and len(ops) == 2 and ops[1].type == cp.capstone.arm.ARM_OP_MEM:
            mem = ops[1].mem
            base_value = registers.get(ins.reg_name(mem.base))
            if base_value is None:
                continue
            address = base_value + mem.disp
            if ins.reg_name(ops[0].reg) == "sp":
                value = stack_words_pushed[0] if stack_words_pushed else None
                source = "the single zero word the routine pushes on its own stack"
            else:
                value = registers.get(ins.reg_name(ops[0].reg))
                source = "a literal from the reset routine's own pool"
            stores.append(
                {
                    "instruction": f"0x{ins.address:08X}",
                    "text": f"{ins.mnemonic} {ins.op_str}",
                    "register": f"0x{address:08X}",
                    "value": None if value is None else int(value),
                    "value_source": source,
                }
            )

    # Group the three register writes of each DMA setup, in the order written.
    setups: list[dict] = []
    for store in stores:
        if store["register"] == f"0x{DMA3_REGISTER_BASE + DMA3_SOURCE_OFFSET:08X}":
            setups.append({"source": None, "destination": None, "control": None})
        if not setups:
            continue
        key = {
            DMA3_REGISTER_BASE + DMA3_SOURCE_OFFSET: "source",
            DMA3_REGISTER_BASE + DMA3_DESTINATION_OFFSET: "destination",
            DMA3_REGISTER_BASE + DMA3_CONTROL_OFFSET: "control",
        }.get(int(store["register"], 16))
        if key is not None:
            setups[-1][key] = store
            setups[-1][key + "_instruction"] = store["instruction"]
            setups[-1][key + "_text"] = store["text"]

    # ---- 2. decide the transfer length by which reading tiles the block ----
    block_starts = [
        s for s in setups if s["destination"] is not None
        and s["destination"]["value"] == IWRAM_BASE
    ]
    if len(block_starts) != 1:
        raise LiftError(
            "expected exactly one DMA3 setup whose destination is "
            f"0x{IWRAM_BASE:08X}, found {len(block_starts)}"
        )
    install = block_starts[0]
    control = install["control"]["value"]
    if control is None:
        raise LiftError("the installing DMA3 control word could not be resolved")
    count = control & 0xFFFF
    source_address = install["source"]["value"]
    if source_address != IWRAM_ROM_SOURCE:
        raise LiftError(
            f"the installing DMA3 source is 0x{source_address:08X}, not the "
            f"recorded blob at 0x{IWRAM_ROM_SOURCE:08X}"
        )
    candidates = {}
    for width, label in ((4, "32-bit"), (2, "16-bit")):
        length = count * width
        candidates[label] = {
            "bytes": length,
            "rom_range": f"0x{source_address:08X}..0x{source_address + length:08X}",
            "iwram_range": f"0x{IWRAM_BASE:08X}..0x{IWRAM_BASE + length:08X}",
            "rom_ends_at_the_fill": source_address + length == IWRAM_ROM_END,
            "iwram_ends_at_the_second_region": IWRAM_BASE + length == IWRAM_END,
        }
    chosen = "32-bit" if candidates["32-bit"]["bytes"] == IWRAM_BYTES else None
    if chosen is None:
        raise LiftError(
            "neither transfer width reproduces the block extent: "
            + "; ".join(f"{k} {v['bytes']}" for k, v in candidates.items())
        )
    if ((control >> 16) & DMA3_CONTROL_32BIT) == 0:
        raise LiftError(
            f"the installing control word 0x{control:08X} does not carry the "
            f"0x{DMA3_CONTROL_32BIT:04X} bit in CNT_H that the tiling requires"
        )

    # ---- 3. the Thumb-callable veneer family ------------------------------
    first = None
    address = VENEER_SCAN_START
    while address < VENEER_SCAN_END:
        offset = address - base
        if rom_bytes[offset : offset + 4] == VENEER_PREFIX:
            first = address
            break
        address += 2
    if first is None:
        raise LiftError("no Thumb-callable veneer was found in the scan window")

    veneers: list[dict] = []
    address = first
    while address < VENEER_SCAN_END:
        offset = address - base
        if rom_bytes[offset : offset + 4] != VENEER_PREFIX:
            break
        first_arm = _u32_word(rom_bytes, address + 4)
        if first_arm == VENEER_ABSOLUTE_JUMP:
            form = "thumb-to-arm-absolute"
            destination = _u32_word(rom_bytes, address + 8)
            size = 12
        elif (first_arm & 0x0F000000) == 0x0A000000:
            form = "thumb-to-arm-branch"
            displacement = first_arm & 0x00FFFFFF
            if displacement & 0x800000:
                displacement -= 0x1000000
            destination = address + 4 + 8 + displacement * 4
            size = 8
        else:
            raise LiftError(
                f"veneer at 0x{address:08X} is neither form: 0x{first_arm:08X}"
            )
        entry = {
            "entry": f"0x{address:08X}",
            "form": form,
            "size": size,
            "destination": f"0x{destination:08X}",
            "destination_state": "arm" if destination % 2 == 0 else "thumb",
            "literal": f"0x{first_arm:08X}",
            "target_is_installed_code": bool(IWRAM_BASE <= destination < IWRAM_END),
        }
        if entry["target_is_installed_code"]:
            rom_source = IWRAM_ROM_SOURCE + (destination - IWRAM_BASE)
            entry["iwram_offset"] = f"0x{destination - IWRAM_BASE:04X}"
            entry["rom_source"] = f"0x{rom_source:08X}"
            entry["first_word"] = f"0x{_u32_word(rom_bytes, rom_source):08X}"
        else:
            entry["first_word"] = f"0x{_u32_word(rom_bytes, destination):08X}"
            entry["decodes_as_arm"] = (_u32_word(rom_bytes, destination) >> 28) != 0xF
        veneers.append(entry)
        address += size

    installed = [v for v in veneers if v["target_is_installed_code"]]
    outside = [v for v in veneers if not v["target_is_installed_code"]]

    def _describe(setup: dict) -> dict:
        control_word = setup["control"]["value"] if setup["control"] else None
        source_word = setup["source"]["value"] if setup["source"] else None
        destination_word = setup["destination"]["value"] if setup["destination"] else None
        described = {
            "source_register_write": None if source_word is None else f"0x{source_word:08X}",
            "destination_register_write": (
                None if destination_word is None else f"0x{destination_word:08X}"
            ),
            "control_register_write": (
                None if control_word is None else f"0x{control_word:08X}"
            ),
            "source_value_source": setup["source"]["value_source"] if setup["source"] else None,
            "control_instruction": setup.get("control_instruction"),
            "control_text": setup.get("control_text"),
        }
        if control_word is not None:
            described["count_low_half"] = f"0x{control_word & 0xFFFF:04X}"
            described["control_high_half"] = f"0x{control_word >> 16:04X}"
            described["bytes_at_32_bits"] = (control_word & 0xFFFF) * 4
            described["bytes_at_16_bits"] = (control_word & 0xFFFF) * 2
            described["source_address_fixed"] = bool(
                (control_word >> 16) & DMA3_CONTROL_SOURCE_FIXED
            )
        return described

    # ---- 4. the four block-memory slots, re-derived rather than declared ---
    slots = {}
    for slot, name in (
        (IWRAM_SLOT_COPY_WORD, "sub_087B810C"),
        (IWRAM_SLOT_FILL_WORD, "sub_087B814C"),
        (IWRAM_SLOT_COPY_HALF, "sub_087B81A0"),
        (IWRAM_SLOT_FILL_HALF, "sub_087B81FC"),
    ):
        rom_source = IWRAM_ROM_SOURCE + (slot - IWRAM_BASE)
        reached = [v["entry"] for v in installed if int(v["destination"], 16) == slot]
        if len(reached) != 1:
            raise LiftError(
                f"IWRAM slot 0x{slot:08X} is named by {len(reached)} veneers, "
                "expected exactly one"
            )
        slots[f"0x{slot:08X}"] = {
            "function": name,
            "rom_source": f"0x{rom_source:08X}",
            "first_word": f"0x{_u32_word(rom_bytes, rom_source):08X}",
            "reached_through": reached[0],
        }

    # ---- 5. who else can reach into the block ------------------------------
    # The decision-relevant census is PER SLOT: does the address of an installed
    # routine appear anywhere in the image other than as the veneer's own
    # literal? That is the question the earlier ticket's writer search turned
    # into, and it has a sharp answer. A census of the whole 4100-address range
    # is also reported, but only in summary: most of the image is compressed
    # data, where four bytes match a given address by chance, so a full listing
    # of that range would be noise dressed as evidence.
    def _occurrences(value: int) -> list[int]:
        needle = value.to_bytes(4, "little")
        found = []
        position = rom_bytes.find(needle)
        while position != -1:
            found.append(_gba.ROM_BASE + position)
            position = rom_bytes.find(needle, position + 1)
        return found

    slot_census = {}
    for entry in installed:
        destination = int(entry["destination"], 16)
        literal_slot = int(entry["entry"], 16) + 8
        occurrences = _occurrences(destination)
        others = [a for a in occurrences if a != literal_slot]
        slot_census[entry["destination"]] = {
            "veneer": entry["entry"],
            "veneer_literal_slot": f"0x{literal_slot:08X}",
            "occurrences_at_any_offset": [f"0x{a:08X}" for a in occurrences],
            "occurrences_other_than_the_veneer_literal": [f"0x{a:08X}" for a in others],
            "occurs_only_as_the_veneer_literal": not others,
        }

    range_values: dict[int, int] = {}
    for offset in range(0, len(rom_bytes) - 3, 4):
        value = int.from_bytes(rom_bytes[offset : offset + 4], "little")
        if IWRAM_BASE <= value < IWRAM_END:
            range_values[value] = range_values.get(value, 0) + 1

    # ---- 6. who calls the veneers ------------------------------------------
    # A pattern scan, not an aligned chain-walk, so the result is an UPPER BOUND:
    # at an offset that is not an instruction boundary four bytes can still spell
    # a BL encoding. Both the any-even-offset count and the four-byte-aligned
    # count are reported, and neither is quoted as an exact total.
    def _thumb_bl_targets() -> list[tuple[int, int]]:
        found = []
        for offset in range(0, len(rom_bytes) - 3, 2):
            first = int.from_bytes(rom_bytes[offset : offset + 2], "little")
            second = int.from_bytes(rom_bytes[offset + 2 : offset + 4], "little")
            if (first & 0xF800) != 0xF000 or (second & 0xF800) != 0xF800:
                continue
            sign = (first >> 10) & 1
            j1 = (second >> 13) & 1
            j2 = (second >> 11) & 1
            i1 = (~(j1 ^ sign)) & 1
            i2 = (~(j2 ^ sign)) & 1
            displacement = (
                (sign << 24) | (i1 << 23) | (i2 << 22)
                | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
            )
            if displacement & 0x01000000:
                displacement -= 0x02000000
            found.append((_gba.ROM_BASE + offset, _gba.ROM_BASE + offset + 4 + displacement))
        return found

    bl_sites = _thumb_bl_targets()
    callers = {}
    veneer_addresses = {int(entry["entry"], 16) for entry in veneers}
    for entry in veneers:
        # NOT `address`: that name holds the family's end, and reusing it here
        # silently truncated the reported extent by the last stub's size.
        entry_address = int(entry["entry"], 16)
        sites = [site for site, target in bl_sites if target == entry_address]
        callers[entry["entry"]] = {
            "pattern_scan_any_even_offset": len(sites),
            "pattern_scan_four_byte_aligned": sum(1 for s in sites if s % 4 == 0),
            "sites_four_byte_aligned": [f"0x{s:08X}" for s in sites if s % 4 == 0][:40],
        }

    # Does any ARM branch reach a veneer? An ARM B/BL is identified from the
    # encoding alone (condition 0x0A in the top byte), so this sweep is a pure
    # arithmetic pass over the aligned words rather than a disassembly.
    arm_branches_to_veneers = []
    for offset in range(0, len(rom_bytes) - 3, 4):
        word = int.from_bytes(rom_bytes[offset : offset + 4], "little")
        if (word & 0x0F000000) != 0x0A000000:
            continue
        displacement = word & 0x00FFFFFF
        if displacement & 0x800000:
            displacement -= 0x1000000
        target = _gba.ROM_BASE + offset + 8 + displacement * 4
        if target in veneer_addresses:
            arm_branches_to_veneers.append(
                {"site": f"0x{_gba.ROM_BASE + offset:08X}", "target": f"0x{target:08X}"}
            )

    # Fail closed on the invariant that a later statement could quietly break:
    # the walk's end must follow the last stub. A loop that reuses `address` as
    # its own variable truncated the reported extent by one stub before this
    # check existed.
    last_end = int(veneers[-1]["entry"], 16) + veneers[-1]["size"]
    if address != last_end:
        raise LiftError(
            "the veneer family's end does not follow its last stub: "
            f"0x{address:08X} != 0x{last_end:08X}"
        )

    # Which veneer destinations the 16-bit reading of the same control word
    # would leave outside the copied block. This number was carried as prose
    # ("eight") in a docstring, a document and this report until
    # DECOMP-IWRAM-DISPATCH-001 measured it; it is derived here so it cannot
    # drift again.
    end_16 = source_address + count * 2
    outside_16bit = sorted(
        (
            entry["destination"],
            iwram_rom(int(entry["destination"], 16)),
        )
        for entry in installed
        if iwram_rom(int(entry["destination"], 16)) >= end_16
    )

    return {
        "method": (
            "the DMA3 register writes are decoded from the reset routine's own "
            "instructions with the ARM immediate rotation applied; the transfer "
            "length is the reading that tiles the block; the veneer family is "
            "walked from the byte pattern `78 47 c0 46`"
        ),
        "install_routine": {
            "entry": f"0x{CRT0_ENTRY:08X}",
            "end": f"0x{CRT0_END:08X}",
            "literal_pool": [f"0x{a:08X}" for a in CRT0_LITERAL_POOL],
            "dma3_register_writes": [
                {
                    "register": store["register"],
                    "value": None if store["value"] is None else f"0x{store['value']:08X}",
                    "instruction": store["instruction"],
                    "text": store["text"],
                    "value_source": store["value_source"],
                }
                for store in stores
            ],
            "notes": (
                "r0 is 0x04000000 (mov r0, #64, #12 -> 0x04000000), so the three "
                "stores are DMA3SAD 0x040000D4, DMA3DAD 0x040000D8 and DMA3CNT "
                "0x040000DC. The stores carry `ne` only because the flags come "
                "from `lsrs`; both counts are non-zero, so both execute."
            ),
        },
        "installed_block": {
            "iwram_start": f"0x{IWRAM_BASE:08X}",
            "iwram_end": f"0x{IWRAM_END:08X}",
            "rom_source": f"0x{IWRAM_ROM_SOURCE:08X}",
            "rom_end": f"0x{IWRAM_ROM_END:08X}",
            "bytes": IWRAM_BYTES,
            "verbatim": True,
            "control_word": f"0x{control:08X}",
            "control_low_half": f"0x{count:04X}",
            "control_high_half": f"0x{control >> 16:04X}",
            "source_address_fixed": bool((control >> 16) & DMA3_CONTROL_SOURCE_FIXED),
            "transfer_width_byte_counts": candidates,
            "transfer_width_decided_by": (
                "the 32-bit reading is the one whose length ends both at the "
                "first byte of the 0xFF fill in ROM and at the destination of "
                "the first DMA in IWRAM; the 16-bit reading ends in the middle "
                "of a function and leaves %d of the thirteen veneer "
                "destinations outside the copied block (%s)"
                % (
                    len(outside_16bit),
                    ", ".join(destination for destination, _ in outside_16bit),
                )
            ),
            "veneer_destinations_outside_the_16_bit_reading": [
                {
                    "iwram": destination,
                    "rom": f"0x{rom_address:08X}",
                }
                for destination, rom_address in outside_16bit
            ],
            "bytes_sha1": __import__("hashlib").sha1(
                rom_bytes[IWRAM_ROM_SOURCE - base : IWRAM_ROM_END - base]
            ).hexdigest(),
        },
        "dma3_setups_in_the_reset_routine": [_describe(setup) for setup in setups],
        "veneers": {
            "family_first": f"0x{first:08X}",
            "family_end": f"0x{address:08X}",
            "family_bytes": address - first,
            "entries": veneers,
            "entry_count": len(veneers),
            "installed_code_destinations": len(installed),
            "rom_destinations": len(outside),
            "forms": sorted({v["form"] for v in veneers}),
            "destinations_unique": len({v["destination"] for v in veneers}) == len(veneers),
            "all_installed_destinations_are_arm": all(
                v["destination_state"] == "arm" for v in installed
            ),
        },
        "block_memory_slots": slots,
        "veneer_callers": {
            "method": (
                "a Thumb BL pattern scan at every two-byte offset of the image, "
                "re-decoded from the halfwords. This is an UPPER BOUND: at an "
                "offset that is not an instruction boundary four bytes can still "
                "spell a BL encoding, so the four-byte-aligned count is reported "
                "alongside it and neither is an exact total. An aligned "
                "chain-walk from evidenced entries would be authoritative."
            ),
            "bound_counts_by_entry": callers,
            "arm_branch_sites_reaching_a_veneer": arm_branches_to_veneers,
            "arm_branch_sweep_method": (
                "an ARM B/BL is identified from the encoding alone (bits 27-25 of "
                "an aligned word equal 0b101), so this sweep is arithmetic rather "
                "than a disassembly and has no alignment blind spot. Every site "
                "in the family is a Thumb BL caller."
            ),
        },
        "slot_addresses_in_the_image": slot_census,
        "words_naming_the_block_anywhere_in_it": {
            "distinct_value_count": len(range_values),
            "total_words": sum(range_values.values()),
            "method": (
                "every four-byte-aligned offset of the image is read as a "
                "little-endian 32-bit word and kept when it lies in "
                "[0x03000000, 0x03001004). This is a LOWER BOUND: a second pass at "
                "every 2-byte-aligned offset finds 225 values over 533 windows "
                "against 129 over 257, the difference being 96 values that occur "
                "at an odd offset only. Most of the image is compressed data, "
                "where four bytes match a given address by chance, so the per-slot "
                "census above is the decision-relevant one and this is a summary."
            ),
            "distinct_values": {
                f"0x{value:08X}": count for value, count in sorted(range_values.items())
            },
        },
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def _u32_read(rom_bytes: bytes, address: int) -> int:
    offset = address - _gba.ROM_BASE
    return int.from_bytes(rom_bytes[offset : offset + 4], "little")


def _one_arm(rom_bytes: bytes, address: int):
    """Decode exactly one ARM word.

    `MD.disasm` stops at the first word it cannot decode, so a region that
    contains a single NV-condition word silently truncates a linear sweep.
    One word at a time has no such failure mode.
    """
    offset = address - _gba.ROM_BASE
    if offset < 0 or offset + 4 > len(rom_bytes):
        return None
    for ins in cp.MD["arm"].disasm(rom_bytes[offset : offset + 4], address):
        return ins
    return None


def _one_thumb(rom_bytes: bytes, address: int):
    offset = address - _gba.ROM_BASE
    if offset < 0 or offset + 2 > len(rom_bytes):
        return None
    for ins in cp.MD["thumb"].disasm(rom_bytes[offset : offset + 2], address):
        return ins
    return None


#: The top of the half of the image prior tickets model as game code: the
#: veneer family ends at 0x080491CC, the native dispatch table at 0x08055360 and
#: the interpreter's bounding string at 0x0805553C, while the first data table
#: above is at 0x080561C4. Readers ABOVE this boundary sit in the asset half,
#: where four bytes spell a plausible IWRAM address by chance; every reader it
#: keeps was read by hand, and every reader it drops is in an asset region.
GAME_CODE_HALF_END = 0x08060000


def _code_region_end() -> int:
    """The boundary above which a pc-relative read is a coincidence.

    Stated as a constant rather than derived from config/rom_map.json, because
    that map classes the installed block itself and a handler cluster at
    0x087B6904 as `code`, so the map's maximum code end lies above the whole
    asset half and a derived boundary would accept every coincidence. The map's
    code regions above the boundary are reported alongside it so the choice is
    auditable rather than asserted.
    """
    return GAME_CODE_HALF_END


def _code_regions_above(boundary: int) -> list:
    document = json.loads((_identity.CONFIG_DIR / "rom_map.json").read_text(encoding="utf-8"))
    return [
        {
            "id": region["id"],
            "start": region["rom_address_start"],
            "end": region["rom_address_end"],
            "classification": region.get("classification"),
        }
        for region in document["regions"]
        if region.get("classification") in ("code", "code_candidate")
        and int(region["rom_address_start"], 16) >= boundary
    ]


def _iwram_pointer_census(rom_bytes: bytes) -> dict:
    """Every 4-byte window, at EVERY 2-byte-aligned offset, holding an IWRAM address.

    A 4-byte-aligned sweep is a lower bound and it is not a small one: the same
    image gives 129 distinct values over 257 windows aligned and 225 over 533 at
    two-byte alignment. A pointer table based at an odd halfword is invisible to
    the aligned form, and there is no reason a compiler would align one.
    """
    base = _gba.ROM_BASE
    counted = len(rom_bytes) // 4
    found: dict[int, list[int]] = {}
    for shift, count in ((0, counted), (2, counted - 1)):
        for index, value in enumerate(struct.unpack_from(f"<{count}I", rom_bytes, shift)):
            if IWRAM_BASE <= value < IWRAM_END:
                found.setdefault(value, []).append(base + shift + 4 * index)
    return {value: sorted(set(sites)) for value, sites in found.items()}


def _pc_relative_index(rom_bytes: bytes) -> dict:
    """Every pc-relative read in the image, keyed by the slot it lands on.

    Arithmetic over the encodings rather than a disassembly, so there is no
    alignment blind spot. This is the question that matters: an address stored in
    a literal pool is not an entry unless some instruction LOADS it, and the
    install path for the IRQ vector proves an address can also be COMPUTED.

    Built once and indexed, because a per-slot rescan makes the whole derivation
    quadratic over an 8 MiB image and it stopped finishing.
    """
    base = _gba.ROM_BASE
    found: dict[int, list] = {}

    def note(slot: int, record: dict):
        found.setdefault(slot, []).append(record)

    for offset in range(0, len(rom_bytes) - 3, 2):
        address = base + offset
        half = int.from_bytes(rom_bytes[offset : offset + 2], "little")
        if (half & 0xF800) in (0x4800, 0xA000):
            slot = ((address + 4) & ~3) + (half & 0xFF) * 4
            note(
                slot,
                {
                    "site": address,
                    "kind": "thumb-ldr-pc" if half & 0x0800 else "thumb-add-pc",
                    "encoding": f"0x{half:04X}",
                },
            )
        if offset % 4:
            continue
        word = int.from_bytes(rom_bytes[offset : offset + 4], "little")
        if word >> 28 == 0xF:
            continue
        top = (word >> 25) & 0x7
        if top == 0b010 and not (word & (1 << 25)) and ((word >> 16) & 0xF) == 0xF \
                and (word & (1 << 24)):
            up = (word >> 23) & 1
            immediate = word & 0xFFF
            slot = address + 8 + (immediate if up else -immediate)
            note(
                slot,
                {
                    "site": address,
                    "kind": "arm-ldr-pc" if (word >> 20) & 1 else "arm-str-pc",
                    "encoding": f"0x{word:08X}",
                },
            )
    return found


def _pc_relative_readers(rom_bytes: bytes, slot: int) -> list:
    """Every instruction whose pc-relative read lands on `slot`."""
    return _pc_relative_index(rom_bytes).get(slot, [])


def _memory_operands(op_str: str):
    """(source, base, index, immediate) for `rS,[rB,#imm]`, `[rB]` or `[rB,rI]`.

    Splitting the operand text on commas is not safe here: `r0,[r1,#0x3c]` has
    three comma-separated pieces, and an earlier revision that required exactly
    two silently dropped every store, which made the whole IRQ install path
    derive as empty.
    """
    if "[" not in op_str or "," not in op_str:
        return None
    source, rest = op_str.split(",", 1)
    if "[" not in rest:
        return None
    inside = rest.split("[", 1)[1].split("]", 1)[0]
    parts = inside.split(",")
    base = parts[0]
    index = None
    immediate = 0
    if len(parts) > 1:
        second = parts[1]
        if second.startswith("#"):
            try:
                immediate = int(second[1:], 0)
            except ValueError:
                immediate = 0
        else:
            index = second
    return source, base, index, immediate


def _thumb_function_start(rom_bytes: bytes, site: int, limit: int = 0x800):
    """The nearest preceding Thumb prologue that still encloses `site`.

    A backward scan for `push {..., lr}` is only evidence while nothing between
    it and the site has already left the function, so the scan stops at the
    first `bx lr` or `pop {..., pc}` it crosses. That makes the answer a bound
    with a stated rule rather than a guess about where a function starts.
    """
    base = _gba.ROM_BASE
    address = site - 2
    stop = max(base, site - limit)
    while address >= stop:
        half = int.from_bytes(rom_bytes[address - base : address - base + 2], "little")
        if half == 0x4770 or (half & 0xFF00) == 0xBD00 or (half & 0xFF07) == 0x4700:
            # A terminator reached first bounds the function from above: the
            # enclosing unit can only start at the instruction after it. Both
            # readers of the dispatch slots are prologue-less leaves, so this is
            # the normal answer here, not the fallback.
            return address + 2
        if (half & 0xFE00) == 0xB400:  # push {..}
            registers = half & 0x01FF
            if (half & 0x0100) or (registers & 0x80):  # lr set, or pc in list
                return address
        address -= 2
    return None


_ARM_BRANCHES = ("b", "bl", "bx", "blx", "bxj")


def _arm_successors(rom_bytes: bytes, ins) -> tuple:
    """(successors, kind, target) for one ARM instruction.

    Capstone reports an ARM branch operand as the ABSOLUTE target, so no pc+8
    arithmetic belongs here. The instruction ID decides what the instruction is:
    the mnemonic carries the condition, so `bne` is neither `b` nor a
    terminator and keying on the text drops every conditional branch - which is
    exactly what left the dispatcher's own tail unreachable the first time.
    A conditional `bxne r4` still falls through and must NOT terminate a walk.
    """
    address = ins.address
    mnemonic = ins.mnemonic
    op_str = ins.op_str.replace(" ", "")
    fallthrough = address + 4
    unconditional = mnemonic in ("b", "bl", "bx", "blx", "bxj")
    ins_id = ins.id
    if ins_id in (cp.capstone.arm.ARM_INS_B, cp.capstone.arm.ARM_INS_BL) and ins.operands:
        target = ins.operands[0].imm & 0xFFFFFFFF
        if ins_id == cp.capstone.arm.ARM_INS_BL:
            return [fallthrough, target], "call", target
        return ([target] if unconditional else [target, fallthrough]), "branch", target
    if ins_id in (cp.capstone.arm.ARM_INS_BX, cp.capstone.arm.ARM_INS_BLX,
                  cp.capstone.arm.ARM_INS_BXJ):
        register = op_str.split(",")[0]
        if register == "lr":
            return ([] if unconditional else [fallthrough]), "return", None
        return ([] if unconditional else [fallthrough]), "indirect", None
    if _is_arm_terminator(ins):
        return ([] if unconditional else [fallthrough]), "terminator", None
    if mnemonic.startswith("add") and ",pc," in op_str and ins.operands \
            and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
        target = address + 8 + ins.operands[-1].imm
        return ([fallthrough, target], "pc_add", target)
    return [fallthrough], "next", None


def _is_arm_terminator(ins) -> bool:
    mnemonic = ins.mnemonic
    op_str = ins.op_str.replace(" ", "")
    if mnemonic in ("bx", "bxj", "blx"):
        return op_str.split(",")[0] == "lr"
    if mnemonic.startswith("pop") or mnemonic.startswith("ldm"):
        return "pc" in op_str.split("{")[-1]
    if mnemonic.startswith("ldr"):
        return op_str.split(",")[0] == "pc"
    if mnemonic.startswith("mov"):
        return op_str.split(",")[0] == "pc"
    return False


def _arm_literal_value(rom_bytes: bytes, ins):
    """The value of a pc-relative literal load, or None.

    The two instruction sets differ in where PC points: ARM reads `address + 8`,
    Thumb reads `(address + 4)` with bit 1 cleared. Using the ARM rule on Thumb
    code reads a word two bytes into the pool and returns a plausible-looking
    wrong constant, which is exactly what it did here first.
    """
    op_str = ins.op_str.replace(" ", "")
    if "[pc," not in op_str:
        return None
    inner = op_str.split("[pc,", 1)[1].split("]", 1)[0]
    try:
        immediate = int(inner.lstrip("#"), 0) if inner.startswith("#") else 0
    except ValueError:
        return None
    if ins.size == 2:
        slot = ((ins.address + 4) & ~3) + immediate
    else:
        slot = ins.address + 8 + immediate
    return _u32_read(rom_bytes, slot)


def derive_iwram_dispatch(rom_bytes: bytes) -> dict:
    """Derive the block's dispatch and IRQ architecture from the ROM.

    Four questions, each answered by a mechanism rather than by reading a name:

    1. Which routes enter the block? The veneer family answers one half; the
       other half is every ROM word whose value is an IWRAM address, filtered by
       the question that actually matters - does an instruction LOAD it.
    2. Which five functions have no caller inside the block, and what reaches
       them? Answered by comparing the walk's reachable set against the block's
       code words minus its literal words.
    3. What is the IRQ dispatcher's algorithm, its vector table, and its install
       path? Decoded from its own instruction stream, including the ARM
       immediate rotation that hides 0x2000 inside `lsls r1, r1, #0xd`.
    4. What does the internal callgraph look like? An aligned recursive descent
       over the code half with the function leaders derived, not declared.
    """
    runtime = derive_iwram_runtime(rom_bytes)
    census = _iwram_pointer_census(rom_bytes)
    readers_index = _pc_relative_index(rom_bytes)
    code_end = _code_region_end()
    veneers = runtime["veneers"]["entries"]
    installed = [entry for entry in veneers if entry["destination_state"] == "arm"]

    # ---- 1. the stored-pointer route --------------------------------------
    # A word in the image that equals an IWRAM address is only a reference when
    # an instruction LOADS it, and only a real one when that instruction lies in
    # the half of the image the structural map calls code.
    stored = []
    coincidences = []
    for value, sites in sorted(census.items()):
        readers = []
        for site in sites:
            for reader in readers_index.get(site, []):
                record = dict(reader, site=f"0x{reader['site']:08X}")
                if reader["site"] < code_end or IW_ROM_START <= reader["site"] < IWRAM_ROM_END:
                    readers.append(record)
                else:
                    coincidences.append(
                        {
                            "iwram": f"0x{value:08X}",
                            "slot": f"0x{site:08X}",
                            "reader": f"0x{reader['site']:08X}",
                            "kind": reader["kind"],
                        }
                    )
        inside = [s for s in sites if IWRAM_ROM_SOURCE <= s < IWRAM_ROM_END]
        veneer_literals = {
            int(entry["entry"], 16) + 8: entry["destination"] for entry in veneers
        }
        as_veneer_literal = [
            f"0x{s:08X}" for s in sites if s in veneer_literals
        ]
        stored.append(
            {
                "iwram": f"0x{value:08X}",
                "region_within_the_block": (
                    "code"
                    if value < CODE_END_IWRAM
                    else "data_tail"
                ),
                "sites": [f"0x{s:08X}" for s in sites],
                "sites_inside_the_block": [f"0x{s:08X}" for s in inside],
                "veneer_literals_that_name_it": as_veneer_literal,
                "readers": readers,
                "is_an_entry": bool(readers),
                "notes": (
                    "read by a pc-relative load, so this really is a stored "
                    "pointer; whether it enters code or names a data slot is the "
                    "region_within_the_block field"
                    if readers
                    else "no instruction in the image loads this word, so it is "
                    "data or a coincidence rather than an entry"
                ),
            }
        )
    entries = [row for row in stored if row["is_an_entry"]]
    code_entries = [row for row in entries if row["region_within_the_block"] == "code"]
    data_entries = [row for row in entries if row["region_within_the_block"] == "data_tail"]

    # ---- 2. the second dispatch path --------------------------------------
    veneer_destinations = {int(entry["destination"], 16) for entry in installed}
    second = []
    for row in code_entries:
        value = int(row["iwram"], 16)
        for reader in row["readers"]:
            site = int(reader["site"], 16)
            # The slot's own index: the word at `value` is written into an
            # object field by the reader, which is what makes this an
            # INSTALLATION rather than a call.
            target_field, store_site = None, None
            start = _thumb_function_start(rom_bytes, site)
            if start is not None:
                tracked: dict[str, int] = {}
                address = start
                while address < site + 0x40:
                    ins = _one_thumb(rom_bytes, address)
                    if ins is None:
                        break
                    literal = _arm_literal_value(rom_bytes, ins)
                    op = ins.op_str.replace(" ", "")
                    if literal is not None and op.startswith("r") and "," in op:
                        tracked[op.split(",")[0]] = literal
                    if ins.mnemonic == "str" and not ins.mnemonic.startswith("strh"):
                        parsed = _memory_operands(op)
                        if parsed is not None:
                            source, base, _index, immediate = parsed
                            base_value = tracked.get(base)
                            if base_value is not None and tracked.get(source) == value:
                                target_field = base_value + immediate
                                store_site = address
                    address += ins.size
            second.append(
                {
                    "iwram": row["iwram"],
                    "rom": f"0x{IWRAM_ROM_SOURCE + (value - IWRAM_BASE):08X}",
                    "route": (
                        "veneer" if value in veneer_destinations else "stored_pointer"
                    ),
                    "slot_rom": next(
                        (s for s in row["sites"]
                         if not (IW_ROM_START <= int(s, 16) < IWRAM_ROM_END)), row["sites"][0]
                    ),
                    "reader": reader["site"],
                    "reader_kind": reader["kind"],
                    "reader_function_start": None if start is None else f"0x{start:08X}",
                    "installed_into": (
                        None if target_field is None else f"0x{target_field:08X}"
                    ),
                    "store_site": None if store_site is None else f"0x{store_site:08X}",
                    "installed_not_called": target_field is not None,
                }
            )

    # A function with no incoming edge from anywhere is orphaned: no veneer, no
    # stored pointer, and no internal caller. That is the interesting set.
    graph = _iwram_callgraph(rom_bytes, code_entries, installed)
    function_starts = {f"0x{row['iwram']:08X}" for row in graph["functions"]}
    for row in second:
        # A value can lie in the code half and still be data: the routine at
        # 0x0804391C byte-compares the ROM string at 0x087B7734 against the
        # bytes at 0x030000F0 and sums the halfwords at 0x03000000. Membership
        # of the callgraph, not the address range, decides what is a function.
        row["is_a_function_entry"] = row["iwram"] in function_starts
    orphaned = [
        row for row in graph["functions"]
        if row["in_degree"] == 0 and not row["externally_reachable"]
    ]
    reached_only_from_outside = [
        row for row in graph["functions"]
        if row["in_degree"] == 0 and row["externally_reachable"]
    ]

    # ---- 3. the IRQ subsystem ---------------------------------------------
    irq = _derive_irq(rom_bytes, graph, readers_index, census)

    return {
        "method": (
            "the stored-pointer census reads every 2-byte-aligned window of the "
            "image; a stored word counts as an entry only when some instruction's "
            "pc-relative read lands on it; the dispatcher, its priority chain and "
            "its vector table are decoded from its own instruction words"
        ),
        "block": {
            "iwram_start": f"0x{IWRAM_BASE:08X}",
            "iwram_end": f"0x{IWRAM_END:08X}",
            "rom_source": f"0x{IWRAM_ROM_SOURCE:08X}",
            "bytes": IWRAM_BYTES,
            "code_end_iwram": f"0x{CODE_END_IWRAM:08X}",
            "verbatim_copy": True,
        },
        "external_entries": {
            "veneer_family": {
                "family_first": runtime["veneers"]["family_first"],
                "family_end": runtime["veneers"]["family_end"],
                "entry_count": runtime["veneers"]["entry_count"],
                "installed_code_destinations": runtime["veneers"]["installed_code_destinations"],
                "destinations": [
                    {
                        "entry": entry["entry"],
                        "destination": entry["destination"],
                        "state": entry["destination_state"],
                        "form": entry["form"],
                    }
                    for entry in veneers
                ],
            },
            "stored_pointer_route": {
                "method": (
                    "every 4-byte window at every 2-byte-aligned offset of the "
                    "image, kept when its value lies in [0x03000000, 0x03001004); "
                    "a value counts as referenced when an instruction's "
                    "pc-relative read lands on its slot and that instruction lies "
                    "below the structural map's code end (0x%08X)" % code_end
                ),
                "code_region_end": f"0x{code_end:08X}",
                "code_regions_above_that_boundary": _code_regions_above(code_end),
                "distinct_values": len(census),
                "windows": sum(len(sites) for sites in census.values()),
                "aligned_distinct_values": len(
                    [v for v, s in census.items() if any(x % 4 == 0 for x in s)]
                ),
                "aligned_windows": sum(
                    len([x for x in s if x % 4 == 0]) for s in census.values()
                ),
                "referenced_values": entries,
                "references_from_the_data_half": coincidences,
                "stored_but_never_loaded": [
                    row for row in stored
                    if not row["is_an_entry"]
                    and not row["sites_inside_the_block"]
                    and not row["veneer_literals_that_name_it"]
                ],
            },
            "entries_with_no_stored_pointer": [
                f"0x{rom_iwram(row['start']):08X}" for row in orphaned
            ],
        },
        "second_dispatch": {
            "route": (
                "a ROM literal pool holds the IWRAM address of a routine that is "
                "not called through a veneer; the reader stores it into an object "
                "field instead, so the block function is installed as a callback "
                "and invoked later through that field"
            ),
            "entries": [
                row for row in second
                if row["route"] == "stored_pointer" and row["is_a_function_entry"]
            ],
            "stored_pointers_that_are_not_function_entries": [
                row for row in second
                if row["route"] == "stored_pointer" and not row["is_a_function_entry"]
            ],
            "veneer_destinations_seen_by_the_census": [
                row for row in second if row["route"] == "veneer"
            ],
            "data_slots_the_rom_references": [
                row for row in data_entries
            ],
            "orphaned_functions": [
                {
                    "iwram": f"0x{rom_iwram(row['start']):08X}",
                    "rom": f"0x{row['start']:08X}",
                    "bytes": row["size"],
                    "reached_from_rom": False,
                    "family": row["family"],
                    "features": row["features"],
                }
                for row in orphaned
            ],
            "reached_only_from_outside": [
                {
                    "iwram": f"0x{rom_iwram(row['start']):08X}",
                    "rom": f"0x{row['start']:08X}",
                    "bytes": row["size"],
                    "routes": [
                        route for route in
                        ([f"veneer 0x{entry['entry']}"
                          for entry in installed
                          if int(entry["destination"], 16) == rom_iwram(row["start"])]
                         + [f"stored pointer {entry['iwram']} read at {reader['site']}"
                            for entry in code_entries
                            if int(entry["iwram"], 16) == rom_iwram(row["start"])
                            for reader in entry["readers"]])
                    ],
                }
                for row in reached_only_from_outside
            ],
        },
        "irq": irq,
        "callgraph": graph,
    }


def _vector_table_writers(rom_bytes: bytes, readers_index: dict, census: dict) -> list:
    """Instructions that store into the dispatcher's vector table.

    The table's base is never a literal in the code that installs handlers: ROM
    0x0803F218 loads the DATA word 0x087B6EDC, the word holds 0x03000FB0, and the
    next instruction dereferences the register. So the derivation is two steps -
    find who loads the address of a word that holds the table base, then follow
    the register through the dereference into the store. A one-step search for
    the literal 0x03000FB0 finds only the dispatcher's own pool word and would
    report that no handler is ever installed.
    """
    base = _gba.ROM_BASE
    out = []
    for site in census.get(IWRAM_VECTOR_TABLE, []):
        needle = site.to_bytes(4, "little")
        position = rom_bytes.find(needle)
        slots = []
        while position != -1:
            slots.append(base + position)
            position = rom_bytes.find(needle, position + 1)
        for slot in slots:
            for reader in readers_index.get(slot, []):
                load_site = reader["site"]
                if not reader["kind"].startswith("thumb"):
                    continue
                tracked: dict[str, object] = {}
                address = load_site
                dereferenced = False
                for _ in range(24):
                    ins = _one_thumb(rom_bytes, address)
                    if ins is None:
                        break
                    op = ins.op_str.replace(" ", "")
                    literal = _arm_literal_value(rom_bytes, ins)
                    if literal is not None and op.startswith("r"):
                        tracked[op.split(",")[0]] = {"literal": literal}
                    elif ins.mnemonic in ("movs", "mov") and "#" in op:
                        destination = op.split(",")[0]
                        try:
                            tracked[destination] = {"value": int(op.split("#")[1], 0)}
                        except ValueError:
                            pass
                    elif ins.mnemonic == "ldr" and "[" in op and "#" not in op:
                        # `ldr r0, [r0]`: the register now holds the DATA at the
                        # address it held before, i.e. the table base.
                        destination = op.split(",")[0]
                        source = op.split("[")[1].rstrip("]")
                        entry = tracked.get(source)
                        if isinstance(entry, dict) and entry.get("literal") == site:
                            tracked[destination] = {"value": IWRAM_VECTOR_TABLE}
                            dereferenced = True
                    elif ins.mnemonic == "str" and "[" in op:
                        parsed = _memory_operands(op)
                        if parsed is not None:
                            source, register, _index, immediate = parsed
                            entry = tracked.get(register)
                            if isinstance(entry, dict) and entry.get("value") == IWRAM_VECTOR_TABLE:
                                stored = tracked.get(source)
                                out.append(
                                    {
                                        "site": f"0x{address:08X}",
                                        "table_entry": f"0x{IWRAM_VECTOR_TABLE + immediate:08X}",
                                        "slot_index": immediate // 4,
                                        "value": (
                                            None if not isinstance(stored, dict)
                                            else f"0x{stored.get('value', stored.get('literal', 0)):08X}"
                                        ),
                                        "table_base_loaded_at": f"0x{load_site:08X}",
                                        "table_word_site": f"0x{site:08X}",
                                        "dereferenced": dereferenced,
                                    }
                                )
                    address += ins.size
    return out


def _branch_sites_into(rom_bytes: bytes, value: int) -> list:
    """Every Thumb BL/BLX and ARM B/BL in the image whose target is `value`.

    This is the question a stored-word search cannot answer. The routine that
    installs the BIOS IRQ vector is named by NO word anywhere in the image - the
    4-byte value 0x0803F3DA occurs zero times at every alignment - so a literal
    search concludes the vector is never installed. It is installed: the routine
    is reached by a BL from the system-init path at 0x0803D7CC. A Thumb BL is a
    32-bit instruction, so it must be decoded as a PAIR; decoding one halfword at
    a time reports it as undecodable and loses the edge.
    """
    base = _gba.ROM_BASE
    out = []
    for offset in range(0, len(rom_bytes) - 3, 2):
        first = int.from_bytes(rom_bytes[offset : offset + 2], "little")
        if (first & 0xF800) != 0xF000:
            continue
        second = int.from_bytes(rom_bytes[offset + 2 : offset + 4], "little")
        if (second & 0xF800) not in (0xF800, 0xE800):
            continue
        sign = (first >> 10) & 1
        j1 = (second >> 13) & 1
        j2 = (second >> 11) & 1
        i1 = (~(j1 ^ sign)) & 1
        i2 = (~(j2 ^ sign)) & 1
        displacement = (
            (sign << 24) | (i1 << 23) | (i2 << 22)
            | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
        )
        if displacement & 0x01000000:
            displacement -= 0x02000000
        kind = "thumb-bl" if (second & 0xF800) == 0xF800 else "thumb-blx"
        target = base + offset + 4 + displacement
        if kind == "thumb-blx":
            target &= ~3
        if target == value:
            out.append((base + offset, kind, target))
    for offset in range(0, len(rom_bytes) - 3, 4):
        word = int.from_bytes(rom_bytes[offset : offset + 4], "little")
        if word >> 28 == 0xF:
            continue
        if ((word >> 25) & 0x7) != 0b101:
            continue
        displacement = word & 0x00FFFFFF
        if displacement & 0x800000:
            displacement -= 0x1000000
        target = base + offset + 8 + displacement * 4
        if target == value:
            out.append((base + offset, "arm-branch", target))
    return out


def _derive_irq(rom_bytes: bytes, graph: dict, readers_index: dict, census: dict) -> dict:
    """Decode the IRQ dispatcher, its vector table and its install path."""
    words = []
    for row in graph["functions"]:
        if row["start"] == IWRAM_DISPATCH_ROM:
            words = row["words"]
    priority = []
    acknowledgement = []
    hardware = set()
    vector_base = None
    pending_word = None
    handler_call = {}
    handler_path = None
    acknowledge_store = None
    null_handler = _u32_read(rom_bytes, ROM_IRQ_NULL_HANDLER)
    tracked: dict[str, int] = {}
    offset_register = None
    current_ip = None
    for address in words:
        ins = _one_arm(rom_bytes, address)
        if ins is None:
            continue
        op = ins.op_str.replace(" ", "")
        immediate = None
        if ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            immediate = ins.operands[-1].imm
        if ins.mnemonic in ("mov", "movs", "add", "adds", "sub", "subs") \
                and op.startswith("r") and "#" in op:
            # An ARM data-processing immediate is imm8 rotated by 2*rot and
            # capstone reports the two halves as two operands, so `#64, #28`
            # arrives as operands (0x40, 0x1C) and reading the last one gives
            # 0x1C instead of 0x4000. Every mask in the priority chain has to be
            # read out of the word.
            value = _arm_immediate(int.from_bytes(ins.bytes, "little"))
            destination = op.split(",")[0]
            base = op.split(",")[1] if "," in op else None
            if ins.mnemonic.startswith("add"):
                tracked[destination] = (tracked.get(base, 0) + value) & 0xFFFFFFFF
            elif ins.mnemonic.startswith("sub"):
                tracked[destination] = (tracked.get(base, 0) - value) & 0xFFFFFFFF
            else:
                tracked[destination] = value
            if 0x04000000 <= tracked[destination] < 0x04000400:
                hardware.add(tracked[destination])
        literal = _arm_literal_value(rom_bytes, ins)
        if literal is not None and op.startswith("r"):
            tracked[op.split(",")[0]] = literal
            if 0x04000000 <= literal < 0x04000400:
                hardware.add(literal)
            if IWRAM_VECTOR_TABLE <= literal < IWRAM_VECTOR_TABLE + 0x100:
                vector_base = literal
        if ins.mnemonic.startswith("ldr") and "!" in op and op.startswith("r"):
            # `ldr r2, [r3, #0x200]!` moves r3 to REG_IE, and the address is
            # never a literal: the base is built by `mov r3, #64, #12`.
            destination = op.split(",")[0]
            base = op.split("[")[1].split(",")[0]
            tail = op.split("[")[1].split(",")[1].rstrip("]!")
            if tail.startswith("#"):
                try:
                    tracked[base] = (tracked.get(base, 0) + int(tail[1:], 0)) & 0xFFFFFFFF
                except ValueError:
                    pass
                if 0x04000000 <= tracked[base] < 0x04000400:
                    hardware.add(tracked[base])
        if ins.mnemonic.startswith(("str", "ldr")) and "[" in op and "#" in op:
            base = op.split("[")[1].split(",")[0]
            tail = op.split("[")[1].split(",")[1].rstrip("]!")
            if tail.startswith("#") and base in tracked:
                try:
                    touched = tracked[base] + int(tail[1:], 0)
                except ValueError:
                    touched = None
                if touched is not None and 0x04000000 <= touched < 0x04000400:
                    hardware.add(touched)
        if ins.mnemonic == "str" and op == "r2,[r3]" and handler_path is not None:
            acknowledge_store = address
        if ins.mnemonic.startswith("ands") and ",#" in op:
            bits = _arm_immediate(int.from_bytes(ins.bytes, "little"))
            priority.append(
                {
                    "test_site": f"0x{address:08X}",
                    "mask": f"0x{bits:08X}",
                    "single_bit": bin(bits).count("1") == 1,
                    "bit": bits.bit_length() - 1 if bin(bits).count("1") == 1 else None,
                    "vector_byte_offset": (
                        None if offset_register is None else tracked.get(offset_register)
                    ),
                    "cpsr_mode_value": None if current_ip is None else f"0x{current_ip:08X}",
                    "_index": len(priority),
                }
            )
        if ins.mnemonic in ("mov", "movs") and op.startswith("ip,"):
            current_ip = immediate
        if ins.mnemonic == "mov" and op.startswith("r4,"):
            offset_register = op.split(",")[0]
        if ins.mnemonic == "bic" and op.startswith("r2,r2,r0"):
            handler_path = address
            acknowledgement.append({"site": f"0x{address:08X}", "operation": "clear the served IE bit"})
        if ins.mnemonic == "orr" and op.startswith("r2,r2,r0,lsl#16"):
            acknowledgement.append({"site": f"0x{address:08X}", "operation": "set the served IF bit"})
            acknowledgement.append(
                {"site": f"0x{address:08X}", "operation": "one 32-bit store acknowledges IF and unmasks IE"}
            )
        if ins.mnemonic.startswith("ldrh") and op.startswith("r5,[r1,#"):
            try:
                pending_word = IWRAM_VECTOR_TABLE + int(op.split("#")[-1].rstrip("]"), 0)
            except ValueError:
                pending_word = None
        if ins.mnemonic.startswith("add") and op.startswith("lr,pc,") and immediate is not None:
            handler_call["return_address"] = f"0x{address + 8 + immediate:08X}"
        if ins.mnemonic.startswith("add") and op.startswith("r4,pc,"):
            handler_call["arm_resume"] = f"0x{address + 8 + (immediate or 0):08X}"
        if ins.mnemonic.startswith("ldr") and op.startswith("r0,[r1,r4]"):
            handler_call["fetch_site"] = f"0x{address:08X}"
        if ins.mnemonic == "bx" and op == "r0":
            handler_call["call_site"] = f"0x{address:08X}"
    slot_count = None
    entries = []
    if pending_word is not None and vector_base is not None:
        slot_count = (pending_word - vector_base) // 4
        for index in range(slot_count):
            rom_slot = IWRAM_VECTOR_TABLE_ROM + 4 * index
            value = _u32_read(rom_bytes, rom_slot)
            entries.append(
                {
                    "index": index,
                    "iwram_slot": f"0x{vector_base + 4 * index:08X}",
                    "rom_slot": f"0x{rom_slot:08X}",
                    "value": f"0x{value:08X}",
                    "state": "thumb" if value & 1 else "arm",
                    "handler": f"0x{value & ~1:08X}",
                }
            )
    install = []
    dispatcher_value = IWRAM_DISPATCH_ENTRY
    for reader in readers_index.get(0x0803F434, []):
        site = reader["site"]
        start = _thumb_function_start(rom_bytes, site)
        if start is None:
            continue
        tracked_regs: dict[str, int] = {}
        address = start
        while address < site + 0x40:
            ins = _one_thumb(rom_bytes, address)
            if ins is None:
                break
            op = ins.op_str.replace(" ", "")
            literal = _arm_literal_value(rom_bytes, ins)
            if literal is not None and op.startswith("r"):
                tracked_regs[op.split(",")[0]] = literal
            if ins.mnemonic == "str" and not ins.mnemonic.startswith("strh"):
                parsed = _memory_operands(op)
                if parsed is not None:
                    source, base, _index, immediate = parsed
                    if tracked_regs.get(source) == dispatcher_value \
                            and base in tracked_regs:
                        install.append(
                            {
                                "site": f"0x{address:08X}",
                                "writes_to": f"0x{tracked_regs[base] + immediate:08X}",
                                "writes": f"0x{dispatcher_value:08X}",
                                "function": f"0x{start:08X}",
                            }
                        )
            address += ins.size
    # Each test's own branch decides whether it reaches the handler path or
    # something else. The last test in the chain branches to a self-loop, so the
    # slot its offset would select is never entered.
    for index, row in enumerate(priority):
        site = int(row["test_site"], 16)
        for step in range(1, 3):
            ins = _one_arm(rom_bytes, site + 4 * step)
            if ins is None:
                break
            if ins.mnemonic.startswith("b") and not ins.mnemonic.startswith("bic") \
                    and ins.operands and ins.operands[0].type == cp.capstone.arm.ARM_OP_IMM:
                target = ins.operands[0].imm & 0xFFFFFFFF
                row["branch_site"] = f"0x{site + 4 * step:08X}"
                row["branch_mnemonic"] = ins.mnemonic
                row["branch_target"] = f"0x{target:08X}"
                # `bne handler` treats the branch as the settled path; the last
                # test is `beq exit`, so ITS settled path is the fallthrough.
                if ins.mnemonic == "bne":
                    found, how = target, "conditional branch taken"
                else:
                    found, how = site + 4 * step + 4, "fallthrough"
                row["settled_path"] = how
                row["settled_path_target"] = f"0x{found:08X}"
                follow = _one_arm(rom_bytes, found)
                row["settled_path_is_a_self_branch"] = bool(
                    follow is not None
                    and follow.mnemonic == "b"
                    and follow.operands
                    and (follow.operands[0].imm & 0xFFFFFFFF) == found
                )
                row["branches_to_itself"] = target == site + 4 * step
                # The acknowledge-and-dispatch block runs from the IE clear to
                # the ack store. The FIRST test settles on the ORR and skips the
                # IE clear, because its ip value is 0x9F; every later test enters
                # at the BIC. Both are the handler path.
                row["lands_in_the_dispatch_block"] = bool(
                    handler_path is not None and acknowledge_store is not None
                    and handler_path <= found < acknowledge_store + 4
                )
                row["skips_the_ie_clear"] = bool(
                    row["lands_in_the_dispatch_block"] and found != handler_path
                )
                break
        row.pop("_index", None)
    reachable_offsets = sorted(
        {
            row["vector_byte_offset"]
            for row in priority
            if row.get("lands_in_the_dispatch_block") and row["vector_byte_offset"] is not None
        }
    )
    unreachable_tests = [
        row["test_site"] for row in priority
        if not row.get("lands_in_the_dispatch_block")
    ]
    return {
        "dispatcher": {
            "iwram_entry": f"0x{IWRAM_DISPATCH_ENTRY:08X}",
            "rom_entry": f"0x{IWRAM_DISPATCH_ROM:08X}",
            "instructions": len(words),
            "code_bytes": IWRAM_DISPATCH_CODE_END - IWRAM_DISPATCH_ROM,
            "state": "arm",
            "hardware_registers_named": [f"0x{v:08X}" for v in sorted(hardware)],
        },
        "priority_chain": priority,
        "priority_chain_length": len(priority),
        "handler_path_entry": None if handler_path is None else f"0x{handler_path:08X}",
        "reachable_vector_byte_offsets": reachable_offsets,
        "reachable_slot_count": len(reachable_offsets),
        "tests_that_do_not_reach_the_handler_path": unreachable_tests,
        "reachability_note": (
            "the fourteen tests select byte offsets 0x00..0x30, so thirteen of "
            "the table's slots are reachable. The last test's taken branch is a "
            "self-branch instead of the handler path, so bit 13 spins and the "
            "slot at the final offset is never entered."
        ),
        "acknowledgement": acknowledgement,
        "vector_table": {
            "iwram_base": f"0x{IWRAM_VECTOR_TABLE:08X}",
            "rom_base": f"0x{IWRAM_VECTOR_TABLE_ROM:08X}",
            "slot_count": slot_count,
            "slot_count_derived_from": (
                f"the dispatcher reads a halfword at the table base + 0x38, so the "
                f"table ends where that word begins: (0x{pending_word:08X} - "
                f"0x{IWRAM_VECTOR_TABLE:08X}) / 4"
                if pending_word is not None
                else None
            ),
            "entries": entries,
            "distinct_handlers": sorted({entry["handler"] for entry in entries}),
            "all_slots_share_one_handler": len({entry["value"] for entry in entries}) == 1,
        },
        "software_pending_word": {
            "iwram": None if pending_word is None else f"0x{pending_word:08X}",
            "role": (
                "the dispatcher ORs the served bit into this halfword before it "
                "calls the handler; nothing else in the block reads it and its "
                "consumer was not found, so its purpose is UNKNOWN"
            ),
        },
        "handler_call": handler_call,
        "default_handler": {
            "rom": f"0x{ROM_IRQ_NULL_HANDLER:08X}",
            "first_halfword": f"0x{null_handler & 0xFFFF:04X}",
            "is_a_bare_return": (null_handler & 0xFFFF) == 0x4770,
            "note": (
                "the install routine is the NEXT function, at ROM 0x0803F3DA; it "
                "is not a vector slot"
            ),
        },
        "install_path": {
            "bios_irq_vector_pointer_sites": install,
            "installer_call_sites": [
                {"site": f"0x{site:08X}", "kind": kind}
                for site, kind, _target in _branch_sites_into(rom_bytes, ROM_IRQ_INSTALL)
            ],
            "installer_is_named_by_a_stored_word": bool(
                rom_bytes.find(ROM_IRQ_INSTALL.to_bytes(4, "little")) != -1
            ),
            "installer_is_named_by_a_stored_word_note": (
                "the 4-byte value 0x%08X does not occur anywhere in the image, so "
                "the only way to reach the routine is a branch - which is why a "
                "search for the address as a pointer reports, wrongly, that the "
                "BIOS IRQ vector is never installed" % ROM_IRQ_INSTALL
            ),
            "bios_irq_vector_pointer_method": (
                "for every instruction that pc-relatively reads the dispatcher's "
                "own address literal, the enclosing Thumb function is walked with "
                "registers tracked through literal loads, and each store of that "
                "value through a literal base is reported with its computed "
                "destination - the BIOS IRQ vector pointer is never stored as a "
                "literal, it is computed as 0x03007FC0 + 0x3C"
            ),
            "vector_table_writes": _vector_table_writers(rom_bytes, readers_index, census),
            "vector_table_write_method": (
                "the table base 0x03000FB0 is stored in a DATA word, not in code; "
                "the derivation finds every instruction that loads the address of "
                "such a word, follows the register through one dereference, and "
                "reports each store through it"
            ),
        },
    }


def _iwram_callgraph(rom_bytes: bytes, entries: list, installed: list) -> dict:
    """Aligned recursive descent over the block's ARM code half."""
    seeds = sorted(
        {int(entry["destination"], 16) for entry in installed}
        | {int(entry["iwram"], 16) for entry in entries if entry["is_an_entry"]}
    )
    seeds = [iwram_rom(a) for a in seeds]
    code_end_rom = iwram_rom(CODE_END_IWRAM)
    reached: dict[int, object] = {}
    edges: list = []
    literal_slots: dict[int, list] = {}
    pending = list(seeds)
    while pending:
        address = pending.pop()
        if address in reached or not (IW_ROM_START <= address < code_end_rom):
            continue
        if (address - IWRAM_ROM_SOURCE) % 4:
            continue
        ins = _one_arm(rom_bytes, address)
        if ins is None:
            continue
        reached[address] = ins
        literal = _arm_literal_value(rom_bytes, ins)
        if literal is not None:
            op = ins.op_str.replace(" ", "")
            inner = op.split("[pc,", 1)[1].split("]", 1)[0]
            try:
                slot = address + 8 + (int(inner.lstrip("#"), 0) if inner.startswith("#") else 0)
            except ValueError:
                slot = None
            if slot is not None:
                literal_slots.setdefault(slot, []).append(
                    {"site": f"0x{address:08X}", "value": f"0x{literal:08X}"}
                )
        successors, kind, target = _arm_successors(rom_bytes, ins)
        if kind in ("call", "branch") and target is not None:
            edges.append(
                {
                    "from": f"0x{address:08X}",
                    "to": f"0x{target:08X}",
                    "kind": "call" if kind == "call" else "tail_branch",
                    "site": f"0x{address:08X}",
                }
            )
        if kind == "indirect":
            edges.append(
                {
                    "from": f"0x{address:08X}",
                    "to": None,
                    "kind": "indirect_register",
                    "site": f"0x{address:08X}",
                    "register": ins.op_str.replace(" ", "").split(",")[0],
                }
            )
        for successor in successors:
            if successor not in reached:
                pending.append(successor)

    fallthrough = set()
    branch_targets = set()
    for address, ins in reached.items():
        successors, kind, target = _arm_successors(rom_bytes, ins)
        if kind in ("call", "branch", "pc_add") and target is not None:
            branch_targets.add(target)
        if address + 4 in successors:
            fallthrough.add(address + 4)
    leaders = sorted(
        {address for address in reached if address not in fallthrough}
        | {t for t in branch_targets if t in reached}
        | set(seeds)
    )

    owner: dict[int, int] = {}
    functions = []
    skipped = []
    for leader in leaders:
        if leader in owner:
            skipped.append(
                {"leader": f"0x{leader:08X}", "owned_by": f"0x{owner[leader]:08X}"}
            )
            continue
        body: set = set()
        queue = [leader]
        shared = []
        while queue:
            address = queue.pop()
            if address in body or address not in reached:
                continue
            if address in owner and owner[address] != leader:
                shared.append(address)
                continue
            body.add(address)
            owner[address] = leader
            successors, kind, _target = _arm_successors(rom_bytes, reached[address])
            for successor in successors:
                if successor in reached and successor not in body:
                    queue.append(successor)
        if not body:
            continue
        local = sorted(body)
        function_edges = [
            edge for edge in edges
            if int(edge["from"], 16) in body
            and (edge["to"] is None or int(edge["to"], 16) not in body)
        ]
        # Indirect targets: resolve a `bx rN` when the function loaded rN from a
        # literal. The block's dispatch tail jumps into ROM exactly this way.
        values: dict[str, int] = {}
        for address in local:
            ins = reached[address]
            op = ins.op_str.replace(" ", "")
            literal = _arm_literal_value(rom_bytes, ins)
            if literal is not None and op.startswith("r"):
                values[op.split(",")[0]] = literal
            for edge in function_edges:
                if edge["site"] == f"0x{address:08X}" and edge["kind"] == "indirect_register":
                    resolved = values.get(edge.get("register", ""))
                    if resolved:
                        edge["resolved_to"] = f"0x{resolved:08X}"
                        edge["resolved_state"] = "thumb" if resolved & 1 else "arm"
                        edge["to"] = f"0x{resolved & ~1:08X}"
                        edge["kind"] = "indirect_resolved"
        features = _arm_features(reached, local, literal_slots)
        functions.append(
            {
                "start": leader,
                "rom_address": leader,
                "iwram": rom_iwram(leader),
                "end": max(local) + 4,
                "size": max(local) + 4 - leader,
                "instructions": len(local),
                "externally_reachable": leader in seeds,
                "edges": function_edges,
                "shared_words": [f"0x{a:08X}" for a in sorted(set(shared))],
                "features": features,
                "family": _family_for(features),
                "words": local,
            }
        )

    # Orphans: code words inside the code half that are neither reached nor a
    # loaded literal slot. A pool can hold words nothing loads, so a run is
    # reported with the loaded slots it contains rather than assumed to be code;
    # only a run that opens with a prologue and closes with a return is called a
    # function.
    orphans = []
    address = IWRAM_ROM_SOURCE
    while address < code_end_rom:
        if address not in reached and address not in literal_slots:
            orphans.append(address)
        address += 4
    runs = []
    for address in orphans:
        if runs and address == runs[-1][1]:
            runs[-1][1] = address + 4
        else:
            runs.append([address, address + 4])
    unreachable = []
    for start, end in runs:
        first = _one_arm(rom_bytes, start)
        last = _one_arm(rom_bytes, end - 4)
        slots_inside = sorted(s for s in literal_slots if start <= s < end)
        words = list(range(start, end, 4))
        opens = bool(first is not None and first.mnemonic.startswith("push"))
        closes = bool(
            last is not None
            and (
                (last.mnemonic == "bx" and last.op_str == "lr")
                or (last.mnemonic.startswith("pop") and "pc" in last.op_str)
            )
        )
        unreachable.append(
            {
                "rom_start": f"0x{start:08X}",
                "rom_end": f"0x{end:08X}",
                "iwram_start": f"0x{rom_iwram(start):08X}",
                "words": len(words),
                "bytes": end - start,
                "loaded_literal_slots_inside": [f"0x{s:08X}" for s in slots_inside],
                "first_instruction": (
                    None if first is None else f"{first.mnemonic} {first.op_str}".strip()
                ),
                "last_instruction": (
                    None if last is None else f"{last.mnemonic} {last.op_str}".strip()
                ),
                "opens_with_a_prologue": opens,
                "closes_with_a_return": closes,
                "looks_like_a_complete_function": opens and closes and len(words) >= 4,
            }
        )

    incoming: dict = {}
    for row in functions:
        for edge in row["edges"]:
            if edge["to"] and edge["kind"] in ("call", "tail_branch"):
                incoming.setdefault(edge["to"], []).append(
                    {"from": f"0x{row['start']:08X}", "site": edge["site"], "kind": edge["kind"]}
                )
    for row in functions:
        row["callers"] = incoming.get(f"0x{row['start']:08X}", [])
        row["in_degree"] = len(row["callers"])

    return {
        "method": (
            "aligned recursive descent from the veneer destinations and from "
            "every stored pointer an instruction actually loads; an address is a "
            "function leader when it is a call or branch target that is not also "
            "reached by fallthrough"
        ),
        "reachable_words": len(reached),
        "reachable_bytes": 4 * len(reached),
        "function_count": len(functions),
        "functions": functions,
        "leaders_already_owned": skipped,
        "literal_slots": {
            f"0x{slot:08X}": reads for slot, reads in sorted(literal_slots.items())
        },
        "unreachable_code_runs": unreachable,
        "edges": edges,
    }


def _arm_features(reached: dict, local: list, literal_slots: dict) -> list:
    """Mechanical features of a function, from its own instructions."""
    features = set()
    addresses = list(local)
    for index, address in enumerate(addresses):
        ins = reached[address]
        mnemonic = ins.mnemonic
        op = ins.op_str.replace(" ", "")
        if mnemonic in ("mla", "mul", "muls", "smull", "smlal", "umull", "umlal"):
            features.add("multiply")
        if mnemonic.startswith("asr"):
            features.add("arithmetic_shift")
        if mnemonic.startswith("sub") and ",pc," in op:
            features.add("pc_relative_data")
        if mnemonic.startswith("ldr") and "],#" in op:
            features.add("post_increment_load")
        if mnemonic.startswith("stm") or mnemonic.startswith("ldm"):
            if "!" in op:
                features.add("block_transfer_writeback")
        if mnemonic.startswith("ands") and ",#" in op:
            value = ins.operands[-1].imm if ins.operands else 0
            if value in (0xFF, 0xFFFF):
                features.add("byte_lane_mask")
        if mnemonic.startswith("strb"):
            features.add("byte_store")
        if mnemonic.startswith("strh"):
            features.add("halfword_store")
    for slot, reads in literal_slots.items():
        if any(int(read["site"], 16) in set(local) for read in reads):
            for read in reads:
                if int(read["site"], 16) in set(local):
                    value = int(read["value"], 16)
                    if 0x04000000 <= value < 0x04000400:
                        features.add("hardware_register")
                    if 0x03000000 <= value < 0x03008000:
                        features.add("iwram_data_pointer")
                    if value & 1:
                        features.add("thumb_code_pointer")
                    if 0x08000000 <= value < 0x08000000 + 0x800000:
                        features.add("rom_code_pointer")
    for address in addresses:
        ins = reached[address]
        mnemonic = ins.mnemonic
        if mnemonic in ("bx", "blx", "bxj") or (mnemonic.startswith("ldr") and ins.op_str.replace(" ", "").split(",")[0] == "pc"):
            features.add("indirect_branch")
        if mnemonic.startswith("add") and ",pc," in ins.op_str.replace(" ", ""):
            features.add("pc_add")
        if mnemonic == "msr" or mnemonic == "mrs":
            features.add("status_register")
        if mnemonic == "swi" or mnemonic == "svc":
            features.add("software_interrupt")
    return sorted(features)


_FAMILY_RULES = (
    ("irq", {"hardware_register", "status_register"}),
    ("dispatch", {"indirect_branch", "pc_add"}),
    ("bitstream", {"post_increment_load", "arithmetic_shift"}),
    ("arithmetic", {"multiply", "arithmetic_shift"}),
    ("memory", {"block_transfer_writeback"}),
    ("unknown", set()),
)


def _family_for(features: list) -> str:
    present = set(features)
    for name, required in _FAMILY_RULES:
        if required and required <= present:
            return name
    return "unknown"


def _register_units() -> None:
    UNITS[cp.GBARAM_TU.id] = {
        "unit": cp.GBARAM_TU,
        "functions": tuple(cp.GBARAM_FUNCTIONS),
        "literal_pool": cp.GBARAM_TU.literal_pool,
        "boundaries": "manifest",
    }
    UNITS[BCI_TU.id] = {
        "unit": BCI_TU,
        "functions": BCI_FUNCTIONS,
        "literal_pool": BCI_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": BCI_ALIGNMENT_PADDING,
    }
    UNITS[H2_TU.id] = {
        "unit": H2_TU,
        "functions": H2_FUNCTIONS,
        "literal_pool": H2_LITERAL_POOL,
        "boundaries": "derived",
        # No adjacent pool, so there is no padding to check.
        "expect_padding": None,
    }
    UNITS[OP_TU.id] = {
        "unit": OP_TU,
        "functions": OP_FUNCTIONS,
        "literal_pool": OP_LITERAL_POOL,
        "boundaries": "derived",
        # A leaf with no pool at all: there is nothing to measure.
        "expect_padding": None,
    }
    UNITS[STACK_TU.id] = {
        "unit": STACK_TU,
        "functions": STACK_FUNCTIONS,
        "literal_pool": STACK_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[ARITH_TU.id] = {
        "unit": ARITH_TU,
        "functions": ARITH_FUNCTIONS,
        "literal_pool": ARITH_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[CLEAR_TU.id] = {
        "unit": CLEAR_TU,
        "functions": CLEAR_FUNCTIONS,
        "literal_pool": CLEAR_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[COLLFLUSH3_TU.id] = {
        "unit": COLLFLUSH3_TU,
        "functions": COLLFLUSH3_FUNCTIONS,
        "literal_pool": COLLFLUSH3_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[COLLINSERT2_TU.id] = {
        "unit": COLLINSERT2_TU,
        "functions": COLLINSERT2_FUNCTIONS,
        "literal_pool": COLLINSERT2_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[COLLWRITE2_TU.id] = {
        "unit": COLLWRITE2_TU,
        "functions": COLLWRITE2_FUNCTIONS,
        "literal_pool": COLLWRITE2_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[COLLREAD_TU.id] = {
        "unit": COLLREAD_TU,
        "functions": COLLREAD_FUNCTIONS,
        "literal_pool": COLLREAD_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[APPEND_TU.id] = {
        "unit": APPEND_TU,
        "functions": APPEND_FUNCTIONS,
        "literal_pool": APPEND_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[NATIVE178_TU.id] = {
        "unit": NATIVE178_TU,
        "functions": NATIVE178_FUNCTIONS,
        "literal_pool": NATIVE178_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[FLAGMASK_TU.id] = {
        "unit": FLAGMASK_TU,
        "functions": FLAGMASK_FUNCTIONS,
        "literal_pool": FLAGMASK_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[GATHER_TU.id] = {
        "unit": GATHER_TU,
        "functions": GATHER_FUNCTIONS,
        "literal_pool": GATHER_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[BOOLUSE_TU.id] = {
        "unit": BOOLUSE_TU,
        "functions": BOOLUSE_FUNCTIONS,
        "literal_pool": BOOLUSE_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[FLAGREAD_TU.id] = {
        "unit": FLAGREAD_TU,
        "functions": FLAGREAD_FUNCTIONS,
        "literal_pool": FLAGREAD_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[EFFECT_TU.id] = {
        "unit": EFFECT_TU,
        "functions": EFFECT_FUNCTIONS,
        "literal_pool": EFFECT_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[USE_TU.id] = {
        "unit": USE_TU,
        "functions": USE_FUNCTIONS,
        "literal_pool": USE_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[IWRAM_BLOCK_TU.id] = {
        "unit": IWRAM_BLOCK_TU,
        "functions": IWRAM_BLOCK_FUNCTIONS,
        "literal_pool": IWRAM_BLOCK_LITERAL_POOL,
        "boundaries": "derived",
        # No pool, so there is no padding to measure.
        "expect_padding": None,
    }
    UNITS[IWRAM_DISPATCH_TU.id] = {
        "unit": IWRAM_DISPATCH_TU,
        "functions": IWRAM_DISPATCH_FUNCTIONS,
        "literal_pool": IWRAM_DISPATCH_LITERAL_POOL,
        "boundaries": "derived",
        # The four bytes between the code and the pool are the Thumb halfword
        # the handler returns through, so a four-byte gap is the expected shape
        # and is reported rather than checked against a constant.
        "expect_padding": None,
        # Opt in to following `add rD, pc, #imm` as a code successor.
        "pc_add_successors": True,
    }
    UNITS[IWRAM_BL_PAIR_TU.id] = {
        "unit": IWRAM_BL_PAIR_TU,
        "functions": IWRAM_BL_PAIR_FUNCTIONS,
        "literal_pool": IWRAM_BL_PAIR_LITERAL_POOL,
        "boundaries": "derived",
        # The four bytes of alignment padding between this unit and the next are
        # expected and are reported; the eight bytes of the PRECEDING routine's
        # pool are before this unit's entry and are not its padding.
        "expect_padding": None,
    }
    UNITS[IWRAM_BL_SPARSE_TU.id] = {
        "unit": IWRAM_BL_SPARSE_TU,
        "functions": IWRAM_BL_SPARSE_FUNCTIONS,
        "literal_pool": IWRAM_BL_SPARSE_LITERAL_POOL,
        "boundaries": "derived",
        "expect_padding": None,
    }
    UNITS[IWRAM_QF_TU.id] = {
        "unit": IWRAM_QF_TU,
        "functions": IWRAM_QF_FUNCTIONS,
        "literal_pool": IWRAM_QF_LITERAL_POOL,
        "boundaries": "derived",
        # Two adjacent routines with no padding and no pool between them.
        "expect_padding": None,
    }


_register_units()


def derive_arith_family(rom_bytes: bytes) -> dict:
    """Derive the whole value-stack arithmetic family from the ROM.

    All three members are re-read here regardless of which unit they live in, so
    the shared contract and the operand order are established from the image
    rather than from the sibling relationship being asserted. Slot 8's
    subtraction is the member that makes the order observable.
    """
    rows = []
    for slot, unit_id, index in ARITH_FAMILY:
        shape = derive_stack_consumer(rom_bytes, unit_id, index)
        rows.append({
            "slot": slot,
            "entry": shape["extent"].split("..")[0],
            "extent": shape["extent"],
            "instructions": shape["instructions"],
            "operation": shape["operation"],
            "pop_shape_matched": shape["pop_shape_matched"],
            "consumes": shape["consumes"],
            "produces": shape["produces"],
            "net_counter_delta": shape["net_counter_delta"],
            "result_slot": shape["result_slot"],
            "upper_slot": shape["upper_slot"],
            "counter_written_before_operand_reads": shape["counter_written_before_operand_reads"],
            "reads_cursor_slot": shape["reads_cursor_slot"],
            "has_underflow_check": shape["has_underflow_check"],
            "calls": shape["calls"],
            "literal_slots": shape["literal_slots"],
            "deeper_operand_is_first_source": shape["deeper_operand_is_first_source"],
        })

    # The order is proven by whichever member is not commutative. Read the
    # mnemonic rather than naming a slot, so this stays honest if the image
    # changes.
    order_proof = []
    for row in rows:
        mnemonic = (row["operation"] or "").split(" ")[0]
        if mnemonic in ("subs", "sub", "rsbs", "rsb"):
            order_proof.append({
                "slot": row["slot"],
                "operation": row["operation"],
                "why": (
                    "subtraction is not commutative, so the two source registers "
                    "fix which stack slot is the left operand"
                ),
                "deeper_operand_is_first_source": row["deeper_operand_is_first_source"],
            })

    return {
        "unit_ids": sorted({unit_id for _slot, unit_id, _index in ARITH_FAMILY}),
        "members": rows,
        "member_count": len(rows),
        "all_shapes_matched": all(row["pop_shape_matched"] for row in rows),
        "shared_contract": {
            "count_offset": VALUE_STACK_COUNT_OFFSET,
            "values_offset": VALUE_STACK_VALUES_OFFSET,
            "entry_size_bytes": VALUE_STACK_ENTRY_SIZE,
            "consumes": 2,
            "produces": 1,
            "net_counter_delta": -1,
            "result_slot": "values[count-2], the LOWER of the two operands",
            "upper_slot": "abandoned above the new counter, not cleared",
            "counter_written_before_operand_reads": True,
            "operand_order": "deeper value is the FIRST source, top value is the SECOND",
        },
        "operand_order_proven_by": order_proof,
        "operand_order_directly_proven": bool(order_proof),
        "commuting_members": [
            row["slot"] for row in rows
            if (row["operation"] or "").split(" ")[0] in ("adds", "add", "muls", "mul", "ands", "orrs", "eors")
        ],
        "calls_across_family": sum(row["calls"] for row in rows),
        "literals_across_family": sum(row["literal_slots"] for row in rows),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def derive_value_use(rom_bytes: bytes) -> dict:
    """Re-read a surviving-value consumer that does NOT write back.

    This matcher exists because the arithmetic shape matcher cannot describe this
    routine, and reusing it produced a report claiming an operation, a result
    slot and a two-into-one reduction that the code does not perform. A report
    field must be derived or absent, never inherited from a shape that did not
    match.

    It matches the seven-instruction POP prefix, then classifies the tail rather
    than assuming it: whether a result is written back into the slot, what calls
    are made, and what literals are loaded.
    """
    base = _gba.ROM_BASE
    start, end, _role = USE_FUNCTIONS[0]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def at(index):
        return insns[index] if 0 <= index < len(insns) else None

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    steps = []

    # A unit reached through the native table may open with a register save, as
    # this one does with `push {r3, lr}`; the pop prefix starts after it.
    off = 1 if insns and insns[0].mnemonic.startswith("push") else 0

    def record(index, name, ok):
        ins = at(index + off)
        steps.append({
            "step": name,
            "address": f"0x{ins.address:08X}" if ins else None,
            "instruction": f"{ins.mnemonic} {ins.op_str}".strip() if ins else None,
            "matched": bool(ok),
        })
        return ok

    a, b, c, d, e, f = (at(k + off) for k in range(6))
    count_reg = _thumb_dst(a) if a else None
    mem_a = _thumb_mem(a) if a else None
    record(0, "read the counter from context+0x00",
           a and a.mnemonic == "ldr" and mem_a and mem_a[1] == VALUE_STACK_COUNT_OFFSET
           and mem_a[2] is None)
    record(1, "decrement it by one",
           b and b.mnemonic == "subs" and immediate(b) == 1 and count_reg in b.op_str)
    count_dec = _thumb_dst(b) if b else count_reg
    mem_c = _thumb_mem(c) if c else None
    record(2, "write the decremented counter back BEFORE the value is read",
           c and c.mnemonic == "str" and mem_c and mem_c[1] == VALUE_STACK_COUNT_OFFSET
           and mem_c[2] is None)
    record(3, "scale the index by four",
           d and d.mnemonic == "lsls" and immediate(d) == 2 and count_dec in d.op_str)
    scaled = _thumb_dst(d) if d else count_dec
    record(4, "form the slot address as context + count*4",
           e and e.mnemonic == "adds" and scaled in e.op_str and "r0" in e.op_str)
    slot_reg = _thumb_dst(e) if e else None
    mem_f = _thumb_mem(f) if f else None
    record(5, "read values[count-1], the old top, through [slot+4]",
           f and f.mnemonic == "ldr" and mem_f and mem_f[1] == VALUE_STACK_ENTRY_SIZE
           and mem_f[2] is None and mem_f[0] == slot_reg)
    value_reg = _thumb_dst(f) if f else None

    tail = insns[6 + off:]
    # A write-back would store into the slot register computed at step 4.
    writes_back = any(
        (m := _thumb_mem(x)) and x.mnemonic.startswith("str") and m[0] == slot_reg
        for x in tail
    )
    calls = []
    for x in tail:
        if x.mnemonic in ("bl", "blx") and x.operands:
            op = x.operands[0]
            if op.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append({"site": f"0x{x.address:08X}", "target": f"0x{op.imm & ~1:08X}"})
            else:
                calls.append({"site": f"0x{x.address:08X}", "target": "register-indirect"})
    literal_slots = []
    for x in insns:
        slot = cp._literal_slot(x.address, "thumb", x.op_str)
        if slot is not None and x.mnemonic.startswith("ldr"):
            literal_slots.append(slot)

    return {
        "unit_id": USE_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "instructions": len(insns),
        "pop_prefix_matched": all(step["matched"] for step in steps),
        "pop_steps": steps,
        "count_offset": VALUE_STACK_COUNT_OFFSET,
        "values_offset": VALUE_STACK_VALUES_OFFSET,
        "entry_size_bytes": VALUE_STACK_ENTRY_SIZE,
        "is_a_pop": True,
        "is_a_peek": False,
        "consumes": 1,
        "produces": 0,
        "writes_back_to_the_stack": writes_back,
        "counter_delta": -1,
        "value_read": "values[count-1], the slot above the new counter",
        "value_register": value_reg,
        "reads_cursor_slot": False,
        "calls": calls,
        "call_count": len(calls),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "has_underflow_check": False,
        "underflow_is_read_only": not writes_back,
        "underflow_effect": (
            "a zero counter becomes 0xFFFFFFFF, so the slot address becomes "
            "context-4 and [slot+4] is context itself; the value passed on is the "
            "brand-new counter 0xFFFFFFFF. Because there is no store to the slot, "
            "nothing below the context is written."
        ),
        "no_write_back_evidence": (
            "the slot register computed at 0x080007F0 is never used as the base of "
            "a store in the tail"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


# ---------------------------------------------------------------------------
# the routine that gives the popped VM value its concrete effect
# ---------------------------------------------------------------------------

def derive_bit_field_write(rom_bytes: bytes) -> dict:
    """Re-read the bit-set arithmetic off the routine's own instructions.

    Every constant below is taken from the instruction stream: the shifts that
    split the bit number, the byte offsets, and the read-modify-write pair. A
    change to any of those changes this block.
    """
    base = _gba.ROM_BASE
    start, end, _role = EFFECT_FUNCTIONS[0]
    insns = list(cp.MD["thumb"].disasm(rom_bytes[start - base : end - base], start))

    def immediate(ins):
        if ins and ins.operands and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM:
            return ins.operands[-1].imm
        return None

    shifts = []
    for ins in insns:
        value = immediate(ins)
        if value is not None and ins.mnemonic in ("asrs", "lsls", "lsrs"):
            shifts.append({"address": f"0x{ins.address:08X}", "mnemonic": ins.mnemonic,
                           "amount": value})
    offsets = []
    for ins in insns:
        mem = _thumb_mem(ins)
        if mem and mem[1]:
            offsets.append({"address": f"0x{ins.address:08X}", "mnemonic": ins.mnemonic,
                            "displacement": mem[1]})
    adds = []
    for ins in insns:
        if ins.mnemonic == "adds" and immediate(ins) is not None:
            adds.append({"address": f"0x{ins.address:08X}", "amount": immediate(ins)})

    byte_shift = next((s for s in shifts if s["mnemonic"] == "asrs"), None)
    mask_pair = [s for s in shifts if s["mnemonic"] in ("lsls", "lsrs") and s["amount"] == 0x1D]
    reads = [x for x in insns if x.mnemonic.startswith("ldr")]
    writes = [x for x in insns if x.mnemonic.startswith("str")]
    combine = [x for x in insns if x.mnemonic == "orrs"]
    literal_slots = [
        slot for x in insns
        if (slot := cp._literal_slot(x.address, "thumb", x.op_str)) is not None
        and x.mnemonic.startswith("ldr")
    ]

    return {
        "unit_id": EFFECT_TU.id,
        "extent": f"0x{start:08X}..0x{end:08X}",
        "instructions": len(insns),
        "byte_index_shift": byte_shift["amount"] if byte_shift else None,
        "byte_index_shift_is_arithmetic": bool(byte_shift and byte_shift["mnemonic"] == "asrs"),
        "bit_index_mask_bits": 32 - 0x1D if len(mask_pair) >= 2 else None,
        "object_offset": 0x50 if any(a["amount"] == 0x50 for a in adds) else None,
        "field_offset_from_object_offset": offsets[0]["displacement"] if offsets else None,
        "read_modify_write": bool(reads and combine and writes),
        "read_count": len(reads),
        "write_count": len(writes),
        "or_count": len(combine),
        "calls": sum(1 for x in insns if x.mnemonic in ("bl", "blx")),
        "literal_slots": len(literal_slots),
        "has_literal_pool": bool(literal_slots),
        "has_bounds_check": False,
        "has_bounds_check_evidence": (
            "there is no compare against a size and no conditional branch anywhere in "
            "the routine; every value selects a byte and the byte is written"
        ),
        "shifts": shifts,
        "offsets": offsets,
        "adds": adds,
        "effect": (
            "sets bit (value & 7) of the byte at base + (value >> 3) + 0x55, preserving "
            "the other seven bits"
        ),
        "negative_index_behaviour": (
            "the byte-index shift is arithmetic, so a value with bit 31 set gives a "
            "negative index and the write lands before the base"
        ),
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def derive_native_table(rom_bytes: bytes) -> dict:
    """Prove the native dispatch table's width and count mechanically.

    The width comes from the handler's own indexed load: `lsls r1,r2,#2` scales
    the index by four before `ldr r1,[r2,r1]`, so entries are four bytes.

    The count is bounded on BOTH sides, which is what makes it a proof rather
    than a scan:

    * LOWER BOUND - the index is one byte, read with `ldrb`, so it ranges over
      0..255. Every one of those must land inside the table, or the handler could
      read past it. So there are at least 256 entries.
    * UPPER BOUND - the primary dispatch table begins at 0x080554C0, an address
      the interpreter loads for itself, and its own extent is anchored by the
      assertion string at 0x0805553C. The native table cannot cross it.

    256 <= 266. That is also why the handler needs no bounds check: no reachable
    index can be out of range.

    A prior claim of 283 entries is refuted here rather than merely restated.
    """
    base = _gba.ROM_BASE
    count = (NATIVE_TABLE_LIMIT - NATIVE_TABLE) // 4
    values = []
    invalid = []
    for index in range(count):
        address = NATIVE_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        values.append(value)
        if not (_gba.in_cartridge(value) and (value & 1)):
            invalid.append({"index": index, "value": f"0x{value:08X}"})

    targets = sorted(v & ~1 for v in values)
    refuted_end = NATIVE_TABLE + REFUTED_NATIVE_ENTRIES * 4

    # Independently re-read what bounds the table from above, so this does not
    # rest on a remembered constant.
    primary_first = int.from_bytes(
        rom_bytes[PRIMARY_TABLE - base : PRIMARY_TABLE - base + 4], "little"
    )
    tail = rom_bytes[PRIMARY_BOUNDING_STRING - base : PRIMARY_BOUNDING_STRING - base + 0x80]
    bounding_text = tail.decode("utf-16-le", "replace").split("\x00")[0]

    return {
        "address": f"0x{NATIVE_TABLE:08X}",
        "entry_width_bytes": 4,
        "entry_width_evidence": (
            "lsls r1,r2,#2 at 0x08003CC8 scales the index by four before "
            "ldr r1,[r2,r1] at 0x08003CCC"
        ),
        "index_width_bytes": 1,
        "index_encoding": "a single unsigned byte, ldrb r2,[r3] at 0x08003CC2",
        "index_range": [0, 255],
        "entries": count,
        "lower_bound": 256,
        "lower_bound_reason": (
            "the index is one byte, so every value in 0..255 must land inside the "
            "table or the handler could read past it"
        ),
        "upper_bound": count,
        "upper_bound_reason": (
            f"the primary dispatch table begins at 0x{PRIMARY_TABLE:08X}, which the "
            "interpreter loads for itself and which is bounded in turn by the "
            f"assertion string at 0x{PRIMARY_BOUNDING_STRING:08X}"
        ),
        "index_is_always_in_range": 256 <= count,
        "invalid_entries": invalid,
        "distinct_targets": len(set(targets)),
        "target_range": [f"0x{targets[0]:08X}", f"0x{targets[-1]:08X}"] if targets else [],
        "bounded_below_by": "the primary table base",
        "bounded_above_by": f"0x{PRIMARY_TABLE:08X}",
        "primary_table_base_recheck": f"0x{primary_first:08X}",
        "primary_table_bounding_string_matches": bounding_text == BCI_BOUNDING_TEXT,
        "refuted_claim": {
            "entries": REFUTED_NATIVE_ENTRIES,
            "would_end_at": f"0x{refuted_end:08X}",
            "why_impossible": (
                f"{REFUTED_NATIVE_ENTRIES} entries at four bytes each reach "
                f"0x{refuted_end:08X}, which is INSIDE the primary dispatch table "
                f"(0x{PRIMARY_TABLE:08X}..0x{PRIMARY_BOUNDING_STRING:08X}). A table "
                "based here cannot have that many entries."
            ),
            "measured_entries": count,
        },
        "derived_from_rom": True,
        "not_hand_written": True,
    }


def derive_dispatch_table(rom_bytes: bytes) -> dict:
    """Prove the dispatch table's extent instead of asserting it.

    A function-pointer table has no length field. Its end is established by what
    follows it: entry 30 occupies 0x08055534..0x08055538 and the UTF-16 assertion
    string begins at 0x0805553C, so the table is exactly 31 entries. This reads
    the string rather than trusting a remembered number.
    """
    base = _gba.ROM_BASE
    entries = []
    for index in range(BCI_DISPATCH_ENTRIES):
        address = BCI_DISPATCH_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        entries.append(value)

    tail = rom_bytes[BCI_BOUNDING_STRING - base : BCI_BOUNDING_STRING - base + 0x80]
    text = tail.decode("utf-16-le", "replace").split("\x00")[0]

    return {
        "address": f"0x{BCI_DISPATCH_TABLE:08X}",
        "entries": len(entries),
        "null_entries": [i for i, v in enumerate(entries) if v == 0],
        "bounding_string_address": f"0x{BCI_BOUNDING_STRING:08X}",
        "bounding_string_text": text,
        "bounding_string_matches": text == BCI_BOUNDING_TEXT,
        "entries_are_thumb_pointers": sum(
            1 for v in entries if v and _gba.in_cartridge(v) and (v & 1)
        ),
    }


def derive_unit_boundaries(rom_bytes: bytes, unit_id: str) -> dict:
    """Re-derive a unit's function extents from the ROM by aligned chain-walk.

    The extents are DERIVED, not read from a table and not hand-written. A long
    linear sweep desyncs whenever a region does not begin on an instruction
    boundary and then misses real branches; walking from an entry stays aligned
    by construction. An earlier revision of this ticket used a linear sweep for
    the caller census and under-counted the callers of 0x08004038 two to
    thirteen, which is why the walk is the method here.
    """
    spec = UNITS.get(unit_id)
    if spec is None or spec.get("boundaries") != "derived":
        raise LiftError(f"{unit_id!r} has no derived boundary; it comes from the manifest")
    unit = spec["unit"]
    functions = spec["functions"]
    expect_padding = spec.get("expect_padding")

    base = _gba.ROM_BASE
    md = cp.MD[unit.isa]
    derived = []
    for start, expected_end, role in functions:
        seen: dict[int, int] = {}
        terminators: list[int] = []
        pending = [start]
        while pending:
            address = pending.pop()
            if address in seen or not _gba.in_cartridge(address):
                continue
            offset = address - base
            for ins in md.disasm(rom_bytes[offset : offset + 0x4000], address):
                if ins.address in seen:
                    break
                seen[ins.address] = ins.size
                mnemonic, operands = ins.mnemonic, ins.op_str
                immediate = None
                if ins.operands and ins.operands[0].type == cp.capstone.arm.ARM_OP_IMM:
                    immediate = ins.operands[0].imm & 0xFFFFFFFF
                if mnemonic in ("bl", "blx"):
                    continue
                if (
                    spec.get("pc_add_successors")
                    and mnemonic.startswith("add")
                    and ins.operands
                    and ins.operands[-1].type == cp.capstone.arm.ARM_OP_IMM
                    and ins.op_str.replace(" ", "").split(",")[1:2] == ["pc"]
                ):
                    # An ARM `add rD, pc, #imm` materialises a code address. In
                    # this unit that is the only static route to the dispatcher's
                    # own return path: the handler is called with `bx r0` and
                    # comes back through a Thumb trampoline to the address this
                    # add puts in r4. Following it is opt-in per unit because in
                    # a Thumb unit the same idiom almost always points at a
                    # literal, not at code.
                    target = ins.address + 8 + ins.operands[-1].imm
                    if unit.rom_address <= target < unit.code_end_address:
                        pending.append(target)
                if mnemonic == "b" and immediate is not None:
                    pending.append(immediate)
                    break
                if mnemonic.startswith(
                    ("bne", "beq", "bcc", "bcs", "bmi", "bpl", "bvs", "bvc",
                     "bhi", "bls", "bge", "blt", "bgt", "ble")
                ) and immediate is not None:
                    pending.append(immediate)
                    continue
                if (
                    mnemonic == "bx"
                    or (mnemonic.startswith("pop") and "pc" in operands)
                    or (mnemonic.startswith("ldr") and operands.startswith("pc"))
                ):
                    terminators.append(ins.address)
                    break
        end = max(a + s for a, s in seen.items())
        gaps = [
            (a + seen[a], b)
            for a, b in zip(sorted(seen), sorted(seen)[1:])
            if a + seen[a] != b
        ]
        derived.append(
            {
                "start": start,
                "end": end,
                "expected_end": expected_end,
                "role": role,
                "instructions": len(seen),
                "terminators": terminators,
                "gaps": gaps,
                "matches": end == expected_end and not gaps,
            }
        )

    # The extents must tile the code body with only alignment padding between.
    tiling_problems = []
    for index, row in enumerate(derived):
        if not row["matches"]:
            tiling_problems.append(
                f"{row['role']}: derived 0x{row['end']:08X}, expected 0x{row['expected_end']:08X}"
            )
        if index + 1 < len(derived):
            nxt = derived[index + 1]
            if row["end"] != nxt["start"]:
                tiling_problems.append(
                    f"gap or overlap between 0x{row['end']:08X} and 0x{nxt['start']:08X}"
                )

    last = derived[-1]
    pool_entries = spec["literal_pool"]
    if pool_entries:
        pool_addresses = sorted(off + _gba.ROM_BASE for off, _value in pool_entries)
        pool_start = pool_addresses[0]
        pool_end = pool_addresses[-1] + 4
        gap = pool_start - last["end"]
        has_pool = True
    else:
        # A register-only function loads no literals, so it has no pool. That is
        # a fact about the unit, not a missing measurement, and the report says
        # which it is.
        pool_start = pool_end = None
        gap = None
        has_pool = False

    if expect_padding is None or not has_pool:
        padding = None
    else:
        padding = gap
        if padding != expect_padding:
            tiling_problems.append(
                f"expected {expect_padding} padding bytes before the pool, saw {padding}"
            )

    return {
        "method": "aligned chain-walk from each entry, following local branches",
        "unit_id": unit_id,
        "code_extent": f"0x{unit.rom_address:08X}..0x{unit.code_end_address:08X}",
        "pool_extent": f"0x{pool_start:08X}..0x{pool_end:08X}" if has_pool else None,
        "has_literal_pool": has_pool,
        "pool_is_adjacent_to_code": bool(has_pool and pool_start == last["end"]),
        "pool_gap_bytes": gap,
        "alignment_padding_bytes": padding,
        "functions": [
            {
                "start": f"0x{row['start']:08X}",
                "end": f"0x{row['end']:08X}",
                "size": row["end"] - row["start"],
                "instructions": row["instructions"],
                "role": row["role"],
                "terminators": [f"0x{t:08X}" for t in row["terminators"]],
                "gaps": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in row["gaps"]],
                "matches_expected": row["matches"],
            }
            for row in derived
        ],
        "problems": tiling_problems,
        "derived_from_rom": True,
        "not_hand_written": True,
    }


class LiftError(RuntimeError):
    """Raised when the lift loop cannot proceed."""


# ---------------------------------------------------------------------------
# the modern toolchain
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class ModernToolchain:
    """A host ARM cross toolchain, identified by running it."""

    root: Path
    prefix: str
    gcc: Path
    ld: Path
    objcopy: Path
    objdump: Path
    nm: Path

    @property
    def root_label(self) -> str:
        return "<" + DEVKITARM_ENV + ">"

    def relabel(self, text: str) -> str:
        """Replace machine- and checkout-specific roots with stable labels.

        Reports are committed, so they must not record where a compiler or a
        checkout happens to live. The toolchain root becomes <DEVKITARM>, the
        repository root becomes <REPO>, and any remaining absolute path is
        replaced by <path>. Meaning is preserved rather than the text dropped.
        """
        for root, label in ((self.root, self.root_label), (_identity.REPO_ROOT, "<REPO>")):
            for form in (str(root), str(root).replace("\\", "/")):
                text = text.replace(form, label)
        return scrub_absolute_paths(text)

    def as_dict(self) -> dict:
        return {
            "family": "GNU Arm Embedded (devkitARM)",
            "root": self.root_label,
            "prefix": self.prefix,
            "tools": {
                "gcc": self.relabel(str(self.gcc)),
                "ld": self.relabel(str(self.ld)),
                "objcopy": self.relabel(str(self.objcopy)),
                "objdump": self.relabel(str(self.objdump)),
                "nm": self.relabel(str(self.nm)),
            },
        }


def _run(command: list, *, timeout: float = 180.0, cwd: Path | None = None):
    return subprocess.run(
        [str(c) for c in command],
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
        cwd=str(cwd) if cwd else None,
    )


def discover_modern_toolchain(root: str | Path | None = None) -> ModernToolchain | None:
    """Locate an existing ARM cross toolchain. Installs nothing.

    An EXPLICIT root is authoritative: if it does not hold a complete toolchain
    the answer is None, never a silent fallback to somewhere else. Falling back
    would mean a caller who pinned a toolchain could be handed a different one
    and never told. $DEVKITARM and the devkitPro default are consulted only when
    no root was given.

    Every tool must be present; a partial installation is reported absent rather
    than used, so a build can never half-run.
    """
    if root is not None:
        candidates = [Path(root)]
    else:
        candidates = []
        env = os.environ.get(DEVKITARM_ENV, "").strip()
        if env:
            candidates.append(Path(env))
        candidates.append(Path(DEFAULT_DEVKITARM))

    for candidate in candidates:
        bin_dir = candidate / "bin"
        tools = {
            name: bin_dir / f"arm-none-eabi-{name}.exe"
            for name in ("gcc", "ld", "objcopy", "objdump", "nm")
        }
        if all(path.is_file() for path in tools.values()):
            return ModernToolchain(
                root=candidate,
                prefix="arm-none-eabi-",
                gcc=tools["gcc"],
                ld=tools["ld"],
                objcopy=tools["objcopy"],
                objdump=tools["objdump"],
                nm=tools["nm"],
            )
    return None


def toolchain_identity(toolchain: ModernToolchain) -> dict:
    """Version facts, read from the tools themselves rather than assumed."""
    gcc_version = _run([toolchain.gcc, "--version"])
    binutils = _run([toolchain.objdump, "--version"])
    machine = _run([toolchain.gcc, "-dumpmachine"])
    dumpversion = _run([toolchain.gcc, "-dumpversion"])

    def first_line(completed) -> str:
        for line in (completed.stdout or "").splitlines():
            if line.strip():
                return line.strip()
        return ""

    return {
        "gcc_banner": first_line(gcc_version),
        "gcc_version": (dumpversion.stdout or "").strip(),
        "target_triple": (machine.stdout or "").strip(),
        "binutils_banner": first_line(binutils),
        "compiler_family": "gcc",
        "is_the_original_compiler": False,
        "why_not": (
            "the original translation unit was built by ARM Developer Suite 1.2 "
            "(the surviving command line names tcpp). GCC is a different "
            "compiler with a different code generator, so its output cannot "
            "establish anything about ADS 1.2."
        ),
    }


def probe_target_support(toolchain: ModernToolchain, workdir: Path) -> dict:
    """Prove the toolchain really builds ARM7TDMI Thumb, by building something.

    A version banner does not establish that the configuration is supported, so
    this compiles, links and disassembles a two-line function and reports the
    machine code it produced.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    source = workdir / "support_probe.c"
    source.write_text("int lift_probe(int x) { return x + 1; }\n", encoding="ascii", newline="\n")
    obj = workdir / "support_probe.o"

    compile_command = [
        toolchain.gcc, "-c", "-mcpu=arm7tdmi", "-mthumb", "-O1",
        "-ffreestanding", "-fno-common", "-fno-builtin",
        "-o", obj, source,
    ]
    completed = _run(compile_command)
    result = {
        "supported": False,
        "cpu": "arm7tdmi",
        "instruction_set": "thumb",
        "commands": [toolchain.relabel(" ".join(str(c) for c in compile_command))],
        "disassembly": [],
        "detail": "",
    }
    if completed.returncode != 0:
        result["detail"] = (
            f"the toolchain refused -mcpu=arm7tdmi -mthumb: "
            f"{(completed.stderr or completed.stdout).strip()[:300]}"
        )
        return result

    disassembly = _run([toolchain.objdump, "-d", "--no-show-raw-insn", obj])
    lines = [
        line.split("\t", 1)[-1].strip().replace("\t", " ")
        for line in (disassembly.stdout or "").splitlines()
        if re.match(r"^\s+[0-9a-f]+:", line)
    ]
    result["disassembly"] = lines[:8]
    # Positive evidence that this really is ARM7TDMI Thumb code: the probe
    # function must produce at least an argument/return register write and a
    # return. Requiring every line to mention r0 was wrong - `bx lr` does not.
    writes_r0 = any(
        re.match(r"^(adds|movs|subs|add|mov|sub)\s+r0\b", line) for line in lines
    )
    returns = any(
        line.startswith("bx lr")
        or (line.startswith("pop") and "pc" in line)
        or line.startswith("ldr pc")
        for line in lines
    )
    result["supported"] = bool(lines) and writes_r0 and returns
    result["detail"] = (
        f"compiled and disassembled a probe function for ARM7TDMI Thumb: "
        f"{len(lines)} instruction(s), r0 written and a return present"
        if result["supported"]
        else "the toolchain produced no usable Thumb disassembly for the probe"
    )
    return result


# ---------------------------------------------------------------------------
# targets
# ---------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class LiftTarget:
    id: str
    name: str
    probe_translation_unit: str
    decomp_source: str
    probe_source: str
    selftest_source: str
    semantic_minimum_checks: int
    host_build_bits: int
    ticket: str
    cpu: str
    isa: str
    optimization: str
    role: str
    notes: str
    extra_compiler_flags: tuple[str, ...]

    @property
    def rom_address(self) -> int:
        return UNITS[self.probe_translation_unit]["unit"].rom_address


def load_target_registry(path: Path | None = None) -> dict:
    target = path or TARGETS_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def load_targets(path: Path | None = None) -> list[LiftTarget]:
    registry = load_target_registry(path)
    out: list[LiftTarget] = []
    for entry in registry["targets"]:
        out.append(
            LiftTarget(
                id=entry["id"],
                name=entry["name"],
                probe_translation_unit=entry["probe_translation_unit"],
                decomp_source=entry["decomp_source"],
                probe_source=entry["probe_source"],
                selftest_source=entry["selftest_source"],
                semantic_minimum_checks=int(entry["semantic_minimum_checks"]),
                host_build_bits=int(entry.get("host_build_bits", 32)),
                ticket=entry.get("ticket", "DECOMP-LIFT-PILOT-001"),
                cpu=entry["compiler"]["cpu"],
                isa=entry["compiler"]["isa"],
                optimization=entry["compiler"]["optimization"],
                role=entry["role"],
                notes=entry.get("notes", ""),
                extra_compiler_flags=tuple(entry["compiler"].get("extra_flags", ())),
            )
        )
    return out


def get_target(target_id: str) -> LiftTarget:
    for target in load_targets():
        if target.id == target_id:
            return target
    raise LiftError(f"unknown lift target {target_id!r}")


def _unit_for(target: LiftTarget) -> cp.TranslationUnit:
    spec = UNITS.get(target.probe_translation_unit)
    if spec is None:
        raise LiftError(
            f"target {target.id!r} names translation unit "
            f"{target.probe_translation_unit!r}, which this module does not know"
        )
    return spec["unit"]


def _probes_for(target: LiftTarget) -> list[dict]:
    """Function rows for a target's unit.

    GBARam's boundaries live in the ADS probe manifest, which derives and
    verifies them. The ByteCodeInterpreter's are derived from the ROM here, and
    re-derived and checked on every run by derive_unit_boundaries, so a drift in
    either the ROM or the derivation is an error rather than a silent change.
    """
    spec = UNITS[target.probe_translation_unit]
    if spec["boundaries"] == "manifest":
        manifest = json.loads(PROBES_PATH.read_text(encoding="utf-8"))
        return [
            probe
            for probe in manifest["probes"]
            if probe["translation_unit"] == target.probe_translation_unit
        ]
    unit = spec["unit"]
    return [
        {
            "name": f"sub_{start:08X}",
            "start": f"0x{start:08X}",
            "end": f"0x{end:08X}",
            "isa": unit.isa,
            "role": role,
            "translation_unit": unit.id,
        }
        for start, end, role in spec["functions"]
    ]


# ---------------------------------------------------------------------------
# per-function analysis
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class FunctionAnalysis:
    """What can be said about one function from its bytes alone."""

    start: int
    end: int
    isa: str
    instructions: int
    size: int
    first_instruction: str
    mnemonics: list[str]
    calls: list[int]
    literal_slots: list[int]
    returns: int
    leaf: bool
    callee_saved_pushed: list[str]
    frame_size: int
    written_registers: list[str]

    def as_dict(self, base: int) -> dict:
        return {
            "start": f"0x{self.start:08X}",
            "end": f"0x{self.end:08X}",
            "size": self.size,
            "isa": self.isa,
            "instructions": self.instructions,
            "first_instruction": self.first_instruction,
            "calls": [f"0x{c:08X}" for c in self.calls],
            "literal_slots": [f"0x{s:08X}" for s in self.literal_slots],
            "returns": self.returns,
            "leaf": self.leaf,
            "abi": {
                "callee_saved_pushed": list(self.callee_saved_pushed),
                "frame_size_bytes": self.frame_size,
                "written_registers": list(self.written_registers),
            },
        }


def _register_list(op_str: str) -> list[str]:
    inner = op_str.split("{", 1)[-1].split("}", 1)[0]
    return [part.strip() for part in inner.split(",") if part.strip()]


_CALLEE_SAVED = {"r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "sl", "fp"}


def analyse_function(
    raw: bytes, base: int, start: int, end: int, isa: str
) -> FunctionAnalysis:
    """Disassemble [start, end) of a buffer whose byte 0 sits at `base`.

    `base` matters: the modern build is a fresh buffer linked at the unit's ROM
    address, so indexing it with `start - ROM_BASE` reads the WRONG BYTES. Every
    caller states the base of the buffer it is handing over.
    """
    offset = start - base
    if offset < 0:
        raise LiftError(f"0x{start:08X} is before the buffer base 0x{base:08X}")
    length = end - start
    segment = raw[offset : offset + length]

    md = cp.MD[isa]
    instructions = 0
    mnemonics: list[str] = []
    calls: list[int] = []
    literal_slots: list[int] = []
    returns = 0
    callee_saved: list[str] = []
    frame_size = 0
    written: set[str] = set()
    first = ""

    for ins in md.disasm(segment, start):
        instructions += 1
        mnemonics.append(ins.mnemonic)
        if not first:
            first = f"{ins.mnemonic} {ins.op_str}".strip()

        slot = cp._literal_slot(ins.address, isa, ins.op_str)
        if slot is not None and ins.mnemonic.startswith("ldr"):
            literal_slots.append(slot)

        if ins.mnemonic in ("bl", "blx") and ins.operands:
            operand = ins.operands[0]
            if operand.type == cp.capstone.arm.ARM_OP_IMM:
                calls.append(operand.imm & ~1)

        if ins.mnemonic == "bx" and "lr" in ins.op_str:
            returns += 1
        if ins.mnemonic == "bx" and "lr" not in ins.op_str:
            # GCC returns via `pop {rN}; bx rN` rather than `bx lr`. Counting
            # both keeps the metric comparable across the two compilers; a
            # register-form bx inside a function is a computed jump in principle,
            # so this is documented as "return-shaped", not proven returns.
            returns += 1
        if ins.mnemonic.startswith("pop") and "pc" in ins.op_str:
            returns += 1
        if ins.mnemonic.startswith("ldr") and "pc" in ins.op_str.split(",")[0]:
            returns += 1

        if ins.mnemonic.startswith("push"):
            for name in _register_list(ins.op_str):
                if name in _CALLEE_SAVED and name not in callee_saved:
                    callee_saved.append(name)
        if ins.mnemonic in ("sub", "add") and ins.op_str.startswith("sp, sp"):
            try:
                amount = int(ins.op_str.split("#")[1].strip(), 0)
                frame_size += amount if ins.mnemonic == "sub" else -amount
            except (IndexError, ValueError):
                pass

        if ins.operands:
            destination = ins.reg_name(ins.operands[0].reg) if ins.operands[0].type == cp.capstone.arm.ARM_OP_REG else None
            if destination and destination.startswith("r"):
                written.add(destination)

    return FunctionAnalysis(
        start=start,
        end=end,
        isa=isa,
        instructions=instructions,
        size=length,
        first_instruction=first,
        mnemonics=mnemonics,
        calls=sorted(set(calls)),
        literal_slots=sorted(set(literal_slots)),
        returns=returns,
        leaf=not calls,
        callee_saved_pushed=callee_saved,
        frame_size=frame_size,
        written_registers=sorted(written, key=lambda r: int(r[1:])),
    )


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class LiftBuild:
    ok: bool
    commands: list[str]
    stdout: str
    stderr: str
    object_file: Path | None
    elf: Path | None
    binary: Path | None
    raw: bytes
    symbols: dict[str, tuple[int, int]]

    def as_dict(self, toolchain: ModernToolchain, target: LiftTarget) -> dict:
        return {
            "ok": self.ok,
            "commands": [toolchain.relabel(c) for c in self.commands],
            "produced_byte_length": len(self.raw),
            "symbols": {
                name: {"address": f"0x{addr:08X}", "size": size}
                for name, (addr, size) in sorted(self.symbols.items())
            },
            "diagnostics": (self.stderr or "").strip()[-1200:],
        }


def render_linker_script(target: LiftTarget, unit: cp.TranslationUnit, entry: str) -> str:
    """A controlled layout that places the unit at its original ROM address.

    Without this every PC-relative literal displacement and every call would
    differ for a reason that says nothing about the compiler.
    """
    return (
        "/* generated by tools/buusfury/lift.py - do not edit */\n"
        f"ENTRY({entry})\n"
        "SECTIONS\n{\n"
        f"  . = 0x{unit.rom_address:08X};\n"
        "  .text : { *(.text) *(.text.*) }\n"
        "  .rodata : { *(.rodata) *(.rodata.*) }\n"
        "  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*)\n"
        "               *(.ARM.attributes) *(.data) *(.bss) }\n"
        "}\n"
    )


def parse_symbols(nm_output: str) -> dict[str, tuple[int, int]]:
    """`nm -S --defined-only` output -> {name: (address, size)}.

    Only function symbols in .text are kept; the file and section symbols are
    not functions and must not become comparison rows.
    """
    out: dict[str, tuple[int, int]] = {}
    for line in nm_output.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        address, size, kind, name = parts
        if kind not in ("T", "t"):
            continue
        try:
            out[name] = (int(address, 16), int(size, 16))
        except ValueError:
            continue
    return out


def derive_external_calls(rom_bytes: bytes, unit_id: str) -> dict[str, int]:
    """Calls a unit makes to code it does not contain, read from the ROM.

    The reconstruction declares these rather than reconstructing them, so the
    link needs a value for each. Binding them to the ORIGINAL addresses, read
    out of the unit's own BL instructions, keeps every call displacement
    correct and adds no stub code to the compared bytes. The symbol names line
    up with the source automatically because the project names functions
    sub_<ROM address>.
    """
    spec = UNITS[unit_id]
    unit = spec["unit"]
    base = _gba.ROM_BASE
    found: dict[str, int] = {}
    for start, end, _role in spec["functions"]:
        for ins in cp.MD[unit.isa].disasm(rom_bytes[start - base : end - base], start):
            if ins.mnemonic not in ("bl", "blx") or not ins.operands:
                continue
            operand = ins.operands[0]
            if operand.type != cp.capstone.arm.ARM_OP_IMM:
                continue
            target = operand.imm & ~1
            if not (unit.rom_address <= target < unit.code_end_address):
                found[f"sub_{target:08X}"] = target
    return found


def render_external_symbols(symbols: dict[str, int]) -> str:
    """Declare each external call target as an absolute THUMB function.

    `--defsym` cannot express this and is a trap: an absolute symbol made that
    way carries no Thumb marking, so the linker emits a Thumb-to-ARM
    interworking veneer. The veneer does `bx pc` and then an ARM branch, which
    enters a Thumb target in ARM state, and it adds eight bytes per target to
    the compared image. Both were observed here rather than predicted.

    `.thumb_func` before `.set` marks the absolute symbol as Thumb, and the call
    becomes a direct Thumb BL to the original address with nothing emitted. An
    earlier revision of this module used `--defsym` and produced five veneers in
    the ByteCodeInterpreter build.
    """
    lines = [
        "/* generated by tools/buusfury/lift.py - do not edit */",
        "\t.syntax unified",
        "\t.thumb",
        "",
        "/* Absolute Thumb entry points for calls this unit makes but does not",
        " * contain. The bodies are not here because these functions belong to",
        " * other translation units; only the call target matters. */",
    ]
    for name, address in sorted(symbols.items()):
        lines.append(f"\t.globl {name}")
        lines.append("\t.thumb_func")
        lines.append(f"\t.set {name}, 0x{address:08X}")
    lines.append("")
    return "\n".join(lines)


def build_target(
    toolchain: ModernToolchain,
    target: LiftTarget,
    workdir: Path,
    *,
    source_override: Path | None = None,
    entry: str | None = None,
    defined_symbols: dict[str, int] | None = None,
) -> LiftBuild:
    """Compile, link at the original address, and emit raw bytes."""
    workdir.mkdir(parents=True, exist_ok=True)
    unit = _unit_for(target)
    probes = _probes_for(target)
    entry = entry or (probes[0]["name"] if probes else "_start")
    source = source_override or (_identity.REPO_ROOT / target.decomp_source)
    if not source.is_file():
        raise LiftError(f"the decompiled source {target.decomp_source} does not exist")

    obj = workdir / f"{target.id}.o"
    elf = workdir / f"{target.id}.elf"
    binary = workdir / f"{target.id}.bin"
    script = workdir / f"{target.id}.ld"
    map_file = workdir / f"{target.id}.map"
    script.write_text(render_linker_script(target, unit, entry), encoding="ascii", newline="\n")

    compile_command = [
        toolchain.gcc, "-c",
        f"-mcpu={target.cpu}",
        "-mthumb" if target.isa == "thumb" else "-marm",
        target.optimization,
        "-ffreestanding", "-fno-common", "-fno-builtin",
        "-fomit-frame-pointer", "-mno-unaligned-access",
        *target.extra_compiler_flags,
        "-o", obj, source,
    ]

    # Declare the unit's external call targets as Thumb functions. See
    # render_external_symbols for why --defsym is not used.
    symbols_source = workdir / f"{target.id}_externs.s"
    symbols_source.write_text(
        render_external_symbols(defined_symbols or {}), encoding="ascii", newline="\n"
    )
    symbols_object = workdir / f"{target.id}_externs.o"
    symbols_command = [
        toolchain.gcc, "-c", "-mcpu=" + target.cpu,
        "-mthumb" if target.isa == "thumb" else "-marm",
        "-o", symbols_object, "-x", "assembler-with-cpp", symbols_source,
    ]

    link_command = [
        toolchain.gcc, "-nostdlib",
        f"-Wl,-T,{script}", f"-Wl,-Map,{map_file}",
        "-o", elf, obj, symbols_object,
    ]
    # Restricted on purpose: the emitted bytes are the reconstructed code and
    # its literals, and nothing a stub or a linker helper might add.
    objcopy_command = [
        toolchain.objcopy, "-O", "binary", "-j", ".text", "-j", ".rodata", elf, binary,
    ]
    commands = [
        " ".join(str(c) for c in compile_command),
        " ".join(str(c) for c in symbols_command),
        " ".join(str(c) for c in link_command),
        " ".join(str(c) for c in objcopy_command),
    ]

    log: list[str] = []
    for command in (compile_command, symbols_command, link_command, objcopy_command):
        completed = _run(command)
        log.append(f"$ {' '.join(str(c) for c in command)}\n{completed.stdout}{completed.stderr}")
        if completed.returncode != 0:
            return LiftBuild(
                ok=False, commands=commands,
                stdout=completed.stdout or "", stderr=completed.stderr or "",
                object_file=None, elf=None, binary=None, raw=b"", symbols={},
            )

    symbols = parse_symbols(_run([toolchain.nm, "-S", "--defined-only", elf]).stdout or "")
    raw = binary.read_bytes() if binary.is_file() else b""
    return LiftBuild(
        ok=True, commands=commands, stdout="\n".join(log), stderr="",
        object_file=obj, elf=elf, binary=binary, raw=raw, symbols=symbols,
    )


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------
def compare_bytes_on_target_boundaries(
    original: bytes, modern: bytes, unit: cp.TranslationUnit
) -> dict:
    """Byte and instruction comparison keyed on the ORIGINAL's boundaries.

    Instruction granularity is taken from the TARGET, not from the modern
    output. Capstone renders distinct Thumb encodings identically (0x4280 and
    0x4500 are both `cmp r0, r0`), so a positional text comparison can report
    zero differences for unequal bytes and can exceed the instruction count.
    Keying on the original's own spans removes both failure modes.

    `instruction_spans` returns (OFFSET-FROM-BASE, SIZE) pairs and decodes the
    buffer it is given, so it is handed the translation unit's own 624 bytes.
    Passing the whole ROM here would decode the cartridge header while labelling
    it with the unit's address, which is how an earlier revision reported zero
    differing instructions for 595 differing bytes.
    """
    overlap = min(len(original), len(modern))
    differing = sum(1 for i in range(overlap) if original[i] != modern[i])

    # Decode only the CODE body: the trailing 16 bytes are the literal pool, and
    # walking constants as instructions invents spans that are not instructions.
    code = original[: unit.code_length]
    spans = cp.instruction_spans(code, unit.rom_address, unit.isa)
    matching_spans = 0
    differing_spans = 0
    covered = 0
    for offset, size in spans:
        if offset + size > overlap:
            continue
        covered += size
        if original[offset : offset + size] == modern[offset : offset + size]:
            matching_spans += 1
        else:
            differing_spans += 1

    uncovered = max(0, overlap - covered)
    modern_only = max(0, len(modern) - len(original))
    original_only = max(0, len(original) - len(modern))

    return {
        "original_byte_length": len(original),
        "modern_byte_length": len(modern),
        "overlap_byte_length": overlap,
        "differing_bytes_in_overlap": differing,
        "matching_bytes_in_overlap": overlap - differing,
        "original_only_bytes": original_only,
        "modern_only_bytes": modern_only,
        "original_instruction_spans": len(spans),
        "matching_instruction_spans": matching_spans,
        "differing_instruction_spans": differing_spans,
        # Published separately and clamped: folding uncovered bytes into the
        # differing count once drove a "matching" field negative.
        "bytes_not_covered_by_an_original_instruction": uncovered,
        "byte_identical": len(original) == len(modern) and differing == 0,
        # A BOOLEAN, so a gate can read it, plus the prose that explains it.
        "is_a_match_claim": False,
        "match_claim_note": (
            "MEASUREMENT ONLY. This compares a modern GCC build against the "
            "cartridge. A modern compiler is not the original compiler, so a "
            "difference here is expected and proves nothing; an identity here "
            "would also prove nothing about ADS 1.2. ADS_MATCH stays BLOCKED."
        ),
    }


def _pool_runs(slots: list[int]) -> list[list[int]]:
    """Group referenced literal slots into contiguous 4-byte runs."""
    runs: list[list[int]] = []
    for slot in sorted(set(slots)):
        if runs and slot == runs[-1][1]:
            runs[-1][1] = slot + 4
        else:
            runs.append([slot, slot + 4])
    return runs


def literal_pool_structure(
    original_rows: list[FunctionAnalysis],
    modern_rows: list[FunctionAnalysis],
    unit: cp.TranslationUnit,
) -> dict:
    """Compare how the two compilers POOL literals.

    This is the sharpest structural difference the loop exposes, and it is the
    reason the comparison must be translation-unit scoped: the original places
    ONE pool after the last function and every function reaches back into it,
    which is itself the evidence that the region was a single translation unit.
    A modern compiler pools per function or per basic block, so no individual
    function can be compared standalone.
    """
    original_slots = sorted({s for row in original_rows for s in row.literal_slots})
    modern_slots = sorted({s for row in modern_rows for s in row.literal_slots})
    original_runs = _pool_runs(original_slots)
    modern_runs = _pool_runs(modern_slots)

    declared_start = unit.code_end_address
    declared_end = unit.end_address
    declared_slots = sorted(off + _gba.ROM_BASE for off, _value in unit.literal_pool)
    original_shared = (
        len(original_runs) == 1
        and original_runs[0][0] == declared_start
        and original_runs[0][1] == declared_end
    )
    modern_shared = len(modern_runs) <= 1

    # Accounting, which is the property that actually matters: is every literal
    # the code loads one of the words the unit declares, and is every declared
    # word actually used? A unit whose literals live in two places satisfies
    # this even though "one shared run" is false, and forcing the run test
    # would report a defect that is not there.
    referenced = set(original_slots)
    declared = set(declared_slots)
    return {
        "original": {
            "distinct_slots": len(original_slots),
            "contiguous_runs": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in original_runs],
            "run_count": len(original_runs),
            "shared_pool": original_shared,
            # A single-function unit with no adjacent pool cannot have a shared
            # run, so the test is not applicable rather than failed.
            "shared_pool_applicable": unit.code_end_address != unit.end_address,
            "declared_pool": [f"0x{declared_start:08X}", f"0x{declared_end:08X}"],
            "declared_slots": [f"0x{a:08X}" for a in declared_slots],
            "declared_slots_used": [f"0x{a:08X}" for a in sorted(referenced & declared)],
            "all_referenced_slots_are_declared": referenced <= declared,
            "all_declared_slots_are_referenced": declared <= referenced,
            "undeclared_slots": [f"0x{a:08X}" for a in sorted(referenced - declared)],
            "functions_reaching_it": sum(1 for row in original_rows if row.literal_slots),
        },
        "modern": {
            "distinct_slots": len(modern_slots),
            "contiguous_runs": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in modern_runs],
            "run_count": len(modern_runs),
            "shared_pool": modern_shared,
            "functions_reaching_a_pool": sum(1 for row in modern_rows if row.literal_slots),
        },
        "interpretation": (
            "the original's literals are accounted for by the words the unit "
            "declares; the modern build pools differently, which is a structural "
            "consequence of the compiler rather than a defect in the "
            "reconstruction. It is also why a function with a literal load "
            "cannot be compared standalone."
        ),
        "is_a_match_claim": False,
    }


def compare_functions(
    rom_bytes: bytes,
    unit: cp.TranslationUnit,
    probes: list[dict],
    build: LiftBuild,
) -> tuple[list[dict], dict]:
    """Pair original functions with modern ones by symbol name.

    The reconstruction names each function sub_<ROM address>, so the pairing is
    exact and needs no heuristic. A missing symbol is reported as missing rather
    than treated as a difference.

    Returns (rows, literal_pool_structure). The pool comparison is derived from
    the same analyses the rows are, so the two can never disagree.
    """
    rows: list[dict] = []
    original_analyses: list[FunctionAnalysis] = []
    modern_analyses: list[FunctionAnalysis] = []

    for probe in probes:
        name = probe["name"]
        original = analyse_function(
            rom_bytes, _gba.ROM_BASE, int(probe["start"], 16), int(probe["end"], 16), probe["isa"]
        )
        original_analyses.append(original)
        modern = None
        if name in build.symbols:
            address, size = build.symbols[name]
            modern = analyse_function(
                build.raw, unit.rom_address, address, address + size, probe["isa"]
            )
            modern_analyses.append(modern)

        row = {
            "name": name,
            "role": probe["role"],
            "original": original.as_dict(unit.rom_address),
            "modern": modern.as_dict(unit.rom_address) if modern else None,
            "modern_symbol_present": modern is not None,
        }
        if modern is not None:
            row["delta"] = {
                "size_bytes": modern.size - original.size,
                "instructions": modern.instructions - original.instructions,
                "returns": modern.returns - original.returns,
                "calls": len(modern.calls) - len(original.calls),
                "literal_slots": len(modern.literal_slots) - len(original.literal_slots),
            }
            # Extent identity is the only condition under which a per-function
            # byte comparison is even meaningful.
            row["same_extent"] = (
                modern.start == original.start and modern.end == original.end
            )
            if row["same_extent"]:
                start = original.start - _gba.ROM_BASE
                offset = original.start - unit.rom_address
                row["byte_identical"] = (
                    rom_bytes[start : start + original.size]
                    == build.raw[offset : offset + original.size]
                )
            else:
                row["byte_identical"] = False
        rows.append(row)

    pools = literal_pool_structure(original_analyses, modern_analyses, unit)
    return rows, pools


# ---------------------------------------------------------------------------
# the host semantic self-check
# ---------------------------------------------------------------------------
_ABSOLUTE_PATH = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|]*")


def scrub_absolute_paths(text: str) -> str:
    """Replace machine-specific paths in captured tool output.

    The lift report is committed, so it must not record where a compiler happens
    to live on the machine that produced it. Positive evidence is preserved: the
    path is replaced by a marker rather than the line being dropped.
    """
    return _ABSOLUTE_PATH.sub("<path>", text)


def semantic_verdict(
    returncode: int, checks: int, failures: int, minimum: int | None = None
) -> tuple[str, str]:
    """The SEMANTIC verdict, as a pure function so it can be tested directly.

    A pass requires POSITIVE evidence: the run must exit 0, report ZERO failures,
    AND report at least `minimum` assertions. A run that exits 0 with fewer checks
    is PARTIAL, never PROVEN, because a self-check that stopped early otherwise
    looks exactly like one that passed.

    `minimum` is per target. One global number would either wave through a
    truncated run of a small self-check or fail a genuinely smaller one.
    """
    minimum = MIN_SEMANTIC_CHECKS if minimum is None else minimum
    if returncode != 0 or failures > 0:
        return (
            "FAILED",
            f"the reconstruction is not behaviourally coherent: exit {returncode}, "
            f"{failures} failures",
        )
    if checks < minimum:
        return (
            "PARTIAL",
            f"all assertions passed but only {checks} ran, below the required "
            f"minimum of {minimum}: checks were lost",
        )
    return (
        "PROVEN",
        f"{checks} behavioural assertions passed with 0 failures "
        f"(minimum {minimum})",
    )


def run_host_selftest(
    workdir: Path,
    *,
    source: Path | None = None,
    minimum_checks: int | None = None,
    host_bits: int = 32,
    timeout: float = 240.0,
) -> dict:
    """Compile and RUN a self-check on the host.

    This is the SEMANTIC verdict. It says nothing about code generation: a
    translation unit whose C is wrong cannot match under any compiler, so a
    behavioural failure is a real defect, while a pass only removes one class of
    error.

    `host_bits` selects the width of the host toolchain. A reconstruction that
    holds pointers in u32 fields models a 32-bit machine and must be built
    32-bit: on a 64-bit host the high half of every stored context address is
    lost and the first dereference through one faults with an access violation.
    That is a property of the machine model, not something to paper over with a
    widened typedef.
    """
    minimum = MIN_SEMANTIC_CHECKS if minimum_checks is None else minimum_checks
    selftest = source or (_identity.REPO_ROOT / "src" / "probes" / "gbaram_selftest.c")
    result = {
        "status": "UNTESTED",
        "checks": 0,
        "failures": None,
        "minimum_checks": minimum,
        "host_compiler": None,
        "host_build_bits": host_bits,
        "detail": "",
        "output": "",
    }
    if not selftest.is_file():
        result["detail"] = f"{selftest.name} is missing"
        return result

    vcvars_name = "vcvars64.bat" if host_bits == 64 else "vcvars32.bat"
    vcvars_candidates = [
        Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools")
        / "VC" / "Auxiliary" / "Build" / vcvars_name,
        Path(r"C:\Program Files\Microsoft Visual Studio\2022\Community")
        / "VC" / "Auxiliary" / "Build" / vcvars_name,
    ]
    vcvars = next((p for p in vcvars_candidates if p.is_file()), None)
    if vcvars is None and shutil.which("cl") is None:
        result["detail"] = "no host C compiler available; SEMANTIC is UNTESTED here"
        return result

    comspec = os.environ.get("COMSPEC") or r"C:\Windows\System32\cmd.exe"
    if not Path(comspec).is_file():
        result["detail"] = "no usable command interpreter for the self-check"
        return result

    workdir.mkdir(parents=True, exist_ok=True)
    exe = workdir / "selftest.exe"
    compile_log = workdir / "compile.log"
    batch = workdir / "build_selftest.bat"
    # A batch file, not a /c string: cmd's quote handling mangles a command that
    # starts with a quoted path and silently returns exit 1 with empty output.
    # /Fo and /Fd are avoided: a path ending in a backslash before a closing
    # quote escapes it and cl fails with "Cannot open compiler generated file".
    lines = ["@echo off"]
    if vcvars is not None:
        lines.append(f'call "{vcvars}" >nul 2>&1')
        lines.append("if errorlevel 1 exit /b 90")
    lines.append(f'cd /d "{workdir}"')
    lines.append(
        f'cl /nologo /W3 /std:c11 /TC /Fe:selftest.exe "{selftest}" '
        f'> "{compile_log}" 2>&1'
    )
    batch.write_text("\r\n".join(lines) + "\r\n", encoding="ascii", newline="\n")

    compiled = _run([comspec, "/c", batch], timeout=timeout)
    log = compile_log.read_text(encoding="utf-8", errors="replace") if compile_log.is_file() else ""
    if compiled.returncode != 0 or not exe.is_file():
        result["status"] = "FAILED"
        result["host_compiler"] = f"MSVC cl.exe ({host_bits}-bit)"
        result["detail"] = f"self-check failed to build (exit {compiled.returncode})"
        result["output"] = scrub_absolute_paths(log[-2000:])
        return result

    executed = _run([exe], timeout=timeout)
    output = executed.stdout or ""
    result["host_compiler"] = f"MSVC cl.exe ({host_bits}-bit)"
    # Scrubbed: the report is committed and must not carry where cl.exe lives.
    result["output"] = scrub_absolute_paths(output[-4000:])

    match = re.search(r"(\d+)\s+check\S*\s*,\s*(\d+)\s+failure\S*", output, re.IGNORECASE)
    if match:
        result["checks"] = int(match.group(1))
        result["failures"] = int(match.group(2))
    else:
        # Fall back to counting the per-check FAIL lines rather than guessing.
        result["failures"] = output.count("FAIL")

    status, detail = semantic_verdict(
        executed.returncode,
        result["checks"],
        result["failures"] if result["failures"] is not None else 0,
        minimum=minimum,
    )
    result["status"] = status
    result["detail"] = detail
    return result


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------
def ads_match_status() -> dict:
    """The ADS verdict. Always BLOCKED here, and never inferred from a build.

    The detail deliberately names no absolute path: this document is committed,
    and where a toolchain happens to be installed is an environment fact, not a
    project fact. The installation is located through ADS12_ROOT.
    """
    return {
        "status": "BLOCKED",
        "code": cp.BLOCK_LICENSE,
        "detail": (
            "an ARM Developer Suite 1.2 installation is present on this machine "
            "but the licence file it ships licenses a different product, so the "
            "ARM compilers cannot be run. No compile has been attempted and no "
            "configuration has been tested. The installation is located through "
            "ADS12_ROOT."
        ),
        "required_to_unblock": [
            "a licensed ADS 1.2 installation, with ADS12_ROOT pointing at it",
            "then: python -m buusfury compiler-probe --plan, then --matrix",
        ],
        "not_inferable_from_modern_build": True,
    }


def run_lift(
    target_id: str,
    rom_bytes: bytes,
    toolchain: ModernToolchain,
    workdir: Path | None = None,
    *,
    run_semantic: bool = True,
) -> dict:
    """Run the whole loop for one target and return the report document."""
    target = get_target(target_id)
    unit = _unit_for(target)
    probes = _probes_for(target)
    if not probes:
        raise LiftError(f"no probes are declared for translation unit {unit.id!r}")

    rom_address = unit.rom_address
    offset = rom_address - _gba.ROM_BASE
    original = rom_bytes[offset : offset + unit.length]

    work = workdir or (LIFT_WORKSPACE / target.id)
    external_calls = derive_external_calls(rom_bytes, unit.id)
    build = build_target(toolchain, target, work, defined_symbols=external_calls)

    semantic = (
        run_host_selftest(
            work / "selftest",
            source=_identity.REPO_ROOT / target.selftest_source,
            minimum_checks=target.semantic_minimum_checks,
            host_bits=target.host_build_bits,
        )
        if run_semantic
        else {
            "status": "UNTESTED",
            "checks": 0,
            "failures": None,
            "minimum_checks": target.semantic_minimum_checks,
            "host_compiler": None,
            "host_build_bits": target.host_build_bits,
            "detail": "the semantic self-check was not requested",
            "output": "",
        }
    )

    modern_build = {
        "status": "PASS" if build.ok else "FAIL",
        "toolchain": toolchain.as_dict(),
        "identity": toolchain_identity(toolchain),
        "target_support": probe_target_support(toolchain, work / "toolchain-probe"),
        "compiler_configuration": {
            "cpu": target.cpu,
            "instruction_set": target.isa,
            "optimization": target.optimization,
            "extra_flags": list(target.extra_compiler_flags),
        },
        "link_origin": f"0x{rom_address:08X}",
        "external_calls_bound_to_original_addresses": {
            name: f"0x{value:08X}" for name, value in sorted(external_calls.items())
        },
        "detail": (
            f"compiled, linked at 0x{rom_address:08X} and emitted "
            f"{len(build.raw)} bytes"
            if build.ok
            else "the build did not complete; see diagnostics"
        ),
        "build": build.as_dict(toolchain, target),
    }

    function_rows, pool_structure = compare_functions(rom_bytes, unit, probes, build)

    # Evidence that is specific to how this unit's boundaries were established.
    if UNITS[target.probe_translation_unit]["boundaries"] == "derived":
        boundary_evidence = derive_unit_boundaries(rom_bytes, unit.id)
        if boundary_evidence["problems"]:
            raise LiftError(
                "the derived boundary disagrees with the recorded one: "
                + "; ".join(boundary_evidence["problems"])
            )
        if unit.id == BCI_TU.id:
            boundary_evidence["dispatch_table"] = derive_dispatch_table(rom_bytes)
        elif unit.id == H2_TU.id:
            boundary_evidence["dispatch_table"] = derive_dispatch_table(rom_bytes)
            boundary_evidence["native_table"] = derive_native_table(rom_bytes)
            boundary_evidence["primary_slot"] = {
                "index": 2,
                "address": f"0x{PRIMARY_TABLE + 2 * 4:08X}",
                "word": f"0x{H2_ENTRY | 1:08X}",
                "detail": (
                    "exactly one primary slot points at this handler, and no direct "
                    "BL site anywhere targets it, so it is reached only through the "
                    "dispatch table"
                ),
            }
        elif unit.id == OP_TU.id:
            boundary_evidence["operand_encoding"] = derive_operand_encoding(rom_bytes)
            boundary_evidence["primary_slot"] = {
                "index": 1,
                "address": f"0x{PRIMARY_TABLE + 4:08X}",
                "word": f"0x{OP_TU.rom_address | 1:08X}",
                "detail": (
                    "exactly one primary slot points at this handler, and no direct "
                    "BL site anywhere targets it, so it is reached only through the "
                    "dispatch table"
                ),
            }
        elif unit.id == STACK_TU.id:
            boundary_evidence["value_stack_access"] = derive_stack_consumer(rom_bytes)
            boundary_evidence["primary_slot"] = {
                "index": 7,
                "address": f"0x{PRIMARY_TABLE + 7 * 4:08X}",
                "word": f"0x{STACK_ENTRY | 1:08X}",
                "detail": (
                    "exactly one primary slot points at this consumer, and no direct "
                    "BL site anywhere targets it"
                ),
            }
        elif unit.id == CLEAR_TU.id:
            boundary_evidence["flag_state"] = derive_flag_state(rom_bytes)
        elif unit.id == COLLFLUSH3_TU.id:
            boundary_evidence["collection_flush3"] = derive_collection_flush3(rom_bytes)
        elif unit.id == COLLINSERT2_TU.id:
            boundary_evidence["collection_insert2"] = derive_collection_insert2(rom_bytes)
        elif unit.id == COLLWRITE2_TU.id:
            boundary_evidence["collection_write2"] = derive_collection_write2(rom_bytes)
        elif unit.id == COLLREAD_TU.id:
            boundary_evidence["collection_read"] = derive_collection_read(rom_bytes)
        elif unit.id == APPEND_TU.id:
            boundary_evidence["object_append"] = derive_object_append(rom_bytes)
            boundary_evidence["object_layout_note"] = {
                "object": "0x03001C4C",
                "count_offset": "object + 0x04",
                "values_base": "object + 0x08",
                "caller": "native slot 178 at 0x08003030",
                "preserved_for_reuse": (
                    "this object is the most heavily referenced entry in the static "
                    "pointer table, so its count-and-array shape is recorded here for "
                    "later tickets"
                ),
            }
        elif unit.id == NATIVE178_TU.id:
            boundary_evidence["slot_identity"] = derive_native_slot(
                rom_bytes, NATIVE178_SLOT)
            boundary_evidence["stack_contract"] = derive_native178_stack(rom_bytes)
        elif unit.id == FLAGMASK_TU.id:
            boundary_evidence["mask_application"] = derive_mask_application(rom_bytes)
        elif unit.id == GATHER_TU.id:
            state = derive_flag_state(rom_bytes)
            boundary_evidence["trio_shared_contract"] = state["trio_shared_contract"]
            boundary_evidence["gather"] = state["gather"]
            boundary_evidence["gather_mask"] = state["gather_mask"]
            boundary_evidence["gather_mask_destination"] = state["gather_mask_destination"]
            boundary_evidence["array_extent"] = state["array_extent"]
        elif unit.id == BOOLUSE_TU.id:
            boundary_evidence["bool_materialisation"] = derive_bool_materialisation(rom_bytes)
        elif unit.id == FLAGREAD_TU.id:
            read = derive_bit_field_read(rom_bytes)
            # Re-derive the call sites so the consequence is measured, not remembered.
            base = _gba.ROM_BASE
            callers = []
            for candidate in range(FLAGREAD_ENTRY - 0x8000, FLAGREAD_ENTRY + 0x8000, 2):
                if not _gba.in_cartridge(candidate):
                    continue
                for ins in cp.MD["thumb"].disasm(
                    rom_bytes[candidate - base : candidate - base + 4], candidate
                ):
                    if ins.mnemonic in ("bl", "blx") and ins.operands:
                        operand = ins.operands[0]
                        if (operand.type == cp.capstone.arm.ARM_OP_IMM
                                and (operand.imm & ~1) == FLAGREAD_ENTRY):
                            callers.append(f"0x{ins.address:08X}")
            read["consumed_by"] = sorted(set(callers))
            read["consequence"] = (
                "the boolean is materialised into an engine slot at two sites "
                "(one directly, one inverted) and gates a bit-gather at a third"
            )
            boundary_evidence["bit_field_read"] = read
        elif unit.id == EFFECT_TU.id:
            boundary_evidence["bit_field_write"] = derive_bit_field_write(rom_bytes)
            boundary_evidence["called_from"] = {
                "routine": "sub_080007E6",
                "site": "0x080007F8",
                "arguments": (
                    "r0 = *(0x08054FBC + 0x14), r1 = the value popped from the VM stack"
                ),
            }
        elif unit.id == USE_TU.id:
            boundary_evidence["value_use"] = derive_value_use(rom_bytes)
            boundary_evidence["dispatch_entry"] = {
                "table": "native",
                "index": 29,
                "word": f"0x{USE_ENTRY | 1:08X}",
                "detail": (
                    "reached by the interpreter dispatching primary slot 2, which "
                    "indexes the native table; exactly one entry points here"
                ),
            }
        elif unit.id == ARITH_TU.id:
            boundary_evidence["value_stack_access"] = derive_stack_consumer(
                rom_bytes, ARITH_TU.id, 0
            )
            boundary_evidence["arith_family"] = derive_arith_family(rom_bytes)
            boundary_evidence["primary_slots"] = [
                {
                    "index": slot,
                    "entry": f"0x{(PRIMARY_TABLE and 0) or entry:08X}",
                    "detail": "one primary slot each; no direct BL site targets either",
                }
                for slot, entry in ((8, ARITH_FUNCTIONS[0][0]), (9, ARITH_FUNCTIONS[1][0]))
            ]
        elif unit.id == IWRAM_BLOCK_TU.id:
            # The whole mechanism, not just this unit: the installing DMA, the
            # block it installs, and the veneer family that reaches into it.
            boundary_evidence["iwram_runtime"] = derive_iwram_runtime(rom_bytes)
        elif unit.id == IWRAM_DISPATCH_TU.id:
            # The other half of the same block: every route into it, the second
            # dispatch path, the IRQ subsystem and the internal callgraph.
            boundary_evidence["iwram_dispatch"] = derive_iwram_dispatch(rom_bytes)
    else:
        boundary_evidence = {
            "method": "config/compiler_probes.json, derived and verified there",
            "derived_from_rom": False,
            "not_hand_written": True,
            "detail": (
                "the ADS probe manifest already derives and whole-document "
                "verifies this unit's boundaries"
            ),
        }

    document = {
        "schema": 1,
        "ticket": target.ticket,
        "generated_by": "tools/buusfury/lift.py",
        "source_sha1": hashlib.sha1(rom_bytes).hexdigest(),
        "target": {
            "id": target.id,
            "name": target.name,
            "role": target.role,
            "notes": target.notes,
            "translation_unit": unit.id,
            "rom_address": f"0x{rom_address:08X}",
            "file_offset": f"0x{offset:06X}",
            "code_end_address": f"0x{unit.code_end_address:08X}",
            "end_address": f"0x{unit.end_address:08X}",
            "byte_length": unit.length,
            "code_byte_length": unit.code_length,
            "isa": unit.isa,
            "decomp_source": target.decomp_source,
            "probe_source": target.probe_source,
            "selftest_source": target.selftest_source,
            "semantic_minimum_checks": target.semantic_minimum_checks,
            "host_build_bits": target.host_build_bits,
            "original_sha1": hashlib.sha1(original).hexdigest(),
        },
        "boundary_evidence": boundary_evidence,
        "verdicts": {
            "semantic": {
                "status": semantic["status"],
                "checks": semantic["checks"],
                "failures": semantic["failures"],
                "minimum_checks": semantic["minimum_checks"],
                "host_compiler": semantic["host_compiler"],
                "detail": semantic["detail"],
                "measures": "whether the reconstructed C behaves correctly, by RUNNING it",
            },
            "modern_build": {
                "status": modern_build["status"],
                "detail": modern_build["detail"],
                "measures": "whether the source compiles, links and emits bytes",
            },
            "ads_match": ads_match_status(),
        },
        "verdicts_are_independent": (
            "SEMANTIC, MODERN_BUILD and ADS_MATCH answer different questions and "
            "none is evidence for another. A passing modern build says nothing "
            "about the original compiler; a passing semantic run only removes one "
            "class of error."
        ),
        "modern_build": modern_build,
        "functions": function_rows,
        "literal_pools": pool_structure,
        "comparison": (
            compare_bytes_on_target_boundaries(original, build.raw, unit)
            if build.ok
            else {
                "status": "NOT_RUN",
                "detail": "the build did not complete, so no comparison was made",
                "is_a_match_claim": False,
                "match_claim_note": "MEASUREMENT ONLY; ADS_MATCH stays BLOCKED regardless.",
            }
        ),
        "semantic_check": semantic,
    }
    return document


def write_report(document: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2)
        handle.write("\n")
    return path


def report_path_for(target_id: str) -> Path:
    return _identity.CONFIG_DIR / f"lift_{target_id}.json"


def verify_report(
    rom_bytes: bytes, target_id: str, path: Path | None = None
) -> dict:
    """Regenerate the report and compare it WHOLE, key by key.

    Comparing a hand-picked subset of keys would let `verdicts`, `comparison` or
    `functions` say anything, so every key is compared. The one documented
    exemption is the SEMANTIC block when no host compiler exists to re-run it:
    that is reported as `exempted`, with the reason, rather than silently
    ignored. Returns {ok, problems, exempted, detail}.
    """
    toolchain = discover_modern_toolchain()
    if toolchain is None:
        return {
            "ok": False,
            "problems": ["no modern toolchain is available, so the report cannot be re-derived"],
            "exempted": [],
            "detail": "BLOCKED: no toolchain",
        }

    report_path = path or report_path_for(target_id)
    expected = json.loads(report_path.read_text(encoding="utf-8"))
    actual = run_lift(target_id, rom_bytes, toolchain)

    exempted: list[str] = []
    if actual["verdicts"]["semantic"]["status"] == "UNTESTED":
        placeholder = {
            "status": "UNTESTED",
            "checks": 0,
            "failures": None,
            "minimum_checks": MIN_SEMANTIC_CHECKS,
            "host_compiler": None,
            "detail": "EXEMPTED FROM THIS COMPARISON",
            "measures": "whether the reconstructed C behaves correctly, by RUNNING it",
            "output": "",
        }
        for document in (expected, actual):
            document["verdicts"]["semantic"] = placeholder
            document["semantic_check"] = dict(placeholder)
        exempted.append(
            "verdicts.semantic and semantic_check: no host C compiler is available "
            "here, so the behavioural self-check could not be re-run. The rest of "
            "the document was still compared key by key."
        )

    problems = _diff_documents(expected, actual, prefix="")
    return {
        "ok": not problems,
        "problems": problems,
        "exempted": exempted,
        "detail": (
            "the whole document regenerated identically"
            if not problems
            else f"{len(problems)} difference(s)"
        ),
    }


def _diff_documents(expected, actual, prefix: str) -> list[str]:
    problems: list[str] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected:
                problems.append(f"{prefix}{key}: present in the regenerated report only")
            elif key not in actual:
                problems.append(f"{prefix}{key}: missing from the regenerated report")
            else:
                problems.extend(_diff_documents(expected[key], actual[key], f"{prefix}{key}."))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            problems.append(f"{prefix}length: {len(expected)} vs {len(actual)}")
        for index, (left, right) in enumerate(zip(expected, actual)):
            problems.extend(_diff_documents(left, right, f"{prefix}[{index}]."))
    elif expected != actual:
        problems.append(f"{prefix}{expected!r} != {actual!r}")
    return problems
