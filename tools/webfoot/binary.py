
from __future__ import annotations

from dataclasses import dataclass


GBA_ROM_BASE = 0x08000000
UINT32_MAX = 0xFFFFFFFF


@dataclass(frozen=True, slots=True, order=True)
class FileOffset:
    """A file position, never implicitly interchangeable with a GBA address."""

    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value < 0:
            raise BinaryAddressError("file offset must be a non-negative integer")

    def to_gba_address(self, rom_size: int) -> GbaRomAddress:
        address = GbaRomAddress(GBA_ROM_BASE + self.value)
        address.to_file_offset(rom_size)
        return address


class BinaryAddressError(ValueError):
    """Raised when an address cannot safely identify bytes in a ROM."""


@dataclass(frozen=True, slots=True)
class GbaRomAddress:
    """A raw 32-bit GBA address that can be checked against one ROM size."""

    raw: int

    def __post_init__(self) -> None:
        if type(self.raw) is not int or not 0 <= self.raw <= UINT32_MAX:
            raise BinaryAddressError("GBA address must be a 32-bit unsigned integer")

    @property
    def is_null(self) -> bool:
        return self.raw == 0

    def to_file_offset(self, rom_size: int, *, allow_end: bool = False) -> int:
        if type(rom_size) is not int or rom_size < 0:
            raise BinaryAddressError("ROM size must be a non-negative integer")
        if self.raw < GBA_ROM_BASE:
            raise BinaryAddressError(
                f"0x{self.raw:08X} is not an address in the GBA ROM window"
            )
        offset = self.raw - GBA_ROM_BASE
        if offset > rom_size or (offset == rom_size and not allow_end):
            raise BinaryAddressError(
                f"GBA address 0x{self.raw:08X} is outside a {rom_size}-byte ROM"
            )
        return offset
