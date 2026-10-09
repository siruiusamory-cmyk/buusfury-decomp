"""Per-user machine facts, outside the repository and outside any project.

Two values live here and both are conveniences: the directory a file dialogue
last opened from, and the window geometry. Neither gates anything, so every
function fails safe - a missing, unreadable or corrupt file yields defaults, and
an unwritable one is a silent no-op rather than a failed close.

The geometry is carried as the base64 text of the window's own saved geometry,
so this module stays free of Qt and a test can drive it with no window. The
directory is supplied by the caller: this module never guesses where a user's
configuration lives.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

#: The file name, inside the directory the caller supplies.
SETTINGS_FILE = "dragonbyte-settings.json"


@dataclass
class Settings:
    """The machine facts this application remembers between runs."""

    last_directory: str = ""
    #: Base64 text of the saved window geometry, not a Qt object.
    geometry: str = ""

    @classmethod
    def load(cls, directory: Path) -> "Settings":
        """Read the settings file, or the defaults.

        Never raises: a missing file, an unreadable one and a corrupt one are
        all the same answer. Unknown keys are ignored, so a file written by a
        later build stays readable by this one.
        """
        try:
            document = json.loads(
                (Path(directory) / SETTINGS_FILE).read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            return cls()
        if not isinstance(document, dict):
            return cls()
        last_directory = document.get("last_directory", "")
        geometry = document.get("geometry", "")
        return cls(
            last_directory=last_directory if isinstance(last_directory, str) else "",
            geometry=geometry if isinstance(geometry, str) else "",
        )

    def save(self, directory: Path) -> None:
        """Write the settings file, creating the directory, or do nothing."""
        target = Path(directory)
        try:
            target.mkdir(parents=True, exist_ok=True)
            (target / SETTINGS_FILE).write_text(
                json.dumps(
                    {"last_directory": self.last_directory, "geometry": self.geometry},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
        except OSError:
            return
