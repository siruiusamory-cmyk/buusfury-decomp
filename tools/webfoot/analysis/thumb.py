
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from ..binary import BinaryAddressError, GBA_ROM_BASE, GbaRomAddress


def addr_to_offset(address: int, rom_size: int) -> int:
    """Convert a GBA ROM virtual address to a file offset."""
    return GbaRomAddress(address).to_file_offset(rom_size)


def offset_to_addr(offset: int, rom_size: int) -> int:
    """Convert a file offset to its GBA ROM virtual address."""
    if type(offset) is not int or type(rom_size) is not int:
        raise BinaryAddressError("offset and rom_size must be integers")
    if not 0 <= offset <= rom_size:
        raise BinaryAddressError(
            f"file offset 0x{offset:X} is outside a {rom_size}-byte ROM"
        )
    return GBA_ROM_BASE + offset


class RomReader:

    def __init__(self, data: bytes) -> None:
        self.data = data

    @property
    def rom_size(self) -> int:
        return len(self.data)

    def _offset(self, address: int, size: int) -> int:
        offset = addr_to_offset(address, len(self.data))
        if offset + size > len(self.data):
            raise BinaryAddressError(
                f"read of {size} bytes at 0x{address:08X} exceeds ROM"
            )
        return offset

    def read_bytes(self, address: int, count: int) -> bytes:
        if type(count) is not int or count < 0:
            raise BinaryAddressError("count must be a non-negative integer")
        offset = self._offset(address, count)
        return self.data[offset : offset + count]

    def u16(self, address: int) -> int:
        offset = self._offset(address, 2)
        if offset % 2 != 0:
            raise BinaryAddressError(f"unaligned halfword read at 0x{address:08X}")
        return int.from_bytes(self.data[offset : offset + 2], "little")

    def u32(self, address: int) -> int:
        offset = self._offset(address, 4)
        if offset % 4 != 0:
            raise BinaryAddressError(f"unaligned word read at 0x{address:08X}")
        return int.from_bytes(self.data[offset : offset + 4], "little")


def _sign_extend(value: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return value - (1 << bits) if value & sign_bit else value


@dataclass(frozen=True, slots=True)
class BlInstruction:

    site_address: int
    halfword1: int
    halfword2: int
    target: int


def decode_bl(halfword1: int, halfword2: int, site_address: int) -> BlInstruction | None:
    if type(halfword1) is not int or type(halfword2) is not int:
        raise BinaryAddressError("halfwords must be integers")
    if not 0 <= halfword1 <= 0xFFFF or not 0 <= halfword2 <= 0xFFFF:
        raise BinaryAddressError("halfwords must be 16-bit values")
    if type(site_address) is not int or site_address % 2 != 0:
        raise BinaryAddressError("site_address must be an even integer")

    h1_is_bl_prefix = (halfword1 & 0xF800) == 0xF000
    h2_is_bl_suffix = (halfword2 & 0xF800) == 0xF800
    if not (h1_is_bl_prefix and h2_is_bl_suffix):
        return None

    s = (halfword1 >> 10) & 0x1
    imm10 = halfword1 & 0x3FF
    j1 = (halfword2 >> 13) & 0x1
    j2 = (halfword2 >> 11) & 0x1
    imm11 = halfword2 & 0x7FF
    i1 = (~(j1 ^ s)) & 0x1
    i2 = (~(j2 ^ s)) & 0x1
    imm23 = (s << 22) | (i1 << 21) | (i2 << 20) | (imm10 << 11) | imm11
    offset = _sign_extend(imm23, 23) << 1
    target = (site_address + 4 + offset) & 0xFFFFFFFF
    return BlInstruction(
        site_address=site_address,
        halfword1=halfword1,
        halfword2=halfword2,
        target=target,
    )


def encode_bl(site_address: int, target: int) -> tuple[int, int]:
    """Encode a BL pair for test fixtures; inverse of :func:`decode_bl`."""
    if site_address % 2 != 0 or target % 2 != 0:
        raise BinaryAddressError("BL addresses must be even")
    offset = target - (site_address + 4)
    if not -(1 << 22) <= offset < (1 << 22):
        raise BinaryAddressError("BL displacement out of range")
    imm23 = (offset >> 1) & 0x7FFFFF
    s = (imm23 >> 22) & 0x1
    imm10 = (imm23 >> 11) & 0x3FF
    imm11 = imm23 & 0x7FF
    i1 = (imm23 >> 21) & 0x1
    i2 = (imm23 >> 20) & 0x1
    j1 = ((~i1) ^ s) & 0x1
    j2 = ((~i2) ^ s) & 0x1
    halfword1 = 0xF000 | (s << 10) | imm10
    halfword2 = 0xF800 | (j1 << 13) | (j2 << 11) | imm11
    decoded = decode_bl(halfword1, halfword2, site_address)
    if decoded is None or decoded.target != target:
        raise BinaryAddressError("encode_bl self-check failed")
    return halfword1, halfword2


# Every bit test here is parenthesized because ``h & 0xF800 == 0xF000`` parses as ``h & (0xF800 == 0xF000)`` in Python.
def is_push_with_lr(halfword: int) -> bool:
    """True for ``push {..., lr}`` (0xB5xx), the common Thumb prologue."""
    return (halfword & 0xFF00) == 0xB500


def is_pop_with_pc(halfword: int) -> bool:
    """True for ``pop {..., pc}`` (0xBDxx), the common Thumb epilogue tail."""
    return (halfword & 0xFF00) == 0xBD00


def is_b_short(halfword: int) -> bool:
    """True for unconditional in-page ``b`` (0xE000-0xE7FF)."""
    return (halfword & 0xF800) == 0xE000


def b_short_target(halfword: int, site_address: int) -> int:
    offset = _sign_extend(halfword & 0x7FF, 11) << 1
    return (site_address + 4 + offset) & 0xFFFFFFFF


def ldr_literal_address(halfword: int, instruction_address: int) -> int | None:
    if (halfword & 0xF800) != 0x4800:
        return None
    imm8 = halfword & 0xFF
    base = (instruction_address + 4) & ~0x3
    return base + imm8 * 4


def scan_bl(data: bytes, start_offset: int, end_offset: int) -> Iterator[BlInstruction]:
    """Yield every BL pair whose first halfword starts within [start,end)."""
    reader = RomReader(data)
    if start_offset % 2 != 0 or end_offset % 2 != 0:
        raise BinaryAddressError("scan bounds must be even offsets")
    if start_offset < 0 or end_offset > len(data):
        raise BinaryAddressError("scan bounds exceed ROM")
    for offset in range(start_offset, end_offset, 2):
        h1 = reader.u16(offset_to_addr(offset, len(data)))
        if not ((h1 & 0xF800) == 0xF000):
            continue
        if offset + 2 >= len(data):
            break
        h2 = reader.u16(offset_to_addr(offset + 2, len(data)))
        decoded = decode_bl(h1, h2, offset_to_addr(offset, len(data)))
        if decoded is not None:
            yield decoded


def scan_push_prologues(
    data: bytes, start_offset: int, end_offset: int
) -> Iterator[int]:
    """Yield GBA addresses of ``push {..., lr}`` halfwords in [start,end)."""
    reader = RomReader(data)
    if start_offset % 2 != 0 or end_offset % 2 != 0:
        raise BinaryAddressError("scan bounds must be even offsets")
    if start_offset < 0 or end_offset > len(data):
        raise BinaryAddressError("scan bounds exceed ROM")
    for offset in range(start_offset, end_offset, 2):
        h = reader.u16(offset_to_addr(offset, len(data)))
        if is_push_with_lr(h):
            yield offset_to_addr(offset, len(data))


def find_aligned_words(data: bytes, value: int, start_offset: int, end_offset: int) -> list[int]:
    """Return file offsets (4-byte aligned) whose little-endian word equals value."""
    if start_offset % 4 != 0 or end_offset % 4 != 0:
        raise BinaryAddressError("word scan bounds must be 4-aligned")
    if not 0 <= value <= 0xFFFFFFFF:
        raise BinaryAddressError("value must be a 32-bit word")
    pattern = value.to_bytes(4, "little")
    results: list[int] = []
    cursor = start_offset
    while True:
        index = data.find(pattern, cursor, end_offset)
        if index < 0:
            break
        if index % 4 == 0:
            results.append(index)
        cursor = index + 1
    return results
