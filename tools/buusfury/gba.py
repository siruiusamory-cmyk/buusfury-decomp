"""Game Boy Advance address model and cartridge header codec.

The single rule this module exists to enforce: a file offset and a ROM address
are different things. Every location in this project is expressible as both, and
converting between them is done here and nowhere else, so that a raw 0x08...
value can never be silently treated as a file position.

Address spaces follow the GBA memory map. The distinction matters for the pointer
census in analysis.py: a 32-bit value that lands in ROM, EWRAM, IWRAM, VRAM,
palette RAM, OAM or MMIO is a different kind of evidence in each case, and MMIO
in particular is almost never a pointer.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

#: Game Pak ROM is mapped at 0x08000000 and is 32 MiB addressable. This
#: cartridge occupies the first 8 MiB of it.
ROM_BASE = 0x08000000
ROM_SIZE = 0x00800000
ROM_END = ROM_BASE + ROM_SIZE

#: Data directory holding the mandated boot logo (see data/README.md).
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BOOT_LOGO_PATH = DATA_DIR / "gba_boot_logo.bin"

# ---------------------------------------------------------------------------
# GBA memory map
# ---------------------------------------------------------------------------
#: (name, first address, last address inclusive, addressable width)
ADDRESS_SPACES: tuple[tuple[str, int, int, int], ...] = (
    ("bios", 0x00000000, 0x00003FFF, 4),
    ("ewram", 0x02000000, 0x0203FFFF, 4),
    ("iwram", 0x03000000, 0x03007FFF, 4),
    ("io", 0x04000000, 0x040003FE, 2),
    ("palette", 0x05000000, 0x050003FF, 2),
    ("vram", 0x06000000, 0x06017FFF, 2),
    ("oam", 0x07000000, 0x070003FF, 2),
    ("rom", 0x08000000, 0x09FFFFFF, 4),
    ("rom_mirror_1", 0x0A000000, 0x0BFFFFFF, 4),
    ("rom_mirror_2", 0x0C000000, 0x0DFFFFFF, 4),
    ("sram", 0x0E000000, 0x0E007FFF, 1),
)

#: Address spaces that can legitimately hold a code or data pointer.
POINTER_SPACES = ("ewram", "iwram", "rom")

#: Which spaces are inside the cartridge image and therefore map to a file offset.
CARTRIDGE_SPACES = ("rom",)


class AddressError(ValueError):
    """Raised when an address or offset is outside the cartridge image."""


def to_address(offset: int) -> int:
    """File offset -> GBA ROM address."""
    if not 0 <= offset < ROM_SIZE:
        raise AddressError(
            f"file offset 0x{offset:X} is outside the cartridge image "
            f"(0x000000..0x{ROM_SIZE - 1:06X})"
        )
    return ROM_BASE + offset


def to_offset(address: int) -> int:
    """GBA ROM address -> file offset."""
    if not ROM_BASE <= address < ROM_END:
        raise AddressError(
            f"address 0x{address:08X} is not inside the cartridge image "
            f"(0x{ROM_BASE:08X}..0x{ROM_END - 1:08X})"
        )
    return address - ROM_BASE


def in_cartridge(address: int) -> bool:
    """True when an address maps to a byte of this cartridge image."""
    return ROM_BASE <= address < ROM_END


def classify_address(value: int) -> str | None:
    """Name the GBA address space a 32-bit value lands in, or None.

    Returns None for values that match no space; callers must treat None as
    "not a pointer" rather than coercing it into one.
    """
    for name, first, last, _width in ADDRESS_SPACES:
        if first <= value <= last:
            return name
    return None


def is_thumb_pointer(value: int) -> bool:
    """True when a code pointer has the Thumb state bit set (bit 0)."""
    return bool(value & 1)


def normalise_code_pointer(value: int) -> tuple[int, str]:
    """Split a code pointer into (even address, ISA implied by bit 0)."""
    return value & ~1, ("thumb" if value & 1 else "arm")


# ---------------------------------------------------------------------------
# Cartridge header
# ---------------------------------------------------------------------------
HEADER_START = 0x000000
HEADER_END = 0x0000C0

ENTRY_BRANCH_OFFSET = 0x0000
ENTRY_BRANCH_END = 0x0004
BOOT_LOGO_OFFSET = 0x0004
BOOT_LOGO_END = 0x00A0
BOOT_LOGO_LENGTH = BOOT_LOGO_END - BOOT_LOGO_OFFSET

TITLE_OFFSET = 0x00A0
TITLE_LENGTH = 12
GAME_CODE_OFFSET = 0x00AC
GAME_CODE_LENGTH = 4
MAKER_CODE_OFFSET = 0x00B0
MAKER_CODE_LENGTH = 2
FIXED_VALUE_OFFSET = 0x00B2
MAIN_UNIT_CODE_OFFSET = 0x00B3
DEVICE_TYPE_OFFSET = 0x00B4
RESERVED_1_OFFSET = 0x00B5
RESERVED_1_LENGTH = 7
SOFTWARE_VERSION_OFFSET = 0x00BC
HEADER_CHECKSUM_OFFSET = 0x00BD
RESERVED_2_OFFSET = 0x00BE
RESERVED_2_LENGTH = 2

#: The header checksum covers 0x00A0..0x00BC inclusive, seeded with 0x19.
CHECKSUM_FIRST = TITLE_OFFSET
CHECKSUM_LAST = SOFTWARE_VERSION_OFFSET
CHECKSUM_SEED = 0x19

#: The value at 0x00B2 of a valid GBA cartridge.
FIXED_VALUE = 0x96


def load_boot_logo(path: Path | None = None) -> bytes:
    """Load the mandated GBA boot logo, a fixed platform constant."""
    target = path or BOOT_LOGO_PATH
    data = target.read_bytes()
    if len(data) != BOOT_LOGO_LENGTH:
        raise AddressError(
            f"{target} is {len(data)} bytes; the GBA boot logo is exactly "
            f"{BOOT_LOGO_LENGTH}"
        )
    return data


def compute_header_checksum(header: bytes | bytearray) -> int:
    """Recompute the complement check byte from a 0xC0-byte header."""
    total = sum(header[CHECKSUM_FIRST : CHECKSUM_LAST + 1])
    return (-(CHECKSUM_SEED + total)) & 0xFF


def _decode_ascii(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")


def encode_ascii(text: str, length: int) -> bytes:
    raw = text.encode("ascii")
    if len(raw) > length:
        raise AddressError(f"{text!r} does not fit in {length} bytes")
    return raw + b"\x00" * (length - len(raw))


@dataclasses.dataclass(frozen=True)
class GbaHeader:
    """A decoded 0xC0-byte GBA cartridge header."""

    entry_branch: bytes
    boot_logo: bytes
    title: str
    game_code: str
    maker_code: str
    fixed_value: int
    main_unit_code: int
    device_type: int
    reserved_1: bytes
    software_version: int
    header_checksum: int
    reserved_2: bytes

    @property
    def computed_checksum(self) -> int:
        return compute_header_checksum(self.encode())

    @property
    def checksum_ok(self) -> bool:
        return self.header_checksum == self.computed_checksum

    @property
    def logo_is_standard(self) -> bool:
        try:
            return self.boot_logo == load_boot_logo()
        except (OSError, AddressError):
            return False

    def encode(self) -> bytes:
        """Rebuild the exact 0xC0 original bytes."""
        out = bytearray()
        out += self.entry_branch
        out += self.boot_logo
        out += encode_ascii(self.title, TITLE_LENGTH)
        out += encode_ascii(self.game_code, GAME_CODE_LENGTH)
        out += encode_ascii(self.maker_code, MAKER_CODE_LENGTH)
        out.append(self.fixed_value)
        out.append(self.main_unit_code)
        out.append(self.device_type)
        out += self.reserved_1
        out.append(self.software_version)
        out.append(self.header_checksum)
        out += self.reserved_2
        if len(out) != HEADER_END:
            raise AddressError(f"encoded header is {len(out)} bytes, expected {HEADER_END}")
        return bytes(out)

    def as_dict(self) -> dict:
        return {
            "entry_branch_bytes": self.entry_branch.hex(),
            "title": self.title,
            "game_code": self.game_code,
            "maker_code": self.maker_code,
            "fixed_value": self.fixed_value,
            "main_unit_code": self.main_unit_code,
            "device_type": self.device_type,
            "reserved_1_hex": self.reserved_1.hex(),
            "software_version": self.software_version,
            "header_checksum": self.header_checksum,
            "header_checksum_computed": self.computed_checksum,
            "header_checksum_valid": self.checksum_ok,
            "boot_logo_is_standard": self.logo_is_standard,
            "reserved_2_hex": self.reserved_2.hex(),
        }


def decode_header(data: bytes) -> GbaHeader:
    """Decode the first 0xC0 bytes of a cartridge image."""
    if len(data) < HEADER_END:
        raise AddressError(
            f"need at least {HEADER_END} bytes to decode a header, got {len(data)}"
        )
    return GbaHeader(
        entry_branch=bytes(data[ENTRY_BRANCH_OFFSET:ENTRY_BRANCH_END]),
        boot_logo=bytes(data[BOOT_LOGO_OFFSET:BOOT_LOGO_END]),
        title=_decode_ascii(data[TITLE_OFFSET : TITLE_OFFSET + TITLE_LENGTH]),
        game_code=_decode_ascii(data[GAME_CODE_OFFSET : GAME_CODE_OFFSET + GAME_CODE_LENGTH]),
        maker_code=_decode_ascii(data[MAKER_CODE_OFFSET : MAKER_CODE_OFFSET + MAKER_CODE_LENGTH]),
        fixed_value=data[FIXED_VALUE_OFFSET],
        main_unit_code=data[MAIN_UNIT_CODE_OFFSET],
        device_type=data[DEVICE_TYPE_OFFSET],
        reserved_1=bytes(data[RESERVED_1_OFFSET : RESERVED_1_OFFSET + RESERVED_1_LENGTH]),
        software_version=data[SOFTWARE_VERSION_OFFSET],
        header_checksum=data[HEADER_CHECKSUM_OFFSET],
        reserved_2=bytes(data[RESERVED_2_OFFSET : RESERVED_2_OFFSET + RESERVED_2_LENGTH]),
    )
