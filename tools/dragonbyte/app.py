"""The application entry point: two headless flags, one window, no other logic.

``--version`` prints the product identity and exits, which is the one thing that
must work with no display and no window. ``--smoke`` drives one real startup -
a project, and an image when one is named - and writes what opened as JSON, which
is how a packaged build is asked to prove it works at all. Otherwise the
application builds its ``QApplication``, takes its name and version from the
identity authority, applies the one theme, and shows the shell. Nothing is loaded
here: the session opens an image only when a user asks for one.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

from tools.webfoot.release_identity import release_identity

from . import theme
from .session import Session
from .shell import Shell
from .smoke import run_smoke


def configuration_directory() -> Path:
    """Where this application keeps its per-user settings.

    Qt's own per-user location, which is outside the repository and outside any
    project. Falls back to the user's home only when Qt cannot name a location.
    """
    location = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
    return Path(location) if location else Path.home() / ".dragonbyte-z"


def parse_headless_arguments(arguments: list[str]) -> argparse.Namespace | None:
    """The headless commands, or None when this is an ordinary window launch.

    Parsed before any Qt import runs, because ``--version`` and ``--smoke`` exist
    precisely to answer without a display, and a parser that gave up on an unknown
    argument would turn a real launch into an error message.
    """
    parser = argparse.ArgumentParser(
        prog="dragonbyte-z",
        description="DragonByte Z, an editor for Dragon Ball Z: Buu's Fury.",
        add_help=False,
    )
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--smoke", type=Path, metavar="PROJECT_DIR")
    parser.add_argument("--smoke-rom", type=Path, metavar="ROM")
    parser.add_argument("--smoke-report", type=Path, metavar="PATH")
    known, _rest = parser.parse_known_args(arguments)
    if known.smoke is None and known.smoke_report is None:
        return None
    return known


def main(argv: list[str] | None = None) -> int:
    """Run the application, or report the version or a smoke result and return."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    identity = release_identity()
    if "--version" in arguments:
        print(identity.display)
        return 0

    headless = parse_headless_arguments(arguments)
    if headless is not None:
        if headless.smoke is None or headless.smoke_report is None:
            print(
                "error: --smoke needs a project directory and --smoke-report a path",
                file=sys.stderr,
            )
            return 2
        return run_smoke(headless.smoke, headless.smoke_rom, headless.smoke_report)

    app = QApplication(sys.argv if argv is None else [sys.argv[0], *arguments])
    app.setApplicationName(identity.product_name)
    app.setApplicationVersion(identity.version)
    theme.apply_theme(app)
    window = Shell(Session(), configuration_directory())
    window.show()
    return app.exec()



if __name__ == "__main__":
    raise SystemExit(main())
