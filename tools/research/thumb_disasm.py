"""Resynchronising read-only Thumb/ARM disassembly helpers for LOGX-LAYER-001.

Repository rule (``docs/research-conventions.md``, "Static disassembly
discipline"): a naive linear sweep stops at the first undecodable halfword and
silently returns nothing for every later address, so an empty sweep is not
evidence of absence.  This module therefore never reports absence from a linear
sweep.  It offers:

* :func:`linear_thumb` - a resynchronising single-pass sweep that advances two
  bytes past an undecodable halfword instead of stopping and reports how many
  halfwords it could not decode;
* :func:`thumb_function` - a control-flow-following decode from a seeded entry;
* :func:`find_thumb_function_entries` - discovers Thumb ``push {.., lr}``
  prologues across a bounded region as candidate boundaries;
* :func:`resolve_thumb_bl` - exact BL/BLX target decoding from raw halfwords.

Nothing here writes to the ROM image or to any file.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

try:  # pragma: no cover - dependency presence is environment-specific
    import capstone
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"capstone is required for this probe: {exc}") from exc

ROM_BASE = 0x08000000

_THUMB = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
_THUMB.detail = False
_ARM = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
_ARM.detail = False


@dataclass(frozen=True, slots=True)
class Instruction:
    address: int
    size: int
    mnemonic: str
    operands: str

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.address:08x}  {self.mnemonic:<8} {self.operands}".rstrip()


@dataclass(slots=True)
class SweepResult:
    """Accumulated result of a resynchronising linear sweep."""

    instructions: list[Instruction] = field(default_factory=list)
    undecodable_halfwords: list[int] = field(default_factory=list)
    start: int = 0
    end: int = 0

    @property
    def coverage_bytes(self) -> int:
        return self.end - self.start


def iter_thumb(data: bytes, start: int, end: int) -> Iterator[Instruction | int]:
    """Yield each decodable Thumb instruction, or the address (an ``int``) of an
    undecodable halfword, in one pass over ``[start, end)``.

    This is the only sweep primitive: correctness (resynchronisation) and speed
    (a single pass) both matter for the caller's absence claims.
    """
    address = start & ~1
    while address + 2 <= end:
        offset = address - ROM_BASE
        if offset < 0 or offset + 2 > len(data):
            break
        item = next(_THUMB.disasm(data[offset : offset + 2], address, 2), None)
        if item is None:
            yield address
            address += 2
            continue
        yield Instruction(item.address, item.size, item.mnemonic, item.op_str)
        address += item.size


def linear_thumb(data: bytes, start: int, end: int) -> SweepResult:
    """Materialised resynchronising Thumb sweep over ``[start, end)``."""
    result = SweepResult(start=start, end=end)
    for item in iter_thumb(data, start, end):
        if isinstance(item, int):
            result.undecodable_halfwords.append(item)
        else:
            result.instructions.append(item)
    return result


def linear_arm(data: bytes, start: int, end: int) -> SweepResult:
    """Resynchronising linear ARM sweep over ``[start, end)``."""
    result = SweepResult(start=start, end=end)
    address = start & ~3
    while address + 4 <= end:
        offset = address - ROM_BASE
        if offset < 0 or offset + 4 > len(data):
            break
        decoded = next(_ARM.disasm(data[offset : offset + 4], address, 4), None)
        if decoded is None:
            result.undecodable_halfwords.append(address)
            address += 4
            continue
        result.instructions.append(
            Instruction(decoded.address, decoded.size, decoded.mnemonic, decoded.op_str)
        )
        address += decoded.size
    return result


def resolve_thumb_bl(address: int, high: int, low: int) -> int:
    """Absolute target of a Thumb ``BL``/``BLX`` halfword pair (T1 encoding)."""
    sign = (high >> 10) & 1
    j1 = (low >> 13) & 1
    j2 = (low >> 11) & 1
    i1 = 1 - (j1 ^ sign)
    i2 = 1 - (j2 ^ sign)
    offset = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((high & 0x3FF) << 12)
        | ((low & 0x7FF) << 1)
    )
    if offset & 0x01000000:
        offset -= 0x02000000
    return address + 4 + offset


def scan_thumb_bl_callers(
    data: bytes, targets: set[int], *, start: int = ROM_BASE, end: int | None = None
) -> dict[int, list[int]]:
    """Every raw Thumb ``BL``/``BLX`` resolving to a member of ``targets``.

    Works on halfword encodings directly, so an undecodable neighbouring
    halfword cannot hide a caller and the scan is a single pass.  Targets are
    compared with the Thumb state bit cleared.
    """
    limit = end if end is not None else ROM_BASE + len(data)
    wanted = {target & ~1 for target in targets}
    found: dict[int, list[int]] = {target: [] for target in wanted}
    address = start & ~1
    while address + 4 <= limit:
        offset = address - ROM_BASE
        if offset < 0 or offset + 4 > len(data):
            break
        high = data[offset] | (data[offset + 1] << 8)
        low = data[offset + 2] | (data[offset + 3] << 8)
        if (high & 0xF800) == 0xF000 and (low & 0xF800) in (0xF800, 0xE800):
            resolved = resolve_thumb_bl(address, high, low) & ~1
            if resolved in found:
                found[resolved].append(address)
        address += 2
    return found


def scan_word_references(
    data: bytes, values: set[int], *, aligned_only: bool = True
) -> dict[int, list[int]]:
    """Every ROM address whose 32-bit little-endian word equals one of ``values``.

    ``str.find`` over a packed needle table, so a full-image scan is cheap while
    remaining exact.  The caller must state the alignment used when reporting a
    negative result.
    """
    step = 4 if aligned_only else 2
    found: dict[int, list[int]] = {value: [] for value in values}
    needles = {value: value.to_bytes(4, "little") for value in values}
    offset = 0
    while offset + 4 <= len(data):
        chunk = data[offset : offset + 4]
        for value, needle in needles.items():
            if chunk == needle:
                found[value].append(offset + ROM_BASE)
        offset += step
    return found


def find_thumb_function_entries(
    data: bytes, start: int, end: int, *, require_lr_push: bool = True
) -> list[int]:
    """Candidate function entries: Thumb ``push`` of a list containing ``lr``."""
    entries: list[int] = []
    for item in iter_thumb(data, start, end):
        if isinstance(item, int):
            continue
        if item.mnemonic == "push" and (not require_lr_push or "lr" in item.operands):
            entries.append(item.address)
    return entries
