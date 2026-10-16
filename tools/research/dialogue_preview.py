"""Render a dialogue line the way the game does, and fit the layout against a real capture.

Read-only over the ROM; every image it writes goes where the caller says, which for ROM-derived data
must be an ignored build path.

WHAT IS DRAWN FROM WHAT. The glyphs come from the font table through its descriptor (see
`dialogue_font`), the background from the box-art container the strip builder decompresses into its
surface (measured: 10,240 bytes = 160x64 at 8bpp), and the colours from the OBJ palette the surface is
drawn with. The engine's placement rules, all measured: advance = width + 1, line height 16, four lines
per page, ink is an 8bpp index, and a glyph is 16 rows tall with row 0 at the top.

WHY THE ORIGIN IS A PARAMETER. The strip's surface origin relative to the box's drawn position is not
established statically (the strip's x/y come from a layout table selected at run time). So the origin
is fitted: `--fit` searches a small window of origins and reports the one whose render has the fewest
differing pixels against a capture. A fitted origin with a zero-pixel difference is a measurement; a
chosen origin would be a guess.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.dialogue_font import Font, GLYPH_ROWS  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
OBJ_PALETTE = 0x5652C            # the global 256-entry BGR555 object palette
BOX_ART_PRIMARY = 0x71758        # the container the strip builder decompresses into its surface
BOX_ART_ALT = 0x71A6C
SURFACE_WIDTH = 160
SURFACE_HEIGHT = 64
#: MEASURED against a native capture: a fitted layout gave 477 of 477 engine ink pixels and zero
#: disagreement with line spacing 14, text origin (8,3) and a wrap width of 108. The static lane read a
#: 16-pixel line height from the cell arithmetic and found no width comparison at all, so the wrap rule
#: is engine behaviour only the capture could show.
LINE_HEIGHT = 14
TEXT_ORIGIN = (8, 3)
WRAP_WIDTH = 108
LINES_PER_PAGE = 4
NEWLINE = 0x0A
INK_ESCAPE = 0x0008
DEFAULT_INK = 2               # palette index 2 is white, the ink the capture showed


def bgr555_to_rgb(word: int) -> tuple[int, int, int]:
    red = (word & 0x1F) << 3
    green = ((word >> 5) & 0x1F) << 3
    blue = ((word >> 10) & 0x1F) << 3
    return red | (red >> 5), green | (green >> 5), blue | (blue >> 5)


def load_palette(image: bytes, offset: int = OBJ_PALETTE, count: int = 256) -> list[tuple[int, int, int]]:
    return [bgr555_to_rgb(struct.unpack_from("<H", image, offset + 2 * index)[0])
            for index in range(count)]


def load_box_art(image: bytes, offset: int = BOX_ART_PRIMARY) -> bytes:
    """The box surface: the container's decoded payload, 160x64 at one byte per pixel."""
    container = webfoot_lz.unpack(image, offset)
    if len(container.data) != SURFACE_WIDTH * SURFACE_HEIGHT:
        raise ValueError(f"box art at 0x{offset:X} decodes to {len(container.data)} bytes, "
                         f"expected {SURFACE_WIDTH * SURFACE_HEIGHT}")
    return bytes(container.data)


def split_units(text: str) -> list[int]:
    """A line's codes, with the engine's control units recognised rather than drawn.

    Only the units that matter to layout are interpreted: `0x0A` is a line break, `0x0008 <value>` sets
    the ink and consumes its own operand. Everything else is a glyph code.
    """
    units: list[int] = []
    for character in text:
        units.append(ord(character))
    return units


def render_units(font: Font, units: list[int], ink: int = DEFAULT_INK,
                 origin: tuple[int, int] = TEXT_ORIGIN) -> tuple[bytes, int, int]:
    """Compose codes into a 160x64 indexed surface over the box art.

    Returns the surface, the number of lines used and the ink index that ended up in force.
    """
    surface = bytearray(load_box_art(font.image))
    x, y = origin
    line = 0
    index = 0
    current_ink = ink
    while index < len(units):
        code = units[index]
        if code == NEWLINE:
            line += 1
            x = origin[0]
            y = origin[1] + line * LINE_HEIGHT
            index += 1
            continue
        if code == INK_ESCAPE and index + 1 < len(units):
            current_ink = units[index + 1] & 0xFF
            index += 2
            continue
        glyph = font.glyph(code)
        if glyph is not None and y + GLYPH_ROWS <= SURFACE_HEIGHT:
            for column in range(glyph.width):
                if x + column >= SURFACE_WIDTH:
                    break
                bits = glyph.columns[column]
                for row in range(GLYPH_ROWS):
                    if (bits >> row) & 1:
                        surface[(y + row) * SURFACE_WIDTH + x + column] = current_ink
        x += font.advance(code)
        if x >= SURFACE_WIDTH:
            line += 1
            x = origin[0]
            y = origin[1] + line * LINE_HEIGHT
        index += 1
    return bytes(surface), line + 1, current_ink


def write_png(path: Path, surface: bytes, palette: list[tuple[int, int, int]],
              scale: int = 1) -> None:
    """Write an indexed-pixel PNG by hand: no dependency, and the indices are the data."""
    rows = []
    for row in range(SURFACE_HEIGHT):
        line = bytearray()
        for column in range(SURFACE_WIDTH):
            pixel = surface[row * SURFACE_WIDTH + column]
            line += bytes([pixel]) * scale
        for _ in range(scale):
            rows.append(bytes(line))
    raw = b"".join(b"\x00" + row for row in rows)

    import zlib
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", SURFACE_WIDTH * scale, SURFACE_HEIGHT * scale, 8, 3, 0, 0, 0)
    plte = b"".join(bytes(colour) for colour in palette)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"PLTE", plte)
                     + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def read_png_pixels(path: Path) -> tuple[int, int, list[bytes]]:
    """Read an ordinary indexed or RGB PNG into rows of palette indices when possible."""
    import zlib
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")
    position = 8
    width = height = None
    colour_type = None
    palette: bytes = b""
    idat = b""
    while position < len(data):
        length = struct.unpack_from(">I", data, position)[0]
        kind = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        if kind == b"IHDR":
            width, height, _depth, colour_type = struct.unpack_from(">IIBB", payload)
        elif kind == b"PLTE":
            palette = payload
        elif kind == b"IDAT":
            idat += payload
        position += 12 + length
    raw = zlib.decompress(idat)
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour_type]
    stride = width * channels
    rows = []
    previous = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        line = bytearray(raw[offset:offset + stride])
        offset += stride
        for index in range(stride):
            left = line[index - channels] if index >= channels else 0
            up = previous[index]
            up_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                line[index] = (line[index] + left) & 0xFF
            elif filter_type == 2:
                line[index] = (line[index] + up) & 0xFF
            elif filter_type == 3:
                line[index] = (line[index] + (left + up) // 2) & 0xFF
            elif filter_type == 4:
                estimate = left + up - up_left
                candidates = (left, up, up_left)
                best = min(candidates, key=lambda value: abs(value - estimate))
                line[index] = (line[index] + best) & 0xFF
        rows.append(bytes(line))
        previous = line
    return width, height, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--text", default="")
    parser.add_argument("--ink", type=int, default=1)
    parser.add_argument("--origin", default="8,16")
    parser.add_argument("--out")
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--fit", help="a capture PNG to fit the origin against")
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()
    font = Font(image)
    palette = load_palette(image)
    units = split_units(args.text)
    origin = tuple(int(part) for part in args.origin.split(","))
    surface, lines, ink = render_units(font, units, args.ink, origin)
    print(f"font table 0x{font.table + ROM_BASE:08X}, {len(units)} unit(s), {lines} line(s), "
          f"ink {ink}, origin {origin}")
    if args.out:
        write_png(Path(args.out), surface, palette, args.scale)
        print(f"# wrote {args.out} ({SURFACE_WIDTH * args.scale}x{SURFACE_HEIGHT * args.scale})")
    if args.fit:
        width, height, rows = read_png_pixels(Path(args.fit))
        print(f"capture {width}x{height}")
        best = None
        for origin_x in range(0, 17):
            for origin_y in range(0, 25):
                candidate, _lines, _ink = render_units(font, units, args.ink, (origin_x, origin_y))
                differing = 0
                for row in range(SURFACE_HEIGHT):
                    for column in range(SURFACE_WIDTH):
                        if candidate[row * SURFACE_WIDTH + column] != surface[row * SURFACE_WIDTH + column]:
                            differing += 1
                if best is None or differing < best[0]:
                    best = (differing, origin_x, origin_y)
        print(f"fit: best origin {best[1]},{best[2]} with {best[0]} differing pixel(s) "
              f"(self-comparison is the control and must be 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
