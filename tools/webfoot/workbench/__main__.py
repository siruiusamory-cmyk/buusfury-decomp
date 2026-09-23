"""Entry point: `python -m tools.webfoot.workbench`.

Loads the ROM profile catalog the same way the CLI does (`cli.load_catalog`),
constructs a `Session` and the `MainWindow`, shows it, and runs the Qt loop.

The one application-wide theme is applied here and nowhere else:
`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001` moved the palette out of a per-tab
stylesheet and into `theme.apply_app_theme`, so every surface resolves the same
colour, radius, spacing and type roles.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ..cli import load_catalog
from . import theme
from .app import MainWindow
from .session import Session


def main() -> int:
    app = QApplication(sys.argv)
    # Namespace AppConfigLocation so settings land in .../Local/Webfoot/Workbench,
    # not the shared generic .../Local/python dir.
    app.setOrganizationName("Webfoot")
    app.setApplicationName("Workbench")
    theme.apply_app_theme(app)
    catalog = load_catalog(None)
    window = MainWindow(Session(), catalog)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
