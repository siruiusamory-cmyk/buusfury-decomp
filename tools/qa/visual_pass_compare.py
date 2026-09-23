"""QA tooling: build a side-by-side BEFORE/AFTER sheet from capture directories.

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001` requires a side-by-side before/after
comparison of the *real* application. Both directories must contain the same
state file names, produced by `tools.qa.visual_pass_capture`.

Each output sheet is one state per row: BEFORE on the left, AFTER on the right,
a labelled caption bar above each image. Sheets are written as PNGs into the
comparison directory, plus a single `index.md` listing them.

Run:

    python -m tools.qa.visual_pass_compare --before <dir> --after <dir> --out <dir>
"""

from __future__ import annotations

import argparse
import html
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

#: Sheet geometry. Each side is scaled to fit a fixed cell so a 1440-wide window
#: and a 1100-wide narrow capture can be compared in the same row.
CELL_W = 900
CELL_H = 620
GUTTER = 12
CAPTION_H = 26
#: Longest edge of a detail crop, when the state has one worth zooming.
DETAIL_MAX = 420

_LABELS = {
    "01-shell-no-rom": (
        "1. Application shell",
        "Menu bar -> one compact editor strip -> the active editor. The four "
        "primary editors are named once, beside the project actions.",
    ),
    "02-maps-browse": (
        "2. Maps / Browse",
        "One Maps editor. Browse mode: map collection, dominant canvas, contextual "
        "inspector, compact status.",
    ),
    "03-maps-layout": (
        "3. Maps / Layout",
        "Layout mode: the chunk palette is adjacent to the map and the edit state "
        "is stated in words.",
    ),
    "04-maps-layout-cell": (
        "4. Maps / cell selected",
        "The selected 256x256 cell is marked on the canvas and named in the "
        "inspector.",
    ),
    "05-maps-pending-pick": (
        "5. Maps / pending pick",
        "A chooser pick previews immediately in memory; the change is uncommitted.",
    ),
    "06-maps-unsaved": (
        "6. Maps / unsaved edit",
        "Applied but unwritten: glyph plus word in the inspector, glyph on the map "
        "row, count in the title and the status bar.",
    ),
    "07-maps-derivative-read-only": (
        "7. Maps / derivative reopen",
        "A real Save As derivative: browsable and rendered, editing unavailable "
        "with the reason stated, no giant badge and no dimming.",
    ),
    "08-maps-read-only-map19": (
        "8. Maps / unsupported map",
        "Map 19's terrain field: editing controls are absent, the reason is named, "
        "the map stays fully viewable.",
    ),
    "09-maps-objects": (
        "9. Maps / Objects",
        "Placement authoring: move a placement, clone one into an authored NPC, "
        "open its detailed editor. Undo/redo are real.",
    ),
    "10-inspector-dialogue": (
        "10. Inspector / dialogue",
        "Game text first, then the editing context, then the state; raw handles "
        "stay available in technical type.",
    ),
    "11-graphics-empty": (
        "11. Graphics / nothing selected",
        "One concise empty state. No empty preview box, no '-' rows, no disabled "
        "actions, no empty animation pane.",
    ),
    "12-graphics-selected": (
        "12. Graphics / sprite selected",
        "Selection decides what appears: preview, size, frames, characters, export, "
        "and the animation stepper only because a character uses it.",
    ),
    "13-atlas-rom-open": (
        "13. Atlas",
        "Image identity and profile stated where the work starts.",
    ),
    "14-build-surface": (
        "14. Build (project action)",
        "Build is an action, not a workspace. Its report and its configuration live "
        "in one surface opened from the action that uses them.",
    ),
    "15-run-configuration": (
        "15. Run configuration (project action)",
        "Run starts an emulator on a file that already exists; the tab says so.",
    ),
    "16-narrow-shell": (
        "16. Narrow shell, Maps / Layout",
        "The window can actually get narrow; panes shrink and the canvas takes the "
        "strain.",
    ),
    "17-narrow-maps-browse": (
        "17. Narrow shell, Maps / Browse",
        "A read-only map at the narrow width: still fully browsable.",
    ),
    "18-narrow-shell-atlas": (
        "18. Narrow shell, Atlas",
        "The narrow state on a non-map editor.",
    ),
}

_FONT_FILES = ("segoeui.ttf", "segoeuib.ttf", "consola.ttf")


def _load_fonts() -> None:
    root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in _FONT_FILES:
        candidate = root / name
        if candidate.is_file():
            QFontDatabase.addApplicationFont(str(candidate))


def _scaled(path: Path, width: int, height: int) -> QPixmap:
    image = QImage(str(path))
    if image.isNull():
        missing = QPixmap(width, height)
        missing.fill(QColor("#20141A"))
        painter = QPainter(missing)
        painter.setPen(QColor("#E4635A"))
        painter.drawText(missing.rect(), Qt.AlignmentFlag.AlignCenter, f"missing: {path.name}")
        painter.end()
        return missing
    pixmap = QPixmap.fromImage(image).scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    backed = QPixmap(width, height)
    backed.fill(QColor("#0A0E14"))
    painter = QPainter(backed)
    painter.drawPixmap(
        (width - pixmap.width()) // 2, (height - pixmap.height()) // 2, pixmap
    )
    painter.end()
    return backed


def _sheet(name: str, before: Path, after: Path, note: str) -> QImage:
    caption = _LABELS.get(name, (name, ""))[0]
    width = GUTTER * 3 + CELL_W * 2
    height = CAPTION_H + CELL_H + 78
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor("#0A0E14"))

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

    title_font = QFont()
    title_font.setBold(True)
    title_font.setPointSize(11)
    painter.setFont(title_font)
    painter.setPen(QColor("#E8ECF1"))
    painter.drawText(
        QRect(GUTTER, 4, width - GUTTER * 2, CAPTION_H),
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        f"{caption}",
    )

    label_font = QFont()
    label_font.setPointSize(8)
    label_font.setBold(True)
    for index, (text, pixmap_path, accent) in enumerate(
        (("BEFORE", before, "#96A3B4"), ("AFTER", after, "#F3C94B"))
    ):
        x = GUTTER + index * (CELL_W + GUTTER)
        painter.setFont(label_font)
        painter.setPen(QColor(accent))
        painter.drawText(
            QRect(x, CAPTION_H, CELL_W, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text,
        )
        painter.drawPixmap(
            x, CAPTION_H + 20, _scaled(pixmap_path, CELL_W, CELL_H)
        )

    painter.setFont(label_font)
    painter.setPen(QColor("#96A3B4"))
    painter.drawText(
        QRect(GUTTER, CAPTION_H + CELL_H + 24, width - GUTTER * 2, 50),
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
        note,
    )
    painter.end()
    return image


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    _load_fonts()
    args.out.mkdir(parents=True, exist_ok=True)

    names = sorted(path.name for path in args.before.glob("*.png"))
    after_names = {path.name for path in args.after.glob("*.png")}
    rows: list[str] = ["# Before / after comparison", ""]
    written = 0
    for name in names:
        if name not in after_names:
            print(f"  no AFTER capture for {name}; skipped")
            continue
        note = _LABELS.get(name[:-4], (name, ""))[1]
        image = _sheet(name[:-4], args.before / name, args.after / name, note)
        target = args.out / f"compare-{name}"
        image.save(str(target), "PNG")
        rows.append(f"## {_LABELS.get(name[:-4], (name, ''))[0]}")
        rows.append("")
        rows.append(f"![{name}]({target.name})")
        rows.append("")
        rows.append(html.escape(note))
        rows.append("")
        written += 1
        print(f"  wrote {target.name}")
    (args.out / "index.md").write_text("\n".join(rows), encoding="utf-8")
    print(f"\n{written} comparison sheet(s) plus index.md in {args.out}")
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
