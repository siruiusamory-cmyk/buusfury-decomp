"""QA probe: is the Graphics tab's overflow real clipping or a real overlap?

The overlap probe reports the Graphics tab's `_anim_preview` sharing pixels with
its status line. This prints the exact parent chain and rectangles so the
question is decided by geometry rather than by inference.

Run: ``python -m tools.qa.graphics_geometry_probe``.
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

from PySide6.QtWidgets import QApplication  # noqa: E402

from tools.qa.visual_pass_capture import (  # noqa: E402
    DESKTOP,
    NARROW,
    Harness,
)


def main() -> int:
    app = QApplication.instance() or QApplication([])
    harness = Harness(Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()))
    for label, size in (("desktop", DESKTOP), ("narrow", NARROW)):
        harness.window.resize(size)
        harness.open_canonical()
        harness.show_editor("Graphics")
        harness.pump(20)
        harness.window.resize(size)
        harness.pump(20)
        tab = harness.editor("Graphics")
        print(f"[{label} {size.width()}x{size.height()}] content pane:")
        node = tab
        while node is not None:
            print(
                f"  {node.__class__.__name__}({node.objectName() or '-'}) "
                f"{node.width()}x{node.height()} "
                f"min {node.minimumSizeHint().width()}x{node.minimumSizeHint().height()} "
                f"vscroll={getattr(node, 'verticalScrollBar', lambda: None)() is not None}"
            )
            node = node.parentWidget()
        for name in ("_anim_preview", "_preview", "_status"):
            widget = getattr(tab, name)
            top = widget.mapTo(tab, widget.rect().topLeft())
            print(
                f"  {name}: local y={widget.y()} h={widget.height()} "
                f"-> pane y={top.y()}"
            )
        print()
    harness.window.close()
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
