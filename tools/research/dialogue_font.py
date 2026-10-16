"""Extract the dialogue font from a ROM image and draw its glyphs.

Read-only over the image; the extracted data is returned in memory and may be written to an ignored
build path, never into the repository (the owner's rule: font data is extracted at build time from the
user's own ROM).

WHAT THE FONT IS, measured by two independent lanes and reproduced here:

* the font is reached through a 12-byte DESCRIPTOR: `u32 table`, `u16 wide_advance`, `u32 wide_base`
  (file `0x6EE6C` for the dialogue font, and `0x6E050` / `0x6F150` for two other styles);
* the table it names (file `0x6E05C` for the dialogue font, `0xE10` bytes long) is 256 `u16`
  code -> record offsets IN `u16` UNITS relative to the table base, indexed by the RAW code, followed
  by the records themselves, contiguous and without padding;
* a record is `u16 width` then `width + 1` `u16` columns. Column `k` is pixel column `x = k`, and bit
  `r` of a column (least significant bit first) is pixel row `r`, row 0 at the top. There are 16 rows.
  The last stored column is always zero and is record stride, not ink;
* the advance is `width + 1`. A code with no record (map entry zero, which is every code below 0x20)
  draws nothing and advances 1. A code at or above 0xFF takes the fixed class: no glyph, advance
  `wide_advance + 1`. Retail's `wide_base` is zero, so retail has no wide glyphs at all.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

ROM_BASE = 0x08000000
DIALOGUE_FONT_DESCRIPTOR = 0x6EE6C
GLYPH_ROWS = 16
WIDE_CODE = 0xFF
DRAW_LIMIT = 0x1D9D          # a literal in the rasteriser: a code at or above it draws nothing


class FontError(Exception):
    """A refusal: the descriptor or the table is not shaped the way the engine requires."""


@dataclass(frozen=True)
class Glyph:
    """One glyph: its ink width and its columns, one u16 per column."""

    code: int
    width: int
    columns: tuple[int, ...]

    def rows(self) -> list[str]:
        """The glyph as text rows, `#` for ink, so a reader can check it by eye."""
        return ["".join("#" if (self.columns[column] >> row) & 1 else "."
                        for column in range(self.width))
                for row in range(GLYPH_ROWS)]


class Font:
    """The glyphs of one descriptor, with the engine's own lookup rules."""

    def __init__(self, image: bytes, descriptor: int = DIALOGUE_FONT_DESCRIPTOR) -> None:
        self.image = image
        self.descriptor = descriptor
        table_pointer, wide_advance, wide_base = struct.unpack_from("<IHI", image, descriptor)
        if table_pointer < ROM_BASE:
            raise FontError(f"descriptor at 0x{descriptor:X} names no table")
        self.table = table_pointer - ROM_BASE
        self.wide_advance = wide_advance
        self.wide_base = wide_base
        self.map = [struct.unpack_from("<H", image, self.table + 2 * code)[0]
                    for code in range(256)]
        self._glyphs: dict[int, Glyph | None] = {}

    def glyph(self, code: int) -> Glyph | None:
        """The glyph for a code, or None where the engine draws nothing."""
        if not 0 <= code < 256:
            return None
        if code in self._glyphs:
            return self._glyphs[code]
        offset = self.map[code]
        glyph = None
        if offset:
            record = self.table + 2 * offset
            width = struct.unpack_from("<H", self.image, record)[0]
            columns = tuple(struct.unpack_from("<H", self.image, record + 2 + 2 * index)[0]
                            for index in range(width + 1))
            glyph = Glyph(code=code, width=width, columns=columns)
        self._glyphs[code] = glyph
        return glyph

    def advance(self, code: int) -> int:
        """How far the cursor moves after this code, exactly as the engine computes it."""
        if code >= WIDE_CODE:
            return self.wide_advance + 1
        glyph = self.glyph(code)
        return 1 if glyph is None else glyph.width + 1

    def population(self) -> dict:
        """How many codes have ink, how many are blank, and how many have no record at all."""
        with_record = [code for code in range(256) if self.map[code]]
        ink = [code for code in with_record if self.sets_ink(code)]
        return {"codes_with_a_record": len(with_record), "codes_with_ink": len(ink),
                "blank_records": len(with_record) - len(ink),
                "codes_without_a_record": 256 - len(with_record),
                "wide_advance": self.wide_advance, "wide_base": self.wide_base}

    def sets_ink(self, code: int) -> bool:
        """Whether this code puts any pixel down: a blank record has a width but no set bit."""
        glyph = self.glyph(code)
        if glyph is None:
            return False
        return any(column for column in glyph.columns)


def render_glyphs(image: bytes, text: str, *, ink: int = 1,
                  descriptor: int = DIALOGUE_FONT_DESCRIPTOR) -> tuple[int, list[list[int]]]:
    """Compose a string's glyphs into a bitmap: (width, rows of palette indices).

    This is glyph-exact, not box-exact: it applies the engine's own lookup, widths and bit order, with
    no line breaking and no box art. The box-exact renderer is the preview tool.
    """
    font = Font(image, descriptor)
    columns: list[list[int]] = []
    x = 0
    for character in text:
        code = ord(character)
        glyph = font.glyph(code)
        if glyph is not None:
            for column in range(glyph.width):
                while len(columns) <= x:
                    columns.append([])
                for row in range(GLYPH_ROWS):
                    if (glyph.columns[column] >> row) & 1:
                        columns[x][row] = ink
        else:
            while len(columns) <= x:
                columns.append([0] * GLYPH_ROWS)
        advance = font.advance(code)
        for step in range(advance):
            while len(columns) <= x + step:
                columns.append([0] * GLYPH_ROWS)
        x += advance
    rows = [[columns[column][row] if column < len(columns) else 0 for column in range(x)]
            for row in range(GLYPH_ROWS)]
    return x, rows


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--glyphs", default="Aa1. 'w,")
    parser.add_argument("--json")
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()
    font = Font(image)
    print(f"descriptor 0x{font.descriptor:X}: table 0x{font.table + ROM_BASE:08X}, "
          f"wide advance {font.wide_advance}, wide base 0x{font.wide_base:08X}")
    print(f"population {font.population()}")
    for character in args.glyphs:
        glyph = font.glyph(ord(character))
        if glyph is None:
            print(f"\n{character!r} (code {ord(character)}): no record, advance "
                  f"{font.advance(ord(character))}")
            continue
        print(f"\n{character!r} (code {ord(character)}): width {glyph.width}, "
              f"advance {font.advance(ord(character))}")
        for row in glyph.rows():
            print(f"  |{row}|")
    if args.json:
        import json
        payload = {"descriptor": f"0x{font.descriptor:X}", "table": f"0x{font.table + ROM_BASE:08X}",
                   "population": font.population(),
                   "widths": {code: font.advance(code) for code in range(32, 127)}}
        Path(args.json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\n# wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
