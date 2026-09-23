"""QA probe: report the real minimum footprint of each workbench tab."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtWidgets import QApplication, QTabWidget  # noqa: E402

from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.workbench import theme  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


def main() -> int:
    app = QApplication.instance() or QApplication([])
    theme.apply_app_theme(app)
    window = MainWindow(Session(), RomProfileCatalog.load("config/roms.yaml"))
    window.resize(1100, 720)
    tabs = window.findChild(QTabWidget)
    print("tabs:", tabs.count(), [tabs.tabText(i) for i in range(tabs.count())])
    print("window at request 1100x720 ->", window.width(), "x", window.height())
    print(
        "window minimumSizeHint ->",
        window.minimumSizeHint().width(),
        "x",
        window.minimumSizeHint().height(),
    )
    for index in range(tabs.count()):
        tabs.setCurrentIndex(index)
        app.processEvents()
        pane = tabs.currentWidget()
        print(
            f"  [{index}] {tabs.tabText(index):<12} pane minimumSizeHint "
            f"{pane.minimumSizeHint().width()} x {pane.minimumSizeHint().height()}"
        )
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
