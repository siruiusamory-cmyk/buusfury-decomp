"""Fixed-format regions: independently generated rather than copied.

Three regions have no toolchain dependency at all. The public reference project
emits them from source; this module generates them from project-owned facts and
proves the result byte-for-byte against the ROM.

  rom_header         192 bytes   entry branch + boot logo + header fields
  gbaram_literals     16 bytes   four address/sentinel words
  titlescreen_data   104 bytes   26 words recorded as facts, semantics UNKNOWN

The distinction that matters: this module does not copy bytes out of the ROM. It
constructs them from declared values and then asserts the construction matches.
Where a value is an address or a sentinel it is a fact about the program's
interface, not creative content. Where a value's meaning is unknown the config
says so rather than inventing a name.

The 156-byte boot logo is a fixed platform constant present in every Game Boy
Advance cartridge, not game content. It is stored at data/gba_boot_logo.bin and a
test asserts it is byte-identical to the mandated constant, which is what makes
including it defensible rather than merely convenient.
"""

from __future__ import annotations

import dataclasses
import json
import struct
from pathlib import Path

from . import gba


class FixedRegionError(RuntimeError):
    """Raised when a declared fixed region does not reproduce."""


def load_config(path: Path | None = None) -> dict:
    target = path or (gba.DATA_DIR / "fixed_regions.json")
    return json.loads(target.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# rom_header
# ---------------------------------------------------------------------------
def encode_branch(source: int, target: int) -> bytes:
    """Encode an unconditional ARM `B` from source to target.

    Derived rather than copied: the header's first word is a function of the
    entry address, so a change of entry point would change the bytes.
    """
    offset = target - (source + 8)
    if offset % 4:
        raise FixedRegionError(f"branch offset 0x{offset:X} is not word aligned")
    displacement = offset // 4
    if not -(1 << 23) <= displacement < (1 << 23):
        raise FixedRegionError(f"branch displacement {displacement} out of range")
    return struct.pack("<I", 0xEA000000 | (displacement & 0x00FFFFFF))


def generate_header(config: dict) -> bytes:
    """Build the 192-byte cartridge header from declared fields."""
    header = config["rom_header"]
    fields = header["fields"]
    out = bytearray()
    out += encode_branch(header["entry_source"], header["entry_target"])
    out += gba.load_boot_logo()
    out += gba.encode_ascii(fields["title"], gba.TITLE_LENGTH)
    out += gba.encode_ascii(fields["game_code"], gba.GAME_CODE_LENGTH)
    out += gba.encode_ascii(fields["maker_code"], gba.MAKER_CODE_LENGTH)
    out.append(fields["fixed_value"])
    out.append(fields["main_unit_code"])
    out.append(fields["device_type"])
    out += bytes.fromhex(fields["reserved_1_hex"])
    out.append(fields["software_version"])
    out.append(fields["header_checksum"])
    out += bytes.fromhex(fields["reserved_2_hex"])
    if len(out) != gba.HEADER_END:
        raise FixedRegionError(f"generated header is {len(out)} bytes, expected {gba.HEADER_END}")
    return bytes(out)


# ---------------------------------------------------------------------------
# word tables
# ---------------------------------------------------------------------------
def generate_word_table(entries: list[dict]) -> bytes:
    """Serialize a declared list of 32-bit words, refusing undeclared widths."""
    out = bytearray()
    for entry in entries:
        value = entry["value"]
        if not 0 <= value <= 0xFFFFFFFF:
            raise FixedRegionError(f"value {value} does not fit in 32 bits")
        out += struct.pack("<I", value)
    return bytes(out)


def generate_gbaram_literals(config: dict) -> bytes:
    return generate_word_table(config["gbaram_literals"]["words"])


def generate_titlescreen_data(config: dict) -> bytes:
    return generate_word_table(config["titlescreen_data"]["words"])


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class FixedRegionResult:
    region_id: str
    start: int
    end: int
    generated_length: int
    matches_rom: bool
    first_difference: int | None
    detail: str

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


GENERATORS = {
    "rom_header": generate_header,
    "gbaram_literals": generate_gbaram_literals,
    "titlescreen_data": generate_titlescreen_data,
}


def region_extent(config: dict, region_id: str) -> tuple[int, int]:
    for entry in config["regions"]:
        if entry["id"] == region_id:
            return int(entry["start"], 0), int(entry["end"], 0)
    raise FixedRegionError(f"region {region_id} is not declared in fixed_regions.json")


def verify_all(data: bytes, config: dict | None = None) -> list[FixedRegionResult]:
    """Generate every fixed region and compare it to the ROM. Never raises."""
    cfg = config if config is not None else load_config()
    results: list[FixedRegionResult] = []
    for region_id, generator in GENERATORS.items():
        start, end = region_extent(cfg, region_id)
        expected = data[start:end]
        try:
            generated = generator(cfg)
        except (FixedRegionError, OSError, KeyError) as exc:
            results.append(
                FixedRegionResult(region_id, start, end, 0, False, None, f"generation failed: {exc}")
            )
            continue
        difference = next(
            (i for i in range(min(len(expected), len(generated))) if expected[i] != generated[i]),
            None,
        )
        if difference is None and len(expected) != len(generated):
            difference = min(len(expected), len(generated))
        results.append(
            FixedRegionResult(
                region_id=region_id,
                start=start,
                end=end,
                generated_length=len(generated),
                matches_rom=(difference is None),
                first_difference=difference,
                detail=(
                    "generated bytes are byte-identical to the cartridge"
                    if difference is None
                    else f"first difference at file 0x{start + difference:06X}"
                ),
            )
        )
    return results
