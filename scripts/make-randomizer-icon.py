"""Render the project mark into the Windows icon the released tools carry.

    python scripts/make-randomizer-icon.py

Reads ``public/favicon.svg`` - the same mark the public site uses - and writes
``scripts/randomizer.ico``, which both spec templates pass to ``EXE(icon=...)``.
The icon is a tracked build input, so this file is what makes it reproducible:
without it the committed ``.ico`` would be an unexplained binary.

The format, and why it is written by hand
-----------------------------------------

Windows reads an ``.ico`` as a directory of images, each independently encoded.
This writes the small sizes as uncompressed 32-bit DIB entries (a
``BITMAPINFOHEADER``, bottom-up BGRA rows, then the 1-bit AND mask) and the
256 px entry as PNG, which is the shape Windows expects and the smallest of the
two encodings at that size. Pillow would do the conversion, but it is not a
dependency of this project and adding one so a build can emit a 19 kB asset is
not a trade worth making; Qt already ships the SVG renderer.

Run it only when the mark in ``public/favicon.svg`` changes, and commit the
resulting ``.ico`` in the same change.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

#: Sizes written as uncompressed DIB entries. 16 and 32 px are what Windows
#: actually draws in a file list and a taskbar; 48 px covers the large-icon view.
DIB_SIZES = (16, 32, 48)

#: The one size written as PNG. Windows uses it for the extra-large icon view,
#: and an uncompressed DIB at 256 px is 262 kB against a few kB for the PNG.
PNG_SIZE = 256

#: The byte a 256 px entry carries in the directory, because the field is a
#: single byte and 256 does not fit in one.
_LARGE_DIMENSION = 0

_ICON_DIRECTORY_HEADER = "<HHH"
_ICON_DIRECTORY_ENTRY = "<BBBBHHII"
_BITMAPINFOHEADER = "<IiiHHIIiiII"


def render_mark(svg: bytes, size: int) -> QImage:
    """The mark at one square size, on a transparent background."""
    renderer = QSvgRenderer(QByteArray(svg))
    if not renderer.isValid():
        raise ValueError("public/favicon.svg did not load as SVG")
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter)
    painter.end()
    return image


def png_image(image: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise ValueError("Qt could not encode the rendered mark as PNG")
    return bytes(buffer.data())


def dib_image(image: QImage) -> bytes:
    """One ICONIMAGE: a 32-bit bottom-up DIB followed by its AND mask.

    The alpha channel carries the shape, so the AND mask is all zeroes; it is
    still written because the header declares a mask and Windows reads one.
    """
    size = image.width()
    header = struct.pack(_BITMAPINFOHEADER, 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    rows = bytearray()
    for y in range(size - 1, -1, -1):
        for x in range(size):
            colour = image.pixelColor(x, y)
            rows += bytes((colour.blue(), colour.green(), colour.red(), colour.alpha()))
    mask_stride = ((size + 31) // 32) * 4
    return header + bytes(rows) + bytes(mask_stride * size)


def build_icon(svg: bytes) -> bytes:
    """The complete ``.ico``: header, one directory entry per image, payloads."""
    images = [(size, dib_image(render_mark(svg, size))) for size in DIB_SIZES]
    images.append((PNG_SIZE, png_image(render_mark(svg, PNG_SIZE))))

    directory = struct.pack(_ICON_DIRECTORY_HEADER, 0, 1, len(images))
    entries = bytearray()
    payload = bytearray()
    offset = len(directory) + 16 * len(images)
    for size, data in images:
        dimension = _LARGE_DIMENSION if size >= 256 else size
        entries += struct.pack(
            _ICON_DIRECTORY_ENTRY, dimension, dimension, 0, 0, 1, 32, len(data), offset
        )
        offset += len(data)
        payload += data
    return bytes(directory + entries + payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="make-randomizer-icon.py",
        description="Render public/favicon.svg into scripts/randomizer.ico.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: the parent of this script's directory)",
    )
    arguments = parser.parse_args(argv)

    source = arguments.root / "public" / "favicon.svg"
    target = arguments.root / "scripts" / "randomizer.ico"
    if not source.is_file():
        print(f"error: no mark to render at {source}", file=sys.stderr)
        return 2

    # QGuiApplication must exist before anything paints, and it must exist only
    # once per process. The mark is rendered offscreen, so this works on a machine
    # with no display; a caller who has a real platform plugin set keeps it.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    application = QGuiApplication.instance() or QGuiApplication([])
    assert application is not None
    data = build_icon(source.read_bytes())
    target.write_bytes(data)
    print(f"wrote {target} ({len(data)} bytes, {len(DIB_SIZES) + 1} sizes) from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
