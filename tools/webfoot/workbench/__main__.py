"""Entry point: `python -m tools.webfoot.workbench`.

Loads the ROM profile catalog the same way the CLI does (`cli.load_catalog`),
constructs a `Session` and the `MainWindow`, shows it, and runs the Qt loop.
Wiring "Open ROM" is Wave 2; here the catalog is just loaded and held so a later
`session.open_rom(path, catalog)` has it.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ..cli import load_catalog
from .app import MainWindow
from .session import Session


def main() -> int:
    app = QApplication(sys.argv)
    # Namespace AppConfigLocation so settings land in .../Local/Webfoot/Workbench,
    # not the shared generic .../Local/python dir.
    app.setOrganizationName("Webfoot")
    app.setApplicationName("Workbench")
    catalog = load_catalog(None)
    window = MainWindow(Session(), catalog)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
