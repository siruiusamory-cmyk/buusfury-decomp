"""QA tooling: one contact sheet from the REAL captures, for fast human review.

Assembles the candidate's captures into a labelled grid so the whole application
can be judged at a glance before opening the full-resolution PNGs. Every tile is a
real screenshot of the running application; **nothing here is generated artwork**
and no synthetic UI image is produced.

Run:

    python -m tools.qa.contact_sheet --dir <capture dir> --out <png>
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

TILE_W = 470
TILE_H = 300
COLS = 3
GUTTER = 10
LABEL_H = 18
_FONT_FILES = ("segoeui.ttf", "segoeuib.ttf")


def _load_fonts() -> None:
    root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in _FONT_FILES:
        candidate = root / name
        if candidate.is_file():
            QFontDatabase.addApplicationFont(str(candidate))


def _tile(path: Path) -> QPixmap:
    image = QImage(str(path))
    if image.isNull():
        empty = QPixmap(TILE_W, TILE_H)
        empty.fill(QColor("#20141A"))
        return empty
    scaled = QPixmap.fromImage(image).scaled(
        TILE_W,
        TILE_H,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    backed = QPixmap(TILE_W, TILE_H)
    backed.fill(QColor("#0A0E14"))
    painter = QPainter(backed)
    painter.drawPixmap(
        (TILE_W - scaled.width()) // 2, (TILE_H - scaled.height()) // 2, scaled
    )
    painter.end()
    return backed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    _load_fonts()

    names = sorted(path.name for path in args.dir.glob("*.png") if not path.name.startswith("contact"))
    rows = (len(names) + COLS - 1) // COLS
    width = GUTTER + COLS * (TILE_W + GUTTER)
    height = GUTTER + rows * (TILE_H + LABEL_H + GUTTER)
    sheet = QImage(width, height, QImage.Format.Format_RGB32)
    sheet.fill(QColor("#07090D"))

    painter = QPainter(sheet)
    font = QFont()
    font.setPointSize(8)
    font.setBold(True)
    painter.setFont(font)
    for index, name in enumerate(names):
        row, column = divmod(index, COLS)
        x = GUTTER + column * (TILE_W + GUTTER)
        y = GUTTER + row * (TILE_H + LABEL_H + GUTTER)
        painter.setPen(QColor("#F3C94B"))
        painter.drawText(
            QRect(x, y, TILE_W, LABEL_H),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            name[:-4],
        )
        painter.drawPixmap(x, y + LABEL_H, _tile(args.dir / name))
    painter.end()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(args.out), "PNG")
    print(f"wrote {args.out} ({width}x{height}) from {len(names)} real capture(s)")
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
