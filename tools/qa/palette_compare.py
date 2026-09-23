"""QA tooling: the palette / colour comparison sheet.

Places two REAL captures of the same state side by side - the candidate as it was
before the colour correction, and the colour-corrected candidate - so the change in
surface value, accent hue and palette density can be judged directly.

Every tile is a real screenshot of the running application. **No generated
artwork, no mockup and no synthetic UI image is produced anywhere in this tool.**

Run:

    python -m tools.qa.palette_compare --old <dir> --new <dir> --out <png>
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtCore import QRect, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QColor,
    QFont,
    QFontDatabase,
    QImage,
    QPainter,
    QPixmap,
)

#: The states the human correction asked to compare, with the reason each matters.
PANELS: list[tuple[str, str, str]] = [
    ("01-shell-no-rom", "Shell", "one shell band, not stacked black bars"),
    ("02-maps-browse", "Maps / Browse", "map dominance and neutral row selection"),
    ("03-maps-layout", "Maps / Layout", "accent restraint around the canvas"),
    ("11-graphics-empty", "Graphics / empty", "the concise empty state"),
    ("12-graphics-selected", "Graphics / selected", "one preview, compact palette"),
    ("10-inspector-dialogue", "Inspector", "text roles and value readability"),
    ("16-narrow-shell", "Narrow Maps", "the narrow window at 1100x720"),
]

TILE_W = 640
TILE_H = 400
LABEL_H = 18
GUTTER = 12
ROW_GAP = 10
_HEADER_H = 30
_FONT_FILES = ("segoeui.ttf", "segoeuib.ttf")


def _load_fonts() -> None:
    root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in _FONT_FILES:
        candidate = root / name
        if candidate.is_file():
            QFontDatabase.addApplicationFont(str(candidate))


def _tile(directory: Path, name: str) -> QPixmap:
    path = directory / f"{name}.png"
    image = QImage(str(path))
    backed = QPixmap(TILE_W, TILE_H)
    backed.fill(QColor("#05070a"))
    if image.isNull():
        return backed
    scaled = QPixmap.fromImage(image).scaled(
        TILE_W,
        TILE_H,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    painter = QPainter(backed)
    painter.drawPixmap(
        (TILE_W - scaled.width()) // 2, (TILE_H - scaled.height()) // 2, scaled
    )
    painter.end()
    return backed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", type=Path, required=True, help="pre-correction captures")
    parser.add_argument("--new", type=Path, required=True, help="colour-corrected captures")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    _load_fonts()

    width = GUTTER + 2 * (TILE_W + GUTTER)
    row_height = TILE_H + LABEL_H + ROW_GAP + _HEADER_H
    height = GUTTER + row_height * len(PANELS)
    sheet = QImage(width, height, QImage.Format.Format_RGB32)
    sheet.fill(QColor("#05070a"))

    painter = QPainter(sheet)
    title = QFont()
    title.setPointSize(10)
    title.setBold(True)
    body = QFont()
    body.setPointSize(8)
    note = QFont()
    note.setPointSize(7)

    for row, (name, label, why) in enumerate(PANELS):
        top = GUTTER + row * row_height
        painter.setFont(title)
        painter.setPen(QColor("#f0c46d"))
        painter.drawText(
            QRect(GUTTER, top, width - 2 * GUTTER, _HEADER_H - 12),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{row + 1}. {label}",
        )
        painter.setFont(note)
        painter.setPen(QColor("#aeb9c2"))
        painter.drawText(
            QRect(GUTTER, top + _HEADER_H - 13, width - 2 * GUTTER, 13),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            why,
        )
        painter.setFont(body)
        tile_top = top + _HEADER_H
        for column, (directory, caption) in enumerate(
            ((args.old, "BEFORE COLOUR CORRECTION"), (args.new, "COLOUR-CORRECTED CANDIDATE"))
        ):
            x = GUTTER + column * (TILE_W + GUTTER)
            painter.setPen(
                QColor("#7e8d9a") if column == 0 else QColor("#93c67c")
            )
            painter.drawText(
                QRect(x, tile_top, TILE_W, LABEL_H),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                caption,
            )
            painter.drawPixmap(x, tile_top + LABEL_H, _tile(directory, name))
    painter.end()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(args.out), "PNG")
    print(f"wrote {args.out} ({width}x{height}) from {len(PANELS)} real state pair(s)")
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
