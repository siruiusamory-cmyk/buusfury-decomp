"""Start-up: the arguments, the theme, the session and the window.

The application name comes from `identity`, so the settings directory, the
window title and the version resource all name the same product.
"""

from __future__ import annotations

import argparse
import os
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from tools.webfoot import textedit

from . import project as project_file, settings, theme
from .identity import PRODUCT_NAME, PRODUCT_VERSION
from .session import open_image
from .shell import Shell


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.buufury_text",
                                     description=f"{PRODUCT_NAME} {PRODUCT_VERSION}")
    parser.add_argument("rom", nargs="?", help="the image to open")
    parser.add_argument("--project", help="a saved edit list to open with the image")
    parser.add_argument("--canonical", help="the original game image, for the retail comparison")
    parser.add_argument("--smoke", action="store_true",
                        help="build the window, walk every pane, close")
    parser.add_argument("--version", action="version",
                        version=f"{PRODUCT_NAME} {PRODUCT_VERSION}")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.smoke:
        # The packaged smoke run has no display, and nothing here needs one.
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    application = QApplication.instance() or QApplication(
        sys.argv if argv is None else [sys.argv[0], *argv])
    application.setApplicationName(PRODUCT_NAME)
    application.setApplicationDisplayName(PRODUCT_NAME)
    application.setOrganizationName("Webfoot")
    stored = settings.load()
    # The mode as stored, not the mode it resolved to, so "follow the system"
    # survives a round trip through the settings file.
    mode = str(stored.get("theme", theme.MODE_SYSTEM))
    applied = theme.apply_theme(application, mode)
    session = None
    if arguments.rom:
        try:
            saved = project_file.load(arguments.project) if arguments.project else None
            session = open_image(arguments.rom, canonical=arguments.canonical, project=saved)
        except (textedit.TextEditError, project_file.ProjectFileError, OSError) as error:
            QMessageBox.critical(None, PRODUCT_NAME, str(error))
            return 2
    window = Shell(session, applied, mode)
    window.show()
    if arguments.smoke:
        window.walk_panes()
        window.close()
        return 0
    return application.exec()
