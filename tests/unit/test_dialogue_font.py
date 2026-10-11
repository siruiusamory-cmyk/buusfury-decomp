"""The dialogue font's shape, pinned by measurement instead of by its artwork.

WHY THERE IS NO GLYPH ART HERE. An earlier version of this file carried the decoded bitmaps of two
commercial font glyphs as ASCII art, plus a machine-specific absolute path to the ROM. Both are
prohibited: `docs/ROM_SAFETY.md` says a local-ROM test must not commit anything derived from the image,
and no tracked file may hold a machine path. A glyph's shape is pinned here by its WIDTH and by a
SHA-256 over its column words instead, which is a checksum of the ROM's data rather than the data.

The ROM is reached only through `tests.rom_support`, which skips the test when the canonical image is
absent and refuses one whose digest is not the profile these offsets target, so these tests never
bypass the project's ROM gate.
"""

from __future__ import annotations

import hashlib
import struct

import pytest

from tests.rom_support import canonical_rom_bytes
from tools.research.dialogue_font import DIALOGUE_FONT_DESCRIPTOR, Font, FontError

#: sha256 over `u16 width` followed by the glyph's `width + 1` column words, little endian. A digest
#: detects a changed glyph without storing the glyph.
GLYPH_DIGESTS = {
    0x41: ("A", 9, "d20a9e9edf5d2155459118be6fbc4f9f91e3dd0fd351b11c842551e588d8760a"),
    0x31: ("1", 4, "345464c845eafda7a61a7e82c70931491feb3752483f8b9ffd5aaab0e540cc84"),
    0x77: ("w", 9, "9815dd86874cf567252e4c6553092785cde8ad1d4df022c16f0c0f3365bafabb"),
    0x20: (" ", 3, "41f45e0c4ba13f0e8c873f321d4a83b354816b4f6f1c7cb51b97d7fae02ebe25"),
}


@pytest.fixture(scope="module")
def image() -> bytes:
    """The canonical image through the project's gate: absent means skip, wrong digest means skip."""
    return canonical_rom_bytes()


def test_the_descriptor_is_a_descriptor_not_a_table(image: bytes) -> None:
    table, wide_advance, wide_base = struct.unpack_from("<IHI", image, DIALOGUE_FONT_DESCRIPTOR)
    assert table == 0x0806E05C, "the table the descriptor names, not the descriptor's own address"
    assert wide_advance == 11, "the fixed class advance for codes at or above 0xFF"
    assert wide_base == 0, "retail ships no wide glyphs at all"


def test_each_glyph_keeps_its_width_and_its_column_digest(image: bytes) -> None:
    font = Font(image)
    for code, (character, width, digest) in GLYPH_DIGESTS.items():
        glyph = font.glyph(code)
        assert glyph is not None, f"{character!r} (code {code}) has no record"
        assert glyph.width == width, f"{character!r} changed width"
        payload = struct.pack("<H", glyph.width) + b"".join(
            struct.pack("<H", column) for column in glyph.columns)
        assert hashlib.sha256(payload).hexdigest() == digest, f"{character!r} changed shape"


def test_the_advance_rule_and_the_apostrophe_erratum(image: bytes) -> None:
    font = Font(image)
    assert font.advance(0x41) == 10, "stored width 9 plus one"
    assert font.advance(0x20) == 4
    assert font.advance(0x27) == 3, (
        "the render-path document says 4; the table and two independent lanes say 3")
    assert font.advance(0xFF) == 12, "fixed class: wide advance 11 plus one"
    # Code 0xFF carries a record but both readers route it to the fixed class, so its glyph is
    # UNREACHABLE rather than absent: a preview must follow the readers, not the table.
    assert font.glyph(0xFF) is not None and font.glyph(0xFF).width == 1
    assert font.advance(0x100) == 12


def test_codes_without_a_record_draw_nothing_and_advance_one(image: bytes) -> None:
    font = Font(image)
    for code in range(0x20):
        assert font.glyph(code) is None
        assert font.advance(code) == 1


def test_the_population_is_the_measured_one(image: bytes) -> None:
    population = Font(image).population()
    assert population["codes_with_a_record"] == 224
    assert population["codes_with_ink"] == 150
    assert population["blank_records"] == 74
    assert population["codes_without_a_record"] == 32


def test_a_descriptor_that_names_no_table_is_refused() -> None:
    with pytest.raises(FontError):
        Font(b"\x00" * 64, descriptor=0)
