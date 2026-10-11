"""Colour-vision simulation, so an acceptance screenshot can be checked not assumed.

The maintainer of this project is red-green colourblind, and no surface may carry a
state in red against green. This tool converts a PNG the way a dichromat sees it,
which turns that rule into something a reviewer can look at and a test can assert.

THE MATRICES are Machado, Oliveira and Fernandes, "A Physiologically-based Model for
Simulation of Color Vision Deficiency", IEEE TVCG 15(6), 2009, Table 1, severity 1.0
(the dichromacy column). They were read from the authors' own page on 2026-10-10:
<https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html>

    protanopia    0.152286   1.052583  -0.204868
                  0.114503   0.786281   0.099216
                 -0.003882  -0.048116   1.051998
    deuteranopia  0.367322   0.860646  -0.227968
                  0.280085   0.672501   0.047413
                 -0.011820   0.042940   0.968881
    tritanopia    1.255528  -0.076749  -0.178779
                 -0.078411   0.930809   0.147602
                  0.004733   0.691367   0.303900

They are applied in LINEAR RGB, which is the space the model is defined in, so a
conversion is sRGB decode, matrix, sRGB encode.

EVERY ROW SUMS TO ONE, which is the property that makes this tool safe to reason
from: a neutral grey maps to itself under all three. It is also why this
application's neutral ladder survives the conversion untouched, and why a state that
must be readable has to be carried by a word, a glyph, a brightness or a shape
rather than by a hue. A test asserts that property, so a mistyped matrix fails.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtGui import QColor, QImage

#: The three dichromacies, keyed by the name a surface or a report uses.
MATRICES: dict[str, tuple[tuple[float, float, float], ...]] = {
    "protanopia": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}

KINDS: tuple[str, ...] = tuple(MATRICES)


def _to_linear(channel: float) -> float:
    """One sRGB channel, 0 to 1, as linear light."""
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _from_linear(channel: float) -> float:
    """One linear channel back to sRGB, clipped rather than wrapped."""
    if channel <= 0.0:
        return 0.0
    if channel >= 1.0:
        return 1.0
    return channel * 12.92 if channel <= 0.0031308 else 1.055 * channel ** (1 / 2.4) - 0.055


def convert_color(rgb: tuple[int, int, int], kind: str) -> tuple[int, int, int]:
    """One sRGB colour as a dichromat of `kind` sees it."""
    if kind not in MATRICES:
        raise KeyError(f"{kind!r} is not one of {KINDS}")
    linear = [_to_linear(channel / 255.0) for channel in rgb]
    rows = MATRICES[kind]
    out = [sum(rows[index][channel] * linear[channel] for channel in range(3))
           for index in range(3)]
    return tuple(round(_from_linear(channel) * 255.0) for channel in out)  # type: ignore[return-value]


def convert(image: QImage, kind: str) -> QImage:
    """The whole image, with each distinct colour converted once."""
    seen: dict[int, int] = {}
    out = QImage(image.size(), QImage.Format.Format_ARGB32)
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = image.pixel(x, y)
            mapped = seen.get(pixel)
            if mapped is None:
                colour = QColor.fromRgba(pixel)
                red, green, blue = convert_color((colour.red(), colour.green(),
                                                  colour.blue()), kind)
                mapped = QColor(red, green, blue, colour.alpha()).rgba()
                seen[pixel] = mapped
            out.setPixel(x, y, mapped)
    return out


def convert_file(path: Path, kind: str, out_dir: Path | None = None) -> Path:
    """Write `<stem>-<kind>.png` beside the source, or into `out_dir`."""
    image = QImage(str(path))
    if image.isNull():
        raise SystemExit(f"cannot read {path}")
    target = (out_dir or path.parent) / f"{path.stem}-{kind}.png"
    if not convert(image, kind).save(str(target)):
        raise SystemExit(f"cannot write {target}")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("images", nargs="+", help="PNG screenshots to convert")
    parser.add_argument("-k", "--kind", action="append", choices=KINDS,
                        help="a dichromacy; repeatable, and the default is all three")
    parser.add_argument("-o", "--out-dir", help="where to write, default beside the source")
    arguments = parser.parse_args(argv)
    kinds = tuple(arguments.kind) if arguments.kind else KINDS
    out_dir = Path(arguments.out_dir) if arguments.out_dir else None
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
    for name in arguments.images:
        path = Path(name)
        for kind in kinds:
            print(convert_file(path, kind, out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
