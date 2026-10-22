from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import namedtuple

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recomp"))
sys.path.insert(0, os.path.join(ROOT, "tools", "research"))

import export_inputs
import name_evidence
import romfile

ROM_BASE = 0x08000000
ROM_SHA256 = name_evidence.ROM_SHA256
RETURN = 0xFFFFFFFE
MASK = 0xFFFFFFFF
STARTS = ("start", "unreferenced")
BUDGET = 256
STACK = 0x03007F00
EWRAM = (0x02000000, 0x40000)
IWRAM = (0x03000000, 0x8000)
BOUNDS = os.path.join("docs", "research", "FUNCTION_BOUNDS.csv")
ARM = capstone.arm
ENGINE = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
ENGINE.detail = True
NAMES = {"r%d" % index: index for index in range(13)}
NAMES.update({"sp": 13, "lr": 14, "pc": 15})
WIDTHS = {ARM.ARM_INS_LDR: 4, ARM.ARM_INS_STR: 4, ARM.ARM_INS_LDRB: 1,
          ARM.ARM_INS_STRB: 1, ARM.ARM_INS_LDRH: 2, ARM.ARM_INS_STRH: 2,
          ARM.ARM_INS_LDRSB: 1, ARM.ARM_INS_LDRSH: 2}

Result = namedtuple("Result", "registers writes calls steps")


def code_rows(root=ROOT):
    return export_inputs.code_rows(root)


def census(root=ROOT):
    path = os.path.join(root, *BOUNDS.split("/"))
    with open(path, newline="", encoding="utf-8") as handle:
        return {int(row["address"], 16): row["kind"] for row in csv.DictReader(handle)}


def body(image, start, root=ROOT):
    row = next((row for row in code_rows(root)
                if ROM_BASE + row[0] <= start < ROM_BASE + row[0] + row[1]), None)
    if row is None:
        raise ValueError("0x%08X is not inside a transcribed code row" % start)
    low, high = ROM_BASE + row[0], ROM_BASE + row[0] + row[1]
    allowed, pending = set(), [start]
    while pending:
        at = pending.pop()
        while low <= at < high and at not in allowed:
            found = name_evidence.decode_one(image, at, "thumb")
            if found is None:
                break
            allowed.add(at)
            if found.mnemonic == "bl":
                at += found.size
                continue
            if found.mnemonic == "bx" or (found.mnemonic.startswith(("pop", "ldm"))
                                          and "pc" in found.op_str):
                break
            if found.mnemonic.startswith("b"):
                target = found.op_str.split(",")[0].strip()
                if target.startswith("#"):
                    pending.append(int(target[1:], 0))
                if found.mnemonic == "b":
                    break
                at += found.size
                continue
            at += found.size
    return allowed


class Memory:
    def __init__(self, image, areas, writes):
        self.image = image
        self.areas = areas
        self.writes = writes

    def area(self, address, width):
        for start, data in self.areas:
            if start <= address and address + width <= start + len(data):
                return data, address - start
        raise ValueError("0x%08X (+%d) is outside the writable footprints the harness maps"
                         % (address, width))

    def seed(self, address, data):
        area, offset = self.area(address, len(data))
        area[offset:offset + len(data)] = data

    def read(self, address, width):
        if ROM_BASE <= address and address + width <= ROM_BASE + len(self.image):
            offset = address - ROM_BASE
            return int.from_bytes(self.image[offset:offset + width], "little")
        area, offset = self.area(address, width)
        return int.from_bytes(area[offset:offset + width], "little")

    def write(self, address, width, value):
        area, offset = self.area(address, width)
        value &= (1 << (8 * width)) - 1
        area[offset:offset + width] = value.to_bytes(width, "little")
        self.writes.append((address, width, value))


class Machine:
    def __init__(self, image, start, allowed, registers=None, memory=None, budget=BUDGET):
        self.image = image
        self.start = start
        self.allowed = set(allowed)
        self.budget = budget
        self.n = self.z = self.c = self.v = 0
        self.steps = 0
        self.calls = []
        self.writes = []
        areas = [(address, bytearray(size)) for address, size in (EWRAM, IWRAM)]
        self.memory = Memory(image, areas, self.writes)
        self.registers = [0] * 16
        self.registers[13] = STACK
        self.registers[14] = RETURN
        self.registers[15] = start
        for index, value in (registers or {}).items():
            self.registers[index] = value & MASK
        for address, data in (memory or {}).items():
            self.memory.seed(address, data)

    def run(self):
        while self.registers[15] != RETURN:
            at = self.registers[15]
            if at not in self.allowed:
                raise ValueError("the run left the body at 0x%08X (start 0x%08X)" % (at, self.start))
            if self.steps >= self.budget:
                raise ValueError("the run passed the %d step budget at 0x%08X"
                                 % (self.budget, at))
            found = self.decode(at)
            self.steps += 1
            self.registers[15] = self.execute(found)
        return Result(tuple(self.registers), list(self.writes), list(self.calls), self.steps)

    def decode(self, at):
        offset = at - ROM_BASE
        if at % 2 or not 0 <= offset < len(self.image):
            raise ValueError("0x%08X is not a Thumb address inside the image" % at)
        found = next(iter(ENGINE.disasm(bytes(self.image[offset:offset + 4]), at, count=1)), None)
        if found is None:
            raise ValueError("0x%08X does not decode as a Thumb instruction" % at)
        return found

    def index(self, insn, register):
        return NAMES[insn.reg_name(register)]

    def register(self, insn, register):
        index = self.index(insn, register)
        if index == 15:
            return (insn.address + 4) & ~3
        return self.registers[index]

    def operand(self, insn, operand):
        if operand.type == ARM.ARM_OP_IMM:
            return operand.imm & MASK
        if operand.type == ARM.ARM_OP_REG:
            return self.register(insn, operand.reg)
        raise ValueError("%s at 0x%08X has an operand the harness does not run"
                         % (insn.mnemonic, insn.address))

    def address(self, insn, operand):
        value = self.register(insn, operand.mem.base) + operand.mem.disp
        if operand.mem.index:
            value += self.registers[self.index(insn, operand.mem.index)]
        return value & MASK

    def add_flags(self, first, second, carry=0):
        total = first + second + carry
        result = total & MASK
        self.n = result >> 31
        self.z = int(result == 0)
        self.c = int(total > MASK)
        self.v = ((first ^ result) & (second ^ result)) >> 31
        return result

    def sub_flags(self, first, second, borrow=0):
        total = first - second - borrow
        result = total & MASK
        self.n = result >> 31
        self.z = int(result == 0)
        self.c = int(total >= 0)
        self.v = ((first ^ second) & (first ^ result)) >> 31
        return result

    def logic(self, result):
        self.n = result >> 31
        self.z = int(result == 0)
        return result

    def shift(self, kind, value, amount):
        if kind == "lsl":
            if amount == 0:
                return value, self.c
            if amount < 32:
                return (value << amount) & MASK, (value >> (32 - amount)) & 1
            return 0, (value & 1) if amount == 32 else 0
        if kind == "lsr":
            if amount == 0:
                return value, self.c
            if amount < 32:
                return value >> amount, (value >> (amount - 1)) & 1
            return 0, (value >> 31) & 1
        if kind == "asr":
            sign = value >> 31
            if amount == 0:
                return value, self.c
            if amount < 32:
                return (((value >> amount) | (sign << (32 - amount))) & MASK,
                        (value >> (amount - 1)) & 1)
            return (MASK if sign else 0), sign
        amount &= 0x1F
        if amount == 0:
            return value, (value >> 31) & 1
        return (((value >> amount) | (value << (32 - amount))) & MASK,
                (value >> (amount - 1)) & 1)

    def taken(self, insn):
        n, z, c, v = self.n, self.z, self.c, self.v
        return {ARM.ARM_CC_AL: True, ARM.ARM_CC_INVALID: True, ARM.ARM_CC_EQ: bool(z),
                ARM.ARM_CC_NE: not z, ARM.ARM_CC_HS: bool(c),
                ARM.ARM_CC_LO: not c, ARM.ARM_CC_MI: bool(n),
                ARM.ARM_CC_PL: not n, ARM.ARM_CC_VS: bool(v), ARM.ARM_CC_VC: not v,
                ARM.ARM_CC_HI: bool(c) and not z, ARM.ARM_CC_LS: not c or bool(z),
                ARM.ARM_CC_GE: n == v, ARM.ARM_CC_LT: n != v,
                ARM.ARM_CC_GT: not z and n == v, ARM.ARM_CC_LE: bool(z) or n != v}.get(
                    insn.cc, True)

    def set(self, insn, operand, value):
        index = self.index(insn, operand.reg)
        self.registers[index] = value & MASK
        return index

    def execute(self, insn):
        next_pc = insn.address + insn.size
        operands = insn.operands
        arm = ARM
        if insn.id == arm.ARM_INS_ADD:
            second = self.operand(insn, operands[-1])
            first = self.operand(insn, operands[-2])
            result = self.add_flags(first, second) if insn.update_flags \
                else (first + second) & MASK
            if self.set(insn, operands[0], result) == 15:
                next_pc = result & ~1
        elif insn.id == arm.ARM_INS_SUB:
            second = self.operand(insn, operands[-1])
            first = self.operand(insn, operands[-2])
            result = self.sub_flags(first, second) if insn.update_flags \
                else (first - second) & MASK
            if self.set(insn, operands[0], result) == 15:
                next_pc = result & ~1
        elif insn.id == arm.ARM_INS_RSB:
            first = self.operand(insn, operands[-2])
            second = self.operand(insn, operands[-1])
            result = self.sub_flags(second, first) if insn.update_flags \
                else (second - first) & MASK
            if self.set(insn, operands[0], result) == 15:
                next_pc = result & ~1
        elif insn.id in (arm.ARM_INS_CMP, arm.ARM_INS_CMN, arm.ARM_INS_TST):
            first = self.operand(insn, operands[0])
            second = self.operand(insn, operands[-1])
            if insn.id == arm.ARM_INS_CMP:
                self.sub_flags(first, second)
            elif insn.id == arm.ARM_INS_CMN:
                self.add_flags(first, second)
            else:
                self.logic(first & second)
        elif insn.id == arm.ARM_INS_MOV:
            value = self.operand(insn, operands[-1])
            if insn.update_flags:
                self.logic(value)
            if self.set(insn, operands[0], value) == 15:
                next_pc = value & ~1
        elif insn.id in (arm.ARM_INS_MVN, arm.ARM_INS_AND, arm.ARM_INS_EOR,
                         arm.ARM_INS_ORR, arm.ARM_INS_BIC, arm.ARM_INS_ADC,
                         arm.ARM_INS_SBC):
            first = self.operand(insn, operands[-2])
            second = self.operand(insn, operands[-1])
            if insn.id == arm.ARM_INS_MVN:
                result = ~second & MASK
            elif insn.id == arm.ARM_INS_AND:
                result = first & second
            elif insn.id == arm.ARM_INS_EOR:
                result = first ^ second
            elif insn.id == arm.ARM_INS_ORR:
                result = first | second
            elif insn.id == arm.ARM_INS_BIC:
                result = first & ~second & MASK
            elif insn.id == arm.ARM_INS_ADC:
                result = self.add_flags(first, second, self.c)
            else:
                result = self.sub_flags(first, second, 1 - self.c)
            if insn.update_flags and insn.id not in (arm.ARM_INS_ADC, arm.ARM_INS_SBC):
                result = self.logic(result)
            if self.set(insn, operands[0], result) == 15:
                next_pc = result & ~1
        elif insn.id == arm.ARM_INS_MUL:
            result = (self.operand(insn, operands[0]) * self.operand(insn, operands[1])) & MASK
            if insn.update_flags:
                self.logic(result)
            self.set(insn, operands[0], result)
        elif insn.id in (arm.ARM_INS_LSL, arm.ARM_INS_LSR, arm.ARM_INS_ASR, arm.ARM_INS_ROR):
            kind = {arm.ARM_INS_LSL: "lsl", arm.ARM_INS_LSR: "lsr",
                    arm.ARM_INS_ASR: "asr", arm.ARM_INS_ROR: "ror"}[insn.id]
            immediate = len(operands) == 3
            if immediate:
                value = self.operand(insn, operands[1])
                amount = self.operand(insn, operands[2])
                if kind in ("lsr", "asr") and amount == 0:
                    amount = 32
            else:
                value = self.operand(insn, operands[0])
                amount = self.operand(insn, operands[1]) & 0xFF
            result, carry = self.shift(kind, value, amount)
            if insn.update_flags:
                self.logic(result)
                self.c = carry
            if self.set(insn, operands[0], result) == 15:
                next_pc = result & ~1
        elif insn.id in (arm.ARM_INS_LDR, arm.ARM_INS_LDRB, arm.ARM_INS_LDRH,
                         arm.ARM_INS_LDRSB, arm.ARM_INS_LDRSH, arm.ARM_INS_STR,
                         arm.ARM_INS_STRB, arm.ARM_INS_STRH):
            address = self.address(insn, operands[1])
            width = WIDTHS[insn.id]
            if insn.id in (arm.ARM_INS_STR, arm.ARM_INS_STRB, arm.ARM_INS_STRH):
                self.memory.write(address, width, self.operand(insn, operands[0]))
                if insn.writeback:
                    self.registers[self.index(insn, operands[1].mem.base)] = address
            else:
                value = self.memory.read(address, width)
                if insn.id == arm.ARM_INS_LDRSB and value & 0x80:
                    value |= MASK ^ 0xFF
                if insn.id == arm.ARM_INS_LDRSH and value & 0x8000:
                    value |= MASK ^ 0xFFFF
                if self.set(insn, operands[0], value) == 15:
                    next_pc = value & ~1
        elif insn.id in (arm.ARM_INS_LDM, arm.ARM_INS_STM):
            base = self.index(insn, operands[0].reg)
            registers = [self.index(insn, operand.reg) for operand in operands[1:]]
            address = self.registers[base]
            for offset, index in enumerate(registers):
                if insn.id == arm.ARM_INS_STM:
                    self.memory.write(address + 4 * offset, 4, self.registers[index])
            loaded = {}
            if insn.id == arm.ARM_INS_LDM:
                for offset, index in enumerate(registers):
                    loaded[index] = self.memory.read(address + 4 * offset, 4)
                for index, value in loaded.items():
                    self.registers[index] = value
            if insn.writeback:
                self.registers[base] = (address + 4 * len(registers)) & MASK
            if insn.id == arm.ARM_INS_LDM and 15 in registers:
                next_pc = loaded[15] & ~1
        elif insn.id == arm.ARM_INS_PUSH:
            address = self.registers[13] - 4 * len(operands)
            for offset, operand in enumerate(operands):
                index = self.index(insn, operand.reg)
                self.memory.write(address + 4 * offset, 4, self.registers[index])
            self.registers[13] = address & MASK
        elif insn.id == arm.ARM_INS_POP:
            address = self.registers[13]
            loaded = {}
            for offset, operand in enumerate(operands):
                index = self.index(insn, operand.reg)
                loaded[index] = self.memory.read(address + 4 * offset, 4)
            for index, value in loaded.items():
                self.registers[index] = value
            self.registers[13] = (address + 4 * len(operands)) & MASK
            if 15 in loaded:
                next_pc = loaded[15] & ~1
        elif insn.id == arm.ARM_INS_B:
            if self.taken(insn):
                next_pc = self.operand(insn, operands[0]) & ~1
        elif insn.id == arm.ARM_INS_BL:
            self.calls.append((insn.address, self.operand(insn, operands[0]) & ~1))
        elif insn.id == arm.ARM_INS_BX:
            next_pc = self.operand(insn, operands[0]) & ~1
        else:
            raise ValueError("%s at 0x%08X is not an instruction the harness runs"
                             % (insn.mnemonic, insn.address))
        return next_pc & MASK


def run(image, start, allowed, registers=None, memory=None, budget=BUDGET):
    return Machine(image, start, allowed, registers, memory, budget).run()


def parse_register(text):
    name, value = text.split("=", 1)
    return NAMES[name], int(value, 0)


def parse_seed(text):
    address, data = text.split("=", 1)
    return int(address, 0), bytes.fromhex(data)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run one transcribed Thumb function from a private image copy.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--function", type=lambda text: int(text, 0), required=True)
    parser.add_argument("--register", action="append", default=[], type=parse_register)
    parser.add_argument("--seed", action="append", default=[], type=parse_seed)
    parser.add_argument("--budget", type=int, default=BUDGET)
    arguments = parser.parse_args(argv)
    image = romfile.read_rom(arguments.rom, ROM_SHA256)
    allowed = body(image, arguments.function)
    result = run(image, arguments.function, allowed, dict(arguments.register),
                 dict(arguments.seed), arguments.budget)
    print("function=0x%08X body=%d steps=%d" % (arguments.function, len(allowed), result.steps))
    for index in range(13):
        print("  r%-2d 0x%08X" % (index, result.registers[index]))
    for address, width, value in result.writes:
        print("  write 0x%08X width=%d value=0x%X" % (address, width, value))
    for site, target in result.calls:
        print("  call 0x%08X -> 0x%08X" % (site, target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
