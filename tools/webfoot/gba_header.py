"""Minimal Game Boy Advance header parser for safe identification."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


HEADER_SIZE = 0xC0
TITLE_SLICE = slice(0xA0, 0xAC)
GAME_CODE_SLICE = slice(0xAC, 0xB0)
MAKER_CODE_SLICE = slice(0xB0, 0xB2)
FIXED_VALUE_OFFSET = 0xB2
SOFTWARE_VERSION_OFFSET = 0xBC
CHECKSUM_OFFSET = 0xBD


class GbaHeaderError(ValueError):
    """Raised when a file cannot supply a parseable minimal GBA header."""


def calculate_header_checksum(header: bytes) -> int:
    if len(header) < HEADER_SIZE:
        raise GbaHeaderError(
            f"GBA header requires at least {HEADER_SIZE} bytes; got {len(header)}"
        )
    return (-(sum(header[0xA0:0xBD]) + 0x19)) & 0xFF


def _decode_ascii(raw: bytes, field_name: str, *, strip_padding: bool = False) -> str:
    try:
        value = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise GbaHeaderError(f"{field_name} is not ASCII") from exc
    return value.rstrip("\x00 ") if strip_padding else value


@dataclass(frozen=True, slots=True)
class GbaHeader:
    title: str
    game_code: str
    maker_code: str
    software_version: int
    header_checksum: int
    calculated_checksum: int
    checksum_valid: bool
    fixed_value: int
    fixed_value_valid: bool
    reserved_bytes_valid: bool
    text_fields_valid: bool

    @property
    def basic_valid(self) -> bool:
        return (
            self.checksum_valid
            and self.fixed_value_valid
            and self.reserved_bytes_valid
            and self.text_fields_valid
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "GbaHeader":
        if len(data) < HEADER_SIZE:
            raise GbaHeaderError(
                f"GBA header requires at least {HEADER_SIZE} bytes; got {len(data)}"
            )

        header = data[:HEADER_SIZE]
        title = _decode_ascii(header[TITLE_SLICE], "title", strip_padding=True)
        game_code = _decode_ascii(header[GAME_CODE_SLICE], "game code")
        maker_code = _decode_ascii(header[MAKER_CODE_SLICE], "maker code")
        calculated = calculate_header_checksum(header)
        stored = header[CHECKSUM_OFFSET]
        reserved_valid = (
            header[0xB3:0xBC] == bytes(9) and header[0xBE:0xC0] == bytes(2)
        )
        text_valid = (
            bool(title)
            and len(game_code) == 4
            and game_code.isalnum()
            and len(maker_code) == 2
            and maker_code.isalnum()
        )

        return cls(
            title=title,
            game_code=game_code,
            maker_code=maker_code,
            software_version=header[SOFTWARE_VERSION_OFFSET],
            header_checksum=stored,
            calculated_checksum=calculated,
            checksum_valid=stored == calculated,
            fixed_value=header[FIXED_VALUE_OFFSET],
            fixed_value_valid=header[FIXED_VALUE_OFFSET] == 0x96,
            reserved_bytes_valid=reserved_valid,
            text_fields_valid=text_valid,
        )


def parse_gba_header(path: str | Path) -> GbaHeader:
    source = Path(path)
    with source.open("rb") as stream:
        header = stream.read(HEADER_SIZE)
    return GbaHeader.from_bytes(header)
