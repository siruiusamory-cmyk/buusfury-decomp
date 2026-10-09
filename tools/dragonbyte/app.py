"""The application entry point: one flag, one window, no other logic.

``--version`` prints the product identity and exits, which is the one thing that
must work with no display and no window. Otherwise the application builds its
``QApplication``, takes its name and version from the identity authority, applies
the one theme, and shows the shell. Nothing is loaded here: the session opens an
image only when a user asks for one.
"""

from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

from tools.webfoot.release_identity import release_identity

from . import theme
from .session import Session
from .shell import Shell


def configuration_directory() -> Path:
    """Where this application keeps its per-user settings.

    Qt's own per-user location, which is outside the repository and outside any
    project. Falls back to the user's home only when Qt cannot name a location.
    """
    location = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
    return Path(location) if location else Path.home() / ".dragonbyte-z"


def main(argv: list[str] | None = None) -> int:
    """Run the application, or report the version and return."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    identity = release_identity()
    if "--version" in arguments:
        print(identity.display)
        return 0

    app = QApplication(sys.argv if argv is None else [sys.argv[0], *arguments])
    app.setApplicationName(identity.product_name)
    app.setApplicationVersion(identity.version)
    theme.apply_theme(app)
    window = Shell(Session(), configuration_directory())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
