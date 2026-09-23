"""QA probe: report the real canvas geometry of the two map surfaces.

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001` requires the map to dominate its
workspace. "Dominant" is measurable: the map's on-screen size against the
viewport it sits in. This prints that ratio for the Map Browser and the Map
workspace at desktop and narrow widths, so a fit that silently lands at a
fraction of the viewport is caught by a number rather than by eye.

Run: ``python -m tools.qa.canvas_probe``.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtCore import QSize  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tools.qa.visual_pass_capture import (  # noqa: E402
    DESKTOP,
    NARROW,
    PROOF_MAP,
    READ_ONLY_MAP,
    TAB_BROWSER,
    TAB_MAP,
    Harness,
)


def _dump(widget, depth: int = 0, limit: int = 6) -> None:
    """Print the geometry chain from a widget up to the window."""
    node = widget
    while node is not None and limit > 0:
        print(
            f"    {'  ' * depth}{node.__class__.__name__}"
            f"({node.objectName() or '-'}) {node.width()}x{node.height()}"
            f" min {node.minimumSizeHint().width()}x{node.minimumSizeHint().height()}"
        )
        node = node.parentWidget()
        depth += 1
        limit -= 1


def _report(label: str, canvas) -> None:
    scene = canvas.sceneRect()
    view = canvas.viewport().size()
    shown_w = scene.width() * canvas.transform().m11()
    shown_h = scene.height() * canvas.transform().m22()
    coverage = (shown_w * shown_h) / max(1, view.width() * view.height())
    window = canvas.window()
    print(
        f"  {label}: window {window.width()}x{window.height()}  "
        f"viewport {view.width()}x{view.height()}  "
        f"scene {scene.width():.0f}x{scene.height():.0f}  "
        f"shown {shown_w:.0f}x{shown_h:.0f}  scale {canvas.transform().m11():.3f}  "
        f"coverage {coverage * 100:.0f}%"
    )
    _dump(canvas)


def main() -> int:
    app = QApplication.instance() or QApplication([])
    harness = Harness(Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()))

    for label, size in (("desktop", DESKTOP), ("narrow", NARROW)):
        print(f"[{label} {size.width()}x{size.height()}]")
        harness.window.resize(size)
        harness.open_canonical()
        harness.pump(6)

        harness.show_tab(TAB_BROWSER)
        harness.select_map(PROOF_MAP)
        harness.pump(8)
        harness.window.resize(size)
        harness.pump(8)
        _report("browser / editable map", harness.browser._canvas)
        harness.select_map(READ_ONLY_MAP)
        harness.pump(8)
        _report("browser / read-only map", harness.browser._canvas)

        harness.show_tab(TAB_MAP)
        harness.pump(10)
        harness.window.resize(size)
        harness.pump(10)
        _report("map workspace       ", harness.tab(TAB_MAP)._canvas)
        print()

    harness.window.close()
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
