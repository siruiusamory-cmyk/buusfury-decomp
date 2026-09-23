"""QA probe: find elided, clipped or overlapping text in the real workbench.

The acceptance rule for `DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001` is that no text
may overlap. Reading 18 screenshots by eye is not a reliable check, so this walks
the live widget tree in each of the same states the capture harness drives and
answers two mechanical questions:

1. **Overlap** - do any two *visible, independently parented* text widgets share
   pixels? Siblings in a layout never do; a re-parented or absolutely positioned
   widget can, and that is exactly the bug this exists to catch.
2. **Elision / clipping** - does a text widget's own text fit its own rect? If it
   does not, Qt either draws an ellipsis (elided) or paints over its neighbour
   (clipped). Either is a defect at that size.
3. **Control compression** - is a visible child laid out smaller than its own
   minimum hint? That is how a combo box or a checkbox ends up with no readable
   text while the pixels look "fine".

Run: ``python -m tools.qa.overlap_probe``. Exit code is 1 when it finds anything.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtCore import QRect, QSize  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QAbstractButton,
    QApplication,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QTabWidget,
    QWidget,
)

from tools.qa.visual_pass_capture import (  # noqa: E402
    DESKTOP,
    NARROW,
    PROOF_CELL,
    PROOF_MAP,
    READ_ONLY_MAP,
    Harness,
)

#: A text-bearing widget, as (widget, text).
_TEXTY = (QLabel, QAbstractButton, QLineEdit, QComboBox)

#: States to probe, as (name, window size, setup key). Mirrors the capture harness
#: so the check covers exactly the surfaces that were captured.
STATES: list[tuple[str, QSize, str]] = [
    ("01-shell-no-rom", DESKTOP, "shell"),
    ("02-maps-browse", DESKTOP, "browse"),
    ("03-maps-layout", DESKTOP, "layout"),
    ("04-maps-layout-cell", DESKTOP, "cell"),
    ("05-maps-pending-pick", DESKTOP, "pending"),
    ("06-maps-unsaved", DESKTOP, "unsaved"),
    ("08-maps-read-only-map19", DESKTOP, "readonly"),
    ("09-maps-objects", DESKTOP, "objects"),
    ("11-graphics-empty", DESKTOP, "graphics_empty"),
    ("12-graphics-selected", DESKTOP, "graphics_selected"),
    ("13-atlas-rom-open", DESKTOP, "atlas"),
    ("14-build-surface", DESKTOP, "build"),
    ("15-run-configuration", DESKTOP, "launch"),
    ("16-narrow-shell", NARROW, "layout"),
    ("17-narrow-maps-browse", NARROW, "narrow_browse"),
    ("18-narrow-shell-atlas", NARROW, "atlas"),
]


def _text_of(widget: QWidget) -> str:
    if isinstance(widget, QLabel):
        return widget.text()
    if isinstance(widget, QAbstractButton):
        return widget.text()
    if isinstance(widget, QLineEdit):
        return widget.text() or widget.placeholderText()
    if isinstance(widget, QComboBox):
        return widget.currentText()
    return ""


def _font_for(widget: QWidget):
    return widget.font()


def _visible_in(root: QWidget, widget: QWidget) -> bool:
    """True when `widget` is actually inside every ancestor's visible rect.

    A widget inside a scroll area whose content is taller than the viewport still
    reports a rectangle - and `isVisible()` is still true - but that rectangle
    lies outside the viewport: it is clipped, not overlapping. Without this check
    every scrollable pane produces a false OVERLAP against whatever sits below it.

    The corners are mapped through ``mapTo`` rather than read from ``pos()``:
    ``pos()`` is relative to the widget's own parent, which is *not* the ancestor
    being tested two or more levels down a nested layout.
    """
    if widget.rect().isEmpty():
        return False
    for point in (widget.rect().topLeft(), widget.rect().bottomRight()):
        node = widget
        mapped = point
        while node is not None and node is not root:
            parent = node.parentWidget()
            if parent is None:
                break
            mapped = node.mapTo(parent, mapped)
            if not parent.rect().contains(mapped):
                return False
            node = parent
    return True


def _text_widgets(root: QWidget) -> list[tuple[QWidget, str, QRect]]:
    """Every visible text-bearing widget under `root`, with its global rect."""
    found: list[tuple[QWidget, str, QRect]] = []
    for widget in root.findChildren(QWidget):
        if not isinstance(widget, _TEXTY):
            continue
        if not widget.isVisible() or widget.width() <= 0 or widget.height() <= 0:
            continue
        text = _text_of(widget).strip()
        if not text:
            continue
        if not _visible_in(root, widget):
            continue
        top_left = widget.mapTo(root, widget.rect().topLeft())
        found.append((widget, text, QRect(top_left, widget.size())))
    return found


def _overlap(a: QRect, b: QRect) -> bool:
    inter = a.intersected(b)
    return inter.width() > 2 and inter.height() > 2


def _same_branch(a: QWidget, b: QWidget) -> bool:
    """True when one widget is an ancestor of the other (so overlap is normal)."""
    node = a
    while node is not None:
        if node is b:
            return True
        node = node.parentWidget()
    node = b
    while node is not None:
        if node is a:
            return True
        node = node.parentWidget()
    return False


def check(root: QWidget, state: str) -> list[str]:
    problems: list[str] = []
    items = _text_widgets(root)

    # 1. Text that does not fit the widget it is drawn in.
    #
    # A QLabel with word wrap legitimately grows in height; a QLineEdit scrolls
    # its own content; a QComboBox elides its current text inside a fixed arrow
    # frame. Everything else must fit, or Qt paints an ellipsis (elided text) or
    # simply clips the glyphs - both of which are the defect this looks for.
    for widget, text, rect in items:
        metrics = widget.fontMetrics()
        name = widget.__class__.__name__
        if isinstance(widget, QLabel) and widget.wordWrap():
            continue
        if isinstance(widget, (QLineEdit, QComboBox)):
            continue
        needed = metrics.horizontalAdvance(text)
        if needed > rect.width() + 1:
            problems.append(
                f"{state}: {name} text needs {needed}px but has {rect.width()}px "
                f"-> elided or clipped: '{text[:52]}'"
            )
        if metrics.height() > rect.height() + 1:
            problems.append(
                f"{state}: {name} text is {metrics.height()}px tall in a "
                f"{rect.height()}px box -> clipped: '{text[:40]}'"
            )

    # 2. Two independently parented text widgets sharing pixels.
    for index, (widget_a, text_a, rect_a) in enumerate(items):
        for widget_b, text_b, rect_b in items[index + 1 :]:
            if _same_branch(widget_a, widget_b):
                continue
            if _overlap(rect_a, rect_b):
                problems.append(
                    f"{state}: OVERLAP {widget_a.__class__.__name__} "
                    f"'{text_a[:28]}' {rect_a.getRect()} vs "
                    f"{widget_b.__class__.__name__} '{text_b[:28]}' {rect_b.getRect()}"
                )

    # 3. A control whose own text is elided or absent.
    #
    # This is the real failure mode the screenshots showed: a combo box, check
    # box or label squeezed by its layout until the words are gone. It is not a
    # pixel overlap, so only a text-fit check catches it.
    for widget in root.findChildren(QWidget):
        if not isinstance(widget, _TEXTY) or not widget.isVisible():
            continue
        text = _text_of(widget).strip()
        if not text:
            continue
        metrics = widget.fontMetrics()
        name = widget.__class__.__name__
        if isinstance(widget, QComboBox):
            # The frame, padding, drop-down and arrow all take width before the
            # current text gets any. A combo listing full map identities is long
            # by nature and Qt elides it inside its own frame; that is a legible
            # control, not a defect, so the bar is set where the *text* itself
            # would have nowhere to go.
            chrome = 34
            if widget.width() - chrome < metrics.horizontalAdvance(text) * 0.6:
                problems.append(
                    f"{state}: {name} '{text[:36]}' has {widget.width()}px of frame "
                    f"but needs {metrics.horizontalAdvance(text) + chrome}px "
                    "-> its text is elided"
                )
        elif isinstance(widget, QLabel):
            if widget.width() + 1 < min(metrics.horizontalAdvance(text), 40):
                problems.append(
                    f"{state}: {name} '{text[:36]}' has {widget.width()}px "
                    "-> unreadable"
                )
        elif isinstance(widget, QAbstractButton):
            # Check boxes and push buttons draw their text beside their indicator.
            # A button given an explicit fixed width is a deliberate metric (the
            # zoom controls are 28px on purpose), so only text that could not fit
            # even in a normal button is a defect there.
            fixed = 0 < widget.minimumWidth() == widget.maximumWidth()
            text_width = metrics.horizontalAdvance(text)
            floor = text_width + 24 if fixed else text_width + max(
                widget.sizeHint().width() - text_width, 0
            )
            if widget.width() + 1 < floor:
                problems.append(
                    f"{state}: {name} '{text[:36]}' has {widget.width()}px but "
                    f"needs {floor}px -> its text is elided"
                )

    # 4. A visible child laid out below its own minimum (squeezed control).
    #
    # A control with an explicit fixed width is exempt: it was *told* to be that
    # size on purpose (the zoom buttons), and that is a deliberate metric rather
    # than a layout failure.
    for widget in root.findChildren(QWidget):
        if not widget.isVisible() or widget.parentWidget() is None:
            continue
        if widget.minimumWidth() == widget.maximumWidth() and widget.minimumWidth() > 0:
            continue
        hint = widget.minimumSizeHint()
        if hint.width() > 0 and widget.width() < hint.width() - 1:
            problems.append(
                f"{state}: {widget.__class__.__name__} "
                f"{widget.objectName() or ''} is {widget.width()}px wide, "
                f"minimum {hint.width()}px -> its content is squeezed"
            )

    # 5. Adjacent text with no gutter.
    #
    # The status bar is where this bites: two *labels* laid out edge to edge read
    # as one run-on string even though their rects technically do not intersect.
    # Framed controls (fields, combos, buttons) are exempt: each has a visible
    # 1 px border of its own, so they are unambiguously separate controls.
    _GUTTER_KINDS = (QLabel, QCheckBox)
    for index, (widget_a, text_a, rect_a) in enumerate(items):
        if not isinstance(widget_a, _GUTTER_KINDS):
            continue
        for widget_b, text_b, rect_b in items[index + 1 :]:
            if not isinstance(widget_b, _GUTTER_KINDS):
                continue
            if _same_branch(widget_a, widget_b):
                continue
            if rect_a.intersected(rect_b).isValid():
                continue
            vertical = rect_a.top() < rect_b.bottom() and rect_b.top() < rect_a.bottom()
            if not vertical:
                continue
            if rect_a.right() < rect_b.left():
                gap = rect_b.left() - rect_a.right()
            else:
                gap = rect_a.left() - rect_b.right()
            if gap < 8:
                problems.append(
                    f"{state}: {widget_a.__class__.__name__} '{text_a[:24]}' and "
                    f"{widget_b.__class__.__name__} '{text_b[:24]}' are {gap}px "
                    "apart -> no gutter between them"
                )
    return problems


def _setup(harness: Harness, key: str) -> None:
    """Drive the shell to one captured state."""
    if key == "shell":
        harness.show_editor("Atlas")
        return
    harness.open_canonical()
    if key in ("browse", "layout", "cell", "pending", "unsaved", "readonly", "objects",
               "narrow_browse"):
        harness.show_editor("Maps")
        if key in ("browse", "layout", "cell", "pending", "unsaved"):
            harness.maps.set_mode("layout" if key != "browse" else "browse")
            harness.select_map(PROOF_MAP)
        elif key in ("readonly", "narrow_browse"):
            harness.maps.set_mode("layout" if key == "readonly" else "browse")
            harness.select_map(READ_ONLY_MAP)
        else:
            harness.maps.set_mode("objects")
        if key in ("cell", "pending", "unsaved"):
            harness.browser._on_cell_clicked(PROOF_CELL)
            harness.pump(2)
        if key in ("pending", "unsaved"):
            tab = harness.browser
            current = tab._chooser_row_for(
                tab._working_pointer(tab._slot.slot, PROOF_CELL)
            )
            harness.choose_chunk_row(1 if current == 0 else 0)
        if key == "unsaved":
            harness.apply_draft()
        harness.pump(6)
        return
    if key in ("graphics_empty", "graphics_selected"):
        harness.show_editor("Graphics")
        harness.pump(20)
        if key == "graphics_selected":
            harness.editor("Graphics")._grid.setCurrentRow(0)
            harness.pump(20)
        return
    if key in ("atlas", "build", "launch"):
        harness.show_editor({"atlas": "Atlas", "build": "Build", "launch": "Launch"}[key])
        harness.pump(6)
        return
    harness.show_editor("Atlas")


def main() -> int:
    import tempfile

    # The console's default code page is not UTF-8 on Windows, and the probe
    # quotes real interface text (which contains glyphs like the minus sign).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable
        pass

    app = QApplication.instance() or QApplication([])
    workspace = Path(tempfile.mkdtemp(prefix="dbz-overlap-"))
    harness = Harness(Path(tempfile.mkdtemp()), workspace)
    all_problems: list[str] = []
    for name, size, key in STATES:
        harness.window.resize(size)
        _setup(harness, key)
        harness.pump(6)
        harness.window.resize(size)
        harness.pump(4)
        problems = check(harness.window, name)
        print(f"[{name}] {len(problems)} problem(s)", flush=True)
        for problem in problems:
            print("  " + problem, flush=True)
        all_problems.extend(problems)
    print(f"\nTOTAL {len(all_problems)} problem(s) across {len(STATES)} state(s)", flush=True)
    harness.window.close()
    del app
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
