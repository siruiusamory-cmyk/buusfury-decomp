"""QA probe: is the Graphics tab's vertical demand a regression or pre-existing?

Run the same measurement against two checkouts (the baseline and the candidate)
and print what each one actually lays out, so "the Graphics tab needs more height
than a 900px window" is decided by measurement rather than by inference.

Usage:  python -m tools.qa.graphics_height_probe <worktree-root>
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication, QTabWidget  # noqa: E402

from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402

ROM = Path(
    os.environ.get(
        "DBZ_QA_ROM",
        r"<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba",
    )
)
ATLAS = Path(os.environ.get("DBZ_QA_ATLAS_DIR", r"<checkout>\build\atlas"))


def main() -> int:
    from tools.webfoot import cli
    from tools.webfoot.workbench import session as workbench_session

    resolver = lambda: ATLAS  # noqa: E731 - a one-line stand-in
    cli._default_atlas_directory = resolver
    workbench_session._default_atlas_directory = resolver

    app = QApplication.instance() or QApplication([])
    try:
        app.setOrganizationName("Webfoot")
        app.setApplicationName("Workbench")
    except Exception:  # noqa: BLE001 - probe only
        pass
    catalog = RomProfileCatalog.load("config/roms.yaml")
    session = Session()
    session.open_rom(ROM, catalog)
    window = MainWindow(session, catalog)
    window.show()
    window.resize(1440, 900)
    for _ in range(6):
        app.processEvents()
    tabs = window.findChild(QTabWidget)
    print(f"root: {ROOT}")
    for index in range(tabs.count()):
        tabs.setCurrentIndex(index)
        for _ in range(8):
            app.processEvents()
        pane = tabs.widget(index)
        content = pane.content() if hasattr(pane, "content") else pane
        print(
            f"  {tabs.tabText(index):<12} "
            f"pane {pane.width()}x{pane.height()} "
            f"pane-min {pane.minimumWidth()}x{pane.minimumHeight()} "
            f"content {content.width()}x{content.height()} "
            f"content-minHint {content.minimumSizeHint().width()}x"
            f"{content.minimumSizeHint().height()}"
        )
    print(f"  window minHint {window.minimumSizeHint().width()}x"
          f"{window.minimumSizeHint().height()}")
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
