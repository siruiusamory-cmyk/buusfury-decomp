"""Recursive Thumb traversal, shared by the code producers.

Ported from scratchpad/trace.py:116-232 (session afdddff1-...-7a33efc68a28). The
wave-4 script carried a second, byte-identical copy of the same `walk` body and
worklist (scratchpad/wave4.py:119-228); it is deduplicated here rather than
ported twice, which is the only structural change. Decoders come from
`tools.webfoot.analysis.thumb` and nowhere else: no linear sweep, no ARM.

Every threshold is the historical one: depth cap 10, per-function scan cap
0x1000, jump-table bar of >= 8 consecutive aligned odd in-ROM words.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from ..analysis.thumb import (RomReader, addr_to_offset, b_short_target, decode_bl,
                              is_b_short, is_pop_with_pc, is_push_with_lr,
                              ldr_literal_address, offset_to_addr)
from ..binary import GBA_ROM_BASE as BASE

#: The address window the walk runs in, from `binary`'s single owner.
MAX_DEPTH = 10
#: Halt a runaway walk; the function is then recorded as having no end evidence.
MAX_FUNC_SCAN = 0x1000
#: A jump table is a run of at least this many aligned odd in-ROM (Thumb) words.
JUMP_TABLE_MIN_ENTRIES = 8


@dataclass
class Traversal:
    """One traversal state: seeds in, functions / reached bytes / pools out."""

    data: bytes
    size: int = field(init=False)
    reader: RomReader = field(init=False)
    functions: dict[int, dict] = field(default_factory=dict)
    callers: dict[int, set[int]] = field(default_factory=dict)
    callees: dict[int, set[int]] = field(default_factory=dict)
    literal_words: dict[int, int] = field(default_factory=dict)
    reached_bytes: set[int] = field(default_factory=set)
    all_pools: set[int] = field(default_factory=set)
    queue: deque = field(default_factory=deque)

    def __post_init__(self) -> None:
        self.size = len(self.data)
        self.reader = RomReader(self.data)

    # -- address helpers ---------------------------------------------------
    @property
    def code_hi(self) -> int:
        return BASE + self.size

    def in_rom(self, address: int) -> bool:
        return BASE <= address < self.code_hi

    def u16(self, address: int) -> int:
        return self.reader.u16(address)

    def u32(self, address: int) -> int:
        return self.reader.u32(address)

    def prologue_text(self, address: int) -> str:
        try:
            halfword = self.u16(address)
        except Exception:
            return ""
        if is_push_with_lr(halfword):
            registers = [f"r{i}" for i in range(8) if halfword & (1 << i)]
            return "push {" + ",".join(registers + ["lr"]) + "}"
        return f"halfword 0x{halfword:04X}"

    # -- the walk ----------------------------------------------------------
    def walk(self, fetch: int, record: bool = True):
        """Linear-in-function decode from `fetch`.

        `record` is False for the positive-control BFS, which re-walks functions
        only to read their edges and must not add to the reached-byte record.
        """
        calls: set[int] = set()
        ptr_seeds: list[tuple[int, int]] = []
        pools: set[int] = set()
        visited: set[int] = set()
        work = deque([fetch])
        end_addr = None
        end_reason = None
        lo = hi = fetch
        while work:
            pc = work.popleft()
            while True:
                if pc in visited:
                    break
                if not self.in_rom(pc) or pc + 1 >= self.code_hi:
                    break
                if pc - fetch > MAX_FUNC_SCAN or pc < fetch:
                    break
                visited.add(pc)
                lo = min(lo, pc)
                hi = max(hi, pc + 2)
                try:
                    halfword = self.u16(pc)
                except Exception:
                    break
                # BL pair
                if (halfword & 0xF800) == 0xF000 and self.in_rom(pc + 2):
                    try:
                        second = self.u16(pc + 2)
                    except Exception:
                        second = 0
                    branch = decode_bl(halfword, second, pc)
                    if branch is not None:
                        if self.in_rom(branch.target):
                            calls.add(branch.target)
                        visited.add(pc + 2)
                        hi = max(hi, pc + 4)
                        pc += 4
                        continue
                # ldr rX,[pc,#imm] -> literal word (DATA, never executable)
                literal = ldr_literal_address(halfword, pc)
                if literal is not None and self.in_rom(literal) and literal + 4 <= self.code_hi:
                    pools.add(literal)
                    try:
                        value = self.u32(literal)
                    except Exception:
                        value = 0
                    self.literal_words[literal] = value
                    if self.in_rom(value) and (value & 1):
                        ptr_seeds.append((value, literal))
                    pc += 2
                    continue
                # pop {..., pc} -> function end
                if is_pop_with_pc(halfword):
                    if end_addr is None or pc + 2 > end_addr:
                        end_addr = pc + 2
                        end_reason = "pop_with_pc"
                    break
                # bx lr -> function end
                if halfword == 0x4770:
                    if end_addr is None or pc + 2 > end_addr:
                        end_addr = pc + 2
                        end_reason = "bx_lr"
                    break
                # unconditional short b
                if is_b_short(halfword):
                    target = b_short_target(halfword, pc)
                    if self.in_rom(target) and fetch <= target <= fetch + MAX_FUNC_SCAN:
                        work.append(target)
                    break
                # conditional branch 0xD0..0xDD (not swi 0xDF / undef 0xDE)
                if (halfword & 0xF000) == 0xD000 and (halfword >> 8) & 0xF < 0xE:
                    offset = halfword & 0xFF
                    if offset & 0x80:
                        offset -= 0x100
                    target = (pc + 4 + offset * 2) & 0xFFFFFFFF
                    if self.in_rom(target) and fetch <= target <= fetch + MAX_FUNC_SCAN:
                        work.append(target)
                    pc += 2
                    continue
                pc += 2
        if record:
            for address in visited:
                try:
                    self.reached_bytes.add(addr_to_offset(address, self.size))
                    self.reached_bytes.add(addr_to_offset(address + 1, self.size))
                except Exception:
                    pass
        return end_addr, end_reason, calls, ptr_seeds, pools, (lo, hi)

    # -- worklist ----------------------------------------------------------
    def seed(self, fetch: int, depth: int, raw_hex: str, via: str) -> None:
        self.queue.append((fetch, depth, raw_hex, via))

    def drain(self) -> None:
        while self.queue:
            fetch, depth, raw_hex, via = self.queue.popleft()
            if fetch in self.functions:
                continue
            end, end_reason, calls, ptrs, pools, span = self.walk(fetch)
            self.all_pools |= pools
            self.functions[fetch] = {
                "fetch": fetch, "raw_hex": raw_hex, "depth": depth, "via": via,
                "end": end, "end_reason": end_reason, "span": span,
                "prologue": self.prologue_text(fetch),
            }
            self.callees.setdefault(fetch, set()).update(calls)
            for target in calls:
                self.callers.setdefault(target, set()).add(fetch)
                if depth + 1 <= MAX_DEPTH and target not in self.functions:
                    self.seed(target, depth + 1, f"0x{target:08X}", f"bl_from:0x{fetch:08X}")
            for raw, literal in ptrs:
                target = raw & ~1
                self.callers.setdefault(target, set()).add(fetch)
                if depth + 1 <= MAX_DEPTH and target not in self.functions:
                    self.seed(target, depth + 1, f"0x{raw:08X}",
                              f"literal_pool:0x{literal:08X}")

    # -- derived records ---------------------------------------------------
    def pool_offsets(self) -> set[int]:
        offsets: set[int] = set()
        for literal in self.all_pools:
            start = addr_to_offset(literal, self.size)
            offsets.update(range(start, start + 4))
        return offsets

    def jump_tables(self, scan_lo: int, scan_hi: int) -> list[dict]:
        """Runs of >= 8 aligned words that are all odd in-ROM addresses.

        Derived from ROM bytes alone — never copied from a prior artifact.
        """
        def is_thumb_ptr(offset: int) -> bool:
            if offset + 4 > self.size:
                return False
            word = int.from_bytes(self.data[offset:offset + 4], "little")
            return bool(word & 1) and BASE <= (word & ~1) < self.code_hi

        tables: list[dict] = []
        offset = scan_lo - (scan_lo % 4)
        while offset < scan_hi:
            if is_thumb_ptr(offset):
                start = offset
                while offset < scan_hi and is_thumb_ptr(offset):
                    offset += 4
                entries = (offset - start) // 4
                if entries >= JUMP_TABLE_MIN_ENTRIES:
                    tables.append({
                        "file_offset": start, "size": offset - start,
                        "gba_address": f"0x{offset_to_addr(start, self.size):08X}",
                        "entries": entries,
                    })
            else:
                offset += 4
        return tables


def spans_from(offsets: set[int]) -> list[tuple[int, int]]:
    """Maximal contiguous runs over a set of file offsets."""
    out: list[tuple[int, int]] = []
    for offset in sorted(offsets):
        if out and out[-1][1] == offset:
            out[-1] = (out[-1][0], offset + 1)
        else:
            out.append((offset, offset + 1))
    return out
