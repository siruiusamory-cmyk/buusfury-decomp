from __future__ import annotations

import struct
import zlib

TILE = 8
TILE_BYTES = 64
SHEET_TILES_ACROSS = 16
SIGNATURE = b"\x89PNG\r\n\x1a\n"


class SheetError(ValueError):
    pass


def read_indexed(path):
    data = open(path, "rb").read()
    if data[:8] != SIGNATURE:
        raise SheetError("%s is not a PNG" % path)
    cursor = 8
    header = None
    palette = None
    compressed = bytearray()
    while cursor + 8 <= len(data):
        length, tag = struct.unpack_from(">I4s", data, cursor)
        body = data[cursor + 8:cursor + 8 + length]
        if len(body) != length:
            raise SheetError("%s: the %s chunk is truncated" % (path, tag.decode("latin-1")))
        cursor += 12 + length
        if tag == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif tag == b"PLTE":
            if len(body) % 3:
                raise SheetError("%s: the palette is %d bytes" % (path, len(body)))
            palette = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif tag == b"tRNS":
            raise SheetError("%s carries a tRNS chunk: a transparent index is not a palette index"
                             % path)
        elif tag == b"IDAT":
            compressed += body
        elif tag == b"IEND":
            break
    if header is None:
        raise SheetError("%s has no IHDR" % path)
    width, height, depth, colour, compression, filtering, interlace = header
    if (depth, colour, compression, filtering, interlace) != (8, 3, 0, 0, 0):
        raise SheetError("%s is depth=%d colour=%d compression=%d filter=%d interlace=%d, not an"
                         " 8-bit indexed, non-interlaced PNG"
                         % (path, depth, colour, compression, filtering, interlace))
    if palette is None or not palette:
        raise SheetError("%s has no palette" % path)
    raw = zlib.decompress(bytes(compressed))
    if len(raw) != height * (width + 1):
        raise SheetError("%s holds %d scanline bytes against %d" % (path, len(raw), height * (width + 1)))
    indices = bytearray()
    previous = bytearray(width)
    cursor = 0
    for _ in range(height):
        kind = raw[cursor]
        line = bytearray(raw[cursor + 1:cursor + 1 + width])
        cursor += width + 1
        _unfilter(kind, line, previous, width, path)
        indices += line
        previous = line
    high = max(indices) if indices else 0
    if high >= len(palette):
        raise SheetError("%s uses index %d against a %d-entry palette" % (path, high, len(palette)))
    return width, height, indices, palette


def _unfilter(kind, line, previous, width, path):
    if kind == 0:
        return
    if kind == 1:
        for i in range(1, width):
            line[i] = (line[i] + line[i - 1]) & 0xFF
        return
    if kind == 2:
        for i in range(width):
            line[i] = (line[i] + previous[i]) & 0xFF
        return
    if kind == 3:
        for i in range(width):
            left = line[i - 1] if i else 0
            line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        return
    if kind == 4:
        for i in range(width):
            left = line[i - 1] if i else 0
            up = previous[i]
            upper_left = previous[i - 1] if i else 0
            estimate = left + up - upper_left
            da, db, dc = abs(estimate - left), abs(estimate - up), abs(estimate - upper_left)
            nearest = left if (da <= db and da <= dc) else (up if db <= dc else upper_left)
            line[i] = (line[i] + nearest) & 0xFF
        return
    raise SheetError("%s uses filter type %d" % (path, kind))


def write_indexed(path, width, height, indices, palette):
    if len(indices) != width * height:
        raise SheetError("%d indices against a %dx%d image" % (len(indices), width, height))
    if not 1 <= len(palette) <= 256:
        raise SheetError("%d palette entries" % len(palette))
    if max(indices) >= len(palette):
        raise SheetError("index %d against a %d-entry palette" % (max(indices), len(palette)))
    raw = b"".join(bytes([0]) + bytes(indices[row * width:(row + 1) * width])
                   for row in range(height))
    table = b"".join(bytes(entry) for entry in palette)
    blob = _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
    blob += _chunk(b"PLTE", table)
    blob += _chunk(b"IDAT", zlib.compress(raw, 9))
    blob += _chunk(b"IEND", b"")
    open(path, "wb").write(SIGNATURE + blob)


def _chunk(tag, body):
    return (struct.pack(">I", len(body)) + tag + body
            + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))


def sheet_shape(tiles, across=SHEET_TILES_ACROSS):
    if tiles < 1:
        raise SheetError("%d tiles" % tiles)
    rows = (tiles + across - 1) // across
    return across * TILE, rows * TILE


def sheet_of(payload, across=SHEET_TILES_ACROSS):
    if len(payload) % TILE_BYTES:
        raise SheetError("a %d-byte payload is not a whole number of %d-byte tiles"
                         % (len(payload), TILE_BYTES))
    tiles = len(payload) // TILE_BYTES
    width, height = sheet_shape(tiles, across)
    out = bytearray(width * height)
    for tile in range(tiles):
        x, y = (tile % across) * TILE, (tile // across) * TILE
        for row in range(TILE):
            source = tile * TILE_BYTES + row * TILE
            out[(y + row) * width + x:(y + row) * width + x + TILE] = payload[source:source + TILE]
    return width, height, out


def payload_of(indices, width, height, tiles, across=SHEET_TILES_ACROSS):
    expect = sheet_shape(tiles, across)
    if (width, height) != expect:
        raise SheetError("the sheet is %dx%d against %dx%d for %d tiles"
                         % (width, height, expect[0], expect[1], tiles))
    if len(indices) != width * height:
        raise SheetError("%d indices against a %dx%d sheet" % (len(indices), width, height))
    out = bytearray(tiles * TILE_BYTES)
    for tile in range(tiles):
        x, y = (tile % across) * TILE, (tile // across) * TILE
        for row in range(TILE):
            out[tile * TILE_BYTES + row * TILE:
                tile * TILE_BYTES + row * TILE + TILE] = \
                indices[(y + row) * width + x:(y + row) * width + x + TILE]
    return bytes(out)
